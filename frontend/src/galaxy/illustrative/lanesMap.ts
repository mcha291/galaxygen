// The dust lanes' map (S107, BUILD_VIII row 107, D275): a polar raster of extra face-on A_V built on the client from
// published geometry - the arm pieces' loci (model/galaxy/layer/arm_pieces.py), the bar's scalars and the m = 2 phase
// of pattern_density_contrast, the gas contrast along each ridge. Pure functions of an /api/arrays frame and the
// shaping parameters: no React, no three, no clock. Everything here is ILLUSTRATIVE: where a lane wanders, breaks and
// feathers is the viewer's own seeded drawing, tuned to the goal pictures, and no number of the model.
//
// The geometry of one arm piece (arm_pieces.py Piece.reach / advance / ends; the model's rotation sense is -1, its
// `turn` +1): from its inner end (r0, phi0) the piece runs out to r0 exp(extent |tan pitch|), its azimuth moving by
// extent - growing for a pitch that is positive or exactly 0, falling for a negative one - in proportion to ln R:
//     ln R(t) = ln r0 + t extent |tan pitch|,   phi(t) = phi0 + t extent sign(tan pitch),   t in [0, 1].
// A chain's pieces join end to end; a template's measured piece of negative pitch is entered by its inner end, which
// is its HIGH-azimuth end, so a chain's path takes each piece from whichever of its ends lies at the path's end.
//
// The map: LANE_MAP.rings x LANE_MAP.sectors texels over 0-rHi and one turn (15 pc by 0.1 degree at rHi = 30 kpc),
// each a byte holding sqrt(shape / LANE_MAP.shapeMax), shape 1 at the centre of one full-depth strand. The feature's
// GLSL (lanes.ts) reads it as the shared map's R channel (index.ts illMap) and multiplies by the depth slider, so depth
// is a uniform and no rebuild.

import type { IllFrame } from "./feature";

const TAU = 2 * Math.PI;

/** The map's size and scale: texels along R and round phi, and the shape drawn at byte 255. */
export const LANE_MAP = { rings: 2000, sectors: 3600, shapeMax: 4 } as const;

/** The /api/arrays names the lanes read: the arm pieces' columns, the two contrast fields and the bar's scalars. */
export const LANE_ARRAYS = [
  "arm_piece_chain",
  "arm_piece_order",
  "arm_piece_start_radius",
  "arm_piece_start_azimuth",
  "arm_piece_pitch",
  "arm_piece_extent",
  "arm_piece_join",
  "gas_density_contrast",
  "pattern_density_contrast",
  "bar_half_length",
  "bar_axis_ratio",
] as const;

/** One arm piece as the model's table states it. */
export interface Piece {
  chain: number;
  order: number;
  /** kpc */
  r0: number;
  /** rad */
  phi0: number;
  pitchDeg: number;
  /** rad */
  extent: number;
  /** 0 none, 1 its inner end meets another chain, 2 its outer end does (arm_pieces.py PIECE_JOINS). */
  join: number;
}

/** The point of a piece at t in [0, 1] from its inner end: arm_pieces.py Piece.ends, the model's turn (+1). */
export function piecePoint(p: Piece, t: number): { r: number; phi: number } {
  const tan = Math.tan((p.pitchDeg * Math.PI) / 180);
  return { r: p.r0 * Math.exp(t * p.extent * Math.abs(tan)), phi: p.phi0 + t * p.extent * (tan >= 0 ? 1 : -1) };
}

/** A piece's length along its locus, kpc: (r1 - r0) / sin|pitch|, an arc r0 extent where the pitch is nothing. */
export function pieceLength(p: Piece): number {
  const pitch = Math.abs((p.pitchDeg * Math.PI) / 180);
  const r1 = piecePoint(p, 1).r;
  return pitch < 1e-6 ? p.r0 * p.extent : (r1 - p.r0) / Math.sin(pitch);
}

const numbers = (a: unknown): ArrayLike<number> | null => (a && typeof a === "object" && "length" in a && !(a instanceof BigInt64Array) ? (a as ArrayLike<number>) : null);

/** The frame's arm pieces, by chain and inside out along each chain (the table's own order restated). */
export function piecesOf(frame: IllFrame | null): Piece[] {
  if (!frame) return [];
  const col = (name: string) => numbers(frame.arrays[`arm_piece_${name}`]);
  const chain = col("chain");
  const order = col("order");
  const r0 = col("start_radius");
  const phi0 = col("start_azimuth");
  const pitch = col("pitch");
  const extent = col("extent");
  const join = col("join");
  if (!chain || !order || !r0 || !phi0 || !pitch || !extent) return [];
  const out: Piece[] = [];
  for (let i = 0; i < chain.length; i += 1) {
    const piece = { chain: Number(chain[i]), order: Number(order[i]), r0: Number(r0[i]), phi0: Number(phi0[i]), pitchDeg: Number(pitch[i]), extent: Number(extent[i]), join: join ? Number(join[i]) : 0 };
    if ([piece.r0, piece.phi0, piece.pitchDeg, piece.extent].every(Number.isFinite) && piece.r0 > 0 && piece.extent > 0) out.push(piece);
  }
  return out.sort((a, b) => a.chain - b.chain || a.order - b.order);
}

/**
 * A path sampled along its length: positions in the model's plane (x = R cos phi, y = R sin phi, kpc), the unit
 * tangent, the unit normal to the path's INNER side (the side of the centre: the concave side of a trailing arm), the
 * length run so far, and whether each end fades (an end that meets another chain does not).
 */
export interface Ridge {
  chain: number;
  n: number;
  x: Float64Array;
  y: Float64Array;
  tx: Float64Array;
  ty: Float64Array;
  nx: Float64Array;
  ny: Float64Array;
  /** kpc along the path, 0 at its first point. */
  s: Float64Array;
  length: number;
  fadeIn: boolean;
  fadeOut: boolean;
  /** S106: a depth multiplier per point (the skeleton's strength), multiplied into the gas's weight; absent 1. */
  weight?: Float32Array;
}

