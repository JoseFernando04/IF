# IF Contenido

Herramienta interna de **IF Techworks** para crear, aprobar y publicar contenido en Instagram y TikTok.
Todo corre en esta PC con componentes gratuitos o de código abierto (ver [docs/licencias.md](docs/licencias.md)).

**Regla de oro: nada se publica sin aprobación humana.** Además, mientras `DRY_RUN=true` (por defecto) no sale nada de la PC.

## Estado

| Fase | Qué incluye | Estado |
|---|---|---|
| 1 | Reel y carrusel completos en modo simulación | ✅ |
| 2 | Calendario editorial y panel de aprobación | Pendiente |
| 3 | Publicación en Instagram + TikTok (borrador / manual) | Pendiente |
| 4 | Métricas y ajuste del calendario | Pendiente |
| 5 | Servidor MCP para pedírselo a Claude | Pendiente |

## Cómo funciona

```
copy (Ollama o archivo) → gráficos / video + voz + música → validación → EN REVISIÓN → aprobado → publicación
```

| Módulo | Carpeta | Motor actual (cambiable en `config/settings.yaml`) |
|---|---|---|
| Copy | `src/ifcontent/copy/` | `ollama` (Qwen3 8B local) o `file` (copy escrito a mano o por Claude) |
| Gráficos | `src/ifcontent/graphics/` | Plantillas HTML/CSS → JPEG con Playwright |
| Video | `src/ifcontent/video/` | `html_frames`: escenas HTML animadas → cuadros → FFmpeg |
| Audio | `src/ifcontent/audio/` | Kokoro (voz) + biblioteca de música con licencias + mezcla con ducking |
| Validación | `src/ifcontent/validate.py` | Especificaciones de Instagram, duración, licencia de la música |
| Publicación | `src/ifcontent/publish/` | `dry_run` (Fase 3: Instagram, TikTok inbox, correo manual) |
| Estado | `src/ifcontent/core/db.py` | SQLite en `data/ifcontent.db` |

Estados de una pieza: `borrador → en_revision → aprobado → publicado`, y además `cambios_solicitados`, `descartado` y `fallido`.
Si un paso falla se reintenta una vez; si vuelve a fallar la pieza queda `fallido` y llega un aviso.

## Instalación (Windows)

1. Instalar herramientas del sistema:
   ```bash
   winget install Gyan.FFmpeg
   ```
   ```bash
   winget install Ollama.Ollama
   ```
2. Descargar el modelo de texto (unos 5 GB):
   ```bash
   ollama pull qwen3:8b
   ```
3. Crear el entorno de Python e instalar la herramienta:
   ```bash
   python -m venv .venv
   ```
   ```bash
   .venv/Scripts/python -m pip install -e .
   ```
   ```bash
   .venv/Scripts/python -m playwright install chromium
   ```
4. Descargar el modelo de voz Kokoro en `models/kokoro/`:
   - `kokoro-v1.0.onnx` y `voices-v1.0.bin` desde
     https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
5. Copiar `.env.example` a `.env` y completar lo que corresponda. **El `.env` nunca se sube a git.**

## Uso diario

Todos los comandos se corren desde la carpeta del proyecto:

```bash
.venv/Scripts/ifcontent generar-reel --pilar educativo --tema "Mitos de la digitalización en pymes"
```
```bash
.venv/Scripts/ifcontent generar-carrusel --pilar tips --tema "Cómo ordenar tu catálogo antes de digitalizarlo"
```
```bash
.venv/Scripts/ifcontent listar
```
```bash
.venv/Scripts/ifcontent ver 3
```
```bash
.venv/Scripts/ifcontent aprobar 3
```
```bash
.venv/Scripts/ifcontent cambios 3 --nota "Cambiar el gancho por una pregunta"
```
```bash
.venv/Scripts/ifcontent publicar 3
```

Pilares disponibles: `educativo`, `soluciones`, `tips`, `proposito`, `cta`.

Para usar un copy escrito a mano (o por Claude) en vez del LLM local, pasá `--copy-file ruta.yaml`.
El formato está en `examples/copy/`.

Cada pieza queda en `data/output/<id>-<tipo>-<tema>/`:
- `reel.mp4` y `cover.jpg`, o `slide_01.jpg` … `slide_NN.jpg`
- `caption.txt`: caption final con crédito de música y hashtags
- `copy.json`: guion completo
- `manifest.json`: detalle técnico y advertencias del revisor automático
- `publish_simulation.json`: qué llamadas se harían a Instagram y TikTok (al correr `publicar` en modo simulación)

## Configuración (sin tocar código)

| Archivo | Qué controla |
|---|---|
| `config/brand.json` | Colores, tipografías, logo, tono, servicios y contacto |
| `config/pillars.yaml` | Pilares, peso en el calendario, temas sugeridos y estilo de música |
| `config/calendar.yaml` | Piezas por semana y horarios |
| `config/settings.yaml` | Motores de cada módulo, voz, duración, límites |
| `config/prompts/` | Instrucciones y ejemplo de referencia que recibe el LLM |
| `templates/` | Plantillas visuales HTML/CSS |
| `assets/music/library.yaml` | Biblioteca de música con licencias |
