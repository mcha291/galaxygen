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
  /** S107: the pitch grows outward as (R / the majors' start)^this, so successive windings separate; 0 a constant pitch. */
  pitchGrow?: number;
  /**
   * S108 (a rerolled galaxy): the least base pitch the skeleton takes from the arm pieces, degrees (before pitchScale).
   * A rerolled Milky Way's pieces can wind at a median of 1.4 degrees (pattern_seed 87658474: 195 near-circular pieces),
   * which drew the arms as concentric rings; the goals' arms open at 10-15 degrees. Above every template's own (the
   * Milky Way's 12.6), so the template's skeleton is today's.
   */
  pitchMin?: number;
  /** S107: the majors' pitch at their start raised by 1 + this, falling back over about a third of a turn: the arm leaves the bar's end at a clear angle; 0 none. */
  open?: number;
  /** S107: the lesser arms' width as a share of the majors' (0.85 until S107). */
  lesserWidth?: number;
  /** S107: the lesser arms' outer end as a share of the majors' (LESSER_REACH until S107). */
  lesserReach?: number;
  /** S107: the light along each arm modulated by a fixed noise (bright clumps, thin stretches) by this share; 0 an even arm. */
  patch?: number;
  /** S107: the clumps' wavelength along the arm, kpc. */
  patchScale?: number;
  /** S107: each side of an arm's band widened or narrowed by a fixed noise by up to this share (ragged edges); 0 even edges. */
  ragged?: number;
  /** S107 (MW2): how far (degrees) a lesser arm's phase may be nudged toward the pieces' strongest phase (NUDGE until MW2). */
  nudge?: number;
  /**
   * S107 (MW2): the lesser arms laid evenly through the gaps between the majors AT EACH RADIUS (the gap from the first
   * major to the second takes ceil(lesser / 2) of them, the other the rest, each at an even fraction of its gap, read
   * off the two majors' own crests ring by ring - so their drift, kinks and the opening at the bar do not bunch them), by
   * this share; 0 each lesser on its own winding from its nominal phase (until MW2).
   */
  even?: number;
}

/** The lesser arms' outer end as a share of the majors' (the default of SkeletonParams.lesserReach). */
export const LESSER_REACH = 0.92;

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
  pitchGrow: 0,
  pitchMin: 10,
  open: 0,
  lesserWidth: 0.85,
  lesserReach: LESSER_REACH,
  patch: 0,
  patchScale: 0.7,
  ragged: 0,
  nudge: 35,
  even: 0,
};

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
  /**
   * S107 (null without patchiness or raggedness): at each sample the light's clump multiplier (mean about 1) and the
   * band's width multipliers on the inner (the centre's) and the outer side.
   */
  patch: Float64Array | null;
  wIn: Float64Array | null;
  wOut: Float64Array | null;
  /** S107: the largest of the two sides' width multipliers (1 without raggedness). */
  wMax?: number;
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
function tabulate(kind: ArmKind, r0: number, r1: number, phi0: number, pitchDeg: number, sense: number, level: number, width: number, p: SkeletonParams, key: number, fadeIn: number, pitchAt: (lnR: number) => number = () => 1): SkelArm {
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
    const t = Math.tan((Math.max(1, Math.min(60, pitchDeg * Math.max(0.2, scale) * pitchAt(lnR))) * Math.PI) / 180);
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
  const { patch, wIn, wOut } = patchTables(n, lnR0, dlnR, tanp, p, key);
  let wMax = 1;
  if (wIn && wOut) for (let i = 0; i < n; i++) wMax = Math.max(wMax, wIn[i], wOut[i]);
  return { kind, r0, r1, lnR0, dlnR, n, phi, tanp, strength, width, patch, wIn, wOut, wMax };
}

/** Two octaves of laneNoise, about [-1, 1]. */
const noise2 = (x: number, key: number): number => (laneNoise(x, key) + 0.5 * laneNoise(x * 2.07 + 13.7, key ^ 0x5bd1e995)) / 1.5;

/**
 * S107 (the patchy arms): an arm's clump and edge tables over its samples, from fixed noises in its arc length (kpc
 * along the crest, ds = R dlnR / sin(pitch)): the clumps min(1, (1 - patch) + patch * 2.2 u^2), u the noise in [0, 1] at the
 * `patchScale` wavelength (the full ridge in the knots, thin stretches between); each side's width 1 + ragged * noise at half
 * that wavelength. Null tables where both shares are 0.
 */
