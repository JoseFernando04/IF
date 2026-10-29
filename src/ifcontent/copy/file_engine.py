"""Copy escrito a mano (o por Claude vía MCP) en un archivo YAML/JSON con el mismo esquema."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

from ..core.models import CarouselCopy, ReelCopy
from .postprocess import clean


class FileEngine:
    def __init__(self, path: Path):
        text = Path(path).read_text(encoding="utf-8")
        self.data = json.loads(text) if str(path).endswith(".json") else yaml.safe_load(text)

    def reel(self, pillar: str, topic: str) -> ReelCopy:
        return clean(ReelCopy.model_validate(self.data))

    def carousel(self, pillar: str, topic: str) -> CarouselCopy:
        return clean(CarouselCopy.model_validate(self.data))
