"""Ubicación de FFmpeg/ffprobe y lectura de metadatos de un archivo."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=None)
def _find(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    # winget instala FFmpeg aquí y el PATH no se refresca hasta reiniciar la terminal.
    base = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
    for exe in base.glob(f"Gyan.FFmpeg*/*/bin/{name}.exe"):
        return str(exe)
    raise FileNotFoundError(f"No se encontró {name}. Instalalo con: winget install Gyan.FFmpeg")


def ffmpeg_bin() -> str:
    return _find("ffmpeg")


def ffprobe(path: Path) -> dict:
    out = subprocess.run(
        [_find("ffprobe"), "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        check=True, capture_output=True, text=True,
    )
    return json.loads(out.stdout)
