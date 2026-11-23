// The arms (BUILD_VIII row 108, S108): the arms made to stand out of the disc under the illustrative look, and their
// sparkle. Display-only, of the illustrative look's own (D275).
//
// The weight (armsField.ts): the model's published arm contrast (pattern_density_contrast blended with
// gas_density_contrast), each ring over its mean, evened across radii, raised to a power and floored between the arms,
// faded in outside the bar and carried past the model's arms' end along their own winding - a polar map built once per
// (arrays frame, shaping values) and handed to the march as a texture. Its light hook (illArmsLight, the contract's
// `light`) multiplies all the starlight at the midplane point - the arms brighter, the disc between them dimmer, the
// ring's mean light kept - and tints it: the arms toward blue-white, the disc between them toward lavender. Its young
// hook (illArmsYoung) gathers the clustered young light onto the ridges with a power of its own.
//
// The sparkle (armsSparkle.ts, SparkleLayer.tsx): a layer of small bright blue-white points along the ridges, grouped
// as OB associations, from a seed of the viewer's own, drawn through FluxPoints (so the dust dims them as it dims
// the knots).

import { createElement, lazy, Suspense } from "react";
import { DataTexture, FloatType, LinearFilter, ClampToEdgeWrapping, RepeatWrapping, RGBAFormat } from "three";
import { armContrast, armMap, gridOf, type ArmGrid, type ArmShape } from "./armsField";
import type { IllContext, IllFeature, IllFrame, IllLayerProps, IllParams } from "./feature";
import { memoOn } from "./feature";

/** The /api/arrays names the arms read. */
export const ARMS_ARRAYS = ["bar_half_length", "gas_density_contrast", "pattern_density_contrast"] as const;

/** The shaping values a map is built from (any change rebuilds it; the tints and the sparkle's gain do not). */
export function shapeOf(p: IllParams, frame: IllFrame | null): ArmShape {
  const bar = frame?.header.scalars.bar_half_length;
  const barred = typeof bar === "number" && Number.isFinite(bar) && bar > 0;
  return {
    gasMix: p.gasmix ?? 0.3,
    power: p.power ?? 4,
    equalise: p.equalise ?? 0.6,
    floor: p.floor ?? 0.45,
    cap: p.cap ?? 3,
    start: Math.max(p.inner ?? 2, barred ? (p.barfade ?? 1.1) * (bar as number) : 0),
    width: p.fadewidth ?? 1.5,
    extend: p.extend ?? 0,
    young: p.young ?? 4,
  };
}

/** The arm map and its grid for a frame and parameters, or null without the contrast. */
const mapOf = memoOn((frame: unknown, ...values: unknown[]) => {
  const f = frame as IllFrame | null;
  const pattern = (f?.arrays.pattern_density_contrast as ArrayLike<number> | undefined) ?? null;
  const gas = (f?.arrays.gas_density_contrast as ArrayLike<number> | undefined) ?? null;
  const any = pattern ?? gas;
  if (!f || !any) return null;
  const grid = gridOf(f.header, any.length);
  const [shapeJson, strength] = values as [string, number];
  const shape = JSON.parse(shapeJson) as ArmShape;
  const n = armContrast(pattern, gas, grid, shape);
  return { grid, map: armMap(n, grid, shape, strength) };
});

/** The arm map for these parameters on this frame (the same object while neither changes). */
export function armMapFor(p: IllParams, frame: IllFrame | null): { grid: ArmGrid; map: Float32Array } | null {
  return mapOf(frame, JSON.stringify(shapeOf(p, frame)), p.strength ?? 1);
}

const textureOf = memoOn((built: unknown) => {
  const b = built as { grid: ArmGrid; map: Float32Array } | null;
  if (!b) return null;
  const t = new DataTexture(b.map, b.grid.nR, b.grid.nPhi, RGBAFormat, FloatType);
  t.minFilter = LinearFilter;
  t.magFilter = LinearFilter;
  t.wrapS = ClampToEdgeWrapping;
  t.wrapT = RepeatWrapping;
  t.generateMipmaps = false;
  t.needsUpdate = true;
  return t;
});

/** A tint of unit mean: white mixed toward `toward` by `share`. */
export function tint(toward: readonly [number, number, number], share: number): [number, number, number] {
  const c = toward.map((v) => 1 + (v - 1) * share) as [number, number, number];
  const mean = (c[0] + c[1] + c[2]) / 3;
  return c.map((v) => v / mean) as [number, number, number];
}

/** The arms' blue-white and the disc's lavender, before the share (unit mean at full share). */
export const ARM_BLUE: readonly [number, number, number] = [0.78, 0.97, 1.25];
export const INTER_LAVENDER: readonly [number, number, number] = [1.06, 0.9, 1.04];

