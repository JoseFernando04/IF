"""IF Social — línea de comandos.

Ejemplos:
    python main.py validar
    python main.py generar --pilar educativo
    python main.py listar --estado en_revision
    python main.py ver <id>
    python main.py aprobar <id> --por "Nombre"
    python main.py rechazar <id> --por "Nombre" --nota "Cambiar el hook"
    python main.py publicar <id>
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime

import config
import pipeline
from ootto_cliente import crear_cliente
from registro import ESTADOS, Registro, TransicionInvalida

log = logging.getLogger("main")


def _cmd_validar(cfg, reg, args):
    pilares = ", ".join(f"{p['id']} ({p.get('peso', 0)}%)" for p in cfg.calendario["pilares"])
    print(f"Configuración válida.\n  Modo: {'SIMULACIÓN (dry-run)' if cfg.dry_run else 'PUBLICACIÓN REAL'}"
          f" · ootto: {cfg.ootto_modo}\n  Redes activas: {', '.join(cfg.redes_activas)}"
          f"\n  Frecuencia: {cfg.calendario['frecuencia']['piezas_por_semana']} por semana\n  Pilares: {pilares}")


def _cmd_generar(cfg, reg, args):
    cuando = datetime.fromisoformat(args.para).replace(tzinfo=cfg.tz) if args.para else None
    pieza_id = pipeline.generar_pieza(cfg, crear_cliente(cfg), reg, args.pilar, args.tema, cuando)
    fila = reg.obtener(pieza_id)
    print(f"{pieza_id}: {fila['estado']}")
    if fila["estado"] == "en_revision":
        print(f"Vista previa: {fila['carpeta']}/preview.html")
    else:
        print(f"Error: {fila['error']}")
        return 1


def _cmd_listar(cfg, reg, args):
    filas = reg.listar(args.estado)
    if not filas:
        print("No hay piezas.")
    for f in filas:
        print(f"{f['id']:40} {f['estado']:12} {f['pilar']:10} {f['tema']}")


def _cmd_ver(cfg, reg, args):
    f = reg.obtener(args.id)
    print(json.dumps({k: f[k] for k in f.keys() if k != "datos"}, ensure_ascii=False, indent=2))
    print("Historial:")
    for e in reg.eventos(args.id):
        print(f"  {e['ts']}  {e['de'] or '-':12} -> {e['a']:12} [{e['actor']}] {e['detalle'] or ''}")


def _cmd_aprobar(cfg, reg, args):
    pipeline.aprobar(reg, args.id, args.por, args.nota or "")
    print(f"{args.id} aprobada por {args.por}.")


def _cmd_rechazar(cfg, reg, args):
    pipeline.rechazar(reg, args.id, args.por, args.nota)
    print(f"{args.id} devuelta a borrador.")


def _cmd_publicar(cfg, reg, args):
    pipeline.publicar_pieza(cfg, crear_cliente(cfg), reg, args.id)
    f = reg.obtener(args.id)
    print(f"{args.id}: {f['estado']}{' (simulación, no se publicó nada)' if cfg.dry_run else ''}")
    return 0 if f["estado"] == "publicado" else 1


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="main.py", description="Gestión de contenido de IF Techworks para Instagram y TikTok")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("validar", help="Revisa .env, brand.json y calendario.json").set_defaults(fn=_cmd_validar)

    g = sub.add_parser("generar", help="Genera una pieza y la deja en revisión")
    g.add_argument("--pilar", required=True, help="id del pilar en calendario.json")
    g.add_argument("--tema", type=int, default=0, help="índice del tema dentro del pilar (0 = primero)")
    g.add_argument("--para", help="fecha y hora de publicación, ej. 2026-11-03T12:30 (hora de Guatemala)")
    g.set_defaults(fn=_cmd_generar)

    l = sub.add_parser("listar", help="Lista piezas y su estado")
    l.add_argument("--estado", choices=ESTADOS)
    l.set_defaults(fn=_cmd_listar)

    v = sub.add_parser("ver", help="Detalle e historial de una pieza")
    v.add_argument("id")
    v.set_defaults(fn=_cmd_ver)

    a = sub.add_parser("aprobar", help="Aprueba una pieza en revisión")
    a.add_argument("id")
    a.add_argument("--por", required=True, help="nombre de quien aprueba")
    a.add_argument("--nota")
    a.set_defaults(fn=_cmd_aprobar)

    r = sub.add_parser("rechazar", help="Devuelve una pieza a borrador con cambios pedidos")
    r.add_argument("id")
    r.add_argument("--por", required=True)
    r.add_argument("--nota", required=True, help="qué hay que cambiar")
    r.set_defaults(fn=_cmd_rechazar)

    pub = sub.add_parser("publicar", help="Publica una pieza aprobada (en dry-run solo simula)")
    pub.add_argument("id")
    pub.set_defaults(fn=_cmd_publicar)
    return p


def main(argv=None) -> int:
    args = _parser().parse_args(argv)
    try:
        cfg = config.cargar()
    except config.ConfigError as e:
        print(f"Error de configuración: {e}", file=sys.stderr)
        return 2
    config.configurar_logging(cfg)
    reg = Registro(cfg.data_dir / "ifsocial.db", cfg.tz)
    try:
        return args.fn(cfg, reg, args) or 0
    except (KeyError, ValueError, PermissionError, TransicionInvalida, config.ConfigError) as e:
        print(f"Error: {e.args[0] if e.args else e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
