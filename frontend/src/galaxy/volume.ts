// The unresolved light as a volume (RENDER_PLAN R3, M4 and the bulge): particles drawn
// from published densities, each carrying an equal share of a published luminosity.
// No three.js here.
//
// Why particles and not a textured plane: a plane has no thickness, so edge-on the
// disc vanishes and a dust lane has nothing to cross. A particle volume has the
// published scale height, a bulge that is round from every side, and a near and a
// far half the dust screen can sit between.
//
// The draw is the viewer's discretisation of densities the model publishes, seeded
// so the same galaxy gives the same picture. The particles are not stars and carry
// no identity: the star sample is drawn over them and is what can be clicked.

import type { Axis } from "../preview/axes";

const PC2_PER_KPC2 = 1e6;

/**
 * Linear sRGB of an HII region's light: Hα 656.3 nm and Hβ 486.1 nm at the case-B
 * ratio 2.86 : 1, through the same CIE 1931 fit and XYZ-to-sRGB matrix as the
 * blackbody cmap (galaxy/core/cmaps.py), brightest channel at 1. Computed there
 * once and copied here, because a line colour is not a field and has no ramp.
 * [recall: Osterbrock & Ferland 2006, case B Hα/Hβ = 2.86 at 10⁴ K]
 */
export const HII_RGB = [1.0, 0.1607, 0.5032] as const;

/** A small, fast, seeded generator (mulberry32), so a galaxy's picture is repeatable. */
export function seeded(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Index drawn from a cumulative table by bisection. */
function pick(cdf: Float64Array, u: number): number {
  let lo = 0;
  let hi = cdf.length - 1;
  const target = u * cdf[hi];
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (cdf[mid] < target) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}

function cumulative(weights: ArrayLike<number>): Float64Array {
  const out = new Float64Array(weights.length);
  let sum = 0;
  for (let i = 0; i < weights.length; i += 1) {
    const w = weights[i];
    sum += Number.isFinite(w) && w > 0 ? w : 0;
    out[i] = sum;
  }
  return out;
}

export interface DiscLight {
  R: Axis;
  /** Surface brightness per R cell, L☉/pc². */
  brightness: ArrayLike<number>;
  /** The (R, φ) pattern contrast, row-major, when the model publishes one. */
  contrast?: { values: ArrayLike<number>; phi: Axis };
  /** Vertical sech² scale height, kpc. */
  height: number;
  /** Face-on A_V per R cell, when the model publishes dust; it follows the same contrast. */
  extinction?: ArrayLike<number>;
}

export interface Particles {
  /** Scene positions: x = r cos φ, y = height, z = −r sin φ, as the stars. */
  positions: Float32Array;
  /** Linear RGB, in L☉ per particle times the caller's gain. */
  colors: Float32Array;
  /**
   * Smoothing size per particle, pc: a few times the local spacing between particles, so
   * where they are sparse each is spread wider and dimmer and the sum stays a surface
   * rather than a spray of dots. The renderer divides each particle's light by its area.
   */
  sizes: Float32Array;
  /** Face-on V-band optical depth of the dust at the particle's (R, φ): the whole column, both sides. */
  tau: Float32Array;
  count: number;
}

/** Smoothing sizes, pc, bounded so the core stays sharp and the outskirts do not fill the sky. */
export const SMOOTHING = { spacings: 5, min: 80, max: 3000 };

function smoothing(spacingPc: number): number {
  return Math.min(SMOOTHING.max, Math.max(SMOOTHING.min, SMOOTHING.spacings * spacingPc));
}

/** Total luminosity of a disc of this surface brightness, L☉. */
export function discLuminosity(R: Axis, brightness: ArrayLike<number>): number {
  let total = 0;
  for (let i = 0; i < R.n; i += 1) {
    const b = brightness[i];
    if (Number.isFinite(b) && b > 0) total += b * 2 * Math.PI * (R.lo + (i + 0.5) * R.width) * R.width * PC2_PER_KPC2;
  }
  return total;
}

/**
 * Draw `count` particles of a disc's light: radius by the light in each ring, azimuth
 * by the contrast at that ring (raised to `clump`, so emission that follows star
 * formation can crowd harder into the arms than the starlight does), height by sech².
 * Each carries `luminosity / count` in the colour `tint(ring)`, times `gain`.
 */
export function sampleDisc(
  disc: DiscLight,
  weights: ArrayLike<number>,
  luminosity: number,
  tint: (ring: number) => readonly number[] | null,
  count: number,
  gain: number,
  random: () => number,
  clump = 1,
  /** A fixed smoothing size, pc, for light that is compact whatever its spacing (HII regions). */
  fixedSize?: number,
): Particles {
  const { R, contrast, height } = disc;
  const ringWeights = new Float64Array(R.n);
  for (let i = 0; i < R.n; i += 1) ringWeights[i] = Math.max(0, weights[i] || 0) * (R.lo + (i + 0.5) * R.width);
  const ringCdf = cumulative(ringWeights);
  const phiCdfs = new Map<number, Float64Array>();
  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);
  const sizes = new Float32Array(count);
  const tau = new Float32Array(count);
  if (!(ringCdf[R.n - 1] > 0) || !(luminosity > 0)) return { positions, colors, sizes, tau, count: 0 };
  const share = luminosity / count;
  const each = share * gain;

  let made = 0;
  for (let k = 0; k < count; k += 1) {
    const ring = pick(ringCdf, random());
    const colour = tint(ring);
    if (!colour) continue;
    const r = R.lo + (ring + random()) * R.width;
    let phi = random() * 2 * Math.PI;
    let local = Math.max(0, weights[ring] || 0);
    let factor = 1;
    if (contrast) {
      let cdf = phiCdfs.get(ring);
      if (!cdf) {
        const row = new Float64Array(contrast.phi.n);
        for (let j = 0; j < row.length; j += 1) row[j] = Math.max(0, contrast.values[ring * contrast.phi.n + j]) ** clump;
        cdf = cumulative(row);
        phiCdfs.set(ring, cdf);
      }
      if (cdf[cdf.length - 1] > 0) {
        const j = pick(cdf, random());
        phi = (j + random()) * contrast.phi.width + contrast.phi.lo;
        // The draw's local surface density: the ring's times this sector's share of it.
        local *= ((cdf[j] - (j > 0 ? cdf[j - 1] : 0)) / cdf[cdf.length - 1]) * contrast.phi.n;
        factor = Math.max(0, contrast.values[ring * contrast.phi.n + j]);
      }
    }
    const u = Math.min(0.999, Math.max(0.001, random()));
    const z = 2 * height * Math.atanh(2 * u - 1);
    const p = made * 3;
    positions[p] = r * Math.cos(phi);
    positions[p + 1] = z;
    positions[p + 2] = -r * Math.sin(phi);
    colors[p] = colour[0] * each;
    colors[p + 1] = colour[1] * each;
    colors[p + 2] = colour[2] * each;
    // Particles per pc² here is local / share, so the spacing between them is its inverse square root.
    sizes[made] = fixedSize ?? smoothing(local > 0 ? Math.sqrt(share / local) : SMOOTHING.max);
    const av = disc.extinction ? Number(disc.extinction[ring]) : 0;
    tau[made] = av > 0 ? (av * factor) / 1.086 : 0;
    made += 1;
  }
  return {
    positions: positions.subarray(0, made * 3),
    colors: colors.subarray(0, made * 3),
    sizes: sizes.subarray(0, made),
    tau: tau.subarray(0, made),
    count: made,
  };
}

