"""Genera música y efectos chiptune originales por síntesis (100 % propios, sin licencias de terceros).

Uso: .venv/Scripts/python tools/make_chiptune.py
Escribe assets/sfx/8bit/*.wav y assets/music/chiptune-bodega.wav
"""
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 48000
ROOT = Path(__file__).resolve().parents[1]
SFX = ROOT / "assets" / "sfx" / "8bit"
rng = np.random.default_rng(8)
NOTAS = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def hz(nota: str) -> float:
    nombre, octava = nota[:-1], int(nota[-1])
    return 440.0 * 2 ** ((NOTAS[nombre] + 12 * (octava + 1) - 69) / 12)


def cuadrada(f: float, seg: float, ancho: float = 0.25) -> np.ndarray:
    t = np.arange(int(seg * SR)) / SR
    return np.where((t * f) % 1 < ancho, 1.0, -1.0)


def triangular(f: float, seg: float) -> np.ndarray:
    t = np.arange(int(seg * SR)) / SR
    return 4 * np.abs((t * f) % 1 - 0.5) - 1


def ruido(seg: float, paso: int = 12) -> np.ndarray:
    n = int(seg * SR)
    return np.repeat(rng.choice([-1.0, 1.0], n // paso + 1), paso)[:n]


def env(x: np.ndarray, caida: float = 8.0) -> np.ndarray:
    t = np.arange(len(x)) / SR
    salida = x * np.exp(-t * caida)
    borde = min(len(x), 96)
    salida[-borde:] *= np.linspace(1, 0, borde)
    return salida


def seq(notas: list[str], dur: float, ancho: float = 0.25, caida: float = 5.0) -> np.ndarray:
    return np.concatenate([env(cuadrada(hz(n), dur, ancho), caida) for n in notas])


def barrido(f0: float, f1: float, seg: float) -> np.ndarray:
    t = np.arange(int(seg * SR)) / SR
    fase = np.cumsum(f0 * (f1 / f0) ** (t / seg)) / SR
    return np.where(fase % 1 < 0.5, 1.0, -1.0)


def guardar(nombre: str, x: np.ndarray, pico: float = 0.7) -> None:
    sf.write(SFX / f"{nombre}.wav", (x / (np.abs(x).max() + 1e-9) * pico).astype(np.float32), SR)


def efectos() -> None:
    SFX.mkdir(parents=True, exist_ok=True)
    guardar("seleccion", seq(["A5", "D6"], 0.05, 0.5, 18))
    guardar("punto", seq(["E6", "G#6", "E7"], 0.055, 0.25, 12))
    guardar("golpe", env(0.7 * barrido(500, 70, 0.3) + 0.5 * ruido(0.3, 20), 5))
    guardar("caida", env(barrido(1200, 110, 0.6), 2))
    guardar("derrota", seq(["A4", "E4", "F4", "D4", "C#4", "A3"], 0.17, 0.5, 2.5), 0.75)
    guardar("cuenta", seq(["D5"], 0.07, 0.5, 20), 0.5)
    guardar("poder", seq(["D5", "F#5", "A5", "D6", "F#6", "A6"], 0.07, 0.25, 4))
    guardar("nivel", seq(["G5", "B5", "D6", "G6", "D6", "G6"], 0.09, 0.5, 3), 0.75)
    guardar("alerta", np.concatenate([env(cuadrada(1320, 0.09, 0.5), 3), np.zeros(int(0.05 * SR)), env(cuadrada(1320, 0.09, 0.5), 3)]), 0.5)


def musica() -> None:
    bpm, compases = 124, 16
    negra = 60 / bpm
    sem = negra / 4
    n_sem = 16 * compases
    total = int(n_sem * sem * SR) + SR
    pista = np.zeros(total)
    # Progresión propia en La menor. Sin melodía: el protagonista es la voz.
    acordes = [("A", "C", "E"), ("F", "A", "C"), ("C", "E", "G"), ("G", "B", "D"),
               ("A", "C", "E"), ("D", "F", "A"), ("F", "A", "C"), ("E", "G#", "B")]
    bajos = ["A2", "F2", "C3", "G2", "A2", "D3", "F2", "E2"]
    patron = [0, 1, 2, 1, 0, 2, 1, 2, 0, 1, 2, 1, 2, 1, 0, 1]

    def poner(x: np.ndarray, en_sem: int, vol: float) -> None:
        i = int(en_sem * sem * SR)
        pista[i:i + len(x)] += x[: len(pista) - i] * vol

    for c in range(compases):
        a = c % 8
        for s in range(16):
            idx = c * 16 + s
            nombre = acordes[a][patron[s]]
            poner(env(cuadrada(hz(f"{nombre}5"), sem * 0.95, 0.25), 9), idx, 0.20)
            if s in (0, 3, 6, 8, 11, 14):
                poner(env(triangular(hz(bajos[a]), sem * 1.8), 2), idx, 0.55)
            if s % 4 == 2:
                poner(env(ruido(sem * 0.5, 4), 35), idx, 0.14)
            if s in (4, 12) and c >= 2:
                poner(env(ruido(sem, 14), 16), idx, 0.26)
            if s in (0, 8) and c >= 2:
                poner(env(barrido(170, 55, sem * 1.2), 10), idx, 0.45)
    pista = pista[: int(n_sem * sem * SR)]
    sf.write(ROOT / "assets" / "music" / "chiptune-bodega.wav", (pista / np.abs(pista).max() * 0.85).astype(np.float32), SR)


if __name__ == "__main__":
    efectos()
    musica()
    print("ok")
