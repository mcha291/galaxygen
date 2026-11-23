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
import { ILL_MAP, ILL_MAP_CHANNELS, memoOn } from "./feature";
import { barAngle } from "./lanesMap";
import { SKEL_CONTRAST_MAX, SKEL_MEAN_SAMPLES, skeletonMemo, skeletonOn, skeletonPlanes } from "./armsSkeleton";
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
});

/** What the share depends on (the rest of the shape is uniforms): the planes' memo key. */
const shareKey = (s: ArmShape): string =>
  JSON.stringify({ ...s, floor: 0, cap: 0, young: 0, width: 0 });

/** The arms' skeleton at the live parameters (S106): its planes in place of the contrast's under `skeleton`. */
export const armsSkeleton = skeletonMemo();

const skeletonPlanesOf = memoOn((sk: unknown, frame: unknown, wing: unknown) => {
  const f = frame as IllFrame | null;
  const s = sk as Skeleton | null;
  const pattern = (f?.arrays.pattern_density_contrast as ArrayLike<number> | undefined) ?? (f?.arrays.gas_density_contrast as ArrayLike<number> | undefined);
  if (!f || !s || !pattern) return null;
  const grid = gridOf(f.header, pattern.length);
  const star = (f.arrays.pattern_density_contrast as ArrayLike<number> | undefined) ?? null;
  const contrast = star ? { n: ringNormalise(star, grid.nR, grid.nPhi), nR: grid.nR, nPhi: grid.nPhi } : null;
  return { grid, ...skeletonPlanes(s, ILL_MAP.width, ILL_MAP.height, grid.rHi, wing as number, FLAG_RINGS / 16, contrast) };
});

