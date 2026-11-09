# Historial del proyecto (oct-nov 2026)

Detalle de decisiones, pruebas y aprendizajes. El estado actual está en CLAUDE.md.


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

### Voces femeninas locales y test con voz (2026-11-02)
- 6 voces femeninas locales en `tools/probar_voces.py` (Kokoro dora, Piper es_MX-claude / es_AR-daniela, Chatterbox
  imitando a esas). El usuario pidió test con la **#5 (Chatterbox imitando a daniela, argentina)**.
- `tools/render_reel_voz.py --voz N`: genera la voz por frase, escribe `tiempos.js` y la animación de
  `prototypes/direcciones/b-voz/reel.html` se sincroniza a cada frase (sin subtítulos). Resultado: 23,4 s.
- Azure: el usuario ya creó la cuenta (tiene USD 200 de crédito de prueba) y le preocupa que le cobren. Se le explicó:
  usar SOLO un recurso Speech **Free F0** (no consume créditos y se bloquea al pasar el límite, no cobra).

### Azure configurado (2026-11-02)
- Clave Azure (F0, eastus) en `.env` y funcionando. Cuenta actual es **@uvg.edu.gt (directorio UVG)**: se recomendó
  pasar a una cuenta de la empresa antes de publicar (términos de suscripción estudiantil y control de la cuenta).
- 8 voces Azure generadas (A1-A8 en `tools/probar_voces.py --nube`), incluidas HD: Dalia DragonHD (A6), Valeria y Harper
  MAI-Voice (A7, A8). La capa F0 limita ~20 solicitudes/min: `AzureTTS` reintenta ante 429.
