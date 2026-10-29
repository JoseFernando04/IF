"""Revisor automático del copy: estructura y voseo. Los problemas vuelven al LLM para que corrija."""
from __future__ import annotations

import re

from ..core.models import CarouselCopy, ReelCopy

# Formas de tuteo frecuentes que no deben aparecer (usamos voseo).
TUTEO = re.compile(
    r"\b(necesitas|tienes|puedes|sabes|quieres|haces|imagina|cuéntanos|escríbenos|agenda tu|descubre|"
    r"conoce|contáctanos|llámanos|visítanos|pierdes|vendes|cuentas con|eres|piensas)\b",
    re.IGNORECASE,
)
# Voseo escrito sin tilde ("podes" en vez de "podés").
VOSEO_SIN_TILDE = re.compile(r"\b(podes|tenes|queres)\b", re.IGNORECASE)


def _words(s: str) -> int:
    return len(s.replace("*", "").split())


def _tuteo(texts: list[str]) -> list[str]:
    found = sorted({m.group(0).lower() for t in texts for m in TUTEO.finditer(t)})
    accents = sorted({m.group(0).lower() for t in texts for m in VOSEO_SIN_TILDE.finditer(t)})
    issues = [f"Usa voseo, no tuteo. Corregí: {', '.join(found)}"] if found else []
    if accents:
        issues.append(f"Al voseo le falta la tilde: {', '.join(accents)} (podés, tenés, querés)")
    return issues


def lint_reel(c: ReelCopy) -> list[str]:
    issues = []
    if c.scenes[0].layout != "hook":
        issues.append('La escena 1 debe tener layout "hook".')
    if c.scenes[-1].layout != "cta":
        issues.append('La última escena debe tener layout "cta".')
    for i, s in enumerate(c.scenes, 1):
        if not 2 <= _words(s.on_screen) <= 9:
            issues.append(f"Escena {i}: on_screen debe tener entre 2 y 8 palabras.")
        if s.layout == "list" and len(s.bullets) < 2:
            issues.append(f'Escena {i}: layout "list" necesita 2 o 3 bullets.')
        if not s.narration.strip():
            issues.append(f"Escena {i}: falta narration.")
    total = sum(_words(s.narration) for s in c.scenes)
    if not 45 <= total <= 110:
        issues.append(f"La narración suma {total} palabras; debe estar entre 55 y 95.")
    texts = [c.caption] + [t for s in c.scenes for t in (s.on_screen, s.sub, s.narration, *s.bullets)]
    return issues + _tuteo(texts)


def lint_carousel(c: CarouselCopy) -> list[str]:
    issues = []
    if c.slides[0].kind != "cover":
        issues.append('La slide 1 debe ser kind "cover".')
    if c.slides[-1].kind != "cta":
        issues.append('La última slide debe ser kind "cta".')
    for i, s in enumerate(c.slides, 1):
        if s.kind == "content" and _words(s.body) < 10:
            issues.append(f"Slide {i}: el body debe tener entre 15 y 35 palabras.")
        if _words(s.heading) > 10:
            issues.append(f"Slide {i}: heading de máximo 9 palabras.")
    texts = [c.caption] + [t for s in c.slides for t in (s.heading, s.body)]
    return issues + _tuteo(texts)


def repair_reel(c: ReelCopy) -> ReelCopy:
    """Arreglos mínimos de estructura cuando el LLM no corrige solo."""
    c.scenes[0].layout = "hook"
    c.scenes[-1].layout = "cta"
    for s in c.scenes[1:-1]:
        if s.layout in ("hook", "cta") or (s.layout == "list" and len(s.bullets) < 2):
            s.layout = "statement"
    return c


def repair_carousel(c: CarouselCopy) -> CarouselCopy:
    c.slides[0].kind = "cover"
    c.slides[-1].kind = "cta"
    for s in c.slides[1:-1]:
        s.kind = "content"
    return c
