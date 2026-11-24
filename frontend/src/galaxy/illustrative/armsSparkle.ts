// The arms' sparkle (BUILD_VIII row 108): a fine grain of small bright blue-white points along the arms' ridges, of
// the illustrative look's own (D275). Pure and deterministic: the same arm map, parameters and seed give the same
// buffers, every value from a hash seed of the viewer's own (never the time or the frame). The points are fixed in the
// galaxy's frame (positions.ts toScene), so they turn with it.
//
// Placement: OB associations - group centres drawn over the disc by rejection against the density
// d = armShare^ridge (the arm map's G channel: the ridge's share, already faded out inside the bar), each group a
// handful of members in a small gaussian; the rest single points against the same density. Brightness: a power law
// (many faint, few bright), the group's brightest at its centre.

import { latticeHash, smoothstep, type ArmGrid } from "./armsField";

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
  /** The outermost radius drawn, kpc: the density tapers smoothly to nothing over its outer 30 %. */
  rMax: number;
  /** The points' half-thickness, pc. */
  heightPc: number;
  /** S106: the density's floor between the arms, as a share of a full ridge's (0 none: every point on the arms). */
  floor?: number;
  /**
   * S106: above 0, the density is read from the raw ridge share (buildSparkle's `raw`) as min(1, share / lift) - a
   * weak ridge lit as fully as a strong one - in place of the map's G; 0 (or no raw share) the G as S105 read it.
   */
  lift?: number;
  /**
   * S106: the share of the sparkle kept off the dust lanes - its density times 1 - avoid * min(1, lane shape) where the
   * shared map's lanes (buildSparkle's `lanes`) lie - since the lanes' veil darkens the march, not the points; 0 none.
   */
  avoid?: number;
  /**
   * S106 (B5, the lumpy grain): the density modulated along the disc by a fixed smooth noise of wavelength `bunchPc`
   * (two octaves of value noise in the plane, hashed - never the rng's stream), by this share: bunches of points with
   * thinner stretches between, as the goal's arms have; 0 (or absent) the even grain.
   */
  bunch?: number;
  /** S106: the bunching noise's wavelength, pc. */
  bunchPc?: number;
  /** S106: the points in a bunch brighter by up to 1 + this (the noise's peak), the thin stretches dimmer; 0 none. */
  bunchBright?: number;
  /** S107 (MW2): the places drawn through an envelope of the density (envelopePlace: the same law, faster); else by rejection over the disc. */
  direct?: boolean;
  /**
   * S110 (A1, the gathered grain): the density cut to nothing where the bunching noise (wavelength `bunchPc`) is below
   * this level, a soft step of `gapSoft` either side - clumps and short strings of grain with empty stretches between
   * along the arms, as the goal's; 0 (or absent) no cut.
   */
  gap?: number;
  /** S110: the gap's soft step, in the noise's units (default 0.06). */
  gapSoft?: number;
  /**
   * S110 (A2, the sparkle's cost): above 0, the density's level (the ridge read, the costly part) read from a polar table
   * of TABLE_RINGS x TABLE_SECTORS corners over the disc, bilinear between them, in place of a read per proposal - so the
   * cost no longer grows with the count of points. 0 (or absent) the exact read.
   */
  table?: number;
  /**
   * S110 (A2, the field stars): this many faint points over the whole disc - between the arms and over the bar too - as a
   * second, sparser tier: area density exp(-R / fieldScale), tapered to nothing from 0.6 of `fieldEdge` to it; each
   * point's brightness the power law's (at most 20 times the faintest) times `fieldDim`. Drawn after the arms' points
   * from a stream of their own (the arms' points are unchanged by them); 0 (or absent) none.
   */
  field?: number;
  /** S110: the field stars' radial scale, kpc. */
  fieldScale?: number;
  /** S110: the field stars' outer edge, kpc. */
  fieldEdge?: number;
  /** S110: the field stars' brightness against the arms' faintest point's. */
  fieldDim?: number;
}

/** S110 (A2): the level table's polar grid (SparkleShape.table). */
export const TABLE_RINGS = 256;
export const TABLE_SECTORS = 1024;

