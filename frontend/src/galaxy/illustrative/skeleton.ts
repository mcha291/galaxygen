// The arm skeleton (S106, builder B3: the Milky Way's second pass). A small set of continuous ridge curves in the disc's
// plane on which every mark of the illustrative look's arms sits - the glow (arms.ts, the shared map's B and A), the
// grain (armsSparkle.ts), the lanes (lanes.ts) and, later, the pink regions (knots*: ridgeAt / sampleRidges below).
//
// DISPLAY-ONLY DRAWING OF THE LAYER'S OWN (the lead's ruling 12, COMMON.md): the model's arm pieces are short, patchy
// and end well inside the goal picture's disc, so the skeleton continues each arm along its own pitch to the disc's edge
// and adds lesser arms and short spurs between the major ones, where the goal picture has them and the model does not.
// It changes no published number, readout, tracer or preview. Everything it places comes from PUBLISHED geometry and
// from its own controls:
//   - the winding's sense and pitch: the arm pieces' (arm_piece_pitch, the length-weighted median of |pitch| and the
//     sign of the length-weighted pitch), times the pitch slider;
//   - the two major arms: from the bar's two ends (bar_half_length, the bar's angle read off pattern_density_contrast
//     as the lanes read it), at `start` times the half-length;
//   - the lesser arms: between the majors, each nudged to the strongest phase of the arm pieces' own loci (their
//     log-spiral phase, length-weighted) within NUDGE of the midway phase;
//   - the spurs, the pitch's slow drift and kinks, the breaks at the outer ends: a fixed seed of the viewer's own.
// The count of arms is the controls' (two majors for the bar's two ends, `lesser` and `spurs` the sliders'): nothing is
// composed or placed from the model's arm number.
//
// An arm is a log spiral with a slowly drifting pitch: phi(ln R) = phi0 + sense * integral of d(ln R) / tan(pitch), so
// it crosses each ring once - the distance from a point (R, phi) to it is read on that ring, R |dphi| sin(pitch).

import type { Piece } from "./lanesMap";
import { laneKey, laneNoise, laneRandom } from "./lanesMap";

const TAU = 2 * Math.PI;

/** The skeleton's controls (arms.ts's `skel*` sliders). Lengths in kpc. */
export interface SkeletonParams {
  /** How many lesser arms (0-4), between the majors. */
  lesser: number;
  /** How many short spurs in all, off the arms' outer sides. */
  spurs: number;
  /** A multiplier on the arm pieces' pitch: below 1 a tighter winding. */
  pitchScale: number;
  /** The pitch's slow drift along an arm, as a share of the pitch. */
  drift: number;
  /** The kinks' size: a few short changes of pitch along each arm, as a share of the pitch. */
  kink: number;
  /** A ridge's full width at half maximum, kpc (lesser arms 0.85 of it, spurs 0.7). */
  width: number;
  /** Where the major arms end, kpc (the lesser arms LESSER_REACH of it). */
  outer: number;
  /** The share of each arm's length (in ln R) over which it fades and breaks into flecks at its outer end. */
  fade: number;
  /** Where the majors start, times the bar's half-length (or kpc without a bar). */
  start: number;
  /** Where the lesser arms start, times the majors' start. */
  lesserStart: number;
  /** The lesser arms' strength (the majors' 1). */
  lesserLevel: number;
  /** The seed of the drift, the kinks, the spurs and the breaks. */
  seed: number;
}

export const SKELETON_DEFAULTS: SkeletonParams = {
  lesser: 2,
  spurs: 4,
  pitchScale: 1,
  drift: 0.15,
  kink: 0.25,
  width: 0.6,
  outer: 18,
  fade: 0.3,
  start: 1,
  lesserStart: 1.25,
  lesserLevel: 0.75,
  seed: 11,
};

/** The lesser arms' outer end as a share of the majors'. */
export const LESSER_REACH = 0.92;
/** How far (rad) a lesser arm's phase may be nudged toward the pieces' strongest phase. */
export const NUDGE = (35 * Math.PI) / 180;
/** The samples per unit ln R of an arm's table. */
const PER_LN = 400;

export type ArmKind = "major" | "lesser" | "spur";

