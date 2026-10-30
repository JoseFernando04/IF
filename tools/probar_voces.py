"""Compara voces femeninas latinoamericanas leyendo el guion real del reel, con la música de la campaña de fondo.

Uso: .venv/Scripts/python tools/probar_voces.py
Genera data/voz/comparacion/<proveedor>-<voz>.mp3 para cada proveedor con clave en .env (los demás se saltan).
"""
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

from ifcontent.audio.mix import mix_audio
from ifcontent.audio.music import get_track
from ifcontent.audio.tts import SAMPLE_RATE, AzureTTS, GoogleTTS
from ifcontent.core.config import ROOT, load_config
from ifcontent.video.ffmpeg import ffmpeg_bin

GUION = [
    "¿La digitalización es solo para grandes?",
    "Spoiler: no.",
    "Si tu negocio vende, compra y cuenta producto, ya calificás.",
    "Y si hoy todo vive en un Excel así… hay algo que ordenar.",
    "Contanos tu caso. El diagnóstico es sin compromiso.",
]
CANDIDATAS = {
    "azure": [AzureTTS, ["es-GT-MartaNeural", "es-MX-DaliaNeural", "es-CO-SalomeNeural", "es-US-PalomaNeural"]],
    "google": [GoogleTTS, ["es-US-Chirp3-HD-Aoede", "es-US-Chirp3-HD-Kore", "es-US-Chirp3-HD-Leda", "es-US-Chirp3-HD-Zephyr"]],
}
PAUSA_S = 0.45

load_config()
out = ROOT / "data" / "voz" / "comparacion"
out.mkdir(parents=True, exist_ok=True)
musica = get_track("voxel-revolution").path

for proveedor, (motor, voces) in CANDIDATAS.items():
    for voz in voces:
        try:
            clips = motor(voice=voz).synth_many(GUION)
        except Exception as e:  # sin clave o voz no disponible: se informa y se sigue
            print(f"✗ {proveedor} {voz}: {e}")
            continue
        silencio = np.zeros(int(PAUSA_S * SAMPLE_RATE), dtype=np.float32)
        narracion = np.concatenate([np.concatenate([c, silencio]) for c in clips])
        wav = out / f"{proveedor}-{voz}.wav"
        sf.write(wav, narracion, SAMPLE_RATE)
        mezcla = mix_audio(wav, musica, len(narracion) / SAMPLE_RATE + 0.8, out / "tmp.wav")
        mp3 = wav.with_suffix(".mp3")
        subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", str(mezcla), "-b:a", "160k", str(mp3)], check=True)
        print(f"✔ {mp3.name}  ({len(narracion) / SAMPLE_RATE:.1f} s)")
