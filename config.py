"""Carga y valida la configuración: .env (credenciales) + brand.json + calendario.json.

Nada de marca, pilares, horarios ni cuentas vive en el código: todo sale de esos archivos.
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parent

# Variables de entorno cuyo valor nunca debe aparecer en logs.
SECRETOS = ("OOTTO_API_KEY", "META_ACCESS_TOKEN", "TIKTOK_ACCESS_TOKEN", "NOTIFY_WEBHOOK_URL")

DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]


class ConfigError(Exception):
    pass


def cargar_env(ruta: Path) -> None:
    """Lee KEY=VALOR de .env sin pisar variables ya definidas en el entorno."""
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


def _leer_json(ruta: Path) -> dict:
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ConfigError(f"No existe {ruta.name}")
    except json.JSONDecodeError as e:
        raise ConfigError(f"{ruta.name} no es JSON válido (línea {e.lineno}): {e.msg}")


def _validar_brand(b: dict) -> None:
    faltan = [k for k in ("nombre", "colores", "tipografia", "voz", "cta", "hashtags_base") if k not in b]
    if faltan:
        raise ConfigError(f"brand.json: faltan claves {faltan}")
    for k in ("primario", "fondo", "texto"):
        if k not in b["colores"]:
            raise ConfigError(f"brand.json: falta colores.{k}")


def _validar_calendario(c: dict) -> None:
    faltan = [k for k in ("zona_horaria", "frecuencia", "horarios", "redes", "pilares", "generacion") if k not in c]
    if faltan:
        raise ConfigError(f"calendario.json: faltan claves {faltan}")
    for h in c["horarios"]:
        if h.get("dia") not in DIAS:
            raise ConfigError(f"calendario.json: día inválido {h.get('dia')!r}; usá {DIAS}")
    ids = [p["id"] for p in c["pilares"]]
    if len(ids) != len(set(ids)):
        raise ConfigError("calendario.json: hay pilares con id repetido")
    for p in c["pilares"]:
        if not p.get("temas"):
            raise ConfigError(f"calendario.json: el pilar {p['id']!r} no tiene temas")
    if not any(r.get("activa") for r in c["redes"].values()):
        raise ConfigError("calendario.json: no hay ninguna red activa")


@dataclass
class Config:
    brand: dict
    calendario: dict
    dry_run: bool
    ootto_modo: str
    data_dir: Path
    salida_dir: Path
    log_dir: Path
    log_level: str
    sim_fallos: str
    # repr=False para que nunca se impriman al hacer print(config)
    ootto_api_key: str = field(default="", repr=False)
    notify_webhook: str = field(default="", repr=False)

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.calendario["zona_horaria"])

    @property
    def redes_activas(self) -> dict:
        return {k: v for k, v in self.calendario["redes"].items() if v.get("activa")}

    def pilar(self, pilar_id: str) -> dict:
        for p in self.calendario["pilares"]:
            if p["id"] == pilar_id:
                return p
        disponibles = [p["id"] for p in self.calendario["pilares"]]
        raise ConfigError(f"Pilar {pilar_id!r} no existe. Disponibles: {disponibles}")


def cargar(raiz: Path = RAIZ) -> Config:
    cargar_env(raiz / ".env")
    brand = _leer_json(raiz / "brand.json")
    calendario = _leer_json(raiz / "calendario.json")
    _validar_brand(brand)
    _validar_calendario(calendario)

    dry_run = os.getenv("DRY_RUN", "true").strip().lower() not in ("false", "0", "no")
    modo = os.getenv("OOTTO_MODO", "simulado").strip().lower()
    if modo not in ("simulado", "mcp"):
        raise ConfigError(f"OOTTO_MODO inválido: {modo!r} (usá 'simulado' o 'mcp')")
    if modo == "simulado" and not dry_run:
        raise ConfigError("OOTTO_MODO=simulado solo puede usarse con DRY_RUN=true")

    def ruta(var: str, defecto: str) -> Path:
        p = Path(os.getenv(var, defecto))
        return p if p.is_absolute() else raiz / p

    return Config(
        brand=brand,
        calendario=calendario,
        dry_run=dry_run,
        ootto_modo=modo,
        data_dir=ruta("DATA_DIR", "data"),
        salida_dir=ruta("SALIDA_DIR", "salida"),
        log_dir=raiz / "logs",
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        sim_fallos=os.getenv("OOTTO_SIM_FALLOS", ""),
        ootto_api_key=os.getenv("OOTTO_API_KEY", ""),
        notify_webhook=os.getenv("NOTIFY_WEBHOOK_URL", ""),
    )


class _FiltroSecretos(logging.Filter):
    """Reemplaza cualquier valor de credencial que aparezca en un mensaje de log."""

    def __init__(self) -> None:
        super().__init__()
        self.valores = [v for k in SECRETOS if len(v := os.getenv(k, "")) >= 6]

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        for v in self.valores:
            msg = msg.replace(v, "***")
        record.msg, record.args = msg, None
        return True


def configurar_logging(cfg: Config) -> None:
    cfg.log_dir.mkdir(parents=True, exist_ok=True)
    formato = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    filtro = _FiltroSecretos()
    raiz = logging.getLogger()
    raiz.setLevel(cfg.log_level)
    raiz.handlers.clear()
    for h in (logging.StreamHandler(), logging.FileHandler(cfg.log_dir / "ifsocial.log", encoding="utf-8")):
        h.setFormatter(formato)
        h.addFilter(filtro)
        raiz.addHandler(h)
