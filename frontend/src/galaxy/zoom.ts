// Camera distance to a zoom position and back, and a scale bar that reads in
// round kiloparsecs. Logarithmic, because the view runs from the whole disc to
// a few tens of parsecs and a linear slider would spend its travel far out.

import { DEFAULT_FOV, distanceFor, lensScale } from "./capture";

export interface ZoomRange {
  min: number;
  max: number;
}

/** The farthest the camera stands over the closest: the zoom slider's whole travel, a factor of 1600. */
export const ZOOM_SPAN = 1600;
/** A stand the view is given (a template's camera) sits this far inside the farthest distance, at the least. */
const STAND_MARGIN = 1.25;

/**
 * The camera distances the view allows, kpc, for a framing radius `reach` through a lens of `fovDegrees`: from
 * reach / 200 to 8 reach at 45° - the range the view has always had - and the same widths of view through any
 * other lens (capture.ts lensScale), so the slider, the regimes and the scale bar mean what they meant. A stand
 * the view must be able to take (`standRadius`, a template camera's framing radius) widens it where the
 * galaxy's own reach would put that stand beyond the farthest distance: a compact galaxy framed at 20 kpc.
 */
export function zoomRange(reach: number, fovDegrees: number = DEFAULT_FOV, standRadius = 0): ZoomRange {
  const needed = (STAND_MARGIN * distanceFor(standRadius, DEFAULT_FOV)) / 8;
  const base = Math.max(reach, needed) * lensScale(fovDegrees);
  return { min: base / 200, max: base * 8 };
}

/**
 * The near and far planes for a zoom range: a fifth of the closest distance and two and a half times the
 * farthest - reach / 1000 and 20 reach at 45°, as before. They follow the lens with the range: at 5° the
 * camera stands 9.5 times further, and a far plane left at 20 reach would cut the galaxy off.
 */
export function clipPlanes(range: ZoomRange): { near: number; far: number } {
  return { near: range.min / 5, far: range.max * 2.5 };
}

/** Distance to a slider position in [0, 1]: 0 is the farthest, 1 the closest. */
export function zoomOf(distance: number, r: ZoomRange): number {
  const d = Math.min(Math.max(distance, r.min), r.max);
  return (Math.log(r.max) - Math.log(d)) / (Math.log(r.max) - Math.log(r.min));
}

export function distanceOf(zoom: number, r: ZoomRange): number {
  const t = Math.min(Math.max(zoom, 0), 1);
  return Math.exp(Math.log(r.max) - t * (Math.log(r.max) - Math.log(r.min)));
}

/** The width of the view at the camera's target, for a perspective camera. */
export function acrossOf(distance: number, fovDegrees: number, aspect: number): number {
  return 2 * distance * Math.tan((fovDegrees * Math.PI) / 360) * aspect;
}

/** A scale bar of 1, 2 or 5 × 10^k kpc no wider than `maxPx`. */
export function scaleBar(pxPerKpc: number, maxPx = 140): { kpc: number; px: number } {
  const target = maxPx / pxPerKpc;
  const power = 10 ** Math.floor(Math.log10(target));
  const kpc = [5, 2, 1].map((m) => m * power).find((v) => v <= target) ?? power;
  return { kpc, px: kpc * pxPerKpc };
}
