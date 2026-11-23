// The arms' sparkle (BUILD_VIII row 108): a fine grain of small bright blue-white points along the arms' ridges, of
// the illustrative look's own (D275). Pure and deterministic: the same arm map, parameters and seed give the same
// buffers, every value from a hash seed of the viewer's own (never the time or the frame). The points are fixed in the
// galaxy's frame (positions.ts toScene), so they turn with it.
//
// Placement: OB associations - group centres drawn over the disc by rejection against the density
// d = armShare^ridge (the arm map's G channel: the ridge's share, already faded out inside the bar), each group a
// handful of members in a small gaussian; the rest single points against the same density. Brightness: a power law
// (many faint, few bright), the group's brightest at its centre.

import type { ArmGrid } from "./armsField";

/** mulberry32: a small seeded generator, the same sequence for the same seed on every machine. */
export function rng(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** A string's 32-bit hash (FNV-1a), for a seed per template. */
export function hashString(s: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

export interface SparkleShape {
  /** How many points in all. */
  count: number;
  /** The share of points in groups (OB associations); the rest single. */
  clump: number;
  /** A group's gaussian radius, pc. */
  groupPc: number;
  /** Members per group, mean. */
  members: number;
  /** The density's power over the arm share: higher keeps the points on the ridge. */
  ridge: number;
  /** The brightness law's index: L ~ u^(-1/slope); smaller has more bright points. */
  slope: number;
  /** The brightest point's flux over the faintest's. */
  range: number;
  /** The outermost radius drawn, kpc. */
  rMax: number;
  /** The points' half-thickness, pc. */
  heightPc: number;
}

export interface Sparkle {
  /** Galaxy-frame (R kpc, phi rad, z kpc) per point. */
  radius: Float32Array;
  azimuth: Float32Array;
  height: Float32Array;
  /** Each point's brightness in units of the faintest. */
  weight: Float32Array;
}

/** The arm share (the arm map's G channel) at (R, phi), linear between texels, 0 outside the grid. */
export function shareAt(map: Float32Array, g: ArmGrid, r: number, phi: number): number {
  const u = (r / g.rHi) * g.nR - 0.5;
  if (u < -0.5 || u > g.nR - 0.5) return 0;
  const v = ((((phi / (2 * Math.PI)) % 1) + 1) % 1) * g.nPhi - 0.5;
  const i0 = Math.max(0, Math.min(g.nR - 1, Math.floor(u)));
  const i1 = Math.min(g.nR - 1, i0 + 1);
  const fu = Math.min(1, Math.max(0, u - i0));
  const j0 = ((Math.floor(v) % g.nPhi) + g.nPhi) % g.nPhi;
  const j1 = (j0 + 1) % g.nPhi;
  const fv = v - Math.floor(v);
  const at = (i: number, j: number) => map[(j * g.nR + i) * 4 + 1];
  return (at(i0, j0) * (1 - fu) + at(i1, j0) * fu) * (1 - fv) + (at(i0, j1) * (1 - fu) + at(i1, j1) * fu) * fv;
}

/** A gaussian deviate (Box-Muller) from the generator. */
const gauss = (next: () => number): number => Math.sqrt(-2 * Math.log(Math.max(1e-12, next()))) * Math.cos(2 * Math.PI * next());

/** A brightness from the power law: 1 to `range`, many faint, few bright. */
export function brightness(u: number, slope: number, range: number): number {
  return Math.min(range, Math.pow(Math.max(1e-9, 1 - u), -1 / Math.max(0.1, slope)));
}

/** The points: deterministic in (map, grid, shape, seed). */
export function buildSparkle(map: Float32Array, g: ArmGrid, s: SparkleShape, seed: number): Sparkle {
  const total = Math.max(0, Math.floor(s.count));
  const radius = new Float32Array(total);
  const azimuth = new Float32Array(total);
  const height = new Float32Array(total);
  const weight = new Float32Array(total);
  const next = rng(seed);
  const rMax = Math.min(s.rMax, g.rHi);
  const density = (r: number, phi: number) => Math.pow(Math.max(0, shareAt(map, g, r, phi)), s.ridge);
  // A place drawn against the density: area-uniform proposals, accepted with probability d (bounded tries).
  const place = (): [number, number] | null => {
    for (let t = 0; t < 400; t++) {
      const r = rMax * Math.sqrt(next());
      const phi = 2 * Math.PI * next();
      if (next() < density(r, phi)) return [r, phi];
    }
    return null;
  };
  const hz = s.heightPc / 1000;
  let k = 0;
  const grouped = Math.floor(total * Math.min(1, Math.max(0, s.clump)));
  while (k < grouped) {
    const c = place();
    if (!c) break;
    // Members: geometric about the mean, at least one; the centre's the brightest.
    const m = Math.max(1, Math.round(-Math.log(Math.max(1e-9, next())) * s.members));
    const sigma = s.groupPc / 1000;
    const lead = brightness(next(), s.slope, s.range);
    for (let q = 0; q < m && k < grouped; q++, k++) {
      const x = c[0] * Math.cos(c[1]) + gauss(next) * sigma;
      const y = c[0] * Math.sin(c[1]) + gauss(next) * sigma;
      radius[k] = Math.hypot(x, y);
      azimuth[k] = ((Math.atan2(y, x) % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);
      height[k] = gauss(next) * hz;
      weight[k] = q === 0 ? lead : Math.min(lead, brightness(next(), s.slope, s.range));
    }
  }
  while (k < total) {
    const c = place();
    if (!c) break;
    radius[k] = c[0];
    azimuth[k] = c[1];
    height[k] = gauss(next) * hz;
    weight[k] = brightness(next(), s.slope, s.range);
    k++;
  }
  return { radius: radius.subarray(0, k), azimuth: azimuth.subarray(0, k), height: height.subarray(0, k), weight: weight.subarray(0, k) };
}
