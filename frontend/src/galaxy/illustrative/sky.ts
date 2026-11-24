// The sky round the galaxy (S106, builder D): field stars and the sky's tint, as the goal photograph of NGC 4414 has
// them (its corners and margins: a sparse scatter of faint blue-white and white points, a few orange-red, a handful
// brighter with a soft glow, on a deep blue-black sky a little lighter and bluer about the disc). DISPLAY-ONLY
// STRUCTURE OF THE VIEWER'S OWN (the lead's ruling 12): nothing of the model places these stars or this light, and no
// published number, readout, tracer or preview reads them. Under the physical look nothing here runs (the layer is drawn
// only with an illustrative runtime); every control at 0 draws nothing at all (the Milky Way's default).
//
// The stars: foreground stars of our own Galaxy, so directions on the sky (a unit vector each, drawn at infinity: no
// parallax, they stay put on the sky as the view orbits and never sit inside the disc), from a fixed seed (never the
// time or the frame), not dimmed by the galaxy's dust (their own material, no dust term), passing through the bloom and
// the grade as the picture does. Their number is given per frame - how many fall in the template's frame at its lens -
// and the sphere carries that density all round (NGC 4414's 5-degree lens needs ~1700 sphere stars per frame star; the
// total is capped at MAX_SKY_STARS). One draw call, the buffers built once per shaping value and lens, never per frame.
//
// The tint: a uniform deep-blue floor over the whole frame (a screen quad) and a wide smooth blue halo about the disc,
// a soft additive sprite lying in the disc's plane centred on the galaxy (so it is the disc's inclined ellipse, the
// faint outer disc's haze; seen edge-on it thins away with the disc). No march sampler, no hook: the layer's own meshes.

import { createElement, lazy, Suspense } from "react";

import type { IllControl, IllFeature, IllLayerProps } from "./feature";

/** The most sphere stars drawn (one vertex each), whatever the lens: ~9 MB of buffers at most. */
export const MAX_SKY_STARS = 400_000;

