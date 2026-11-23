// The grade (S105, BUILD_VIII row 105): a tone and colour pass of the illustrative look, between the bloom and the
// output pass (GalaxyView's HdrOutput), the renderer's tone mapping off so the output pass only encodes sRGB. Colour
// for appearance (D275): none of it is physics.
//
// Why: the goal pictures span about 2 stops from core to disc where the model's disc is 6 stops under its core, and a
// filmic curve washes the core white; the goals carry a warm bar and core against blue arms where the frames are one
// grey-blue. An asinh stretch on luminance compresses the range and keeps each pixel's hue; saturation is taken about
// luminance; a split tone warms the bright and cools the faint.
//
// The fix pass (S105, the lead's sheets): the curve has a shoulder above `knee` (identity below it, an exponential
// approach to 1 above it, never reaching it), and the light in the shoulder drifts toward a pale warm white, so a bar
// is a cream ellipse brightening smoothly instead of one flat saturated colour clipped at full scale. The black level
// is a soft toe on luminance (a per-channel subtraction made the faintest light pure blue); faint light loses its
// saturation below `faint`, so the outer disc sinks into the sky grey-blue and smooth. The tints are colours of their
// own, luminance-normalised: the cool side between sky blue and lavender, the warm between orange and cream - the
// green channel moves with the others, where a red-blue-only tint read teal.

import type { IllControl, IllFeature, IllParams } from "./feature";

const CONTROLS: readonly IllControl[] = [
  { key: "gain", label: "grade gain", min: -6, max: 8, step: 0.05, unit: "stops", default: 0, perTemplate: { milky_way: -0.5, ngc_4414: -0.2 }, about: "The light's scale into the stretch, stops. Illustrative." },
  {
    key: "stretch", label: "asinh stretch", min: 0.1, max: 3000, step: 0.1, log: true, unit: "", default: 30, perTemplate: { milky_way: 35, ngc_4414: 20 },
    about: "How hard the asinh compresses: about linear below 1 / stretch, logarithmic above. Illustrative.",
  },
  { key: "white", label: "grade white", min: 0.02, max: 50, step: 0.01, log: true, unit: "", default: 1, about: "The linear luminance drawn at full scale (before the shoulder). Illustrative." },
  {
    key: "knee", label: "shoulder knee", min: 0.3, max: 0.98, step: 0.01, unit: "", default: 0.75, perTemplate: { milky_way: 0.8, ngc_4414: 0.6 },
    about: "The stretched brightness (0 to 1) above which the curve rolls off toward full scale and the light drifts to a pale warm white; below it the curve is the stretch as it is. Illustrative.",
  },
  { key: "saturation", label: "saturation", min: 0, max: 3, step: 0.01, unit: "×", default: 1, perTemplate: { milky_way: 1.7, ngc_4414: 2 }, about: "Colour about each pixel's luminance: 0 grey, 1 as drawn. Illustrative." },
  {
    key: "faint", label: "faint fade", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0.3, ngc_4414: 0.12 },
    about: "The stretched brightness below which colour fades (to `faint colour` at nothing): the faintest light goes grey into the sky instead of a saturated fringe. 0 no fade. Illustrative.",
  },
  {
    key: "faintsat", label: "faint colour", min: 0, max: 1, step: 0.01, unit: "×", default: 1, perTemplate: { milky_way: 0.2, ngc_4414: 0.3 },
    about: "The share of the saturation left at the faintest light, under the faint fade. Illustrative.",
  },
  { key: "contrast", label: "grade contrast", min: 0.3, max: 3, step: 0.01, unit: "power", default: 1, perTemplate: { milky_way: 0.8, ngc_4414: 1.1 }, about: "A power on the stretched luminance: above 1 darker faint light. Illustrative." },
  {
    key: "black", label: "black level", min: 0, max: 0.3, step: 0.005, unit: "", default: 0, perTemplate: { milky_way: 0.1, ngc_4414: 0.1 },
    about: "A soft toe on the stretched luminance (each pixel's colour kept): the faint light about this level and under it taken smoothly down to a dark sky. Illustrative.",
  },
  { key: "balance", label: "white balance", min: -1, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: -0.55, ngc_4414: -0.15 }, about: "Toward the warm tint (above 0) or the cool tint (below) over the whole picture. Colour for appearance." },
  {
    key: "split", label: "split tone", min: -1, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1, ngc_4414: 1 },
    about: "Above 0 the bright light toward the warm tint and the faint toward the cool (a warm core against blue arms); below 0 the reverse. Colour for appearance.",
  },
  {
    key: "pivot", label: "split pivot", min: 0.05, max: 0.95, step: 0.01, unit: "", default: 0.6, perTemplate: { milky_way: 0.9, ngc_4414: 0.65 },
    about: "The stretched brightness (0 to 1) about which the split tone turns from cool to warm, over a quarter either side: high, only the brightest (a bar, a core) warm. Colour for appearance.",
  },
  {
    key: "cool", label: "cool hue", min: 0, max: 1, step: 0.01, unit: "", default: 0.5, perTemplate: { milky_way: 0.3, ngc_4414: 0.2 },
    about: "The cool tint's colour: 0 sky blue, 1 lavender. Colour for appearance.",
  },
  {
    key: "warm", label: "warm hue", min: 0, max: 1, step: 0.01, unit: "", default: 0.5, perTemplate: { milky_way: 0.8, ngc_4414: 0.8 },
    about: "The warm tint's colour: 0 orange, 1 cream. Colour for appearance.",
  },
  {
    key: "green", label: "green removal", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1, ngc_4414: 1 },
    about: "The green channel held to the mean of red and blue where it is above it, this much (the astronomer's SCNR, luminance kept): no galaxy's light is green, and a green-cyan cast at a core is the render's. Colour for appearance.",
  },
  {
    key: "highlight", label: "highlight whiten", min: 0, max: 1, step: 0.01, unit: "", default: 0.2, perTemplate: { milky_way: 0.5, ngc_4414: 0.85 },
    about: "How far the light in the shoulder drifts to a pale warm white (all the way at full scale at 1), and how much of the saturation's boost is taken off above half scale. Illustrative.",
  },
];

