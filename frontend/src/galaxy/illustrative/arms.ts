// The arms (BUILD_VIII row 108, S108): the arms made to stand out of the disc under the illustrative look, and their
// sparkle. Display-only, of the illustrative look's own (D275).
//
// The weight (armsField.ts): the model's published arm contrast (pattern_density_contrast blended with
// gas_density_contrast), each ring over its mean, evened across radii, raised to a power and floored between the arms,
// faded in outside the bar and carried past the model's arms' end along their own winding - built once per (arrays
// frame, shaping values) and handed to the march as two channels of the shared map (index.ts; B the ridge share, A its
// ring mean: armsField.ts armPlanes), the light, the young light, the tone and the fade made from them in GLSL with
// the floor, the caps, the start and the strength as uniforms. Its light hook (illArmsLight, the contract's
// `light`) multiplies all the starlight at the midplane point - the arms brighter, the disc between them dimmer, the
// ring's mean light kept - and tints it: the arms toward blue-white, the disc between them toward lavender. Its young
// hook (illArmsYoung) gathers the clustered young light onto the ridges with a power of its own.
//
// The sparkle (armsSparkle.ts, SparkleLayer.tsx): a layer of small bright blue-white points along the ridges, grouped
// as OB associations, from a seed of the viewer's own, drawn through FluxPoints (so the dust dims them as it dims
// the knots).
//
// S106 (the Milky Way's grain): the sparkle may be read off the ridge share itself, lifted so a weak ridge carries as
// much grain as a strong one (sparklelift), kept off the dust lanes (sparkleavoid: the lanes' veil darkens the march,
// not the points), given a sparse floor between the arms (sparklefloor) and drawn in two sprite sizes (sparklebig,
// sparklebigsize). Every new control's ngc_4414 default leaves that template's drawing as S105 left it.

import { createElement, lazy, Suspense } from "react";
import { FLAG_RINGS, YOUNG_CAP, barFade, armContrast, armMap, armPlanes, armShare, gridOf, ringNormalise, type ArmGrid, type ArmShape } from "./armsField";
import type { IllContext, IllFeature, IllFrame, IllLayerProps, IllParams } from "./feature";
import { ILL_MAP, ILL_MAP_CHANNELS, memoHeld, memoOn, wouldBuild } from "./feature";
import { barAngle } from "./lanesMap";
import { SKEL_CONTRAST_MAX, SKEL_MEAN_SAMPLES, contrastPlane, meanSamples, skeletonMemo, skeletonOn, skeletonPlanes } from "./armsSkeleton";
import type { Skeleton } from "./skeleton";

/** The /api/arrays names the arms read. */
export const ARMS_ARRAYS = [
  "bar_axis_ratio",
  "bar_half_length",
  "gas_density_contrast",
  "pattern_density_contrast",
  "thin_disc_scale_length",
  // S106 (the skeleton): the arm pieces, as the lanes ask them (one request for all features).
  "arm_piece_chain",
  "arm_piece_order",
  "arm_piece_start_radius",
  "arm_piece_start_azimuth",
  "arm_piece_pitch",
  "arm_piece_extent",
  "arm_piece_join",
] as const;

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
    knee: p.knee ?? 3,
    start: Math.max(p.inner ?? 2, barred ? (p.barfade ?? 1.1) * (bar as number) : 0),
    width: p.fadewidth ?? 1.5,
    extend: p.extend ?? 0,
    young: p.young ?? 0.2,
    lineMix: p.lines ?? 0.7,
    armWidth: p.armwidth ?? 0.8,
    fragment: p.fragment ?? 0,
    fragScale: p.fragscale ?? 1.5,
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
  const map = armMap(n, grid, shape, strength);
  // S106: the ridge share itself, faded as the map's G is but without its smoothstep (index j * nR + i), so the
  // sparkle can light a weak ridge as fully as a strong one (sparklelift).
  const { share, sd } = armShare(n, grid, shape);
  const raw = new Float32Array(grid.nR * grid.nPhi);
  for (let i = 0; i < grid.nR; i++) {
    const fa = Math.min(1, barFade((i + 0.5) * (grid.rHi / grid.nR), shape.start, shape.width) * strength);
    if (sd[i] <= 0.02 || fa <= 0) continue;
    for (let j = 0; j < grid.nPhi; j++) raw[j * grid.nR + i] = fa * share[i * grid.nPhi + j];
  }
  return { grid, map, raw };
});

/** The arm map for these parameters on this frame (the same object while neither changes). */
export function armMapFor(p: IllParams, frame: IllFrame | null): { grid: ArmGrid; map: Float32Array; raw: Float32Array } | null {
  return mapOf(frame, JSON.stringify(shapeOf(p, frame)), p.strength ?? 1);
}

/**
 * The arms' planes of the shared map (B the ridge share, A its ring mean; armsField.ts armPlanes) and the per-ring
 * tint flags, for a frame and the shaping values that make the share: null without the contrast. The floor, the cap,
 * the young floor, the start, the fade's width and the strength are uniforms (no rebuild).
 */
const planesOf = memoOn((frame: unknown, shapeJson: unknown) => {
  const f = frame as IllFrame | null;
  const pattern = (f?.arrays.pattern_density_contrast as ArrayLike<number> | undefined) ?? null;
  const gas = (f?.arrays.gas_density_contrast as ArrayLike<number> | undefined) ?? null;
  const any = pattern ?? gas;
  if (!f || !any) return null;
  const grid = gridOf(f.header, any.length);
  const shape = JSON.parse(shapeJson as string) as ArmShape;
  const { share, sd } = armShare(armContrast(pattern, gas, grid, shape), grid, shape);
  return { grid, ...armPlanes(share, sd, grid, ILL_MAP.width, ILL_MAP.height) };
}, "arms.planes");

/** What the share depends on (the rest of the shape is uniforms): the planes' memo key. */
const shareKey = (s: ArmShape): string =>
  JSON.stringify({ ...s, floor: 0, cap: 0, young: 0, width: 0 });

/** The arms' skeleton at the live parameters (S106): its planes in place of the contrast's under `skeleton`. */
export const armsSkeleton = skeletonMemo("arms.skeleton");

/**
 * S109 (A4): the model's star contrast for the skeleton's A plane, and that plane, per frame (it moves with no slider):
 * built once, not at every skeleton slider's rebuild (about 70 ms of it). Never handed out itself (skeletonPlanes copies
 * it), so a transfer of the map's planes cannot take it.
 */
const skelContrastOf = memoOn((frame: unknown) => {
  const f = frame as IllFrame | null;
  const star = (f?.arrays.pattern_density_contrast as ArrayLike<number> | undefined) ?? null;
  if (!f || !star) return null;
  const grid = gridOf(f.header, star.length);
  const contrast = { n: ringNormalise(star, grid.nR, grid.nPhi), nR: grid.nR, nPhi: grid.nPhi };
  return { ...contrast, plane: contrastPlane(contrast, ILL_MAP.width, ILL_MAP.height) };
});

const skeletonPlanesOf = memoOn((sk: unknown, frame: unknown, wing: unknown) => {
  const f = frame as IllFrame | null;
  const s = sk as Skeleton | null;
  const pattern = (f?.arrays.pattern_density_contrast as ArrayLike<number> | undefined) ?? (f?.arrays.gas_density_contrast as ArrayLike<number> | undefined);
  if (!f || !s || !pattern) return null;
  const grid = gridOf(f.header, pattern.length);
  const contrast = skelContrastOf(f);
  return { grid, ...skeletonPlanes(s, ILL_MAP.width, ILL_MAP.height, grid.rHi, wing as number, FLAG_RINGS / 16, contrast) };
}, "arms.skelPlanes");

