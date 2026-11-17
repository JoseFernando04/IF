# Guiones de voz — Flor de Loto Spa (para José en ElevenLabs)

Guardar cada audio en `campanas/flor-de-loto-spa/material/voz/` con estos nombres exactos:
`reel-A.mp3`, `reel-B.mp3`, `reel-C.mp3`. Esa carpeta no va a git.

- El texto está en **tuteo**, como escribe el cliente («inhala», «agenda», «ven»).
- Ritmo **lento y cálido**; es un spa. Deja silencios de 1 segundo donde dice *(pausa)*.
- La herramienta compara el audio con el guion: si se cambia alguna palabra, avísame para actualizar el YAML.
- Sin siglas. «WhatsApp» se dice normal.

---

## Reel A — Respira con la flor (~25 s)

Aquí la pausa es real: la flor de la pantalla se abre mientras inhalas y se cierra mientras sueltas.

> Dame veinte segundos. *(pausa)*
> Inhala, dos, tres, cuatro. *(pausa)*
> Suelta despacio. *(pausa larga)*
> Otra vez. Inhala. *(pausa)*
> Y suelta. *(pausa larga)*
> Así se siente una pausa.
> Ahora imagina una hora completa así.
> En Flor de Loto Spa te esperamos. Agenda tu cita por WhatsApp.

## Reel B — ¿Qué te está pidiendo hoy? (~25 s)

> Hay días en que te pide atención el cuerpo.
> Otros, la mente.
> Y otros, algo más adentro. *(pausa)*
> Para el cuerpo, masajes relajantes, terapéuticos, linfáticos y más.
> Para la mente, acompañamiento profesional con psicología.
> Para el alma, reiki, para equilibrar tu energía. *(pausa)*
> Los tres, en un mismo lugar.
> Flor de Loto Spa. Agenda tu cita por WhatsApp.

## Reel C — Estrenamos espacio (~22 s)

> Tenemos noticias.
> Flor de Loto Spa ahora está en un lugar más amplio y acogedor, aquí en Cobán.
> Más espacio, un ambiente más tranquilo y una decoración renovada.
> Lo que no cambia es el cuidado con que te atendemos, de lunes a domingo.
> Ven a conocerlo. Agenda tu cita por WhatsApp.

---

Cuando estén los audios:
```
.venv/Scripts/python tools/render_formato.py campanas/flor-de-loto-spa/piezas/reel-A.yaml
```
(igual para B y C). Sale `salida/reel-X/reel.mp4`, `cover.jpg` y `caption.txt`.
