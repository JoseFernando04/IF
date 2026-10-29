"""Línea de tiempo del reel: duración de cada escena según su voz en off, y subtítulos sincronizados."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np

from ..audio.tts import SAMPLE_RATE, TTSEngine
from ..core.models import ReelCopy, Scene

VOICE_LEAD_S = 0.25   # la voz entra un poco después que la escena
CTA_HOLD_S = 1.6      # la última escena se queda un rato en pantalla


@dataclass
class TimedScene:
    scene: Scene
    start: float
    end: float


@dataclass
class Caption:
    text: str
    start: float
    end: float


@dataclass
class Timeline:
    scenes: list[TimedScene]
    captions: list[Caption]
    duration: float
    voice: np.ndarray | None = field(default=None, repr=False)


def _chunks(text: str, max_words: int = 5, max_chars: int = 30) -> list[str]:
    words = re.sub(r"[*_#]", "", text).split()
    out, cur = [], []
    for w in words:
        if cur and (len(cur) >= max_words or len(" ".join(cur + [w])) > max_chars):
            out.append(" ".join(cur))
            cur = []
        cur.append(w)
        if re.search(r"[.,;:?!]$", w) and len(cur) >= 2:
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def _reading_time(text: str) -> float:
    return len(text.split()) / 2.7 + 0.6


def build_timeline(copy: ReelCopy, tts: TTSEngine | None, settings: dict) -> Timeline:
    padding, min_scene = settings["scene_padding_s"], settings["min_scene_s"]
    scenes: list[TimedScene] = []
    captions: list[Caption] = []
    clips: list[tuple[float, np.ndarray]] = []
    voices = tts.synth_many([s.narration for s in copy.scenes]) if tts else []
    t = 0.0
    for i, scene in enumerate(copy.scenes):
        last = i == len(copy.scenes) - 1
        if tts:
            audio = voices[i]
            voice_dur = len(audio) / SAMPLE_RATE
            clips.append((t + VOICE_LEAD_S, audio))
        else:
            voice_dur = _reading_time(scene.narration or scene.on_screen)
        dur = max(min_scene, VOICE_LEAD_S + voice_dur + padding) + (CTA_HOLD_S if last else 0)
        scenes.append(TimedScene(scene, t, t + dur))

        # Subtítulos repartidos proporcionalmente al largo de cada fragmento.
        parts = _chunks(scene.narration)
        total_chars = sum(len(p) for p in parts) or 1
        c = t + VOICE_LEAD_S
        for p in parts:
            d = voice_dur * len(p) / total_chars
            captions.append(Caption(p, c, c + d))
            c += d
        t += dur

    min_total = settings["min_seconds"]
    if t < min_total:  # alarga la escena final para cumplir el mínimo
        scenes[-1].end += min_total - t
        t = min_total

    voice = None
    if clips:
        voice = np.zeros(int(t * SAMPLE_RATE) + SAMPLE_RATE, dtype=np.float32)
        for start, audio in clips:
            i0 = int(start * SAMPLE_RATE)
            voice[i0 : i0 + len(audio)] += audio
        voice = voice[: int(t * SAMPLE_RATE)]
    return Timeline(scenes, captions, round(t, 3), voice)
