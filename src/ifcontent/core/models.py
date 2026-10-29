"""Esquemas del copy. Los motores de texto (Ollama, archivo, Claude vía MCP) deben devolver esto."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SceneLayout = Literal["hook", "statement", "list", "big", "cta"]
SlideKind = Literal["cover", "content", "cta"]


class Scene(BaseModel):
    layout: SceneLayout = Field(description="hook=gancho; statement=idea con ícono; list=hasta 3 puntos; big=palabra o dato grande; cta=llamado a la acción")
    on_screen: str = Field(description="Texto en pantalla, máximo 8 palabras. Marcá con *asteriscos* la palabra a resaltar.")
    sub: str = Field(default="", description="Texto secundario en pantalla, máximo 14 palabras")
    bullets: list[str] = Field(default_factory=list, description="Solo para layout=list: 2 o 3 puntos de máximo 5 palabras")
    narration: str = Field(description="Lo que dice la voz en off en esta escena (1 o 2 frases cortas)")
    icon: str = Field(default="lightbulb", description="Nombre de ícono de la lista permitida")


class ReelCopy(BaseModel):
    title: str = Field(description="Título interno de la pieza")
    hook: str = Field(description="El gancho de los primeros 3 segundos")
    scenes: list[Scene] = Field(min_length=3, max_length=8)
    caption: str
    hashtags: list[str] = Field(max_length=5)


class Slide(BaseModel):
    kind: SlideKind
    heading: str = Field(description="Título de la slide, máximo 9 palabras. *asteriscos* para resaltar.")
    body: str = Field(default="", description="Texto de la slide, máximo 35 palabras")
    icon: str = Field(default="lightbulb")


class CarouselCopy(BaseModel):
    title: str
    hook: str = Field(description="El gancho de la portada")
    slides: list[Slide] = Field(min_length=3, max_length=10)
    caption: str
    hashtags: list[str] = Field(max_length=5)