/**
 * S107 (NGC2): the contrast's planes with the model's own star contrast in A in place of the share's ring mean (as the
 * skeleton carries it: armsSkeleton.ts contrastPlane), the ring means handed to the GLSL as illArmsSkelMean's samples -
 * so `flat` can divide the model's arm light (the march's starlight carries pattern_density_contrast: on a flocculent
 * template its long strokes along the flow) out of the disc without the skeleton. B, the flags and meanMax as planesOf.
 */
const flatPlanesOf = memoOn((frame: unknown, shapeJson: unknown) => {
  const f = frame as IllFrame | null;
  const pattern = (f?.arrays.pattern_density_contrast as ArrayLike<number> | undefined) ?? null;
  const gas = (f?.arrays.gas_density_contrast as ArrayLike<number> | undefined) ?? null;
  const any = pattern ?? gas;
  if (!f || !any) return null;
  const grid = gridOf(f.header, any.length);
  const shape = JSON.parse(shapeJson as string) as ArmShape;
  const { share, sd } = armShare(armContrast(pattern, gas, grid, shape), grid, shape);
  const planes = armPlanes(share, sd, grid, ILL_MAP.width, ILL_MAP.height);
  const ring = new Float64Array(grid.nR);
  for (let i = 0; i < grid.nR; i++) {
    let s = 0;
    for (let j = 0; j < grid.nPhi; j++) s += share[i * grid.nPhi + j];
    ring[i] = s / grid.nPhi;
  }
  const mean = pattern
    ? contrastPlane({ n: ringNormalise(pattern, grid.nR, grid.nPhi), nR: grid.nR, nPhi: grid.nPhi }, ILL_MAP.width, ILL_MAP.height)
    : new Uint8Array(ILL_MAP.width * ILL_MAP.height).fill(Math.round(255 / SKEL_CONTRAST_MAX));
  return { grid, share: planes.share, mean, meanMax: planes.meanMax, flags: planes.flags, ringMean: meanSamples(ring, grid.nR) };
}, "arms.flatPlanes");

/** Whether the model's own arm light is divided out off the skeleton (`flat` above 0). */
const flatOn = (p: IllParams): boolean => !skeletonOn(p) && (p.flat ?? 0) > 0;

const planesFor = (p: IllParams, frame: IllFrame | null) =>
  skeletonOn(p)
    ? skeletonPlanesOf(armsSkeleton(frame, p), frame, p.skelwing ?? 0.15)
    : flatOn(p)
      ? flatPlanesOf(frame, shareKey(shapeOf(p, frame)))
      : planesOf(frame, shareKey(shapeOf(p, frame)));

/**
 * S109 (A3): the planes the uniforms read (the ring means, meanMax). On the skeleton, while the map worker has not yet
 * answered for the live values (a slider dragged), the last planes held - a drag of a skeleton slider otherwise built the
 * whole band on the main thread inside the uniforms (a 1.2-1.9 s long task, the stall probe's "uniforms arms"); the map
 * itself is the worker's, and the uniforms follow it when it lands.
 */
function uniformPlanes(p: IllParams, frame: IllFrame | null) {
  if (skeletonOn(p) && wouldBuild(() => planesFor(p, frame))) {
    const held = memoHeld("arms.skelPlanes");
    if (held && held.inputs[1] === frame) return held.value as ReturnType<typeof planesFor>;
  }
  return planesFor(p, frame);
}

/**
 * The bar's ellipse in the disc (S105, tuner M): its half-length and axis ratio as published, its angle read off
 * pattern_density_contrast as the lanes read it (lanesMap.ts barAngle); null without a bar.
 */
export const barOf = memoOn((frame: unknown) => {
  const f = frame as IllFrame | null;
  const a = f?.header.scalars.bar_half_length;
  const q = f?.header.scalars.bar_axis_ratio;
  const pattern = (f?.arrays.pattern_density_contrast as ArrayLike<number> | undefined) ?? null;
  if (!f || !pattern || typeof a !== "number" || !(a > 0)) return null;
  const grid = gridOf(f.header, pattern.length);
  const angle = barAngle(pattern, grid.nR, grid.nPhi, grid.rHi, a);
  if (!Number.isFinite(angle)) return null;
  return { halfLength: a, axisRatio: typeof q === "number" && q > 0 ? q : 0.4, angle };
});

/** The bar's cream (unit mean at full share). */
export const BAR_CREAM: readonly [number, number, number] = [1.16, 1.0, 0.72];
/** The ground about the bar: a slate blue, less green than the arms' blue-white (unit mean at full share). */
export const BAR_GROUND: readonly [number, number, number] = [0.84, 0.9, 1.26];

/** A tint of unit mean: white mixed toward `toward` by `share`. */
export function tint(toward: readonly [number, number, number], share: number): [number, number, number] {
  const c = toward.map((v) => 1 + (v - 1) * share) as [number, number, number];
  const mean = (c[0] + c[1] + c[2]) / 3;
  return c.map((v) => v / mean) as [number, number, number];
}

/** The arms' blue-white and the disc's lavender, before the share (unit mean at full share). */
export const ARM_BLUE: readonly [number, number, number] = [0.8, 1.04, 1.16];
/** S107: the arms' cyan-teal (the goal's arm light: greener than ARM_BLUE), mixed into it by the `cyan` share. */
export const ARM_CYAN: readonly [number, number, number] = [0.68, 1.12, 1.2];
/** The arms' tint target at a cyan share (ARM_BLUE at 0). */
export const armTarget = (cyan: number): [number, number, number] => ARM_BLUE.map((v, k) => v + (ARM_CYAN[k] - v) * Math.min(1, Math.max(0, cyan))) as [number, number, number];
export const INTER_LAVENDER: readonly [number, number, number] = [1.06, 0.9, 1.04];
/** The disc's warm tint between the arms (a negative lavender share), for a flocculent disc's warm inner light. */
export const INTER_WARM: readonly [number, number, number] = [1.12, 1.0, 0.82];