/** A path's points given, its tangents (smoothed over `smooth` kpc), inward normals and lengths filled in. */
export function ridgeOfPoints(chain: number, xs: number[], ys: number[], smooth: number, fadeIn = true, fadeOut = true): Ridge {
  const n = xs.length;
  const x = Float64Array.from(xs);
  const y = Float64Array.from(ys);
  const s = new Float64Array(n);
  for (let i = 1; i < n; i += 1) s[i] = s[i - 1] + Math.hypot(x[i] - x[i - 1], y[i] - y[i - 1]);
  const rawX = new Float64Array(n);
  const rawY = new Float64Array(n);
  for (let i = 0; i < n; i += 1) {
    const a = Math.max(0, i - 1);
    const b = Math.min(n - 1, i + 1);
    const d = Math.hypot(x[b] - x[a], y[b] - y[a]) || 1;
    rawX[i] = (x[b] - x[a]) / d;
    rawY[i] = (y[b] - y[a]) / d;
  }
  // A running mean of the tangent over `smooth` kpc: a kink between two pieces turns the lane over that length instead
  // of stepping it sideways by the offset times the kink's angle.
  const tx = new Float64Array(n);
  const ty = new Float64Array(n);
  const nx = new Float64Array(n);
  const ny = new Float64Array(n);
  let lo = 0;
  let hi = 0;
  let sumX = 0;
  let sumY = 0;
  for (let i = 0; i < n; i += 1) {
    while (hi < n && s[hi] <= s[i] + smooth / 2) {
      sumX += rawX[hi];
      sumY += rawY[hi];
      hi += 1;
    }
    while (s[lo] < s[i] - smooth / 2) {
      sumX -= rawX[lo];
      sumY -= rawY[lo];
      lo += 1;
    }
    const d = Math.hypot(sumX, sumY) || 1;
    tx[i] = sumX / d;
    ty[i] = sumY / d;
    // The normal on the centre's side: perpendicular to the tangent, its radial part inward.
    const side = -ty[i] * x[i] + tx[i] * y[i] <= 0 ? 1 : -1;
    nx[i] = -ty[i] * side;
    ny[i] = tx[i] * side;
  }
  return { chain, n, x, y, tx, ty, nx, ny, s, length: n > 0 ? s[n - 1] : 0, fadeIn, fadeOut };
}

/** How far apart two (ln R, phi) points are, the azimuth within a turn. */
const apart = (a: { r: number; phi: number }, b: { r: number; phi: number }) => Math.hypot(Math.log(a.r / b.r), Math.atan2(Math.sin(a.phi - b.phi), Math.cos(a.phi - b.phi)));

/**
 * One chain's ridge: its pieces in order, each taken from whichever end lies at the path's end so far, sampled every
 * `step` kpc along the locus.
 */
export function chainRidge(pieces: readonly Piece[], step: number, smooth = 0.3): Ridge {
  const xs: number[] = [];
  const ys: number[] = [];
  let end: { r: number; phi: number } | null = null;
  pieces.forEach((p, k) => {
    const inner = piecePoint(p, 0);
    const outer = piecePoint(p, 1);
    let forward = true;
    if (end) forward = apart(inner, end) <= apart(outer, end);
    else if (pieces.length > 1) {
      // The first piece ends where the second begins: at whichever of its ends lies nearer either end of the second.
      const next = pieces[1];
      const ends = [piecePoint(next, 0), piecePoint(next, 1)];
      forward = Math.min(...ends.map((e) => apart(outer, e))) <= Math.min(...ends.map((e) => apart(inner, e)));
    }
    const count = Math.max(1, Math.ceil(pieceLength(p) / step));
    const tan = Math.abs(Math.tan((p.pitchDeg * Math.PI) / 180));
    const r1 = outer.r;
    for (let i = k === 0 ? 0 : 1; i <= count; i += 1) {
      // Even steps of length: along a log spiral the length run is proportional to R - r0.
      const f = forward ? i / count : 1 - i / count;
      const r = p.r0 + f * (r1 - p.r0);
      const t = tan * p.extent > 1e-9 ? Math.log(r / p.r0) / (tan * p.extent) : f;
      const at = piecePoint(p, t);
      xs.push(at.r * Math.cos(at.phi));
      ys.push(at.r * Math.sin(at.phi));
    }
    end = forward ? outer : inner;
  });
  const first = pieces[0];
  const last = pieces[pieces.length - 1];
  // An end that meets another chain is not faded (the model's rule for a join: it runs at full height into the arm).
  return ridgeOfPoints(first?.chain ?? 0, xs, ys, smooth, first?.join !== 1, last?.join !== 2);
}

/** Every chain's ridge. */
export function ridgesOf(pieces: readonly Piece[], step: number): Ridge[] {
  const chains = new Map<number, Piece[]>();
  for (const p of pieces) chains.set(p.chain, [...(chains.get(p.chain) ?? []), p]);
  return [...chains.keys()].sort((a, b) => a - b).map((c) => chainRidge(chains.get(c)!, step));
}

/**
 * The bar's position angle (rad, in [0, pi)) read off a published field: half the phase of the m = 2 harmonic of
 * pattern_density_contrast over the rings between 0.2 and 0.6 of the bar's half-length. NaN without a bar.
 * (The model's own convention, ln(half-length) cot(pitch), is not published; this reads where the bar was laid.)
 */
export function barAngle(pattern: ArrayLike<number> | null, rings: number, sectors: number, rHi: number, halfLength: number): number {
  if (!pattern || !(halfLength > 0) || pattern.length !== rings * sectors) return NaN;
  let c = 0;
  let s = 0;
  for (let i = 0; i < rings; i += 1) {
    const r = ((i + 0.5) * rHi) / rings;
    if (r < 0.2 * halfLength || r > 0.6 * halfLength) continue;
    for (let j = 0; j < sectors; j += 1) {
      const phi = ((j + 0.5) * TAU) / sectors;
      const v = Number(pattern[i * sectors + j]);
      c += v * Math.cos(2 * phi);
      s += v * Math.sin(2 * phi);
    }
  }
  if (Math.hypot(c, s) < 1e-9) return NaN;
  const angle = 0.5 * Math.atan2(s, c);
  return angle < 0 ? angle + Math.PI : angle;
}

