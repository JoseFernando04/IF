"""Clips de video con IA vía Higgsfield (Seedance 2.5).

Cada llamada a `generar` es una generación DE PAGO. La credencial `HF_KEY` (key-id:key-secret)
se lee del .env en tiempo de ejecución; nunca se imprime ni se registra.

Los clips son solo imagen de apoyo (b-roll): la voz de los reels sigue siendo la del equipo.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import httpx

from ifcontent.core.config import load_config

log = logging.getLogger(__name__)

MODELO_TEXTO = "bytedance/seedance-2.5/text-to-video"
RESOLUCIONES = ("480p", "720p", "1080p")
ASPECTOS = ("16:9", "4:3", "1:1", "3:4", "9:16", "21:9")


class GeneracionFallida(RuntimeError):
    """La solicitud terminó sin video (falló, fue cancelada o moderada)."""


def _url_video(resultado: dict[str, Any]) -> str | None:
    video = resultado.get("video")
    if isinstance(video, dict):
        return video.get("url")
    if isinstance(video, str):
        return video
    videos = resultado.get("videos")
    if isinstance(videos, list) and videos:
        primero = videos[0]
        return primero.get("url") if isinstance(primero, dict) else primero
    return None


def generar(
    prompt: str,
    *,
    duracion: int = 5,
    resolucion: str = "720p",
    aspecto: str = "9:16",
    audio: bool = False,
    modelo: str = MODELO_TEXTO,
    destino: Path | None = None,
) -> dict[str, Any]:
    """Genera un clip y espera a que termine. Devuelve {request_id, url, archivo}.

    Lanza GeneracionFallida si la solicitud no termina en `completed` con un video.
    """
    if not 1 <= duracion <= 30:
        raise ValueError("duracion debe estar entre 1 y 30 segundos")
    if resolucion not in RESOLUCIONES:
        raise ValueError(f"resolucion debe ser una de {RESOLUCIONES}")
    if aspecto not in ASPECTOS:
        raise ValueError(f"aspecto debe ser uno de {ASPECTOS}")
    argumentos: dict[str, Any] = {"prompt": prompt, "duration": duracion, "resolution": resolucion, "aspect_ratio": aspecto}
    if "seedance" in modelo:
        argumentos["generate_audio"] = audio

    load_config()  # carga el .env e instala el filtro que enmascara credenciales en los logs
    if not os.getenv("HF_KEY"):
        raise GeneracionFallida("Falta HF_KEY en el .env (formato key-id:key-secret).")

    import higgsfield_client  # import tardío: solo hace falta si se usa este motor

    ids: list[str] = []
    try:
        resultado = higgsfield_client.subscribe(
            modelo,
            arguments=argumentos,
            on_enqueue=ids.append,
            on_queue_update=lambda estado: log.info("Higgsfield: %s", type(estado).__name__),
        )
    except higgsfield_client.HiggsfieldClientError as exc:
        raise GeneracionFallida(f"Higgsfield rechazó la solicitud: {exc}") from exc

    request_id = ids[0] if ids else resultado.get("request_id")
    estado = str(resultado.get("status", "")).lower()
    url = _url_video(resultado)
    if estado != "completed" or not url:
        motivo = {"nsfw": "moderada por contenido", "canceled": "cancelada", "failed": "falló"}.get(estado, estado or "sin estado")
        detalle = resultado.get("error") or resultado.get("detail") or ""
        raise GeneracionFallida(f"Solicitud {request_id}: {motivo}. {detalle}".strip())

    archivo = None
    if destino is not None:
        destino.parent.mkdir(parents=True, exist_ok=True)
        with httpx.stream("GET", url, timeout=300, follow_redirects=True) as r:
            r.raise_for_status()
            with destino.open("wb") as f:
                for trozo in r.iter_bytes():
                    f.write(trozo)
        archivo = str(destino)
    return {"request_id": request_id, "url": url, "archivo": archivo}
