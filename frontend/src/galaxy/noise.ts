/**
 * The randomness layer's noise in float32 (S66, BUILD_III Phase V7; D226 R1, R9a): the TypeScript twin of the GLSL
 * include `noise.glsl.ts`, operation for operation, and the preparation of the tables the march uploads - pure
 * functions of the render header's entries (`gas_fluctuation`, `census_clustering`, `spurs`), no React, no three.
 *
 * Every float operation is rounded to float32 (`Math.fround`), in the model's own order (galaxy/layer/noise.py,
 * gas_fluctuation.py, census_clustering.py, stages/spurs.py: each function names the Python it twins); the integers
 * are uint32 (`Math.imul`, `>>> 0`). Held in `noise.test.ts` against `model/galaxy/layer/vectors.json`: the noise's
 * sections bit-exact to numpy's float32 column; the gas sum given the read positions too; the polar read itself to
 * float32's geometry (R1c: g within 5e-3 of float64, the map 1e-3 relative).
 *
 * The viewer computes no physics here (rule D5 as amended, D220's precedent): it evaluates functions the model
 * publishes, with every parameter the model's.
 */

import type { ClusteringEntry, GasFluctuationEntry, SpursEntry } from "../api";

const f = Math.fround;

// --- the hash: 32-bit integers only (noise.py: MIX_SHIFTS, MIX_MULTIPLIERS, SEED_SALT, lattice_hash) -------------

export const SEED_SALT = 0x9e3779b9;
export const MIX_MULTIPLIERS = [0x7feb352d, 0x846ca68b] as const;
const TWO_POW_MINUS_23 = 2 ** -23;
/** noise.py SQRT3 in float32: one over the standard deviation of a value uniform in [-1, 1). */
const SQRT3 = f(Math.sqrt(3));
export const TWO_PI = 2 * Math.PI;

/** `lowbias32` (noise.py `_mix`): x ^= x >> 16; x *= 0x7feb352d; x ^= x >> 15; x *= 0x846ca68b; x ^= x >> 16. */
export function mix32(h: number): number {
  h = (h ^ (h >>> 16)) >>> 0;
  h = Math.imul(h, MIX_MULTIPLIERS[0]) >>> 0;
  h = (h ^ (h >>> 15)) >>> 0;
  h = Math.imul(h, MIX_MULTIPLIERS[1] | 0) >>> 0;
  return (h ^ (h >>> 16)) >>> 0;
}

/** noise.py `_key`: the chain's first two steps, mix32(mix32(seed ^ SEED_SALT) ^ octave). */
export function hashKey(seed: number, octave: number): number {
  return mix32((mix32((seed ^ SEED_SALT) >>> 0) ^ octave) >>> 0);
}

/** An int to its uint32 (two's complement: GLSL's uint(int)). */
export const asUint = (i: number): number => i >>> 0;

/** noise.py `lattice_hash`: seed, octave and two or three integer coordinates to a uint32. */
export function latticeHash(seed: number, octave: number, ix: number, iy: number, iz?: number): number {
  let h = mix32((hashKey(seed, octave) ^ asUint(ix)) >>> 0);
  h = mix32((h ^ asUint(iy)) >>> 0);
  return iz === undefined ? h : mix32((h ^ asUint(iz)) >>> 0);
}

/** noise.py `lattice_value`: (h >> 8) * 2^-23 - 1, exact in float32. */
export function latticeValue(h: number): number {
  return f(f((h >>> 8) * TWO_POW_MINUS_23) - 1);
}

// --- one octave (noise.py noise2, noise3) ------------------------------------------------------------------------

/** noise.py `_fade`: t*t*t*(t*(t*6 - 15) + 10), left to right. */
function fade(t: number): number {
  return f(f(f(t * t) * t) * f(f(t * f(f(t * 6) - 15)) + 10));
}

/** noise.py `_cell`: (uint32 index, fade weight, variance factor 1 - 2 s (1 - s)). */
function cell(c: number): [number, number, number] {
  const base = Math.floor(c);
  const s = fade(f(c - base));
  return [asUint(base), s, f(1 - f(f(2 * s) * f(1 - s)))];
}