// --- the seeded wander: integers only, then smooth interpolation (a seed of the viewer's own; never a clock) -------

/** lowbias32. */
function mix(h: number): number {
  h = (h ^ (h >>> 16)) >>> 0;
  h = Math.imul(h, 0x7feb352d) >>> 0;
  h = (h ^ (h >>> 15)) >>> 0;
  h = Math.imul(h, 0x846ca68b) >>> 0;
  return (h ^ (h >>> 16)) >>> 0;
}

/** A key from the seed and up to three labels (chain, strand, which quantity). */
export const laneKey = (seed: number, a = 0, b = 0, c = 0): number => mix((mix((mix((mix((seed ^ 0x9e3779b9) >>> 0) ^ (a >>> 0)) >>> 0) ^ (b >>> 0)) >>> 0) ^ (c >>> 0)) >>> 0);

/** A number in [0, 1) from a key and an index. */
export const laneRandom = (key: number, i: number): number => mix((key ^ mix(i >>> 0)) >>> 0) / 4294967296;

/** Smooth value noise in [-1, 1] along a line, its lattice at the integers. */
export function laneNoise(x: number, key: number): number {
  const i = Math.floor(x);
  const f = x - i;
  const u = f * f * f * (f * (f * 6 - 15) + 10);
  const a = laneRandom(key, i) * 2 - 1;
  const b = laneRandom(key, i + 1) * 2 - 1;
  return a + (b - a) * u;
}

/** Two octaves of it, still about [-1, 1]. */
const wander = (x: number, key: number): number => (laneNoise(x, key) + 0.5 * laneNoise(x * 2.07 + 13.7, key ^ 0x5bd1e995)) / 1.5;

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));
const smoothstep = (e0: number, e1: number, v: number) => {
  const t = clamp01((v - e0) / (e1 - e0));
  return t * t * (3 - 2 * t);
};

/** The lanes' shaping parameters: lanes.ts's controls by their keys (lengths in pc or kpc as each control states). */
export interface LaneShape {
  /** pc: the lane's centre line to the inner side of the ridge. */
  offset: number;
  /** pc: one strand's full width at half depth. */
  width: number;
  strands: number;
  /** pc: the band the strands braid across. */
  spread: number;
  /** pc: a strand's fine sideways wiggle. */
  wiggle: number;
  /** kpc: the wiggle's length. */
  wiggleLength: number;
  /** kpc: the length over which the strands cross. */
  braidLength: number;
  /** 0-0.9: the share of a lane's length that is broken away. */
  gaps: number;
  /** kpc: the length of the pieces and the breaks. */
  gapLength: number;
  /** 0-1: how much a strand's width and depth swell and thin along it. */
  clump: number;
  /** 0-1: a faint wide band under the strands, of the first strand's depth times this. */
  envelope: number;
  /** 0-1: how far the depth follows the gas contrast along the ridge. */
  followGas: number;
  /** kpc: a chain's free ends fade over this. */
  taper: number;
  /** kpc: lanes fade to nothing inside this radius. */
  innerRadius: number;
  /** kpc: lanes fade to nothing from 0.55 of this radius out to it. */
  outerRadius: number;
  /** kpc between feathers along a lane; 0 none. */
  featherSpacing: number;
  /** kpc */
  featherLength: number;
  /** degrees more open than the arm at its root. */
  featherPitch: number;
  /** x a strand's depth. */
  featherDepth: number;
  /** x a strand's depth: short thin wisps leaving the strands at a low angle, either side; 0 none. */
  fray: number;
  /** x a strand's depth; 0 no bar lanes. */
  barDepth: number;
  /** the lanes' distance from the bar's long axis, as a share of the bar's half-width. */
  barOffset: number;
  /** pc */
  barWidth: number;
  /** how late the lane turns in to the bar's end: 1 a straight line, higher a lane parallel to the axis that turns at the end. */
  barCurve: number;
  /** where the lane begins, as a share of the bar's half-length. */
  barReach: number;
  seed: number;
  /** S106: 1 the lanes drawn along the arms' traced crests (LaneGeometry.traced), 0 along the model's arm pieces. */
  trace: number;
  /** S106 (B3): 1 the arms' lanes drawn along the arm skeleton's ridges (LaneGeometry.skeleton); absent or 0 not. */
  skeleton?: number;
  /** S106 (B3): the bar lanes' curl round the nucleus, a share of its 220 degrees; absent 1 (S107's curl), 0 straight. */
  barCurl?: number;
}

export const SHAPE_KEYS: readonly (keyof LaneShape)[] = [
  "offset", "width", "strands", "spread", "wiggle", "wiggleLength", "braidLength", "gaps", "gapLength", "clump", "envelope", "followGas", "taper",
  "innerRadius", "outerRadius", "featherSpacing", "featherLength", "featherPitch", "featherDepth", "fray", "barDepth", "barOffset", "barWidth", "barCurve", "barReach", "seed", "trace", "skeleton", "barCurl",
];

/** What the map is drawn from: the ridges, the gas contrast to weigh them by, and the bar. */
export interface LaneGeometry {
  rHi: number;
  pieces: Piece[];
  gas: { values: ArrayLike<number>; rings: number; sectors: number } | null;
  bar: { halfLength: number; axisRatio: number; angle: number } | null;
  /** S106: the arms' own crests traced into ridges (traceRidges), drawn in place of the pieces where the shape's `trace` is on. */
  traced?: Ridge[] | null;
  /** S106 (B3): the arm skeleton's ridges (lanes.ts skeletonRidges), drawn in place of the pieces where the shape's `skeleton` is on. */
  skeleton?: Ridge[] | null;
}

/** A peak of the arms' ridge lines (armsField.ts ArmPeak): ring i, azimuth cell j, height in [0, 1]. */
export interface TracePeak {
  i: number;
  j: number;
  height: number;
}