/** One ridge curve, tabulated in ln R. */
export interface SkelArm {
  kind: ArmKind;
  /** kpc */
  r0: number;
  r1: number;
  lnR0: number;
  dlnR: number;
  n: number;
  /** The crest's azimuth (rad, unwrapped), tan(pitch) and strength in [0, 1] at each sample. */
  phi: Float64Array;
  tanp: Float64Array;
  strength: Float64Array;
  /** The ridge's full width at half maximum here, kpc. */
  width: number;
}

export interface Skeleton {
  arms: SkelArm[];
  /** +1: the azimuth grows outward along an arm (the pieces' sense), -1 falls. */
  sense: number;
  /** The base pitch, degrees (the pieces' times the pitch scale). */
  pitchDeg: number;
  /** The majors' width, kpc (the params'). */
  width: number;
}

/** The pieces' winding: the length-weighted median |pitch| (degrees) and the sign of the length-weighted pitch. */
export function piecesPitch(pieces: readonly Piece[]): { pitchDeg: number; sense: number } {
  const rows: { p: number; w: number }[] = [];
  let signed = 0;
  for (const q of pieces) {
    const tan = Math.abs(Math.tan((q.pitchDeg * Math.PI) / 180));
    const w = q.r0 * Math.exp(q.extent * tan) - q.r0 + q.r0 * q.extent * 0.05;
    if (!(w > 0)) continue;
    rows.push({ p: Math.abs(q.pitchDeg), w });
    signed += Math.sign(q.pitchDeg || 1) * w;
  }
  if (rows.length === 0) return { pitchDeg: 12, sense: 1 };
  rows.sort((a, b) => a.p - b.p);
  const total = rows.reduce((s, r) => s + r.w, 0);
  let acc = 0;
  let median = rows[rows.length - 1].p;
  for (const r of rows) {
    acc += r.w;
    if (acc >= total / 2) {
      median = r.p;
      break;
    }
  }
  return { pitchDeg: Math.min(40, Math.max(3, median)), sense: signed >= 0 ? 1 : -1 };
}

const wrap = (a: number): number => a - TAU * Math.round(a / TAU);

/**
 * The pieces' loci as log-spiral phases psi = phi - sense ln R / tan(pitch), length-weighted, in `bins` bins round the
 * turn and smoothed: where along the turn the model's own arms gather.
 */
export function piecePhases(pieces: readonly Piece[], sense: number, tanp: number, bins = 72): Float64Array {
  const h = new Float64Array(bins);
  for (const q of pieces) {
    const tan = Math.tan((q.pitchDeg * Math.PI) / 180);
    const steps = Math.max(2, Math.ceil(q.extent / 0.05));
    for (let i = 0; i <= steps; i++) {
      const t = i / steps;
      const r = q.r0 * Math.exp(t * q.extent * Math.abs(tan));
      const phi = q.phi0 + t * q.extent * (tan >= 0 ? 1 : -1);
      const psi = wrap(phi - (sense * Math.log(r)) / tanp);
      const b = Math.floor(((psi + TAU) % TAU) / (TAU / bins)) % bins;
      h[b] += r * (q.extent / steps);
    }
  }
  const out = new Float64Array(bins);
  for (let b = 0; b < bins; b++) for (let d = -3; d <= 3; d++) out[b] += h[(b + d + bins) % bins] * Math.exp(-(d * d) / 4);
  return out;
}

const smooth01 = (e0: number, e1: number, x: number): number => {
  if (e1 <= e0) return x < e0 ? 0 : 1;
  const t = Math.min(1, Math.max(0, (x - e0) / (e1 - e0)));
  return t * t * (3 - 2 * t);
};