/** noise.py `noise2` in float32: one octave of 2-D value noise, unit variance at every point. */
export function noise2(seed: number, x: number, y: number, octave: number): number {
  const key = hashKey(seed, octave);
  const [ux, sx, nx] = cell(f(x));
  const [uy, sy, ny] = cell(f(y));
  const h0 = mix32((key ^ ux) >>> 0);
  const h1 = mix32((key ^ ((ux + 1) >>> 0)) >>> 0);
  const uy1 = (uy + 1) >>> 0;
  const v00 = latticeValue(mix32((h0 ^ uy) >>> 0));
  const v10 = latticeValue(mix32((h1 ^ uy) >>> 0));
  const v01 = latticeValue(mix32((h0 ^ uy1) >>> 0));
  const v11 = latticeValue(mix32((h1 ^ uy1) >>> 0));
  const a = f(v00 + f(sx * f(v10 - v00)));
  const b = f(v01 + f(sx * f(v11 - v01)));
  const r = f(a + f(sy * f(b - a)));
  return f(r * f(SQRT3 / f(Math.sqrt(f(nx * ny)))));
}

/** noise.py `noise3` in float32. */
export function noise3(seed: number, x: number, y: number, z: number, octave: number): number {
  const key = hashKey(seed, octave);
  const [ux, sx, nx] = cell(f(x));
  const [uy, sy, ny] = cell(f(y));
  const [uz, sz, nz] = cell(f(z));
  const uy1 = (uy + 1) >>> 0;
  const uz1 = (uz + 1) >>> 0;
  const h0 = mix32((key ^ ux) >>> 0);
  const h1 = mix32((key ^ ((ux + 1) >>> 0)) >>> 0);
  const h00 = mix32((h0 ^ uy) >>> 0);
  const h10 = mix32((h1 ^ uy) >>> 0);
  const h01 = mix32((h0 ^ uy1) >>> 0);
  const h11 = mix32((h1 ^ uy1) >>> 0);
  const alongX = (low: number, high: number, uk: number) => {
    const vl = latticeValue(mix32((low ^ uk) >>> 0));
    const vh = latticeValue(mix32((high ^ uk) >>> 0));
    return f(vl + f(sx * f(vh - vl)));
  };
  const a00 = alongX(h00, h10, uz);
  const a10 = alongX(h01, h11, uz);
  const a01 = alongX(h00, h10, uz1);
  const a11 = alongX(h01, h11, uz1);
  const b0 = f(a00 + f(sy * f(a10 - a00)));
  const b1 = f(a01 + f(sy * f(a11 - a01)));
  const r = f(b0 + f(sz * f(b1 - b0)));
  return f(r * f(SQRT3 / f(Math.sqrt(f(f(nx * ny) * nz)))));
}

// --- octave sums (noise.py fractal, fractal_coarsest), shear, the log-normal map ---------------------------------

/** An octave sum's numbers as the model publishes them (noise.octave_weights: a shader computes no power). */
export interface OctaveSum {
  seed: number;
  octaves: number;
  base_frequency: number;
  lacunarity: number;
  gain: number;
  top: number;
  norm: number;
}

/**
 * noise.py `fractal_coarsest` in float32: for each n of `kept`, octaves 0..n-1 at the whole sum's amplitudes, times
 * its normaliser; `kept` = [octaves] is `fractal`. `p` has two or three coordinates.
 */
export function fractalCoarsest(position: readonly number[], c: OctaveSum, kept: readonly number[]): number[] {
  const p = position.map(f); // the positions in the working precision first, as numpy's asarray(positions, float32)
  let fr = f(c.base_frequency);
  let a = f(1);
  let total = f(0);
  const step = f(c.lacunarity);
  const gain = f(c.gain);
  const norm = f(c.norm);
  const out = new Map<number, number>();
  const last = Math.max(...kept);
  for (let j = 0; j < last; j += 1) {
    if (j === c.octaves - 1) a = f(a * f(c.top));
    const n = p.length === 2 ? noise2(c.seed, f(p[0] * fr), f(p[1] * fr), j) : noise3(c.seed, f(p[0] * fr), f(p[1] * fr), f(p[2] * fr), j);
    total = f(total + f(a * n));
    fr = f(fr * step);
    a = f(a * gain);
    if (kept.includes(j + 1)) out.set(j + 1, f(total * norm));
  }
  return kept.map((n) => out.get(n) as number);
}

/** noise.py `fractal` in float32. */
export function fractal(p: readonly number[], c: OctaveSum): number {
  return fractalCoarsest(p, c, [c.octaves])[0];
}