/**
 * The arms' crests traced into ridges (S106, the Milky Way's picture; display-only, the lead's ruling 12): the ridge
 * lines' peaks (armsField.ts armPeaks) linked ring to ring outward - a peak joins the track whose last crest, carried
 * along the measured winding k (dphi / dlnR), lies within `reach` cells of it and no more than `skip` rings back -
 * and each track of at least `minLength` kpc resampled every `step` kpc into a Ridge. So a lane lies on the arm the
 * picture draws (its sparkle, its glow), not on the model's arm pieces where the two part.
 */
export function traceRidges(
  peaks: readonly TracePeak[],
  grid: { nR: number; nPhi: number; rHi: number },
  k: number,
  step: number,
  opts: { reach?: number; skip?: number; minLength?: number; minHeight?: number } = {},
): Ridge[] {
  const reach = opts.reach ?? 4;
  const skip = opts.skip ?? 4;
  const minLength = opts.minLength ?? 1.5;
  const minHeight = opts.minHeight ?? 0.15;
  const dR = grid.rHi / grid.nR;
  const P = grid.nPhi;
  const cell = TAU / P;
  type Track = { i: number[]; phi: number[]; last: number; lastPhi: number };
  // dphi / dlnR over a track's last ten crests (least squares).
  const slopeOf = (tr: Track): number => {
    const n = Math.min(10, tr.i.length);
    let sx = 0, sy = 0, sxx = 0, sxy = 0;
    for (let a = tr.i.length - n; a < tr.i.length; a++) {
      const x = Math.log((tr.i[a] + 0.5) * dR);
      sx += x; sy += tr.phi[a]; sxx += x * x; sxy += x * tr.phi[a];
    }
    const den = n * sxx - sx * sx;
    return den > 1e-12 ? (n * sxy - sx * sy) / den : k;
  };
  const live: Track[] = [];
  const done: Track[] = [];
  const byRing = new Map<number, TracePeak[]>();
  for (const q of peaks) if (q.height >= minHeight) byRing.set(q.i, [...(byRing.get(q.i) ?? []), q]);
  const rings = [...byRing.keys()].sort((a, b) => a - b);
  for (const i of rings) {
    for (let t = live.length - 1; t >= 0; t--) if (i - live[t].last > skip) done.push(...live.splice(t, 1));
    const used = new Set<Track>();
    const R = (i + 0.5) * dR;
    for (const q of byRing.get(i)!) {
      let best: Track | null = null;
      let bestD = Infinity;
      for (const tr of live) {
        if (used.has(tr)) continue;
        const dl = Math.log(R / ((tr.last + 0.5) * dR));
        // A young track (under three crests) looks either way by the winding's whole step; an older one follows its
        // own measured drift (the field's sign and the measured winding's need not agree).
        const young = tr.i.length < 3;
        const predicted = tr.lastPhi + (young ? 0 : slopeOf(tr) * dl);
        let d = ((q.j + 0.5) * cell - predicted) / cell;
        d = ((((d + P / 2) % P) + P) % P) - P / 2;
        const window = reach + (young ? (Math.abs(k) * dl) / cell : 0);
        if (Math.abs(d) <= window && Math.abs(d) < bestD) {
          bestD = Math.abs(d);
          best = tr;
        }
      }
      // Unwrapped azimuth: continue the track's own phase.
      if (best) {
        const predicted = best.lastPhi;
        const raw = (q.j + 0.5) * cell;
        const phi = raw + TAU * Math.round((predicted - raw) / TAU);
        best.i.push(i);
        best.phi.push(phi);
        best.last = i;
        best.lastPhi = phi;
        used.add(best);
      } else {
        const phi = (q.j + 0.5) * cell;
        const tr = { i: [i], phi: [phi], last: i, lastPhi: phi };
        live.push(tr);
        used.add(tr);
      }
    }
  }
  done.push(...live);
  const out: Ridge[] = [];
  let chain = 1000;
  for (const tr of done) {
    if (tr.i.length < 4) continue;
    // Smooth the azimuth over five crests (the peak finder steps a whole cell), then lay the points.
    const n = tr.i.length;
    const xs0: number[] = [];
    const ys0: number[] = [];
    for (let a = 0; a < n; a++) {
      let s = 0;
      let w = 0;
      for (let b = Math.max(0, a - 2); b <= Math.min(n - 1, a + 2); b++) {
        s += tr.phi[b];
        w += 1;
      }
      const R = (tr.i[a] + 0.5) * dR;
      xs0.push(R * Math.cos(s / w));
      ys0.push(R * Math.sin(s / w));
    }
    let length = 0;
    for (let a = 1; a < n; a++) length += Math.hypot(xs0[a] - xs0[a - 1], ys0[a] - ys0[a - 1]);
    if (length < minLength) continue;
    // Resampled every `step` kpc along the path (drawChain reads an even spacing).
    const xs: number[] = [xs0[0]];
    const ys: number[] = [ys0[0]];
    let carry = 0;
    for (let a = 1; a < n; a++) {
      const seg = Math.hypot(xs0[a] - xs0[a - 1], ys0[a] - ys0[a - 1]);
      let at = step - carry;
      while (at <= seg) {
        const f = at / seg;
        xs.push(xs0[a - 1] + (xs0[a] - xs0[a - 1]) * f);
        ys.push(ys0[a - 1] + (ys0[a] - ys0[a - 1]) * f);
        at += step;
      }
      carry = seg - (at - step);
    }
    if (xs.length >= 3) out.push(ridgeOfPoints(chain++, xs, ys, 0.3));
  }
  return out;
}

const finite = (v: unknown): number => (typeof v === "number" && Number.isFinite(v) ? v : NaN);

