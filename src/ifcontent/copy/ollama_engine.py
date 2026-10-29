"""Copy con un LLM local vía Ollama, usando salida estructurada (JSON Schema)."""
from __future__ import annotations

import json
import logging
import os
from typing import Callable, TypeVar

import httpx
import yaml
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, ValidationError

from ..core.config import CONFIG_DIR, load_config
from ..core.models import CarouselCopy, ReelCopy
from . import available_icons
from .lint import lint_carousel, lint_reel, repair_carousel, repair_reel
from .postprocess import clean

log = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)
MAX_ATTEMPTS = 3


class OllamaEngine:
    def __init__(self) -> None:
        self.cfg = load_config()
        self.host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
        self.prompts = Environment(loader=FileSystemLoader(CONFIG_DIR / "prompts"), autoescape=False)

    def _context(self, kind: str, pillar: str, topic: str) -> dict:
        if pillar not in self.cfg.pillars:
            raise ValueError(f"Pilar desconocido: {pillar}. Opciones: {', '.join(self.cfg.pillars)}")
        example = yaml.safe_load((CONFIG_DIR / "prompts" / "examples" / f"{kind}.yaml").read_text(encoding="utf-8"))
        return {
            "brand": self.cfg.brand,
            "pillar": self.cfg.pillars[pillar],
            "topic": topic,
            "icons": ", ".join(available_icons()),
            "hashtags_max": self.cfg.settings["limits"]["hashtags_max"],
            "example": json.dumps(example, ensure_ascii=False, indent=1),
        }

    def _chat(self, messages: list[dict], schema: dict) -> str:
        r = httpx.post(
            f"{self.host}/api/chat",
            json={
                "model": self.cfg.settings["copy"]["ollama_model"],
                "messages": messages,
                "format": schema,
                "stream": False,
                "think": False,
                "options": {"temperature": self.cfg.settings["copy"]["temperature"], "num_ctx": 8192},
            },
            timeout=600,
        )
        r.raise_for_status()
        return r.json()["message"]["content"]

    def _ask(self, kind: str, model: type[T], pillar: str, topic: str,
             lint: Callable[[T], list[str]], repair: Callable[[T], T]) -> T:
        ctx = self._context(kind, pillar, topic)
        messages = [
            {"role": "system", "content": self.prompts.get_template("system.md").render(**ctx)},
            {"role": "user", "content": self.prompts.get_template(f"{kind}.md").render(**ctx)},
        ]
        best: T | None = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            content = self._chat(messages, model.model_json_schema())
            messages.append({"role": "assistant", "content": content})
            try:
                copy = model.model_validate(json.loads(content))
            except (ValidationError, json.JSONDecodeError) as e:
                messages.append({"role": "user", "content": f"No cumple el esquema JSON: {str(e)[:400]}. Corregilo."})
                continue
            best = copy
            issues = lint(copy)
            if not issues:
                return copy
            log.info("Intento %d: el revisor encontró %d problemas; se piden correcciones", attempt, len(issues))
            messages.append({"role": "user", "content": "Corregí estos problemas y devolvé el JSON completo:\n- " + "\n- ".join(issues)})
        if best is None:
            raise RuntimeError("El LLM no devolvió copy válido después de varios intentos")
        return repair(best)

    def reel(self, pillar: str, topic: str) -> ReelCopy:
        return clean(self._ask("reel", ReelCopy, pillar, topic, lint_reel, repair_reel))

    def carousel(self, pillar: str, topic: str) -> CarouselCopy:
        return clean(self._ask("carousel", CarouselCopy, pillar, topic, lint_carousel, repair_carousel))
