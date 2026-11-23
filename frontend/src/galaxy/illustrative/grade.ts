// The grade (S105, BUILD_VIII row 105): a tone and colour pass of the illustrative look, between the bloom and the
// output pass (GalaxyView's HdrOutput), the renderer's tone mapping off so the output pass only encodes sRGB. Colour
// for appearance (D275): none of it is physics.
//
// Why: the goal pictures span about 2 stops from core to disc where the model's disc is 6 stops under its core, and a
// filmic curve washes the core white; the goals carry a warm bar and core against blue arms where the frames are one
// grey-blue. An asinh stretch on luminance compresses the range and keeps each pixel's hue; saturation is taken about
// luminance; a split tone warms the bright and cools the faint.

import type { IllControl, IllFeature, IllParams } from "./feature";

const CONTROLS: readonly IllControl[] = [
  { key: "gain", label: "grade gain", min: -6, max: 8, step: 0.05, unit: "stops", default: 0, about: "The light's scale into the stretch, stops. Illustrative." },
  {
    key: "stretch", label: "asinh stretch", min: 0.1, max: 3000, step: 0.1, log: true, unit: "", default: 30,
    about: "How hard the asinh compresses: about linear below 1 / stretch, logarithmic above. Illustrative.",
  },
  { key: "white", label: "grade white", min: 0.02, max: 50, step: 0.01, log: true, unit: "", default: 1, about: "The linear luminance drawn at full scale. Illustrative." },
  { key: "saturation", label: "saturation", min: 0, max: 3, step: 0.01, unit: "×", default: 1, about: "Colour about each pixel's luminance: 0 grey, 1 as drawn. Illustrative." },
  { key: "contrast", label: "grade contrast", min: 0.3, max: 3, step: 0.01, unit: "power", default: 1, about: "A power on the stretched luminance: above 1 darker faint light. Illustrative." },
  { key: "black", label: "black level", min: 0, max: 0.3, step: 0.005, unit: "", default: 0, about: "Subtracted after the stretch, the rest rescaled: a darker sky. Illustrative." },
  { key: "balance", label: "white balance", min: -1, max: 1, step: 0.01, unit: "", default: 0, about: "Warm (above 0) or cool (below) over the whole picture. Colour for appearance." },
  {
    key: "split", label: "split tone", min: -1, max: 1, step: 0.01, unit: "", default: 0,
    about: "Above 0 the bright light warmer and the faint cooler (a warm core against blue arms); below 0 the reverse. Colour for appearance.",
  },
  {
    key: "highlight", label: "highlight whiten", min: 0, max: 1, step: 0.01, unit: "", default: 0.2,
    about: "Light past full scale keeps its hue (divided by its largest channel); this much of the excess goes to white. Illustrative.",
  },
];

export const grade: IllFeature = {
  id: "grade",
  label: "grade",
  about: "An asinh stretch on luminance that keeps hue, with saturation, contrast, a black level, white balance and a split tone.",
  controls: CONTROLS,
};

/** The grade pass's uniform values from its parameters. */
export function gradeUniforms(p: IllParams): Record<string, number> {
  return {
    uGain: 2 ** (p.gain ?? 0),
    uStretch: p.stretch ?? 30,
    uWhite: p.white ?? 1,
    uSat: p.saturation ?? 1,
    uContrast: p.contrast ?? 1,
    uBlack: p.black ?? 0,
    uBalance: p.balance ?? 0,
    uSplit: p.split ?? 0,
    uHighlight: p.highlight ?? 0.2,
  };
}

/** The grade's luminance weights (Rec. 709, linear light). */
export const LUMA = [0.2126, 0.7152, 0.0722] as const;

/** The pass's fragment: the TS twin below is line for line (gradeColor). */
export const GRADE_FRAGMENT = /* glsl */ `
  uniform sampler2D tDiffuse;
  uniform float uGain;
  uniform float uStretch;
  uniform float uWhite;
  uniform float uSat;
  uniform float uContrast;
  uniform float uBlack;
  uniform float uBalance;
  uniform float uSplit;
  uniform float uHighlight;
  varying vec2 vUv;
  float gradeLum(vec3 c) { return dot(c, vec3(${LUMA.join(", ")})); }
  float gradeAsinh(float x) { return log(x + sqrt(x * x + 1.0)); }
  void main() {
    vec3 c = max(texture2D(tDiffuse, vUv).rgb, vec3(0.0));
    float L = gradeLum(c);
    float y = gradeAsinh(uStretch * uGain * L) / gradeAsinh(uStretch * uWhite);
    y = pow(max(y, 0.0), uContrast);
    vec3 c2 = c * (y / max(L, 1e-8));
    vec3 c3 = max(mix(vec3(gradeLum(c2)), c2, uSat), vec3(0.0));
    float k = clamp(y, 0.0, 1.0);
    vec3 cool = vec3(1.0 - 0.25 * uSplit, 1.0, 1.0 + 0.25 * uSplit);
    vec3 warm = vec3(1.0 + 0.25 * uSplit, 1.0, 1.0 - 0.25 * uSplit);
    c3 *= vec3(1.0 + 0.25 * uBalance, 1.0, 1.0 - 0.25 * uBalance) * mix(cool, warm, k);
    float m = max(c3.r, max(c3.g, c3.b));
    if (m > 1.0) c3 = mix(c3 / m, vec3(1.0), uHighlight * (1.0 - 1.0 / m));
    c3 = max(c3 - uBlack, vec3(0.0)) / (1.0 - uBlack);
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

const lum = (c: readonly number[]) => LUMA[0] * c[0] + LUMA[1] * c[1] + LUMA[2] * c[2];

/** GRADE_FRAGMENT's arithmetic on one linear colour, line for line (the tests' twin). */
export function gradeColor(input: readonly [number, number, number], p: IllParams): [number, number, number] {
  const u = gradeUniforms(p);
  const c = input.map((v) => Math.max(v, 0));
  const L = lum(c);
  let y = Math.asinh(u.uStretch * u.uGain * L) / Math.asinh(u.uStretch * u.uWhite);
  y = Math.max(y, 0) ** u.uContrast;
  const c2 = c.map((v) => v * (y / Math.max(L, 1e-8)));
  const l2 = lum(c2);
  let c3 = c2.map((v) => Math.max(l2 + (v - l2) * u.uSat, 0));
  const k = Math.min(1, Math.max(0, y));
  const s = 0.25 * u.uSplit;
  const tint = [(1 + 0.25 * u.uBalance) * ((1 - s) + 2 * s * k), 1, (1 - 0.25 * u.uBalance) * ((1 + s) - 2 * s * k)];
  c3 = c3.map((v, i) => v * tint[i]);
  const m = Math.max(...c3);
  if (m > 1) c3 = c3.map((v) => v / m + (1 - v / m) * u.uHighlight * (1 - 1 / m));
  return c3.map((v) => Math.max(v - u.uBlack, 0) / (1 - u.uBlack)) as [number, number, number];
}
