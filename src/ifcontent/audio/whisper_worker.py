"""Transcripción local con faster-whisper (MIT). Corre en .venv-tts (PyTorch + CUDA).

Entrada (stdin, JSON): {"files": [...], "model": "medium", "language": "es"}
Salida (stdout, JSON): {archivo: {"text": ..., "segments": [{"start", "end", "text", "words": [...]}]}}
"""
import json
import os
import sys
from pathlib import Path

import torch  # trae las DLL de CUDA 12 (cublas) que CTranslate2 necesita en Windows

if hasattr(os, "add_dll_directory"):
    os.add_dll_directory(str(Path(torch.__file__).parent / "lib"))

from faster_whisper import WhisperModel  # noqa: E402


def main() -> None:
    job = json.loads(sys.stdin.read())
    try:
        model = WhisperModel(job.get("model", "medium"), device="cuda", compute_type="int8_float16")
    except Exception:  # sin GPU disponible
        model = WhisperModel(job.get("model", "medium"), device="cpu", compute_type="int8")
    out = {}
    for f in job["files"]:
        segs, _ = model.transcribe(f, language=job.get("language", "es"), word_timestamps=True, vad_filter=True)
        segs = list(segs)
        out[f] = {
            "text": " ".join(s.text.strip() for s in segs),
            "segments": [{"start": s.start, "end": s.end, "text": s.text.strip(),
                          "words": [{"start": w.start, "end": w.end, "word": w.word} for w in (s.words or [])]}
                         for s in segs],
        }
    sys.stdout.write(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
