"""Limpieza común del copy, sin importar qué motor lo generó."""
from __future__ import annotations

import re

from ..core.config import load_config
from ..core.models import CarouselCopy, ReelCopy
from . import available_icons


def _hashtag(tag: str) -> str:
    tag = re.sub(r"[^\wáéíóúñÁÉÍÓÚÑ]", "", tag.strip().lstrip("#"))
    return f"#{tag}" if tag else ""


def clean(copy: ReelCopy | CarouselCopy) -> ReelCopy | CarouselCopy:
    limits = load_config().settings["limits"]
    icons = set(available_icons())
    tags = [t for t in dict.fromkeys(_hashtag(t) for t in copy.hashtags) if t]
    copy.hashtags = tags[: limits["hashtags_max"]]
    # El caption no debe traer hashtags propios: se agregan al final desde la lista.
    copy.caption = re.sub(r"(\s*#\w+)+\s*$", "", copy.caption.strip())
    items = copy.scenes if isinstance(copy, ReelCopy) else copy.slides
    for item in items:
        if item.icon not in icons:
            item.icon = "lightbulb"
    return copy
