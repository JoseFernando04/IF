"""Renderiza un prototipo de dirección visual: slide.html → slide.png y reel.html → reel.mp4 (con música + SFX).

Uso: .venv/Scripts/python tools/render_direction.py prototypes/direcciones/a-papel
La carpeta trae meta.json: {"duration": 5, "music": "voxel-revolution", "sfx": [{"t": 0.8, "sfx": "thud"}]}
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from ifcontent.audio.mix import build_sfx_track, mix_audio
from ifcontent.audio.music import get_track
from ifcontent.video.html_frames import render_html_video

d = Path(sys.argv[1]).resolve()
meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1080, "height": 1350})
    page.goto((d / "slide.html").as_uri())
    page.evaluate("document.fonts.ready")
    page.screenshot(path=str(d / "slide.png"))
    b.close()
print("✔ slide.png")

work = d / "work"
work.mkdir(exist_ok=True)
fg = build_sfx_track(meta["sfx"], meta["duration"], work / "sfx.wav")
audio = mix_audio(fg, get_track(meta["music"]).path, meta["duration"], work / "audio.wav")
render_html_video(d / "reel.html", meta["duration"], audio, d / "reel.mp4", 1080, 1920, 30)
print("✔ reel.mp4")