/** The geometry an /api/arrays frame holds (LANE_ARRAYS asked): empty without the frame. */
export function geometryOf(frame: IllFrame | null): LaneGeometry {
  const axes = ((frame?.header as { grid?: { axes?: Record<string, { n?: number; hi?: number }> } } | undefined)?.grid?.axes ?? {}) as Record<string, { n?: number; hi?: number }>;
  const rings = finite(axes.R?.n) || 400;
  const sectors = finite(axes.phi?.n) || 360;
  const rHi = finite(axes.R?.hi) || 30;
  const field = (name: string) => {
    const a = frame ? numbers(frame.arrays[name]) : null;
    return a && a.length === rings * sectors ? a : null;
  };
  const gas = field("gas_density_contrast");
  const halfLength = finite(frame?.header.scalars?.bar_half_length);
  const axisRatio = finite(frame?.header.scalars?.bar_axis_ratio);
  const angle = barAngle(field("pattern_density_contrast"), rings, sectors, rHi, halfLength);
  return {
    rHi,
    pieces: piecesOf(frame),
    gas: gas ? { values: gas, rings, sectors } : null,
    bar: Number.isFinite(angle) && halfLength > 0 ? { halfLength, axisRatio: axisRatio > 0 ? axisRatio : 0.4, angle } : null,
  };
}

/** A field over the disc read at a point, bilinear between its cell centres, the azimuth wrapped. */
function readField(f: { values: ArrayLike<number>; rings: number; sectors: number }, rHi: number, x: number, y: number): number {
  const r = Math.hypot(x, y);
  let phi = Math.atan2(y, x);
  if (phi < 0) phi += TAU;
  const u = Math.min(f.rings - 1, Math.max(0, (r / rHi) * f.rings - 0.5));
  const v = (phi / TAU) * f.sectors - 0.5;
  const i0 = Math.min(f.rings - 2, Math.floor(u));
  const j0 = Math.floor(v);
  const a = u - i0;
  const b = v - j0;
  const at = (i: number, j: number) => Number(f.values[i * f.sectors + (((j % f.sectors) + f.sectors) % f.sectors)]);
  return (1 - a) * ((1 - b) * at(i0, j0) + b * at(i0, j0 + 1)) + a * ((1 - b) * at(i0 + 1, j0) + b * at(i0 + 1, j0 + 1));
}

/** The raster being drawn: sums of shape per texel, row = sector, column = ring. */
class Raster {
  readonly acc: Float32Array;
  readonly dR: number;
  readonly dPhi: number;
  private readonly kr = new Float64Array(4096);
  constructor(readonly rings: number, readonly sectors: number, readonly rHi: number) {
    this.acc = new Float32Array(rings * sectors);
    this.dR = rHi / rings;
    this.dPhi = TAU / sectors;
  }

  /**
   * A round Gaussian spot of standard deviation `sigma` kpc at (x, y), its centre's height `weight`: summed into the
   * texels within 3.2 sigma. Spots laid every ds along a line with weight ds / (sigma sqrt(2 pi)) sum to a lane whose
   * centre is 1 and whose cross-section is the Gaussian.
   */
  spot(x: number, y: number, sigma: number, weight: number): void {
    const { acc, rings, sectors, dR, dPhi, kr } = this;
    const r = Math.hypot(x, y);
    const reach = 3.2 * sigma;
    if (!(weight > 0) || r - reach >= this.rHi) return;
    let phi = Math.atan2(y, x);
    if (phi < 0) phi += TAU;
    const inv = 1 / (2 * sigma * sigma);
    const iLo = Math.max(0, Math.ceil((r - reach) / dR - 0.5));
    const iHi = Math.min(rings - 1, Math.floor((r + reach) / dR - 0.5));
    if (iHi < iLo) return;
    if (r >= 10 * sigma) {
      // Far from the centre the ring's arc is straight over the spot: the Gaussian is a product along R and along phi.
      for (let i = iLo; i <= iHi; i += 1) {
        const d = (i + 0.5) * dR - r;
        kr[i - iLo] = Math.exp(-d * d * inv);
      }
      const half = reach / r;
      const jLo = Math.ceil((phi - half) / dPhi - 0.5);
      const jHi = Math.floor((phi + half) / dPhi - 0.5);
      for (let j = jLo; j <= jHi; j += 1) {
        const d = r * ((j + 0.5) * dPhi - phi);
        const w = weight * Math.exp(-d * d * inv);
        const row = (((j % sectors) + sectors) % sectors) * rings;
        for (let i = iLo; i <= iHi; i += 1) acc[row + i] += w * kr[i - iLo];
      }
      return;
    }
    // Near the centre: every texel's own distance.
    const half = r <= reach ? Math.PI : Math.min(Math.PI, 1.05 * Math.asin(reach / r) + dPhi);
    const jLo = Math.ceil((phi - half) / dPhi - 0.5);
    const jHi = Math.min(jLo + sectors - 1, Math.floor((phi + half) / dPhi - 0.5));
    const reach2 = reach * reach;
    for (let j = jLo; j <= jHi; j += 1) {
      const c = Math.cos((j + 0.5) * dPhi - phi);
      const row = (((j % sectors) + sectors) % sectors) * rings;
      for (let i = iLo; i <= iHi; i += 1) {
        const ri = (i + 0.5) * dR;
        const d2 = ri * ri + r * r - 2 * ri * r * c;
        if (d2 < reach2) acc[row + i] += weight * Math.exp(-d2 * inv);
      }
    }
  }
}

const SQRT_TAU = Math.sqrt(TAU);
/** The radius, kpc, inside which an arm lane's offsets, widths and branches shrink in proportion to the radius. */
const NEAR = 3;
/** A Gaussian's standard deviation from its full width at half height. */
const sigmaOf = (fwhmKpc: number) => fwhmKpc / 2.3548;

/**
 * A line of spots: `at(i)` gives the i-th point's place, standard deviation (kpc) and depth (shape at its centre);
 * each spot is weighed by the length of line it stands for, so the lane's centre holds the depth however the line bends.
 */