// The e2e tools type-check this registry without JSX (e2e/tsconfig.json): the drawing is a .tsx they never load.
// @ts-ignore TS6142 under the e2e tools' compiler options only
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
      key: "strength", label: "arm strength", min: 0, max: 1.5, step: 0.01, unit: "×", default: 1, perTemplate: { milky_way: 1.4, ngc_4414: 0.5 },
      about: "How much of the arms' shaping is applied to the starlight: 0 the disc as the model lights it, 1 the full shaping below. Illustrative.",
    },
    {
      key: "gasmix", label: "gas in the arms", min: 0, max: 1, step: 0.01, unit: "", default: 0.2, perTemplate: { milky_way: 0.15, ngc_4414: 0.8 },
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
      key: "floor", label: "inter-arm light", min: 0, max: 1, step: 0.01, unit: "", default: 0.45, perTemplate: { milky_way: 0.6, ngc_4414: 0.5 },
      about: "The disc's light between the arms as a share of a full ridge's (each ring's mean light is then kept): lower darkens the gaps; 1 no arm contrast. Illustrative.",
    },
    {
      key: "knee", label: "ridge knee", min: 0.2, max: 10, step: 0.1, unit: "", default: 3, perTemplate: { milky_way: 2, ngc_4414: 3 },
      about: "Where a ridge's brightening saturates, in units of its ring's mean sharpened contrast: higher keeps a strong arm brighter than a weak one, lower lights every arm alike. Illustrative.",
    },
    {
      key: "cap", label: "ridge cap", min: 1, max: 8, step: 0.1, unit: "×", default: 2.2, perTemplate: { milky_way: 1.6, ngc_4414: 2.5 },
      about: "The most a ridge's light is multiplied. Illustrative.",
    },
    {
      key: "young", label: "young between arms", min: 0, max: 1, step: 0.01, unit: "", default: 0.1, perTemplate: { milky_way: 0, ngc_4414: 0.15 },
      about: "The clustered young light between the arms as a share of a full ridge's (its ring mean kept): lower gathers it onto the ridges; 1 leaves it as the model places it. Illustrative.",
    },
    {
      key: "lines", label: "ridge lines", min: 0, max: 1, step: 0.01, unit: "", default: 1, perTemplate: { milky_way: 1, ngc_4414: 1 },
      about: "The share of the arms drawn as narrow lines along the contrast's ridges (of the width below), the rest the sharpened contrast's own breadth. Illustrative.",
    },
    {
      key: "armwidth", label: "arm width", min: 0.1, max: 4, step: 0.05, unit: "kpc", default: 0.6, perTemplate: { milky_way: 0.55, ngc_4414: 0.5 },
      about: "The ridge lines' full width at half maximum across the arm, kpc (the model's own ridges are 1.2-2.3 kpc wide). Illustrative.",
    },
    {
      key: "fragment", label: "arm breaks", min: 0, max: 0.9, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0.15, ngc_4414: 0.25 },
      about: "About this share of each ridge line's length broken away into gaps by a fixed noise of the viewer's own, so the arms read as fragments (a flocculent disc); 0 whole arms. Illustrative.",
    },
    {
      key: "fragscale", label: "break scale", min: 0.2, max: 6, step: 0.1, unit: "kpc", default: 1.5, perTemplate: { milky_way: 2, ngc_4414: 0.8 },
      about: "The size of the breaks and fragments along the arms, kpc. Illustrative.",
    },
    {
      key: "barfade", label: "bar fade", min: 0, max: 3, step: 0.05, unit: "× bar", default: 1, perTemplate: { milky_way: 0.3, ngc_4414: 1 },
      about: "The arms' shaping starts at this multiple of the bar's half-length (the published bar_half_length), so the bar and the bulge are never brightened. Illustrative.",
    },
    {
      key: "inner", label: "inner start", min: 0, max: 10, step: 0.1, unit: "kpc", default: 2, perTemplate: { milky_way: 1, ngc_4414: 3 },
      about: "The arms' shaping starts no nearer the centre than this, kpc (an unbarred disc's start). Illustrative.",
    },
    {
      key: "fadewidth", label: "fade-in width", min: 0, max: 6, step: 0.1, unit: "kpc", default: 1, perTemplate: { milky_way: 2.5, ngc_4414: 2 },
      about: "Over how many kpc the arms' shaping fades in from its start. Illustrative.",
    },
    {
      key: "extend", label: "arms carried out", min: 0, max: 15, step: 0.5, unit: "kpc", default: 4, perTemplate: { milky_way: 1, ngc_4414: 1 },
      about: "How far past the ring where the model's arms fade out their pattern is carried outward along the arms' own measured winding, kpc, so the arms reach the disc's edge; 0 the model's end. Illustrative.",
    },
    {
      key: "blue", label: "arm blue", min: 0, max: 1.5, step: 0.01, unit: "", default: 0.4, perTemplate: { milky_way: 0.7, ngc_4414: 0.05 },
      about: "The arms' light tinted toward blue-white by this share. Illustrative.",
    },
    {
      key: "cyan", label: "arm cyan", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0.3 },
      about: "The arms' tint and the sparkle's colour turned from blue-white toward cyan-teal by this share; 0 the blue-white. Colour for appearance (S107).",
    },
    {
      key: "lavender", label: "inter-arm tint", min: -1.5, max: 1.5, step: 0.01, unit: "", default: 0.4, perTemplate: { milky_way: 0.6, ngc_4414: -0.6 },
      about: "The disc's light between the arms (outside the bar's fade) tinted toward lavender by this share; a negative share tints it warm instead. Illustrative.",
    },
    {
      key: "sparkle", label: "sparkle points", min: 0, max: 400000, step: 1000, unit: "", default: 20000, perTemplate: { milky_way: 400000, ngc_4414: 70000 },
      about: "How many small bright young-star points are scattered along the arms' ridges; 0 none. Illustrative.",
    },
    {
      key: "sparklegain", label: "sparkle brightness", min: 10, max: 1e7, step: 0.01, log: true, unit: "L☉", default: 300000, perTemplate: { milky_way: 40000, ngc_4414: 10000 },
      about: "The faintest sparkle point's light, L☉ over the white point (on the field's scale, with the exposure). Illustrative.",
    },
    {
      key: "sparklerange", label: "sparkle range", min: 1, max: 1000, step: 0.01, log: true, unit: "×", default: 15, perTemplate: { milky_way: 200, ngc_4414: 15 },
      about: "The brightest sparkle point over the faintest. Illustrative.",
    },
    {
      key: "sparkleslope", label: "sparkle slope", min: 0.3, max: 4, step: 0.05, unit: "", default: 1.4, perTemplate: { milky_way: 1.3, ngc_4414: 1.4 },
      about: "The brightness law's index: lower has more bright points, higher more faint. Illustrative.",
    },
    {
      key: "sparkleridge", label: "sparkle on ridge", min: 0.2, max: 6, step: 0.05, unit: "", default: 2, perTemplate: { milky_way: 2, ngc_4414: 1.2 },
      about: "The sparkle's density as this power of the arm share: higher keeps the points on the ridge and thins them faster toward the arm's edges. Illustrative.",
    },
    {
      key: "clump", label: "sparkle grouped", min: 0, max: 1, step: 0.01, unit: "", default: 0.6, perTemplate: { milky_way: 0.2, ngc_4414: 0.5 },
      about: "The share of sparkle points gathered into groups (OB associations), the rest single. Illustrative.",
    },
    {
      key: "groupsize", label: "group size", min: 10, max: 600, step: 5, unit: "pc", default: 120, perTemplate: { milky_way: 80, ngc_4414: 80 },
      about: "A sparkle group's gaussian radius, pc. Illustrative.",
    },
    {
      key: "members", label: "group members", min: 1, max: 60, step: 1, unit: "", default: 10, perTemplate: { milky_way: 10, ngc_4414: 6 },
      about: "A sparkle group's mean number of points. Illustrative.",
    },
    {
      key: "sparklesize", label: "sparkle size", min: 0.5, max: 4, step: 0.1, unit: "px", default: 1.5, perTemplate: { milky_way: 1, ngc_4414: 1.5 },
      about: "A sparkle point's sprite, pixels. Illustrative.",
    },
    {
      key: "sparklefloor", label: "sparkle between arms", min: 0, max: 1, step: 0.005, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 0 },
      about: "The sparkle's density between the arms as a share of a full ridge's, so a sparse grain of stars lies over the whole disc; 0 every point on the arms (S106). Illustrative.",
    },
    {
      key: "sparklelift", label: "sparkle on weak arms", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0.3, ngc_4414: 0 },
      about: "Above 0, the sparkle's density read from the arms' ridge share over this level (saturating at 1), so a weak ridge carries as much grain as a strong one; 0 the S105 reading (the tone share). Illustrative (S106).",
    },
    {
      key: "sparkleavoid", label: "sparkle off the lanes", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1, ngc_4414: 0 },
      about: "The share of the sparkle kept off the dust lanes (the points are not under the lanes' veil, so a lane on an arm's crest is lost in its grain otherwise); 0 none. Illustrative (S106).",
    },
    {
      key: "sparklebig", label: "bright sparkle share", min: 0, max: 0.5, step: 0.005, unit: "", default: 0, perTemplate: { milky_way: 0.06, ngc_4414: 0 },
      about: "The brightest share of the sparkle points drawn on the larger sprite below, so the grain has sizes; 0 every point on the small sprite (S106). Illustrative.",
    },
    {
      key: "sparklebigsize", label: "bright sparkle size", min: 0.5, max: 8, step: 0.1, unit: "px", default: 3, perTemplate: { milky_way: 1.6, ngc_4414: 3 },
      about: "The bright sparkle points' sprite, pixels (S106). Illustrative.",
    },
    {
      key: "sparklecap", label: "sparkle brightness cap", min: 0, max: 5000, step: 1, unit: "", default: 0, perTemplate: { milky_way: 10, ngc_4414: 0 },
      about: "The brightest a sparkle point may be drawn (its largest channel, in the frame's linear light before the bloom): up close the grain's points grow bright as 1 / distance^2 and the bloom spreads the brightest into soft round discs; capped they stay crisp points. 0 no cap (S108). Illustrative.",
    },
    {
      key: "sparklebar", label: "sparkle on the bar", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0.4},
      about: "On the skeleton, the sparkle's density over the drawn bar (the bar light's ellipse and profile) as a share of a ridge crest's, so the bar is grainy with stars; 0 none. Illustrative (S109).",
    },
    {
      key: "sparklebarcream", label: "bar grain cream", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1 },
      about: "The sparkle's points on the drawn bar (where the bar's grain above outweighs the arms') turned from the arms' blue-white toward the bar's cream by this share; 0 all blue-white. Colour for appearance (S109).",
    },
    {
      key: "sparklebunch", label: "sparkle bunching", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1, ngc_4414: 0 },
      about: "The sparkle's density modulated along the arms by a fixed smooth noise of the wavelength below (the viewer's own): bunches of points with thinner stretches between; 0 an even grain. Illustrative (S106).",
    },
    {
      key: "sparklebunchsize", label: "bunch wavelength", min: 50, max: 3000, step: 10, unit: "pc", default: 400, perTemplate: { milky_way: 1200 },
      about: "The bunching noise's wavelength, pc. Illustrative (S106).",
    },
    {
      key: "sparklegap", label: "sparkle gaps", min: 0, max: 0.9, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0.3 },
      about: "The grain gathered: where the bunching noise is below this level the arm holds no sparkle - clumps and short strings with empty stretches between, as the goal's grain; 0 no gaps. Illustrative (S110).",
    },
    {
      key: "sparklegapsoft", label: "gap softness", min: 0.005, max: 0.3, step: 0.005, unit: "", default: 0.06,
      about: "The gaps' soft step either side of their level, in the noise's units: small a clean clump edge, large a thinning. Illustrative (S110).",
    },
    {
      key: "sparklelav", label: "sparkle lavender", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1 },
      about: "The fine grain's colour from the sparkle's blue-white toward the goal's lavender-white by this share (its brightness kept); the bright share (the clumps' cores) keeps the blue-white. Illustrative (S110).",
    },
    {
      key: "sparklebunchbright", label: "bunch brightness", min: 0, max: 2, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1.2 },
      about: "The points in a bunch brighter (up to 1 + this at the noise's peak), those between dimmer; 0 none. Illustrative (S106).",
    },
    {
      key: "sparkledirect", label: "sparkle drawn directly", min: 0, max: 1, step: 1, unit: "", default: 0, perTemplate: { milky_way: 1 },
      about: "1: the sparkle's places drawn through an envelope of their density (the same law, other points, several times faster where the points keep to the arms); 0: by rejection over the whole disc. Illustrative (S107).",
    },
    {
      key: "sparkletable", label: "sparkle density table", min: 0, max: 1, step: 1, unit: "", default: 0, perTemplate: { milky_way: 1 },
      about: "1: the sparkle's density across the ridges read from a polar table (256 x 1024 corners, bilinear) built once per build, so many more points cost no more; 0: read exactly at every proposal. Illustrative (S110).",
    },
    {
      key: "sparklefield", label: "field stars", min: 0, max: 200000, step: 1000, unit: "", default: 0, perTemplate: { milky_way: 40000 },
      about: "This many faint points over the whole disc - between the arms and over the bar too - a sparse second tier of the grain, thinning outward with the disc and gone by the field's edge; 0 none. Illustrative (S110).",
    },
    {
      key: "sparklefieldscale", label: "field stars' scale", min: 0.5, max: 20, step: 0.1, unit: "kpc", default: 4,
      about: "The field stars' density falls outward as exp(-R / this). Illustrative (S110).",
    },
    {
      key: "sparklefieldedge", label: "field stars' edge", min: 2, max: 30, step: 0.5, unit: "kpc", default: 16,
      about: "The field stars taper to nothing from 0.6 of this radius to it, so none lie on the black sky. Illustrative (S110).",
    },
    {
      key: "sparklefielddim", label: "field stars' brightness", min: 0.01, max: 2, step: 0.01, unit: "×", default: 0.3, perTemplate: { milky_way: 0.3 },
      about: "A field star's brightness against the arms' faintest grain point's: below 1 a dimmer tier. Illustrative (S110).",
    },
    {
      key: "sparklefall", label: "sparkle falloff", min: 0, max: 10, step: 0.1, unit: "× h", default: 2, perTemplate: { milky_way: 1.6, ngc_4414: 3 },
      about: "The sparkle's brightness falls outward as exp(-R / (this times the published thin-disc scale length)) from the arms' start, as the disc's own light does; 0 no falloff. Illustrative.",
    },
    {
      key: "sparkleedge", label: "sparkle edge", min: 2, max: 30, step: 0.5, unit: "kpc", default: 16, perTemplate: { milky_way: 13.5, ngc_4414: 10 },
      about: "The outermost radius of the sparkle, kpc, its density tapered to nothing over the outer 30 % (so no lone points stand beyond the fading disc). Illustrative.",
    },
    {
      key: "sparkleblue", label: "sparkle blue", min: 0, max: 1.5, step: 0.01, unit: "", default: 0.7, perTemplate: { milky_way: 0.1, ngc_4414: 0.15 },
      about: "The sparkle's colour from white toward blue-white by this share. Illustrative.",
    },
    {
      key: "skeleton", label: "arms on the skeleton", min: 0, max: 1, step: 1, unit: "", default: 0, perTemplate: { milky_way: 1, ngc_4414: 0 },
      about: "1: the arms' glow, grain and lanes drawn on one skeleton of continuous ridges (log spirals from the bar's ends at the arm pieces' pitch, carried to the disc's edge, with lesser arms and spurs of the viewer's own); 0: the model's contrast ridges as S105 drew them. Illustrative (S106).",
    },
    {
      key: "skellesser", label: "lesser arms", min: 0, max: 4, step: 1, unit: "", default: 2, perTemplate: { milky_way: 2},
      about: "How many lesser arms the skeleton draws between the two major arms (each nudged to the arm pieces' strongest phase near midway). Illustrative (S106).",
    },
    {
      key: "skeleven", label: "even winding", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1 },
      about: "The lesser arms laid evenly through the gaps between the two major arms on every ring (one gap takes half of them rounded up, the other the rest, each at an even share of its gap, read off the majors' own crests), by this share; 0 each lesser on its own winding (they may bunch on one side). Illustrative (S107).",
    },
    {
      key: "skelnudge", label: "lesser nudge", min: 0, max: 60, step: 1, unit: "°", default: 35, perTemplate: { milky_way: 10 },
      about: "How far a lesser arm may be moved from its place between the majors toward the arm pieces' strongest phase, degrees of the spiral's phase. Illustrative (S107).",
    },
    {
      key: "skelspurs", label: "spurs", min: 0, max: 12, step: 1, unit: "", default: 4, perTemplate: { milky_way: 7 },
      about: "How many short spurs leave the skeleton's arms on their outer sides, more open than the arm. Illustrative (S106).",
    },
    {
      key: "skelpitch", label: "skeleton pitch", min: 0.3, max: 2, step: 0.01, unit: "×", default: 1, perTemplate: { milky_way: 0.75},
      about: "A multiplier on the arm pieces' pitch (their length-weighted median) for the skeleton's winding: below 1 more turns before the edge. Illustrative (S106).",
    },
    {
      key: "skelpitchmin", label: "pitch floor", min: 2, max: 30, step: 0.1, unit: "deg", default: 10,
      about: "The least pitch the skeleton winds at before the multiplier above (the pieces' median raised to it): a rerolled galaxy whose pieces are nearly circular is drawn as a spiral, not rings; above a galaxy's own median it opens that spiral (the Milky Way's own is 12.6). Illustrative (S108).",
    },
    {
      key: "skeldrift", label: "pitch drift", min: 0, max: 0.6, step: 0.01, unit: "", default: 0.15,
      about: "The skeleton's pitch drifts slowly along each arm by about this share (a seeded noise of the viewer's own). Illustrative (S106).",
    },
    {
      key: "skelkink", label: "kinks", min: 0, max: 1, step: 0.01, unit: "", default: 0.25,
      about: "Two or three short changes of pitch along each arm, this share of the pitch: slight kinks. Illustrative (S106).",
    },
    {
      key: "skelwidth", label: "ridge width", min: 0.1, max: 3, step: 0.01, unit: "kpc", default: 0.6, perTemplate: { milky_way: 0.75},
      about: "A skeleton ridge's full width at half maximum, kpc (the lesser arms 0.85 of it, the spurs 0.7). Illustrative (S106).",
    },
    {
      key: "skelouter", label: "arms' reach", min: 4, max: 30, step: 0.5, unit: "kpc", default: 18, perTemplate: { milky_way: 13.5},
      about: "Where the skeleton's major arms end, kpc (the lesser arms a little inside): the winding's extent. Illustrative (S106).",
    },
    {
      key: "skelfade", label: "outer fade", min: 0.02, max: 0.9, step: 0.01, unit: "", default: 0.3, perTemplate: { milky_way: 0.2},
      about: "The outer share of each arm's length (in ln R) over which it fades and breaks into flecks. Illustrative (S106).",
    },
    {
      key: "skelstart", label: "arms' start", min: 0.3, max: 2, step: 0.01, unit: "× bar", default: 1, perTemplate: { milky_way: 0.95},
      about: "Where the major arms leave the bar, times its published half-length (kpc without a bar). Illustrative (S106).",
    },
    {
      key: "skellesserstart", label: "lesser start", min: 1, max: 3, step: 0.01, unit: "×", default: 1.25, perTemplate: { milky_way: 1.25},
      about: "Where the lesser arms start, times the majors' start. Illustrative (S106).",
    },
    {
      key: "skellevel", label: "lesser strength", min: 0, max: 1, step: 0.01, unit: "", default: 0.75, perTemplate: { milky_way: 1},
      about: "The lesser arms' strength against the majors' (glow, grain and lanes alike). Illustrative (S106).",
    },
    {
      key: "skellesserwidth", label: "lesser width", min: 0.2, max: 1.5, step: 0.01, unit: "×", default: 0.85, perTemplate: { milky_way: 0.9},
      about: "The lesser arms' ridge width as a share of the majors' (glow, grain and lanes alike). Illustrative (S107).",
    },
    {
      key: "skellesserreach", label: "lesser reach", min: 0.3, max: 1.2, step: 0.01, unit: "×", default: 0.92,
      about: "Where the lesser arms end, as a share of the majors' reach: shorter lessers leave the outer disc to the two major arms. Illustrative (S107).",
    },
    {
      key: "skelpitchgrow", label: "pitch opening", min: 0, max: 1.5, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0.1},
      about: "The skeleton's pitch grows outward as (R / the arms' start) to this power, so successive windings separate instead of running round as rings; 0 a constant pitch. Illustrative (S107).",
    },
    {
      key: "skelopen", label: "leave the bar", min: -0.95, max: 3, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: -0.7},
      about: "The major arms' pitch at the bar's ends multiplied by 1 + this, easing back over the length below, so each major leaves its bar end at a clear angle; below 0 (S109) the majors hug the bar instead - they leave its ends at a lower pitch and run round it close to its ends before opening; 0 none. Illustrative (S107).",
    },
    {
      key: "skelopenturns", label: "leave-the-bar length", min: 0.05, max: 1.5, step: 0.005, unit: "turn", default: 0.175, perTemplate: { milky_way: 0.2},
      about: "Over how much of a turn (at the skeleton's base pitch) the majors' changed pitch at the bar's ends eases back (the slider above): longer keeps a hugging arm round the bar for longer. Illustrative (S109).",
    },
    {
      key: "skeloval", label: "oval round the bar", min: 0.3, max: 1, step: 0.01, unit: "", default: 1, perTemplate: { milky_way: 0.55},
      about: "Near the bar the whole skeleton (glow, grain, lanes, regions) squashed across the bar's axis to this share: the arms round the bar become an oval along it, through its ends and closer to its long sides; 1 none. The viewer's own drawing. Illustrative (S109).",
    },
    {
      key: "skelovalin", label: "oval out to", min: 0, max: 4, step: 0.05, unit: "× bar", default: 1.2, perTemplate: { milky_way: 1.1},
      about: "The squash above is full out to this many bar half-lengths (of the skeleton's radius)... Illustrative (S109).",
    },
    {
      key: "skelovalout", label: "oval gone at", min: 0.5, max: 6, step: 0.05, unit: "× bar", default: 2.5, perTemplate: { milky_way: 2.0},
      about: "...and gone from this many bar half-lengths on, smoothly between. Illustrative (S109).",
    },
    {
      key: "skelpatch", label: "patchy arms", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0.35},
      about: "Each arm's glow and grain modulated along it by a fixed noise of the viewer's own (the wavelength below): bright clumps and thin stretches; 0 an even arm. Illustrative (S107).",
    },
    {
      key: "skelpatchsize", label: "patch size", min: 0.1, max: 4, step: 0.05, unit: "kpc", default: 0.7, perTemplate: { milky_way: 0.3},
      about: "The arms' clumps' wavelength along the arm, kpc. Illustrative (S107).",
    },
    {
      key: "skelragged", label: "ragged edges", min: 0, max: 0.9, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0.3},
      about: "Each side of an arm's band widened or narrowed along it by a fixed noise by up to this share: uneven edges; 0 even. Illustrative (S107).",
    },
    {
      key: "skelraggedsize", label: "ragged wavelength", min: 0.05, max: 6, step: 0.05, unit: "kpc", default: 0.35, perTemplate: { milky_way: 2.5},
      about: "The ragged edges' wavelength along the arm, kpc: well above the band's width the edges swell and narrow; below it each swelling is a short lash off the arm. Illustrative (S109).",
    },
    {
      key: "skelmottle", label: "mottled arms", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1},
      about: "The arms' clumps (patchy arms above) read off a noise in both directions along and across the band, by this share: mottling inside a continuous band; 0 clumps along the arm only (each one spans the band). Illustrative (S109).",
    },
    {
      key: "skelfoot", label: "strength across the arm", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1},
      about: "The arm band's strength read at each point's nearest place on the crest by this share, the rest on the point's ring: read on the ring, a change of strength along the arm (its outer end, a break) is cut along the ring right across a broad band, a straight edge; 0 the ring's reading (the foot near the start only). Illustrative (S109).",
    },
    {
      key: "skelbreaks", label: "breaks at the ends", min: 0, max: 1, step: 0.01, unit: "", default: 1, perTemplate: { milky_way: 0},
      about: "The breaks and flecks at the arms' outer ends by this share; 0 each arm fades out whole. Illustrative (S109).",
    },
    {
      key: "skelwidthgrow", label: "width growth", min: -0.5, max: 1.5, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0.3},
      about: "The skeleton's ridge width grows outward as (R / 8 kpc) to this power (held within 0.4-2.5 of the ridge width), so the arms keep one share of their spacing, which grows outward; 0 one width throughout. Illustrative (S109).",
    },
    {
      key: "skelwing", label: "glow wing", min: 0, max: 0.6, step: 0.01, unit: "", default: 0.15, perTemplate: { milky_way: 0.05},
      about: "A faint wing three ridge widths wide under each ridge's glow, this share of it. Illustrative (S106).",
    },
    {
      key: "skeltail", label: "grain tail", min: 0, max: 0.5, step: 0.005, unit: "", default: 0.05, perTemplate: { milky_way: 0 },
      about: "The skeleton's grain: a sparse tail of points two ridge widths to either side, this share of the crest's density. Illustrative (S106).",
    },
    {
      key: "skelgrainfade", label: "grain fade", min: 0, max: 4, step: 0.05, unit: "", default: 1.5,
      about: "The skeleton's grain thins with the ridge's strength to this power (so it breaks up at the arms' outer ends). Illustrative (S106).",
    },
    {
      key: "skelflat", label: "model arms out", min: 0, max: 1.5, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1 },
      about: "On the skeleton, the model's own arm light (the published star contrast over its ring mean) divided out by this power, so the skeleton's arms are the only arms drawn; 0 the model's arms kept under them. Illustrative (S106).",
    },
    {
      key: "flat", label: "model streaks out", min: 0, max: 1.5, step: 0.01, unit: "", default: 0,
      about: "Off the skeleton, the model's own arm light (the published star contrast over its ring mean, which the disc's starlight carries: on a flocculent disc long faint strokes along the flow) divided out of all the starlight by this power, over the whole disc, so the old light is a smooth ring-wise even base; 0 the model's light as drawn. The arms' own ridges (strength) are drawn over it as before. Illustrative (S107).",
    },
    {
      key: "skelyoungin", label: "young inside the arms", min: 0, max: 1, step: 0.01, unit: "", default: 1, perTemplate: { milky_way: 0 },
      about: "On the skeleton, the model's clustered young light inside the arms' start (where the arms' shaping has not yet faded in: round the bar) kept by this share; 0 none - no blue smudges inside the first arm. Illustrative (S106, B4).",
    },
    {
      key: "skelyoungcut", label: "young on the crest", min: 0, max: 0.9, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0.85 },
      about: "On the skeleton, the model's clustered young light kept only where the arm band is above this level (smoothly over the next 0.4): the blue clumps on the crests, none in the haze between; 0 as the arms' shaping alone gives it. Illustrative (S106, B4).",
    },
    {
      key: "skellavin", label: "lavender inside the arms", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1 },
      about: "On the skeleton, the inter-arm tint carried inside the arms' start (round the bar) by this share, so the disc about the bar is lavender as between the arms, not the model's grey; 0 none. Colour for appearance (S106, B4).",
    },
    {
      key: "skelseed", label: "skeleton seed", min: 0, max: 999, step: 1, unit: "", default: 11, perTemplate: { milky_way: 23 },
      about: "The seed of the skeleton's drift, kinks, spurs and breaks: another number, another drawing. Illustrative (S106).",
    },
    {
      key: "barglow", label: "bar light", min: 0.3, max: 4, step: 0.01, unit: "×", default: 1, perTemplate: { milky_way: 2, ngc_4414: 1 },
      about: "The disc's starlight inside the bar's ellipse (the published half-length and axis ratio, the angle the lanes read) multiplied, so the bar stands out of the inner disc as a distinct ellipse; 1 none. Illustrative (S105).",
    },
    {
      key: "barwarm", label: "bar cream", min: 0, max: 1.5, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1.0, ngc_4414: 0 },
      about: "The starlight inside the bar's ellipse tinted toward cream by this share; 0 none. Colour for appearance (S105).",
    },
    {
      key: "barhold", label: "bar cream to its edge", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1 },
      about: "The bar's cream held out toward its ellipse's edge by this share, so its fading light keeps the bar's hue (mixed with the light alone the glow outlives the tint: a pale rim round the bar); 0 as S105 drew it. Colour for appearance (S109).",
    },
    {
      key: "barsize", label: "bar ellipse size", min: 0.3, max: 2, step: 0.01, unit: "× bar", default: 1, perTemplate: { milky_way: 0.7, ngc_4414: 1 },
      about: "The ellipse of the bar light and cream, as a multiple of the published bar (the light and cream falling from the centre as exp(-1.6 e^2), e the ellipse radius in its units: a fifth at its edge). Illustrative (S105).",
    },
    {
      key: "bardim", label: "around the bar", min: 0, max: 0.9, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 0 },
      about: "The inner disc's starlight about the bar (inside 1.6 of its scaled half-length, outside its ellipse) dimmed by this share, so the bar stands on a darker ground; 0 none. Illustrative (S105).",
    },
    {
      key: "barcool", label: "ground blue", min: 0, max: 1.5, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0.4, ngc_4414: 0 },
      about: "The same ground about the bar tinted toward a slate blue by this share, so the bar stands on blue, not on the old light's khaki; 0 none. Colour for appearance (S105).",
    },
    {
      key: "barsharp", label: "bar edge", min: 1, max: 8, step: 0.1, unit: "", default: 2, perTemplate: { milky_way: 5},
      about: "The bar light's profile across its ellipse as exp(-1.6 e^this): 2 the soft gaussian; higher a flatter body with a sharper edge. Illustrative (S106).",
    },
    {
      key: "barthin", label: "bar slimness", min: 0.3, max: 1.5, step: 0.01, unit: "× q", default: 1, perTemplate: { milky_way: 0.8},
      about: "The bar light's ellipse's axis ratio as a multiple of the published bar_axis_ratio: below 1 a slimmer drawn bar. Illustrative (S106).",
    },
    {
      key: "barcore", label: "bar core", min: 0, max: 6, step: 0.05, unit: "×", default: 0, perTemplate: { milky_way: 2 },
      about: "A brighter core at the bar's centre: the light there multiplied by 1 + this, falling as a gaussian of the radius below; 0 none. Illustrative (S106).",
    },
    {
      key: "barcoresize", label: "bar core size", min: 0.03, max: 0.6, step: 0.01, unit: "× bar", default: 0.15, perTemplate: { milky_way: 0.2 },
      about: "The bar core's gaussian radius, times the drawn bar's half-length. Illustrative (S106).",
    },
    {
      key: "skelhold", label: "haze inside the arms", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0.5},
      about: "On the skeleton, the disc inside the first arm dimmed as the disc between the arms is (the ring mean the light is kept by held inward from where the arms begin) by this share; 0 undimmed there - a pale disc round the bar ending in a circle where the arms start. Illustrative (S106).",
    },
    {
      key: "skelcore", label: "light inside the arms", min: 0.05, max: 1, step: 0.01, unit: "×", default: 1, perTemplate: { milky_way: 0.6},
      about: "On the skeleton, the inner disc's starlight round the bar (off the bar's ellipse) taken to this share, fully inside the radius below and smoothly less out to the next, so the ground about the bar is the disc's darkest; 1 none. Illustrative (S106).",
    },
    {
      key: "skelcoreblue", label: "inner slate", min: 0, max: 1.5, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1.1 },
      about: "The same inner zone (round the bar, off its ellipse, over the same ramp) tinted toward a slate blue by this share; 0 none. Colour for appearance (S106).",
    },
    {
      key: "skelcorein", label: "inner dark to", min: 0, max: 10, step: 0.1, unit: "kpc", default: 2, perTemplate: { milky_way: 0.3},
      about: "The inner disc's darkening (above) is full inside this radius, kpc. Illustrative (S106).",
    },
    {
      key: "skelcoreout", label: "inner dark ends", min: 0.5, max: 15, step: 0.1, unit: "kpc", default: 6, perTemplate: { milky_way: 1.2},
      about: "The inner disc's darkening has faded to nothing at this radius, kpc (a smooth ramp from the radius above). Illustrative (S106).",
    },
    {
      key: "skelcorebar", label: "inner dark in bar units", min: 0, max: 1, step: 1, unit: "", default: 0, perTemplate: { milky_way: 1 },
      about: "1: the two radii above are read as multiples of the published bar half-length (so the dark ground round the bar follows a rerolled bar's length); 0 kpc. Kpc without a bar. Illustrative (S109).",
    },
  ],
  arrays: ARMS_ARRAYS,
  // The shared map's B is sqrt(share), its A the share's ring mean over illArmsMeanMax (armsField.ts armPlanes); the
  // rest is armMap's arithmetic, line for line: the fade outside the bar from the radius, each ring's light kept by
  // dividing by its mean, the tone share only on rings of contrast (illArmsFlags, 16 rings to a float).
  glsl: /* glsl */ `
  uniform float illArmsOn;
  uniform vec3 illArmsBlue;
  uniform vec3 illArmsLavender;
  uniform float illArmsStrength;
  uniform float illArmsStart;
  uniform float illArmsWidth;
  uniform float illArmsFloor;
  uniform float illArmsYoungFloor;
  uniform float illArmsCap;
  uniform float illArmsMeanMax;
  uniform float illArmsRings;
  uniform float illArmsFlags[${FLAG_RINGS / 16}];
  float illArmsFade(float r) {
    float t = illArmsWidth > 0.0 ? clamp((r - illArmsStart) / illArmsWidth, 0.0, 1.0) : step(illArmsStart, r);
    return t * t * (3.0 - 2.0 * t) * illArmsStrength;
  }
  float illArmsFlag(float r) {
    int i = int(clamp(floor(r / rHi * illArmsRings), 0.0, illArmsRings - 1.0));
    if (i >= ${FLAG_RINGS}) return 1.0;
    return mod(floor(illArmsFlags[i / 16] / exp2(float(i - (i / 16) * 16))), 2.0);
  }
  float illArmsRing(float s, float m, float lo, float cap) {
    float mean = lo + (1.0 - lo) * m;
    return mean > 0.0 ? min(cap, (lo + (1.0 - lo) * s) / mean) : 1.0;
  }
  uniform float illArmsBarOn;
  uniform vec4 illArmsBar;
  uniform vec3 illArmsBarTint;
  uniform vec3 illArmsBarGround;
  // S106 (B5): the profile's power (2 the S105 gaussian; higher a flatter top and a sharper edge) and a core at the
  // centre (x its gain, y its radius in the ellipse's units).
  uniform float illArmsBarSharp;
  uniform vec2 illArmsBarCore;
  uniform float illArmsBarHold;
  // The ellipse radius e at rp, in the bar's (scaled) units.
  float illArmsBarE(vec2 rp) {
    float x = rp.x * cos(rp.y);
    float y = rp.x * sin(rp.y);
    float X = x * cos(illArmsBar.z) + y * sin(illArmsBar.z);
    float Y = y * cos(illArmsBar.z) - x * sin(illArmsBar.z);
    return length(vec2(X / illArmsBar.x, Y / (illArmsBar.x * illArmsBar.y)));
  }
  float illArmsBarProfile(float e) { return illArmsBarSharp == 2.0 ? exp(-1.6 * e * e) : exp(-1.6 * pow(e, illArmsBarSharp)); }
  // The bar ellipse's weight at rp (1 on the bar's axis, 0 far off it); 0 without a bar.
  float illArmsBarW(vec2 rp) {
    if (illArmsBar.x <= 0.0) return 0.0;
    return illArmsBarProfile(illArmsBarE(rp));
  }
  vec3 illArmsBarLight(vec2 rp) {
    if (illArmsBarOn < 0.5) return vec3(1.0);
    float e = illArmsBarE(rp);
    float w = illArmsBarProfile(e);
    float d = (1.0 - w) * (1.0 - smoothstep(illArmsBar.x, 1.6 * illArmsBar.x, rp.x));
    // S109 (illArmsBarHold > 0): the cream held out toward the bar's edge (its share w^(1 - 0.75 hold) of the way), so
    // the fading light keeps the bar's hue - mixed by w alone the glow outlived the tint: a white rim round the bar.
    vec3 lit = illArmsBarHold > 0.0
      ? mix(1.0, illArmsBar.w, w) * mix(vec3(1.0), illArmsBarTint, pow(w, 1.0 - 0.75 * illArmsBarHold)) * mix(vec3(1.0), illArmsBarGround, d)
      : mix(vec3(1.0), illArmsBar.w * illArmsBarTint, w) * mix(vec3(1.0), illArmsBarGround, d);
    if (illArmsBarCore.x > 0.0) {
      float c = rp.x / (illArmsBar.x * illArmsBarCore.y);
      lit *= 1.0 + illArmsBarCore.x * exp(-c * c);
    }
    return lit;
  }
  // S106 (B3): on the skeleton (illArmsSkel), A carries the model's own star contrast and the ring means come from
  // illArmsSkelMean; the model's arm light is divided out by its power illArmsFlat, faded in as the shaping is.
  uniform float illArmsSkel;
  uniform float illArmsFlat;
  uniform float illArmsYoungIn;
  uniform float illArmsYoungCut;
  uniform float illArmsLavIn;
  uniform vec3 illArmsCore;
  uniform float illArmsCoreOn;
  uniform vec3 illArmsCoreTint;
  uniform float illArmsSkelMean[${SKEL_MEAN_SAMPLES}];
  // (S106 B5: a Catmull-Rom cubic through the samples - a linear read kinks at each, a thin arc in the haze.)
  float illArmsSkelMeanAt(float r) {
    float x = clamp(r / rHi * ${SKEL_MEAN_SAMPLES.toFixed(1)} - 0.5, 0.0, ${(SKEL_MEAN_SAMPLES - 1).toFixed(1)});
    int i = int(floor(x));
    float t = x - float(i);
    float p0 = illArmsSkelMean[max(i - 1, 0)];
    float p1 = illArmsSkelMean[i];
    float p2 = illArmsSkelMean[min(i + 1, ${SKEL_MEAN_SAMPLES - 1})];
    float p3 = illArmsSkelMean[min(i + 2, ${SKEL_MEAN_SAMPLES - 1})];
    float v = 0.5 * (2.0 * p1 + (p2 - p0) * t + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t * t + (3.0 * p1 - p0 - 3.0 * p2 + p3) * t * t * t);
    return max(v, 0.0);
  }
  // S107 (NGC2): illArmsAc - A carries the model's contrast (the skeleton, or the contrast's planes under arms.flat);
  // illArmsFlatAll - off the skeleton, the division over the whole disc, not faded in with the arms' shaping.
  uniform float illArmsAc;
  uniform float illArmsFlatAll;
  float illArmsMeanOf(vec4 w, float r) { return illArmsAc > 0.5 ? illArmsSkelMeanAt(r) : w.a * illArmsMeanMax; }
  float illArmsFlatOf(vec4 w, float fa) {
    if (illArmsAc < 0.5 || illArmsFlat <= 0.0) return 1.0;
    return mix(1.0, pow(max(w.a * ${SKEL_CONTRAST_MAX.toFixed(2)}, 0.25), -illArmsFlat), max(fa, illArmsFlatAll));
  }
  // (Off the skeleton the light hook, which multiplies the young light too, divides it once: the young hook not again.)
  float illArmsFlatYoung(vec4 w, float fa) { return illArmsFlatAll > 0.5 ? 1.0 : illArmsFlatOf(w, fa); }
  vec3 illArmsShaped(vec2 rp) {
    if (illArmsOn < 0.5 || rp.x >= rHi) return vec3(1.0);
    vec4 w = illMap(rp);
    float s = w.b * w.b;
    float m = illArmsMeanOf(w, rp.x);
    float f = illArmsFade(rp.x);
    float fa = min(1.0, f);
    float light = max(0.0, 1.0 + (illArmsRing(s, m, illArmsFloor, illArmsCap) - 1.0) * f) * illArmsFlatOf(w, fa);
    // S106 (B5): on the skeleton, the inner disc's light taken to illArmsCore.x of itself, the full share inside
    // illArmsCore.y kpc and none from illArmsCore.z out (a smooth ramp: no circle), the bar's ellipse kept - so the
    // ground about the bar is the disc's darkest, not a pale disc.
    // illArmsCoreTint: the same zone tinted toward a slate blue.
    float coreW = 0.0;
    if (illArmsSkel > 0.5 && (illArmsCore.x != 1.0 || illArmsCoreOn > 0.5)) {
      coreW = (1.0 - illArmsBarW(rp)) * (1.0 - smoothstep(illArmsCore.y, illArmsCore.z, rp.x));
      light *= mix(1.0, illArmsCore.x, coreW);
    }
    float g = fa * smoothstep(0.25, 0.9, s) * illArmsFlag(rp.x);
    // Inside the arms' start the tint is carried off the bar itself (its cream is the bar light's).
    float lav = illArmsSkel > 0.5 ? max(fa, illArmsLavIn * (1.0 - illArmsBarW(rp))) : fa;
    vec3 tone = mix(mix(vec3(1.0), illArmsLavender, lav), illArmsBlue, g);
    if (illArmsCoreOn > 0.5) tone *= mix(vec3(1.0), illArmsCoreTint, coreW);
    return light * tone;
  }
  vec3 illArmsLight(vec2 rp) { return illArmsShaped(rp) * illArmsBarLight(rp); }
  float illArmsYoung(vec2 rp) {
    if (illArmsOn < 0.5 || rp.x >= rHi) return 1.0;
    vec4 w = illMap(rp);
    float f = illArmsFade(rp.x);
    if (illArmsSkel > 0.5 && illArmsYoungCut > 0.0) {
      float s = w.b * w.b;
      if (s < illArmsYoungCut) return 0.0;
      float ramp = smoothstep(illArmsYoungCut, min(1.0, illArmsYoungCut + 0.4), s);
      float inside = mix(illArmsYoungIn, 1.0, illArmsStrength > 0.0 ? min(1.0, f / illArmsStrength) : 1.0);
      return ramp * inside * max(0.0, 1.0 + (illArmsRing(s, illArmsMeanOf(w, rp.x), illArmsYoungFloor, ${YOUNG_CAP.toFixed(1)}) - 1.0) * f) * illArmsFlatYoung(w, min(1.0, f));
    }
    float inside = illArmsSkel > 0.5 ? mix(illArmsYoungIn, 1.0, illArmsStrength > 0.0 ? min(1.0, f / illArmsStrength) : 1.0) : 1.0;
    return inside * max(0.0, 1.0 + (illArmsRing(w.b * w.b, illArmsMeanOf(w, rp.x), illArmsYoungFloor, ${YOUNG_CAP.toFixed(1)}) - 1.0) * f) * illArmsFlatYoung(w, min(1.0, f));
  }
`,
  hooks: { youngGain: "illArmsYoung", light: "illArmsLight" },
  map: {
    channels: ILL_MAP_CHANNELS.arms,
    build: (p: IllParams, context: IllContext) => {
      const planes = planesFor(p, context.frame);
      return planes ? [planes.share, planes.mean] : [null, null];
    },
  },
  uniforms: (p: IllParams, context: IllContext) => {
    const planes = uniformPlanes(p, context.frame);
    const shape = shapeOf(p, context.frame);
    return {
      illArmsOn: planes ? 1 : 0,
      illArmsBlue: tint(armTarget(p.cyan ?? 0), p.blue ?? 0),
      illArmsLavender: interTint(p.lavender ?? 0),
      illArmsStrength: p.strength ?? 1,
      illArmsStart: shape.start,
      illArmsWidth: shape.width,
      illArmsFloor: shape.floor,
      illArmsYoungFloor: shape.young,
      illArmsCap: shape.cap,
      illArmsMeanMax: planes?.meanMax ?? 0,
      illArmsRings: planes?.grid.nR ?? 1,
      illArmsFlags: planes?.flags ?? new Array<number>(FLAG_RINGS / 16).fill(0),
      illArmsSkel: planes && skeletonOn(p) ? 1 : 0,
      illArmsAc: planes && "ringMean" in planes ? 1 : 0,
      illArmsFlatAll: planes && flatOn(p) ? 1 : 0,
      illArmsFlat: skeletonOn(p) ? (p.skelflat ?? 0) : (p.flat ?? 0),
      illArmsYoungIn: p.skelyoungin ?? 1,
      illArmsYoungCut: p.skelyoungcut ?? 0,
      illArmsLavIn: p.skellavin ?? 0,
      illArmsCoreOn: (p.skelcoreblue ?? 0) !== 0 ? 1 : 0,
      illArmsCoreTint: tint(BAR_GROUND, p.skelcoreblue ?? 0),
      illArmsCore: coreRadii(p, context.frame),
      illArmsSkelMean: planes && "ringMean" in planes ? heldMean(planes.ringMean as number[], skeletonOn(p) ? (p.skelhold ?? 0) : 0) : SKEL_MEAN_ZERO,
      ...barUniforms(p, context.frame),
    };
  },
  layer: ArmsLayer,
};