/** noise.py `shear`: x' = x - strain y, y' = y. */
export function shear(x: number, y: number, strain: number): [number, number] {
  return [f(f(x) - f(f(strain) * f(y))), f(y)];
}

/** noise.py `lognormal_map` in float32: normaliser exp(sigma g - sigma^2 / 2), as (sigma g) - ((0.5 sigma) sigma). */
export function lognormalMap(g: number, sigma: number, normaliser = 1): number {
  const s = f(sigma);
  return f(f(normaliser) * f(Math.exp(f(f(s * f(g)) - f(f(0.5 * s) * s)))));
}

// --- the gas fluctuation field (gas_fluctuation.py GasFluctuationField) ------------------------------------------

/** The levels the field's tables are laid out in (D221 item 6): 32 level-0 rings of 32 sectors, a six-octave ladder. */
export const CELL_RINGS = 32;
export const CELL_SECTORS = 32;
export const GAS_OCTAVES = 6;
/** Floats per ring row of the gas table: inner edge, sigma, strain, twist (mod 2 pi), break index, norm, outer edge, 0. */
export const GAS_RING_STRIDE = 8;
/** Floats per weights row: the six octaves' weights, then two zeros. */
export const GAS_WEIGHT_STRIDE = 8;

/** The gas field's tables as the march uploads them, float32 throughout. */
export interface GasTables {
  seed: number;
  /** 1 / scale, kpc^-1: the coarsest octave's frequency, rounded once (gas_fluctuation._sum's ft(1 / scale)). */
  invScale: number;
  sense: number;
  /** 33 edges, kpc. */
  edges: Float32Array;
  /** 32 rows of GAS_RING_STRIDE. */
  ring: Float32Array;
  /** (octaves + 1) rows of GAS_WEIGHT_STRIDE: the weights for each break index. */
  weights: Float32Array;
  /** 1024 cell normalisers, ring-major (the texture's row a ring, its column a sector). */
  cells: Float32Array;
}

/**
 * The twist reduced modulo 2 pi in doubles before it is rounded to float32 (D226 R1c): the read angle sense (twist +
 * strain ln(R / R_r)) differs by whole turns, so the position is the same, and float32 keeps 2-3 more digits of it.
 */
export function reduceTwist(twist: number): number {
  return twist - TWO_PI * Math.round(twist / TWO_PI);
}

/** The gas field's tables from the render header's entry, or null with the layer off (its seed null) or off-form. */
export function prepareGas(entry: GasFluctuationEntry | null | undefined, reduce = true): GasTables | null {
  if (!entry || entry.seed === null || !entry.ring || !entry.edges || !entry.weights || !entry.cell_normaliser || entry.sense === null) return null;
  if (entry.octaves !== GAS_OCTAVES || entry.edges.length !== CELL_RINGS + 1 || entry.cell_normaliser.length !== CELL_RINGS * CELL_SECTORS) return null;
  const ring = new Float32Array(CELL_RINGS * GAS_RING_STRIDE);
  for (let r = 0; r < CELL_RINGS; r += 1) {
    const twist = entry.ring.twist[r];
    ring.set([entry.edges[r], entry.ring.sigma[r], entry.ring.strain[r], reduce ? reduceTwist(twist) : twist,
      entry.ring.break_octave[r], entry.ring.norm[r], entry.edges[r + 1], 0], r * GAS_RING_STRIDE);
  }
  const weights = new Float32Array(entry.weights.length * GAS_WEIGHT_STRIDE);
  entry.weights.forEach((row, b) => weights.set(row, b * GAS_WEIGHT_STRIDE));
  return {
    seed: entry.seed >>> 0,
    invScale: f(1 / entry.scale),
    sense: f(entry.sense),
    edges: Float32Array.from(entry.edges),
    ring,
    weights,
    cells: Float32Array.from(entry.cell_normaliser),
  };
}

/** gas_fluctuation `ring_of`: the last edge not above R, held to the first and last rings. */
export function ringOf(R: number, edges: Float32Array): number {
  let lo = 0;
  let hi = edges.length - 2;
  if (R < edges[1]) return 0;
  while (lo < hi) {
    const mid = (lo + hi + 1) >> 1;
    if (edges[mid] <= R) lo = mid;
    else hi = mid - 1;
  }
  return lo;
}

