"""Cliente de ootto: interfaz + backend simulado.

AVISO: la interfaz real del MCP de ootto NO está validada (no hay suscripción activa).
Los métodos de `OottoCliente` son una SUPOSICIÓN basada en lo que ootto dice ofrecer
(hook, guion, gráficos, motion, música, publicación). Cuando el MCP esté conectado,
se listan sus herramientas reales y se escribe `OottoMCP` implementando esta misma
interfaz; el resto del sistema no cambia.
"""
from __future__ import annotations

import json
import random
from abc import ABC, abstractmethod
from datetime import datetime
from html import escape
from pathlib import Path
from textwrap import wrap


class OottoError(Exception):
    pass


class OottoCliente(ABC):
    @abstractmethod
    def generar_hooks(self, tema: dict, pilar: dict, marca: dict, n: int) -> list[str]:
        """Devuelve n variantes de gancho (primera frase/3 segundos)."""

    @abstractmethod
    def generar_guion(self, hook: str, tema: dict, pilar: dict, marca: dict, duracion_s: int) -> dict:
        """Devuelve {"escenas": [{"texto_pantalla", "locucion", "duracion_s"}], "caption", "hashtags"}."""

    @abstractmethod
    def generar_graficos(self, guion: dict, marca: dict, destino: Path) -> list[Path]:
        """Un gráfico por escena, con la identidad de marca."""

    @abstractmethod
    def generar_motion(self, guion: dict, graficos: list[Path], relacion: str, destino: Path) -> Path:
        """Arma el video a partir de los gráficos."""

    @abstractmethod
    def generar_musica(self, estilo: str, duracion_s: int, destino: Path) -> Path:
        """Pista de audio para el video."""

    @abstractmethod
    def publicar(self, red: str, video: Path, caption: str, programado_para: datetime | None) -> dict:
        """Publica o programa en una red. Devuelve {"id", "url"}."""


def crear_cliente(cfg) -> OottoCliente:
    if cfg.ootto_modo == "simulado":
        return OottoSimulado(cfg.sim_fallos)
    raise OottoError("OOTTO_MODO=mcp todavía no está implementado: falta validar la interfaz real del MCP de ootto.")


# --------------------------------------------------------------------------- simulado

_PLANTILLAS_HOOK = {
    "educativo": ["{t}, explicado en 30 segundos.", "{t}: sin paja técnica.", "Nadie te explicó esto: {t}."],
    "casos": ["{t}. Así lo resolvimos.", "Este negocio tenía un problema. {t}.", "Antes y después: {t}."],
    "detras": ["{t}.", "Te mostramos cómo trabajamos: {t}.", "Lo que no se ve: {t}."],
    "tips": ["{t}.", "Si te pasa esto, ojo: {t}.", "Guardá este video: {t}."],
    "impacto": ["{t}.", "Digitalizar no debería ser un privilegio.", "Esto también es tecnología: {t}."],
    "cta": ["{t}.", "¿Por dónde empezar a digitalizar tu negocio?", "Te ayudamos a decidir qué digitalizar primero."],
}


