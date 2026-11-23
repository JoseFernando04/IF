# Plan de contenido diario · IF Techworks

**Meta:** publicar al menos **2 piezas por día** en Instagram y TikTok (2 reels, 2 posts o 1 y 1).
Cada día Claude propone **3 opciones de reel y 3 de post**; el equipo elige.

## Rutina (lunes a viernes, por la mañana)

| Hora (GT) | Quién | Qué pasa |
|---|---|---|
| **7:30** | José | Enciende la PC, abre la app de Ollama y una **conversación nueva** en esta carpeta. Escribe: **"Listo, empecemos el día"**. |
| 7:30-8:15 | Claude | Prepara 3 opciones de reel (concepto, guion y una imagen de muestra del estilo) y 3 posts terminados. |
| 8:15-8:30 | José | Elige. Genera en ElevenLabs las voces de los reels elegidos y las deja en `assets/voice/elevenlabs/`. |
| 8:30-9:30 | Claude | Produce los reels finales, sus captions y hashtags. Ajusta lo que pidan. |
| 9:30-10:00 | José | Revisa, aprueba y **programa** la publicación (ver abajo). |

**La PC queda encendida de 7:30 a 10:00.** Un formato nuevo (que el motor aún no sabe animar) puede tomar
30-60 minutos extra la primera vez; las veces siguientes ya sale rápido.

**Recomendado:** producir hoy lo que se publica **mañana**. Así siempre hay un día de margen si algo falla.

## Publicación (gratis, sin esperar la Fase 3)

- **Instagram:** Meta Business Suite → *Crear publicación/reel* → **Programar**.
- **TikTok:** desde la computadora (tiktok.com/upload) → **Programar** (hasta 10 días antes).
- Horarios iniciales a probar (hora de Guatemala): **12:00-13:00** y **18:30-20:00**. Se ajustan con las métricas.

## Control de lo publicado