/**
 * S110 (A2): a level read off a table - `f` read at the (TABLE_RINGS + 1) x TABLE_SECTORS corners of a polar grid out to
 * rMax, bilinear between them (round the turn, wrapped); 0 beyond rMax.
 */
export function tabulated(f: (r: number, phi: number) => number, rMax: number): (r: number, phi: number) => number {
  const nR = TABLE_RINGS;
  const nP = TABLE_SECTORS;
  const dR = rMax / nR;
  const dP = (2 * Math.PI) / nP;
  const t = new Float32Array((nR + 1) * nP);
  for (let i = 0; i <= nR; i++) for (let j = 0; j < nP; j++) t[i * nP + j] = f(i * dR, j * dP);
  return (r, phi) => {
    const u = r / dR;
    if (!(u >= 0) || u > nR) return 0;
    const i = Math.min(nR - 1, Math.floor(u));
    const fu = u - i;
    const v = ((((phi / (2 * Math.PI)) % 1) + 1) % 1) * nP;
    const j = Math.min(nP - 1, Math.floor(v));
    const fv = v - j;
    const j1 = (j + 1) % nP;
    const a = t[i * nP + j] * (1 - fu) + t[(i + 1) * nP + j] * fu;
    const b = t[i * nP + j1] * (1 - fu) + t[(i + 1) * nP + j1] * fu;
    return a * (1 - fv) + b * fv;
  };
}

/** A smooth value noise in [0, 1] at plane point (x, y) in lattice units (two octaves, the second half as strong). */
export function bunchNoise(x: number, y: number): number {
  const octave = (u: number, v: number, salt: number): number => {
    const i = Math.floor(u);
    const j = Math.floor(v);
    const fu = u - i;
    const fv = v - j;
    const su = fu * fu * (3 - 2 * fu);
    const sv = fv * fv * (3 - 2 * fv);
    const h = (a: number, b: number) => latticeHash(a + salt, b - salt);
    const top = h(i, j) * (1 - su) + h(i + 1, j) * su;
    const bottom = h(i, j + 1) * (1 - su) + h(i + 1, j + 1) * su;
    return top * (1 - sv) + bottom * sv;
  };
  return (2 * octave(x, y, 7919) + octave(2.03 * x + 0.5, 2.03 * y + 0.25, 104729)) / 3;
}

/** The shared map's lane plane as buildSparkle reads it: RGBA bytes (R the lanes, lanesMap.ts's sqrt(shape / 4)). */
export interface LanePlane {
  data: ArrayLike<number>;
  width: number;
  height: number;
  rHi: number;
}

/** The lanes' shape (lanesMap.ts: 1 at a full strand's centre) at (R, phi), nearest texel, 0 outside the map. */
export function laneShapeAt(l: LanePlane, r: number, phi: number): number {
  const c = Math.floor((r / l.rHi) * l.width);
  if (c < 0 || c >= l.width) return 0;
  const row = Math.floor(((((phi / (2 * Math.PI)) % 1) + 1) % 1) * l.height) % l.height;
  const b = l.data[(row * l.width + c) * 4] / 255;
  return 4 * b * b;
}

export interface Sparkle {
  /** Galaxy-frame (R kpc, phi rad, z kpc) per point. */
  radius: Float32Array;
  azimuth: Float32Array;
  height: Float32Array;
  /** Each point's brightness in units of the faintest. */
  weight: Float32Array;
  /** S110 (A2): how many of the points, at the end of the buffers, are field stars (SparkleShape.field); absent none. */
  field?: number;
}

/**
 * The arm share (the arm map's G channel: `stride` 4, `channel` 1; or a one-value-per-texel plane: 1, 0) at (R, phi),
 * linear between texels, 0 outside the grid.
 */