function patchTables(n: number, lnR0: number, dlnR: number, tanp: Float64Array, p: SkeletonParams, key: number) {
  const share = Math.min(1, Math.max(0, p.patch ?? 0));
  const ragged = Math.min(0.9, Math.max(0, p.ragged ?? 0));
  if (share <= 0 && ragged <= 0) return { patch: null, wIn: null, wOut: null };
  const L = Math.max(0.05, p.patchScale ?? 0.7);
  const patch = new Float64Array(n);
  const wIn = new Float64Array(n);
  const wOut = new Float64Array(n);
  let s = 0;
  for (let i = 0; i < n; i++) {
    if (i > 0) {
      const R = Math.exp(lnR0 + (i - 0.5) * dlnR);
      const t = 0.5 * (tanp[i] + tanp[i - 1]);
      s += (R * dlnR * Math.sqrt(1 + t * t)) / t;
    }
    const u = Math.min(1, Math.max(0, 0.5 + 0.65 * noise2(s / L + 0.71, key ^ 0x2a17)));
    patch[i] = Math.min(1, 1 - share + share * 2.2 * u * u);
    wIn[i] = Math.max(0.1, 1 + ragged * noise2((2 * s) / L + 3.3, key ^ 0x6c3));
    wOut[i] = Math.max(0.1, 1 + ragged * noise2((2 * s) / L + 7.9, key ^ 0x4e1));
  }
  return { patch, wIn, wOut };
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
  const pitchDeg = Math.min(45, Math.max(2, Math.max(base, p.pitchMin ?? 0) * p.pitchScale));
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
  // S107: the pitch grows outward from the majors' start (every arm the same function of R, so the arms keep their
  // spacing), and the majors leave the bar's ends more steeply (1 + open at the start, back to 1 over about a third of
  // a turn).
  const lnRef = Math.log(r0);
  const grow = p.pitchGrow ?? 0;
  const pitchAt = (lnR: number): number => Math.exp(grow * Math.max(0, lnR - lnRef));
  const open = Math.max(0, p.open ?? 0);
  const openLen = 0.35 * Math.PI * tanp;
  const majorPitchAt = open > 0 ? (lnR: number): number => pitchAt(lnR) * (1 + open * Math.exp(-Math.max(0, lnR - lnRef) / Math.max(0.02, openLen))) : pitchAt;
  for (let k = 0; k < 2; k++) arms.push(tabulate("major", r0, r1, phiA + k * Math.PI, pitchDeg, sense, 1, p.width, p, laneKey(p.seed, 1, k, 0), 0.04, majorPitchAt));
  // The lesser arms: between the majors in the log-spiral phase, nudged to the pieces' strongest phase near there.
  const lesser = Math.max(0, Math.min(4, Math.round(p.lesser)));
  const psiA = phiA - (sense * Math.log(r0)) / tanp;
  const hist = piecePhases(g.pieces, sense, tanp);
  const bins = hist.length;
  const rL = r0 * p.lesserStart;
  const nudge = (Math.max(0, p.nudge ?? 35) * Math.PI) / 180;
  const even = Math.min(1, Math.max(0, p.even ?? 0));
  // MW2: with `even`, the gap from the first major to the second takes ceil(lesser / 2) lessers, the other the rest.
  const inGap0 = Math.ceil(lesser / 2);
  const slot = (k: number): { gap: number; f: number } => (k < inGap0 ? { gap: 0, f: (k + 1) / (inGap0 + 1) } : { gap: 1, f: (k - inGap0 + 1) / (lesser - inGap0 + 1) });
  for (let k = 0; k < lesser; k++) {
    // The first two midway between the majors; a third and fourth a quarter turn on from them (MW2, `even`: each at
    // its even fraction of its gap).
    const nominal = even > 0 ? psiA + slot(k).gap * Math.PI + slot(k).f * Math.PI : psiA + Math.PI / 2 + (k % 2) * Math.PI + (k >= 2 ? Math.PI / 4 : 0);
    let best = nominal;
    let bestH = -1;
    for (let b = 0; b < bins; b++) {
      const psi = ((b + 0.5) * TAU) / bins;
      const d = wrap(psi - nominal);
      if (Math.abs(d) > nudge) continue;
      // Preferring the midway phase a little: a flat histogram leaves it there.
      const h = hist[b] * (1 - 0.3 * (Math.abs(d) / Math.max(1e-9, nudge)));
      if (h > bestH) {
        bestH = h;
        best = nominal + d;
      }
    }
    // (With a growing pitch the phase is carried from the majors' start to the lesser start along the same winding.)
    const phiL = grow > 0 ? best + (sense * lnRef) / tanp + sense * windingTo(lnRef, Math.log(rL), tanp, pitchAt) : best + (sense * Math.log(rL)) / tanp;
    const arm = tabulate("lesser", rL, Math.max(rL * 1.2, r1 * (p.lesserReach ?? LESSER_REACH)), phiL, pitchDeg, sense, p.lesserLevel, p.width * (p.lesserWidth ?? 0.85), p, laneKey(p.seed, 2, k, 0), 0.12, pitchAt);
    if (even > 0) evenOut(arm, arms[0], arms[1], slot(k), best - nominal, even, sense);
    arms.push(arm);
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
    arms.push(tabulate("spur", rs, rs * Math.exp(length), parent.phi[i], spurPitch, sense, 0.5 * parent.strength[i] + 0.1, p.width * 0.7, { ...p, fade: 0.6, drift: p.drift * 0.5, kink: 0 }, key, 0.15, pitchAt));
  }
  return { arms, sense, pitchDeg, width: p.width };
}