function line(raster: Raster, n: number, at: (i: number, out: Float64Array) => void): void {
  if (n < 2) return;
  const pts = new Float64Array(4 * n);
  const one = new Float64Array(4);
  for (let i = 0; i < n; i += 1) {
    at(i, one);
    pts.set(one, 4 * i);
  }
  for (let i = 0; i < n; i += 1) {
    const a = Math.max(0, i - 1);
    const b = Math.min(n - 1, i + 1);
    const ds = Math.hypot(pts[4 * b] - pts[4 * a], pts[4 * b + 1] - pts[4 * a + 1]) / (b - a);
    const sigma = pts[4 * i + 2];
    const depth = pts[4 * i + 3];
    if (depth > 1e-4 && sigma > 0) raster.spot(pts[4 * i], pts[4 * i + 1], sigma, (depth * ds) / (sigma * SQRT_TAU));
  }
}

/** The step along a line of spots, kpc: the thinnest standard deviation drawn (spots a sigma apart sum to a line even to 1e-8), at most 30 pc so a wiggle is followed. */
const stepFor = (sigmaKpc: number): number => Math.min(0.03, Math.max(0.006, sigmaKpc));
/** The step along an arm's ridge: a strand thins to 0.8 exp(-0.7 clump) of the width's standard deviation. */
export const ridgeStep = (shape: LaneShape): number => stepFor(sigmaOf(shape.width * 1e-3) * 0.8 * Math.exp(-0.7 * shape.clump));

/** How far each chain's depth follows the gas: per ridge point a factor in [1 - followGas, 1]. */
function gasWeights(ridges: readonly Ridge[], g: LaneGeometry, followGas: number): Float32Array[] {
  if (!g.gas || followGas <= 0) return ridges.map((r) => new Float32Array(r.n).fill(1));
  const raw = ridges.map((r) => {
    const out = new Float32Array(r.n);
    for (let i = 0; i < r.n; i += 1) out[i] = Math.max(0, readField(g.gas!, g.rHi, r.x[i], r.y[i]) - 1);
    return out;
  });
  // Full depth at 0.7 of the ridges' 90th percentile (read off every 16th point): each galaxy by its own arms.
  const all: number[] = [];
  for (const a of raw) for (let i = 0; i < a.length; i += 16) all.push(a[i]);
  all.sort((a, b) => a - b);
  const full = Math.max(0.05, 0.7 * (all[Math.floor(0.9 * (all.length - 1))] ?? 1));
  return raw.map((a) => a.map((v) => 1 - followGas + followGas * clamp01(v / full)));
}

