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
  En redes, cada formato usa sus fuentes OFL (documental: Bricolage/Instrument Serif/Inter Tight; 8-bit: Press Start 2P), con la paleta de marca.
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

## Cómo trabajamos ahora (desde 2026-11-09)

- **Rutina diaria por la mañana:** ver `docs/plan-contenido-diario.md`. Cada día: **3 opciones de reel + 3 de post**;
  el equipo elige ~2 piezas para publicar. Una **conversación nueva por día** (para no quedarse sin contexto).
- Al empezar ("Listo, empecemos el día"): revisar `data/dias/` y `VideosInstagram/` para no repetir tema ni formato,
  proponer 3 reels (concepto + guion a una sola voz + imagen de muestra) y 3 posts terminados.
- **Reels:** José genera la voz en ElevenLabs (plan pago) con el guion y la deja en `assets/voice/elevenlabs/AAAA-MM-DD-reel-X.mp3`.
  Se usa el audio tal cual; solo se agregan animación, música y efectos. Sin subtítulos (solo palabras clave en pantalla).
- **Rotar formatos** (ningún formato dos días seguidos). Catálogo y estado en `docs/plan-contenido-diario.md`.
  El usuario quiere variedad real, siguiendo lo que hoy llama la atención en redes, no solo documental y 8-bit.
  **Desde 2026-11-11:** al menos 1-2 de los 3 reels deben ser un formato NUEVO de `docs/tendencias-reels.md` (no la misma plantilla con otro texto).
- Descripciones: llamativas, que **no repitan el guion**, con WhatsApp +502 3808 9808 y 5 hashtags. Los posts llevan además `titulo_tiktok` (máx. 90 caracteres).
- Publicación: el equipo programa a mano en Meta Business Suite y TikTok (la automatización por API es la Fase 3).
- **Control de lo publicado:** `docs/publicaciones.yaml` (vista en `docs/publicaciones.md`) con `tools/publicaciones.py`.
  Cuando el usuario diga qué subió ("ayer subí el reel A del 10"), correr `marcar <día> <pieza> --redes ig,tt --fecha AAAA-MM-DD`
  (o `descartar`). Al empezar el día: `sync` y `lista --pendientes` para recordar lo que falta subir.
- **Tablero interactivo (desde 2026-11-11):** https://claude.ai/artifact/Lhzfzm9U8GHYvEC1kt9Rim (fuente `docs/panel/publicaciones.html`).
  El equipo marca ahí pendiente/subido/descartado. **Al empezar el día:** `ArtifactData list` de la colección `piezas` con `out_dir`
  → `tools/publicaciones.py importar-panel <out_dir>` → `sync`. Piezas nuevas o marcadas por chat: `exportar-panel <carpeta>` y
  subirlas con `ArtifactData batch` (id `<día>__<pieza>`, `if_version` si ya existen).
- **Formato `cine` (desde 2026-11-10; EN PAUSA desde 2026-11-11 hasta que el usuario lo retome):** reels para convertir vistas en clientes, con tomas de Higgsfield, voz del equipo y una
  palabra clave por WhatsApp. Reglas en `docs/plan-contenido-diario.md` ("Enfoque cine"). Generar tomas cuesta créditos:
  mostrar el plan y generar solo lo que el usuario eligió. `HF_KEY` en `.env`. Nunca generar tomas sin guion aprobado por el equipo.
  Montaje: `tools/render_formato.py <yaml>` (`--borrador` = sin voz, tiempos estimados). Gastado al 2026-11-10: ~USD 6.76 de 15. Decir siempre el precio antes de generar; el aviso "Escena de ejemplo" va solo en la descripción, no en el video.
- Commit y push solo cuando el usuario lo pide (suele pedirlo al cerrar el día).

## Herramientas listas

