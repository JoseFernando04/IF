"""Sonido característico de IF Techworks, sintetizado por código (100 % propio, sin licencias de terceros).

Genera:
  assets/music/if-firma.wav       pista de ~31 s (92 bpm, Re mayor) para posts y fotos en IG/TikTok
  assets/music/if-firma.mp3       la misma pista en mp3, lista para subir
  assets/sfx/if-logo.wav          el logo sonoro solo (~3 s): campana La-Re-Fa# ("I-F Tech-works")

Uso: .venv/Scripts/python tools/make_firma.py
"""
from pathlib import Path
import subprocess
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

SR = 48000
ROOT = Path(__file__).resolve().parents[1]
rng = np.random.default_rng(4)
NOTAS = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
BPM = 92
NEGRA = 60 / BPM
COMPAS = 4 * NEGRA


def hz(nota: str) -> float:
    nombre, octava = nota[:-1], int(nota[-1])
    return 440.0 * 2 ** ((NOTAS[nombre] + 12 * (octava + 1) - 69) / 12)


def t_(seg: float) -> np.ndarray:
    return np.arange(int(seg * SR)) / SR


def fin_suave(x: np.ndarray, ms: float = 8) -> np.ndarray:
    n = min(len(x), int(ms / 1000 * SR))
    x[-n:] *= np.linspace(1, 0, n)
    return x


def piano(f: float, seg: float) -> np.ndarray:
    """Piano eléctrico por FM (ratio 1:1, índice que decae), cálido."""
    t = t_(seg)
    indice = 1.6 * np.exp(-t * 4)
    x = np.sin(2 * np.pi * f * t + indice * np.sin(2 * np.pi * f * t))
    x += 0.15 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 6)
    ataque = np.minimum(1, t / 0.004)
    return fin_suave(x * ataque * np.exp(-t * 1.1))


def campana(f: float, seg: float) -> np.ndarray:
    """Campana FM (ratio 3.5): el timbre del logo."""
    t = t_(seg)
    indice = 2.2 * np.exp(-t * 2.5)
    x = np.sin(2 * np.pi * f * t + indice * np.sin(2 * np.pi * 3.5 * f * t))
    x += 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3)
    ataque = np.minimum(1, t / 0.002)
    return fin_suave(x * ataque * np.exp(-t * 1.6))


def bajo(f: float, seg: float) -> np.ndarray:
    t = t_(seg)
    x = np.sin(2 * np.pi * f * t) + 0.2 * np.sin(2 * np.pi * 2 * f * t)
    return fin_suave(x * np.minimum(1, t / 0.01) * np.exp(-t * 1.5), 30)


def bombo(seg: float = 0.45) -> np.ndarray:
    t = t_(seg)
    fase = 2 * np.pi * np.cumsum(45 + 90 * np.exp(-t * 28)) / SR
    return fin_suave(np.sin(fase) * np.exp(-t * 9))


def aro(seg: float = 0.25) -> np.ndarray:
    """Golpe de aro suave (rimshot) en vez de caja: más limpio."""
    t = t_(seg)
    x = 0.6 * np.sin(2 * np.pi * 820 * t) * np.exp(-t * 60)
    ruido = rng.standard_normal(len(t))
    x += 0.5 * np.diff(ruido, prepend=0) * np.exp(-t * 40)
    return fin_suave(x)


def shaker(seg: float = 0.09) -> np.ndarray:
    t = t_(seg)
    ruido = np.diff(np.diff(rng.standard_normal(len(t)), prepend=0), prepend=0)
    return fin_suave(ruido * np.minimum(1, t / 0.01) * np.exp(-t * 45))


def reverb(x: np.ndarray, seg: float = 1.4, mezcla: float = 0.22) -> np.ndarray:
    t = t_(seg)
    ir = rng.standard_normal(len(t)) * np.exp(-t * 4.5)
    ir[: int(0.012 * SR)] = 0  # pre-delay
    n = len(x) + len(ir)
    tam = 1 << (n - 1).bit_length()
    humedo = np.fft.irfft(np.fft.rfft(x, tam) * np.fft.rfft(ir, tam), tam)[: len(x)]
    humedo *= np.abs(x).max() / (np.abs(humedo).max() + 1e-9)
    return x + mezcla * humedo