/** One arm tabulated: from (r0, phi0) out to r1 at a pitch drifting about `pitchDeg`, its strength profile laid. */
function tabulate(kind: ArmKind, r0: number, r1: number, phi0: number, pitchDeg: number, sense: number, level: number, width: number, p: SkeletonParams, key: number, fadeIn: number): SkelArm {
  const lnR0 = Math.log(r0);
  const span = Math.max(1e-3, Math.log(r1) - lnR0);
  const n = Math.max(8, Math.ceil(span * PER_LN) + 1);
  const dlnR = span / (n - 1);
  const phi = new Float64Array(n);
  const tanp = new Float64Array(n);
  const strength = new Float64Array(n);
  // Kinks: two or three short bumps of pitch at seeded places along the arm.
  const kinks = 2 + Math.floor(laneRandom(key, 90) * 2);
  const kinkAt = Array.from({ length: kinks }, (_, k) => ({ at: 0.15 + 0.7 * laneRandom(key, 91 + k), sign: laneRandom(key, 95 + k) < 0.5 ? -1 : 1 }));
  let ph = phi0;
  for (let i = 0; i < n; i++) {
    const f = i / (n - 1);
    const lnR = lnR0 + i * dlnR;
    // The slow drift: smooth noise over 0.45 in ln R (a few kpc); the kinks: bumps 0.04 wide in ln R.
    let scale = 1 + p.drift * laneNoise(lnR / 0.45 + 3.1, key ^ 0x51);
    for (const k of kinkAt) {
      const x = (f - k.at) * (span / 0.04);
      scale += p.kink * k.sign * Math.exp(-x * x);
    }
    const t = Math.tan((Math.max(1, Math.min(60, pitchDeg * Math.max(0.2, scale))) * Math.PI) / 180);
    tanp[i] = t;
    if (i > 0) ph += (sense * dlnR) / (0.5 * (t + tanp[i - 1]));
    phi[i] = ph;
    // The strength: in over `fadeIn` of the length, out over the outer `fade`, broken into flecks as it fades.
    const inner = fadeIn > 0 ? smooth01(0, fadeIn, f) : 1;
    const outFrom = 1 - Math.max(0.02, p.fade);
    const out = 1 - smooth01(outFrom, 1, f);
    const late = smooth01(outFrom - 0.1, 1, f);
    const s = (Math.exp(lnR) * TAU) / 1.2;
    const brk = laneNoise(s / TAU / 0.9 + 0.37, key ^ 0x77) * 0.65 + 0.35 * laneNoise(s / TAU / 0.3 + 5.1, key ^ 0x99);
    const cut = -1.2 + 1.7 * late;
    const kept = smooth01(cut - 0.12, cut + 0.12, brk);
    const grain = 0.88 + 0.12 * laneNoise(s / TAU / 1.7 + 9.4, key ^ 0x3c);
    strength[i] = level * inner * out * kept * grain;
  }
  return { kind, r0, r1, lnR0, dlnR, n, phi, tanp, strength, width };
}

/** What the skeleton is built from: the arm pieces and the bar (lanesMap.ts LaneGeometry's own). */
export interface SkeletonGeometry {
  pieces: readonly Piece[];
  bar: { halfLength: number; angle: number } | null;
}

/** The skeleton for a geometry and its controls: deterministic in both. */
export function buildSkeleton(g: SkeletonGeometry, params: Partial<SkeletonParams> = {}): Skeleton {
  const p: SkeletonParams = { ...SKELETON_DEFAULTS, ...params };
  const { pitchDeg: base, sense } = piecesPitch(g.pieces);
  const pitchDeg = Math.min(45, Math.max(2, base * p.pitchScale));
  const tanp = Math.tan((pitchDeg * Math.PI) / 180);
  const arms: SkelArm[] = [];
  // The majors: from the bar's two ends; without a bar, from the start of the longest chain of pieces and opposite it.
  let phiA = 0;
  let r0 = p.start;
  if (g.bar) {
    phiA = g.bar.angle;
    r0 = p.start * g.bar.halfLength;
  } else if (g.pieces.length) {
    const longest = [...g.pieces].sort((a, b) => b.extent * b.r0 - a.extent * a.r0)[0];
    phiA = longest.phi0 - (sense * Math.log(longest.r0 / r0)) / tanp;
  }
  const r1 = Math.max(r0 * 1.2, p.outer);
  for (let k = 0; k < 2; k++) arms.push(tabulate("major", r0, r1, phiA + k * Math.PI, pitchDeg, sense, 1, p.width, p, laneKey(p.seed, 1, k, 0), 0.04));
  // The lesser arms: between the majors in the log-spiral phase, nudged to the pieces' strongest phase near there.
  const lesser = Math.max(0, Math.min(4, Math.round(p.lesser)));
  const psiA = phiA - (sense * Math.log(r0)) / tanp;
  const hist = piecePhases(g.pieces, sense, tanp);
  const bins = hist.length;
  const rL = r0 * p.lesserStart;
  for (let k = 0; k < lesser; k++) {
    // The first two midway between the majors; a third and fourth a quarter turn on from them.
    const nominal = psiA + Math.PI / 2 + (k % 2) * Math.PI + (k >= 2 ? Math.PI / 4 : 0);
    let best = nominal;
    let bestH = -1;
    for (let b = 0; b < bins; b++) {
      const psi = ((b + 0.5) * TAU) / bins;
      const d = wrap(psi - nominal);
      if (Math.abs(d) > NUDGE) continue;
      // Preferring the midway phase a little: a flat histogram leaves it there.
      const h = hist[b] * (1 - 0.3 * (Math.abs(d) / NUDGE));
      if (h > bestH) {
        bestH = h;
        best = nominal + d;
      }
    }
    const phiL = best + (sense * Math.log(rL)) / tanp;
    arms.push(tabulate("lesser", rL, Math.max(rL * 1.2, r1 * LESSER_REACH), phiL, pitchDeg, sense, p.lesserLevel, p.width * 0.85, p, laneKey(p.seed, 2, k, 0), 0.12));
  }
  // The spurs: off the arms' outer sides at seeded places, more open than the arm, short.
  const parents = arms.slice();
  const spurs = Math.max(0, Math.min(12, Math.round(p.spurs)));
  for (let k = 0; k < spurs; k++) {
    const key = laneKey(p.seed, 3, k, 0);
    const parent = parents[k % parents.length];
    const f = 0.3 + 0.45 * laneRandom(key, 1);
    const i = Math.round(f * (parent.n - 1));
    const rs = Math.exp(parent.lnR0 + i * parent.dlnR);
    const length = 0.12 + 0.14 * laneRandom(key, 2);
    const spurPitch = pitchDeg * (2 + laneRandom(key, 3));
    arms.push(tabulate("spur", rs, rs * Math.exp(length), parent.phi[i], spurPitch, sense, 0.5 * parent.strength[i] + 0.1, p.width * 0.7, { ...p, fade: 0.6, drift: p.drift * 0.5, kink: 0 }, key, 0.15));
  }
  return { arms, sense, pitchDeg, width: p.width };
}