const Sparkle = lazy(() => import("./SparkleLayer"));
/** The sparkle's drawing, loaded apart from the registry (it draws through FluxPoints, which imports the registry). */
function ArmsLayer(props: IllLayerProps) {
  return createElement(Suspense, { fallback: null }, createElement(Sparkle, props));
}

export const arms: IllFeature = {
  id: "arms",
  label: "arms",
  about: "The arms made to stand out of the disc: the model's published arm contrast sharpened into narrow bright ridges over a dimmer disc, tinted blue-white on the arms and lavender between them, with a sparkle of young stars along the ridges. Illustrative.",
  controls: [
    {
      key: "strength", label: "arm strength", min: 0, max: 1.5, step: 0.01, unit: "×", default: 1, perTemplate: { milky_way: 1, ngc_4414: 0.8 },
      about: "How much of the arms' shaping is applied to the starlight: 0 the disc as the model lights it, 1 the full shaping below. Illustrative.",
    },
    {
      key: "gasmix", label: "gas in the arms", min: 0, max: 1, step: 0.01, unit: "", default: 0.3, perTemplate: { milky_way: 0.3, ngc_4414: 0.5 },
      about: "The share of the gas's density contrast in the arms' placement, the rest the stars' (both the model's published fields): the gas's ridges are narrower and patchier. Illustrative.",
    },
    {
      key: "power", label: "ridge power", min: 1, max: 16, step: 0.1, unit: "", default: 5, perTemplate: { milky_way: 5, ngc_4414: 3 },
      about: "The contrast raised to this power over its ring mean: higher narrows the arms to sharper ridges. Illustrative.",
    },
    {
      key: "equalise", label: "even the arms", min: 0, max: 1, step: 0.01, unit: "", default: 0.6, perTemplate: { milky_way: 0.7, ngc_4414: 0.5 },
      about: "0 the model's own arm amplitude at each radius; 1 every ring's arm contrast evened to one level, so the outer arms read as strongly as the inner. Illustrative.",
    },
    {
      key: "floor", label: "inter-arm light", min: 0, max: 1, step: 0.01, unit: "", default: 0.45, perTemplate: { milky_way: 0.4, ngc_4414: 0.6 },
      about: "The disc's light between the arms, as a share of its ring's mean (the ring's mean light is kept): lower darkens the gaps. Illustrative.",
    },
    {
      key: "cap", label: "ridge cap", min: 1, max: 8, step: 0.1, unit: "×", default: 3, perTemplate: { milky_way: 3, ngc_4414: 3 },
      about: "The most a ridge's light is multiplied. Illustrative.",
    },
    {
      key: "young", label: "young on ridges", min: 0, max: 16, step: 0.1, unit: "", default: 4, perTemplate: { milky_way: 6, ngc_4414: 4 },
      about: "The clustered young light's own power over the arms' ridge (its ring mean kept): higher gathers it onto the ridges; 0 leaves it as the model places it. Illustrative.",
    },
    {
      key: "barfade", label: "bar fade", min: 0, max: 3, step: 0.05, unit: "× bar", default: 1.1, perTemplate: { milky_way: 1.1, ngc_4414: 1.1 },
      about: "The arms' shaping starts at this multiple of the bar's half-length (the published bar_half_length), so the bar and the bulge are never brightened. Illustrative.",
    },
    {
      key: "inner", label: "inner start", min: 0, max: 10, step: 0.1, unit: "kpc", default: 2, perTemplate: { milky_way: 2, ngc_4414: 3.5 },
      about: "The arms' shaping starts no nearer the centre than this, kpc (an unbarred disc's start). Illustrative.",
    },
    {
      key: "fadewidth", label: "fade-in width", min: 0, max: 6, step: 0.1, unit: "kpc", default: 1.5, perTemplate: { milky_way: 1.5, ngc_4414: 2 },
      about: "Over how many kpc the arms' shaping fades in from its start. Illustrative.",
    },
    {
      key: "extend", label: "arms carried out", min: 0, max: 15, step: 0.5, unit: "kpc", default: 5, perTemplate: { milky_way: 6, ngc_4414: 4 },
      about: "How far past the ring where the model's arms fade out their pattern is carried outward along the arms' own measured winding, kpc, so the arms reach the disc's edge; 0 the model's end. Illustrative.",
    },
    {
      key: "blue", label: "arm blue", min: 0, max: 1.5, step: 0.01, unit: "", default: 0.6, perTemplate: { milky_way: 0.6, ngc_4414: 0.6 },
      about: "The arms' light tinted toward blue-white by this share. Illustrative.",
    },
    {
      key: "lavender", label: "inter-arm lavender", min: 0, max: 1.5, step: 0.01, unit: "", default: 0.3, perTemplate: { milky_way: 0.4, ngc_4414: 0 },
      about: "The disc's light between the arms (outside the bar's fade) tinted toward lavender by this share. Illustrative.",
    },
    {
      key: "sparkle", label: "sparkle points", min: 0, max: 80000, step: 1000, unit: "", default: 30000, perTemplate: { milky_way: 30000, ngc_4414: 20000 },
      about: "How many small bright young-star points are scattered along the arms' ridges; 0 none. Illustrative.",
    },
    {
      key: "sparklegain", label: "sparkle brightness", min: 10, max: 1e7, step: 0.01, log: true, unit: "L☉", default: 2e4, perTemplate: { milky_way: 2e4, ngc_4414: 2e4 },
      about: "The faintest sparkle point's light, L☉ over the white point (on the field's scale, with the exposure). Illustrative.",
    },
    {
      key: "sparklerange", label: "sparkle range", min: 1, max: 1000, step: 0.01, log: true, unit: "×", default: 40, perTemplate: { milky_way: 40, ngc_4414: 40 },
      about: "The brightest sparkle point over the faintest. Illustrative.",
    },
    {
      key: "sparkleslope", label: "sparkle slope", min: 0.3, max: 4, step: 0.05, unit: "", default: 1.4, perTemplate: { milky_way: 1.4, ngc_4414: 1.4 },
      about: "The brightness law's index: lower has more bright points, higher more faint. Illustrative.",
    },
    {
      key: "sparkleridge", label: "sparkle on ridge", min: 0.2, max: 6, step: 0.05, unit: "", default: 2, perTemplate: { milky_way: 2, ngc_4414: 1.5 },
      about: "The sparkle's density as this power of the arm share: higher keeps the points on the ridge and thins them faster toward the arm's edges. Illustrative.",
    },
    {
      key: "clump", label: "sparkle grouped", min: 0, max: 1, step: 0.01, unit: "", default: 0.6, perTemplate: { milky_way: 0.6, ngc_4414: 0.75 },
      about: "The share of sparkle points gathered into groups (OB associations), the rest single. Illustrative.",
    },
    {
      key: "groupsize", label: "group size", min: 10, max: 600, step: 5, unit: "pc", default: 120, perTemplate: { milky_way: 120, ngc_4414: 150 },
      about: "A sparkle group's gaussian radius, pc. Illustrative.",
    },
    {
      key: "members", label: "group members", min: 1, max: 60, step: 1, unit: "", default: 10, perTemplate: { milky_way: 10, ngc_4414: 14 },
      about: "A sparkle group's mean number of points. Illustrative.",
    },
    {
      key: "sparklesize", label: "sparkle size", min: 0.5, max: 4, step: 0.1, unit: "px", default: 1.5, perTemplate: { milky_way: 1.5, ngc_4414: 1.5 },
      about: "A sparkle point's sprite, pixels. Illustrative.",
    },
    {
      key: "sparkleblue", label: "sparkle blue", min: 0, max: 1.5, step: 0.01, unit: "", default: 0.7, perTemplate: { milky_way: 0.7, ngc_4414: 0.7 },
      about: "The sparkle's colour from white toward blue-white by this share. Illustrative.",
    },
  ],
  arrays: ARMS_ARRAYS,
  glsl: /* glsl */ `
  uniform sampler2D illArmsTex;
  uniform float illArmsOn;
  uniform vec3 illArmsBlue;
  uniform vec3 illArmsLavender;
  vec3 illArmsLight(vec2 rp) {
    if (illArmsOn < 0.5 || rp.x >= rHi) return vec3(1.0);
    vec4 w = illPolar(illArmsTex, rp);
    vec3 tone = mix(mix(vec3(1.0), illArmsLavender, w.a), illArmsBlue, w.g);
    return w.r * tone;
  }
  float illArmsYoung(vec2 rp) {
    if (illArmsOn < 0.5 || rp.x >= rHi) return 1.0;
    return illPolar(illArmsTex, rp).b;
  }
`,
  hooks: { youngGain: "illArmsYoung", light: "illArmsLight" },
  uniforms: (p: IllParams, context: IllContext) => {
    const tex = textureOf(armMapFor(p, context.frame));
    return {
      illArmsTex: tex,
      illArmsOn: tex ? 1 : 0,
      illArmsBlue: tint(ARM_BLUE, p.blue ?? 0),
      illArmsLavender: tint(INTER_LAVENDER, p.lavender ?? 0),
    };
  },
  layer: ArmsLayer,
};
