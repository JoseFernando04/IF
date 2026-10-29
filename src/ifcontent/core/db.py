"""Estado de cada pieza en SQLite (librería estándar, sin ORM)."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from .config import load_config

# Estados posibles de una pieza.
BORRADOR = "borrador"
EN_REVISION = "en_revision"
CAMBIOS = "cambios_solicitados"
APROBADO = "aprobado"
PROGRAMADO = "programado"
PUBLICADO = "publicado"
FALLIDO = "fallido"
DESCARTADO = "descartado"

SCHEMA = """
CREATE TABLE IF NOT EXISTS pieces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL,              -- reel | carousel
    pillar TEXT NOT NULL,
    topic TEXT NOT NULL,
    status TEXT NOT NULL,
    copy_json TEXT,
    output_dir TEXT,
    music_track TEXT,
    scheduled_at TEXT,
    error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    piece_id INTEGER NOT NULL REFERENCES pieces(id),
    at TEXT NOT NULL,
    status TEXT NOT NULL,
    note TEXT
);
"""


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    path: Path = load_config().path("database")
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def create_piece(kind: str, pillar: str, topic: str) -> int:
    with connect() as c:
        cur = c.execute(
            "INSERT INTO pieces (kind, pillar, topic, status, created_at, updated_at) VALUES (?,?,?,?,?,?)",
            (kind, pillar, topic, BORRADOR, _now(), _now()),
        )
        piece_id = cur.lastrowid
        c.execute("INSERT INTO events (piece_id, at, status, note) VALUES (?,?,?,?)", (piece_id, _now(), BORRADOR, "creada"))
        return piece_id


def update_piece(piece_id: int, **fields: Any) -> None:
    if "copy" in fields:
        fields["copy_json"] = json.dumps(fields.pop("copy"), ensure_ascii=False)
    fields["updated_at"] = _now()
    cols = ", ".join(f"{k} = ?" for k in fields)
    with connect() as c:
        c.execute(f"UPDATE pieces SET {cols} WHERE id = ?", (*fields.values(), piece_id))


def set_status(piece_id: int, status: str, note: str = "") -> None:
    update_piece(piece_id, status=status, error=note if status == FALLIDO else None)
    with connect() as c:
        c.execute("INSERT INTO events (piece_id, at, status, note) VALUES (?,?,?,?)", (piece_id, _now(), status, note))


def get_piece(piece_id: int) -> dict[str, Any] | None:
    with connect() as c:
        row = c.execute("SELECT * FROM pieces WHERE id = ?", (piece_id,)).fetchone()
        return dict(row) if row else None


def list_pieces(status: str | None = None) -> list[dict[str, Any]]:
    with connect() as c:
        if status:
            rows = c.execute("SELECT * FROM pieces WHERE status = ? ORDER BY id DESC", (status,)).fetchall()
        else:
            rows = c.execute("SELECT * FROM pieces ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


def events(piece_id: int) -> list[dict[str, Any]]:
    with connect() as c:
        return [dict(r) for r in c.execute("SELECT * FROM events WHERE piece_id = ? ORDER BY id", (piece_id,))]
