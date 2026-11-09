"""Exporta un post (imagen o carrusel 1080×1350) desde templates/graphics/posts/post.html.

Uso: .venv/Scripts/python tools/render_post.py examples/copy/dia/2026-11-08-post-1.yaml
El YAML define formato (checklist | este-o-este | frase), salida, caption, hashtags y los textos del formato.
Salida: <salida>/slide-01.png …, caption.txt
"""
import json
import sys
from pathlib import Path

import yaml
from playwright.sync_api import sync_playwright

from ifcontent.core.config import ASSETS_DIR, ROOT, TEMPLATES_DIR, load_config


def main() -> None:
    load_config()
    g = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
    salida = ROOT / g["salida"]
    (salida / "work").mkdir(parents=True, exist_ok=True)
    datos = {k: v for k, v in g.items() if k not in ("caption", "hashtags", "titulo_tiktok")}
    html = (TEMPLATES_DIR / "graphics" / "posts" / "post.html").read_text(encoding="utf-8")
    html = (html.replace("__FONTS__", (ASSETS_DIR / "fonts").as_uri())
                .replace("__SHARED__", (TEMPLATES_DIR / "shared").as_uri())
                .replace("__LOGO_OSCURO__", (ASSETS_DIR / "logo" / "logo-dark.png").as_uri())
                .replace("__LOGO__", (ASSETS_DIR / "logo" / "logo-white.png").as_uri())
                .replace("__DATOS__", json.dumps(datos, ensure_ascii=False)))
    html_path = salida / "work" / "post.html"
    html_path.write_text(html, encoding="utf-8")
    for viejo in salida.glob("slide-*.png"):
        viejo.unlink()
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=["--allow-file-access-from-files"])
        page = b.new_page(viewport={"width": 1080, "height": 1350})
        page.on("pageerror", lambda e: print("  [error JS]", e))
        page.goto(html_path.as_uri())
        page.wait_for_function("window.__ready === true", timeout=30000)
        slides = page.query_selector_all(".slide")
        for i, s in enumerate(slides, 1):
            s.screenshot(path=str(salida / f"slide-{i:02d}.png"))
        b.close()
    caption = g["caption"].strip() + "\n\n" + " ".join(f"#{h}" for h in g["hashtags"])
    if g.get("titulo_tiktok"):  # TikTok permite un título aparte en publicaciones de fotos (máx. 90 caracteres)
        caption = f"TÍTULO (TikTok): {g['titulo_tiktok']}\n\nDESCRIPCIÓN:\n{caption}"
    (salida / "caption.txt").write_text(caption, encoding="utf-8")
    print(f"✔ {len(slides)} imagen(es) en {salida}")


if __name__ == "__main__":
    main()
