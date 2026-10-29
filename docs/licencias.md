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