const SKEL_MEAN_ZERO: number[] = new Array<number>(SKEL_MEAN_SAMPLES).fill(0);

/**
 * The skeleton's ring means with the inner disc held (S106, B5): inside the first sample to reach half the largest
 * mean, each sample raised toward that sample's value by `hold` (0 the means as built). Inside the skeleton's start
 * the band is empty and its ring mean nothing, so the disc between the arms was dimmed only where arms are - a pale
 * disc round the bar ending in a circle where the arms begin; held, the haze inside the first arm is dimmed as the
 * haze between the arms is.
 */
export function heldMean(samples: readonly number[], hold: number): number[] {
  if (!(hold > 0) || samples.length === 0) return [...samples];
  const top = Math.max(...samples);
  const k = samples.findIndex((v) => v >= 0.5 * top);
  return samples.map((v, i) => (i < k && top > 0 ? v + (Math.max(v, samples[k]) - v) * Math.min(1, hold) : v));
}

/**
 * The inner disc's darkening (illArmsCore): its share, the radius it is full inside and the radius it has faded out at,
 * kpc - S109: under skelcorebar the two radii are multiples of the published bar half-length (kpc without a bar), the
 * outer at least the inner's plus a tenth of the unit (the S106 guard).
 */
export function coreRadii(p: IllParams, frame: IllFrame | null): [number, number, number] {
  const unit = (p.skelcorebar ?? 0) >= 0.5 ? (barOf(frame)?.halfLength ?? 1) : 1;
  const inn = (p.skelcorein ?? 2) * unit;
  return [p.skelcore ?? 1, inn, Math.max(inn + 0.1 * unit, (p.skelcoreout ?? 6) * unit)];
}