export function shareAt(map: Float32Array, g: ArmGrid, r: number, phi: number, stride = 4, channel = 1): number {
  const u = (r / g.rHi) * g.nR - 0.5;
  if (u < -0.5 || u > g.nR - 0.5) return 0;
  const v = ((((phi / (2 * Math.PI)) % 1) + 1) % 1) * g.nPhi - 0.5;
  const i0 = Math.max(0, Math.min(g.nR - 1, Math.floor(u)));
  const i1 = Math.min(g.nR - 1, i0 + 1);
  const fu = Math.min(1, Math.max(0, u - i0));
  const j0 = ((Math.floor(v) % g.nPhi) + g.nPhi) % g.nPhi;
  const j1 = (j0 + 1) % g.nPhi;
  const fv = v - Math.floor(v);
  const at = (i: number, j: number) => map[(j * g.nR + i) * stride + channel];
  return (at(i0, j0) * (1 - fu) + at(i1, j0) * fu) * (1 - fv) + (at(i0, j1) * (1 - fu) + at(i1, j1) * fu) * fv;
}

/** A gaussian deviate (Box-Muller) from the generator. */
const gauss = (next: () => number): number => Math.sqrt(-2 * Math.log(Math.max(1e-12, next()))) * Math.cos(2 * Math.PI * next());

/** A brightness from the power law: 1 to `range`, many faint, few bright. */
export function brightness(u: number, slope: number, range: number): number {
  return Math.min(range, Math.pow(Math.max(1e-9, 1 - u), -1 / Math.max(0.1, slope)));
}

/**
 * The points: deterministic in (map, grid, shape, seed). S106: `level` (the skeleton's grain density, skeleton.ts
 * grainDensity) read in place of the map's share where given - the floor, the ridge power, the lanes' avoidance and
 * the edge's taper apply to it as to the share.
 */
