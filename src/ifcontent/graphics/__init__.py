"""Gráficos: plantillas HTML/CSS de marca renderizadas con Playwright."""
from __future__ import annotations

import re
from functools import lru_cache

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup, escape

from ..core.config import ASSETS_DIR, TEMPLATES_DIR, load_config


def accent(text: str) -> Markup:
    """'Tu *inventario* manda' -> resalta la palabra entre asteriscos con el color de acento."""
    return Markup(re.sub(r"\*(.+?)\*", r'<span class="accent">\1</span>', str(escape(text))))


def strip_marks(text: str) -> str:
    return text.replace("*", "")


@lru_cache(maxsize=None)
def icon(name: str) -> Markup:
    path = ASSETS_DIR / "icons" / f"{name}.svg"
    if not path.exists():
        path = ASSETS_DIR / "icons" / "lightbulb.svg"
    svg = re.sub(r"<!--.*?-->", "", path.read_text(encoding="utf-8"), flags=re.S)
    return Markup(svg)


@lru_cache(maxsize=1)
def env() -> Environment:
    e = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=select_autoescape(["html", "j2"]))
    e.filters.update(accent=accent, icon=icon, plain=strip_marks)
    return e


def base_css(width: int, height: int) -> Markup:
    css = env().get_template("shared/base.css.j2").render(
        brand=load_config().brand, width=width, height=height, fonts_uri=(ASSETS_DIR / "fonts").as_uri()
    )
    return Markup(css)