/** gas_fluctuation `evaluate`'s sector: floor((atan2(y, x) mod 2 pi) / (2 pi / 32)), held to 0..31. */
export function sectorOf(x: number, y: number): number {
  let phi = Math.atan2(y, x);
  if (phi < 0) phi += TWO_PI;
  return Math.min(CELL_SECTORS - 1, Math.max(0, Math.floor(phi / (TWO_PI / CELL_SECTORS))));
}

/**
 * gas_fluctuation `read_positions` in float32, with ring r's numbers: R = hypot(x, y), theta = sense (twist + strain
 * log(max(R, R_0) / R_r)), and the point (R cos, R sin)(atan2(y, x) - theta) as the same point by rotation, (x cos theta
 * + y sin theta, y cos theta - x sin theta) - the GLSL's form (noise.glsl.ts layerGasRead), which needs no atan2 and no
 * cos and sin of the larger angle phi - theta (S66: on the RTX 4070 the polar form put g 5e-2 from float64 at 24 kpc).
 */
export function gasReadPosition(x: number, y: number, ring: number, t: GasTables): [number, number] {
  x = f(x);
  y = f(y);
  const row = ring * GAS_RING_STRIDE;
  const R = f(Math.hypot(x, y));
  const L = f(Math.log(f(f(Math.max(R, t.edges[0])) / t.ring[row])));
  const theta = f(t.sense * f(t.ring[row + 3] + f(t.ring[row + 2] * L)));
  const c = f(Math.cos(theta));
  const s = f(Math.sin(theta));
  return [f(f(x * c) + f(y * s)), f(f(y * c) - f(x * s))];
}

/** gas_fluctuation `_sum` in float32: sum_j w[b_r][j] noise2(seed, X f_j, Y f_j, j), f stepped by doubling. */
export function gasSum(X: number, Y: number, ring: number, t: GasTables): number {
  const w = Math.round(t.ring[ring * GAS_RING_STRIDE + 4]) * GAS_WEIGHT_STRIDE;
  let fr = t.invScale;
  let total = f(0);
  for (let j = 0; j < GAS_OCTAVES; j += 1) {
    total = f(total + f(t.weights[w + j] * noise2(t.seed, f(X * fr), f(Y * fr), j)));
    fr = f(fr * 2);
  }
  return total;
}

/** gas_fluctuation `gaussian`: the unit-variance sum at a face-on position, its own ring's ladder and shear. */
export function gasGaussian(x: number, y: number, t: GasTables): number {
  const ring = ringOf(Math.hypot(x, y), t.edges);
  const [X, Y] = gasReadPosition(x, y, ring, t);
  return gasSum(X, Y, ring, t);
}

/** gas_fluctuation `evaluate` in float32: normaliser_cell exp(sigma_r g - sigma_r^2 / 2); unit mean in every cell. */
export function gasMap(x: number, y: number, t: GasTables): number {
  const ring = ringOf(Math.hypot(x, y), t.edges);
  const [X, Y] = gasReadPosition(x, y, ring, t);
  const g = gasSum(X, Y, ring, t);
  return lognormalMap(g, t.ring[ring * GAS_RING_STRIDE + 1], t.cells[ring * CELL_SECTORS + sectorOf(x, y)]);
}

// --- the clustering field (census_clustering.py ClusteringField.maps) ---------------------------------------------

/** The clustering field's numbers and its k-octave cell means as the march uploads them. */
export interface ClusteringTables extends OctaveSum {
  sigma: number;
  /** 3 × 1024: the k-octave means, k = 1, 2, 3 (row k - 1), ring-major. */
  cellMean: Float32Array;
  /** Myr, coarsest octave first. */
  octaveAgesMyr: number[];
}

/** The clustering tables from the render header's entry, or null with the layer off or off-form (three octaves). */
export function prepareClustering(entry: ClusteringEntry | null | undefined): ClusteringTables | null {
  if (!entry || entry.seed === null || !entry.cell_mean || entry.octaves !== 3) return null;
  const cellMean = new Float32Array(3 * CELL_RINGS * CELL_SECTORS);
  for (let k = 1; k <= 3; k += 1) {
    const row = entry.cell_mean[String(k)];
    if (!row || row.length !== CELL_RINGS * CELL_SECTORS) return null;
    cellMean.set(row, (k - 1) * CELL_RINGS * CELL_SECTORS);
  }
  return {
    seed: entry.seed >>> 0, octaves: entry.octaves, base_frequency: 1 / entry.scale, lacunarity: entry.lacunarity,
    gain: entry.gain, top: entry.top, norm: entry.norm, sigma: entry.sigma, cellMean, octaveAgesMyr: entry.octave_ages_myr,
  };
}