export const grade: IllFeature = {
  id: "grade",
  label: "grade",
  about: "An asinh stretch on luminance with a shoulder, keeping hue, with saturation, a faint fade, contrast, a black toe, white balance and a split tone.",
  controls: CONTROLS,
};

/** The grade pass's uniform values from its parameters. */
export function gradeUniforms(p: IllParams): Record<string, number> {
  return {
    uGain: 2 ** (p.gain ?? 0),
    uStretch: p.stretch ?? 30,
    uWhite: p.white ?? 1,
    uKnee: p.knee ?? 0.75,
    uSat: p.saturation ?? 1,
    uFaint: p.faint ?? 0,
    uFaintSat: p.faintsat ?? 1,
    uContrast: p.contrast ?? 1,
    uBlack: p.black ?? 0,
    uBalance: p.balance ?? 0,
    uSplit: p.split ?? 0,
    uPivot: p.pivot ?? 0.6,
    uCool: p.cool ?? 0.5,
    uWarm: p.warm ?? 0.5,
    uGreen: p.green ?? 0,
    uHighlight: p.highlight ?? 0.2,
  };
}

/** The largest finite half float, near enough: the grade's input is clamped to it. */
export const HALF_MAX = 60000;

/** The grade's luminance weights (Rec. 709, linear light). */
export const LUMA = [0.2126, 0.7152, 0.0722] as const;

/** The tints' end colours (linear, each normalised to its luminance where used). Colour for appearance. */
export const SKY = [0.62, 0.8, 1.0] as const;
export const LAVENDER = [0.86, 0.8, 1.0] as const;
export const ORANGE = [1.0, 0.78, 0.52] as const;
export const CREAM = [1.0, 0.93, 0.78] as const;
/** The pale warm white the shoulder's light drifts to. */
export const PALE = [1.0, 0.96, 0.88] as const;

const vec3 = (c: readonly number[]) => `vec3(${c.map((v) => v.toFixed(4)).join(", ")})`;

