"""Compara voces femeninas leyendo el guion real del reel, con la música de la campaña de fondo.

Uso:
  .venv/Scripts/python tools/probar_voces.py            → voces locales (gratis, sin cuenta)
  .venv/Scripts/python tools/probar_voces.py --nube     → además Azure y Google (si hay claves en .env)
Genera data/voz/comparacion/<nombre>.mp3.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

from ifcontent.audio.mix import mix_audio
from ifcontent.audio.music import get_track
from ifcontent.audio.tts import SAMPLE_RATE, AzureTTS, ChatterboxTTS, GoogleTTS, KokoroTTS, PiperTTS
from ifcontent.core.config import ROOT, load_config
from ifcontent.video.ffmpeg import ffmpeg_bin

GUION = [
    "¿La digitalización es solo para grandes?",
    "Spoiler: no.",
    "Si tu negocio vende, compra y cuenta producto, ya calificás.",
    "Y si hoy todo vive en un Excel así… hay algo que ordenar.",
    "Contanos tu caso. El diagnóstico es sin compromiso.",
]
# Texto largo y neutro para crear la referencia que imita Chatterbox.
TEXTO_REFERENCIA = ("Hola, gracias por escribirnos. Te cuento cómo trabajamos: primero conversamos sobre tu negocio, "
                    "después revisamos juntos cómo llevás el inventario y al final te proponemos una solución clara, "
                    "paso a paso, sin complicaciones.")
PAUSA_S = 0.45
OUT = ROOT / "data" / "voz" / "comparacion"


def referencia(voz_piper: str) -> str:
    """Genera (una vez) un clip de ~15 s con una voz sintética de Piper, para que Chatterbox la imite."""
    ref = OUT / f"ref-{voz_piper}.wav"
    if not ref.exists():
        sf.write(ref, PiperTTS(voz_piper).synth_many([TEXTO_REFERENCIA])[0], SAMPLE_RATE)
    return str(ref.relative_to(ROOT))


def candidatas(nube: bool) -> dict:
    c = {
        "1-kokoro-dora": lambda: KokoroTTS("ef_dora"),
        "2-piper-mexicana-claude": lambda: PiperTTS("es_MX-claude-high"),
        "3-piper-argentina-daniela": lambda: PiperTTS("es_AR-daniela-high"),
        "4-chatterbox-imita-mexicana": lambda: ChatterboxTTS(referencia("es_MX-claude-high"), 0.5, 0.5),
        "5-chatterbox-imita-argentina": lambda: ChatterboxTTS(referencia("es_AR-daniela-high"), 0.5, 0.5),
        "6-chatterbox-argentina-expresiva": lambda: ChatterboxTTS(referencia("es_AR-daniela-high"), 0.7, 0.35),
    }
    if nube:
        for i, v in enumerate(["es-GT-MartaNeural", "es-MX-DaliaNeural", "es-CO-SalomeNeural", "es-US-PalomaNeural",
                               "es-MX-DaliaMultilingualNeural", "es-MX-Dalia:DragonHDLatestNeural",
                               "es-MX-Valeria:MAI-Voice-2.1", "es-MX-Harper:MAI-Voice-2.1"], start=1):
            c[f"A{i}-azure-{v.replace(':', '-')}"] = lambda v=v: AzureTTS(voice=v)
        for v in ["Aoede", "Kore", "Leda", "Zephyr"]:
            c[f"google-{v}"] = lambda v=v: GoogleTTS(voice=f"es-US-Chirp3-HD-{v}")
    return c


if __name__ == "__main__":
    load_config()
    OUT.mkdir(parents=True, exist_ok=True)
    musica = get_track("voxel-revolution").path
    for nombre, motor in candidatas("--nube" in sys.argv).items():
        try:
            clips = motor().synth_many(GUION)
        except Exception as e:  # sin clave, sin modelo o voz no disponible: se informa y se sigue
            print(f"✗ {nombre}: {e}")
            continue
        silencio = np.zeros(int(PAUSA_S * SAMPLE_RATE), dtype=np.float32)
        narracion = np.concatenate([np.concatenate([c, silencio]) for c in clips])
        wav = OUT / f"{nombre}.wav"
        sf.write(wav, narracion, SAMPLE_RATE)
        mezcla = mix_audio(wav, musica, len(narracion) / SAMPLE_RATE + 0.8, OUT / "tmp.wav")
        mp3 = wav.with_suffix(".mp3")
        subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", str(mezcla), "-b:a", "160k", str(mp3)], check=True)
        print(f"✔ {mp3.name}  ({len(narracion) / SAMPLE_RATE:.1f} s)")
