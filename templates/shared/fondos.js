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
  // Textura de papel (fibra, arrugas, dobleces). Sin imagen: solo el papel.
  papel: async (o) => [P.paperTextureFragmentShader, {
    u_colorBack: color(o.back ?? "#e8e2d2"), u_colorPaper: color(o.paper ?? "#f4eee2"), u_colorShadow: color(o.shadow ?? "#7a6f5c"),
    u_image: await imagen(P.emptyPixel), u_isImage: false, u_imageAspectRatio: 1, u_clip: false,
    u_roughness: o.roughness ?? 0.4, u_roughnessSize: 0.3, u_roughnessRows: 0.5, u_fiber: o.fiber ?? 0.3, u_fiberSize: 0.2,
    u_crumples: o.crumples ?? 0.3, u_crumpleCount: 3, u_wrinkles: o.wrinkles ?? 0.4, u_wrinkleSize: 0.4, u_folds: o.folds ?? 0.5,
    u_foldOffsetX: 0, u_foldOffsetY: 0, u_foldSizeX: 0.5, u_foldSizeY: 0.5, u_drops: o.drops ?? 0.1, u_seed: o.seed ?? 5.8,
    u_blending: 0, u_distortion: 0, u_angle: 0, u_noiseTexture: await ruido(), ...tam(o.sizing) }],
  // Trama de pixeles con dithering (look de pantalla).
  trama: async (o) => [P.ditheringFragmentShader, {
    u_colorBack: color(o.back), u_colorFront: color(o.front), u_shape: P.DitheringShapes[o.shape ?? "warp"],
    u_type: P.DitheringTypes[o.type ?? "4x4"], u_pxSize: o.px ?? 4, ...tam({ fit: "none", ...o.sizing }) }],
};
const imagen = (src) => new Promise((ok) => { const i = new Image(); i.onload = () => ok(i); i.src = src; });

export async function fondo(el, tipo, opciones = {}) {
  const [shader, uniforms] = await TIPOS[tipo](opciones);
  // speed 0: no corre solo; cada cuadro se fija con frame(ms) para que el render sea reproducible.
  const m = new P.ShaderMount(el, shader, uniforms, { preserveDrawingBuffer: true }, 0, opciones.frame ?? 0, 1);
  return { frame: (ms) => m.setFrame(ms), mount: m };
}