export function buildSparkle(
  map: Float32Array,
  g: ArmGrid,
  s: SparkleShape,
  seed: number,
  raw: Float32Array | null = null,
  lanes: LanePlane | null = null,
  levelOf: ((r: number, phi: number) => number) | null = null,
): Sparkle {
  const total = Math.max(0, Math.floor(s.count));
  const radius = new Float32Array(total);
  const azimuth = new Float32Array(total);
  const height = new Float32Array(total);
  const weight = new Float32Array(total);
  const next = rng(seed);
  const rMax = Math.min(s.rMax, g.rHi);
  const floor = Math.min(1, Math.max(0, s.floor ?? 0));
  const lift = s.lift ?? 0;
  const exact = levelOf
    ? levelOf
    : raw && lift > 0
      ? (r: number, phi: number) => Math.min(1, shareAt(raw, g, r, phi, 1, 0) / lift)
      : (r: number, phi: number) => shareAt(map, g, r, phi);
  // S110 (A2): the level off a table where asked (the cost then fixed, whatever the count).
  const level = (s.table ?? 0) > 0 ? tabulated(exact, rMax) : exact;
  const avoid = lanes ? Math.min(1, Math.max(0, s.avoid ?? 0)) : 0;
  const clear = avoid > 0 && lanes ? (r: number, phi: number) => Math.max(0, 1 - avoid * Math.min(1, laneShapeAt(lanes, r, phi))) : () => 1;
  const bunch = Math.min(1, Math.max(0, s.bunch ?? 0));
  const bunchBright = Math.max(0, s.bunchBright ?? 0);
  const lattice = Math.max(0.01, (s.bunchPc ?? 400) / 1000);
  const noiseAt = (r: number, phi: number) => bunchNoise((r * Math.cos(phi)) / lattice, (r * Math.sin(phi)) / lattice);
  // The bunching: 3 n^2 has a mean near 1 over the noise, so the count of points per arm is about kept.
  // S110 (A1): the gaps - below `gap` the noise empties the arm (the same noise as the bunching, read once).
  const gap = Math.min(0.95, Math.max(0, s.gap ?? 0));
  const gapSoft = Math.max(1e-3, s.gapSoft ?? 0.06);
  const lumps =
    bunch > 0 || gap > 0
      ? (r: number, phi: number) => {
          const n = noiseAt(r, phi);
          const kept = gap > 0 ? smoothstep(gap - gapSoft, gap + gapSoft, n) : 1;
          return kept * (1 - bunch + bunch * 3 * n * n);
        }
      : () => 1;
  const lift2 = bunchBright > 0 ? (r: number, phi: number) => Math.max(0.2, 1 + bunchBright * (2 * noiseAt(r, phi) - 1)) : () => 1;
  const density = (r: number, phi: number) =>
    clear(r, phi) * lumps(r, phi) * (floor + (1 - floor) * Math.pow(Math.max(0, level(r, phi)), s.ridge)) * (1 - smoothstep(0.7 * rMax, rMax, r));
  // (The density without the lanes' clearing, never below it: the envelope's bound.)
  const open = (r: number, phi: number) => lumps(r, phi) * (floor + (1 - floor) * Math.pow(Math.max(0, level(r, phi)), s.ridge)) * (1 - smoothstep(0.7 * rMax, rMax, r));
  // A place drawn against the density: area-uniform proposals, accepted with probability d (bounded tries).
  // S107 (MW2, `direct`): the same law drawn through an envelope - see envelopePlace.
  const place = s.direct ? envelopePlace(rMax, next, density, open) : (): [number, number] | null => {
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
  if (bunchBright > 0) for (let i = 0; i < k; i++) weight[i] *= lift2(radius[i], azimuth[i]);
  const field = Math.max(0, Math.floor(s.field ?? 0));
  if (field <= 0) return { radius: radius.subarray(0, k), azimuth: azimuth.subarray(0, k), height: height.subarray(0, k), weight: weight.subarray(0, k) };
  // S110 (A2): the field stars, after the arms' points, from a stream of their own.
  const f = fieldStars(field, s, (seed ^ 0x9e3779b9) >>> 0);
  const join = (a: Float32Array, b: Float32Array) => {
    const o = new Float32Array(k + b.length);
    o.set(a.subarray(0, k));
    o.set(b, k);
    return o;
  };
  return { radius: join(radius, f.radius), azimuth: join(azimuth, f.azimuth), height: join(height, f.height), weight: join(weight, f.weight), field: f.radius.length };
}

/** S110 (A2): the field stars (SparkleShape.field): area density exp(-R / scale), tapered over the edge; faint. */
export function fieldStars(count: number, s: SparkleShape, seed: number): Sparkle {
  const next = rng(seed);
  const edge = Math.max(0.5, s.fieldEdge ?? 16);
  const scale = Math.max(0.1, s.fieldScale ?? 4);
  const dim = Math.max(0, s.fieldDim ?? 0.3);
  const hz = s.heightPc / 1000;
  const radius = new Float32Array(count);
  const azimuth = new Float32Array(count);
  const height = new Float32Array(count);
  const weight = new Float32Array(count);
  let k = 0;
  for (let t = 0; k < count && t < 400 * count; t++) {
    const r = edge * Math.sqrt(next());
    const phi = 2 * Math.PI * next();
    if (next() >= Math.exp(-r / scale) * (1 - smoothstep(0.6 * edge, edge, r))) continue;
    radius[k] = r;
    azimuth[k] = phi;
    height[k] = gauss(next) * hz;
    weight[k] = brightness(next(), s.slope, Math.min(20, s.range)) * dim;
    k++;
  }
  return { radius: radius.subarray(0, k), azimuth: azimuth.subarray(0, k), height: height.subarray(0, k), weight: weight.subarray(0, k) };
}

/** The envelope's polar grid (S107, MW2): cells across R and round the turn. */
export const ENVELOPE_RINGS = 192;
export const ENVELOPE_SECTORS = 768;

/**
 * S107 (MW2, the sparkle's latency): places drawn from the law min(1, density) over the disc's area - the law the
 * area-uniform rejection draws from - through a piecewise envelope: the density without the lanes' clearing (`bound`,
 * never below the density) read at every corner of a polar grid, each cell's bound 1.3 times its corners' largest plus
 * 0.02 (at most 1); a cell chosen by its bound times its area, a place uniform in its area, accepted with min(1, d) over
 * the cell's bound. Most proposals fall on the arms, so a few hundred thousand reads of the density stand for the
 * millions the rejection over the whole disc made. The same law, other points (the stream is used otherwise).
 */
export function envelopePlace(
  rMax: number,
  next: () => number,
  density: (r: number, phi: number) => number,
  bound: (r: number, phi: number) => number,
): () => [number, number] | null {
  const nR = ENVELOPE_RINGS;
  const nP = ENVELOPE_SECTORS;
  const dR = rMax / nR;
  const dP = (2 * Math.PI) / nP;
  const corner = new Float32Array((nR + 1) * nP);
  for (let i = 0; i <= nR; i++) {
    const r = i * dR;
    for (let j = 0; j < nP; j++) corner[i * nP + j] = Math.min(1, bound(r, j * dP));
  }
  const env = new Float32Array(nR * nP);
  const cum = new Float64Array(nR * nP);
  let total = 0;
  for (let i = 0; i < nR; i++) {
    const area = 0.5 * dP * ((i + 1) * (i + 1) - i * i) * dR * dR;
    for (let j = 0; j < nP; j++) {
      const j1 = (j + 1) % nP;
      const m = Math.max(corner[i * nP + j], corner[i * nP + j1], corner[(i + 1) * nP + j], corner[(i + 1) * nP + j1]);
      const e = m > 0 ? Math.min(1, 1.3 * m + 0.02) : 0;
      env[i * nP + j] = e;
      total += e * area;
      cum[i * nP + j] = total;
    }
  }
  return () => {
    if (!(total > 0)) return null;
    for (let t = 0; t < 400; t++) {
      const u = next() * total;
      let lo = 0;
      let hi = cum.length - 1;
      while (lo < hi) {
        const mid = (lo + hi) >> 1;
        if (cum[mid] < u) lo = mid + 1;
        else hi = mid;
      }
      const i = Math.floor(lo / nP);
      const j = lo - i * nP;
      const r = dR * Math.sqrt(i * i + next() * (2 * i + 1));
      const phi = (j + next()) * dP;
      if (next() * env[lo] < Math.min(1, density(r, phi))) return [r, phi];
    }
    return null;
  };
}

/**
 * The sparkle's two sprite sizes (S106, the Milky Way's grain): the brightest `share` of the points (by weight; ties
 * at the threshold all bright) drawn on the larger sprite, the rest on the fine one. Returns each point's tier, 1 the
 * bright. A share of 0 or less: every point fine (the S105 drawing).
 */
export function sparkleTiers(weight: ArrayLike<number>, share: number): Uint8Array {
  const n = weight.length;
  const out = new Uint8Array(n);
  const big = Math.floor(n * Math.min(1, Math.max(0, share)));
  if (big <= 0) return out;
  const sorted = Float32Array.from(weight).sort();
  const threshold = sorted[n - big];
  for (let i = 0; i < n; i++) if (weight[i] >= threshold) out[i] = 1;
  return out;
}

/** The members of one tier: the indices whose tier is `tier`. */
export function tierIndices(tiers: Uint8Array, tier: number): Uint32Array {
  let n = 0;
  for (let i = 0; i < tiers.length; i++) if (tiers[i] === tier) n++;
  const out = new Uint32Array(n);
  let k = 0;
  for (let i = 0; i < tiers.length; i++) if (tiers[i] === tier) out[k++] = i;
  return out;
}

/**
 * Each point's light per channel: its weight times the base and the colour, times exp(-(R - start) / scale) outside
 * `start` (1 inside), so the sparkle fades outward as the disc's own light does and no point outshines a faint outer
 * disc. Scale 0 or less: no falloff.
 */
export function sparkleFlux(
  weight: ArrayLike<number>,
  radius: ArrayLike<number>,
  base: number,
  colour: readonly [number, number, number],
  start: number,
  scale: number,
): Float32Array {
  const out = new Float32Array(weight.length * 3);
  for (let i = 0; i < weight.length; i++) {
    const fall = scale > 0 ? Math.exp(-Math.max(0, radius[i] - start) / scale) : 1;
    for (let k = 0; k < 3; k++) out[3 * i + k] = weight[i] * base * colour[k] * fall;
  }
  return out;
}
