# Campañas para clientes (marketing digital)

Guía de trabajo para las campañas que IF Techworks hace para **clientes de marketing digital** que todavía atiende.
Es un trabajo **aparte** del contenido propio de IF: otra marca, otro tono, otra carpeta, otro control.

> El contenido de IF (reels, posts, descripciones) **nunca** menciona el marketing digital.
> Y nada de IF (colores, logo, sonido, WhatsApp, hashtags) aparece en las piezas de un cliente.

---

## 1. Reglas

1. **Separación total de IF.** Todo vive en `campanas/<cliente>/`. No se toca `data/dias/`, `docs/publicaciones.yaml`,
   `docs/plan-contenido-diario.md` ni el tablero de publicaciones de IF.
2. **La marca es la del cliente.** Colores, logo, fuentes, tono y contacto salen de `campanas/<cliente>/marca.yaml`,
   nunca de `config/brand.json`. No usar `if-firma`, `assets/sfx/if-logo.wav` ni el logo de IF.
3. **No inventar.** Nada de clientes, cifras, precios, reseñas ni testimonios que el cliente no haya dado por escrito.
   Si falta un dato, se marca «pendiente» y se pregunta.
4. **Doble aprobación.** Primero aprueba el equipo de IF (plan y piezas); después aprueba el cliente. Nada se publica sin las dos.
5. **Licencias.** Música solo de `assets/music/library.yaml` con licencia comercial (crédito CC BY en el caption);
   fuentes libres (OFL / Apache). Fotos o videos de stock: revisar la licencia y anotarla en `material/LICENCIAS.md`.
   Material que manda el cliente: él garantiza los derechos; se anota de dónde vino.
6. **Datos personales.** Fotos de personas, voces y material del cliente quedan fuera de git (ver `.gitignore`).
7. **Gastos.** Voz en ElevenLabs, tomas con IA (Higgsfield) o pauta pagada: decir el precio y esperar el sí antes de gastar.
8. **Commit y push** solo cuando el usuario lo pide.

---

## 2. Estructura de cada campaña

```
campanas/
├── README.md              ← esta guía
├── _plantilla/            ← copiar para cada cliente nuevo
└── <cliente>/             ← nombre corto, sin tildes ni ñ (ej. panaderia-lupita)
    ├── brief.md           ← datos del cliente, objetivo, público, medios, fechas
    ├── marca.yaml         ← colores, fuentes, logo, contacto, tono, trato (voseo/tuteo/usted)
    ├── plan.md            ← concepto, mensajes, piezas, calendario, medición
    ├── entregas.md        ← qué se le mandó al cliente y qué respondió
    ├── material/          ← lo que manda el cliente (logo, fotos, videos)        · fuera de git
    │   └── voz/           ← audios de ElevenLabs para los reels                  · fuera de git
    ├── piezas/            ← un YAML por pieza (reel-01.yaml, post-01.yaml…)
    ├── plantillas/        ← copia de las plantillas HTML con la marca del cliente
    ├── salida/            ← renders (mp4, png, caption.txt)                      · fuera de git
    └── entregas/          ← paquetes listos para mandar (AAAA-MM-DD/)            · fuera de git
```

---

## 3. Paso a paso

### Paso 1 — Brief
1. `cp -r campanas/_plantilla campanas/<cliente>` y crear `material/`, `piezas/`, `plantillas/`, `salida/`, `entregas/`.
2. Llenar `brief.md` con lo que dé el equipo. Revisar el sitio o las redes del cliente si las hay (solo para conocerlo;
   no copiar textos ni imágenes sin permiso).
3. Llenar `marca.yaml`. Si el cliente no tiene manual de marca, sacar los colores de su logo y proponer fuentes libres parecidas.

### Paso 2 — Plan (lo aprueba el equipo)
Llenar `plan.md`:
- **Concepto:** una idea que una toda la campaña.
- **Mensajes:** 3-5, cada uno contra una objeción o un deseo real del público.
- **Piezas:** mezcla por red (ver tabla de abajo).
- **Calendario:** fechas y horas sugeridas por red.
- **Medición:** qué contar (mensajes de WhatsApp, ventas, alcance) y cuándo reportar.

No se produce nada hasta que el plan esté aprobado (anotar quién y cuándo arriba del `plan.md`).

### Paso 3 — Guiones y textos
- Un YAML por pieza en `piezas/`. Mismo formato que los de `examples/copy/dia/`, pero con
  `salida: campanas/<cliente>/salida/<pieza>` y el contacto y los hashtags **del cliente**.
- Reels: guion a una sola voz. Si se usa ElevenLabs, el audio va a `material/voz/<pieza>.mp3`.
  Evitar siglas en la voz (ElevenLabs las deletrea).
- Captions: llamativos, sin repetir el guion, con el contacto del cliente y 5 hashtags. Para TikTok, `titulo_tiktok` (máx. 90 caracteres).
- `copy/lint.py` revisa voseo y tildes: si el cliente usa tuteo o usted, ignorar los avisos de tuteo.

