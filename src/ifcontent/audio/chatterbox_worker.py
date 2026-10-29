"""Proceso aislado para Chatterbox (corre en .venv-tts, que tiene PyTorch con CUDA).

Entrada (stdin, JSON): {"texts": [...], "out_dir": "...", "language": "es", "reference": ruta|null,
                         "exaggeration": 0.5, "cfg_weight": 0.5}
Salida: un WAV por texto (000.wav, 001.wav, ...) en out_dir.
"""
import json
import sys
from pathlib import Path

import torch
import torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS


def main() -> None:
    job = json.loads(sys.stdin.read())
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = ChatterboxMultilingualTTS.from_pretrained(device=device)
    out = Path(job["out_dir"])
    out.mkdir(parents=True, exist_ok=True)
    for i, text in enumerate(job["texts"]):
        wav = model.generate(
            text,
            language_id=job.get("language", "es"),
            audio_prompt_path=job.get("reference"),
            exaggeration=job.get("exaggeration", 0.5),
            cfg_weight=job.get("cfg_weight", 0.5),
        )
        torchaudio.save(str(out / f"{i:03d}.wav"), wav.cpu(), model.sr)
        print(f"{i + 1}/{len(job['texts'])}", flush=True)


if __name__ == "__main__":
    main()
