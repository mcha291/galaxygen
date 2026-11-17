// A knot as its HII region's sphere seen in projection (S102, #232; batch Q's viewer lane, V2). No three.js here: the
// pure parts, tested, which FluxPoints' shaders repeat line for line.
//
// The model publishes each HII region's radius, `hii_radius`, and an Halpha emissivity uniform inside it (the nebular
// stage, S102). A uniform sphere of radius R seen from afar has the column of its chord: proportional to
// sqrt(1 - (r/R)^2) inside R and zero outside - geometry of what the model publishes, not physics (rule D5). The knot is
// that profile convolved with what a point already gets (the sprite, or the instrument's image of a point): its light
// is the profile's samples, each drawn as the point would be, with weights that sum to 1 - so the knot's light is the
// point's (the closure, sphere.test.ts). Two samplings of the one profile, by its radius in pixels:
//
// - **taps** (R under SPHERE_LATTICE_PX): 2n points in antipodal pairs at the profile's own radial quantiles, equal
//   weights 1 / 2n - the centroid is the knot's centre exactly, and n grows with R^2 so the taps stay about a pixel
//   apart; each tap is the point's own image at that offset;
// - **lattice** (R from SPHERE_LATTICE_PX): the profile's mean over each pixel (2 x 2 samples) at the pixel centres
//   round the knot, over their sum (the normaliser, `sphereNorm`), each drawn as the point's image at a pixel centre.
//
// Below SPHERE_MIN_PX a knot is the point it was, drawn by the same statements (the frame's bytes are the old frame's
// wherever no region reaches it). The dust dims the whole knot by its centre's column, as it dims the point (an
// extended region dimmed by its centre's column: a stated approximation, not the column over its face).

/** Under this radius, pixels, a knot is drawn as the point, unchanged: the profile's rms radius, sqrt(2/5) R, is then
 * under 0.16 px - against the default sprite's core of 1.35 px, a broadening of 0.7 % in its variance. A bound. */
export const SPHERE_MIN_PX = 0.25;
/** From this radius, pixels, the profile is sampled on the pixel lattice rather than by taps: a sampling bound. */
export const SPHERE_LATTICE_PX = 4;
/** The most tap pairs (the taps' loop bound): 2 x 4^2 at SPHERE_LATTICE_PX. */
export const SPHERE_MAX_PAIRS = 32;
/** The largest half-side, pixels, of the instrument's image a knot is convolved with: the image past it is cut and
 * its light put back inside (the box's weights are normalised over it), as the clamped point's box does. A bound on
 * work, not a display choice. */
export const SPHERE_KERNEL_MAX_HALF = 8;
/** The golden angle, radians: the taps' turn from pair to pair (pi (3 - sqrt 5)). */
export const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5));

/** The chord through a uniform sphere of unit radius at impact parameter rho, over the central one: sqrt(1 - rho^2). */
export function chord(rho: number): number {
  return Math.sqrt(Math.max(0, 1 - rho * rho));
}

/** The chord profile's integral over the plane, for radius R (in the unit of R): 2 pi R^2 / 3. */
export function chordIntegral(r: number): number {
  return (2 * Math.PI * r * r) / 3;
}

/** How a knot of radius `rPx` pixels is drawn: 0 the point, 1 taps, 2 lattice. */
export function sphereMode(rPx: number): 0 | 1 | 2 {
  if (!(rPx >= SPHERE_MIN_PX)) return 0;
  return rPx < SPHERE_LATTICE_PX ? 1 : 2;
}

/** The tap pairs for a radius of `rPx` pixels: 2 R^2 pairs (the taps about a pixel apart), at least 1, at most the bound. */
export function tapPairs(rPx: number): number {
  return Math.min(SPHERE_MAX_PAIRS, Math.max(1, Math.ceil(2 * rPx * rPx)));
}

/**
 * Tap t of 2n, as an offset in units of the radius: pair p = floor(t / 2) at the profile's radial quantile
 * F = (p + 0.5) / n - the share of the projected sphere's light inside rho is 1 - (1 - rho^2)^(3/2), so
 * rho = sqrt(1 - (1 - F)^(2/3)) - turned by the golden angle per pair, the pair's second tap opposite the first.
 */
export function tapOffset(t: number, n: number): [number, number] {
  const p = Math.floor(t / 2);
  const f = (p + 0.5) / n;
  const rho = Math.sqrt(1 - (1 - f) ** (2 / 3));
  const turn = p * GOLDEN_ANGLE + (t % 2) * Math.PI;
  return [rho * Math.cos(turn), rho * Math.sin(turn)];
}

