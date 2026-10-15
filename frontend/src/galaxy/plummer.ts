// An object drawn with its own extent once it fills a pixel (S64, BUILD_III V6; RULING_S64 R6, R7; T6). No three.js
// here: the pure parts, tested, which FluxPoints' shaders repeat line for line.
//
// A point (FluxPoints) is the instrument's sprite: its light spread by the PSF. An object whose size fills a pixel is
// drawn with its own profile instead, in a box of whole pixels round it, each pixel taking the profile's light over
// that pixel's own area, over the light over the whole box - so the box's pixels sum to the object's light whatever the
// scale (the light past the box is put back in it: a truncation, conserving). Two profiles:
//
// - **A cluster (R7)** is a Plummer sphere of half-mass radius r_h (`cluster_half_mass_radius`): seen in projection its
//   surface density is a^2 / (pi (a^2 + R^2)^2) of its light, a = r_h / PLUMMER_HALF_MASS. The light over a pixel is
//   exact: the profile's integral over a rectangle has a closed form (plummerCorner).
// - **A knot (R6)** is its HII region's Stromgren sphere (`hii_stromgren_radius`, where the line light is): a disc of
//   that radius, each pixel taking the disc's coverage of it (an anti-aliased edge), the box's sum computed over the
//   box (discBoxSum), so the sum is the light to rounding.
//
// The switch (both): drawn with its extent once its diameter fills a pixel, 2 x extent >= the pixel's side at the
// object (flux.ts pixelArea's side); a point below.

/**
 * A Plummer sphere's half-mass radius over its scale length, r_h / a = 1 / sqrt(2^(2/3) - 1) = 1.30477: the radius
 * holding half the mass in three dimensions (the plan's 1.305, derived here). In projection a holds half the light.
 */
export const PLUMMER_HALF_MASS = 1 / Math.sqrt(2 ** (2 / 3) - 1);

/**
 * How far the cluster's box reaches each side of it, in scale lengths: a display choice (A9). The Plummer's light past
 * R is a^2 / (a^2 + R^2) of it, 1.5 % at 8 a, and that light is put back in the box, not lost.
 */
export const PLUMMER_REACH = 8;

/** The box's largest half-side, pixels: a bound on the sprite (2 x this + 4 pixels a side), a display choice. */
export const PROFILE_MAX_HALF = 60;

/** The largest half-side, pixels, over which a knot's disc sums its own box (the vertex shader's loop bound): past it the disc's area is the sum to 1e-3 (plummer.test.ts). A bound on work, not a display choice. */
export const DISC_LOOP_HALF = 24;

/** Drawn with its extent: the diameter, 2 x `extentPc`, fills the pixel's side at the object, `pixelPc` (pc). */
export function resolvedAt(extentPc: number, pixelPc: number): boolean {
  return extentPc > 0 && pixelPc > 0 && 2 * extentPc >= pixelPc;
}

/** The pixel's side at a point, pc: flux.ts pixelArea's side, `depth` kpc along the view's axis. */
export function pixelSide(depth: number, pxPerUnit: number): number {
  return (1000 * depth) / pxPerUnit;
}

/**
 * The integral of 1 / (a^2 + x^2 + y^2)^2 over [0, x] x [0, y], times a^2 / pi: the Plummer's share of its light in
 * that rectangle (odd in x and in y, so any rectangle is four corners). Its mixed derivative is the profile, and at
 * infinity in both it is 1/4.
 */
export function plummerCorner(x: number, y: number, a: number): number {
  const sx = Math.sqrt(a * a + x * x);
  const sy = Math.sqrt(a * a + y * y);
  return ((x / sx) * Math.atan(y / sx) + (y / sy) * Math.atan(x / sy)) / (2 * Math.PI);
}

/** The Plummer's share of its light over [x0, x1] x [y0, y1], the object at the origin, all in the same unit as a. */
export function plummerRect(x0: number, x1: number, y0: number, y1: number, a: number): number {
  return plummerCorner(x1, y1, a) - plummerCorner(x0, y1, a) - plummerCorner(x1, y0, a) + plummerCorner(x0, y0, a);
}

/** A disc of radius r's coverage of the pixel whose centre is (dx, dy) from the disc's: an anti-aliased edge. */
export function discCover(dx: number, dy: number, r: number): number {
  return Math.min(1, Math.max(0, r - Math.hypot(dx, dy) + 0.5));
}

/** The box of whole pixels round an object at window position (cx, cy), px: its first pixel and its side, pixels. */
export function profileBox(cx: number, cy: number, half: number): { x0: number; y0: number; side: number } {
  const h = Math.max(1, Math.min(PROFILE_MAX_HALF, Math.ceil(half)));
  return { x0: Math.floor(cx) - h, y0: Math.floor(cy) - h, side: 2 * h + 1 };
}

/** The cluster's box half-side, pixels: PLUMMER_REACH scale lengths of `aPx`. */
export function plummerHalf(aPx: number): number {
  return PLUMMER_REACH * aPx;
}

/** The knot's box half-side, pixels: its radius and a pixel for the edge. */
export function discHalf(rPx: number): number {
  return rPx + 1;
}

/** The disc's coverage summed over its box (discCover): the vertex shader's loop, the normaliser of each pixel. */
export function discBoxSum(cx: number, cy: number, r: number): number {
  const box = profileBox(cx, cy, discHalf(r));
  let sum = 0;
  for (let i = 0; i < box.side; i += 1) {
    for (let j = 0; j < box.side; j += 1) sum += discCover(box.x0 + i + 0.5 - cx, box.y0 + j + 0.5 - cy, r);
  }
  return sum;
}

/**
 * Each pixel's weight in an object's box, row-major (side x side), summing to 1: the light over each pixel over the
 * light over the box. `kind` 1 is the Plummer of scale `scale` px, 2 the disc of radius `scale` px. The shaders' sum.
 */
export function profileWeights(kind: 1 | 2, cx: number, cy: number, scale: number): { x0: number; y0: number; side: number; weights: Float64Array } {
  const box = profileBox(cx, cy, kind === 1 ? plummerHalf(scale) : discHalf(scale));
  const weights = new Float64Array(box.side * box.side);
  const norm =
    kind === 1
      ? plummerRect(box.x0 - cx, box.x0 + box.side - cx, box.y0 - cy, box.y0 + box.side - cy, scale)
      : discNorm(cx, cy, scale);
  for (let j = 0; j < box.side; j += 1) {
    for (let i = 0; i < box.side; i += 1) {
      const x = box.x0 + i - cx;
      const y = box.y0 + j - cy;
      const w = kind === 1 ? plummerRect(x, x + 1, y, y + 1, scale) : discCover(x + 0.5, y + 0.5, scale);
      weights[j * box.side + i] = w / norm;
    }
  }
  return { ...box, weights };
}

/** The disc's normaliser as the shader takes it: its box's sum where the box fits the loop, its area beyond. */
export function discNorm(cx: number, cy: number, r: number): number {
  return profileBox(cx, cy, discHalf(r)).side <= 2 * DISC_LOOP_HALF + 1 ? discBoxSum(cx, cy, r) : Math.PI * r * r;
}
