"""Música de fondo para Flor de Loto Spa, sintetizada por código (propia de IF para este cliente, sin licencias de terceros).

Ambiente tranquilo: colchón cálido (acordes lentos en Fa mayor), cuenco tibetano sintético, arpegio suave tipo
arpa / kalimba y un aire de agua muy bajo. Sin pulso marcado, para que la voz de José quede al frente.

Genera:
  campanas/flor-de-loto-spa/musica/flor-de-loto-calma.wav  (~80 s, estéreo 48 kHz)
  campanas/flor-de-loto-spa/musica/flor-de-loto-calma.mp3

Uso: .venv/Scripts/python campanas/flor-de-loto-spa/herramientas/make_musica.py
No usa nada del sonido de IF (if-firma / if-logo).
"""
from pathlib import Path
import subprocess
import sys

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from ifcontent.video.ffmpeg import ffmpeg_bin  # noqa: E402

SR = 48000
DUR = 80.0
CHORD_S = 10.0
rng = np.random.default_rng(17)
NOTAS = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def hz(n: str) -> float:
    return 440.0 * 2 ** ((NOTAS[n[:-1]] + 12 * (int(n[-1]) + 1) - 69) / 12)


def t_(seg: float) -> np.ndarray:
    return np.arange(int(seg * SR)) / SR


def lowpass_fft(x: np.ndarray, corte: float) -> np.ndarray:
    f = np.fft.rfft(x)
    fr = np.fft.rfftfreq(len(x), 1 / SR)
    f *= 1 / np.sqrt(1 + (fr / corte) ** 4)
    return np.fft.irfft(f, len(x))


def pad(nota: str, seg: float) -> np.ndarray:
    """Colchón: 3 osciladores levemente desafinados, ataque y salida lentos."""
    t = t_(seg)
    f = hz(nota)
    x = sum(np.sin(2 * np.pi * f * (1 + d) * t + rng.uniform(0, 6.28)) for d in (-0.003, 0, 0.0035))
    x += 0.25 * sum(np.sin(2 * np.pi * 2 * f * (1 + d) * t) for d in (-0.002, 0.002))
    x += 0.08 * np.sin(2 * np.pi * 3 * f * t)
    trem = 1 + 0.08 * np.sin(2 * np.pi * 0.17 * t + rng.uniform(0, 6.28))
    env = np.minimum(1, t / 3.2) * np.minimum(1, (seg - t) / 3.2)
    return x * trem * env


def cuenco(f: float, seg: float) -> np.ndarray:
    """Cuenco tibetano: parciales inarmónicos con batido lento."""
    t = t_(seg)
    x = np.zeros_like(t)
    for r, a, dec in ((1, 1, 0.35), (2.71, 0.45, 0.6), (5.15, 0.2, 1.0), (8.4, 0.08, 1.6)):
        x += a * np.sin(2 * np.pi * f * r * t) * (1 + 0.3 * np.sin(2 * np.pi * (0.9 * r) * t)) * np.exp(-t * dec)
    return x * np.minimum(1, t / 0.01)


def arpa(f: float, seg: float) -> np.ndarray:
    """Karplus-Strong suave (arpa / kalimba)."""
    n = int(seg * SR)
    p = int(SR / f)
    buf = rng.uniform(-1, 1, p)
    buf = np.convolve(buf, np.ones(4) / 4, mode="same")
    out = np.empty(n)
    for i in range(n):
        v = buf[i % p]
        out[i] = v
        buf[i % p] = 0.4985 * (v + buf[(i + 1) % p])
    return out * np.minimum(1, np.arange(n) / (0.003 * SR))


def reverb(x: np.ndarray, seg: float = 4.5, mezcla: float = 0.35) -> np.ndarray:
    t = t_(seg)
    ir = rng.normal(0, 1, len(t)) * np.exp(-t * 6.9 / seg)
    ir = lowpass_fft(ir, 5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    n = len(x) + len(ir)
    m = 1 << (n - 1).bit_length()
    w = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[:len(x)]
    return (1 - mezcla) * x + mezcla * w * 0.9


def poner(pista: np.ndarray, x: np.ndarray, t0: float, g: float) -> None:
    i = int(t0 * SR)
    j = min(len(pista), i + len(x))
    pista[i:j] += g * x[:j - i]


def main() -> None:
    n = int(DUR * SR)
    L = np.zeros(n)
    R = np.zeros(n)
    # Fmaj9 · Dm9 · Bbmaj7 · C6/9 (dos vueltas)
    acordes = [["F3", "A3", "C4", "E4", "G4"], ["D3", "F3", "A3", "C4", "E4"],
               ["A#2", "D3", "F3", "A3", "C4"], ["C3", "E3", "G3", "A3", "D4"]] * 2
    bajos = ["F2", "D2", "A#1", "C2"] * 2
    for k, (ac, bajo) in enumerate(zip(acordes, bajos)):
        t0 = k * CHORD_S - (1.6 if k else 0)
        seg = CHORD_S + 3.2
        for j, nota in enumerate(ac):
            x = pad(nota, seg)
            pan = 0.5 + 0.35 * np.sin(j * 1.9 + k)
            poner(L, x, max(0, t0), 0.05 * (1 - pan))
            poner(R, x, max(0, t0), 0.05 * pan)
        b = pad(bajo, seg)
        poner(L, b, max(0, t0), 0.06)
        poner(R, b, max(0, t0), 0.06)
        # arpegio lento: 5 notas del acorde, una octava arriba, espaciadas
        notas = [n_[:-1] + str(int(n_[-1]) + 1) for n_ in ac]
        orden = [0, 2, 4, 3, 1] if k % 2 == 0 else [4, 2, 3, 0, 2]
        for s, idx in enumerate(orden):
            ts = k * CHORD_S + 1.2 + s * 1.7 + rng.uniform(-0.08, 0.08)
            x = arpa(hz(notas[idx]), 4.0)
            pan = rng.uniform(0.25, 0.75)
            poner(L, x, ts, 0.10 * (1 - pan))
            poner(R, x, ts, 0.10 * pan)
    # cuencos: al inicio de cada 2 acordes
    for ts, f in ((0.4, hz("F3")), (20.3, hz("C4")), (40.2, hz("F3")), (60.4, hz("A3"))):
        x = cuenco(f, 12)
        poner(L, x, ts, 0.07)
        poner(R, x, ts + 0.012, 0.07)
    # aire de agua muy bajo
    aire = lowpass_fft(rng.normal(0, 1, n), 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.05 * np.arange(n) / SR))
    L += 0.012 * aire
    R += 0.012 * np.roll(aire, 9000)
    L, R = reverb(L), reverb(R)
    # entrada y salida
    tt = np.arange(n) / SR
    env = np.minimum(1, tt / 2.5) * np.minimum(1, (DUR - tt) / 6)
    st = np.stack([L * env, R * env], axis=1)
    st *= 0.89 / np.max(np.abs(st))  # pico -1 dBFS
    out = ROOT / "campanas" / "flor-de-loto-spa" / "musica"
    out.mkdir(parents=True, exist_ok=True)
    wav = out / "flor-de-loto-calma.wav"
    sf.write(wav, st, SR, subtype="PCM_24")
    subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", str(wav), "-b:a", "192k",
                    str(out / "flor-de-loto-calma.mp3")], check=True)
    print("OK", wav, f"({DUR:.0f} s)")


if __name__ == "__main__":
    main()