/** The chord profile's mean over the pixel whose centre is (dx, dy) px from the knot's, radius r px: 2 x 2 samples. */
export function chordCell(dx: number, dy: number, r: number): number {
  let s = 0;
  for (const ox of [-0.25, 0.25]) for (const oy of [-0.25, 0.25]) s += chord(Math.hypot(dx + ox, dy + oy) / r);
  return 0.25 * s;
}

/** The lattice's largest half-side, pixels, over which the normaliser sums its own box (the vertex shader's loop
 * bound): past it the sum is the profile's integral (to 1e-3, sphere.test.ts). A bound on work. */
export const SPHERE_NORM_LOOP_HALF = 24;

/** The lattice's box half-side, pixels: the radius and a pixel for the edge. */
export function latticeHalf(r: number): number {
  return Math.ceil(r) + 1;
}

/** The lattice's normaliser as the shader takes it: the chord cells summed over the knot's box (pixel centres at
 * floor(c) + i + 0.5), or the profile's integral past the loop's bound. */
export function sphereNorm(cx: number, cy: number, r: number): number {
  const h = latticeHalf(r);
  if (h > SPHERE_NORM_LOOP_HALF) return chordIntegral(r);
  let s = 0;
  for (let i = -h; i <= h; i += 1) {
    for (let j = -h; j <= h; j += 1) s += chordCell(Math.floor(cx) + i + 0.5 - cx, Math.floor(cy) + j + 0.5 - cy, r);
  }
  return s;
}

/** The kernel: what a point at the origin deposits on the pixel whose centre is at offset (ox, oy) px from it. */
export type Kernel = (ox: number, oy: number) => number;

/** The kernel's light summed over the pixels round a point at (px, py): what the point itself deposits there. */
export function kernelSum(kernel: Kernel, reach: number, px: number, py: number): number {
  let s = 0;
  for (let i = -reach - 1; i <= reach + 1; i += 1) {
    for (let j = -reach - 1; j <= reach + 1; j += 1) s += kernel(Math.floor(px) + i + 0.5 - px, Math.floor(py) + j + 0.5 - py);
  }
  return s;
}

/**
 * The display sprite's deposit wobbles with where a point falls in its pixel (2 % for the default sprite, measured):
 * the knot's samples stand elsewhere than its centre, so their light is scaled to the point's own at the centre -
 * the point's sum at the centre over the samples' mean sum (taps) or the pixel centre's (lattice). 1 for the
 * instrument's image, whose box sum is 1 wherever it stands (the shaders skip it there). The closure made exact.
 */
export function knotScale(kernel: Kernel, reach: number, cx: number, cy: number, r: number): number {
  const mode = sphereMode(r);
  if (mode === 0) return 1;
  const point = kernelSum(kernel, reach, cx, cy);
  if (mode === 2) return point / kernelSum(kernel, reach, 0.5, 0.5);
  const n = tapPairs(r);
  let s = 0;
  for (let t = 0; t < 2 * n; t += 1) {
    const [ux, uy] = tapOffset(t, n);
    s += kernelSum(kernel, reach, cx + r * ux, cy + r * uy);
  }
  return point / (s / (2 * n));
}

/**
 * The knot's deposit on pixel (kx, ky) (its lower corner, integer), centre (cx, cy), radius r px, through `kernel` of
 * half-reach `reach` px (the lattice's loop over the kernel's integer offsets), times `scale` (knotScale): the
 * shaders' sum, in double.
 */
export function knotDeposit(kernel: Kernel, reach: number, kx: number, ky: number, cx: number, cy: number, r: number, scale = 1): number {
  const mode = sphereMode(r);
  if (mode === 0) return kernel(kx + 0.5 - cx, ky + 0.5 - cy);
  if (mode === 1) {
    const n = tapPairs(r);
    let s = 0;
    for (let t = 0; t < 2 * n; t += 1) {
      const [ux, uy] = tapOffset(t, n);
      s += kernel(kx + 0.5 - cx - r * ux, ky + 0.5 - cy - r * uy);
    }
    return (s / (2 * n)) * scale;
  }
  // The lattice: pixel centres m + 0.5 round the knot, each the point's image at that centre (an integer offset).
  const norm = sphereNorm(cx, cy, r);
  let s = 0;
  for (let i = -reach; i <= reach; i += 1) {
    for (let j = -reach; j <= reach; j += 1) {
      const w = chordCell(kx - i + 0.5 - cx, ky - j + 0.5 - cy, r);
      if (w > 0) s += w * kernel(i, j);
    }
  }
  return (s / norm) * scale;
}
