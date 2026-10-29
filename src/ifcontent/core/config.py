"""Carga de configuración editable (config/*.yaml, brand.json) y del .env.

Nada de marca, pilares, horarios ni motores vive en el código: todo sale de aquí.
"""
from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = ROOT / "config"
TEMPLATES_DIR = ROOT / "templates"
ASSETS_DIR = ROOT / "assets"

_SECRET_KEY_RE = re.compile(r"(TOKEN|SECRET|PASSWORD|KEY)", re.IGNORECASE)


def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@dataclass(frozen=True)
class Config:
    settings: dict[str, Any]
    brand: dict[str, Any]
    pillars: dict[str, Any]
    calendar: dict[str, Any]

    @property
    def dry_run(self) -> bool:
        return os.getenv("DRY_RUN", "true").strip().lower() not in {"0", "false", "no"}

    def engine(self, module: str) -> str:
        return self.settings["engines"][module]

    def path(self, key: str) -> Path:
        p = Path(self.settings["paths"][key])
        return p if p.is_absolute() else ROOT / p


@lru_cache(maxsize=1)
def load_config() -> Config:
    load_dotenv(ROOT / ".env")
    _install_secret_filter()
    return Config(
        settings=_read_yaml(CONFIG_DIR / "settings.yaml"),
        brand=json.loads((CONFIG_DIR / "brand.json").read_text(encoding="utf-8")),
        pillars=_read_yaml(CONFIG_DIR / "pillars.yaml")["pillars"],
        calendar=_read_yaml(CONFIG_DIR / "calendar.yaml"),
    )


class _SecretFilter(logging.Filter):
    """Reemplaza en los logs cualquier valor de credencial del .env por ***."""

    def filter(self, record: logging.LogRecord) -> bool:
        secrets = [v for k, v in os.environ.items() if _SECRET_KEY_RE.search(k) and v and len(v) >= 6]
        if secrets:
            msg = record.getMessage()
            for s in secrets:
                msg = msg.replace(s, "***")
            record.msg, record.args = msg, None
        return True


def _install_secret_filter() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    for handler in logging.getLogger().handlers:
        handler.addFilter(_SecretFilter())
