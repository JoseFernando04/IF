# Direcciones visuales (prototipo)

Dos direcciones para salir de la "plantilla de IA". Cada una trae `slide.png` (portada del carrusel
"5 señales…") y `reel.mp4` (primeros 5 s del reel "¿La digitalización es solo para grandes?").

Renderizar: `.venv/Scripts/python tools/render_direction.py prototypes/direcciones/<carpeta>`

| | A · Papel editorial | B · Documental |
|---|---|---|
| Base | Crema `#F2EDE4` con grano y fibra de papel | Foto real a sangre en duotono verde |
| Tipografía | Instrument Serif gigante + Bricolage Grotesque condensada + Caveat (mano) | Bricolage condensada en mayúsculas + Instrument Serif itálica + Inter Tight |
| Elemento real | Recorte de libreta con conteos tachados | Fotografía de pasillo de tienda + etiqueta de archivo Excel tachada |
| Acento | Marcador amarillo dibujado | Cintas amarillas como etiquetas |
| Motion | Golpe con rebote + sacudida, tachón que se dibuja, escritura a mano, transición "etiqueta de precio" | Ken Burns + paralaje, letra por letra, match cut (la cinta llena la pantalla), "NO." con golpe |
| Subtítulos | Sin subtítulos (el texto cinético es el mensaje) | Editoriales, palabra por palabra, la hablada en amarillo |

## Checklist "¿se ve IA?"

| Punto | A | B |
|---|---|---|
| Composición distinta a la plantilla anterior | ✅ | ✅ |
| Elemento del mundo real (foto, textura, escaneo) | ✅ papel + libreta | ✅ foto + etiqueta |
| Cero íconos en cuadrito con glow, cero blobs | ✅ | ✅ |
| ≥3 duraciones/easings distintos | ✅ 6 (golpe, trazo, lineal, expo, back, sine) | ✅ 6 |
| Sigue el audio | ⚠️ sigue los SFX; falta voz definitiva | ⚠️ tiempos por palabra simulados hasta tener voz |
| Copy con ejemplo concreto y voz guatemalteca | ✅ "¿y la tienda de la esquina?", voseo | ✅ voseo |
| Licencias gratuitas y comerciales | ✅ | ✅ |

## Reporte de seguridad

| Componente | Versión | Fuente | Licencia | Verificación |
|---|---|---|---|---|
| gsap (+SplitText, CustomEase, DrawSVG) | 3.15.0 (abr. 2026) | registry.npmjs.org, mantenedor `greensock` | GSAP Standard No-Charge | Integridad sha512 coincide con el registro; sin dependencias ni scripts de instalación; solo se copiaron 4 archivos `.min.js` |
| Bricolage Grotesque, Instrument Serif, Inter Tight, Caveat | — | github.com/google/fonts | OFL 1.1 | Repositorio oficial de Google Fonts |
| Foto `pasillo-tienda.jpg` | — | unsplash.com (Sean Foster) | Unsplash License | Descarga oficial |
| SFX | — | Generados localmente | Propios | Sin código ni archivos externos |

No se instaló Node.js, npm, HyperFrames, Remotion ni ninguna skill/MCP externa: el motor propio ya
renderiza HTML + GSAP a MP4 de forma determinista, así que no hacía falta sumar superficie de ataque.
