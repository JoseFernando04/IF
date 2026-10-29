"""Carrusel: una slide HTML por imagen, exportada a JPEG (Instagram solo acepta JPEG)."""
from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

from ..core.config import load_config
from ..core.models import CarouselCopy
from . import base_css, env


def render_carousel(copy: CarouselCopy, pillar: str, out_dir: Path) -> list[Path]:
    cfg = load_config()
    w, h = cfg.settings["carousel"]["width"], cfg.settings["carousel"]["height"]
    tpl = env().get_template("graphics/carousel_slide.html.j2")
    css = base_css(w, h)
    out_dir = out_dir.resolve()
    html_dir = out_dir / "html"
    html_dir.mkdir(parents=True, exist_ok=True)
    total = len(copy.slides)
    paths: list[Path] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": w, "height": h})
        for i, slide in enumerate(copy.slides, start=1):
            html = tpl.render(
                base_css=css, brand=cfg.brand, slide=slide, index=i, total=total,
                pillar_name=cfg.pillars[pillar]["name"],
            )
            html_path = html_dir / f"slide_{i:02d}.html"
            html_path.write_text(html, encoding="utf-8")
            page.goto(html_path.as_uri())
            page.evaluate("document.fonts.ready")
            img = out_dir / f"slide_{i:02d}.jpg"
            page.screenshot(path=str(img), type="jpeg", quality=95)
            paths.append(img)
        browser.close()
    build_preview(paths, out_dir / "preview.jpg")
    return paths


def build_preview(images: list[Path], out: Path, cols: int = 4, thumb_w: int = 540, gap: int = 24) -> Path:
    """Una sola imagen con todas las slides, para revisar el carrusel completo de un vistazo."""
    from PIL import Image

    thumbs = []
    for p in images:
        with Image.open(p) as im:
            thumbs.append(im.convert("RGB").resize((thumb_w, round(im.height * thumb_w / im.width))))
    th = thumbs[0].height
    rows = -(-len(thumbs) // cols)
    sheet = Image.new("RGB", (cols * thumb_w + (cols + 1) * gap, rows * th + (rows + 1) * gap), (32, 36, 34))
    for i, t in enumerate(thumbs):
        r, c = divmod(i, cols)
        sheet.paste(t, (gap + c * (thumb_w + gap), gap + r * (th + gap)))
    sheet.save(out, quality=90)
    return out