Lo más fácil: marcarlo en el **tablero** (https://claude.ai/artifact/Lhzfzm9U8GHYvEC1kt9Rim); Claude lo lee cada mañana.
También se puede decirle a Claude qué fue (por ejemplo: *"ayer subí el reel A y el post 2 del 10, solo en Instagram"*).
Claude lo marca con `tools/publicaciones.py` y queda en [publicaciones.md](publicaciones.md): ✅ publicado · ⏳ pendiente · ✖️ descartado.
Cada mañana Claude muestra lo que sigue pendiente de días anteriores.

## Entrega de voces

- Nombre del archivo: `AAAA-MM-DD-reel-A.mp3` (o `-B`, `-C`) en `assets/voice/elevenlabs/`.
- Un audio por reel, con el guion completo y en orden. Revisar el voseo antes de descargar.

## Carpetas

```
data/dias/AAAA-MM-DD/
  reel-A/  reel-B/  reel-C/     → reel.mp4, caption.txt, preview.png
  post-1/  post-2/  post-3/     → slides o imagen, caption.txt
VideosInstagram/                → lo que ya se publicó
```

## Formatos (rotar: ningún formato dos días seguidos)

### Reels

| Formato | Estado | Idea |
|---|---|---|
| Documental (estilo B) | ✅ listo | Foto real duotono, tipografía grande, voz de José |
| Videojuego 8-bit | ✅ listo | Misiones, game over, niveles (`docs/guiones-8bit.md`) |
| Historia en el celular | ✅ listo (`chat`) | Chat y notificaciones que cuentan una situación de bodega |
| Mito vs. realidad | ✅ listo (`mito`, look risográfico) | Pantalla dividida que se voltea |
| Antes / después | ✅ listo (`antesdespues`) | Deslizador entre el caos y el orden |
| Tipografía cinética | ✅ listo (`cinetica`) | Palabras grandes al ritmo de la voz |
| POV del dueño | ✅ listo (`pov`) | "POV: es cierre de mes y…" con texto en pantalla |
| Cuenta regresiva / top 3 | ✅ listo (`top3`, estilo suizo) | Lista rápida con números grandes |
| Pantalla de sistema | ✅ listo (`sistema`) | Tablero tipo software: reloj, escaneo y tarjetas de alerta que se apilan |
| **Cine (video con IA)** | ✅ listo (`cine`: `tools/generar_clip.py` + `tools/render_formato.py`, `--borrador` = video sin voz) | Tomas reales generadas con Higgsfield + voz del equipo + una sola acción por WhatsApp. Ver "Enfoque cine" abajo |
| Decilo así | ✅ listo (`decilo`, desde 2026-11-12) | La frase exacta para una situación incómoda, escrita en una tarjeta con botón «copiá y pegá». Serie por tema (cobros, cotizaciones, atrasos) |
| Tráiler de película | ✅ listo (`trailer`, desde 2026-11-12) | Barras de cine, rótulos en serif, fotos duotono y el título de la «película» (un dolor real). Voz grave |
| Texto diminuto en loop | ✅ listo (`diminuto`, desde 2026-11-12) | 5-6 s: frase grande en voz + remate en letra minúscula que obliga a pausar. El detalle va en la descripción |
| Cargando… | ✅ listo (`cargando`, desde 2026-11-15) | El negocio trabado en una barra de carga sobre el caos; golpe y corte seco al resultado listo |
| Lo que pediste vs. lo que te entregaron | ✅ listo (`pediste`, desde 2026-11-15) | Expectativa (pedido sencillo) → giro (14 pantallas, manual, contraseña) → cómo lo hace IF |
| Flechas rojas | ✅ listo (`flechas`, desde 2026-11-16) | Pantallas de una app recreadas (sin logo) con flechas y círculos rojos a mano sobre el botón poco conocido; paso a paso para guardar. Verificar cada paso en la app real antes de grabar |
| Respondiendo a… | ✅ listo (`respuesta`, desde 2026-11-16) | Una pregunta frecuente en burbuja de comentario (sin usuario inventado) y la respuesta en tarjetas numeradas. Sin cifras |
| Nombrá el problema | ✅ listo (`concepto`, desde 2026-11-17) | Archivos que se multiplican → «diagnóstico» con un nombre memorable para el dolor → 3 síntomas → la cura → cierre. Serie numerada |
| Dosis de realidad | ✅ listo (`realidad`, desde 2026-11-17) | Clip vertical que graba el equipo (pantallas reales, sin datos de clientes) + notas adhesivas con palabras clave. Clip en `<salida>/clips/<id>.mp4` |
| Lista sin intro | ✅ listo (`lista`, desde 2026-11-18) | El #1 aparece en el segundo 0, sin presentación; una imagen de referencia por punto |
| A mano vs. agente | ✅ listo (`versus`, desde 2026-11-18) | Pantalla dividida: misma situación en dos versiones y giro final donde la persona gana |
| Te lo explico en una servilleta | ✅ listo (`servilleta`, desde 2026-11-19) | Un concepto dibujado a mano, trazo por trazo, sobre una servilleta (letra Caveat, marcador que sigue el trazo). Serie numerada. Reemplaza al prototipo «papel y libreta» |
| Habla el objeto | ✅ listo (`objeto`, desde 2026-11-19) | Un objeto del negocio con cara confiesa sus defectos en primera persona. Hoy existe la página web (estados: url, anuncios, buscador, cursor, whatsapp, pulido, cara); otros objetos (cuaderno, Excel) se agregan a la plantilla |
| Encontrá los 3 errores | ✅ listo (`errores`, desde 2026-11-20) | Juego: una pantalla de ejemplo (perfil de negocio genérico, sin logos) con 3 fallas; cuenta regresiva de 5 s, cada error se encierra en rojo y al final se ve arreglado en verde. Invita a comentar cuántos encontraste |
| Un día en la vida | ✅ listo (`undia`, desde 2026-11-20) | Estética de vlog (REC, hora grande, subtítulo en caja, emoji del momento): el día real de alguien del negocio; a mitad se «rebobina» y se ve el mismo día con la solución (acento dorado) |
| Tier list | ✅ listo (`tierlist`, desde 2026-11-22) | Clasificación S-A-B-C-D de cómo los negocios hacen algo (inventario, cobros, pedidos); la S siempre es la solución. Invita a comentar la letra |
| Tu negocio en resumen | ✅ listo (`resumen`, desde 2026-11-22) | Tarjetas de «resumen del año» con barra de historias (frase más dicha, hora favorita…), estética propia IF. Temporada: diciembre. Sin cifras inventadas |

### Posts

| Formato | Estado | Idea |
|---|---|---|
| Carrusel documental | ✅ listo (12 layouts) | Señales, comparaciones, pasos |
| Mito o verdad | por construir | Afirmación + respuesta al deslizar |
| Checklist para guardar | ✅ listo (`checklist`) | Lista útil que invita a guardar |
| Este o este | ✅ listo (`este-o-este`) | Dos opciones para comentar |
| Frase de dueño | ✅ listo (`frase`) |
| Diccionario | ✅ listo (`diccionario`) | Palabras que todo dueño conoce, con definición y "cura" |
| Recibo | ✅ listo (`recibo`) | Ticket con lo que cuesta un problema (sin cifras inventadas) | Una situación que todos reconocen |
| Infografía simple | ✅ listo (`infografia`) | Un dato del proceso explicado en una imagen |
| Carrusel 8-bit | por construir | Mismo universo de los reels de videojuego |

## Enfoque cine: de vistas a clientes (desde 2026-11-10)

Los formatos animados (8-bit, chat, mito…) sirven para **alcance**. El formato `cine` sirve para **convertir**:
se ve como un negocio real, habla de un solo dolor y pide una sola acción.

**Estructura fija (20-30 s, una sola voz del equipo):**

| Parte | Tiempo | Qué hace | Imagen |
|---|---|---|---|
| Gancho | 0-3 s | Nombra el dolor con una hora o situación concreta ("Son las seis de la tarde y…") | Toma IA: el dueño de espaldas, en su negocio |
| Causa | 3-10 s | Le quita la culpa a la gente y la pone en el proceso | Toma IA: detalle (cuaderno, papeles, manos) |
| Solución | 10-18 s | Qué hace IF, en una frase y sin tecnicismos | Toma IA: celular o pantalla desenfocada en el mismo lugar |
| Alivio | 18-23 s | Cómo se siente el negocio ordenado | Toma IA: el mismo lugar, en calma |
| Acción | últimos 4-5 s | **Una palabra clave por WhatsApp** ("Escribinos BODEGA") | Tarjeta de marca, sin IA |

**Reglas del formato:**

- **Una palabra clave distinta por reel** (BODEGA, COTIZAR, RUTA…). Quien escribe esa palabra dice de qué reel vino:
  así se mide cuál convierte, sin esperar la Fase 4. Anotar los mensajes recibidos por palabra.
- La acción es **una sola** y se repite igual en la voz, en pantalla y en la descripción. Nada de "seguinos y comentá y…".
- Un reel = un dolor = un tipo de negocio. Rotar: bodega, ferretería, distribuidora, taller, oficina.
- Voz del equipo tal cual (ElevenLabs). Las tomas se generan **sin audio**; música `if-firma` baja y efectos mínimos.
- Solo palabras clave en pantalla (2-3 palabras por línea), sin subtítulos.
- Tomas: 4 por reel, 5-6 s, 720p vertical. Personas solo de espaldas, en silueta o manos: nunca una cara que parezca
  un cliente o un testimonio. Sin texto ni logos dentro de la toma. La descripción dice "Escena de ejemplo, imágenes generadas con IA".
- Mismo look en todas las tomas (luz dorada, sombras verde bosque): sale de `config/settings.yaml > higgsfield.estilo`.
- Sigue aplicando: sin clientes, cifras ni testimonios inventados; nada se publica sin aprobación.

**Orden obligatorio (para no gastar a ciegas):** 1) concepto, gancho y guion medidos a la duración de las tomas (≈ 2,7 palabras por segundo:
una toma de 5 s = 12-14 palabras) → 2) el equipo aprueba el guion → 3) recién entonces `tools/generar_clip.py <yaml> --confirmar` →
4) `tools/render_formato.py <yaml> --borrador` (video completo sin voz) → 5) el equipo graba la voz → 6) `tools/render_formato.py <yaml>`.
**Nunca generar tomas sin guion aprobado.** Ejemplo: `examples/copy/cine/asi-se-siente-bodega.yaml` (serie «Así se siente / Así es»).
En la rutina diaria: de las 3 opciones de reel, **una** puede ser `cine`; las tomas solo se generan si esa opción es la elegida.