/** The pass's fragment: the TS twin below is line for line (gradeColor). */
export const GRADE_FRAGMENT = /* glsl */ `
  uniform sampler2D tDiffuse;
  uniform float uGain;
  uniform float uStretch;
  uniform float uWhite;
  uniform float uKnee;
  uniform float uSat;
  uniform float uFaint;
  uniform float uFaintSat;
  uniform float uContrast;
  uniform float uBlack;
  uniform float uBalance;
  uniform float uSplit;
  uniform float uPivot;
  uniform float uCool;
  uniform float uWarm;
  uniform float uGreen;
  uniform float uHighlight;
  varying vec2 vUv;
  float gradeLum(vec3 c) { return dot(c, vec3(${LUMA.join(", ")})); }
  float gradeAsinh(float x) { return log(x + sqrt(x * x + 1.0)); }
  float gradeShoulder(float y, float k) {
    return y <= k ? y : k + (1.0 - k) * (1.0 - exp(-(y - k) / (1.0 - k)));
  }
  float gradeToeF(float y, float b) { return 0.5 * ((y - b) + sqrt((y - b) * (y - b) + 0.25 * b * b)); }
  float gradeToe(float y, float b) {
    if (b <= 0.0) return y;
    float f0 = gradeToeF(0.0, b);
    return (gradeToeF(y, b) - f0) / (gradeToeF(1.0, b) - f0);
  }
  vec3 gradeTint(vec3 col, float amount) { return mix(vec3(1.0), col / gradeLum(col), amount); }
  void main() {
    // Clamped to the half-float target's range: a bulge's cusp overflows a channel to infinity, which the stretch would
    // turn into a hue of its own (a green-cyan dot at NGC 4414's centre before this clamp).
    vec3 c = clamp(texture2D(tDiffuse, vUv).rgb, vec3(0.0), vec3(${HALF_MAX.toFixed(1)}));
    float L = gradeLum(c);
    float y = gradeAsinh(uStretch * uGain * L) / gradeAsinh(uStretch * uWhite);
    y = pow(max(y, 0.0), uContrast);
    y = gradeToe(gradeShoulder(y, uKnee), uBlack);
    vec3 c2 = c * (y / max(L, 1e-8));
    c2.g = mix(c2.g, min(c2.g, 0.5 * (c2.r + c2.b)), uGreen);
    c2 *= y / max(gradeLum(c2), 1e-8);
    vec3 cool = mix(${vec3(SKY)}, ${vec3(LAVENDER)}, uCool);
    vec3 warm = mix(${vec3(ORANGE)}, ${vec3(CREAM)}, uWarm);
    float k = smoothstep(uPivot - 0.25, uPivot + 0.25, y);
    if (uSplit < 0.0) k = 1.0 - k;
    vec3 tint = mix(gradeTint(cool, abs(uSplit)), gradeTint(warm, abs(uSplit)), k);
    tint *= uBalance >= 0.0 ? gradeTint(warm, uBalance) : gradeTint(cool, -uBalance);
    vec3 c3 = c2 * tint;
    c3 *= y / max(gradeLum(c3), 1e-8);
    float sat = uSat * mix(uFaintSat, 1.0, smoothstep(0.0, max(uFaint, 1e-4), y));
    sat = mix(sat, 1.0, uHighlight * smoothstep(0.5, 1.0, y));
    c3 = max(mix(vec3(y), c3, sat), vec3(0.0));
    float w = uHighlight * smoothstep(uKnee, 1.0, y);
    c3 = mix(c3, y * ${vec3(PALE)} / gradeLum(${vec3(PALE)}), w);
    float m = max(c3.r, max(c3.g, c3.b));
    if (m > 1.0) c3 /= m;
    gl_FragColor = vec4(c3, 1.0);
  }
`;

