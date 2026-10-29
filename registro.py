"""Registro de piezas y su historial de estados (SQLite).

Estados: borrador -> en_revision -> aprobado -> publicado, y fallido desde cualquier paso.
Ninguna pieza llega a 'publicado' sin pasar por 'aprobado' con un aprobador explícito.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, tzinfo
from pathlib import Path

ESTADOS = ("borrador", "en_revision", "aprobado", "publicado", "fallido")

TRANSICIONES = {
    "borrador": {"en_revision", "fallido"},
    "en_revision": {"aprobado", "borrador", "fallido"},  # rechazar = volver a borrador con nota
    "aprobado": {"publicado", "fallido"},
    # reintentar publicación de una pieza aprobada: puede volver a fallar o publicarse (ver pipeline)
    "fallido": {"borrador", "publicado", "fallido"},
    "publicado": set(),
}

_ESQUEMA = """
CREATE TABLE IF NOT EXISTS piezas (
    id TEXT PRIMARY KEY,
    creada TEXT NOT NULL,
    actualizada TEXT NOT NULL,
    estado TEXT NOT NULL,
    pilar TEXT NOT NULL,
    tema TEXT NOT NULL,
    programada_para TEXT,
    carpeta TEXT NOT NULL,
    aprobada_por TEXT,
    datos TEXT NOT NULL DEFAULT '{}',
    error TEXT
);
CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pieza_id TEXT NOT NULL REFERENCES piezas(id),
    ts TEXT NOT NULL,
    de TEXT,
    a TEXT NOT NULL,
    actor TEXT NOT NULL,
    detalle TEXT
);
CREATE TABLE IF NOT EXISTS publicaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pieza_id TEXT NOT NULL REFERENCES piezas(id),
    red TEXT NOT NULL,
    ts TEXT NOT NULL,
    simulado INTEGER NOT NULL,
    post_id TEXT,
    url TEXT,
    UNIQUE (pieza_id, red)
);
"""


class TransicionInvalida(Exception):
    pass


class Registro:
    def __init__(self, ruta_db: Path, tz: tzinfo | None = None) -> None:
        self.tz = tz
        ruta_db.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(ruta_db)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(_ESQUEMA)

    def crear(self, pieza_id: str, pilar: str, tema: str, carpeta: Path, programada_para: str | None) -> None:
        ts = self._ahora()
        with self.db:
            self.db.execute(
                "INSERT INTO piezas (id, creada, actualizada, estado, pilar, tema, programada_para, carpeta)"
                " VALUES (?, ?, ?, 'borrador', ?, ?, ?, ?)",
                (pieza_id, ts, ts, pilar, tema, programada_para, str(carpeta)),
            )
            self.db.execute("INSERT INTO eventos (pieza_id, ts, de, a, actor, detalle) VALUES (?, ?, NULL, 'borrador', 'sistema', 'creada')",
                            (pieza_id, ts))

    def obtener(self, pieza_id: str) -> sqlite3.Row:
        fila = self.db.execute("SELECT * FROM piezas WHERE id = ?", (pieza_id,)).fetchone()
        if fila is None:
            raise KeyError(f"No existe la pieza {pieza_id}")
        return fila

    def cambiar_estado(self, pieza_id: str, nuevo: str, actor: str = "sistema", detalle: str = "",
                       error: str | None = None, aprobada_por: str | None = None) -> None:
        actual = self.obtener(pieza_id)["estado"]
        if nuevo not in TRANSICIONES[actual]:
            raise TransicionInvalida(f"{pieza_id}: no se puede pasar de '{actual}' a '{nuevo}'")
        ts = self._ahora()
        with self.db:
            self.db.execute(
                "UPDATE piezas SET estado = ?, actualizada = ?, error = ?,"
                " aprobada_por = CASE WHEN ? = 'borrador' THEN NULL ELSE COALESCE(?, aprobada_por) END WHERE id = ?",
                (nuevo, ts, error, nuevo, aprobada_por, pieza_id),
            )
            self.db.execute("INSERT INTO eventos (pieza_id, ts, de, a, actor, detalle) VALUES (?, ?, ?, ?, ?, ?)",
                            (pieza_id, ts, actual, nuevo, actor, detalle or error))

    def guardar_datos(self, pieza_id: str, datos: dict) -> None:
        with self.db:
            self.db.execute("UPDATE piezas SET datos = ?, actualizada = ? WHERE id = ?",
                            (json.dumps(datos, ensure_ascii=False), self._ahora(), pieza_id))

    def registrar_publicacion(self, pieza_id: str, red: str, simulado: bool, post_id: str | None, url: str | None) -> None:
        with self.db:
            self.db.execute("INSERT INTO publicaciones (pieza_id, red, ts, simulado, post_id, url) VALUES (?, ?, ?, ?, ?, ?)",
                            (pieza_id, red, self._ahora(), int(simulado), post_id, url))

    def redes_publicadas(self, pieza_id: str) -> set[str]:
        return {r["red"] for r in self.db.execute("SELECT red FROM publicaciones WHERE pieza_id = ?", (pieza_id,))}

    def listar(self, estado: str | None = None) -> list[sqlite3.Row]:
        if estado:
            return self.db.execute("SELECT * FROM piezas WHERE estado = ? ORDER BY creada", (estado,)).fetchall()
        return self.db.execute("SELECT * FROM piezas ORDER BY creada").fetchall()

    def _ahora(self) -> str:
        return datetime.now(self.tz).astimezone(self.tz).isoformat(timespec="seconds")

    def eventos(self, pieza_id: str) -> list[sqlite3.Row]:
        return self.db.execute("SELECT * FROM eventos WHERE pieza_id = ? ORDER BY id", (pieza_id,)).fetchall()
