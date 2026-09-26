// The region regime (BUILD_II V3, S40): below the stars handover the view asks the model for the cell
// hierarchy's level that fits it, and synthesises each cloud's interior from the published vector
// (RENDER_PHYSICS §5a): mass and size for the mean density, the log-normal width σ_s for the structure,
// the source offset for the cavity and the pillars, the gradient for the tilt — all seeded by the cloud's
// cell-and-index path, so the same cloud is the same at every approach and at every level (§5c, D181).
// Nothing here is physics the model does not publish: the noise is a construction that realises the
// published one-point distribution, and its parameters are stated here and tested (region.test.ts).

/**
 * The hierarchy level a view `across` kpc wide asks for: level 0 down to the stars handover (4 kpc),
 * then one level per factor four of width, so a level-k cell (a level-0 cell is ~1.6 kpc × 0.2 rad at
 * the Sun's radius, 2^k finer per side) is never more than about half the view. The steps are the
 * hierarchy's own factor, not a display choice; the anchor is REGIME_KPC.stars (regimes.ts).
 */
export const LEVEL_KPC: readonly number[] = [4, 1, 0.25, 0.0625];
export const MAX_LEVEL = 3;

export function levelFor(across: number): number {
  let level = 0;
  for (let k = 0; k < LEVEL_KPC.length; k += 1) if (across < LEVEL_KPC[k]) level = k + 1;
  return Math.min(level, MAX_LEVEL);
}

/**
 * A 32-bit integer hash of a lattice point and a seed (the cloud's cell and index). The same hash runs
 * in the shader (RegionVolume.tsx), line for line in integer arithmetic, so the CPU and the GPU agree
 * on every sample: the vitest asserts the CPU side's distribution, the shader draws it.
 */
export function hash3(x: number, y: number, z: number, seed: number): number {
  let h = (x * 374761393 + y * 668265263 + z * 2147483647 + seed * 1597334677) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h = h ^ (h >>> 16);
  return (h >>> 0) / 4294967296; // [0, 1)
}

/** Value noise on the unit lattice: trilinear between the eight corners' hashes, smoothed. */
export function valueNoise(x: number, y: number, z: number, seed: number): number {
  const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z);
  const fx = x - ix, fy = y - iy, fz = z - iz;
  const sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy), sz = fz * fz * (3 - 2 * fz);
  const c = (dx: number, dy: number, dz: number) => hash3(ix + dx, iy + dy, iz + dz, seed);
  const x00 = c(0, 0, 0) + (c(1, 0, 0) - c(0, 0, 0)) * sx;
  const x10 = c(0, 1, 0) + (c(1, 1, 0) - c(0, 1, 0)) * sx;
  const x01 = c(0, 0, 1) + (c(1, 0, 1) - c(0, 0, 1)) * sx;
  const x11 = c(0, 1, 1) + (c(1, 1, 1) - c(0, 1, 1)) * sx;
  const y0 = x00 + (x10 - x00) * sy;
  const y1 = x01 + (x11 - x01) * sy;
  return y0 + (y1 - y0) * sz; // [0, 1)
}

/** Octaves of the value noise, frequencies 1, 2, 4, 8 per unit, weights 1, 1/2, 1/4, 1/8. */
export const OCTAVES = 4;
/** A single octave of smoothed value noise, uniform corners: its standard deviation, measured (region.test.ts). */
export const OCTAVE_SIGMA = 0.1794;
/** The weights' quadrature sum: were the octaves independent, the sum's spread would be OCTAVE_SIGMA × this (0.2067). */
export const OCTAVE_NORM = Math.sqrt(1 + 1 / 4 + 1 / 16 + 1 / 64);
/**
 * The summed octaves' standard deviation, measured on 64 000 points (region.test.ts): 0.2088, 1% above the
 * independent-octave figure because the octaves share lattice corners. The field is divided by this, so its
 * variance is 1 by measurement rather than by assumption.
 */
export const FIELD_SIGMA = 0.2088;

/**
 * A field g(x) of zero mean and unit variance built from the octaves — approximately Gaussian, being a
 * sum of many smoothed uniforms — read at a point in the cloud's own frame (units of its radius).
 */
export function unitField(x: number, y: number, z: number, seed: number): number {
  let sum = 0;
  let f = 1;
  let w = 1;
  for (let k = 0; k < OCTAVES; k += 1) {
    sum += (valueNoise(x * f + 17.3 * k, y * f + 31.7 * k, z * f + 47.1 * k, seed + 1013 * k) - 0.5) * w;
    f *= 2;
    w *= 0.5;
  }
  return sum / FIELD_SIGMA;
}

/**
 * The cloud's density over its mean at a point: the log-normal the census publishes the width of,
 * ρ/ρ̄ = exp(σ_s g − σ_s²/2), whose mean over the field is 1 (RENDER_PHYSICS §6: the same mechanism
 * that structures the cloud keeps its mean column). The gradient tilts the mean: 1 + G (x · ĝ) over the
 * cloud's radius, clamped so the tilted mean stays positive [inferred: a linear tilt].
 */
export function densityRatio(
  x: number, y: number, z: number, seed: number, sigmaS: number, gradient: number, gradientAngle: number,
): number {
  const g = unitField(x, y, z, seed);
  const tilt = Math.max(0.05, 1 + Math.min(0.95, Math.abs(gradient)) * (x * Math.cos(gradientAngle) + z * Math.sin(gradientAngle)));
  return tilt * Math.exp(sigmaS * g - 0.5 * sigmaS * sigmaS);
}

/** How a cloud's rows are keyed: the same (cell, index) path the model names it by (§5a), as one integer seed. */
export function cloudSeed(cell: number, index: number): number {
  return ((cell & 0xffff) << 15) ^ (index & 0x7fff);
}