class OottoSimulado(OottoCliente):
    """Genera contenido determinista a partir de calendario.json y archivos locales de vista previa."""

    def __init__(self, fallos: str = "") -> None:
        # "motion:1,publicar" -> {"motion": 1, "publicar": inf}
        self._fallos: dict[str, float] = {}
        for item in filter(None, (s.strip() for s in fallos.split(","))):
            paso, _, veces = item.partition(":")
            self._fallos[paso] = int(veces) if veces else float("inf")

    def _quizas_fallar(self, paso: str) -> None:
        if self._fallos.get(paso, 0) > 0:
            self._fallos[paso] -= 1
            raise OottoError(f"[simulado] fallo forzado en '{paso}'")

    def generar_hooks(self, tema, pilar, marca, n):
        self._quizas_fallar("hooks")
        t = tema["titulo"]
        plantillas = _PLANTILLAS_HOOK.get(pilar["id"], ["{t}."])
        # Después de ":" va minúscula ("Ojo: 3 señales…"); en otro caso se respeta el título.
        return [p.replace(": {t}", ": " + t[0].lower() + t[1:]).replace("{t}", t) for p in plantillas][:n]

    def generar_guion(self, hook, tema, pilar, marca, duracion_s):
        self._quizas_fallar("guion")
        puntos = tema["puntos"]
        cierre = marca["cta"]["principal"]
        por_punto = max(4, (duracion_s - 3 - 4) // max(1, len(puntos)))
        escenas = [{"texto_pantalla": hook, "locucion": hook, "duracion_s": 3}]
        escenas += [{"texto_pantalla": p, "locucion": p + ".", "duracion_s": por_punto} for p in puntos]
        escenas.append({"texto_pantalla": cierre, "locucion": f"{cierre}. {marca['cta']['corto']}.", "duracion_s": 4})
        caption = "\n".join([hook, "", *[f"✅ {p}" for p in puntos], "", f"👉 {cierre}. {marca['cta']['corto']}."])
        rng = random.Random(tema["titulo"])
        extra = rng.sample(["#Digitalización", "#IoT", "#Inventario", "#Emprendedores", "#Centroamérica"], 2)
        return {"escenas": escenas, "caption": caption, "hashtags": marca["hashtags_base"] + extra}

    def generar_graficos(self, guion, marca, destino):
        self._quizas_fallar("graficos")
        destino.mkdir(parents=True, exist_ok=True)
        rutas = []
        total = len(guion["escenas"])
        for i, esc in enumerate(guion["escenas"], 1):
            ruta = destino / f"escena_{i:02d}.svg"
            ruta.write_text(_svg_escena(esc["texto_pantalla"], i, total, marca), encoding="utf-8")
            rutas.append(ruta)
        return rutas

    def generar_motion(self, guion, graficos, relacion, destino):
        self._quizas_fallar("motion")
        manifiesto = {
            "simulado": True,
            "nota": "En modo real aquí estaría el .mp4 renderizado por ootto.",
            "relacion": relacion,
            "duracion_s": sum(e["duracion_s"] for e in guion["escenas"]),
            "secuencia": [{"grafico": g.name, "duracion_s": e["duracion_s"], "transicion": "deslizar"}
                          for g, e in zip(graficos, guion["escenas"])],
        }
        destino.write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8")
        return destino

    def generar_musica(self, estilo, duracion_s, destino):
        self._quizas_fallar("musica")
        destino.write_text(json.dumps({"simulado": True, "estilo": estilo, "duracion_s": duracion_s,
                                       "licencia": "libre de regalías (supuesto)"}, ensure_ascii=False, indent=2),
                           encoding="utf-8")
        return destino

    def publicar(self, red, video, caption, programado_para):
        self._quizas_fallar("publicar")
        return {"id": f"sim-{red}-{datetime.now():%Y%m%d%H%M%S}", "url": None}


def _svg_escena(texto: str, i: int, total: int, m: dict) -> str:
    c, f = m["colores"], m["tipografia"]
    lineas = wrap(texto, 18 if i == 1 else 22)
    tam = 92 if i == 1 else 72
    y0 = 960 - (len(lineas) - 1) * tam * 0.6
    tspans = "".join(f'<tspan x="90" y="{y0 + n * tam * 1.2:.0f}">{escape(l)}</tspan>' for n, l in enumerate(lineas))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{c['borde']}"/><stop offset="1" stop-color="{c['fondo']}"/>
    </linearGradient>
    <radialGradient id="glow" cx=".85" cy=".1" r=".6">
      <stop offset="0" stop-color="{c['primario']}" stop-opacity=".25"/><stop offset="1" stop-color="{c['primario']}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1080" height="1920" fill="url(#g)"/>
  <rect width="1080" height="1920" fill="url(#glow)"/>
  <text x="90" y="170" font-family="{f['titulos']}, sans-serif" font-size="44" font-weight="700" fill="{c['texto']}">IF <tspan fill="{c['primario']}">Techworks</tspan></text>
  <rect x="90" y="{y0 - tam * 1.4:.0f}" width="120" height="10" rx="5" fill="{c['primario']}"/>
  <text font-family="{f['titulos']}, sans-serif" font-size="{tam}" font-weight="700" fill="{c['texto']}">{tspans}</text>
  <text x="90" y="1780" font-family="{f['datos']}, monospace" font-size="32" fill="{c['texto_secundario']}">{i:02d}/{total:02d} · {escape(m['lema'])}</text>
</svg>
"""
