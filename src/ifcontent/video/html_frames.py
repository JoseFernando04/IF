"""Motor de video 'html_frames': escenas HTML animadas, capturadas cuadro por cuadro con
Playwright y codificadas con FFmpeg. Sin licencias de pago (reemplaza a Remotion)."""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path

import soundfile as sf
from playwright.sync_api import sync_playwright

from ..audio.mix import mix_audio
from ..audio.tts import SAMPLE_RATE, get_tts
from ..core.config import load_config
from ..core.models import ReelCopy
from ..graphics import base_css, env
from .ffmpeg import ffmpeg_bin
from .timeline import build_timeline

log = logging.getLogger(__name__)


class HtmlFramesEngine:
    def render(self, copy: ReelCopy, pillar: str, music: Path, out_dir: Path) -> dict:
        cfg = load_config()
        rs = cfg.settings["reel"]
        w, h, fps = rs["width"], rs["height"], rs["fps"]
        out_dir = out_dir.resolve()
        work = out_dir / "work"
        work.mkdir(parents=True, exist_ok=True)

        tts = get_tts()
        tl = build_timeline(copy, tts, rs)
        log.info("Reel de %.1f s, %d escenas, %d subtítulos", tl.duration, len(tl.scenes), len(tl.captions))

        voice_wav = None
        if tl.voice is not None:
            voice_wav = work / "voice.wav"
            sf.write(voice_wav, tl.voice, SAMPLE_RATE)
        audio = mix_audio(voice_wav, music, tl.duration, work / "audio.wav")

        html = env().get_template("video/reel.html.j2").render(
            base_css=base_css(w, h), brand=cfg.brand, pillar_name=cfg.pillars[pillar]["name"],
            scenes=tl.scenes, captions=tl.captions, total=tl.duration,
            show_captions=rs.get("captions", False) and tl.voice is not None, show_progress=rs.get("progress_bar", False),
        )
        html_path = work / "reel.html"
        html_path.write_text(html, encoding="utf-8")

        video = out_dir / "reel.mp4"
        cover = out_dir / "cover.jpg"
        n_frames = int(round(tl.duration * fps))
        enc = subprocess.Popen(
            [ffmpeg_bin(), "-y", "-hide_banner", "-loglevel", "error",
             "-f", "image2pipe", "-framerate", str(fps), "-c:v", "mjpeg", "-i", "-",
             "-i", str(audio),
             "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(fps), "-g", str(fps * 2),
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
             "-movflags", "+faststart", "-shortest", str(video)],
            stdin=subprocess.PIPE,
        )
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": w, "height": h})
                page.goto(html_path.as_uri())
                page.evaluate("document.fonts.ready")
                for f in range(n_frames):
                    page.evaluate("t => window.__seek(t)", f / fps)
                    enc.stdin.write(page.screenshot(type="jpeg", quality=92))
                    if f and f % (fps * 5) == 0:
                        log.info("  cuadro %d/%d", f, n_frames)
                # Portada: el gancho ya completo, sin subtítulos.
                page.evaluate("document.querySelector('.captions')?.remove()")
                page.evaluate("t => window.__seek(t)", min(tl.scenes[0].end - 0.4, 2.2))
                page.screenshot(path=str(cover), type="jpeg", quality=95)
                browser.close()
        finally:
            enc.stdin.close()
            if enc.wait() != 0:
                raise RuntimeError("FFmpeg falló al codificar el reel")

        return {
            "video": str(video), "cover": str(cover), "duration": tl.duration,
            "scenes": [{"layout": s.scene.layout, "start": round(s.start, 2), "end": round(s.end, 2)} for s in tl.scenes],
            "voice": voice_wav is not None,
        }
