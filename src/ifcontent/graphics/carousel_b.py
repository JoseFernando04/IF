"""Carrusel en estilo B (Documental): cada slide elige su layout (ver templates/graphics/b/carousel.html.j2)."""
from __future__ import annotations

import re
from pathlib import Path

import yaml
from markupsafe import Markup, escape
from playwright.sync_api import sync_playwright

from ..core.config import ASSETS_DIR, load_config
from . import env
from .carousel import build_preview

LAYOUTS = {"portada-foto", "libreta", "chat", "numero", "archivos", "cita", "cta",
           "versus", "hoja", "comparacion", "split-foto", "notificacion"}


def _marks(text: str, tag: str, cls: str = "") -> Markup:
    attr = f' class="{cls}"' if cls else ""
    return Markup(re.sub(r"\*(.+?)\*", rf"<{tag}{attr}>\1</{tag}>", str(escape(text))))


def render_carousel_b(data: dict, out_dir: Path) -> list[Path]:
    slides = data["slides"]
    bad = [s.get("layout") for s in slides if s.get("layout") not in LAYOUTS]
    if bad:
        raise ValueError(f"Layouts desconocidos: {bad}. Opciones: {sorted(LAYOUTS)}")
    e = env().overlay()
    e.filters.update(accent=lambda t: _marks(t, "span", "ac"), em=lambda t: _marks(t, "em"))
    tpl = e.get_template("graphics/b/carousel.html.j2")

    out_dir = out_dir.resolve()
    html_dir = out_dir / "html"
    html_dir.mkdir(parents=True, exist_ok=True)
    common = {"fonts": (ASSETS_DIR / "fonts").as_uri(), "photos": (ASSETS_DIR / "photos").as_uri(),
              "brand": load_config().brand, "total": len(slides)}
    paths = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(slides, start=1):
            html = html_dir / f"slide_{i:02d}.html"
            html.write_text(tpl.render(s=s, index=i, **common), encoding="utf-8")
            page.goto(html.as_uri())
            page.evaluate("document.fonts.ready")
            img = out_dir / f"slide_{i:02d}.jpg"
            page.screenshot(path=str(img), type="jpeg", quality=95)
            paths.append(img)
        browser.close()
    build_preview(paths, out_dir / "preview.jpg")
    return paths


def render_from_file(path: Path, out_dir: Path) -> list[Path]:
    return render_carousel_b(yaml.safe_load(Path(path).read_text(encoding="utf-8")), out_dir)
