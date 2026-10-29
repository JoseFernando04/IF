"""Comandos de uso diario. Ejecutá `ifcontent --help` para ver todos."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from . import pipeline
from .core import db
from .core.config import load_config

app = typer.Typer(help="IF Techworks · herramienta de contenido para Instagram y TikTok", no_args_is_help=True)


@app.callback()
def _init() -> None:
    load_config()


@app.command("generar-reel")
def generar_reel(
    pilar: str = typer.Option(..., help="educativo | soluciones | tips | proposito | cta"),
    tema: str = typer.Option(..., help="Tema del reel"),
    copy_file: Optional[Path] = typer.Option(None, "--copy-file", help="Usar copy escrito a mano (YAML/JSON) en vez del LLM"),
) -> None:
    """Genera un reel 9:16 completo y lo deja en revisión."""
    pid = pipeline.generate("reel", pilar, tema, copy_file)
    typer.echo(f"✔ Reel #{pid} listo para revisar: {db.get_piece(pid)['output_dir']}")


@app.command("generar-carrusel")
def generar_carrusel(
    pilar: str = typer.Option(...),
    tema: str = typer.Option(...),
    copy_file: Optional[Path] = typer.Option(None, "--copy-file"),
) -> None:
    """Genera un carrusel 4:5 y lo deja en revisión."""
    pid = pipeline.generate("carousel", pilar, tema, copy_file)
    typer.echo(f"✔ Carrusel #{pid} listo para revisar: {db.get_piece(pid)['output_dir']}")


@app.command()
def listar(estado: Optional[str] = typer.Option(None, help="Filtrar por estado")) -> None:
    """Lista las piezas y su estado."""
    for p in db.list_pieces(estado):
        typer.echo(f"#{p['id']:<4} {p['status']:<20} {p['kind']:<9} {p['pillar']:<11} {p['topic']}")


@app.command()
def ver(id: int) -> None:
    """Muestra el detalle e historial de una pieza."""
    p = db.get_piece(id)
    if not p:
        raise typer.BadParameter(f"No existe la pieza #{id}")
    typer.echo(json.dumps({k: v for k, v in p.items() if k != "copy_json"}, ensure_ascii=False, indent=2))
    for e in db.events(id):
        typer.echo(f"  {e['at']}  {e['status']:<20} {e['note'] or ''}")


def _transition(id: int, allowed: set[str], new: str, nota: str) -> None:
    p = db.get_piece(id)
    if not p:
        raise typer.BadParameter(f"No existe la pieza #{id}")
    if p["status"] not in allowed:
        raise typer.BadParameter(f"La pieza #{id} está '{p['status']}'; no se puede pasar a '{new}'")
    db.set_status(id, new, nota)
    typer.echo(f"#{id} → {new}")


@app.command()
def aprobar(id: int, nota: str = "") -> None:
    """Aprueba una pieza en revisión."""
    _transition(id, {db.EN_REVISION}, db.APROBADO, nota)


@app.command()
def cambios(id: int, nota: str = typer.Option(..., help="Qué hay que cambiar")) -> None:
    """Pide cambios sobre una pieza en revisión."""
    _transition(id, {db.EN_REVISION, db.APROBADO}, db.CAMBIOS, nota)


@app.command()
def descartar(id: int, nota: str = "") -> None:
    """Descarta una pieza."""
    _transition(id, {db.BORRADOR, db.EN_REVISION, db.CAMBIOS, db.APROBADO, db.FALLIDO}, db.DESCARTADO, nota)


@app.command()
def publicar(id: int) -> None:
    """Publica una pieza aprobada (en modo DRY_RUN solo genera la simulación)."""
    result = pipeline.publish(id)
    modo = "SIMULACIÓN (no se publicó nada)" if result.get("dry_run") else "PUBLICADO"
    typer.echo(f"#{id}: {modo}. Detalle en publish_simulation.json")


if __name__ == "__main__":
    app()
