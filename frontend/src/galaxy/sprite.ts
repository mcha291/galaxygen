// The default star sprite's shape, with no three.js in it (moved out of psf.ts at S67's fourth pass so the picture spec
// can trace a sprite's deposit pixel by pixel; psf.ts re-exports psfProfile and psfMean and builds the texture from it).

/**
 * A star's point spread function as a sprite (RENDER_PLAN R2): a Gaussian core with Moffat-like wings, white, so the
 * vertex colour carries the hue. r is 0 at the centre and 1 at the sprite's edge.
 */
export function psfProfile(r: number, core = 0.3, beta = 2.2): number {
  const gauss = Math.exp(-(r * r) / (2 * core * core));
  const moffat = (1 + (r / (core * 1.6)) ** 2) ** -beta;
  const edge = Math.max(0, 1 - r) ** 2; // the wing reaches zero at the edge, never a hard ring
  return Math.min(1, (0.7 * gauss + 0.3 * moffat) * edge);
}

/** The sprite's texels as its 8-bit texture holds them (alpha, 0..1), row-major on a `size` grid: psf.ts psfTexture's. */
export function spriteTexels(size = 64): Float64Array {
  const half = size / 2;
  const out = new Float64Array(size * size);
  for (let y = 0; y < size; y += 1) {
    for (let x = 0; x < size; x += 1) out[y * size + x] = Math.round(255 * psfProfile(Math.hypot(x + 0.5 - half, y + 0.5 - half) / half)) / 255;
  }
  return out;
}

/**
 * The default sprite's mean over its square, as its texture holds it: what the star-first mode divides by so that a
 * sprite's pixels sum to the point's light (flux.ts, D208). The same for every channel: the sprite is white.
 */
export function psfMean(size = 64): number {
  const t = spriteTexels(size);
  let sum = 0;
  for (let p = 0; p < t.length; p += 1) sum += t[p];
  return sum / t.length;
}

/**
 * The texture read as the GPU reads it with LinearFilter and clamp-to-edge, at (u, v) in 0..1: bilinear between texel
 * centres. The sprite is symmetric, so which way v runs does not matter.
 */
export function spriteSample(texels: Float64Array, size: number, u: number, v: number): number {
  const tx = Math.min(size - 1, Math.max(0, u * size - 0.5));
  const ty = Math.min(size - 1, Math.max(0, v * size - 0.5));
  const x0 = Math.floor(tx);
  const y0 = Math.floor(ty);
  const x1 = Math.min(x0 + 1, size - 1);
  const y1 = Math.min(y0 + 1, size - 1);
  const fx = tx - x0;
  const fy = ty - y0;
  const at = (x: number, y: number) => texels[y * size + x];
  return (at(x0, y0) * (1 - fx) + at(x1, y0) * fx) * (1 - fy) + (at(x0, y1) * (1 - fx) + at(x1, y1) * fx) * fy;
}
