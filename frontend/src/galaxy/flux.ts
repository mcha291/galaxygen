// The star-first mode's points on the field's own scale (S50, D208). No three.js here: the pure parts, tested.
//
// A point is a published flux, not a painted dot: its `response` through each filter over the white point's —
// the division every cell of the field gets — in L☉. The field's march integrates light per pc² across the line
// of sight, so a point drawn on that scale deposits, summed over its sprite's pixels, its flux over the area of
// sky one pixel covers at the point (Ω D², pc²), times the field's gain. Nothing here is a display choice but
// the sprite's shape and size, which belong to the instrument (psf.ts) and conserve the sum.
//
// The dust in front of a point (T20) is the march's own: each ring's published depth times its placement,
// through the dust's layer, along the segment from the point to the camera, each step taking the layer's
// exact column.

import { layerColumn } from "./regimes";

/**
 * Each point's light per display channel, L☉: its `response` (row-major, N × filters, /api/bright's and
 * /api/clusters') over the white point's. A missing number or a missing white point is no light (rule B9).
 * Null without a response or a usable white point: nothing is drawn on a guess.
 */
export function fluxOf(response: ArrayLike<number> | undefined, white: readonly (number | null)[] | null | undefined, count: number): Float32Array | null {
  if (!response || !white || white.length < 3) return null;
  const w = white.slice(0, 3).map(Number);
  if (!w.every((v) => Number.isFinite(v) && v > 0)) return null;
  const filters = white.length;
  if (response.length !== count * filters) return null;
  const out = new Float32Array(count * 3);
  for (let i = 0; i < count; i += 1) {
    for (let k = 0; k < 3; k += 1) {
      const v = Number(response[i * filters + k]) / w[k];
      out[3 * i + k] = Number.isFinite(v) && v > 0 ? v : 0;
    }
  }
  return out;
}

/**
 * The area of sky one drawing-buffer pixel covers at a point, pc² — the shader's, line for line. `depth` is the
 * point's distance along the view's axis and `distance` its distance from the camera, kpc; `pxPerUnit` is the
 * buffer's height over 2 tan(fov / 2), pixels per kpc at unit depth. The pixel's side at that depth, squared,
 * times the cosine of the point's angle off the axis: the pixel's solid angle times the squared distance.
 */
export function pixelArea(depth: number, distance: number, pxPerUnit: number): number {
  const side = (1000 * depth) / pxPerUnit;
  return (side * side * depth) / distance;
}

/**
 * What one sprite pixel is drawn at, per unit of the sprite's pattern there: the point's flux times the gain,
 * over the pixel's area of sky and over the pattern's sum across the sprite (its mean times its pixels), so the
 * sprite's pixels sum to flux × gain / area whatever its size and shape. The shader's, line for line.
 */
export function spriteLight(flux: number, gain: number, area: number, spritePx: number, mean: number): number {
  return (flux * gain) / (area * spritePx * spritePx * mean);
}

/** Steps along the segment from a point to the camera: the vertex shader's loop bound. The march's sampling. */
export const DUST_SEGMENT_STEPS = 48;

/** What the segment reads at a place in the disc: the ring's face-on depth per channel times the dust's placement
 * there, and the dust layer's scale height, kpc (the march's own textures). */
export type DustRead = (r: number, phi: number) => { depth: readonly [number, number, number]; height: number };

/**
 * The dust's optical depth per channel between a point and the camera (T20) — the vertex shader's `dustTo`, line
 * for line. The segment is cut where it leaves the slab |y| ≤ `top` or the disc's radius `rHi`, split into
 * `steps` equal steps, and each takes the dust layer's exact column over its own heights (regimes.ts
 * layerColumn) at the depth and height read at its middle. Scene coordinates: x = R cos φ, y = height,
 * z = −R sin φ, kpc.
 */
export function dustToPoint(
  point: readonly [number, number, number],
  eye: readonly [number, number, number],
  top: number,
  rHi: number,
  read: DustRead,
  steps: number = DUST_SEGMENT_STEPS,
): [number, number, number] {
  const d = [eye[0] - point[0], eye[1] - point[1], eye[2] - point[2]];
  const length = Math.hypot(d[0], d[1], d[2]);
  const tau: [number, number, number] = [0, 0, 0];
  if (!(length > 0)) return tau;
  const u = [d[0] / length, d[1] / length, d[2] / length];
  let sMax = length;
  // Out of the slab: beyond it the layer holds nothing worth a step.
  if (Math.abs(u[1]) > 1e-6) sMax = Math.min(sMax, Math.max(0, ((u[1] > 0 ? top : -top) - point[1]) / u[1]));
  // Out of the disc's radius: the far root of |p + u s| = rHi in the plane.
  const a = u[0] * u[0] + u[2] * u[2];
  if (a > 1e-12) {
    const b = point[0] * u[0] + point[2] * u[2];
    const c = point[0] * point[0] + point[2] * point[2] - rHi * rHi;
    const disc = b * b - a * c;
    sMax = disc > 0 ? Math.min(sMax, Math.max(0, (-b + Math.sqrt(disc)) / a)) : 0;
  }
  if (!(sMax > 0)) return tau;
  const ds = sMax / steps;
  for (let j = 0; j < steps; j += 1) {
    const s0 = j * ds;
    const s1 = s0 + ds;
    const mid = 0.5 * (s0 + s1);
    const x = point[0] + u[0] * mid;
    const z = point[2] + u[2] * mid;
    const r = Math.hypot(x, z);
    if (r >= rHi) continue;
    let phi = Math.atan2(-z, x);
    if (phi < 0) phi += 2 * Math.PI;
    const at = read(r, phi);
    const column = layerColumn(point[1] + u[1] * s0, point[1] + u[1] * s1, at.height, ds);
    for (let k = 0; k < 3; k += 1) tau[k] += at.depth[k] * column;
  }
  return tau;
}

/**
 * The slab the segment is cut by, kpc: this many of the tallest dust layer's scale heights, where the layer's
 * density is under 10⁻⁶ of its midplane's (regimes.ts MARCH_SCALE_HEIGHTS, the march's own reasoning).
 */
export const DUST_TOP_HEIGHTS = 16;

/** The tallest published dust layer among the rings, kpc (`dust_height`, or the one height the render names). */
export function tallestLayer(heights: ArrayLike<number> | number | null | undefined): number {
  if (typeof heights === "number") return Number.isFinite(heights) && heights > 0 ? heights : 0;
  let top = 0;
  for (let i = 0; i < (heights?.length ?? 0); i += 1) {
    const h = Number(heights![i]);
    if (Number.isFinite(h) && h > top) top = h;
  }
  return top;
}
