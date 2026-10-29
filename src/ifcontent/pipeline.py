"""Orquestador: copy → gráficos/video+audio → validación → cola de revisión.

Si un paso falla se reintenta una vez; si vuelve a fallar la pieza queda 'fallido' y se avisa por correo.
"""
from __future__ import annotations

import json
import logging
import re
import shutil
import unicodedata
from pathlib import Path
from typing import Callable

from .audio.music import choose_track
from .copy import get_engine as copy_engine
from .copy.lint import lint_carousel, lint_reel
from .core import db
from .core.config import load_config
from .core.models import CarouselCopy, ReelCopy
from .core.notify import notify
from .graphics.carousel import render_carousel
from .publish import get_publisher
from .validate import validate_carousel, validate_reel
from .video import get_engine as video_engine

log = logging.getLogger(__name__)


def _slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]


def _full_caption(copy: ReelCopy | CarouselCopy, attribution: str = "") -> str:
    parts = [copy.caption.strip()]
    if attribution:
        parts.append(f"🎵 {attribution}")
    parts.append(" ".join(copy.hashtags))
    return "\n\n".join(p for p in parts if p)


def _with_retry(piece_id: int, step: str, fn: Callable[[], dict]) -> dict:
    for attempt in (1, 2):
        try:
            return fn()
        except Exception as e:
            log.exception("Pieza #%d: falló '%s' (intento %d)", piece_id, step, attempt)
            if attempt == 2:
                db.set_status(piece_id, db.FALLIDO, f"{step}: {e}")
                notify(f"Pieza #{piece_id} falló", f"El paso '{step}' falló dos veces.\n\nError: {e}")
                raise
    raise AssertionError("inalcanzable")


def generate(kind: str, pillar: str, topic: str, copy_file: Path | None = None) -> int:
    cfg = load_config()
    if pillar not in cfg.pillars:
        raise ValueError(f"Pilar desconocido: {pillar}. Opciones: {', '.join(cfg.pillars)}")
    piece_id = db.create_piece(kind, pillar, topic)
    out = cfg.path("output") / f"{piece_id:04d}-{kind}-{_slug(topic)}"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    db.update_piece(piece_id, output_dir=str(out))
    log.info("Pieza #%d (%s, %s): %s", piece_id, kind, pillar, topic)

    def build() -> dict:
        engine = copy_engine(copy_file=copy_file)
        if kind == "reel":
            copy = engine.reel(pillar, topic)
            warnings = lint_reel(copy)
            track = choose_track(pillar, piece_id)
            media = video_engine().render(copy, pillar, track.path, out)
            caption = _full_caption(copy, track.attribution)
            validate_reel(media, caption, copy.hashtags, track.id)
            music = {"id": track.id, "title": track.title, "license": track.license, "attribution": track.attribution}
        else:
            copy = engine.carousel(pillar, topic)
            warnings = lint_carousel(copy)
            images = [str(p) for p in render_carousel(copy, pillar, out)]
            media = {"images": images}
            caption = _full_caption(copy)
            validate_carousel(images, caption, copy.hashtags)
            music = None
        return {"copy": copy.model_dump(), "media": media, "caption": caption, "music": music, "warnings": warnings}

    result = _with_retry(piece_id, "generar", build)
    (out / "copy.json").write_text(json.dumps(result["copy"], ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "caption.txt").write_text(result["caption"], encoding="utf-8")
    manifest = {"id": piece_id, "kind": kind, "pillar": pillar, "topic": topic, "dry_run": cfg.dry_run,
                "copy_engine": "file" if copy_file else cfg.engine("copy"), **{k: result[k] for k in ("media", "music", "warnings")}}
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    db.update_piece(piece_id, copy=result["copy"], music_track=(result["music"] or {}).get("id"))
    note = "Advertencias del revisor: " + " | ".join(result["warnings"]) if result["warnings"] else ""
    db.set_status(piece_id, db.EN_REVISION, note)
    notify(f"Pieza #{piece_id} lista para revisar", f"{kind} · {pillar} · {topic}\nCarpeta: {out}\n{note}")
    return piece_id


def publish(piece_id: int) -> dict:
    piece = db.get_piece(piece_id)
    if not piece:
        raise ValueError(f"No existe la pieza #{piece_id}")
    if piece["status"] != db.APROBADO:
        raise PermissionError(f"La pieza #{piece_id} está '{piece['status']}'. Solo se publica lo aprobado.")
    publisher = get_publisher()
    result = _with_retry(piece_id, "publicar", lambda: publisher.publish(piece))
    if result.get("dry_run"):
        db.set_status(piece_id, db.APROBADO, "Simulación de publicación generada (DRY_RUN)")
    else:
        db.set_status(piece_id, db.PUBLICADO)
    return result