/** The lanes along one chain's ridge: the envelope, the braided strands and the feathers. */
function drawChain(raster: Raster, ridge: Ridge, gasWeight: Float32Array, shape: LaneShape): void {
  if (ridge.n < 3 || ridge.length <= 0) return;
  const kpc = 1e-3;
  const sigma0 = sigmaOf(shape.width * kpc);
  const taper = Math.min(shape.taper, ridge.length / 3);
  const strands = Math.max(1, Math.round(shape.strands));
  const chainKey = laneKey(shape.seed, ridge.chain, 0, 1);
  // A chain's own breaks, which its strands share in part.
  // The level of the breaking noise (in [-1, 1]) under which a strand is broken away: below every value at gaps 0
  // (unbroken), rising with the gaps.
  const cut = -1.1 + 2.526 * shape.gaps;
  const ends = (i: number) => {
    const s = ridge.s[i];
    const a = ridge.fadeIn && taper > 0 ? smoothstep(0, taper, s) : 1;
    const b = ridge.fadeOut && taper > 0 ? smoothstep(0, taper, ridge.length - s) : 1;
    const r = Math.hypot(ridge.x[i], ridge.y[i]);
    const inner = shape.innerRadius > 0 ? smoothstep(0.5 * shape.innerRadius, 1.5 * shape.innerRadius, r) : 1;
    const outer = 1 - smoothstep(0.55 * shape.outerRadius, shape.outerRadius, r);
    return a * b * inner * outer * gasWeight[i];
  };
  // Near the centre everything a lane is made of shrinks with the radius (full size from NEAR kpc out): a short arc
  // half a kiloparsec from the nucleus is a fine thread with short twigs, not a blot.
  const near = (i: number) => Math.min(1, Math.hypot(ridge.x[i], ridge.y[i]) / NEAR);
  // Where a strand's centre line lies, to the inner side of the ridge, kpc (at full size).
  const lateral = (k: number, s: number) => {
    const key = laneKey(shape.seed, ridge.chain, k, 2);
    const base = strands > 1 ? 0.35 * ((2 * k + 1) / strands - 1) : 0;
    // The whole lane meanders about its line (every strand with it); each strand braids across the spread and has a
    // finer wiggle of its own, a third as long and a third as far.
    const meander = shape.wiggle * (wander(s / shape.wiggleLength, chainKey ^ 0x2468ace) + 0.35 * wander((3 * s) / shape.wiggleLength, key ^ 0x1234567));
    return (shape.offset + meander + shape.spread * (base + 0.45 * laneNoise(s / shape.braidLength, key))) * kpc;
  };
  const broken = (k: number, s: number) => {
    const key = laneKey(shape.seed, ridge.chain, k, 3);
    const v = 0.6 * laneNoise(s / shape.gapLength, chainKey) + 0.4 * laneNoise(s / (0.7 * shape.gapLength) + 5.3, key);
    // A lane's second and later strands are broken more than its first.
    const at = cut + 0.22 * Math.max(0, k);
    return smoothstep(at - 0.1, at + 0.1, v);
  };
  // Knots and threads: a swell over 0.7 kpc and a finer one over 0.18 kpc.
  const swell = (k: number, s: number) => {
    const key = laneKey(shape.seed, ridge.chain, k, 4);
    return 0.65 * wander(s / 0.7, key) + 0.55 * laneNoise(s / 0.18, key ^ 0x3c6ef372);
  };

  if (shape.envelope > 0 && shape.spread > 0) {
    // The band under the strands: wide, faint and unbroken but for the chain's own fading.
    // As wide as the braid, at most three strands' widths (a wider band is nothing a viewer sees, and its spots cost).
    const sigma = Math.max(sigma0, sigmaOf(Math.min(Math.max(shape.spread, shape.width), 3 * shape.width) * kpc));
    const every = Math.max(1, Math.round((0.8 * sigma) / (ridge.length / (ridge.n - 1))));
    const count = Math.floor((ridge.n - 1) / every) + 1;
    line(raster, count, (c, out) => {
      const i = Math.min(ridge.n - 1, c * every);
      const s = ridge.s[i];
      const l = (shape.offset + 0.3 * shape.spread * laneNoise(s / (1.5 * shape.braidLength), chainKey ^ 0x77)) * kpc * near(i);
      out[0] = ridge.x[i] + ridge.nx[i] * l;
      out[1] = ridge.y[i] + ridge.ny[i] * l;
      out[2] = sigma;
      out[3] = shape.envelope * ends(i) * (0.55 + 0.45 * broken(-1, s)) * (sigma0 / sigma) * 2.5;
    });
  }

  for (let k = 0; k < strands; k += 1) {
    const share = 1 / (1 + 0.45 * k);
    line(raster, ridge.n, (i, out) => {
      const s = ridge.s[i];
      const q = near(i);
      const l = lateral(k, s) * q;
      const w = swell(k, s);
      out[0] = ridge.x[i] + ridge.nx[i] * l;
      out[1] = ridge.y[i] + ridge.ny[i] * l;
      out[2] = sigma0 * Math.exp(0.7 * shape.clump * w) * (k === 0 ? 1 : 0.8) * Math.max(0.4, q);
      out[3] = share * ends(i) * broken(k, s) * Math.max(0, 1 + shape.clump * (0.8 * w - 0.2));
    });
  }

  if (shape.featherSpacing > 0 && shape.featherLength > 0 && shape.featherDepth > 0) {
    const count = Math.floor(ridge.length / shape.featherSpacing);
    const key = laneKey(shape.seed, ridge.chain, 0, 5);
    const step = stepFor(0.35 * sigma0);
    for (let f = 0; f < count; f += 1) {
      const s0 = (f + laneRandom(key, 4 * f)) * shape.featherSpacing;
      let i0 = Math.min(ridge.n - 1, Math.round((s0 / ridge.length) * (ridge.n - 1)));
      while (i0 < ridge.n - 1 && ridge.s[i0] < s0) i0 += 1;
      const strand = Math.floor(laneRandom(key, 4 * f + 1) * strands);
      const root = ends(i0) * broken(strand, ridge.s[i0]);
      if (root < 0.15) continue;
      // One in four leaves to the inner side instead, shorter.
      const inward = laneRandom(key, 4 * f + 3) < 0.25;
      const q = near(i0);
      const length = shape.featherLength * (0.5 + laneRandom(key, 4 * f + 2)) * (inward ? 0.6 : 1) * q;
      const open = ((shape.featherPitch * Math.PI) / 180) * (0.5 + laneRandom(laneKey(shape.seed, ridge.chain, f, 8), 0)) * (inward ? -0.7 : 1);
      const l0 = lateral(strand, ridge.s[i0]) * q;
      // From its root in the strand it runs on along the arm and outward: the tangent turned away from the centre by
      // `open`, closing back toward the arm's own direction along its length (a sheared branch).
      const fKey = laneKey(shape.seed, ridge.chain, f, 6);
      // The sense of the rotation that takes the tangent toward minus the inward normal (the outside).
      const hand = ridge.tx[i0] * -ridge.ny[i0] - ridge.ty[i0] * -ridge.nx[i0] >= 0 ? 1 : -1;
      branch(
        raster, ridge.x[i0] + ridge.nx[i0] * l0, ridge.y[i0] + ridge.ny[i0] * l0, ridge.tx[i0], ridge.ty[i0], length, step,
        (t) => hand * (open * (1 - 0.6 * t) + 0.45 * wander(t * 2.5, fKey)),
        (t) => sigma0 * (0.9 - 0.55 * t) * Math.max(0.4, q),
        (t) => shape.featherDepth * root * (1 - t) ** 1.2 * (0.7 + 0.3 * wander(t * 4 + 9, fKey)),
      );
    }
  }

  if (shape.fray > 0) {
    // The fray: short thin wisps every ~120 pc, leaving a strand at a low angle to either side.
    const spacing = 0.12;
    const count = Math.floor(ridge.length / spacing);
    const key = laneKey(shape.seed, ridge.chain, 0, 9);
    const thin = 0.45 * sigma0;
    const step = stepFor(0.6 * thin);
    for (let f = 0; f < count; f += 1) {
      const s0 = (f + laneRandom(key, 5 * f)) * spacing;
      const i0 = Math.min(ridge.n - 1, Math.round((s0 / ridge.length) * (ridge.n - 1)));
      const strand = Math.floor(laneRandom(key, 5 * f + 1) * strands);
      const root = ends(i0) * broken(strand, ridge.s[i0]);
      if (root < 0.2) continue;
      const q = near(i0);
      const length = (0.12 + 0.4 * laneRandom(key, 5 * f + 2) ** 2) * q;
      const side = laneRandom(key, 5 * f + 3) < 0.5 ? -1 : 1;
      const angle = side * (0.15 + 0.5 * laneRandom(key, 5 * f + 4));
      const l0 = lateral(strand, ridge.s[i0]) * q;
      const fKey = laneKey(shape.seed, ridge.chain, f, 10);
      branch(
        raster, ridge.x[i0] + ridge.nx[i0] * l0, ridge.y[i0] + ridge.ny[i0] * l0, ridge.tx[i0], ridge.ty[i0], length, step,
        (t) => angle * (1 - 0.5 * t) + 0.35 * wander(t * 2 + 1, fKey),
        (t) => thin * (1.1 - 0.6 * t) * Math.max(0.5, q),
        (t) => shape.fray * root * (1 - t) ** 0.8,
      );
    }
  }
}

