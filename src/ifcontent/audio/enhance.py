"""Limpieza de voz con IA (WPE contra el eco + DeepFilterNet contra el ruido). Ver denoise_worker.py."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ..core.config import ROOT, load_config


def mejorar(pares: list[tuple[Path, Path]], dereverb: bool = True) -> None:
    """Procesa cada (entrada, salida). Entrada y salida pueden ser el mismo archivo."""
    if not pares:
        return
    python = ROOT / load_config().settings["tts"]["chatterbox"]["python"]
    worker = Path(__file__).with_name("denoise_worker.py")
    job = {"pairs": [[str(a), str(b)] for a, b in pares], "dereverb": dereverb}
    subprocess.run([str(python), str(worker)], input=json.dumps(job), text=True, encoding="utf-8",
                   check=True, capture_output=True)