/** An arm's sample index (fractional) at radius R, or null outside it. */
function at(a: SkelArm, R: number): number | null {
  const x = (Math.log(R) - a.lnR0) / a.dlnR;
  if (!(x >= 0 && x <= a.n - 1)) return null;
  return x;
}

const lerp = (v: Float64Array, x: number): number => {
  const i = Math.min(v.length - 2, Math.floor(x));
  const f = x - i;
  return v[i] * (1 - f) + v[i + 1] * f;
};

/** An arm's crest azimuth (unwrapped), tan(pitch) and strength at radius R; null outside it. */
export function armAt(a: SkelArm, R: number): { phi: number; tanp: number; strength: number } | null {
  const x = at(a, R);
  if (x === null) return null;
  return { phi: lerp(a.phi, x), tanp: lerp(a.tanp, x), strength: lerp(a.strength, x) };
}

/** The nearest ridge to a point: its distance (kpc, across the arm on the point's ring), strength there, arm index and side. */
export interface RidgeHit {
  /** kpc, R |dphi| sin(pitch) on the point's ring; Infinity where no arm crosses it. */
  distance: number;
  /** The ridge's strength where it crosses the point's ring, [0, 1]. */
  strength: number;
  /** Index into skeleton.arms, -1 none. */
  arm: number;
  /** +1 the point lies on the ridge's inner (concave, the centre's) side, -1 its outer. */
  side: number;
  /** The ridge's FWHM there, kpc. */
  width: number;
}

/**
 * THE REGIONS' READ (exported for the pink regions' builder): for a point (R kpc, phi rad) of the disc's plane, the
 * nearest ridge crossing its ring - the distance to its crest, the ridge's strength there, which arm and which side.
 */
export function ridgeAt(sk: Skeleton, R: number, phi: number): RidgeHit {
  let best: RidgeHit = { distance: Infinity, strength: 0, arm: -1, side: 0, width: sk.width };
  for (let k = 0; k < sk.arms.length; k++) {
    const a = sk.arms[k];
    const h = armAt(a, R);
    if (!h) continue;
    const d = wrap(phi - h.phi);
    const sin = h.tanp / Math.sqrt(1 + h.tanp * h.tanp);
    const dist = Math.abs(R * d * sin);
    if (dist < best.distance) {
      // The inner side: a point displaced from the crest along the ring in the arm's own sense lies where the arm
      // passes further out, so the arm is outside it.
      const side = Math.sign(d) * sk.sense >= 0 ? 1 : -1;
      best = { distance: dist, strength: h.strength, arm: k, side, width: a.width };
    }
  }
  return best;
}