class Pista:
    def __init__(self, seg: float):
        self.x = np.zeros(int(seg * SR))

    def poner(self, sonido: np.ndarray, en: float, vol: float) -> None:
        i = int(en * SR)
        if i >= len(self.x):
            return
        trozo = sonido[: len(self.x) - i]
        self.x[i:i + len(trozo)] += trozo * vol


def logo(p: Pista, en: float, vol: float = 0.30) -> None:
    """Motivo de IF: La5 · Re6 (corcheas) → Fa#6 (larga). Se lee como "I · F · Tech-works"."""
    corchea = NEGRA / 2
    for k, (nota, dur) in enumerate([("A5", 1.2), ("D6", 1.2), ("F#6", 2.6)]):
        p.poner(campana(hz(nota), dur), en + k * corchea, vol)


ACORDES = [  # Sol maj7 · La · Fa#m7 · Si m7 (Re mayor, cálido y optimista)
    (["G3", "B3", "D4", "F#4"], "G2"),
    (["A3", "C#4", "E4", "A4"], "A2"),
    (["F#3", "A3", "C#4", "E4"], "F#2"),
    (["B3", "D4", "F#4", "A4"], "B1"),
]


def firma() -> np.ndarray:
    compases = 12
    p = Pista(compases * COMPAS + 3.0)
    for c in range(compases):
        t0 = c * COMPAS
        notas, b = ACORDES[c % 4] if c < compases - 1 else (["D4", "F#4", "A4", "E5"], "D2")
        ultimo = c == compases - 1
        # Acordes: golpe en 1 y anticipación en el "y" del 2 (groove relajado)
        for en, vol in ([(0, 0.24)] if ultimo else [(0, 0.24), (1.5 * NEGRA, 0.15)]):
            for k, n in enumerate(notas):
                p.poner(piano(hz(n), 3.5 if ultimo else 1.6), t0 + en + k * 0.012, vol)
        if c >= 1:
            p.poner(bajo(hz(b), 3.0 if ultimo else COMPAS * 0.9), t0, 0.55)
        if 2 <= c < compases - 1:
            for pulso in (0, 2.5):
                p.poner(bombo(), t0 + pulso * NEGRA, 0.55)
            for pulso in (1, 3):
                p.poner(aro(), t0 + pulso * NEGRA, 0.14)
            for s in range(8):
                p.poner(shaker(), t0 + s * NEGRA / 2, 0.05 if s % 2 else 0.03)
    for c in (0, 4, 8, compases - 1):
        logo(p, c * COMPAS + (0.0 if c == compases - 1 else 2 * NEGRA))
    x = reverb(p.x)
    x[-int(1.5 * SR):] *= np.linspace(1, 0, int(1.5 * SR)) ** 2
    return x


def solo_logo() -> np.ndarray:
    p = Pista(3.2)
    for k, n in enumerate(["D4", "F#4", "A4", "E5"]):
        p.poner(piano(hz(n), 3.0), NEGRA + k * 0.012, 0.13)
    p.poner(bajo(hz("D2"), 2.6), NEGRA, 0.35)
    logo(p, 0.0, 0.45)
    x = reverb(p.x)
    x[-int(0.4 * SR):] *= np.linspace(1, 0, int(0.4 * SR))
    return x


def guardar(ruta: Path, x: np.ndarray, pico_db: float = -1.5) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    x = x / np.abs(x).max() * 10 ** (pico_db / 20)
    sf.write(ruta, np.stack([x, x], 1).astype(np.float32), SR)


if __name__ == "__main__":
    from ifcontent.video.ffmpeg import ffmpeg_bin

    pista = ROOT / "assets" / "music" / "if-firma.wav"
    guardar(pista, firma())
    guardar(ROOT / "assets" / "sfx" / "if-logo.wav", solo_logo())
    subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", str(pista), "-b:a", "256k",
                    str(pista.with_suffix(".mp3"))], check=True)
    print("ok")