const planesFor = (p: IllParams, frame: IllFrame | null) =>
  skeletonOn(p) ? skeletonPlanesOf(armsSkeleton(frame, p), frame, p.skelwing ?? 0.15) : planesOf(frame, shareKey(shapeOf(p, frame)));

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
      key: "strength", label: "arm strength", min: 0, max: 1.5, step: 0.01, unit: "×", default: 1, perTemplate: { milky_way: 1, ngc_4414: 0.5 },
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
      key: "floor", label: "inter-arm light", min: 0, max: 1, step: 0.01, unit: "", default: 0.45, perTemplate: { milky_way: 0.55, ngc_4414: 0.5 },
      about: "The disc's light between the arms as a share of a full ridge's (each ring's mean light is then kept): lower darkens the gaps; 1 no arm contrast. Illustrative.",
    },
    {
      key: "knee", label: "ridge knee", min: 0.2, max: 10, step: 0.1, unit: "", default: 3, perTemplate: { milky_way: 2, ngc_4414: 3 },
      about: "Where a ridge's brightening saturates, in units of its ring's mean sharpened contrast: higher keeps a strong arm brighter than a weak one, lower lights every arm alike. Illustrative.",
    },
    {
      key: "cap", label: "ridge cap", min: 1, max: 8, step: 0.1, unit: "×", default: 2.2, perTemplate: { milky_way: 2, ngc_4414: 2.5 },
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
      key: "barfade", label: "bar fade", min: 0, max: 3, step: 0.05, unit: "× bar", default: 1, perTemplate: { milky_way: 0.7, ngc_4414: 1 },
      about: "The arms' shaping starts at this multiple of the bar's half-length (the published bar_half_length), so the bar and the bulge are never brightened. Illustrative.",
    },
    {
      key: "inner", label: "inner start", min: 0, max: 10, step: 0.1, unit: "kpc", default: 2, perTemplate: { milky_way: 1, ngc_4414: 3 },
      about: "The arms' shaping starts no nearer the centre than this, kpc (an unbarred disc's start). Illustrative.",
    },
    {
      key: "fadewidth", label: "fade-in width", min: 0, max: 6, step: 0.1, unit: "kpc", default: 1, perTemplate: { milky_way: 0.5, ngc_4414: 2 },
      about: "Over how many kpc the arms' shaping fades in from its start. Illustrative.",
    },
    {
      key: "extend", label: "arms carried out", min: 0, max: 15, step: 0.5, unit: "kpc", default: 4, perTemplate: { milky_way: 1, ngc_4414: 1 },
      about: "How far past the ring where the model's arms fade out their pattern is carried outward along the arms' own measured winding, kpc, so the arms reach the disc's edge; 0 the model's end. Illustrative.",
    },
    {
      key: "blue", label: "arm blue", min: 0, max: 1.5, step: 0.01, unit: "", default: 0.4, perTemplate: { milky_way: 0.1, ngc_4414: 0.05 },
      about: "The arms' light tinted toward blue-white by this share. Illustrative.",
    },
    {
      key: "lavender", label: "inter-arm tint", min: -1.5, max: 1.5, step: 0.01, unit: "", default: 0.4, perTemplate: { milky_way: 0.6, ngc_4414: -0.6 },
      about: "The disc's light between the arms (outside the bar's fade) tinted toward lavender by this share; a negative share tints it warm instead. Illustrative.",
    },
    {
      key: "sparkle", label: "sparkle points", min: 0, max: 400000, step: 1000, unit: "", default: 20000, perTemplate: { milky_way: 80000, ngc_4414: 70000 },
      about: "How many small bright young-star points are scattered along the arms' ridges; 0 none. Illustrative.",
    },
    {
      key: "sparklegain", label: "sparkle brightness", min: 10, max: 1e7, step: 0.01, log: true, unit: "L☉", default: 300000, perTemplate: { milky_way: 80000, ngc_4414: 10000 },
      about: "The faintest sparkle point's light, L☉ over the white point (on the field's scale, with the exposure). Illustrative.",
    },
    {
      key: "sparklerange", label: "sparkle range", min: 1, max: 1000, step: 0.01, log: true, unit: "×", default: 15, perTemplate: { milky_way: 20, ngc_4414: 15 },
      about: "The brightest sparkle point over the faintest. Illustrative.",
    },
    {
      key: "sparkleslope", label: "sparkle slope", min: 0.3, max: 4, step: 0.05, unit: "", default: 1.4, perTemplate: { milky_way: 1.6, ngc_4414: 1.4 },
      about: "The brightness law's index: lower has more bright points, higher more faint. Illustrative.",
    },
    {
      key: "sparkleridge", label: "sparkle on ridge", min: 0.2, max: 6, step: 0.05, unit: "", default: 2, perTemplate: { milky_way: 1, ngc_4414: 1.2 },
      about: "The sparkle's density as this power of the arm share: higher keeps the points on the ridge and thins them faster toward the arm's edges. Illustrative.",
    },
    {
      key: "clump", label: "sparkle grouped", min: 0, max: 1, step: 0.01, unit: "", default: 0.6, perTemplate: { milky_way: 0.3, ngc_4414: 0.5 },
      about: "The share of sparkle points gathered into groups (OB associations), the rest single. Illustrative.",
    },
    {
      key: "groupsize", label: "group size", min: 10, max: 600, step: 5, unit: "pc", default: 120, perTemplate: { milky_way: 120, ngc_4414: 80 },
      about: "A sparkle group's gaussian radius, pc. Illustrative.",
    },
    {
      key: "members", label: "group members", min: 1, max: 60, step: 1, unit: "", default: 10, perTemplate: { milky_way: 6, ngc_4414: 6 },
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
      key: "sparklelift", label: "sparkle on weak arms", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0.12, ngc_4414: 0 },
      about: "Above 0, the sparkle's density read from the arms' ridge share over this level (saturating at 1), so a weak ridge carries as much grain as a strong one; 0 the S105 reading (the tone share). Illustrative (S106).",
    },
    {
      key: "sparkleavoid", label: "sparkle off the lanes", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1, ngc_4414: 0 },
      about: "The share of the sparkle kept off the dust lanes (the points are not under the lanes' veil, so a lane on an arm's crest is lost in its grain otherwise); 0 none. Illustrative (S106).",
    },
    {
      key: "sparklebig", label: "bright sparkle share", min: 0, max: 0.5, step: 0.005, unit: "", default: 0, perTemplate: { milky_way: 0.01, ngc_4414: 0 },
      about: "The brightest share of the sparkle points drawn on the larger sprite below, so the grain has sizes; 0 every point on the small sprite (S106). Illustrative.",
    },
    {
      key: "sparklebigsize", label: "bright sparkle size", min: 0.5, max: 8, step: 0.1, unit: "px", default: 3, perTemplate: { milky_way: 1.6, ngc_4414: 3 },
      about: "The bright sparkle points' sprite, pixels (S106). Illustrative.",
    },
    {
      key: "sparklefall", label: "sparkle falloff", min: 0, max: 10, step: 0.1, unit: "× h", default: 2, perTemplate: { milky_way: 2, ngc_4414: 3 },
      about: "The sparkle's brightness falls outward as exp(-R / (this times the published thin-disc scale length)) from the arms' start, as the disc's own light does; 0 no falloff. Illustrative.",
    },
    {
      key: "sparkleedge", label: "sparkle edge", min: 2, max: 30, step: 0.5, unit: "kpc", default: 16, perTemplate: { milky_way: 19, ngc_4414: 10 },
      about: "The outermost radius of the sparkle, kpc, its density tapered to nothing over the outer 30 % (so no lone points stand beyond the fading disc). Illustrative.",
    },
    {
      key: "sparkleblue", label: "sparkle blue", min: 0, max: 1.5, step: 0.01, unit: "", default: 0.7, perTemplate: { milky_way: 0.15, ngc_4414: 0.15 },
      about: "The sparkle's colour from white toward blue-white by this share. Illustrative.",
    },
    {
      key: "skeleton", label: "arms on the skeleton", min: 0, max: 1, step: 1, unit: "", default: 0, perTemplate: { milky_way: 1, ngc_4414: 0 },
      about: "1: the arms' glow, grain and lanes drawn on one skeleton of continuous ridges (log spirals from the bar's ends at the arm pieces' pitch, carried to the disc's edge, with lesser arms and spurs of the viewer's own); 0: the model's contrast ridges as S105 drew them. Illustrative (S106).",
    },
    {
      key: "skellesser", label: "lesser arms", min: 0, max: 4, step: 1, unit: "", default: 2,
      about: "How many lesser arms the skeleton draws between the two major arms (each nudged to the arm pieces' strongest phase near midway). Illustrative (S106).",
    },
    {
      key: "skelspurs", label: "spurs", min: 0, max: 12, step: 1, unit: "", default: 4,
      about: "How many short spurs leave the skeleton's arms on their outer sides, more open than the arm. Illustrative (S106).",
    },
    {
      key: "skelpitch", label: "skeleton pitch", min: 0.3, max: 2, step: 0.01, unit: "×", default: 1, perTemplate: { milky_way: 1.0},
      about: "A multiplier on the arm pieces' pitch (their length-weighted median) for the skeleton's winding: below 1 more turns before the edge. Illustrative (S106).",
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
      key: "skelwidth", label: "ridge width", min: 0.1, max: 3, step: 0.01, unit: "kpc", default: 0.6, perTemplate: { milky_way: 0.45},
      about: "A skeleton ridge's full width at half maximum, kpc (the lesser arms 0.85 of it, the spurs 0.7). Illustrative (S106).",
    },
    {
      key: "skelouter", label: "arms' reach", min: 4, max: 30, step: 0.5, unit: "kpc", default: 18, perTemplate: { milky_way: 17.5},
      about: "Where the skeleton's major arms end, kpc (the lesser arms a little inside): the winding's extent. Illustrative (S106).",
    },
    {
      key: "skelfade", label: "outer fade", min: 0.02, max: 0.9, step: 0.01, unit: "", default: 0.3, perTemplate: { milky_way: 0.2 },
      about: "The outer share of each arm's length (in ln R) over which it fades and breaks into flecks. Illustrative (S106).",
    },
    {
      key: "skelstart", label: "arms' start", min: 0.3, max: 2, step: 0.01, unit: "× bar", default: 1,
      about: "Where the major arms leave the bar, times its published half-length (kpc without a bar). Illustrative (S106).",
    },
    {
      key: "skellesserstart", label: "lesser start", min: 1, max: 3, step: 0.01, unit: "×", default: 1.25,
      about: "Where the lesser arms start, times the majors' start. Illustrative (S106).",
    },
    {
      key: "skellevel", label: "lesser strength", min: 0, max: 1, step: 0.01, unit: "", default: 0.75,
      about: "The lesser arms' strength against the majors' (glow, grain and lanes alike). Illustrative (S106).",
    },
    {
      key: "skelwing", label: "glow wing", min: 0, max: 0.6, step: 0.01, unit: "", default: 0.15,
      about: "A faint wing three ridge widths wide under each ridge's glow, this share of it. Illustrative (S106).",
    },
    {
      key: "skeltail", label: "grain tail", min: 0, max: 0.5, step: 0.005, unit: "", default: 0.05,
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
      key: "skelseed", label: "skeleton seed", min: 0, max: 999, step: 1, unit: "", default: 11,
      about: "The seed of the skeleton's drift, kinks, spurs and breaks: another number, another drawing. Illustrative (S106).",
    },
    {
      key: "barglow", label: "bar light", min: 0.3, max: 4, step: 0.01, unit: "×", default: 1, perTemplate: { milky_way: 2.6, ngc_4414: 1 },
      about: "The disc's starlight inside the bar's ellipse (the published half-length and axis ratio, the angle the lanes read) multiplied, so the bar stands out of the inner disc as a distinct ellipse; 1 none. Illustrative (S105).",
    },
    {
      key: "barwarm", label: "bar cream", min: 0, max: 1.5, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0.8, ngc_4414: 0 },
      about: "The starlight inside the bar's ellipse tinted toward cream by this share; 0 none. Colour for appearance (S105).",
    },
    {
      key: "barsize", label: "bar ellipse size", min: 0.3, max: 2, step: 0.01, unit: "× bar", default: 1, perTemplate: { milky_way: 1.0, ngc_4414: 1 },
      about: "The ellipse of the bar light and cream, as a multiple of the published bar (the light and cream falling from the centre as exp(-1.6 e^2), e the ellipse radius in its units: a fifth at its edge). Illustrative (S105).",
    },
    {
      key: "bardim", label: "around the bar", min: 0, max: 0.9, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0.3, ngc_4414: 0 },
      about: "The inner disc's starlight about the bar (inside 1.6 of its scaled half-length, outside its ellipse) dimmed by this share, so the bar stands on a darker ground; 0 none. Illustrative (S105).",
    },
    {
      key: "barcool", label: "ground blue", min: 0, max: 1.5, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0.6, ngc_4414: 0 },
      about: "The same ground about the bar tinted toward a slate blue by this share, so the bar stands on blue, not on the old light's khaki; 0 none. Colour for appearance (S105).",
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
  vec3 illArmsBarLight(vec2 rp) {
    if (illArmsBarOn < 0.5) return vec3(1.0);
    float x = rp.x * cos(rp.y);
    float y = rp.x * sin(rp.y);
    float X = x * cos(illArmsBar.z) + y * sin(illArmsBar.z);
    float Y = y * cos(illArmsBar.z) - x * sin(illArmsBar.z);
    float e = length(vec2(X / illArmsBar.x, Y / (illArmsBar.x * illArmsBar.y)));
    float w = exp(-1.6 * e * e);
    float d = (1.0 - w) * (1.0 - smoothstep(illArmsBar.x, 1.6 * illArmsBar.x, rp.x));
    return mix(vec3(1.0), illArmsBar.w * illArmsBarTint, w) * mix(vec3(1.0), illArmsBarGround, d);
  }
  // S106 (B3): on the skeleton (illArmsSkel), A carries the model's own star contrast and the ring means come from
  // illArmsSkelMean; the model's arm light is divided out by its power illArmsFlat, faded in as the shaping is.
  uniform float illArmsSkel;
  uniform float illArmsFlat;
  uniform float illArmsSkelMean[${SKEL_MEAN_SAMPLES}];
  float illArmsSkelMeanAt(float r) {
    float x = clamp(r / rHi * ${SKEL_MEAN_SAMPLES.toFixed(1)} - 0.5, 0.0, ${(SKEL_MEAN_SAMPLES - 1).toFixed(1)});
    int i = int(floor(x));
    int j = min(i + 1, ${SKEL_MEAN_SAMPLES - 1});
    return mix(illArmsSkelMean[i], illArmsSkelMean[j], x - float(i));
  }
  float illArmsMeanOf(vec4 w, float r) { return illArmsSkel > 0.5 ? illArmsSkelMeanAt(r) : w.a * illArmsMeanMax; }
  float illArmsFlatOf(vec4 w, float fa) {
    if (illArmsSkel < 0.5 || illArmsFlat <= 0.0) return 1.0;
    return mix(1.0, pow(max(w.a * ${SKEL_CONTRAST_MAX.toFixed(2)}, 0.25), -illArmsFlat), fa);
  }
  vec3 illArmsShaped(vec2 rp) {
    if (illArmsOn < 0.5 || rp.x >= rHi) return vec3(1.0);
    vec4 w = illMap(rp);
    float s = w.b * w.b;
    float m = illArmsMeanOf(w, rp.x);
    float f = illArmsFade(rp.x);
    float fa = min(1.0, f);
    float light = max(0.0, 1.0 + (illArmsRing(s, m, illArmsFloor, illArmsCap) - 1.0) * f) * illArmsFlatOf(w, fa);
    float g = fa * smoothstep(0.25, 0.9, s) * illArmsFlag(rp.x);
    vec3 tone = mix(mix(vec3(1.0), illArmsLavender, fa), illArmsBlue, g);
    return light * tone;
  }
  vec3 illArmsLight(vec2 rp) { return illArmsShaped(rp) * illArmsBarLight(rp); }
  float illArmsYoung(vec2 rp) {
    if (illArmsOn < 0.5 || rp.x >= rHi) return 1.0;
    vec4 w = illMap(rp);
    float f = illArmsFade(rp.x);
    return max(0.0, 1.0 + (illArmsRing(w.b * w.b, illArmsMeanOf(w, rp.x), illArmsYoungFloor, ${YOUNG_CAP.toFixed(1)}) - 1.0) * f) * illArmsFlatOf(w, min(1.0, f));
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
    const planes = planesFor(p, context.frame);
    const shape = shapeOf(p, context.frame);
    return {
      illArmsOn: planes ? 1 : 0,
      illArmsBlue: tint(ARM_BLUE, p.blue ?? 0),
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
      illArmsSkel: planes && "ringMean" in planes ? 1 : 0,
      illArmsFlat: p.skelflat ?? 0,
      illArmsSkelMean: planes && "ringMean" in planes ? planes.ringMean : SKEL_MEAN_ZERO,
      ...barUniforms(p, context.frame),
    };
  },
  layer: ArmsLayer,
};

const SKEL_MEAN_ZERO: number[] = new Array<number>(SKEL_MEAN_SAMPLES).fill(0);

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
    illArmsBar: [(bar?.halfLength ?? 1) * size, bar?.axisRatio ?? 1, bar?.angle ?? 0, glow] as [number, number, number, number],
    illArmsBarTint: tint(BAR_CREAM, warm),
    illArmsBarGround: tint(BAR_GROUND, cool).map((v) => v * (1 - dim)) as [number, number, number],
  };
}

/** The inter-arm tint: toward lavender for a positive share, toward warm for a negative one (unit mean). */
export const interTint = (share: number): [number, number, number] => (share >= 0 ? tint(INTER_LAVENDER, share) : tint(INTER_WARM, -share));