/** A short branch from (x, y) heading along (dx, dy), turning by `turn(t)` radians as it goes, thinning to its tip. */
function branch(raster: Raster, x: number, y: number, dx: number, dy: number, length: number, step: number, turn: (t: number) => number, sigma: (t: number) => number, depth: (t: number) => number): void {
  const n = Math.max(3, Math.ceil(length / step));
  const xs = new Float64Array(n);
  const ys = new Float64Array(n);
  let px = x;
  let py = y;
  for (let j = 0; j < n; j += 1) {
    xs[j] = px;
    ys[j] = py;
    const a = turn(j / (n - 1));
    const c = Math.cos(a);
    const sn = Math.sin(a);
    px += (dx * c - dy * sn) * (length / (n - 1));
    py += (dx * sn + dy * c) * (length / (n - 1));
  }
  line(raster, n, (j, out) => {
    const t = j / (n - 1);
    out[0] = xs[j];
    out[1] = ys[j];
    out[2] = sigma(t);
    out[3] = depth(t);
  });
}

/**
 * The bar's two lanes: on each half's LEADING side (the disc turns toward decreasing azimuth - the arms trail, a
 * positive pitch's azimuth growing outward - so the half that points along the bar's angle leads on its low-azimuth
 * side), from the bar's end along a line offset from the long axis, then curling once round the nucleus.
 * In the bar's own frame (X along the angle, Y a quarter turn on, toward growing azimuth) the first lane is
 *     Y = -c (1 - (X / a)^curve),   X from reach a down to 0,   c = offset (a axisRatio),
 * and then a trailing spiral inward from (0, -c); the second is its mirror through the centre.
 */
export function barRidges(bar: NonNullable<LaneGeometry["bar"]>, shape: LaneShape, step: number): Ridge[] {
  const a = bar.halfLength;
  const c = shape.barOffset * a * bar.axisRatio;
  if (!(c > 0) || !(shape.barReach > 0)) return [];
  const X: number[] = [];
  const Y: number[] = [];
  const n = Math.max(8, Math.ceil((a * shape.barReach) / step));
  for (let i = 0; i <= n; i += 1) {
    const x = a * shape.barReach * (1 - i / n);
    X.push(x);
    Y.push(-c * (1 - (x / a) ** shape.barCurve));
  }
  // The curl: from (0, -c), heading toward -X, round the centre by 220 degrees, the radius falling to a third.
  const sweep = ((220 * Math.PI) / 180) * Math.max(0, shape.barCurl ?? 1);
  const m = sweep > 0 ? Math.max(8, Math.ceil((c * sweep) / step)) : 0;
  for (let i = 1; i <= m; i += 1) {
    const t = i / m;
    const theta = -Math.PI / 2 - sweep * t;
    const r = c * Math.exp(-1.1 * t);
    X.push(r * Math.cos(theta));
    Y.push(r * Math.sin(theta));
  }
  const cos = Math.cos(bar.angle);
  const sin = Math.sin(bar.angle);
  return [1, -1].map((h, k) =>
    ridgeOfPoints(
      -1 - k,
      X.map((x, i) => h * (x * cos - Y[i] * sin)),
      X.map((x, i) => h * (x * sin + Y[i] * cos)),
      0.1,
    ),
  );
}

/** The bar's lanes drawn: one smooth strand each, fading in from the bar's end and out through the curl. */
function drawBar(raster: Raster, bar: NonNullable<LaneGeometry["bar"]>, shape: LaneShape, step: number): void {
  if (!(shape.barDepth > 0)) return;
  const sigma = sigmaOf(shape.barWidth * 1e-3);
  const c = shape.barOffset * bar.halfLength * bar.axisRatio;
  const straight = bar.halfLength * shape.barReach;
  for (const ridge of barRidges(bar, shape, step)) {
    const key = laneKey(shape.seed, ridge.chain & 0xffff, 0, 7);
    line(raster, ridge.n, (i, out) => {
      const s = ridge.s[i];
      const l = c * (0.14 * wander(s / 1.3, key) + 0.05 * wander(s / 0.3 + 2, key));
      out[0] = ridge.x[i] + ridge.nx[i] * l;
      out[1] = ridge.y[i] + ridge.ny[i] * l;
      out[2] = sigma * (1 + 0.3 * wander(s / 0.9 + 3, key));
      out[3] = shape.barDepth * smoothstep(0, 0.2 * straight, s) * (1 - smoothstep(straight, ridge.length, s) ** 2) * (0.85 + 0.15 * wander(s / 0.5 + 7, key));
    });
  }
}

/** The lanes' map: bytes of sqrt(shape / shapeMax), `rings` to a row (R) and `sectors` rows (phi). */
export interface LaneMap {
  data: Uint8Array;
  rings: number;
  sectors: number;
  /** Whether anything was drawn. */
  drawn: boolean;
}

/** The map for a geometry and a shape. The same inputs give the same bytes. */
export function buildLaneMap(g: LaneGeometry, shape: LaneShape, rings: number = LANE_MAP.rings, sectors: number = LANE_MAP.sectors): LaneMap {
  const raster = new Raster(rings, sectors, g.rHi);
  const step = ridgeStep(shape);
  const ridges = (shape.skeleton ?? 0) >= 0.5 && g.skeleton ? g.skeleton : shape.trace >= 0.5 && g.traced ? g.traced : ridgesOf(g.pieces, step);
  const weights = gasWeights(ridges, g, shape.followGas).map((w, k) => {
    const own = ridges[k].weight;
    return own ? w.map((v, i) => v * own[i]) : w;
  });
  ridges.forEach((ridge, k) => drawChain(raster, ridge, weights[k], shape));
  if (g.bar) drawBar(raster, g.bar, shape, stepFor(sigmaOf(shape.barWidth * 1e-3) * 0.75));
  const data = new Uint8Array(rings * sectors);
  const acc = raster.acc;
  let drawn = false;
  for (let i = 0; i < acc.length; i += 1) {
    const v = acc[i];
    if (v > 0) {
      const b = Math.round(255 * Math.sqrt(Math.min(1, v / LANE_MAP.shapeMax)));
      data[i] = b;
      if (b > 0) drawn = true;
    }
  }
  return { data, rings, sectors, drawn };
}

/** The shape a map's texel holds at ring i, sector j: (byte / 255)^2 shapeMax, as the GLSL reads it. */
export const shapeAt = (map: LaneMap, i: number, j: number): number => (map.data[j * map.rings + i] / 255) ** 2 * LANE_MAP.shapeMax;
