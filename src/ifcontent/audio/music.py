"""Biblioteca local de música. Solo se usan pistas con licencia comercial registrada."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from ..core.config import ROOT, load_config

REQUIRED = ("id", "file", "license", "license_url", "source", "commercial_use")


@dataclass
class Track:
    id: str
    path: Path
    title: str
    license: str
    attribution: str
    moods: list[str]


def load_library() -> list[Track]:
    lib_path = ROOT / load_config().settings["music"]["library"]
    data = yaml.safe_load(lib_path.read_text(encoding="utf-8")) or {}
    tracks = []
    for t in data.get("tracks", []):
        if any(not t.get(k) for k in REQUIRED) or t["commercial_use"] is not True:
            continue  # pista sin licencia completa: no se usa nunca
        path = lib_path.parent / t["file"]
        if path.exists():
            tracks.append(Track(t["id"], path, t.get("title", t["id"]), t["license"], t.get("attribution", ""), t.get("moods", [])))
    return tracks


def choose_track(pillar: str, seed: int) -> Track:
    tracks = load_library()
    if not tracks:
        raise RuntimeError("No hay pistas con licencia válida en la biblioteca de música")
    moods = set(load_config().pillars[pillar].get("music_moods", []))
    matching = [t for t in tracks if moods & set(t.moods)] or tracks
    return matching[seed % len(matching)]  # rota entre pistas compatibles


def get_track(track_id: str) -> Track | None:
    return next((t for t in load_library() if t.id == track_id), None)
