"""Ejemplo mínimo del SDK oficial de Higgsfield con Seedance 2.5 (texto a video).

OJO: cada ejecución es una generación de pago.
Uso: .venv/Scripts/python examples/higgsfield/main.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")  # HF_KEY=key-id:key-secret

import higgsfield_client  # noqa: E402


def main() -> int:
    try:
        resultado = higgsfield_client.subscribe(
            "bytedance/seedance-2.5/text-to-video",
            arguments={
                "prompt": "A cinematic scene at sunset",
                "duration": 5,
                "resolution": "720p",
                "aspect_ratio": "16:9",
            },
            on_enqueue=lambda rid: print(f"Solicitud en cola: {rid}", flush=True),
            on_queue_update=lambda estado: print(f"  estado: {type(estado).__name__}", flush=True),
        )
    except (higgsfield_client.HiggsfieldClientError, higgsfield_client.CredentialsMissedError) as exc:
        print(f"ERROR: la solicitud no se pudo enviar: {exc}", file=sys.stderr)
        return 1

    estado = str(resultado.get("status", "")).lower()
    video = resultado.get("video")
    url = video.get("url") if isinstance(video, dict) else video
    if estado != "completed" or not url:
        motivos = {"failed": "falló", "canceled": "fue cancelada", "nsfw": "fue moderada por contenido"}
        print(f"ERROR: la generación {motivos.get(estado, f'terminó en estado {estado!r}')}; no hay video.", file=sys.stderr)
        campos = {k: v for k, v in resultado.items() if k in ("status", "request_id", "error", "detail")}
        print(f"  respuesta: {campos}", file=sys.stderr)
        return 1

    print(f"Video listo: {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
