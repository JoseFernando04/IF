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

### Pruebas de voz (2026-10-29) — ninguna aprobada todavía
El usuario quiere una voz **humana, no robótica**, preferiblemente con acento latino (tipo México); no importa que no sea guatemalteca.
Muestras generadas en `data/voz/` (fuera de git), todas con la misma frase:
- Kokoro `em_alex` (voz original): rechazada, suena robótica.
- Chatterbox Multilingual con voz por defecto (`voz-nueva-chatterbox.mp3`): enviada; no le convenció.
- A/B: Chatterbox clonando como referencia una voz sintética mexicana de Piper (`es_MX-claude-high` Apache 2.0,
  `es_MX-ald-medium` Unlicense). C/D: esas voces de Piper directas. **No le gustó ninguna.**
- Chatterbox ya funciona en la GPU (`.venv-tts`, ~30 it/s); `piper-tts` también instalado ahí; modelos Piper en `models/piper/`.
- El pipeline aún tiene `engines.tts: chatterbox` sin referencia y los reels de ejemplo NO se regeneraron.

Próximas opciones a proponer (todas deben ser gratis y con licencia comercial):
1. **Grabar una voz real** del equipo (10-20 s, con permiso) en `assets/voice/referencia.wav` y clonarla con Chatterbox
   → suele ser lo más humano. Recomendado.
2. Buscar otros modelos abiertos con voces latinas naturales y licencia comercial (verificar licencia de pesos, no solo código;
   descartar los NC). Probar ajustes de Chatterbox (`exaggeration`, `cfg_weight`) con una buena referencia.
3. Reels solo con música (`engines.tts: none`) mientras se decide.

### Rediseño "que no se vea IA" (2026-10-29)
Brief del usuario: rediseñar carruseles y reels (ver `prototypes/direcciones/README.md`). Se mostraron 2 direcciones;
**el usuario eligió la B · Documental** (`prototypes/direcciones/b-documental/`):
foto real en duotono verde + grano, Bricolage Grotesque condensada en mayúsculas, Instrument Serif itálica para acentos,
Inter Tight para texto, cintas amarillas como etiquetas, match cuts, subtítulos editoriales palabra por palabra.
- Reels: **mínimo 7-10 s** (el usuario siente cortos los de 5 s). El prototipo B dura 12,5 s: pregunta → "NO." → Excel tachado → cierre CTA.
- Motion con GSAP 3.15.0 vendorizado (`assets/vendor/`), renderizado por `render_html_video()`; SFX propios (`tools/make_sfx.py`).
- Sin Node/HyperFrames/Remotion (no hace falta; menos superficie de ataque). Fuentes solo OFL. Fotos: `assets/photos/CREDITOS.yaml`.
- Abiertos: ¿cifras de ejemplo (prohibidas por la regla de no inventar) o datos reales de clientes? ¿subtítulos sí o no
  (antes dijo que no; la dirección B los usa)? Fotos propias/locales serían mejores que las de Unsplash.
- Siguiente: producir el carrusel completo de 7 slides con layouts distintos y el reel completo en estilo B, y llevar ese
  estilo a las plantillas del pipeline (`templates/`) con 5 layouts base de carrusel.

### Voz femenina LATAM y carruseles B (2026-10-29)
- El usuario quiere **voz de mujer latinoamericana** y el video final **sin subtítulos, con voz**.
- ElevenLabs gratis descartado (sin licencia comercial). Candidatas: **Azure** (es-GT-MartaNeural, es-MX-DaliaNeural…)
  y **Google** Chirp 3 HD (es-US-Chirp3-HD-Aoede…). Motores `azure`/`google` ya integrados en `audio/tts.py`.
- **Bloqueado:** faltan las claves en `.env` (el usuario las crea con `docs/guia-voces.md`). Luego correr
  `tools/probar_voces.py`, enviar las muestras y esperar que elija ANTES de producir videos.
- Carruseles B listos: `examples/copy/b/*.yaml` → `graphics/carousel_b.py` (12 layouts) → `examples/piezas/b-carrusel-*`.

### Pendiente
- [ ] Definir la voz (ver opciones arriba) y regenerar los reels de ejemplo sin barra ni subtítulos.
- [ ] Agregar pistas de Pixabay Music (las descarga el usuario; ver `docs/licencias.md`).
- [ ] **Fase 2:** calendario mensual automático, panel web local de aprobación (FastAPI + HTMX), avisos SMTP
      (falta saber el proveedor de correo de contacto@iftechworks.com), Programador de tareas de Windows.
- [ ] **Fase 3:** guías de apps Meta y TikTok; Instagram con Instagram Login + Standard Access (sin App Review, solo cuenta propia)
      y Cloudflare Quick Tunnel para la URL pública temporal; TikTok con otra cuenta/correo: plan B `video.upload` (borrador en
      bandeja) o plan C (MP4 + caption por correo para subir a mano). Crear página `/privacidad` en el sitio.
- [ ] **Fase 4:** métricas (`instagram_business_manage_insights`) y ajuste del calendario.
- [ ] **Fase 5:** servidor MCP propio.
