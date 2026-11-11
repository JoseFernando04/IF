"""Genera con Higgsfield (Seedance 2.5) las tomas de un reel de formato `cine`. CADA TOMA ES DE PAGO.

Uso:
  .venv/Scripts/python tools/generar_clip.py examples/copy/cine/ejemplo-inventario.yaml              (solo muestra el plan, no gasta)
  .venv/Scripts/python tools/generar_clip.py <yaml> --confirmar                                      (genera las tomas que falten)
  .venv/Scripts/python tools/generar_clip.py <yaml> --confirmar --solo 01-gancho                     (una sola toma)
  .venv/Scripts/python tools/generar_clip.py <yaml> --confirmar --rehacer 02-cuaderno                (vuelve a pagar esa toma)

Lee las tomas de `lineas[].toma` ({id, prompt, duracion}) y guarda cada clip en <salida>/clips/<id>.mp4.
Las tomas que ya existen no se vuelven a generar. Los valores por defecto están en config/settings.yaml > higgsfield.
"""
import json
import sys
from pathlib import Path

import yaml

from ifcontent.core.config import ROOT, load_config
from ifcontent.video.higgsfield import GeneracionFallida, generar


def arg(nombre: str) -> str | None:
    return sys.argv[sys.argv.index(nombre) + 1] if nombre in sys.argv else None


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1].startswith("--"):
        print(__doc__)
        return 2
    cfg = load_config().settings["higgsfield"]
    datos = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
    carpeta = ROOT / datos["salida"] / "clips"
    estilo = (datos["estilo"] if "estilo" in datos else cfg["estilo"]).strip()
    modelo = datos.get("modelo", cfg["modelo"])
    resolucion = datos.get("resolucion", cfg["resolucion"])
    solo, rehacer = arg("--solo"), arg("--rehacer")

    tomas = [l["toma"] for l in datos["lineas"] if l.get("toma")]
    ids = [t["id"] for t in tomas]
    if len(set(ids)) != len(ids):
        print("ERROR: hay ids de toma repetidos.")
        return 2
    if len(tomas) > cfg["max_tomas_por_reel"]:
        print(f"ERROR: {len(tomas)} tomas supera el tope de {cfg['max_tomas_por_reel']} (settings.yaml > higgsfield).")
        return 2

    pendientes = []
    for t in tomas:
        destino = carpeta / f"{t['id']}.mp4"
        if solo and t["id"] != solo:
            continue
        if destino.exists() and t["id"] != rehacer:
            print(f"  ya existe   {t['id']}")
            continue
        pendientes.append((t, destino))
        print(f"  por generar {t['id']}  ({t.get('duracion', cfg['duracion'])} s, {resolucion}, {cfg['aspecto']})")

    if not pendientes:
        print("Nada por generar.")
        return 0
    segundos = sum(int(t.get("duracion", cfg["duracion"])) for t, _ in pendientes)
    costo = segundos * cfg["usd_por_segundo"][modelo][resolucion]
    print(f"\n{len(pendientes)} generación(es) de pago con {modelo}: {segundos} s a {resolucion} ≈ USD {costo:.2f} (estimado).")
    if costo > cfg["max_usd_por_corrida"]:
        print(f"ERROR: supera el tope de USD {cfg['max_usd_por_corrida']:.2f} por corrida (settings.yaml > higgsfield).")
        return 2
    if "--confirmar" not in sys.argv:
        print("Agregá --confirmar para lanzarlas.")
        return 0

    fallos = 0
    registro = carpeta / "tomas.json"
    hechas = json.loads(registro.read_text(encoding="utf-8")) if registro.exists() else {}
    for t, destino in pendientes:
        prompt = f"{t['prompt'].strip()} {estilo}".strip()
        for intento in (1, 2):  # regla del proyecto: un reintento y luego se reporta el fallo
            try:
                r = generar(
                    prompt,
                    duracion=int(t.get("duracion", cfg["duracion"])),
                    resolucion=resolucion,
                    aspecto=cfg["aspecto"],
                    audio=bool(cfg["audio"]),
                    modelo=modelo,
                    destino=destino,
                )
                hechas[t["id"]] = {"request_id": r["request_id"], "prompt": prompt}
                registro.write_text(json.dumps(hechas, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"  LISTO  {t['id']} → {destino.relative_to(ROOT)}")
                break
            except GeneracionFallida as exc:
                print(f"  FALLÓ  {t['id']} (intento {intento}): {exc}")
                if "not_enough_credits" in str(exc) or "HF_KEY" in str(exc):
                    return 1  # reintentar no sirve
                if intento == 2:
                    fallos += 1
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