### Paso 4 — Producción
1. Copiar la plantilla que se va a usar a `plantillas/` y cambiar ahí colores (`:root`), fuentes y logo por los del cliente.
   **No editar las plantillas de IF en `templates/`.**
2. Muestras primero (`--muestra` en reels) y revisarlas con el equipo; después el render completo.
3. Revisar cuadros reales del video y escuchar el audio antes de dar la pieza por buena.

### Paso 5 — Entrega al cliente
1. Juntar en `entregas/AAAA-MM-DD/`: los videos e imágenes finales, un `captions.md` con el texto de cada pieza
   (caption, hashtags, título de TikTok) y el calendario sugerido.
2. El equipo lo manda al cliente (correo o WhatsApp). Anotar el envío en `entregas.md`.
3. Cambios que pida el cliente → nueva versión de la pieza (`-v2`) y nueva fila en `entregas.md`.

### Paso 6 — Publicación y seguimiento
- Publica quien se acuerde con el cliente (él mismo o el equipo desde Meta Business Suite / TikTok con acceso del cliente).
  Nunca pedir ni guardar contraseñas del cliente: acceso por roles de Meta Business o invitación.
- Marcar el estado de cada pieza en la tabla de `plan.md` (`publicado`, fecha y redes).
- Al cerrar la campaña: resumen de resultados con números reales que dé el cliente o las estadísticas de las redes.

---

## 4. Piezas por red

| Red | Formatos | Medidas | Notas |
|---|---|---|---|
| Instagram | Reel, post, carrusel, historia | 1080×1920 (9:16) · 1080×1350 (4:5) | Reels y carruseles para alcance; historias para ventas directas |
| TikTok | Video | 1080×1920 | Gancho en el primer segundo; textos dentro de la zona segura |
| Facebook | Reel, post, historia | Mismas que Instagram | Se puede publicar junto con Instagram desde Meta Business Suite |
| WhatsApp | Estado, catálogo, mensaje | 1080×1920 para estados | Piezas cortas con precio, promoción y llamada a escribir |
| Pauta (Meta Ads) | Variantes del mismo anuncio | 9:16, 4:5 y 1:1 | 2-3 textos y 2-3 visuales para probar; presupuesto lo define el cliente |

---

## 5. Herramientas del repo que se reutilizan

| Para | Herramienta | Qué cambiar para un cliente |
|---|---|---|
| Reels por formato (chat, mito, top3, pov, antesdespues, cinetica, trailer, etc.) | `tools/render_formato.py <yaml>` (`--muestra`, `--borrador`) | Plantilla de `templates/video/<formato>/reel.html` copiada a `plantillas/` con la marca del cliente |
| Posts y carruseles (checklist, este-o-este, frase, infografía, diccionario, recibo) | `tools/render_post.py <yaml>` | Plantilla `templates/graphics/posts/post.html` copiada con colores y logo del cliente |
| Fondos animados | `templates/shared/fondos.js` (Paper Shaders) | Pasar los colores del cliente |
| Revisar un audio | `ifcontent.audio.transcribe.transcribir([ruta])` | — |
| Música | `assets/music/library.yaml` | No usar `if-firma` ni `chiptune-bodega` (son sonido de IF) |
| Tomas con IA | `tools/generar_clip.py <yaml>` (Higgsfield, **de pago**) | Mostrar plan y precio; generar solo lo aprobado |

**Marca del cliente en los renders (listo desde 2026-11-17):** `render_formato.py` y `render_post.py` aceptan en el YAML
de la pieza las claves `plantilla`, `logo`, `logo_oscuro`, `fuentes`, `fondo_muestra` y (solo reels) `musica_archivo`,
todas con rutas desde la raíz del repo. Sin esas claves, todo sigue igual para IF. Ejemplo completo: `campanas/flor-de-loto-spa/piezas/`.
Música propia por cliente: un script como `campanas/flor-de-loto-spa/herramientas/make_musica.py` (sin el sonido de IF).

---

## 6. Antes de mandar cualquier pieza (lista de control)

- [ ] Colores, logo y fuentes del cliente; nada de IF a la vista ni en el audio.
- [ ] Contacto y hashtags del cliente.
- [ ] Ningún dato inventado (precios, cifras, reseñas).
- [ ] Ortografía y trato correctos (voseo, tuteo o usted, según el cliente).
- [ ] Música con licencia y crédito si hace falta.
- [ ] Revisado en cuadros reales (video) o a tamaño completo (imagen).
- [ ] Aprobado por el equipo; anotado en `entregas.md` al mandarlo.

---

## 7. Campañas

| Cliente | Carpeta | Estado | Inicio |
|---|---|---|---|
| Flor de Loto Spa (Cobán) | `campanas/flor-de-loto-spa/` | 3 reels y 3 posts listos; paquete `entregas/2026-11-17/` por enviar (2026-11-17) | pendiente |