/** The glow's profile across a ridge: a soft Gaussian of FWHM `width` and a faint wing three times as wide. */
export function bandProfile(d: number, width: number, wing: number): number {
  const s = width / 2.3548;
  const x = d / s;
  return Math.exp(-0.5 * x * x) * (1 - wing) + wing * Math.exp(-0.5 * (x / 3) ** 2);
}

/**
 * The skeleton's band over the shared map's grid (width columns along R over [0, rHi], height rows round the turn,
 * cell-centred, row-major): at each texel the largest strength * bandProfile over the arms crossing its ring.
 * Ring by ring and arm by arm, only the rows within 3.5 sigma of the wing of each crest are touched.
 */
export function skeletonBand(sk: Skeleton, width: number, height: number, rHi: number, wing: number): Float32Array {
  const out = new Float32Array(width * height);
  const dPhi = TAU / height;
  // S106 (B5): near an arm's START each texel's strength is read at the FOOT of its perpendicular on the arm (the
  // crest's point nearest it: ln R moved by sense * dphi * sin(p) cos(p)), none where that foot lies before the start;
  // from a few widths along the arm on, on its own ring as before. Read on the ring there too, a low-pitched arm's wing
  // (three widths across: most of the turn on the first ring) began everywhere at once at the start's radius - a
  // circle round the bar. (Read at the foot everywhere, the faded outer ends and the breaks stop square across the
  // wing; on the ring they trail off along it, as the goal's arms do.)
  const sense = sk.sense >= 0 ? 1 : -1;
  for (let c = 0; c < width; c++) {
    const R = ((c + 0.5) / width) * rHi;
    const lnR = Math.log(R);
    for (const a of sk.arms) {
      const s = a.width / 2.3548;
      const reachKpc = (wing > 0 ? 3 * 3.2 : 3.5) * s;
      // Inside the arm's start (within a reach of it) its crest carried inward at the start's pitch: texels there
      // whose foot lies on the arm are its band's rounded start.
      const h = armAt(a, R) ?? armBefore(a, R, reachKpc, sense);
      if (!h) continue;
      const sin = h.tanp / Math.sqrt(1 + h.tanp * h.tanp);
      const cos = 1 / Math.sqrt(1 + h.tanp * h.tanp);
      const half = Math.min(Math.PI, reachKpc / Math.max(1e-6, R * sin));
      const centre = (((h.phi % TAU) + TAU) % TAU) / dPhi - 0.5;
      const jLo = Math.ceil(centre - half / dPhi);
      const jHi = Math.min(jLo + height - 1, Math.floor(centre + half / dPhi));
      const lnEnd = a.lnR0 + (a.n - 1) * a.dlnR;
      // The start's reach along the arm, in ln R: the foot's reading blends into the ring's over the next as much.
      const startLen = Math.max(4 * a.dlnR, (3 * a.width) / a.r0);
      const ringStrength = "strength" in h ? (h.strength as number) : 0;
      for (let j = jLo; j <= jHi; j++) {
        const dphi = (j - centre) * dPhi;
        const foot = lnR + sense * dphi * sin * cos;
        if (foot < a.lnR0) continue;
        const t = Math.min(1, Math.max(0, (foot - a.lnR0 - startLen) / startLen));
        const blend = t * t * (3 - 2 * t);
        const atFoot = blend < 1 ? lerp(a.strength, Math.min(a.n - 1, (foot - a.lnR0) / a.dlnR)) : 0;
        const strength = atFoot + (ringStrength - atFoot) * blend;
        if (strength <= 1e-3) continue;
        const v = strength * bandProfile(R * dphi * sin, a.width, wing);
        const o = (((j % height) + height) % height) * width + c;
        if (v > out[o]) out[o] = v;
      }
    }
  }
  return out;
}

/** An arm's crest carried inside its start (within `reach` kpc of it) at the start's pitch; null elsewhere. */
function armBefore(a: SkelArm, R: number, reach: number, sense: number): { phi: number; tanp: number } | null {
  if (!(R < a.r0 && R > a.r0 - reach)) return null;
  return { phi: a.phi[0] + (sense * (Math.log(R) - a.lnR0)) / a.tanp[0], tanp: a.tanp[0] };
}