/** ClusteringField.maps at (x, y) kpc, kept (1, 2, 3), in float32: the three log-normal maps of the truncated sums. */
export function clusteringMaps(x: number, y: number, t: ClusteringTables): [number, number, number] {
  const [g1, g2, g3] = fractalCoarsest([x, y], t, [1, 2, 3]);
  return [lognormalMap(g1, t.sigma), lognormalMap(g2, t.sigma), lognormalMap(g3, t.sigma)];
}

// --- the gas spurs (stages/spurs.py Spurs) ---------------------------------------------------------------------------

/** Floats per spur row: ln R_f, phi_f, A, F | sin p, cos p, T, lambda | sigma, T sin p, 0, 0 (three RGBA texels). */
export const SPUR_STRIDE = 12;

/** The spurs' table as the march uploads it: each row's derived numbers (Spurs.__post_init__), float32. */
export interface SpurTables {
  count: number;
  rows: Float32Array;
  turn: number;
  /** REACH: a spur is read where its nearest point to the ring lies within this many dispersions. */
  reach: number;
}

/** Spurs.__post_init__'s derived numbers per row, computed in doubles and rounded once; null with the layer off. */
export function prepareSpurs(entry: SpursEntry | null | undefined): SpurTables | null {
  if (!entry || !entry.rows || entry.turn === null) return null;
  const n = entry.rows.radius.length;
  const rows = new Float32Array(n * SPUR_STRIDE);
  for (let j = 0; j < n; j += 1) {
    const radius = entry.rows.radius[j];
    const pitch = (entry.rows.pitch[j] * Math.PI) / 180;
    const span = entry.rows.length[j] / radius;
    rows.set([
      Math.log(radius), entry.rows.azimuth[j], entry.rows.contrast[j], entry.rows.fall[j],
      Math.sin(pitch), Math.cos(pitch), span, Math.log(entry.rows.fall[j]) / span,
      entry.rows.width[j] / entry.fwhm_per_sigma, span * Math.sin(pitch), 0, 0,
    ], j * SPUR_STRIDE);
  }
  return { count: n, rows, turn: f(entry.turn), reach: f(entry.reach) };
}

/** Spurs.reads: whether spur j is read at radius R - R times the gap in ln R past its foot or tip within reach dispersions. */
export function spurReads(R: number, j: number, t: SpurTables): boolean {
  const o = j * SPUR_STRIDE;
  const x = f(Math.log(f(R)));
  const gap = Math.max(Math.max(f(t.rows[o] - x), f(x - f(t.rows[o] + t.rows[o + 9]))), 0);
  return f(f(R) * gap) <= f(t.reach * t.rows[o + 8]);
}

/** Spurs.excess in float32: spur j's E at (R, phi), its three stretches (the foot's cap, the middle, the tip's cap). */
export function spurExcess(R: number, phi: number, j: number, t: SpurTables): number {
  const o = j * SPUR_STRIDE;
  const r = t.rows;
  R = f(R);
  const dx = f(f(Math.log(R)) - r[o]);
  const s = r[o + 4];
  const c = r[o + 5];
  const T = r[o + 6];
  const middle = f(f(0.5 * T) * c);
  // psi = middle + mod(turn (phi - phi_f) - middle + pi, 2 pi) - pi (numpy's mod: the result has the divisor's sign)
  const u = f(f(f(t.turn * f(f(phi) - r[o + 1])) - middle) + f(Math.PI));
  const twoPi = f(TWO_PI);
  const wrapped = f(u - f(twoPi * Math.floor(f(u / twoPi))));
  const psi = f(f(middle + wrapped) - f(Math.PI));
  const across = f(f(dx * c) - f(psi * s));
  const along = f(f(dx * s) + f(psi * c));
  const q = f(R / r[o + 8]);
  const inv2 = f(0.5 * f(q * q));
  const gap = along < 0 ? along : along > T ? f(along - T) : 0;
  const height = along < 0 ? 1 : along > T ? f(1 / r[o + 3]) : f(Math.exp(f(-r[o + 7] * Math.min(Math.max(along, 0), T))));
  return f(f(r[o + 2] * height) * f(Math.exp(f(-f(f(f(across * across) + f(gap * gap)) * inv2)))));
}

