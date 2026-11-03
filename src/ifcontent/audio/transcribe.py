"""Transcripción local (Whisper vía faster-whisper en .venv-tts) y alineación de un guion con una grabación."""
from __future__ import annotations

import json
import re
import subprocess
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

from ..core.config import ROOT, load_config


def transcribir(files: list[Path], model: str = "medium") -> dict[str, dict]:
    python = ROOT / load_config().settings["tts"]["chatterbox"]["python"]
    worker = Path(__file__).with_name("whisper_worker.py")
    job = {"files": [str(f) for f in files], "model": model, "language": "es"}
    r = subprocess.run([str(python), str(worker)], input=json.dumps(job), capture_output=True,
                       text=True, encoding="utf-8", check=True)
    return json.loads(r.stdout)


def normalizar(texto: str) -> list[str]:
    t = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    return re.findall(r"[a-z0-9]+", t)


NUMEROS = set("cero uno una dos tres cuatro cinco seis siete ocho nueve diez once doce veinte treinta cuarenta cincuenta "
               "sesenta setenta ochenta noventa cien ciento doscientos trescientos quinientos mil".split())


def parecido(a: str, b: str) -> float:
    """Similitud de palabras (0-1). Ignora números, que el transcriptor escribe en cifras ("150")."""
    def limpiar(t: str) -> list[str]:
        return [w for w in normalizar(t) if not w.isdigit() and w not in NUMEROS]
    return SequenceMatcher(None, limpiar(a), limpiar(b)).ratio()


def cortes_por_frase(transcripcion: dict, frases: list[str], margen: float = 0.12) -> list[tuple[float, float]]:
    """Ubica cada frase del guion dentro de una grabación continua usando los tiempos de cada palabra."""
    palabras = [w for s in transcripcion["segments"] for w in s["words"]]
    dichas = [normalizar(w["word"])[0] if normalizar(w["word"]) else "" for w in palabras]
    guion, limites = [], []
    for f in frases:
        tokens = normalizar(f)
        limites.append((len(guion), len(guion) + len(tokens) - 1))
        guion.extend(tokens)
    # Mapa índice-del-guion → índice-de-palabra-dicha, con las coincidencias de la alineación.
    mapa: dict[int, int] = {}
    for bloque in SequenceMatcher(None, guion, dichas, autojunk=False).get_matching_blocks():
        for k in range(bloque.size):
            mapa[bloque.a + k] = bloque.b + k

    # Primera y última palabra dicha que coincidieron en cada frase.
    coincidencias = [[mapa[i] for i in range(a, b + 1) if i in mapa] for a, b in limites]
    cortes = []
    for n, (a, b) in enumerate(limites):
        m = coincidencias[n] or [0]
        ini, fin = min(m), max(m)
        # Si las primeras palabras no coincidieron (el transcriptor oyó otra cosa), la frase empieza
        # justo después de la anterior; si las últimas no coincidieron, termina justo antes de la siguiente.
        if a not in mapa:
            anteriores = [x for c in coincidencias[:n] for x in c]
            ini = (max(anteriores) + 1) if anteriores else 0
        if b not in mapa:
            siguientes = [x for c in coincidencias[n + 1:] for x in c]
            fin = (min(siguientes) - 1) if siguientes else len(palabras) - 1
        ini, fin = min(ini, len(palabras) - 1), max(min(fin, len(palabras) - 1), ini)
        cortes.append((max(0.0, palabras[ini]["start"] - margen), palabras[fin]["end"] + margen))
    # Sin solapes: cada frase termina, como mucho, donde empieza la siguiente.
    return [(s, min(e, cortes[i + 1][0]) if i + 1 < len(cortes) else e) for i, (s, e) in enumerate(cortes)]