/** An arm sampled every `step` kpc along its crest: plane positions (x = R cos phi, y = R sin phi) and strength. */
export function ridgeLine(a: SkelArm, step: number): { x: number[]; y: number[]; strength: number[]; r: number[]; phi: number[] } {
  const x: number[] = [];
  const y: number[] = [];
  const strength: number[] = [];
  const r: number[] = [];
  const phi: number[] = [];
  let lnR = a.lnR0;
  const lnEnd = a.lnR0 + (a.n - 1) * a.dlnR;
  while (lnR <= lnEnd + 1e-12) {
    const R = Math.exp(lnR);
    const h = armAt(a, Math.min(R, Math.exp(lnEnd)))!;
    x.push(R * Math.cos(h.phi));
    y.push(R * Math.sin(h.phi));
    strength.push(h.strength);
    r.push(R);
    phi.push(((h.phi % TAU) + TAU) % TAU);
    // Along the crest ds = R dlnR / sin(pitch).
    const sin = h.tanp / Math.sqrt(1 + h.tanp * h.tanp);
    lnR += Math.max(1e-5, (step * sin) / R);
  }
  return { x, y, strength, r, phi };
}

/** mulberry32. */
function generator(seed: number): () => number {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/**
 * THE REGIONS' SAMPLER (exported for the pink regions' builder): `count` points along the ridges, each arm chosen by
 * its length times its mean strength, a place along it accepted with the ridge's strength there, and laid across the
 * crest by a Gaussian of `spread` times the ridge's FWHM (0: on the crest). Galaxy-frame R (kpc) and phi (rad), the
 * strength at the crest, the arm. Deterministic in (skeleton, count, seed, spread).
 */
export function sampleRidges(sk: Skeleton, count: number, seed: number, spread = 0.3): { radius: Float32Array; azimuth: Float32Array; strength: Float32Array; arm: Int16Array } {
  const next = generator(seed);
  const lines = sk.arms.map((a) => ridgeLine(a, 0.05));
  const weights = lines.map((l) => l.strength.reduce((s, v) => s + v, 0));
  const total = weights.reduce((s, v) => s + v, 0);
  const n = total > 0 ? Math.max(0, Math.floor(count)) : 0;
  const radius = new Float32Array(n);
  const azimuth = new Float32Array(n);
  const strength = new Float32Array(n);
  const arm = new Int16Array(n);
  let k = 0;
  for (let tries = 0; k < n && tries < n * 60; tries++) {
    let u = next() * total;
    let a = 0;
    while (a < weights.length - 1 && u > weights[a]) u -= weights[a++];
    const l = lines[a];
    const i = Math.floor(next() * l.x.length);
    if (next() > l.strength[i]) continue;
    const g = Math.sqrt(-2 * Math.log(Math.max(1e-12, next()))) * Math.cos(TAU * next());
    // Across the crest: along the ring, by the across distance over R sin(pitch).
    const h = armAt(sk.arms[a], l.r[i]);
    const sin = h ? h.tanp / Math.sqrt(1 + h.tanp * h.tanp) : 0.2;
    const d = g * spread * sk.arms[a].width;
    radius[k] = l.r[i];
    azimuth[k] = (((l.phi[i] + d / (l.r[i] * Math.max(0.05, sin))) % TAU) + TAU) % TAU;
    strength[k] = l.strength[i];
    arm[k] = a;
    k++;
  }
  return { radius: radius.subarray(0, k), azimuth: azimuth.subarray(0, k), strength: strength.subarray(0, k), arm: arm.subarray(0, k) };
}

/**
 * The grain's density across a ridge (the sparkle, armsSparkle.ts): dense on the crest, thinning to both sides over
 * about one ridge width, a sparse tail further, all times the ridge's strength to the power `fadePow`. `tail` the
 * tail's level against the crest's.
 */
export function grainDensity(hit: RidgeHit, tail: number, fadePow: number): number {
  if (!(hit.distance < Infinity) || hit.strength <= 0) return 0;
  const x = hit.distance / Math.max(1e-3, hit.width);
  const v = Math.exp(-0.5 * (x / 0.3) ** 2) * 0.7 + 0.3 * Math.exp(-0.5 * (x / 0.7) ** 2) + tail * Math.exp(-0.5 * (x / 2) ** 2);
  return Math.min(1, v) * Math.pow(hit.strength, fadePow);
}
