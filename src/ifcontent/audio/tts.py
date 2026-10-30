"""Voz en off, 100 % local.

- chatterbox: Chatterbox Multilingual (MIT). Voz natural; corre en .venv-tts con la GPU.
- kokoro: Kokoro-82M (Apache 2.0). Muy liviano, pero suena más robótico.
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Protocol

import numpy as np
import soundfile as sf

from ..core.config import ROOT, load_config

SAMPLE_RATE = 24000


def _clean(text: str) -> str:
    return re.sub(r"[*_#]", "", text).strip()


def _resample(audio: np.ndarray, sr: int) -> np.ndarray:
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    if sr == SAMPLE_RATE:
        return audio.astype(np.float32)
    n = int(len(audio) * SAMPLE_RATE / sr)
    return np.interp(np.linspace(0, len(audio) - 1, n), np.arange(len(audio)), audio).astype(np.float32)


class TTSEngine(Protocol):
    def synth_many(self, texts: list[str]) -> list[np.ndarray]: ...


class KokoroTTS:
    def __init__(self) -> None:
        from kokoro_onnx import Kokoro

        s = load_config().settings["tts"]
        model_dir = ROOT / s["kokoro"]["model_dir"]
        self.kokoro = Kokoro(str(model_dir / "kokoro-v1.0.onnx"), str(model_dir / "voices-v1.0.bin"))
        self.voice, self.speed = s["kokoro"]["voice"], s["kokoro"]["speed"]

    def synth_many(self, texts: list[str]) -> list[np.ndarray]:
        out = []
        for t in texts:
            samples, sr = self.kokoro.create(_clean(t), voice=self.voice, speed=self.speed, lang="es")
            out.append(_resample(samples, sr))
        return out


class ChatterboxTTS:
    def __init__(self) -> None:
        self.s = load_config().settings["tts"]["chatterbox"]
        self.python = ROOT / self.s["python"]
        if not self.python.exists():
            raise FileNotFoundError(f"No existe {self.python}. Ver README: instalación de la voz.")

    def synth_many(self, texts: list[str]) -> list[np.ndarray]:
        ref = self.s.get("reference")
        ref_path = str(ROOT / ref) if ref and (ROOT / ref).exists() else None
        with tempfile.TemporaryDirectory() as tmp:
            job = {"texts": [_clean(t) for t in texts], "out_dir": tmp, "language": "es", "reference": ref_path,
                   "exaggeration": self.s["exaggeration"], "cfg_weight": self.s["cfg_weight"]}
            worker = Path(__file__).with_name("chatterbox_worker.py")
            subprocess.run([str(self.python), str(worker)], input=json.dumps(job), text=True, check=True,
                           encoding="utf-8")
            out = []
            for i in range(len(texts)):
                audio, sr = sf.read(Path(tmp) / f"{i:03d}.wav", dtype="float32")
                out.append(_resample(audio, sr))
            return out


@lru_cache(maxsize=1)
def get_tts() -> TTSEngine | None:
    name = load_config().engine("tts")
    if name == "none":
        return None
    if name == "kokoro":
        return KokoroTTS()
    if name == "chatterbox":
        return ChatterboxTTS()
    if name == "azure":
        return AzureTTS()
    if name == "google":
        return GoogleTTS()
    raise ValueError(f"Motor de TTS desconocido: {name}")


def _wav_bytes_to_array(data: bytes) -> np.ndarray:
    import io

    audio, sr = sf.read(io.BytesIO(data), dtype="float32")
    return _resample(audio, sr)


class AzureTTS:
    """Azure AI Speech (capa gratis F0: 500 000 caracteres/mes, uso comercial permitido). Clave en .env."""

    def __init__(self, voice: str | None = None) -> None:
        import os

        self.key, self.region = os.getenv("AZURE_SPEECH_KEY"), os.getenv("AZURE_SPEECH_REGION")
        if not (self.key and self.region):
            raise RuntimeError("Faltan AZURE_SPEECH_KEY y AZURE_SPEECH_REGION en .env")
        s = load_config().settings["tts"].get("azure", {})
        self.voice = voice or s.get("voice", "es-GT-MartaNeural")
        self.rate = s.get("rate", "0%")

    def synth_many(self, texts: list[str]) -> list[np.ndarray]:
        import httpx
        from xml.sax.saxutils import escape as xml_escape

        lang = "-".join(self.voice.split("-")[:2])
        out = []
        for t in texts:
            ssml = (f'<speak version="1.0" xml:lang="{lang}"><voice name="{self.voice}">'
                    f'<prosody rate="{self.rate}">{xml_escape(_clean(t))}</prosody></voice></speak>')
            r = httpx.post(
                f"https://{self.region}.tts.speech.microsoft.com/cognitiveservices/v1",
                headers={"Ocp-Apim-Subscription-Key": self.key, "Content-Type": "application/ssml+xml",
                         "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm", "User-Agent": "ifcontent"},
                content=ssml.encode("utf-8"), timeout=60,
            )
            r.raise_for_status()
            out.append(_wav_bytes_to_array(r.content))
        return out


class GoogleTTS:
    """Google Cloud Text-to-Speech (capa gratis: 1 M caracteres/mes en Chirp 3 HD, uso comercial permitido)."""

    def __init__(self, voice: str | None = None) -> None:
        import os

        self.key = os.getenv("GOOGLE_TTS_API_KEY")
        if not self.key:
            raise RuntimeError("Falta GOOGLE_TTS_API_KEY en .env")
        s = load_config().settings["tts"].get("google", {})
        self.voice = voice or s.get("voice", "es-US-Chirp3-HD-Aoede")
        self.rate = s.get("speaking_rate", 1.0)

    def synth_many(self, texts: list[str]) -> list[np.ndarray]:
        import base64

        import httpx

        lang = "-".join(self.voice.split("-")[:2])
        out = []
        for t in texts:
            r = httpx.post(
                "https://texttospeech.googleapis.com/v1/text:synthesize",
                headers={"X-Goog-Api-Key": self.key},
                json={"input": {"text": _clean(t)},
                      "voice": {"languageCode": lang, "name": self.voice},
                      "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": SAMPLE_RATE, "speakingRate": self.rate}},
                timeout=60,
            )
            r.raise_for_status()
            out.append(_wav_bytes_to_array(base64.b64decode(r.json()["audioContent"])))
        return out