- Reel B con A6 renderizado (19,9 s) en `prototypes/direcciones/b-voz/reel.mp4` (copia en `data/voz/`).
- Esperando que el usuario elija voz (A1-A8 o la #5 local).

### Voces reales del usuario y amigos (2026-11-02)
- Las voces de Azure le siguen sonando algo robóticas; quiere usar **voces grabadas por él y sus amigos**.
- Guía: `docs/guia-grabar-voces.md` (permiso escrito obligatorio por persona, cómo grabar, textos a leer).
- `assets/voice/<persona>/` (fuera de git: datos personales) con `permiso.*`, `referencia.*` (20-30 s) y `frase1..5.*`.
- `tools/preparar_voz.py` limpia (graves, ruido, silencios, volumen) → `*.limpio.wav`; exige permiso; avisa si la referencia < 12 s
  (con referencias cortas Chatterbox corta frases).
- `tools/render_reel_voz.py --grabada <persona>` (voz real tal cual) o `--clon <persona>` (Chatterbox imita la referencia).
  Flujo probado de punta a punta con grabaciones simuladas en m4a.

### Voces reales de José e Irvin y reel de conversación (2026-11-02)
- Grabaciones en `assets/voice/jose` y `assets/voice/irvin` con permisos (capturas de WhatsApp). Nombres libres:
  `tools/preparar_voz.py` transcribe con **Whisper local** (faster-whisper en `.venv-tts`, MIT) y detecta si cada audio es
  la referencia, el guion del reel B o las líneas de un diálogo, y lo corta por frase/línea con tiempos por palabra.
- Reel B con voz real: `data/voz/reel-grabada-irvin.mp4` y `reel-grabada-jose.mp4`.
- **Reel de conversación** (idea del usuario: suena más real): `prototypes/direcciones/b-conversacion/` (guion.yaml + reel.html),
  `tools/render_conversacion.py --fuente clon|grabada`. José = IF Techworks, Irvin = el dueño. Clon con QA automático
  (Whisper verifica cada línea y regenera; Chatterbox a veces balbucea o cambia palabras). 34 s.
- Siguiente: que graben sus líneas del diálogo (guía §5) para la versión 100 % humana.

### Eco y ruido en el clon (2026-11-02)
- Al usuario NO le gustó el clon: mucho eco/ruido. Causa medida: Irvin grabó en **nota de voz de WhatsApp** (Opus, sin agudos
  >8 kHz) en cuarto con eco (~420 ms de cola); José con AAC bueno pero ruido de fondo (-59 dBFS). Chatterbox copia el cuarto.
- Mejoras: limpieza con IA en `.venv-tts` — **WPE** (nara_wpe, MIT) contra eco + **DeepFilterNet3** (MIT) contra ruido —
  en referencias y grabaciones (`audio/enhance.py`, `denoise_worker.py`) y en la salida del clon (`tts.chatterbox.limpiar_salida`).
  Chatterbox usa solo ~10 s de la referencia → `preparar_voz.py` deja el mejor tramo de 11 s.
- Guía de grabación reescrita (`docs/guia-grabar-voces.md` §2-3): sin WhatsApp, carro estacionado/clóset, 15-20 cm,
  3 s de silencio inicial; nuevo texto de referencia expresivo (45-60 s). Recomendado: grabar el diálogo real (sin clon).
- Comparación enviada: `data/voz/audio-reel-ANTES.mp3` vs `reel-conversacion-clon-DESPUES.mp4`.

### Regrabación (2026-11-06)
- **Solo José regrabó** (`Prueba_3` guion del reel B, `Prueba_4` referencia; texto viejo, no el nuevo de la guía). Mejora medida:
  ruido -59 → -75 dBFS, cola ~290 → 140-240 ms. **Irvin sigue con las notas de WhatsApp del 02-nov** (cola 420 ms, sin agudos).
- `preparar_voz.py` mide cada grabación y aplica WPE/DeepFilterNet solo si hace falta (`necesita_limpieza`).
- Pruebas en `data/voz/prueba-2026-11-06/`: reel B con voz real de José, conversación con clones (37 s) y pista de solo voces.
- Falta: Irvin regraba con la guía; ambos graban sus líneas del diálogo (guía §5) para la versión 100 % real.

### Música y conversación más natural (2026-11-06)
- Reel de José "se escucha mal": la música casi no se oía (-30 dB en el cierre). Ahora `music.volume_db: -12`, ducking suave
  (`duck_threshold`, `duck_ratio`), `pulir_voz()` (EQ + compresión) y `--musica ID` en `render_reel_voz.py`.
  Opciones en `data/voz/prueba-2026-11-06/reel-jose-musica-{digital-lemonade,inspired}.mp4`.
- Para medir picos NO usar `-ac 1` en ffmpeg: suma ~3 dB y da falsos positivos de saturación.
- Conversación clonada "robotizada": se probó más expresividad (`clon` en guion.yaml: exaggeration 0.8, cfg 0.3) y respuestas más
  rápidas (pausa 0.18 s). Limitación real: el clon no actúa ni reacciona; la solución es grabarla de verdad.
- `preparar_voz.py` acepta la **conversación grabada junta en un solo audio** y corta cada línea a la carpeta de su persona.
  `render_conversacion.py --fuente grabada` probado de punta a punta (con audio de prueba, ya borrado). Guía §5.

### Pruebas ElevenLabs y voces grabadas (2026-11-06)
- Kate (ElevenLabs, guion completo): `render_reel_voz.py --audio RUTA --nombre kate` → `data/voz/prueba-elevenlabs/reel-kate.mp4`.
- `jose_elevenlabs.mp3` e `irvin_elevenlabs.mp3` NO dicen el guion (textos de muestra); solo sirvieron de referencia al clon local (`render_conversacion.py --ref-archivo _elevenlabs.mp3`).
- Voces grabadas: `--grabada PERSONA` y `--dos-voces irvin,jose,jose,irvin,jose` (frases reales intercaladas) en `data/voz/prueba-voces-grabadas/`.
- Diálogo real aún no grabado. Si ElevenLabs genera las líneas de cada uno, `preparar_voz.py` las reconoce y corta igual.

### Plan pago de ElevenLabs y reels 8-bit (2026-11-07)
- El usuario **pagó un plan de ElevenLabs**: excepción a "solo gratis". Falta confirmar en su cuenta que incluye licencia comercial.
- `assets/voice/jose/Jose_Eleven.mp3` (voz de José, guion del reel B). Reel: `render_reel_voz.py --audio RUTA --tal-cual --musica digital-lemonade --musica-db -17`
  → `data/voz/reel-jose-elevenlabs-tal-cual.mp4` (18,2 s). Audio intacto, solo música; sin pulido, pausas ni SFX. Pendiente de aprobación.
- Whisper oyó "para **el** grandes" en ese audio: el usuario debe confirmarlo escuchando (~2 s).
- Pidió más reels en **Motion Graphics 8-bit**, **a una sola voz, no conversacionales**. Por ahora solo guiones: `docs/guiones-8bit.md` (3 reels). Espera sus audios.
- Al producirlos: no agregar esos guiones a `prototypes/**/guion.yaml` sin antes separar los `lineaNN.limpio.wav` por reel; hoy `preparar_voz.py` los escribiría en la misma carpeta y se pisarían.

### Reels 8-bit generados (2026-11-07)
- Al equipo le gustaron los guiones 1 y 3 y descartó el 2. Audios en `assets/voice/elevenlabs/reel_1.mp3` y `reel_3.mp3`.
- `tools/render_8bit.py examples/copy/8bit/reel-N.yaml` → `data/reels-8bit/reel-N/reel.mp4` + `caption.txt`. Motor en `templates/video/8bit/reel.html`
  (canvas 180×320 x6, sprites propios, Press Start 2P leída por cuadrícula para que no se deforme; tildes dibujadas aparte porque sus mayúsculas acentuadas son minúsculas).
- Música y SFX propios: `tools/make_chiptune.py` (`chiptune-bodega`, `assets/sfx/8bit/`), sin crédito. Música -13 dB por defecto.
- Reel 1 (23,6 s) y reel 3 (25,2 s) enviados, **pendientes de aprobación**. Revisar: "Cámbialo" del reel 3, que se oía con posible acento de tuteo.
- Guiones nuevos 4-7 en `docs/guiones-8bit.md`, pendientes de que elijan y carguen audios. Cada guion nuevo necesita sus escenas en el motor.

### Videos publicados (2026-11-07)
- `VideosInstagram/`: videos que el equipo seleccionó y subió a Instagram (`Reel1.mp4`, `Reel1-whatsapp.mp4`, `Reel2.mp4`). Se versionan a pedido del usuario.

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