| Para | Comando |
|---|---|
| Reel documental (estilo B) con audio externo | `tools/render_reel_voz.py --audio RUTA --tal-cual --musica ID --musica-db N` |
| Reel 8-bit | `tools/render_8bit.py examples/copy/8bit/<reel>.yaml` (escenas en `templates/video/8bit/reel.html`) |
| Reels chat / mito / top3 / pov / antesdespues / cinetica / sistema / decilo / trailer / diminuto | `tools/render_formato.py examples/copy/dia/<día>-reel-X.yaml` (`--muestra 3,9,15` sin audio = imágenes de muestra) |
| Posts checklist / este-o-este / frase / infografia / diccionario / recibo | `tools/render_post.py examples/copy/dia/<día>-post-N.yaml` (plantilla `templates/graphics/posts/post.html`) |
| Tomas de video con IA (formato `cine`) | `tools/generar_clip.py <yaml>` muestra el plan; `--confirmar` genera (Higgsfield · Seedance 2.5, **de pago**). Motor: `ifcontent.video.higgsfield`. Ejemplo del SDK: `examples/higgsfield/main.py` |
| Fondos animados | `templates/shared/fondos.js` (Paper Shaders: `malla`, `grano`, `puntos`, `papel`, `trama`); Chromium con `--allow-file-access-from-files` |
| Carrusel documental | `ifcontent.graphics.carousel_b.render_from_file(yaml, carpeta)` con YAML como `examples/copy/b/*.yaml` |
| Revisar un audio | `ifcontent.audio.transcribe.transcribir([ruta])` (Whisper local) |
| Música | `assets/music/library.yaml` (incluye `chiptune-bodega` y `if-firma`, propias, sin crédito) |
| Sonido característico de IF | `tools/make_firma.py` → `assets/music/if-firma.wav/.mp3` (34 s) y `assets/sfx/if-logo.wav` (logo sonoro, 3 s) |

- Medir picos sin `-ac 1` en ffmpeg (suma ~3 dB). Revisar cuadros reales del video antes de enviarlo.
- Voces y renders con voces de personas: nunca a git (`assets/voice/`, `data/`).

## Herramientas de animación a evaluar (revisadas 2026-11-08, sin instalar)

IF Techworks tiene **2 personas**: Remotion es gratis para empresas de hasta 3 (confirmar en remotion.dev antes de instalar; requiere Node.js).
| Repo | Licencia | Notas |
|---|---|---|
| paper-design/shaders | Apache-2.0, organización, activo | ✅ **Instalado 2026-11-08** (v0.0.82 vendorizada, ver `docs/licencias.md`). |
| lemomo-ai/lemo-opuscar | MIT, cuenta personal, creado sep-2026 | ❌ **No instalar** (revisado 2026-11-08: scripts de descarga, deps sin fijar, cambia a diario). Sus `styles/*/STYLE.md` sirven como referencia de diseño. |
| remotion-dev/remotion + remotion-dev/skills | Licencia propia de Remotion; skills sin licencia declarada | Alternativa al motor propio para formatos nuevos. |
| heygen-com/hyperframes | Apache-2.0, organización | HTML → video: hace lo mismo que nuestro `render_html_video`. Baja prioridad. |
| JohnHeibel/ClaudeAnimationBase | MIT, cuenta personal, sin cambios desde sep-2026 | Dibujos animados a mano. Baja prioridad. |
Antes de instalar: fuente oficial, revisar SKILL.md y scripts (`npm install --ignore-scripts`), versiones fijas, `npm audit`. Registrar en `docs/licencias.md`.

## Estado actual

- Publicados en IG y TikTok: 2 reels (`VideosInstagram/`): documental con voz de José y 8-bit.
- Guiones 8-bit 4-7 sin producir (`docs/guiones-8bit.md`).
- Pendiente técnico: Fase 2 (panel de aprobación), Fase 3 (publicación por API), Fase 4 (métricas), Fase 5 (MCP).
- Historial completo de decisiones y pruebas: `docs/historial-proyecto.md`.
