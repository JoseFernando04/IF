"""Limpia las grabaciones de voz reales en assets/voice/<persona>/ (ver docs/guia-grabar-voces.md).

Uso: .venv/Scripts/python tools/preparar_voz.py
Por cada persona CON permiso: convierte referencia.* y frase*.* (m4a, mp3, ogg, wav…) a <nombre>.limpio.wav
(mono 48 kHz, filtro de graves, reducción de ruido suave, sin silencios al inicio/final, volumen nivelado).
"""
import re
import subprocess

import soundfile as sf

from ifcontent.core.config import ASSETS_DIR
from ifcontent.video.ffmpeg import ffmpeg_bin

VOCES = ASSETS_DIR / "voice"
AUDIO = re.compile(r"^(referencia|frase\d+)\.(m4a|mp3|ogg|opus|wav|aac|flac|webm|mp4)$", re.IGNORECASE)
FILTRO = ("highpass=f=80,afftdn=nf=-28,"
          "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,"
          "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.15,areverse,"
          "loudnorm=I=-16:TP=-1.5:LRA=7")


def tiene_permiso(persona) -> bool:
    return any(persona.glob("permiso.*"))


def preparar() -> None:
    personas = [p for p in sorted(VOCES.iterdir()) if p.is_dir()] if VOCES.exists() else []
    if not personas:
        print(f"No hay carpetas de personas en {VOCES}")
        return
    for persona in personas:
        if not tiene_permiso(persona):
            print(f"✗ {persona.name}: falta permiso.* (ver la guía). No se procesa.")
            continue
        archivos = [f for f in sorted(persona.iterdir()) if AUDIO.match(f.name)]
        if not archivos:
            print(f"✗ {persona.name}: no hay referencia.* ni frase*.*")
            continue
        for f in archivos:
            salida = persona / f"{f.stem.lower()}.limpio.wav"
            extra = ["-t", "30"] if f.stem.lower() == "referencia" else []  # la referencia ideal: 10-30 s
            subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", str(f), "-af", FILTRO,
                            "-ac", "1", "-ar", "48000", *extra, str(salida)], check=True)
            dur = sf.info(salida).duration
            print(f"✔ {persona.name}/{salida.name}  ({dur:.1f} s)")
            if f.stem.lower() == "referencia" and dur < 12:
                print(f"  ⚠ La referencia dura {dur:.1f} s: con menos de 12 s el clon puede cortar frases o sonar raro. "
                      "Grabá 20-30 s.")


if __name__ == "__main__":
    preparar()
