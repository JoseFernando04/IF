# IF Social — contenido automatizado para Instagram y TikTok

Herramienta interna de **IF Techworks** para planificar, generar, aprobar, publicar y medir contenido en Instagram y TikTok con ootto.

> **Estado actual: Fase 1 en modo simulación.** No hay suscripción activa de ootto, así que el backend de ootto es **simulado**: la interfaz (`ootto_cliente.py`) es una suposición de cómo funcionará el MCP real. Cuando haya suscripción se listan sus herramientas reales, se ajusta la interfaz si hace falta y se escribe el cliente real. Nada se publica de verdad hasta entonces.

## Arquitectura

```
calendario.json ─┐                       ┌──────────── OottoCliente (interfaz) ─────────────┐
brand.json ──────┼─> config.py ─> pipeline.py ──> hooks → guion → gráficos → motion → música │
.env ────────────┘        │            │          │  OottoSimulado (hoy) | OottoMCP (pend.)  │
                          │            │          └──────────────────────────────────────────┘
                          │            ├─> validación (completa + reglas de marca)
                          │            ├─> registro.py (SQLite: estados + historial + publicaciones)
                          │            ├─> preview.html para revisión humana
                          │            └─> notificar() (log + webhook) si algo falla 2 veces
                          └─> main.py (CLI)

Estados:  borrador ─> en_revision ─> aprobado ─> publicado
              ▲            │ rechazar      │
              └────────────┘               └─> fallido (reintento de publicación posible)
```

Reglas:

- **Nada se publica sin aprobación humana explícita.** `publicar` exige estado `aprobado` y el nombre de quien aprobó.
- **No se publica contenido incompleto.** Antes de pasar a revisión y otra vez antes de publicar se verifica:
  - que la pieza tenga hook, guion, gráficos, video y música;
  - que los textos respeten los límites de caracteres y hashtags de cada red;
  - que no usen palabras prohibidas por la marca.
- **Reintento único.** Cada paso con ootto se reintenta una vez. Si vuelve a fallar, la pieza queda como `fallido` y se manda una notificación.
- **Credenciales solo en `.env`.** El log reemplaza por `***` cualquier valor de credencial que aparezca.
- **`DRY_RUN=true`** genera todo pero no llama a la publicación; solo registra lo que se habría publicado. El modo simulado se niega a correr con `DRY_RUN=false`.

## Estructura

| Archivo | Qué es |
|---|---|
| `brand.json` | Identidad: colores, tipografía, estilo visual, voz, palabras prohibidas, CTA, hashtags. **Editable.** |
| `calendario.json` | Frecuencia, horarios, redes y sus límites, pilares con temas, parámetros de generación, aprobación. **Editable.** |
| `.env.example` | Plantilla de variables de entorno (credenciales y modos). |
| `config.py` | Carga y valida configuración; logging con filtro de credenciales. |
| `ootto_cliente.py` | Interfaz `OottoCliente` + `OottoSimulado`. |
| `pipeline.py` | Generación con reintentos, validación, aprobación, publicación, vista previa. |
| `registro.py` | SQLite (`data/ifsocial.db`): piezas, historial de estados, publicaciones. |
| `main.py` | Línea de comandos. |
| `ejemplos/fase1/` | 3 piezas de ejemplo generadas en simulación. |
| `salida/`, `data/`, `logs/` | Generados en ejecución (no se suben a git). |

Se agregarán en fases posteriores: `planificador.py` (Fase 2), `programador.py` (Fase 3), `metricas.py` (Fase 4).

## Fases

| Fase | Contenido | Estado |
|---|---|---|
| 1 | Una pieza de punta a punta en simulación: generar, validar, revisar, aprobar y simular la publicación | ✅ Hecha (con ootto simulado) |
| 2 | Calendario mensual automático: reparte las piezas por peso de pilar en los horarios configurados y rota los temas. Cola de aprobación con un canal por definir (panel web, WhatsApp o Slack); hoy se aprueba por línea de comandos | Pendiente |
| 3 | Publicación programada: proceso que cada hora publica las piezas aprobadas cuya hora llegó, más el cliente real de ootto (MCP) | Pendiente; requiere suscripción a ootto |
| 4 | Métricas: lectura de Instagram Insights y TikTok, guardadas por pieza; ajuste de pesos y horarios del mes siguiente | Pendiente; requiere tokens o exportación CSV |

## Instalación

Requiere **Python 3.10 o superior**. No hay dependencias externas.

```bash
git clone <repo> && cd IF
cp .env.example .env      # dejar DRY_RUN=true y OOTTO_MODO=simulado para pruebas
python main.py validar
```

## Uso diario

```bash
python main.py generar --pilar educativo --para 2026-11-03T12:30   # genera y deja en revisión
python main.py listar --estado en_revision                          # cola de aprobación
# abrir salida/<id>/preview.html para revisar hook, storyboard y textos
python main.py aprobar <id> --por "Nombre"                          # o:
python main.py rechazar <id> --por "Nombre" --nota "Cambiar el hook"
python main.py publicar <id>                                        # en DRY_RUN solo simula
python main.py ver <id>                                             # detalle + historial de estados
```

Los ids de pilar están en `calendario.json`: `educativo`, `casos`, `detras`, `tips`, `impacto` y `cta`. `--tema N` elige el N-ésimo tema del pilar, empezando en 0.

### Probar fallos

```bash
OOTTO_SIM_FALLOS=motion:1 python main.py generar --pilar tips    # falla una vez, el reintento lo resuelve
OOTTO_SIM_FALLOS=graficos python main.py generar --pilar casos   # falla siempre -> fallido + notificación
```

## Configuración

- **Marca:** se edita en `brand.json`. Colores y tipografías vienen del sitio web. Falta contrastarlos con el feed de Instagram.
- **Tono:** el sitio usa voseo ("Agendá", "Contanos"), y el contenido de ejemplo también. Si se decide otro tratamiento, se cambia `voz.tratamiento` y los textos de `cta`.
- **Pilares y temas:** cada tema lleva `titulo` y `puntos`. Los puntos son la materia prima del guion. `peso` es el porcentaje del calendario que ocupa el pilar.
- **Frecuencia:** 3 piezas por semana (martes 12:30, miércoles 18:30, jueves 12:30, hora de Guatemala). La justificación está en `calendario.json`.
- **Notificaciones:** si `NOTIFY_WEBHOOK_URL` tiene valor, los avisos de error también se mandan ahí (Slack, Discord o Google Chat).

## Supuestos y pendientes

- **La interfaz de ootto es supuesta.** Se asumió que ootto genera hooks, guion, gráficos, motion y música, y que publica. No se sabe si **devuelve métricas**: si no lo hace, la Fase 4 usará la API de Instagram (Meta Graph) y la de TikTok, o una exportación CSV.
- **Formato del video simulado.** En simulación, "motion" produce un manifiesto (`video.json`) y "música" un archivo de metadatos; no hay `.mp4` real.
- **Datos por definir con IF Techworks:**
  - aprobadores y canal de aprobación;
  - cuenta de TikTok;
  - plan y límites de ootto;
  - acceso a métricas;
  - servidor donde va a correr la herramienta.