/** A major's crest azimuth (unwrapped) at ln R, carried on at its end pitch outside its table. */
function crestAt(a: SkelArm, lnR: number, sense: number): number {
  const x = (lnR - a.lnR0) / a.dlnR;
  if (x <= 0) return a.phi[0] + (sense * (lnR - a.lnR0)) / a.tanp[0];
  if (x >= a.n - 1) return a.phi[a.n - 1] + (sense * (lnR - a.lnR0 - (a.n - 1) * a.dlnR)) / a.tanp[a.n - 1];
  return lerp(a.phi, x);
}

/**
 * MW2 (the even winding): a lesser arm's crest moved, by the share `even`, onto its even fraction `f` of its gap between
 * the two majors' crests on each ring (gap 0 from the first major round to the second in the sense of growing azimuth,
 * gap 1 from the second back to the first), plus its nudge `off`; its pitch read back off the moved crest.
 */
function evenOut(arm: SkelArm, m0: SkelArm, m1: SkelArm, at: { gap: number; f: number }, off: number, even: number, sense: number): void {
  let shift = 0;
  for (let i = 0; i < arm.n; i++) {
    const lnR = arm.lnR0 + i * arm.dlnR;
    const p0 = crestAt(m0, lnR, sense);
    const p1 = crestAt(m1, lnR, sense);
    const gap0 = wrap(p1 - p0 - Math.PI) + Math.PI;
    let target = (at.gap === 0 ? p0 + at.f * gap0 : p0 + gap0 + at.f * (TAU - gap0)) + off;
    if (i === 0) shift = TAU * Math.round((arm.phi[0] - target) / TAU);
    target += shift;
    arm.phi[i] += even * (target - arm.phi[i]);
  }
  const lo = Math.tan(Math.PI / 180);
  const hi = Math.tan(Math.PI / 3);
  for (let i = 0; i < arm.n; i++) {
    const a = Math.max(0, i - 1);
    const b = Math.min(arm.n - 1, i + 1);
    const dphi = (arm.phi[b] - arm.phi[a]) * sense;
    arm.tanp[i] = dphi > 0 ? Math.min(hi, Math.max(lo, ((b - a) * arm.dlnR) / dphi)) : hi;
  }
}

