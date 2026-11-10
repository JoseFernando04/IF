"""Control de lo que ya se subió a redes. Registro en docs/publicaciones.yaml; vista legible en docs/publicaciones.md.

Uso:
  .venv/Scripts/python tools/publicaciones.py sync                      agrega las piezas nuevas de data/dias/*/para-subir como pendientes
  .venv/Scripts/python tools/publicaciones.py lista [--pendientes]      muestra el estado
  .venv/Scripts/python tools/publicaciones.py marcar 2026-11-10 reel-A [--redes ig,tt] [--fecha 2026-11-11] [--nota "..."]
  .venv/Scripts/python tools/publicaciones.py descartar 2026-11-10 post-2 [--nota "..."]
  .venv/Scripts/python tools/publicaciones.py pendiente 2026-11-10 post-2      (deshace marcar/descartar)

La pieza se puede escribir corta ("reel-A", "post-2") o con el nombre de la carpeta.
Estados: pendiente | publicado | descartado. Redes: ig (Instagram), tt (TikTok).
"""
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRO = ROOT / "docs" / "publicaciones.yaml"
VISTA = ROOT / "docs" / "publicaciones.md"
DIAS = ROOT / "data" / "dias"
COPY = ROOT / "examples" / "copy" / "dia"
REDES = {"ig": "Instagram", "tt": "TikTok"}
MARCA = {"publicado": "✅", "pendiente": "⏳", "descartado": "✖️"}

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8")


def arg(nombre: str) -> str | None:
    return sys.argv[sys.argv.index(nombre) + 1] if nombre in sys.argv else None


def cargar() -> list[dict]:
    if not REGISTRO.exists():
        return []
    return (yaml.safe_load(REGISTRO.read_text(encoding="utf-8")) or {}).get("piezas", [])


def guardar(piezas: list[dict]) -> None:
    piezas.sort(key=lambda p: (p["dia"], p["pieza"]))
    cab = ("# Registro de publicaciones (lo mantiene tools/publicaciones.py; se puede editar a mano).\n"
           "# estado: pendiente | publicado | descartado · redes: ig, tt\n")
    REGISTRO.write_text(cab + yaml.safe_dump({"piezas": piezas}, allow_unicode=True, sort_keys=False, width=140),
                        encoding="utf-8")
    vista(piezas)


def vista(piezas: list[dict]) -> None:
    pub = [p for p in piezas if p["estado"] == "publicado"]
    pen = [p for p in piezas if p["estado"] == "pendiente"]
    out = ["# Publicaciones", "",
           "Se genera sola con `tools/publicaciones.py` a partir de `docs/publicaciones.yaml`. No editar a mano.", "",
           f"**{len(pub)} publicadas · {len(pen)} pendientes · "
           f"{len(piezas) - len(pub) - len(pen)} descartadas**", "",
           "| Día | Pieza | Tema | Estado | Redes | Subido |", "|---|---|---|---|---|---|"]
    for p in piezas:
        redes = ", ".join(REDES.get(r, r) for r in p.get("redes") or [])
        nota = f" ({p['nota']})" if p.get("nota") else ""
        out.append(f"| {p['dia']} | {p['pieza']} | {p.get('tema', '')} | {MARCA[p['estado']]} {p['estado']}{nota} "
                   f"| {redes} | {p.get('fecha') or ''} |")
    VISTA.write_text("\n".join(out) + "\n", encoding="utf-8")


def tema(dia: str, carpeta: str) -> str:
    corto = "-".join(carpeta.split("-")[:2])  # reel-A, post-1
    y = COPY / f"{dia}-{corto}.yaml"
    if y.exists():
        d = yaml.safe_load(y.read_text(encoding="utf-8"))
        return d.get("titulo_tiktok") or d.get("titulo") or carpeta
    return carpeta.split("-", 2)[-1].replace("-", " ")


def sync(piezas: list[dict]) -> int:
    ya = {(p["dia"], p["pieza"]) for p in piezas}
    nuevas = 0
    for carpeta in sorted(DIAS.glob("*/para-subir/*")):
        if not carpeta.is_dir() or carpeta.name.startswith("sonido"):
            continue
        dia = carpeta.parent.parent.name
        if (dia, carpeta.name) in ya:
            continue
        piezas.append({"dia": dia, "pieza": carpeta.name, "tipo": carpeta.name.split("-")[0],
                       "tema": tema(dia, carpeta.name), "estado": "pendiente", "redes": [], "fecha": None})
        nuevas += 1
    return nuevas


def buscar(piezas: list[dict], dia: str, pieza: str) -> dict:
    hits = [p for p in piezas if p["dia"] == dia and (p["pieza"] == pieza or p["pieza"].lower().startswith(pieza.lower() + "-"))]
    if len(hits) != 1:
        opciones = ", ".join(p["pieza"] for p in piezas if p["dia"] == dia) or "ninguna"
        sys.exit(f"✗ No encontré una sola pieza '{pieza}' del {dia}. Piezas de ese día: {opciones}")
    return hits[0]


def lista(piezas: list[dict], solo_pendientes: bool) -> None:
    dia = None
    for p in piezas:
        if solo_pendientes and p["estado"] != "pendiente":
            continue
        if p["dia"] != dia:
            dia = p["dia"]
            print(f"\n{dia}")
        redes = ",".join(p.get("redes") or [])
        extra = f"  [{redes} · {p['fecha']}]" if p["estado"] == "publicado" else ""
        print(f"  {MARCA[p['estado']]} {p['pieza']:28s} {p.get('tema', '')}{extra}")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    piezas = cargar()
    if cmd == "sync":
        n = sync(piezas)
        guardar(piezas)
        print(f"✔ {n} piezas nuevas agregadas como pendientes")
    elif cmd == "lista":
        lista(piezas, "--pendientes" in sys.argv)
    elif cmd in ("marcar", "descartar", "pendiente"):
        sync(piezas)
        p = buscar(piezas, sys.argv[2], sys.argv[3])
        if cmd == "marcar":
            p["estado"] = "publicado"
            p["redes"] = (arg("--redes") or "ig,tt").split(",")
            p["fecha"] = arg("--fecha") or date.today().isoformat()
        elif cmd == "descartar":
            p["estado"], p["redes"], p["fecha"] = "descartado", [], None
        else:
            p["estado"], p["redes"], p["fecha"] = "pendiente", [], None
        if arg("--nota"):
            p["nota"] = arg("--nota")
        elif cmd == "pendiente":
            p.pop("nota", None)
        guardar(piezas)
        print(f"✔ {p['dia']} {p['pieza']} → {p['estado']}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
