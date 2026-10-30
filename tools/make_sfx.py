"""Genera los efectos de sonido de marca por síntesis (100 % propios, sin licencias de terceros).

Uso: .venv/Scripts/python tools/make_sfx.py  → escribe assets/sfx/*.wav
"""
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 48000
OUT = Path(__file__).resolve().parents[1] / "assets" / "sfx"
rng = np.random.default_rng(7)


def t(sec: float) -> np.ndarray:
    return np.arange(int(sec * SR)) / SR


def lowpass(x: np.ndarray, alpha: np.ndarray | float) -> np.ndarray:
    y = np.zeros_like(x)
    a = np.broadcast_to(alpha, x.shape)
    for i in range(1, len(x)):
        y[i] = y[i - 1] + a[i] * (x[i] - y[i - 1])
    return y


def norm(x: np.ndarray, peak: float = 0.8) -> np.ndarray:
    return (x / (np.abs(x).max() + 1e-9) * peak).astype(np.float32)


def whoosh(sec: float = 0.45) -> np.ndarray:
    tt = t(sec)
    env = np.sin(np.pi * tt / sec) ** 2
    sweep = 0.02 + 0.35 * (tt / sec) ** 1.5           # el filtro se abre: sensación de paso
    n = rng.standard_normal(len(tt))
    return norm(lowpass(n, sweep) * env, 0.6)


def thud(sec: float = 0.35) -> np.ndarray:
    tt = t(sec)
    f = 95 * np.exp(-tt * 9) + 45                        # golpe grave con caída de tono
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 14)
    click = lowpass(rng.standard_normal(len(tt)), 0.4) * np.exp(-tt * 120) * 0.4
    return norm(body + click, 0.9)


def pop(sec: float = 0.12) -> np.ndarray:
    tt = t(sec)
    f = 900 * np.exp(-tt * 30) + 300
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 45), 0.55)


def tick(sec: float = 0.05) -> np.ndarray:
    tt = t(sec)
    return norm(np.sin(2 * np.pi * 2400 * tt) * np.exp(-tt * 160) + rng.standard_normal(len(tt)) * np.exp(-tt * 300) * 0.3, 0.4)


def marker(sec: float = 0.55) -> np.ndarray:
    """Trazo de marcador sobre papel: ruido filtrado con micro-golpes irregulares."""
    tt = t(sec)
    n = rng.standard_normal(len(tt))
    grain = lowpass(n, 0.55) - lowpass(n, 0.08)          # banda media, como fricción
    wobble = 0.6 + 0.4 * np.sin(2 * np.pi * 11 * tt + rng.uniform(0, 6)) ** 2
    env = np.minimum(1, tt / 0.03) * np.minimum(1, (sec - tt) / 0.08)
    return norm(grain * wobble * env, 0.35)


def paper(sec: float = 0.3) -> np.ndarray:
    tt = t(sec)
    n = rng.standard_normal(len(tt))
    crackle = (rng.random(len(tt)) > 0.985) * rng.standard_normal(len(tt)) * 3
    return norm((lowpass(n, 0.3) * 0.5 + crackle) * np.exp(-tt * 9), 0.4)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in {"whoosh": whoosh, "thud": thud, "pop": pop, "tick": tick, "marker": marker, "paper": paper}.items():
        sf.write(OUT / f"{name}.wav", fn(), SR)
        print("✔", name)
