// Camera distance to a zoom position and back, and a scale bar that reads in
// round kiloparsecs. Logarithmic, because the view runs from the whole disc to
// a few tens of parsecs and a linear slider would spend its travel far out.

export interface ZoomRange {
  min: number;
  max: number;
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