/** The share of a Hernquist sphere's light drawn: the tail past 18 scale radii is left out. */
export const BULGE_DRAWN = 0.9;

/**
 * A Hernquist sphere of scale `a` (kpc): enclosed mass M r²/(r + a)², so r = a√u/(1 − √u),
 * in a random direction. Drawn to BULGE_DRAWN of its light, 18 scale radii: the rest is a
 * faint tail tens of kiloparsecs wide that, drawn, fills the view with a haze no image shows
 * at this exposure. `tauAt(r)` is the disc's face-on dust column at cylindrical radius r.
 */
export function sampleBulge(
  a: number,
  luminosity: number,
  colour: readonly number[],
  count: number,
  gain: number,
  random: () => number,
  tauAt: (r: number) => number = () => 0,
): Particles {
  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);
  const sizes = new Float32Array(count);
  const tau = new Float32Array(count);
  if (!(a > 0) || !(luminosity > 0)) return { positions, colors, sizes, tau, count: 0 };
  const each = ((luminosity * BULGE_DRAWN) / count) * gain;
  for (let k = 0; k < count; k += 1) {
    const s = Math.sqrt(random() * BULGE_DRAWN);
    const r = (a * s) / (1 - s);
    const cosTheta = 2 * random() - 1;
    const sinTheta = Math.sqrt(1 - cosTheta * cosTheta);
    const phi = random() * 2 * Math.PI;
    const p = k * 3;
    positions[p] = r * sinTheta * Math.cos(phi);
    positions[p + 1] = r * cosTheta;
    positions[p + 2] = -r * sinTheta * Math.sin(phi);
    colors[p] = colour[0] * each;
    colors[p + 1] = colour[1] * each;
    colors[p + 2] = colour[2] * each;
    // Hernquist spacing grows about linearly with radius outside the scale: smooth by it.
    sizes[k] = smoothing(1000 * (0.25 * r + 0.05 * a));
    tau[k] = tauAt(r * sinTheta);
  }
  return { positions, colors, sizes, tau, count };
}
