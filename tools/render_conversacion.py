"""Renderiza un reel de conversación a dos voces (estilo B) a partir de un guion YAML.

Uso: .venv/Scripts/python tools/render_conversacion.py [carpeta] [--fuente clon|grabada]
  carpeta  por defecto prototypes/direcciones/b-conversacion (con guion.yaml y reel.html)
  clon     cada personaje habla con su voz clonada (assets/voice/<voz>/referencia.limpio.wav)
  grabada  usa las líneas grabadas de cada persona (assets/voice/<voz>/linea<N>.limpio.wav)
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import yaml

from ifcontent.audio.mix import build_sfx_track, mix_audio
from ifcontent.audio.music import get_track
from ifcontent.audio.transcribe import parecido, transcribir
from ifcontent.audio.tts import SAMPLE_RATE, ChatterboxTTS, _resample
from ifcontent.core.config import ROOT, load_config
from ifcontent.video.html_frames import render_html_video

PAUSA_DEFECTO = 0.3   # conversación: respuestas rápidas
UMBRAL_QA = 0.95      # parecido mínimo entre lo que se oye y el guion
CIERRE_S = 2.4


def voz_dir(voz: str) -> Path:
    d = ROOT / "assets" / "voice" / voz
    if not any("permiso" in f.name.lower() for f in d.glob("*")):
        sys.exit(f"✗ {voz}: falta el permiso en {d}")
    return d


def generar_audios(g: dict, fuente: str) -> list[np.ndarray]:
    lineas, personajes = g["lineas"], g["personajes"]
    audios: list[np.ndarray | None] = [None] * len(lineas)
    for clave, p in personajes.items():
        idx = [i for i, l in enumerate(lineas) if l["quien"] == clave]
        d = voz_dir(p["voz"])
        if fuente == "grabada":
            for i in idx:
                f = d / f"linea{i + 1:02d}.limpio.wav"
                if not f.exists():
                    sys.exit(f"✗ Falta {f}. ¿Grabó {p['voz']} sus líneas y corriste tools/preparar_voz.py?")
                a, sr = sf.read(f, dtype="float32")
                audios[i] = _resample(a, sr)
        else:
            ref = d / "referencia.limpio.wav"
            if not ref.exists():
                sys.exit(f"✗ Falta {ref}. Corré tools/preparar_voz.py")
            print(f"  {p['voz']}: {len(idx)} líneas con voz clonada…")
            tts = ChatterboxTTS(str(ref.relative_to(ROOT)), 0.55, 0.45)
            for i, c in zip(idx, tts.synth_many([lineas[i]["texto"] for i in idx])):
                audios[i] = c
            verificar(tts, idx, lineas, audios)
    return audios


def verificar(tts: ChatterboxTTS, idx: list[int], lineas: list[dict], audios: list, intentos: int = 3) -> None:
    """Control de calidad: transcribe cada línea clonada y regenera la que no dice lo que dice el guion."""
    tmp = ROOT / "data" / "voz" / "qa"
    tmp.mkdir(parents=True, exist_ok=True)
    pendientes, mejor = list(idx), {i: (0.0, audios[i]) for i in idx}
    for ronda in range(intentos + 1):
        archivos = {}
        for i in pendientes:
            f = tmp / f"l{i:02d}.wav"
            sf.write(f, audios[i], SAMPLE_RATE)
            archivos[i] = f
        oido = transcribir(list(archivos.values()))
        siguientes = []
        for i, f in archivos.items():
            p = parecido(oido[str(f)]["text"], lineas[i]["texto"])
            if p > mejor[i][0]:
                mejor[i] = (p, audios[i])
            if p < UMBRAL_QA:
                siguientes.append(i)
                print(f"    ↻ línea {i + 1} ({p:.0%}): oído «{oido[str(f)]['text']}»")
        pendientes = siguientes
        if not pendientes or ronda == intentos:
            break
        for i, c in zip(pendientes, tts.synth_many([lineas[i]["texto"] for i in pendientes])):
            audios[i] = c
    for i in idx:
        audios[i] = mejor[i][1]
        if mejor[i][0] < UMBRAL_QA:
            print(f"    ⚠ línea {i + 1}: quedó la mejor toma ({mejor[i][0]:.0%}); revisala al escuchar")


def main() -> None:
    load_config()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    fuente = sys.argv[sys.argv.index("--fuente") + 1] if "--fuente" in sys.argv else "clon"
    if fuente in args:
        args.remove(fuente)
    carpeta = (ROOT / args[0]) if args else ROOT / "prototypes" / "direcciones" / "b-conversacion"
    g = yaml.safe_load((carpeta / "guion.yaml").read_text(encoding="utf-8"))
    print(f"Conversación: {g['titulo']} · voces {fuente}")
    audios = generar_audios(g, fuente)

    t, lineas = 0.0, []
    for l, a in zip(g["lineas"], audios):
        t += l.get("pausa", PAUSA_DEFECTO)
        dur = len(a) / SAMPLE_RATE
        lineas.append({**l, "etiqueta": g["personajes"][l["quien"]]["etiqueta"], "inicio": round(t, 3), "duracion": round(dur, 3)})
        t += dur
    fin = round(t + CIERRE_S, 3)
    (carpeta / "conversacion.js").write_text(
        f"window.CONV = {json.dumps({'lineas': lineas, 'fin': fin}, ensure_ascii=False)};\n", encoding="utf-8")
    print(f"Duración: {fin:.1f} s · {len(lineas)} líneas")

    work = carpeta / "work"
    work.mkdir(exist_ok=True)
    voz = np.zeros(int((fin + 0.5) * SAMPLE_RATE), dtype=np.float32)
    for l, a in zip(lineas, audios):
        i0 = int(l["inicio"] * SAMPLE_RATE)
        voz[i0 : i0 + len(a)] += a
    sf.write(work / "voz.wav", voz[: int(fin * SAMPLE_RATE)], SAMPLE_RATE)

    sfx = [{"t": 0.05, "sfx": "tick", "gain_db": -8}]
    for i, l in enumerate(lineas):
        s, d = l["inicio"], l["duracion"]
        sfx += {"excel": [{"t": s + d * 0.25, "sfx": "paper", "gain_db": -5}],
                "libreta": [{"t": s, "sfx": "whoosh", "gain_db": -12}] + [{"t": s + d * k, "sfx": "marker", "gain_db": -12} for k in (0.35, 0.55, 0.75)],
                "alerta": [{"t": s + d * 0.45, "sfx": "pop", "gain_db": -4}]}.get(l.get("objeto"), [])
        if l.get("estilo") == "golpe":
            sfx.append({"t": s, "sfx": "thud", "gain_db": -2})
        if l.get("estilo") == "spoiler":
            sfx += [{"t": s - 0.47, "sfx": "whoosh", "gain_db": -3}, {"t": s + d * 0.13, "sfx": "thud", "gain_db": -3}]
        if l.get("estilo") == "cierre":
            sfx += [{"t": s - 0.47, "sfx": "whoosh", "gain_db": -3}, {"t": s + d * 0.45, "sfx": "thud", "gain_db": -4}]
        if i > 0 and lineas[i - 1].get("objeto") == "excel":  # "Mejor no te digo": se tacha el Excel
            sfx.append({"t": s + 0.3, "sfx": "marker", "gain_db": -6})

    primer_plano = build_sfx_track(sfx, fin, work / "voz_sfx.wav", voice=work / "voz.wav")
    audio = mix_audio(primer_plano, get_track("digital-lemonade").path, fin, work / "audio.wav")
    salida = carpeta / f"reel-{fuente}.mp4"
    render_html_video(carpeta / "reel.html", fin, audio, salida, 1080, 1920, 30, cover=carpeta / "cover.jpg", cover_t=1.6)
    print("✔", salida)


if __name__ == "__main__":
    main()
