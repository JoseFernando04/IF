"""Publicación. Solo se publican piezas en estado 'aprobado'. En modo simulación nada sale de la PC."""
from __future__ import annotations

from typing import Protocol

from ..core.config import load_config


class Publisher(Protocol):
    def publish(self, piece: dict) -> dict: ...


def get_publisher(name: str | None = None) -> Publisher:
    cfg = load_config()
    name = "dry_run" if cfg.dry_run else (name or cfg.engine("publisher"))
    if name == "dry_run":
        from .dry_run import DryRunPublisher
        return DryRunPublisher()
    raise NotImplementedError(f"El publicador '{name}' llega en la Fase 3")