/** The bar light's uniforms: off (the light untouched) at a light of 1, no cream and no dimming, or without a bar. */
export function barUniforms(p: IllParams, frame: IllFrame | null) {
  const bar = barOf(frame);
  const glow = p.barglow ?? 1;
  const warm = p.barwarm ?? 0;
  const dim = p.bardim ?? 0;
  const cool = p.barcool ?? 0;
  const on = !!bar && (glow !== 1 || warm !== 0 || dim !== 0 || cool !== 0);
  const size = p.barsize ?? 1;
  return {
    illArmsBarOn: on ? 1 : 0,
    illArmsBar: [(bar?.halfLength ?? 1) * size, (bar?.axisRatio ?? 1) * (p.barthin ?? 1), bar?.angle ?? 0, glow] as [number, number, number, number],
    illArmsBarSharp: p.barsharp ?? 2,
    illArmsBarCore: [p.barcore ?? 0, p.barcoresize ?? 0.15] as [number, number],
    illArmsBarHold: p.barhold ?? 0,
    illArmsBarTint: tint(BAR_CREAM, warm),
    illArmsBarGround: tint(BAR_GROUND, cool).map((v) => v * (1 - dim)) as [number, number, number],
  };
}

/** The inter-arm tint: toward lavender for a positive share, toward warm for a negative one (unit mean). */
export const interTint = (share: number): [number, number, number] => (share >= 0 ? tint(INTER_LAVENDER, share) : tint(INTER_WARM, -share));
