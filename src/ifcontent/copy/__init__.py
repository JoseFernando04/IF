"""Módulo de copy: gancho, guion, texto en pantalla, caption y hashtags."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ..core.config import ASSETS_DIR, load_config
from ..core.models import CarouselCopy, ReelCopy


class CopyEngine(Protocol):
    def reel(self, pillar: str, topic: str) -> ReelCopy: ...
    def carousel(self, pillar: str, topic: str) -> CarouselCopy: ...


def available_icons() -> list[str]:
    return sorted(p.stem for p in (ASSETS_DIR / "icons").glob("*.svg"))


def get_engine(name: str | None = None, copy_file: Path | None = None) -> CopyEngine:
    name = name or ("file" if copy_file else load_config().engine("copy"))
    if name == "ollama":
        from .ollama_engine import OllamaEngine
        return OllamaEngine()
    if name == "file":
        from .file_engine import FileEngine
        if not copy_file:
            raise ValueError("El motor 'file' necesita --copy-file")
        return FileEngine(copy_file)
    raise ValueError(f"Motor de copy desconocido: {name}")
