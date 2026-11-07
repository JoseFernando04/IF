"""Renderiza un reel Motion Graphics 8-bit: audio externo (intacto) + animación en pixeles + chiptune propio.

Uso: .venv/Scripts/python tools/render_8bit.py examples/copy/8bit/reel-1.yaml [--cuadros t1,t2,...] [--musica-db -22]
Salida: data/reels-8bit/<nombre>/reel.mp4, caption.txt
--cuadros: solo exporta imágenes en esos segundos, sin renderizar el video (para revisar el diseño).
"""
import json
import subprocess
import sys
from pathlib import Path

import yaml
from playwright.sync_api import sync_playwright

from ifcontent.audio.mix import build_sfx_track, mix_audio
from ifcontent.audio.music import get_track
from ifcontent.audio.transcribe import cortes_por_frase, parecido, transcribir
from ifcontent.core.config import ASSETS_DIR, ROOT, TEMPLATES_DIR, load_config
from ifcontent.video.ffmpeg import ffmpeg_bin
from ifcontent.video.html_frames import render_html_video

LEAD_S = 0.2     # respiro antes de la primera palabra
CIERRE_S = 2.6   # el cierre se queda en pantalla


def arg(nombre: str) -> str | None:
    return sys.argv[sys.argv.index(nombre) + 1] if nombre in sys.argv else None


def main() -> None:
    load_config()
    guion = Path(sys.argv[1])
    g = yaml.safe_load(guion.read_text(encoding="utf-8"))
    audio_in = ROOT / g["audio"]
    salida = ROOT / "data" / "reels-8bit" / guion.stem
    (salida / "work").mkdir(parents=True, exist_ok=True)

    t = transcribir([audio_in])[str(audio_in)]
    textos = [l["texto"] for l in g["lineas"]]
    p = parecido(t["text"], " ".join(textos))
    print(f"{g['titulo']} · parecido con el guion: {p:.0%}")
    if p < 0.8:
        sys.exit(f"✗ El audio no coincide con el guion. Se oyó: {t['text'][:150]}")
    cortes = cortes_por_frase(t, textos)

    lineas = []
    for l, (a, b) in zip(g["lineas"], cortes):
        lineas.append({k: v for k, v in l.items() if k != "sfx"} | {"inicio": round(LEAD_S + a, 3), "duracion": round(b - a, 3)})
    fin = round(LEAD_S + cortes[-1][1] + CIERRE_S, 3)
    for l in lineas:
        print(f"  {l['inicio']:6.2f}s +{l['duracion']:5.2f}  {l['escena']:10s} {l['texto']}")

    html = (TEMPLATES_DIR / "video" / "8bit" / "reel.html").read_text(encoding="utf-8")
    html = html.replace("__FONTS__", (ASSETS_DIR / "fonts").as_uri()).replace(
        "__DATOS__", json.dumps({"lineas": lineas, "fin": fin}, ensure_ascii=False))
    html_path = salida / "work" / "reel.html"
    html_path.write_text(html, encoding="utf-8")

    if arg("--cuadros"):
        tiempos = [float(x) for x in arg("--cuadros").split(",")]
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            page = b.new_page(viewport={"width": 1080, "height": 1920})
            page.goto(html_path.as_uri())
            page.wait_for_function("window.__ready === true")
            for x in tiempos:
                page.evaluate("t => window.__seek(t)", x)
                page.screenshot(path=str(salida / "work" / f"c{x:06.2f}.png"))
            b.close()
        print("✔ cuadros en", salida / "work")
        return

    voz = salida / "work" / "voz.wav"
    subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", str(audio_in),
                    "-af", f"aresample=48000,adelay={int(LEAD_S * 1000)}:all=1,apad=whole_dur={fin}", "-ac", "1", str(voz)], check=True)
    sfx = []
    for l, orig in zip(lineas, g["lineas"]):
        for frac, nombre in orig.get("sfx", []):
            sfx.append({"t": l["inicio"] + l["duracion"] * frac, "sfx": f"8bit/{nombre}", "gain_db": -9})
    primer_plano = build_sfx_track(sfx, fin, salida / "work" / "voz_sfx.wav", voice=voz)
    db = float(arg("--musica-db") or -13)
    audio = mix_audio(primer_plano, get_track("chiptune-bodega").path, fin, salida / "work" / "audio.wav", volume_db=db)
    render_html_video(html_path, fin, audio, salida / "reel.mp4", 1080, 1920, 30,
                      cover=salida / "cover.jpg", cover_t=lineas[0]["inicio"] + lineas[0]["duracion"] * 0.7)
    caption = g["caption"].strip() + "\n\n" + " ".join(f"#{h}" for h in g["hashtags"])
    (salida / "caption.txt").write_text(caption, encoding="utf-8")
    print("✔", salida / "reel.mp4", f"({fin:.1f} s)")


if __name__ == "__main__":
    main()
