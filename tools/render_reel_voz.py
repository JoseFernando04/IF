"""Renderiza el reel B con voz: genera cada frase, calcula los tiempos y sincroniza animación, SFX y música.

Uso: .venv/Scripts/python tools/render_reel_voz.py [--voz 5 | --voz A6 | --grabada jose | --clon jose]
  --voz N        voz sintética de tools/probar_voces.py
  --grabada X    usa las frases que grabó la persona X (assets/voice/X/frase1..5.limpio.wav)
  --clon X       Chatterbox imita la voz de X a partir de assets/voice/X/referencia.limpio.wav
Salida: prototypes/direcciones/b-voz/reel.mp4 (y una copia en data/voz/)
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
from probar_voces import GUION, candidatas  # noqa: E402  (mismas voces que la comparación)

from ifcontent.audio.mix import build_sfx_track, mix_audio  # noqa: E402
from ifcontent.audio.music import get_track  # noqa: E402
from ifcontent.audio.tts import SAMPLE_RATE, ChatterboxTTS, _resample  # noqa: E402
from ifcontent.core.config import ROOT, load_config  # noqa: E402
from ifcontent.video.html_frames import render_html_video  # noqa: E402

DIR = ROOT / "prototypes" / "direcciones" / "b-voz"
# Silencio ANTES de cada frase: deja respirar y da lugar a las transiciones.
PAUSAS = [0.35, 0.75, 0.55, 0.8, 0.8]
CIERRE_S = 2.4  # el CTA se queda en pantalla después de la última frase

def arg(nombre: str) -> str | None:
    return sys.argv[sys.argv.index(nombre) + 1] if nombre in sys.argv else None


def carpeta_persona(persona: str) -> Path:
    d = ROOT / "assets" / "voice" / persona
    if not any("permiso" in f.name.lower() for f in d.glob("*")):
        sys.exit(f"✗ {persona}: falta el permiso en {d} (ver docs/guia-grabar-voces.md)")
    return d


def frases_grabadas(persona: str) -> list[np.ndarray]:
    d = carpeta_persona(persona)
    clips = []
    for i in range(1, len(GUION) + 1):
        f = d / f"frase{i}.limpio.wav"
        if not f.exists():
            sys.exit(f"✗ Falta {f.name} en {d}. ¿Corriste tools/preparar_voz.py?")
        audio, sr = sf.read(f, dtype="float32")
        clips.append(_resample(audio, sr))
    return clips


load_config()
if arg("--grabada"):
    nombre = f"grabada-{arg('--grabada')}"
    clips = frases_grabadas(arg("--grabada"))
elif arg("--clon"):
    ref = carpeta_persona(arg("--clon")) / "referencia.limpio.wav"
    if not ref.exists():
        sys.exit(f"✗ Falta {ref}. ¿Corriste tools/preparar_voz.py?")
    nombre = f"clon-{arg('--clon')}"
    clips = ChatterboxTTS(str(ref.relative_to(ROOT)), 0.5, 0.5).synth_many(GUION)
else:
    num = arg("--voz") or "5"
    nombre, motor = next((k, v) for k, v in candidatas(num.startswith("A")).items() if k.startswith(f"{num}-"))
    clips = motor().synth_many(GUION)
print(f"Voz: {nombre}")
work = DIR / "work"
work.mkdir(parents=True, exist_ok=True)

inicio, duracion, t = [], [], 0.0
for pausa, c in zip(PAUSAS, clips):
    t += pausa
    inicio.append(round(t, 3))
    duracion.append(round(len(c) / SAMPLE_RATE, 3))
    t += len(c) / SAMPLE_RATE
fin = round(t + CIERRE_S, 3)
(DIR / "tiempos.js").write_text(
    f"window.TIEMPOS = {json.dumps({'inicio': inicio, 'duracion': duracion, 'fin': fin})};\n", encoding="utf-8")
print("Frases:", [f"{s:.2f}s (+{d:.2f})" for s, d in zip(inicio, duracion)], f"fin {fin:.2f}s")

voz = np.zeros(int((fin + 0.5) * SAMPLE_RATE), dtype=np.float32)
for s, c in zip(inicio, clips):
    i0 = int(s * SAMPLE_RATE)
    voz[i0 : i0 + len(c)] += c
sf.write(work / "voz.wav", voz[: int(fin * SAMPLE_RATE)], SAMPLE_RATE)

S, D = inicio, duracion
sfx = [  # mismos golpes que la animación (ver reel.html)
    {"t": 0.02, "sfx": "tick", "gain_db": -8},
    {"t": S[0] + D[0] * 0.66, "sfx": "pop", "gain_db": -10},
    {"t": S[1] - 0.47, "sfx": "whoosh", "gain_db": -4},
    {"t": S[1] + D[1] * 0.6, "sfx": "thud", "gain_db": -3},
    {"t": S[2] - 0.15, "sfx": "whoosh", "gain_db": -12},
    {"t": S[3] - 0.47, "sfx": "whoosh", "gain_db": -4},
    {"t": S[3] + D[3] * 0.3, "sfx": "paper", "gain_db": -4},
    {"t": S[3] + D[3] * 0.52, "sfx": "marker", "gain_db": -5},
    {"t": S[4] - 0.47, "sfx": "whoosh", "gain_db": -4},
    {"t": S[4] + D[4] * 0.45, "sfx": "thud", "gain_db": -4},
]
primer_plano = build_sfx_track(sfx, fin, work / "voz_sfx.wav", voice=work / "voz.wav")
audio = mix_audio(primer_plano, get_track("voxel-revolution").path, fin, work / "audio.wav")
render_html_video(DIR / "reel.html", fin, audio, DIR / "reel.mp4", 1080, 1920, 30,
                  cover=DIR / "cover.jpg", cover_t=S[0] + D[0] * 0.66 + 0.6)
print("✔", DIR / "reel.mp4")
copia = ROOT / "data" / "voz" / f"reel-{nombre}.mp4"
copia.parent.mkdir(parents=True, exist_ok=True)
copia.write_bytes((DIR / "reel.mp4").read_bytes())
print("✔ copia:", copia)
