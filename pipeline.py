"""Flujo de una pieza: generar -> validar -> revisión -> (aprobación humana) -> publicar.

Reglas:
- Cada paso con ootto se reintenta una vez; si vuelve a fallar se notifica y la pieza queda 'fallido'.
- Una pieza incompleta o que no cumple la marca nunca pasa a revisión ni se publica.
- En DRY_RUN no se llama a la publicación: se registra lo que se habría publicado.
"""
from __future__ import annotations

import json
import logging
import re
import urllib.request
import uuid
from datetime import datetime
from html import escape
from pathlib import Path

from ootto_cliente import OottoCliente
from registro import Registro

log = logging.getLogger("pipeline")


class PasoFallido(Exception):
    pass


def notificar(cfg, asunto: str, mensaje: str) -> None:
    log.error("NOTIFICACIÓN: %s — %s", asunto, mensaje)
    if not cfg.notify_webhook:
        return
    cuerpo = json.dumps({"text": f"[IF Social] {asunto}\n{mensaje}"}).encode()
    req = urllib.request.Request(cfg.notify_webhook, data=cuerpo, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:  # una notificación fallida no debe tumbar el flujo
        log.error("No se pudo enviar la notificación al webhook: %s", type(e).__name__)


def _con_reintento(cfg, paso: str, fn, *args):
    intentos = 1 + int(cfg.calendario["generacion"].get("reintentos", 1))
    for n in range(1, intentos + 1):
        try:
            return fn(*args)
        except Exception as e:
            log.warning("Paso '%s' falló (intento %d/%d): %s", paso, n, intentos, e)
            if n == intentos:
                raise PasoFallido(f"'{paso}' falló {intentos} veces: {e}") from e


# --------------------------------------------------------------------------- validación

def validar_pieza(cfg, pieza: dict, carpeta: Path) -> list[str]:
    """Devuelve la lista de problemas; vacía = pieza completa y dentro de marca."""
    problemas = []
    for campo in ("hook", "hooks_alternativos", "guion", "graficos", "video", "musica", "por_red"):
        if not pieza.get(campo):
            problemas.append(f"falta '{campo}'")
    for archivo in pieza.get("graficos", []) + [pieza.get("video"), pieza.get("musica")]:
        if archivo and not (carpeta / archivo).exists():
            problemas.append(f"no existe el archivo {archivo}")

    prohibidas = [p.lower() for p in cfg.brand["voz"].get("palabras_prohibidas", [])]
    texto = json.dumps(pieza.get("guion", {}), ensure_ascii=False).lower()
    for red, d in pieza.get("por_red", {}).items():
        lim = cfg.calendario["redes"][red]
        texto += d["caption"].lower()
        if len(d["caption"]) > lim["caption_max"]:
            problemas.append(f"{red}: caption de {len(d['caption'])} caracteres (máx {lim['caption_max']})")
        if len(d["hashtags"]) > lim["hashtags_max"]:
            problemas.append(f"{red}: {len(d['hashtags'])} hashtags (máx {lim['hashtags_max']})")
    for p in prohibidas:
        if re.search(rf"\b{re.escape(p)}\b", texto):
            problemas.append(f"usa la palabra prohibida '{p}'")
    return problemas


def adaptar_por_red(cfg, guion: dict) -> dict:
    """Ajusta caption y hashtags a los límites de cada red activa."""
    salida = {}
    for red, conf in cfg.redes_activas.items():
        hashtags = guion["hashtags"][: conf["hashtags_max"]]
        caption = f"{guion['caption']}\n\n{' '.join(hashtags)}"
        if len(caption) > conf["caption_max"]:
            caption = caption[: conf["caption_max"] - 1] + "…"
        salida[red] = {"formato": conf["formato"], "relacion": conf["relacion"], "caption": caption, "hashtags": hashtags}
    return salida


# --------------------------------------------------------------------------- generación

def generar_pieza(cfg, cliente: OottoCliente, reg: Registro, pilar_id: str, tema_idx: int = 0,
                  programada_para: datetime | None = None) -> str:
    pilar = cfg.pilar(pilar_id)
    temas = pilar["temas"]
    if not 0 <= tema_idx < len(temas):
        raise ValueError(f"El pilar '{pilar_id}' tiene {len(temas)} tema(s); índice {tema_idx} no existe")
    tema = temas[tema_idx]
    gen = cfg.calendario["generacion"]

    pieza_id = f"{datetime.now(cfg.tz):%Y%m%d-%H%M%S}-{pilar_id}-{uuid.uuid4().hex[:4]}"
    carpeta = cfg.salida_dir / pieza_id
    carpeta.mkdir(parents=True)
    reg.crear(pieza_id, pilar_id, tema["titulo"], carpeta, programada_para.isoformat() if programada_para else None)
    log.info("Pieza %s creada (%s: %s)", pieza_id, pilar["nombre"], tema["titulo"])

    try:
        hooks = _con_reintento(cfg, "hooks", cliente.generar_hooks, tema, pilar, cfg.brand, gen["variantes_hook"])
        guion = _con_reintento(cfg, "guion", cliente.generar_guion, hooks[0], tema, pilar, cfg.brand, gen["duracion_objetivo_s"])
        graficos = _con_reintento(cfg, "graficos", cliente.generar_graficos, guion, cfg.brand, carpeta / "graficos")
        relacion = next(iter(cfg.redes_activas.values()))["relacion"]
        video = _con_reintento(cfg, "motion", cliente.generar_motion, guion, graficos, relacion, carpeta / "video.json")
        duracion = sum(e["duracion_s"] for e in guion["escenas"])
        musica = _con_reintento(cfg, "musica", cliente.generar_musica, gen["estilo_musica"], duracion, carpeta / "musica.json")
    except PasoFallido as e:
        reg.cambiar_estado(pieza_id, "fallido", error=str(e))
        notificar(cfg, f"Falló la generación de {pieza_id}", str(e))
        return pieza_id

    pieza = {
        "id": pieza_id,
        "pilar": pilar_id,
        "tema": tema["titulo"],
        "hook": hooks[0],
        "hooks_alternativos": hooks[1:],
        "guion": guion,
        "graficos": [str(g.relative_to(carpeta)) for g in graficos],
        "video": video.name,
        "musica": musica.name,
        "duracion_s": duracion,
        "por_red": adaptar_por_red(cfg, guion),
        "simulado": cfg.ootto_modo == "simulado",
    }
    (carpeta / "pieza.json").write_text(json.dumps(pieza, ensure_ascii=False, indent=2), encoding="utf-8")
    reg.guardar_datos(pieza_id, pieza)

    problemas = validar_pieza(cfg, pieza, carpeta)
    if problemas:
        reg.cambiar_estado(pieza_id, "fallido", error="; ".join(problemas))
        notificar(cfg, f"Pieza {pieza_id} incompleta o fuera de marca", "; ".join(problemas))
        return pieza_id

    _escribir_preview(cfg, pieza, carpeta)
    reg.cambiar_estado(pieza_id, "en_revision", detalle="lista para aprobación")
    log.info("Pieza %s en revisión. Vista previa: %s", pieza_id, carpeta / "preview.html")
    return pieza_id


# --------------------------------------------------------------------------- aprobación y publicación

def aprobar(reg: Registro, pieza_id: str, por: str, nota: str = "") -> None:
    if not por.strip():
        raise ValueError("La aprobación necesita el nombre de quien aprueba")
    reg.cambiar_estado(pieza_id, "aprobado", actor=por, detalle=nota or "aprobada", aprobada_por=por)


def rechazar(reg: Registro, pieza_id: str, por: str, nota: str) -> None:
    if not nota.strip():
        raise ValueError("El rechazo necesita una nota con los cambios pedidos")
    reg.cambiar_estado(pieza_id, "borrador", actor=por, detalle=f"rechazada: {nota}")


def publicar_pieza(cfg, cliente: OottoCliente, reg: Registro, pieza_id: str) -> None:
    fila = reg.obtener(pieza_id)
    if fila["estado"] not in ("aprobado", "fallido") or not fila["aprobada_por"]:
        raise PermissionError(f"{pieza_id} no tiene aprobación humana (estado: {fila['estado']}). No se publica.")

    pieza = json.loads(fila["datos"])
    carpeta = Path(fila["carpeta"])
    problemas = validar_pieza(cfg, pieza, carpeta)
    if problemas:
        reg.cambiar_estado(pieza_id, "fallido", error="; ".join(problemas))
        notificar(cfg, f"No se publica {pieza_id}: pieza incompleta", "; ".join(problemas))
        return

    programada = datetime.fromisoformat(fila["programada_para"]) if fila["programada_para"] else None
    ya = reg.redes_publicadas(pieza_id)
    errores = []
    for red, datos in pieza["por_red"].items():
        if red in ya or red not in cfg.redes_activas:
            continue
        if cfg.dry_run:
            log.info("[SIMULACIÓN] Se habría publicado %s en %s (%s, %s)", pieza_id, red, datos["formato"],
                     programada or "inmediato")
            reg.registrar_publicacion(pieza_id, red, True, None, None)
            continue
        try:
            r = _con_reintento(cfg, f"publicar:{red}", cliente.publicar, red, carpeta / pieza["video"], datos["caption"], programada)
            reg.registrar_publicacion(pieza_id, red, False, r.get("id"), r.get("url"))
        except PasoFallido as e:
            errores.append(f"{red}: {e}")

    if errores:
        reg.cambiar_estado(pieza_id, "fallido", error="; ".join(errores))
        notificar(cfg, f"Falló la publicación de {pieza_id}", "; ".join(errores))
    else:
        reg.cambiar_estado(pieza_id, "publicado", detalle="SIMULACIÓN" if cfg.dry_run else "publicada")


# --------------------------------------------------------------------------- vista previa para revisión

def _escribir_preview(cfg, pieza: dict, carpeta: Path) -> None:
    c = cfg.brand["colores"]
    escenas = "".join(
        f'<figure><img src="{g}" alt=""><figcaption>{e["duracion_s"]}s · {escape(e["locucion"])}</figcaption></figure>'
        for g, e in zip(pieza["graficos"], pieza["guion"]["escenas"]))
    redes = "".join(f"<h3>{red} · {d['formato']} {d['relacion']}</h3><pre>{escape(d['caption'])}</pre>"
                    for red, d in pieza["por_red"].items())
    alternos = "".join(f"<li>{escape(h)}</li>" for h in pieza["hooks_alternativos"])
    aviso = "<p class=aviso>SIMULACIÓN: contenido generado por el backend simulado, no por ootto.</p>" if pieza["simulado"] else ""
    html = f"""<!doctype html><html lang="es"><meta charset="utf-8"><title>{escape(pieza['id'])}</title>
<style>
body{{background:{c['fondo']};color:{c['texto']};font-family:Inter,system-ui,sans-serif;max-width:1100px;margin:auto;padding:24px}}
h1,h2,h3{{font-family:'Space Grotesk',sans-serif}} h1 span{{color:{c['primario']}}}
.aviso{{background:{c['primario']};color:{c['fondo']};padding:8px 12px;border-radius:6px;font-weight:600}}
.escenas{{display:flex;gap:12px;overflow-x:auto}} figure{{margin:0;flex:0 0 200px}} img{{width:200px;border-radius:8px}}
figcaption{{font-size:13px;color:{c['texto_secundario']}}} pre{{white-space:pre-wrap;background:{c['superficie']};padding:12px;border-radius:8px}}
</style>
<h1>{escape(pieza['tema'])} <span>· {escape(pieza['pilar'])}</span></h1>{aviso}
<h2>Hook</h2><p><strong>{escape(pieza['hook'])}</strong></p><p>Alternativas:</p><ul>{alternos}</ul>
<h2>Storyboard ({pieza['duracion_s']} s)</h2><div class="escenas">{escenas}</div>
<h2>Texto por red</h2>{redes}
<p>Aprobar: <code>python main.py aprobar {escape(pieza['id'])} --por "Tu nombre"</code></p>
</html>"""
    (carpeta / "preview.html").write_text(html, encoding="utf-8")
