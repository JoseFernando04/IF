"""Validación previa: una pieza incompleta o fuera de especificación nunca pasa a revisión ni se publica."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from .audio.music import get_track
from .core.config import load_config
from .video.ffmpeg import ffprobe


class PieceInvalid(Exception):
    pass


def _caption_checks(caption: str, hashtags: list[str]) -> list[str]:
    lim = load_config().settings["limits"]
    errs = []
    if len(caption) > lim["caption_max_chars"]:
        errs.append(f"Caption de {len(caption)} caracteres (máximo {lim['caption_max_chars']})")
    if len(hashtags) > lim["hashtags_max"]:
        errs.append(f"{len(hashtags)} hashtags (máximo {lim['hashtags_max']})")
    if not caption.strip():
        errs.append("Caption vacío")
    return errs


def validate_reel(media: dict, caption: str, hashtags: list[str], track_id: str) -> None:
    rs = load_config().settings["reel"]
    errs = _caption_checks(caption, hashtags)
    video, cover = Path(media["video"]), Path(media["cover"])
    if not video.exists() or video.stat().st_size == 0:
        raise PieceInvalid("El video no existe")
    if not cover.exists():
        errs.append("Falta la portada")
    info = ffprobe(video)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur = float(info["format"]["duration"])
    if not v or v["codec_name"] != "h264" or (v["width"], v["height"]) != (rs["width"], rs["height"]):
        errs.append("Video fuera de especificación (se espera H.264 1080x1920)")
    if not a or a["codec_name"] != "aac":
        errs.append("Falta pista de audio AAC")
    if not rs["min_seconds"] - 0.5 <= dur <= rs["max_seconds"]:
        errs.append(f"Duración {dur:.1f} s fuera del rango {rs['min_seconds']}-{rs['max_seconds']} s")
    if not get_track(track_id):
        errs.append(f"La pista '{track_id}' no tiene licencia registrada")
    if errs:
        raise PieceInvalid("; ".join(errs))


def validate_carousel(images: list[str], caption: str, hashtags: list[str]) -> None:
    cs = load_config().settings["carousel"]
    errs = _caption_checks(caption, hashtags)
    if not cs["min_slides"] <= len(images) <= cs["max_slides"]:
        errs.append(f"{len(images)} slides (se esperan {cs['min_slides']}-{cs['max_slides']})")
    for p in images:
        if not Path(p).exists():
            errs.append(f"Falta {Path(p).name}")
            continue
        with Image.open(p) as im:
            if im.format != "JPEG" or im.size != (cs["width"], cs["height"]):
                errs.append(f"{Path(p).name}: debe ser JPEG {cs['width']}x{cs['height']}")
    if errs:
        raise PieceInvalid("; ".join(errs))
