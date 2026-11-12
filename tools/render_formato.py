"""Renderiza un reel de un formato HTML (templates/video/<formato>/reel.html) con audio externo (intacto).

Uso:
  .venv/Scripts/python tools/render_formato.py examples/copy/dia/2026-11-08-reel-A.yaml
  .venv/Scripts/python tools/render_formato.py <yaml> --muestra 3.5,9,14   (sin audio: tiempos estimados, solo imágenes)
  .venv/Scripts/python tools/render_formato.py <yaml> --borrador           (video completo SIN voz, tiempos estimados)
  opciones: --musica-db -20

El YAML define: formato, titulo, audio, salida, musica, caption, hashtags, lineas (texto + campos de escena
+ sfx: [[fracción, nombre de assets/sfx]]) y cualquier dato extra que la plantilla lea (va completo a __DATOS__).
"""
import json
import subprocess
import sys
from pathlib import Path

import yaml
from PIL import Image
from playwright.sync_api import sync_playwright

from ifcontent.audio.mix import build_sfx_track, mix_audio
from ifcontent.audio.music import get_track
from ifcontent.audio.transcribe import cortes_por_frase, parecido, transcribir
from ifcontent.core.config import ASSETS_DIR, ROOT, TEMPLATES_DIR, load_config
from ifcontent.video.ffmpeg import ffmpeg_bin
from ifcontent.video.html_frames import render_html_video

LEAD_S = 0.2     # respiro antes de la primera palabra
CIERRE_S = 2.4   # el cierre se queda en pantalla
PALABRAS_S = 2.7  # ritmo estimado de la voz para las muestras


def arg(nombre: str) -> str | None:
    return sys.argv[sys.argv.index(nombre) + 1] if nombre in sys.argv else None


def cortes_estimados(textos: list[str]) -> list[tuple[float, float]]:
    t, out = 0.0, []
    for x in textos:
        d = max(0.9, len(x.split()) / PALABRAS_S)
        out.append((t, t + d))
        t += d + 0.25
    return out


def preparar_tomas(lineas: list[dict], salida: Path, work: Path) -> None:
    """Formato cine: extrae los cuadros de cada clip (<salida>/clips/<id>.mp4) a 1080x1920 y 30 fps para la plantilla."""
    for l in lineas:
        toma = l.get("toma")
        if not toma:
            continue
        clip = salida / "clips" / f"{toma['id']}.mp4"
        if not clip.exists():
            sys.exit(f"✗ Falta la toma: {clip} (generala con tools/generar_clip.py)")
        desde = float(toma.get("desde", 0))  # segundos a saltar al inicio (p. ej. texto falso que mete el modelo)
        carpeta = work / "cuadros" / f"{toma['id']}-{desde:g}"
        if not carpeta.exists() or clip.stat().st_mtime > carpeta.stat().st_mtime:
            carpeta.mkdir(parents=True, exist_ok=True)
            for viejo in carpeta.glob("*.jpg"):
                viejo.unlink()
            subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-ss", f"{desde:.3f}", "-i", str(clip),
                            "-vf", "fps=30,scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920",
                            "-q:v", "3", str(carpeta / "%04d.jpg")], check=True)
        l["toma"] = {"id": toma["id"], "n": len(list(carpeta.glob("*.jpg"))), "base": carpeta.as_uri()}


def armar_html(g: dict, lineas: list[dict], fin: float, destino: Path) -> Path:
    datos = {k: v for k, v in g.items() if k not in ("lineas", "caption", "hashtags")} | {"lineas": lineas, "fin": fin}
    html = (TEMPLATES_DIR / "video" / g["formato"] / "reel.html").read_text(encoding="utf-8")
    html = (html.replace("__FONTS__", (ASSETS_DIR / "fonts").as_uri())
                .replace("__SHARED__", (TEMPLATES_DIR / "shared").as_uri())
                .replace("__PHOTOS__", (ASSETS_DIR / "photos").as_uri())
                .replace("__LOGO__", (ASSETS_DIR / "logo" / "logo-white.png").as_uri())
                .replace("__LOGO_OSCURO__", (ASSETS_DIR / "logo" / "logo-dark.png").as_uri())
                .replace("__DATOS__", json.dumps(datos, ensure_ascii=False)))
    destino.write_text(html, encoding="utf-8")
    return destino


