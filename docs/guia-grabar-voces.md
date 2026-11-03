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

## 2 · Cómo grabar (con el celular)

- Cuarto silencioso, sin eco (un cuarto con cortinas, ropa o sillones es mejor que un baño o una cocina).
- Celular a 20-30 cm de la boca, siempre a la misma distancia. Sin audífonos con micrófono.
- App de notas de voz del celular (cualquier formato: m4a, mp3, wav, ogg de WhatsApp).
- Hablá como le explicarías algo a un cliente que conocés: natural, con energía, sin leer "de corrido".
- Dejá **1 segundo de silencio** al inicio y al final de cada archivo.
- Si te equivocás, repetí la frase entera en un archivo nuevo.

## 3 · Qué grabar

### A · Para la voz clonada: `referencia` (20-30 s, un solo archivo)

Leé este texto con tu tono natural:

> Hola, ¿cómo estás? Te cuento rápido cómo trabajamos. Primero platicamos de tu negocio: qué vendés, cómo
> llevás el inventario y qué es lo que más te quita tiempo. Después te mostramos, con ejemplos de verdad,
> cómo se vería todo ordenado. Sin tecnicismos y sin compromiso. ¿Te parece si lo vemos esta semana?

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
