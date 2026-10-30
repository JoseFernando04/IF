# Licencias de componentes

Todo el stack es gratuito para uso comercial. Revisar esta tabla antes de agregar cualquier librería o modelo nuevo.

| Componente | Uso | Licencia | Costo | Nota |
|---|---|---|---|---|
| Python, Jinja2, PyYAML, Pydantic, Typer, httpx, python-dotenv | Base | PSF / BSD / MIT | 0 | |
| Playwright + Chromium | Render de gráficos y cuadros de video | Apache 2.0 / BSD | 0 | |
| FFmpeg (build Gyan, winget) | Codificación de video y audio | GPL v3 | 0 | Uso interno; no redistribuimos el binario |
| Pillow | Validación de imágenes | MIT-CMU | 0 | |
| Ollama | Servidor local de LLM | MIT | 0 | |
| Qwen3 8B | Generación de copy | Apache 2.0 | 0 | Corre local en la RTX 3050 |
| kokoro-onnx | Motor TTS | MIT | 0 | |
| Kokoro-82M (pesos y voces) | Voz en off | Apache 2.0 | 0 | |
| Space Grotesk, Inter, JetBrains Mono | Tipografías de marca | SIL OFL 1.1 | 0 | Licencias en `assets/fonts/` |
| Lucide (íconos) | Íconos de las plantillas | ISC | 0 | Licencia en `assets/icons/LICENSE.txt` |
| GSAP 3.15.0 (gsap, SplitText, CustomEase, DrawSVG) | Motion de reels | GSAP Standard No-Charge License | 0 | Uso comercial OK; prohibido solo en constructores visuales que compitan con Webflow. Vendorizado en `assets/vendor/` con hash verificado |
| Bricolage Grotesque, Instrument Serif, Inter Tight, Caveat | Tipografías de la nueva dirección | SIL OFL 1.1 | 0 | Licencias en `assets/fonts/` |
| Fotos de Unsplash | Fotografía real | Unsplash License | 0 | Registro en `assets/photos/CREDITOS.yaml` |
| SFX (`assets/sfx/`) | Efectos de sonido | Propios (sintetizados con `tools/make_sfx.py`) | 0 | Sin terceros |
| Azure AI Speech (F0) | Voz en la nube (en evaluación) | Términos de Azure: el audio generado se puede usar comercialmente | 0 hasta 500 000 car./mes | Requiere cuenta y clave (`docs/guia-voces.md`) |
| Google Cloud Text-to-Speech | Voz en la nube (en evaluación) | Términos de Google Cloud: uso comercial permitido | 0 hasta 1 M car./mes (Chirp 3 HD) | Requiere cuenta y clave |
| ElevenLabs (capa gratis) | — | Sin licencia comercial | **Descartado** | El plan Starter (~USD 5-6/mes) sí la incluye |
| Chatterbox Multilingual | Voz (en evaluación) | MIT | 0 | En `.venv-tts` |
| Piper + voces es_MX claude / ald | Voz (en evaluación) | GPL-3.0 (motor, uso interno) · Apache 2.0 / Unlicense (voces) | 0 | |
| cloudflared (Quick Tunnel) | URL pública temporal para Instagram (Fase 3) | Apache 2.0 | 0 | Sin cuenta |
| Remotion | — | Licencia de empresa paga (más de 3 empleados) | **Descartado** | Reemplazado por el motor `html_frames` |
| Coqui XTTS-v2 | — | CPML (no comercial) | **Descartado** | |
| YouTube Audio Library | — | Ligada a uso en YouTube | **Descartado** | |

## Música

Cada pista está en `assets/music/library.yaml` con su licencia, URL de la licencia, fuente y fecha de descarga.
Las pistas de Kevin MacLeod (incompetech.com) son **CC BY 4.0**: se pueden usar comercialmente siempre que se dé
crédito. El sistema agrega el crédito al caption automáticamente.

Para agregar pistas de Pixabay Music (licencia Pixabay, uso comercial sin atribución obligatoria): descargá el MP3
desde pixabay.com/music, guardalo en `assets/music/` y agregá su entrada en `library.yaml` con
`license: Pixabay-Content-License` y `license_url: https://pixabay.com/service/license-summary/`.
Guardá también una captura de la página de la pista como respaldo.