def capturar(html_path: Path, tiempos: list[float], carpeta: Path) -> list[Path]:
    rutas = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=["--allow-file-access-from-files"])
        page = b.new_page(viewport={"width": 1080, "height": 1920})
        page.on("console", lambda m: m.type == "error" and print("  [consola]", m.text))
        page.on("pageerror", lambda e: print("  [error JS]", e))
        page.goto(html_path.as_uri())
        page.wait_for_function("window.__ready === true", timeout=30000)
        for x in tiempos:
            page.evaluate("t => window.__seek(t)", x)
            r = carpeta / f"cuadro-{x:05.2f}.png"
            page.screenshot(path=str(r))
            rutas.append(r)
        b.close()
    return rutas


def tira(rutas: list[Path], destino: Path) -> None:
    """Une los cuadros en una sola imagen de muestra (a media escala)."""
    ims = [Image.open(r).convert("RGB").resize((540, 960)) for r in rutas]
    sep = 24
    out = Image.new("RGB", (len(ims) * 540 + (len(ims) + 1) * sep, 960 + 2 * sep), "#0a1410")
    for i, im in enumerate(ims):
        out.paste(im, (sep + i * (540 + sep), sep))
    out.save(destino, quality=92)


def main() -> None:
    load_config()
    guion = Path(sys.argv[1])
    g = yaml.safe_load(guion.read_text(encoding="utf-8"))
    salida = ROOT / g["salida"]
    work = salida / "work"
    work.mkdir(parents=True, exist_ok=True)
    textos = [l["texto"] for l in g["lineas"]]
    muestra = arg("--muestra")
    borrador = "--borrador" in sys.argv  # video completo SIN voz, con tiempos estimados (para aprobar antes de grabar)

    if muestra or borrador:
        cortes = cortes_estimados(textos)
    else:
        audio_in = ROOT / g["audio"]
        if not audio_in.exists():
            sys.exit(f"✗ Falta el audio: {audio_in}")
        t = transcribir([audio_in])[str(audio_in)]
        p = parecido(t["text"], " ".join(textos))
        print(f"{g['titulo']} · parecido con el guion: {p:.0%}")
        if p < 0.8:
            sys.exit(f"✗ El audio no coincide con el guion. Se oyó: {t['text'][:200]}")
        cortes = cortes_por_frase(t, textos)

    lineas = [{k: v for k, v in l.items() if k != "sfx"} | {"inicio": round(LEAD_S + a, 3), "duracion": round(b - a, 3)}
              for l, (a, b) in zip(g["lineas"], cortes)]
    fin = round(LEAD_S + cortes[-1][1] + CIERRE_S, 3)
    for l in lineas:
        print(f"  {l['inicio']:6.2f}s +{l['duracion']:5.2f}  {l['texto']}")
    preparar_tomas(lineas, salida, work)
    html_path = armar_html(g, lineas, fin, work / "reel.html")

    if muestra:
        tiempos = [float(x) for x in muestra.split(",")]
        rutas = capturar(html_path, tiempos, work)
        tira(rutas, salida / "muestra.jpg")
        Image.open(rutas[len(rutas) // 2]).convert("RGB").save(salida / "preview.png")
        print("✔ muestra en", salida / "muestra.jpg")
        return

    voz = work / "voz.wav"
    if borrador:
        subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
                        "-t", str(fin), str(voz)], check=True)
    else:
        subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", str(audio_in),
                        "-af", f"aresample=48000,adelay={int(LEAD_S * 1000)}:all=1,apad=whole_dur={fin}", "-ac", "1", str(voz)], check=True)
    sfx = [{"t": l["inicio"] + l["duracion"] * frac, "sfx": nombre, "gain_db": -10}
           for l, orig in zip(lineas, g["lineas"]) for frac, nombre in orig.get("sfx", [])]
    primer_plano = build_sfx_track(sfx, fin, work / "voz_sfx.wav", voice=voz)
    pista = get_track(g["musica"])
    db = float(arg("--musica-db") or g.get("musica_db", -20))
    audio = mix_audio(primer_plano, pista.path, fin, work / "audio.wav", volume_db=db)
    destino = salida / ("reel-borrador.mp4" if borrador else "reel.mp4")
    render_html_video(html_path, fin, audio, destino, 1080, 1920, 30,
                      cover=salida / "cover.jpg", cover_t=g.get("portada_t", lineas[0]["inicio"] + lineas[0]["duracion"] * 0.8))
    caption = g["caption"].strip()
    if getattr(pista, "attribution", ""):
        caption += "\n\nMúsica: " + pista.attribution
    caption += "\n\n" + " ".join(f"#{h}" for h in g["hashtags"])
    (salida / "caption.txt").write_text(caption, encoding="utf-8")
    print("✔", destino, f"({fin:.1f} s)" + (" · BORRADOR SIN VOZ" if borrador else ""))


if __name__ == "__main__":
    main()
