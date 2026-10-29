"""Motion / video: reels verticales 9:16 a partir de escenas HTML animadas."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ..core.config import load_config
from ..core.models import ReelCopy


class VideoEngine(Protocol):
    def render(self, copy: ReelCopy, pillar: str, music: Path, out_dir: Path) -> dict: ...


def get_engine(name: str | None = None) -> VideoEngine:
    name = name or load_config().engine("video")
    if name == "html_frames":
        from .html_frames import HtmlFramesEngine
        return HtmlFramesEngine()
    raise ValueError(f"Motor de video desconocido: {name}")
