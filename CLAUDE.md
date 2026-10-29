# CLAUDE.md — IF Contenido

Herramienta interna de **IF Techworks** (iftechworks.com, Guatemala) para crear, aprobar y publicar contenido en
Instagram y TikTok. Construida solo con componentes gratuitos o de código abierto. Detalle de uso en [README.md](README.md).

## Reglas del proyecto (no negociables)

- **Nada se publica sin aprobación humana.** Una sola persona aprueba. `pipeline.publish()` exige estado `aprobado`.
- `DRY_RUN=true` por defecto: genera todo y simula la publicación (`publish_simulation.json`), sin llamar APIs.
- Credenciales solo en `.env` (nunca en código ni logs; `core/config.py` las enmascara en los logs).
  No pedir ni manejar contraseñas de Meta/TikTok: el usuario autoriza por OAuth en su navegador.
- Toda la configuración (marca, pilares, horarios, motores, prompts, plantillas) vive en `config/` y `templates/`, no en código.
- Cada módulo es reemplazable vía `config/settings.yaml > engines`.
- Si un paso falla: un reintento, luego estado `fallido` + aviso. Nunca publicar contenido incompleto (ver `validate.py`).
- Música: solo pistas con licencia comercial registrada en `assets/music/library.yaml`; el crédito CC BY va al caption.
- Revisar la licencia antes de agregar cualquier librería/modelo; registrar en `docs/licencias.md`.
  Descartados: Remotion (licencia de empresa paga), XTTS-v2 y Fish Speech (no comerciales), YouTube Audio Library.

## Marca y contenido

- Colores, tipografías y tono en `config/brand.json` (extraídos SOLO del sitio web, no del Instagram).
  Verde bosque `#0a1410`…`#1d362b`, dorado `#f0c419`, marfil `#fefcf3`; Space Grotesk / Inter / JetBrains Mono.
- Copy en español de Guatemala con **voseo** ("contanos", "agendá", "podés"). `copy/lint.py` detecta tuteo y tildes faltantes.
- Nunca inventar clientes, cifras ni testimonios; los casos son "escenarios de ejemplo".
- Pilares: educativo 35 %, soluciones 25 %, tips 20 %, propósito y proceso 10 %, CTA 10 %. 4 piezas/semana.
- Contacto oficial: WhatsApp +502 3808 9808 · contacto@iftechworks.com (avisos van a este correo).

## Entorno (Windows, esta PC)

- RTX 3050 6 GB, 16 GB RAM. La PC debe estar encendida en los horarios de publicación.
- `.venv/` (Python 3.11): la herramienta. `.venv-tts/`: PyTorch CUDA + Chatterbox (aislado; se llama por subproceso).
- FFmpeg y uv vía winget (el PATH puede no refrescarse; `video/ffmpeg.py` busca en la carpeta de winget).
- Ollama + `qwen3:8b`. Si no responde en 127.0.0.1:11434, abrir la app de Ollama o correr `ollama serve`.
- Modelos de voz Kokoro en `models/kokoro/` (fuera de git). Datos generados en `data/` (fuera de git).
- Pruebas: `.venv/Scripts/python -m pytest -q tests`.
- Repo: github.com/JoseFernando04/IF (privado), rama `main`.

## Avances

### Fase 1 — Reel y carrusel en simulación ✅ (2026-10-29)
- Pipeline completo con CLI `ifcontent` (generar-reel, generar-carrusel, listar, ver, aprobar, cambios, descartar, publicar).
- Video: motor `html_frames` (escenas HTML animadas → Playwright cuadro a cuadro → FFmpeg H.264/AAC 1080x1920 30 fps).
- 4 piezas de ejemplo en `examples/piezas/` (2 reels, 2 carruseles; 2 con copy a mano y 2 con Qwen3).
- Comentarios del usuario tras revisar:
  - La voz Kokoro suena robótica → cambiado a **Chatterbox Multilingual** (MIT). Instalado; **falta probarlo** y que el usuario lo escuche.
  - No quiere barra de progreso ni subtítulos en los reels → desactivados (`reel.progress_bar`, `reel.captions` en settings).
  - Necesitaba ver los carruseles completos → se genera `preview.jpg` (vista con todas las slides) por carrusel.
- Calidad de Qwen3: aceptable con ejemplo few-shot + revisor; a veces copia demasiado el ejemplo. Claude vía MCP (Fase 5) dará mejor copy.

### Pendiente
- [ ] Probar Chatterbox, enviar muestras de voz y regenerar los reels de ejemplo.
- [ ] Opcional: grabar 10-20 s de una voz real del equipo (con permiso) en `assets/voice/referencia.wav` para que Chatterbox la use.
- [ ] Agregar pistas de Pixabay Music (las descarga el usuario; ver `docs/licencias.md`).
- [ ] **Fase 2:** calendario mensual automático, panel web local de aprobación (FastAPI + HTMX), avisos SMTP
      (falta saber el proveedor de correo de contacto@iftechworks.com), Programador de tareas de Windows.
- [ ] **Fase 3:** guías de apps Meta y TikTok; Instagram con Instagram Login + Standard Access (sin App Review, solo cuenta propia)
      y Cloudflare Quick Tunnel para la URL pública temporal; TikTok con otra cuenta/correo: plan B `video.upload` (borrador en
      bandeja) o plan C (MP4 + caption por correo para subir a mano). Crear página `/privacidad` en el sitio.
- [ ] **Fase 4:** métricas (`instagram_business_manage_insights`) y ajuste del calendario.
- [ ] **Fase 5:** servidor MCP propio.