## Historial (para no repetir)

| Día | Reels propuestos | Posts propuestos |
|---|---|---|
| 2026-11-08 | A chat (inventario) ✅ producido · B mito vs. realidad (digitalizar) ✅ producido · C top 3 (vendedores de calle) ✅ producido | 1 checklist (comprar sistema) · 2 este o este (cotizaciones) · 3 frase de dueño (memoria) |
| 2026-11-09 | A POV del dueño (catálogo) ✅ producido · B antes/después (activos) ✅ producido · C tipografía cinética (así trabajamos; reemplaza la versión de charlas) ✅ producido | 1 infografía (estante con sensores) · 2 diccionario del dueño · 3 recibo (costo de no ordenar) |
| 2026-11-10 | A 8-bit "jefe final: el cierre de mes" ✅ producido · B mito vs. realidad (la nube) ✅ producido · C pantalla de sistema (lunes 7:00, formato nuevo) ✅ producido | 1 checklist (5 cosas que debería avisarte solo) · 2 este o este (cierre de mes) · 3 frase de dueño (doña Marta) |
| 2026-11-11 | A chat (pedido perdido en un audio) ✅ producido · B top 3 (tareas a mano) ✅ producido · C POV (el que sabe todo se fue de vacaciones) ✅ producido | 1 infografía (taller: orden de trabajo) · 2 diccionario vol. 2 (oficina) · 3 recibo (cobrar tarde) |
| 2026-11-12 | A decilo así (cobros: «ya te deposito») ✅ producido · B tráiler (el conteo de inventario) ✅ producido · C texto diminuto (no necesita más horas) ✅ producido — los tres formatos nuevos | 1 carrusel documental (el impuesto del desorden) · 2 checklist (cerrar el año) · 3 frase (antes de venderme, escuchame) |
| 2026-11-15 | A cargando… (cotización que llega tarde, formato nuevo) · B lo que pediste vs. lo que te entregaron (formato nuevo) · C pantalla de sistema (viernes 5:30: equipos, cobros, entregas) | 1 este o este (cuánto vendiste hoy) · 2 infografía (herramientas con QR) · 3 recibo (tu diciembre) |
| 2026-11-16 | A flechas rojas (respuestas rápidas de WhatsApp Business, formato nuevo) ✅ producido · B respondiendo a… (¿cuánto cuesta un sistema?, formato nuevo) ✅ producido · C top 3 (señales de que todavía NO necesitás un sistema) ✅ producido | 1 checklist (5 preguntas antes de pagar por un sistema) · 2 frase (yo sé dónde está todo) · 3 diccionario vol. 3 (bodega y mostrador) |
| 2026-11-17 | A nombrá el problema (el síndrome del archivo final, formato nuevo) · B dosis de realidad (nuestro propio tablero, formato nuevo; José graba el clip) · C decilo así ep. 02 («¿me lo dejás más barato?») | 1 este o este (lista de precios) · 2 infografía (distribuidora: del mensaje a la entrega) · 3 recibo (primera semana del nuevo) |
| 2026-11-18 | A chat (la cotización que se enfrió: seguimiento día 2·5·10) ✅ producido · B lista sin intro (lo que tu cliente revisa antes de escribirte, formato nuevo) ✅ producido · C a mano vs. agente (la máquina contesta, la persona vende, formato nuevo) ✅ producido — primer día con los servicios nuevos del sitio | 1 checklist (5 cosas que tu página web tiene que tener) · 2 frase (nadie volvió a escribir) · 3 diccionario vol. 4 (edición WhatsApp) |
| 2026-11-19 | A te lo explico en una servilleta (cómo funciona un sistema de inventario, formato nuevo) ✅ producido · B habla el objeto (confesiones de una página web gratis, formato nuevo) ✅ producido · C mito vs. realidad (dos mitos de cobrar por WhatsApp) ✅ producido | 1 recibo (conteo de fin de año) · 2 este o este (fotos o catálogo) · 3 infografía (reseñas en Google) — primer día en carrusel de 5 slides |
| 2026-11-20 | A encontrá los 3 errores (perfil de negocio sin vida → contenido para redes, formato nuevo) · B un día en la vida (vendedor de ruta → app para vendedores de calle, formato nuevo) · C nombrá el problema ep. 02 (el teléfono descompuesto → sistema de ventas e inventario) | 1 checklist (4 cosas para tu WhatsApp antes de diciembre) · 2 frase («sí hay, déjeme ver…», carrusel de 4) · 3 diccionario vol. 5 (edición diciembre) |
| 2026-11-22 | A tier list (dónde vive el inventario de tu negocio → sistema de inventario, formato nuevo) ✅ producido · B tu negocio en resumen 2026 (resumen del año → automatizaciones por WhatsApp, formato nuevo) ✅ producido · C decilo así ep. 03 («lo voy a pensar» → seguimiento de cotizaciones) ✅ producido | 1 carrusel documental (3 señales de que tu página web te cuesta clientes) · 2 infografía (agente de IA en WhatsApp, 3 pasos) · 3 recibo (oferta de fin de mes sin inventario al día) — se probaron 8-9 slides y se volvió a 5 |