/** Spurs.at in float32: the sum of every spur the point's radius reads, in the table's order. */
export function spurSum(R: number, phi: number, t: SpurTables): number {
  let total = f(0);
  for (let j = 0; j < t.count; j += 1) {
    if (spurReads(R, j, t)) total = f(total + spurExcess(R, phi, j, t));
  }
  return total;
}

// --- the textures' layouts (noise.glsl.ts' tables): row-major texel arrays, four floats a texel -------------------

/** `uGasRing`, 32 x 2 RGBA: texel (r, 0) = (inner edge, sigma, strain, twist), (r, 1) = (break index, norm, outer edge, 0). */
export function gasRingTexels(t: GasTables): Float32Array {
  const out = new Float32Array(CELL_RINGS * 2 * 4);
  for (let r = 0; r < CELL_RINGS; r += 1) {
    out.set(t.ring.subarray(r * GAS_RING_STRIDE, r * GAS_RING_STRIDE + 4), r * 4);
    out.set(t.ring.subarray(r * GAS_RING_STRIDE + 4, r * GAS_RING_STRIDE + 8), (CELL_RINGS + r) * 4);
  }
  return out;
}

/** `uGasWeights`, (octaves + 1) x 2 RGBA: texel (b, 0) = weights 0-3, (b, 1) = weights 4-5, 0, 0. */
export function gasWeightTexels(t: GasTables): Float32Array {
  const rows = t.weights.length / GAS_WEIGHT_STRIDE;
  const out = new Float32Array(rows * 2 * 4);
  for (let b = 0; b < rows; b += 1) {
    out.set(t.weights.subarray(b * GAS_WEIGHT_STRIDE, b * GAS_WEIGHT_STRIDE + 4), b * 4);
    out.set(t.weights.subarray(b * GAS_WEIGHT_STRIDE + 4, b * GAS_WEIGHT_STRIDE + 8), (rows + b) * 4);
  }
  return out;
}

/**
 * The march's k-octave cell means (S66, D226 R5c), 32 x 32 RGBA, column a sector and row a level-0 ring (the gas
 * cells' layout): texel (sector, ring) = (mean k = 3, mean k = 2, mean k = 1, 0) - the order of KEPT_OCTAVES
 * (interface/ages.js) and of the march's three clump textures. Read at its own texel (nearest).
 */
export function clusterMeanTexels(t: ClusteringTables): Float32Array {
  const cells = CELL_RINGS * CELL_SECTORS;
  const out = new Float32Array(cells * 4);
  for (let c = 0; c < cells; c += 1) {
    for (let k = 3; k >= 1; k -= 1) out[c * 4 + (3 - k)] = t.cellMean[(k - 1) * cells + c];
  }
  return out;
}

/** `uSpurs`, (3 count) x 1 RGBA: the rows as they are (SPUR_STRIDE is three texels). */
export function spurTexels(t: SpurTables): Float32Array {
  return t.rows.length > 0 ? t.rows : new Float32Array(SPUR_STRIDE);
}

/**
 * The scalar uniforms the include reads, from the prepared tables (absent tables leave their uniforms unset). The
 * clustering field's coarsest frequency is rounded once, as numpy's ft(base_frequency).
 */
export function noiseScalars(gas: GasTables | null, clustering: ClusteringTables | null, spurs: SpurTables | null): Record<string, number> {
  const out: Record<string, number> = {};
  if (gas) Object.assign(out, { uGasSeed: gas.seed, uGasInvScale: gas.invScale, uGasSense: gas.sense, uGasEdge0: gas.edges[0] });
  if (clustering) {
    Object.assign(out, {
      uClusterSeed: clustering.seed, uClusterInvScale: f(clustering.base_frequency), uClusterGain: f(clustering.gain),
      uClusterTop: f(clustering.top), uClusterNorm: f(clustering.norm), uClusterSigma: f(clustering.sigma),
    });
  }
  if (spurs) Object.assign(out, { uSpurTurn: spurs.turn, uSpurReach: spurs.reach });
  return out;
}
