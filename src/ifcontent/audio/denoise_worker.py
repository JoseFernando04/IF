"""Limpieza de voz con IA, en .venv-tts:
- WPE (nara_wpe, MIT): reduce el eco/reverberación del cuarto (opcional, "dereverb").
- DeepFilterNet3 (MIT/Apache-2.0): reduce el ruido de fondo.

Entrada (stdin, JSON): {"pairs": [[entrada, salida], ...], "dereverb": true}
"""
import json
import sys

import numpy as np
import torch
import torchaudio
from df.enhance import enhance, init_df
from nara_wpe.utils import istft, stft
from nara_wpe.wpe import wpe


def quitar_eco(x: np.ndarray) -> np.ndarray:
    y = stft(x[None], size=512, shift=128).transpose(2, 0, 1)
    z = wpe(y, taps=10, delay=3, iterations=5, statistics_mode="full").transpose(1, 2, 0)
    z = istft(z, size=512, shift=128)[0][: len(x)]
    return z / (np.abs(z).max() + 1e-9) * np.abs(x).max()


def main() -> None:
    job = json.loads(sys.stdin.read())
    model, state, _ = init_df()
    sr = state.sr()
    for src, dst in job["pairs"]:
        audio, in_sr = torchaudio.load(src)
        audio = audio.mean(0, keepdim=True)
        if in_sr != sr:
            audio = torchaudio.functional.resample(audio, in_sr, sr)
        if job.get("dereverb"):
            audio = torch.from_numpy(quitar_eco(audio[0].double().numpy())).float()[None]
        torchaudio.save(dst, enhance(model, state, audio).cpu(), sr)
        print(f"ok {dst}", flush=True)


if __name__ == "__main__":
    main()