## Prueba en paralelo: voz local con VoiceStudio (desde 2026-11-19, una semana)

Objetivo: ver si la voz local puede reemplazar a ElevenLabs. **No cancelar ElevenLabs hasta terminar la prueba.**

- Cada día: de los reels elegidos, **el más corto** se genera con VoiceStudio (Claude lo hace directo desde el guion);
  los demás guiones se le pasan a José para ElevenLabs, como siempre. El equipo compara y anota cuál suena mejor.
- VoiceStudio debe estar abierto **desde el menú Inicio** (API en `http://127.0.0.1:3900`; comprobar `/health`).
- Generar con `POST /generate` (multipart): `engine=voxcpm2`, `language=es`, `seed=7`, `ref_audio` + `ref_text`
  (transcripciones en `data/pruebas-voz/ref-textos.json`) e `instruct` de estilo:
  «Tono conversacional y expresivo, como contando una historia en redes sociales: sube en las preguntas, hace pausas con
  intención y enfatiza las palabras clave.» Opcional `guidance_scale=3.0`. **Sin puntuación dramática** (la v4 se descartó).
- Referencias actuales: `data/pruebas-voz/ref-irvin-eleven.wav` (8 s, la que más gustó) y `ref-jose-eleven.wav` (29 s).
  Salen de audios de ElevenLabs: **no publicar** con ellas hasta revisar los términos de ElevenLabs; lo ideal es que
  José e Irvin graben referencias propias de 20-30 s hablando como en un reel (`docs/guia-grabar-voces.md`).
