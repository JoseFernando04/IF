# Guía: grabar voces reales (tuya y de amigos)

Dos formas de usar voces reales. Se pueden combinar.

| | **Voz grabada** | **Voz clonada** |
|---|---|---|
| Qué se graba | Las frases exactas de cada reel | Una sola vez, ~20-30 s de lectura |
| Cómo suena | 100 % humana (es la persona) | Muy parecida a la persona, generada por IA local (Chatterbox) |
| Para qué sirve | Reels importantes | Volumen: guiones nuevos sin volver a grabar |
| Costo | 0 | 0 (corre en esta PC) |

## 1 · Permiso de cada persona (obligatorio)

Antes de usar la voz de alguien en contenido de IF Techworks, esa persona tiene que aceptar por escrito
(un mensaje de WhatsApp o correo alcanza) algo como:

> "Autorizo a IF Techworks a usar grabaciones de mi voz, y una voz generada a partir de ellas, en contenido
> publicitario de sus redes sociales. Puedo retirar este permiso cuando quiera, y desde ese momento no se
> generan piezas nuevas con mi voz."

Guardá una captura en `assets/voice/<nombre>/permiso.png` (o .jpg/.pdf). **Sin permiso, la herramienta no usa esa voz.**

Las grabaciones de voz son datos personales: la carpeta `assets/voice/` **no se sube a GitHub**.

## 2 · Cómo grabar (con el celular) — lo que más importa para que suene nítido

El clon copia la voz **junto con el cuarto y el micrófono**: si la grabación tiene eco o ruido, el clon sale con eco
o ruido (y lo exagera). Estas reglas evitan eso:

1. **NO usar notas de voz de WhatsApp.** WhatsApp comprime el audio y recorta los agudos: suena "de teléfono".
   Usá la app de grabadora del celular (iPhone: *Notas de voz*; Android: *Grabadora*). Para mandar el archivo,
   adjuntalo **como documento** (no como nota de voz), o pasalo por Drive o cable.
2. **El lugar es la clave. Lo mejor: un carro estacionado** con las ventanas cerradas (es chico y acolchado, casi
   sin eco). Segunda opción: un clóset con ropa, o un cuarto con cama, cortinas y alfombra. **Evitá** cocina, baño,
   salas vacías, oficinas con vidrio o piso cerámico.
3. **Apagá ventiladores, aire acondicionado y refrigeradoras cercanas.** Poné el celular en modo avión (sin vibraciones).
4. **Celular apoyado** (en una mesa o en el tablero, no en la mano), a **15-20 cm** de la boca y un poco de lado,
   para que las "p" y "b" no golpeen el micrófono.
5. **Al empezar, dejá 3 segundos en silencio** (sirve para medir el ruido del lugar). Después hablá.
6. Hablá con energía de conversación, como si le contaras algo a un amigo frente a vos. No leas "de corrido":
   si te trabás, hacé una pausa y repetí la oración completa (después se recorta).

## 3 · Qué grabar

### A · Para la voz clonada: `referencia` (45-60 s, un solo archivo)

Este texto tiene preguntas, sorpresa, risa, números y oraciones largas y cortas: así el clon aprende cómo suena
tu voz en distintos tonos. La herramienta elige sola los ~10 segundos más limpios y expresivos.

> *(3 segundos de silencio)*
> ¡Hola! ¿Cómo estás? Qué gusto saludarte.
> Mirá, te cuento algo que nos pasa a todos: contás la bodega el lunes, te da ciento cuarenta;
> la volvés a contar el martes… ¡y te da ciento cincuenta y dos! ¿Cómo puede ser? *(reíte si te sale)*
> Por eso trabajamos así: primero platicamos de tu negocio. Qué vendés, cómo llevás el inventario
> y qué es lo que más tiempo te quita.
> Después te mostramos, con ejemplos de verdad, cómo se vería todo ordenado. Sin tecnicismos.
> ¿Y lo mejor? El diagnóstico es sin compromiso.
> Entonces… ¿te parece si lo vemos esta semana? ¡Dale, escribime y lo platicamos!

### B · Para la voz grabada del reel "¿La digitalización es solo para grandes?" (5 archivos)

| Archivo | Frase |
|---|---|
| `frase1` | ¿La digitalización es solo para grandes? |
| `frase2` | Spoiler: no. |
| `frase3` | Si tu negocio vende, compra y cuenta producto, ya calificás. |
| `frase4` | Y si hoy todo vive en un Excel así… hay algo que ordenar. |
| `frase5` | Contanos tu caso. El diagnóstico es sin compromiso. |

## 4 · Dónde dejar los archivos

```
assets/voice/
  jose/
    permiso.png
    referencia.m4a
    frase1.m4a … frase5.m4a
  ana/
    permiso.jpg
    referencia.ogg
```

(Una carpeta por persona, nombre en minúsculas y sin tildes.) Después avisame y corro:

```bash
.venv/Scripts/python tools/preparar_voz.py
```

Eso limpia el audio (quita ruido grave, recorta silencios y nivela el volumen). Luego:

```bash
.venv/Scripts/python tools/render_reel_voz.py --grabada jose
```
```bash
.venv/Scripts/python tools/render_reel_voz.py --clon jose
```

## 5 · Reel de conversación «¿Cuántas cajas te quedan?» (2 voces)

Cada persona graba **solo sus líneas, en un solo audio** (en el mismo lugar y sesión que la referencia), dejando ~1 segundo entre línea y línea. **Esta es la opción más nítida y humana: con el diálogo grabado no hace falta clonar.**
Lean como si estuvieran platicando de verdad (pueden imaginar al otro respondiendo).

**José (IF Techworks)** — archivo, por ejemplo, `assets/voice/jose/dialogo.m4a`:
1. ¿Cuántas cajas de tornillo te quedan?
2. ¿Y según la bodega?
3. Contaste tres veces y no cuadra, ¿verdad?
4. ¿Y si el estante te avisara solito cuándo se está acabando algo?
5. Spoiler: no. Si vendés, comprás y contás producto, ya calificás.
6. Contanos tu caso. El diagnóstico es sin compromiso.

**Irvin (el dueño)** — archivo, por ejemplo, `assets/voice/irvin/dialogo.m4a`:
1. Según el Excel… ciento cincuenta.
2. Mejor no te digo.
3. Cuatro.
4. Eso es para empresas grandes.
5. Va pues. ¿Y por dónde empiezo?

Después:

```bash
.venv/Scripts/python tools/preparar_voz.py
```
```bash
.venv/Scripts/python tools/render_conversacion.py --fuente grabada
```

El guion vive en `prototypes/direcciones/b-conversacion/guion.yaml`: se pueden cambiar líneas, quién las dice,
pausas y lo que aparece en pantalla, y volver a renderizar. Con `--fuente clon` se usa la voz clonada de cada uno
(con control de calidad automático: cada línea se transcribe y se regenera si no dice lo que dice el guion).