export const GRADE_VERTEX = /* glsl */ `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

/** GLSL's smoothstep. */
const smoothstep = (e0: number, e1: number, x: number) => {
  const t = Math.min(1, Math.max(0, (x - e0) / (e1 - e0)));
  return t * t * (3 - 2 * t);
};
const lum = (c: readonly number[]) => LUMA[0] * c[0] + LUMA[1] * c[1] + LUMA[2] * c[2];
const mix3 = (a: readonly number[], b: readonly number[], t: number) => a.map((v, i) => v + (b[i] - v) * t);
// The shader's constants are written to four places: the twin reads the same rounding.
const r4 = (c: readonly number[]) => c.map((v) => Number(v.toFixed(4)));
const tintOf = (col: readonly number[], amount: number) => {
  const l = lum(col);
  return col.map((v) => 1 + (v / l - 1) * amount);
};

/** The shoulder: the identity up to `knee`, then an exponential approach to 1 (continuous in value and slope, below 1). */
export function shoulder(y: number, knee: number): number {
  return y <= knee ? y : knee + (1 - knee) * (1 - Math.exp(-(y - knee) / (1 - knee)));
}

const toeF = (y: number, b: number) => 0.5 * (y - b + Math.sqrt((y - b) * (y - b) + 0.25 * b * b));
/** The black level's soft toe: 0 to 0, 1 to 1, monotone; the identity at b = 0. */
export function toe(y: number, b: number): number {
  if (b <= 0) return y;
  const f0 = toeF(0, b);
  return (toeF(y, b) - f0) / (toeF(1, b) - f0);
}

/** The tone curve alone: a grey's stretched, shouldered and toed luminance. */
export function gradeTone(L: number, p: IllParams): number {
  const u = gradeUniforms(p);
  let y = Math.asinh(u.uStretch * u.uGain * L) / Math.asinh(u.uStretch * u.uWhite);
  y = Math.max(y, 0) ** u.uContrast;
  return toe(shoulder(y, u.uKnee), u.uBlack);
}

/** GRADE_FRAGMENT's arithmetic on one linear colour, line for line (the tests' twin). */
export function gradeColor(input: readonly [number, number, number], p: IllParams): [number, number, number] {
  const u = gradeUniforms(p);
  const c = input.map((v) => Math.min(HALF_MAX, Math.max(v, 0)));
  const L = lum(c);
  const y = gradeTone(L, p);
  let c2 = c.map((v) => v * (y / Math.max(L, 1e-8)));
  c2[1] = c2[1] + (Math.min(c2[1], 0.5 * (c2[0] + c2[2])) - c2[1]) * u.uGreen;
  const l2 = Math.max(lum(c2), 1e-8);
  c2 = c2.map((v) => v * (y / l2));
  const cool = mix3(r4(SKY), r4(LAVENDER), u.uCool);
  const warm = mix3(r4(ORANGE), r4(CREAM), u.uWarm);
  let k = smoothstep(u.uPivot - 0.25, u.uPivot + 0.25, y);
  if (u.uSplit < 0) k = 1 - k;
  const a = Math.abs(u.uSplit);
  let tint = mix3(tintOf(cool, a), tintOf(warm, a), k);
  const bal = u.uBalance >= 0 ? tintOf(warm, u.uBalance) : tintOf(cool, -u.uBalance);
  tint = tint.map((v, i) => v * bal[i]);
  let c3 = c2.map((v, i) => v * tint[i]);
  const l3 = Math.max(lum(c3), 1e-8);
  c3 = c3.map((v) => v * (y / l3));
  let sat = u.uSat * (u.uFaintSat + (1 - u.uFaintSat) * smoothstep(0, Math.max(u.uFaint, 1e-4), y));
  sat = sat + (1 - sat) * u.uHighlight * smoothstep(0.5, 1, y);
  c3 = c3.map((v) => Math.max(y + (v - y) * sat, 0));
  const w = u.uHighlight * smoothstep(u.uKnee, 1, y);
  const pale = r4(PALE);
  const lp = lum(pale);
  c3 = c3.map((v, i) => v + ((y * pale[i]) / lp - v) * w);
  const m = Math.max(...c3);
  if (m > 1) c3 = c3.map((v) => v / m);
  return c3 as [number, number, number];
}