- Guardar el audio como `assets/voice/elevenlabs/AAAA-MM-DD-reel-X.mp3` (mismo flujo de montaje) y además una copia
  `data/pruebas-voz/AAAA-MM-DD-reel-X-local.wav`. Revisar con Whisper que diga el guion completo.
- Problemas conocidos: pierde el acento del voseo («contestas» por «contestás»): probar escribirlo distinto y avisar
  si no se corrige. Tarda ~3-5 min por reel (la VRAM queda al límite).
- Registro: anotar cada día la elección del equipo en la tabla de abajo.

| Día | Reel local | Resultado |
|---|---|---|
| 2026-11-19 | — | Sin voz local: el equipo grabó las 3 voces en ElevenLabs |
| 2026-11-20 | **Los 3** (pedido de José): A y C con Irvin, B con José | ~1.5-2.5 min por reel; Whisper 98-100 %. Posibles fallas: «¿qué haces?» en A (voseo), «escribímos» en B. **Al equipo no le gustó ninguna: se rehicieron con ElevenLabs** |

## Reglas de contenido (siempre)

- **Palabras que la gente busca (OpenSEO, desde 2026-11-19):** usar en temas, descripciones y hashtags lo que se busca en
  Guatemala (detalle en `pruebas-herramientas/openseo/NOTAS.md`). **El foco sigue siendo dar a conocer los servicios de IF**
  como hasta ahora; **solo algunos días** (no todos) una pieza sobre **«WhatsApp Business»** (14 800/mes) que termine en las
  automatizaciones. Para lo demás, usar las palabras buscadas: «sistema de inventario» / «sistema de ventas e inventario», «bot de WhatsApp»,
  «página web para mi negocio» (ángulo gratis vs. profesional). Decir «sistema de inventario» antes que «software a la medida».
- **No hacer tutoriales paso a paso de configuración de apps** (como el de respuestas automáticas de WhatsApp Business del
  2026-11-16): el usuario no encontró esa opción en la app. WhatsApp Business se trata con ideas, errores comunes y
  comparaciones, no con «tocá aquí, luego aquí».

- **Guiones de voz sin siglas** (desde 2026-11-15): ElevenLabs lee «IF» como «ai-ef» y «POV» letra por letra. En la voz decir «nosotros» o rehacer la frase; la sigla solo va en pantalla.
- Voseo guatemalteco. Sin clientes, cifras ni testimonios inventados (las escenas son "de ejemplo").
- Llamado a la acción con WhatsApp **+502 3808 9808**. Descripciones llamativas que **no repitan el guion**.
- 5 hashtags. Si la música es CC BY, el crédito va en la descripción.
- **Posts en carrusel de 4-5 slides** (desde 2026-11-19, pedido del equipo: los de una sola imagen «no pegan»; el 2026-11-22 se probaron 8-9 y fue demasiado). Portada con gancho → 2-3 de desarrollo → cierre con WhatsApp.
  En `render_post.py`: recibo y este-o-este aceptan `slides:` (cada una con `titulo`, `texto`, `puntos`, `marca: ✓|✗`, `claro`, `tira: {q, t}`) + `cierre`/`cierre_bajada`;
  la infografía con `carrusel: true` + `bajada` va un paso por slide. Ejemplos: `examples/copy/dia/2026-11-19-post-*.yaml`.
- Posts: además, un título para TikTok (`titulo_tiktok` en el YAML, máx. 90 caracteres, llamativo y distinto a la descripción).
- Sonido: los posts se publican con el sonido característico de IF (`if-firma`); ver `data/dias/2026-11-09/para-subir/sonido-IF/`.
- Rotar pilares: educativo, soluciones, tips, propósito y proceso, llamado a la acción.
