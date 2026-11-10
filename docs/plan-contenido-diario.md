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
| Papel y libreta (estilo A) | prototipo | Papel, marcador y escritura a mano |

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

## Historial (para no repetir)

| Día | Reels propuestos | Posts propuestos |
|---|---|---|
| 2026-11-08 | A chat (inventario) ✅ producido · B mito vs. realidad (digitalizar) ✅ producido · C top 3 (vendedores de calle) ✅ producido | 1 checklist (comprar sistema) · 2 este o este (cotizaciones) · 3 frase de dueño (memoria) |
| 2026-11-09 | A POV del dueño (catálogo) ✅ producido · B antes/después (activos) ✅ producido · C tipografía cinética (así trabajamos; reemplaza la versión de charlas) ✅ producido | 1 infografía (estante con sensores) · 2 diccionario del dueño · 3 recibo (costo de no ordenar) |
| 2026-11-10 | A 8-bit "jefe final: el cierre de mes" ✅ producido · B mito vs. realidad (la nube) ✅ producido · C pantalla de sistema (lunes 7:00, formato nuevo) ✅ producido | 1 checklist (5 cosas que debería avisarte solo) · 2 este o este (cierre de mes) · 3 frase de dueño (doña Marta) |

## Reglas de contenido (siempre)

- Voseo guatemalteco. Sin clientes, cifras ni testimonios inventados (las escenas son "de ejemplo").
- Llamado a la acción con WhatsApp **+502 3808 9808**. Descripciones llamativas que **no repitan el guion**.
- 5 hashtags. Si la música es CC BY, el crédito va en la descripción.
- Posts: además, un título para TikTok (`titulo_tiktok` en el YAML, máx. 90 caracteres, llamativo y distinto a la descripción).
- Sonido: los posts se publican con el sonido característico de IF (`if-firma`); ver `data/dias/2026-11-09/para-subir/sonido-IF/`.
- Rotar pilares: educativo, soluciones, tips, propósito y proceso, llamado a la acción.
