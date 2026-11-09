// Fondos animados con Paper Shaders (Apache-2.0, vendorizado en assets/vendor/paper-shaders-0.0.82).
// Uso desde una plantilla (módulo): import { fondo } from "__SHARED__/fondos.js";
//   const f = await fondo(div, "malla", { colors: [...], ... });  f.frame(ms) → cuadro determinista.
// El navegador debe abrirse con --allow-file-access-from-files para importar módulos desde file://.
import * as P from "../../assets/vendor/paper-shaders-0.0.82/dist/index.js";

const color = (c) => P.getShaderColorFromString(c);
const tam = (s = {}) => {
  const z = { ...P.defaultObjectSizing, fit: "cover", ...s };
  return { u_fit: P.ShaderFitOptions[z.fit], u_scale: z.scale, u_rotation: z.rotation, u_offsetX: z.offsetX,
    u_offsetY: z.offsetY, u_originX: z.originX, u_originY: z.originY, u_worldWidth: z.worldWidth, u_worldHeight: z.worldHeight };
};
const ruido = () => new Promise((ok) => { const i = P.getShaderNoiseTexture(); i.complete ? ok(i) : (i.onload = () => ok(i)); });

const TIPOS = {
  // Degradado de malla suave (fondos de UI, "este o este").
  malla: async (o) => [P.meshGradientFragmentShader, {
    u_colors: o.colors.map(color), u_colorsCount: o.colors.length, u_distortion: o.distortion ?? 0.8,
    u_swirl: o.swirl ?? 0.1, u_grainMixer: o.grainMixer ?? 0, u_grainOverlay: o.grainOverlay ?? 0, ...tam(o.sizing) }],
  // Degradado con grano (look impreso / riso).
  grano: async (o) => [P.grainGradientFragmentShader, {
    u_colorBack: color(o.back), u_colors: o.colors.map(color), u_colorsCount: o.colors.length,
    u_softness: o.softness ?? 0.5, u_intensity: o.intensity ?? 0.5, u_noise: o.noise ?? 0.25,
    u_shape: P.GrainGradientShapes[o.shape ?? "corners"], u_noiseTexture: await ruido(), ...tam(o.sizing) }],
  // Retícula de puntos (grilla suiza).
  puntos: async (o) => [P.dotGridFragmentShader, {
    u_colorBack: color(o.back), u_colorFill: color(o.fill), u_colorStroke: color(o.stroke ?? o.fill),
    u_dotSize: o.size ?? 2, u_gapX: o.gap ?? 40, u_gapY: o.gap ?? 40, u_strokeWidth: 0, u_sizeRange: o.sizeRange ?? 0,
    u_opacityRange: o.opacityRange ?? 0, u_shape: P.DotGridShapes[o.shape ?? "circle"], ...tam({ fit: "none", ...o.sizing }) }],
};

export async function fondo(el, tipo, opciones = {}) {
  const [shader, uniforms] = await TIPOS[tipo](opciones);
  // speed 0: no corre solo; cada cuadro se fija con frame(ms) para que el render sea reproducible.
  const m = new P.ShaderMount(el, shader, uniforms, { preserveDrawingBuffer: true }, 0, opciones.frame ?? 0, 1);
  return { frame: (ms) => m.setFrame(ms), mount: m };
}