/** mulberry32: a small seeded generator, the same sequence for the same seed on every machine. */
export function skyRng(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** The solid angle of a frame of vertical field `fovDeg` and aspect `aspect` (width / height), steradians. */
export function frameSolidAngle(fovDeg: number, aspect: number): number {
  const ty = Math.tan((fovDeg * Math.PI) / 360);
  const tx = ty * Math.max(aspect, 1e-6);
  // A rectangular pyramid of half-tangents tx, ty: 4 asin(sin(a/2) sin(b/2)), a and b the full apex angles.
  return 4 * Math.asin(Math.sin(Math.atan(tx)) * Math.sin(Math.atan(ty)));
}

/** How many sphere stars give `perFrame` in a frame of that field and aspect, capped. */
export function sphereCount(perFrame: number, fovDeg: number, aspect: number): number {
  if (!(perFrame > 0)) return 0;
  const n = Math.round((perFrame * 4 * Math.PI) / Math.max(frameSolidAngle(fovDeg, aspect), 1e-9));
  return Math.min(MAX_SKY_STARS, Math.max(1, n));
}

/** The stars' colours, unit luminance (Rec. 709) each before the weight: white, the blue-white end, the warm end. */
export const SKY_WHITE: readonly [number, number, number] = [1, 1, 1];
export const SKY_BLUE: readonly [number, number, number] = [0.72, 0.9, 1.35];
export const SKY_WARM: readonly [number, number, number] = [1.45, 0.82, 0.5];
/** The floor's and the halo's colours at full blue (each then normalised to unit luminance). */
export const FLOOR_BLUE: readonly [number, number, number] = [0.08, 0.05, 1];
export const HALO_BLUE: readonly [number, number, number] = [0.45, 0.6, 1];

const LUMA = [0.2126, 0.7152, 0.0722] as const;
const lum = (c: readonly number[]) => LUMA[0] * c[0] + LUMA[1] * c[1] + LUMA[2] * c[2];
/** White mixed toward `toward` by `share`, normalised to unit luminance. */
export function skyTint(toward: readonly [number, number, number], share: number): [number, number, number] {
  const c = toward.map((v) => 1 + (v - 1) * share);
  const l = lum(c);
  return c.map((v) => v / l) as [number, number, number];
}

export interface SkyShape {
  /** Sphere stars in all. */
  count: number;
  seed: number;
  /** The brightness law's index: weight = u^(-1/slope), from 1 to `range`; smaller has more bright stars. */
  slope: number;
  /** The brightest star's weight over the faintest's. */
  range: number;
  /** The share of warm (orange-red) stars. */
  warm: number;
  /** How far the others go from white toward blue-white (each drawn between, up to this). */
  blue: number;
}

export interface SkyStars {
  /** Unit directions, xyz per star. */
  direction: Float32Array;
  /** Colour times weight (unit luminance times the weight), rgb per star. */
  colour: Float32Array;
  /** Each star's weight, 1 to range. */
  weight: Float32Array;
}

/** A brightness from the power law: 1 to `range`, many faint, few bright. */
export function skyBrightness(u: number, slope: number, range: number): number {
  return Math.min(range, Math.pow(Math.max(1e-9, 1 - u), -1 / Math.max(0.1, slope)));
}

/** The stars: deterministic in the shape. Directions uniform on the sphere. */
export function buildSkyStars(s: SkyShape): SkyStars {
  const n = Math.max(0, Math.min(MAX_SKY_STARS, Math.floor(s.count)));
  const direction = new Float32Array(n * 3);
  const colour = new Float32Array(n * 3);
  const weight = new Float32Array(n);
  const next = skyRng(s.seed);
  const range = Math.max(1, s.range);
  for (let i = 0; i < n; i++) {
    const z = 2 * next() - 1;
    const a = 2 * Math.PI * next();
    const q = Math.sqrt(Math.max(0, 1 - z * z));
    direction[3 * i] = q * Math.cos(a);
    direction[3 * i + 1] = z;
    direction[3 * i + 2] = q * Math.sin(a);
    const w = skyBrightness(next(), s.slope, range);
    weight[i] = w;
    const warm = next() < s.warm;
    const c = warm ? skyTint(SKY_WARM, 0.5 + 0.5 * next()) : skyTint(SKY_BLUE, s.blue * next());
    for (let k = 0; k < 3; k++) colour[3 * i + k] = c[k] * w;
  }
  return { direction, colour, weight };
}

const CONTROLS: readonly IllControl[] = [
  {
    key: "stars", label: "field stars per frame", min: 0, max: 600, step: 1, unit: "", default: 0, perTemplate: { ngc_4414: 200 },
    about: "Foreground stars of our own Galaxy, fixed on the sky: how many fall in the template's frame at its lens (most of them faint). 0 none. Illustrative: no model star.",
  },
  {
    key: "bright", label: "field star brightness", min: 0.001, max: 2, step: 0.001, log: true, unit: "", default: 0.018, perTemplate: { ngc_4414: 0.018 },
    about: "The faintest field star's light (linear, summed over its pixels, before the grade). Illustrative.",
  },
  {
    key: "range", label: "field star spread", min: 1, max: 1000, step: 1, log: true, unit: "×", default: 200, perTemplate: { ngc_4414: 200 },
    about: "The brightest field star over the faintest. Illustrative.",
  },
  {
    key: "slope", label: "field star law", min: 0.2, max: 3, step: 0.01, unit: "", default: 0.8, perTemplate: { ngc_4414: 0.8 },
    about: "The brightness law's index: smaller has more bright stars, larger many faint and a handful bright. Illustrative.",
  },
  {
    key: "size", label: "field star size", min: 0.2, max: 3, step: 0.01, unit: "px", default: 0.55, perTemplate: { ngc_4414: 0.55 },
    about: "The faintest star's gaussian radius at a 1024-pixel frame; the brighter grow a little with their light. Illustrative.",
  },
  {
    key: "glow", label: "field star glow", min: 0, max: 1, step: 0.01, unit: "", default: 0.25, perTemplate: { ngc_4414: 0.25 },
    about: "The share of the brightest stars' light spread in a soft glow four times their size (none for the faint). Illustrative.",
  },
  {
    key: "warm", label: "warm field stars", min: 0, max: 1, step: 0.01, unit: "", default: 0.15, perTemplate: { ngc_4414: 0.15 },
    about: "The share of orange-red field stars; the rest between white and blue-white. Colour for appearance.",
  },
  {
    key: "blue", label: "field star blue", min: 0, max: 1, step: 0.01, unit: "", default: 0.7, perTemplate: { ngc_4414: 0.7 },
    about: "How far the other field stars go from white toward blue-white. Colour for appearance.",
  },
  {
    key: "seed", label: "field star seed", min: 0, max: 999, step: 1, unit: "", default: 1,
    about: "Another fixed scatter of the same stars. Illustrative.",
  },
  {
    key: "floor", label: "sky floor", min: 0, max: 0.05, step: 0.0001, unit: "", default: 0, perTemplate: { ngc_4414: 0.0003 },
    about: "A uniform deep-blue light over the whole frame (linear, before the grade): the photograph's sky is blue-black, not black. 0 black. Colour for appearance.",
  },
  {
    key: "floorblue", label: "sky floor blue", min: 0, max: 1, step: 0.01, unit: "", default: 1, perTemplate: { ngc_4414: 1 },
    about: "The floor's colour from grey (0) to deep blue (1). Colour for appearance.",
  },
  {
    key: "halo", label: "sky halo", min: 0, max: 0.2, step: 0.0005, unit: "", default: 0, perTemplate: { ngc_4414: 0.012 },
    about: "A wide smooth blue haze about the disc, in its plane (linear light at its centre, before the grade): the faint outer disc's glow on the sky. 0 none. Illustrative.",
  },
  {
    key: "haloradius", label: "sky halo radius", min: 1, max: 60, step: 0.1, unit: "kpc", default: 11, perTemplate: { ngc_4414: 11 },
    about: "The halo's gaussian radius in the disc's plane (its light at e^-1/2 there). Illustrative.",
  },
  {
    key: "haloblue", label: "sky halo blue", min: 0, max: 1, step: 0.01, unit: "", default: 1, perTemplate: { ngc_4414: 1 },
    about: "The halo's colour from grey (0) to blue (1). Colour for appearance.",
  },
];

// The e2e tools type-check this registry without JSX (e2e/tsconfig.json): the drawing is a .tsx they never load.
// @ts-ignore TS6142 under the e2e tools' compiler options only
const Layer = lazy(() => import("./SkyLayer"));
/** The sky's drawing, loaded apart from the registry. */
function SkyLayerLazy(props: IllLayerProps) {
  if (!skyDrawn(props.params)) return null;
  return createElement(Suspense, { fallback: null }, createElement(Layer, props));
}

/**
 * S110 (B2): the registry's handover angles (index.ts illGrazeAt, radians off the disc's axis: a pair or a vector) as
 * the halo's (SkyLayer.tsx: the halo fades with the sight line's grazing weight, exactly as drawn while it is 1);
 * (0, 0) - no handover, the halo as drawn - while unknown.
 */
export function grazePair(value: unknown): [number, number] {
  if (Array.isArray(value) && value.length >= 2) return [Number(value[0]) || 0, Number(value[1]) || 0];
  const v = value as { x?: unknown; y?: unknown } | null;
  if (v && typeof v.x === "number" && typeof v.y === "number") return [v.x, v.y];
  return [0, 0];
}

/** Whether the layer draws anything at these parameters (all off: nothing mounted, the frame as without it). */
export function skyDrawn(p: Readonly<Record<string, number>>): boolean {
  return (p.stars ?? 0) > 0 || (p.floor ?? 0) > 0 || (p.halo ?? 0) > 0;
}

export const sky: IllFeature = {
  id: "sky",
  label: "sky",
  about: "The sky round the galaxy: foreground field stars fixed on the sky (not dimmed by the galaxy's dust), a deep-blue sky floor and a wide blue haze about the disc. Display-only, of the viewer's own.",
  controls: CONTROLS,
  layer: SkyLayerLazy,
};