/** The winding (rad) from ln R a to b at base tan(pitch) `tanp` times pitchAt (a constant pitch: (b - a) / tanp). */
function windingTo(a: number, b: number, tanp: number, pitchAt: (lnR: number) => number): number {
  const steps = 64;
  const base = (Math.atan(tanp) * 180) / Math.PI;
  let w = 0;
  for (let i = 0; i < steps; i++) {
    const lnR = a + ((i + 0.5) / steps) * (b - a);
    w += (b - a) / steps / Math.tan((Math.min(60, base * pitchAt(lnR)) * Math.PI) / 180);
  }
  return w;
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

/** S107: an arm's clump multiplier at radius R (1 without patchiness or outside it). */
export function patchAt(a: SkelArm, R: number): number {
  if (!a.patch) return 1;
  const x = at(a, R);
  return x === null ? 1 : lerp(a.patch, x);
}

/** S107: an arm's width at radius R on its inner (side +1) or outer (-1) side, kpc. */
export function sideWidth(a: SkelArm, R: number, side: number): number {
  const t = side >= 0 ? a.wIn : a.wOut;
  if (!t) return a.width;
  const x = at(a, R);
  return x === null ? a.width : a.width * lerp(t, x);
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
  /** The ridge's FWHM there, kpc (S107: on the point's side of the crest). */
  width: number;
  /** S107: the arm's clump multiplier there (1 without patchiness). */
  patch?: number;
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
      best = a.patch || a.wIn ? { distance: dist, strength: h.strength, arm: k, side, width: sideWidth(a, R, side), patch: patchAt(a, R) } : { distance: dist, strength: h.strength, arm: k, side, width: a.width };
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
 * Ring by ring and arm by arm, only the rows within 3.5 sigma of the wing of each crest are touched. S107: `plainMean`,
 * if given (`width` values), takes each ring's mean of the band without the arms' clumps (the light kept per ring is
 * the unclumped arm's, so a ring crossing a bright clump is not dimmed between the arms - concentric bands otherwise).
 */
export function skeletonBand(sk: Skeleton, width: number, height: number, rHi: number, wingAll: number, plainMean: Float64Array | null = null): Float32Array {
  const out = new Float32Array(width * height);
  // The unclumped band of the ring in hand (one column: every arm crossing it is drawn before the next ring).
  const plain = plainMean ? new Float32Array(height) : null;
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
    if (plain) plain.fill(0);
    for (const a of sk.arms) {
      // S107: a spur's glow has no wing (its wing, three widths across a short branch, began square across it where
      // the spur leaves its arm: a straight edge in the haze).
      const wing = a.kind === "spur" ? 0 : wingAll;
      const s = a.width / 2.3548;
      // (S107: the core's reach at its widest ragged side; the wing's at the even width.)
      const core = 3.5 * s * (a.wMax ?? 1);
      const reachKpc = wing > 0 ? Math.max(3 * 3.2 * s, core) : core;
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
      // S107: the clumps and the two sides' widths on this ring (the arm's own tables; 1 and the width without them).
      const clump = R >= a.r0 ? patchAt(a, R) : 1;
      const wInner = R >= a.r0 ? sideWidth(a, R, 1) : a.width;
      const wOuter = R >= a.r0 ? sideWidth(a, R, -1) : a.width;
      const clumped = !!(a.patch || a.wIn);
      for (let j = jLo; j <= jHi; j++) {
        const dphi = (j - centre) * dPhi;
        const foot = lnR + sense * dphi * sin * cos;
        if (foot < a.lnR0) continue;
        const t = Math.min(1, Math.max(0, (foot - a.lnR0 - startLen) / startLen));
        const blend = t * t * (3 - 2 * t);
        const atFoot = blend < 1 ? lerp(a.strength, Math.min(a.n - 1, (foot - a.lnR0) / a.dlnR)) : 0;
        const strength = atFoot + (ringStrength - atFoot) * blend;
        if (strength <= 1e-3) continue;
        const across = R * dphi * sin;
        let u: number;
        let v: number;
        if (clumped) {
          // S107: the clumps and the ragged sides on the crest's core only - the wing (three widths across: much of
          // the ring at a low pitch) read at the even width and unclumped, else each ring's clump would lay a faint
          // arc along the whole wing.
          const ws = (dphi * sense >= 0 ? wInner : wOuter) / 2.3548;
          const x = across / ws;
          const core = Math.exp(-0.5 * x * x) * (1 - wing);
          const wingPart = wing * Math.exp(-0.5 * (across / ((3 * a.width) / 2.3548)) ** 2);
          u = strength * (core + wingPart);
          v = strength * (clump * core + wingPart);
        } else {
          u = strength * bandProfile(across, a.width, wing);
          v = u;
        }
        const row = ((j % height) + height) % height;
        const o = row * width + c;
        if (v > out[o]) out[o] = v;
        if (plain && u > plain[row]) plain[row] = u;
      }
    }
    if (plain && plainMean) {
      let sum = 0;
      for (let r = 0; r < height; r++) sum += plain[r];
      plainMean[c] = sum / height;
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
  return Math.min(1, v * (hit.patch ?? 1)) * Math.pow(hit.strength, fadePow);
}
