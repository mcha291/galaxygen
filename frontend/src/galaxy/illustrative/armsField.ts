// The arms' weight over the disc (BUILD_VIII row 108): pure arithmetic on the model's published arm contrast, shaped
// into a polar map of the illustrative look's own. Display-only (D275): nothing here is a published number.
//
// From the published (R, phi) contrast - the stars' pattern_density_contrast blended with gas_density_contrast - each
// ring is normalised by its own mean (n = c / <c>), its deviation optionally evened across radii (so the outer arms,
// whose model amplitude is a fifth of the inner ones', read as strongly), raised to a power and normalised again
// (a = n^p / <n^p>: the ridge narrows and the ring's mean light is kept), and a floor laid under it between the arms
// (L = floor + (1 - floor) a, the ring mean still 1). Inside the bar (bar_half_length) or an inner radius it fades to
// nothing, so the bar and the bulge are never brightened. Beyond the ring where the model's arms fade out the pattern
// is carried outward along the arms' own measured winding, so the arms reach the disc's edge as the goals' do.

export interface ArmGrid {
  nR: number;
  nPhi: number;
  /** The grid's outer radius, kpc (the inner is 0). */
  rHi: number;
}

export interface ArmShape {
  /** The gas contrast's share in the blend, 0 the stars' alone. */
  gasMix: number;
  /** The ridge's power. */
  power: number;
  /** 0 the model's amplitudes; 1 every ring's deviation scaled to `level`. */
  equalise: number;
  /** The light's floor between the arms (share of the ring mean). */
  floor: number;
  /** The highest light multiplier on a ridge. */
  cap: number;
  /** Where the effect starts, kpc (bar_half_length times barFade, else `inner`). */
  start: number;
  /** The fade-in's width, kpc. */
  width: number;
  /** How far past the model's arms' end the pattern is carried, kpc. */
  extend: number;
  /** The young light's own power over the ridge. */
  young: number;
}

/** The deviation an evened ring is scaled to (the model's typical outer-disc sd is 0.1-0.25). */
export const EQUAL_LEVEL = 0.25;
/** The most an evened ring's deviation is multiplied. */
export const EQUAL_MAX = 6;

export function smoothstep(e0: number, e1: number, x: number): number {
  if (e1 <= e0) return x < e0 ? 0 : 1;
  const t = Math.min(1, Math.max(0, (x - e0) / (e1 - e0)));
  return t * t * (3 - 2 * t);
}

/** The fade-in outside the bar: 0 inside `start`, 1 from start + width. */
export const barFade = (r: number, start: number, width: number): number => smoothstep(start, start + width, r);

/** Each ring's values over its mean (a ring whose mean is not positive: 1s). In place on a copy. */
export function ringNormalise(values: ArrayLike<number>, nR: number, nPhi: number): Float64Array {
  const out = new Float64Array(nR * nPhi);
  for (let i = 0; i < nR; i++) {
    let s = 0;
    for (let j = 0; j < nPhi; j++) s += Number(values[i * nPhi + j]);
    const mean = s / nPhi;
    for (let j = 0; j < nPhi; j++) out[i * nPhi + j] = mean > 0 && Number.isFinite(mean) ? Math.max(0, Number(values[i * nPhi + j]) / mean) : 1;
  }
  return out;
}

/** Each ring's standard deviation. */
export function ringSd(n: Float64Array, nR: number, nPhi: number): Float64Array {
  const out = new Float64Array(nR);
  for (let i = 0; i < nR; i++) {
    let s = 0;
    let s2 = 0;
    for (let j = 0; j < nPhi; j++) {
      const v = n[i * nPhi + j];
      s += v;
      s2 += v * v;
    }
    const m = s / nPhi;
    out[i] = Math.sqrt(Math.max(0, s2 / nPhi - m * m));
  }
  return out;
}

/** a = n^p over its ring mean (n >= 0): the ridge narrowed, the ring's mean kept at 1. */
export function sharpen(n: Float64Array, nR: number, nPhi: number, power: number): Float64Array {
  const out = new Float64Array(nR * nPhi);
  for (let i = 0; i < nR; i++) {
    let s = 0;
    for (let j = 0; j < nPhi; j++) {
      const v = Math.pow(Math.max(0, n[i * nPhi + j]), power);
      out[i * nPhi + j] = v;
      s += v;
    }
    const mean = s / nPhi;
    for (let j = 0; j < nPhi; j++) out[i * nPhi + j] = mean > 0 ? out[i * nPhi + j] / mean : 1;
  }
  return out;
}

/** The light under a floor: floor + (1 - floor) a, capped (the ring's mean stays 1 below the cap). */
export const floored = (a: number, floor: number, cap: number): number => Math.min(cap, floor + (1 - floor) * a);

/** The ring index of a radius (cell centres at (i + 0.5) dR). */
const ringOf = (g: ArmGrid, r: number): number => Math.min(g.nR - 1, Math.max(0, Math.round(r / (g.rHi / g.nR) - 0.5)));

/**
 * The arms' end and winding: the outermost ring whose deviation is at least half the disc's typical (the median over
 * the structured rings outside `inner`), and the phase shift per unit ln R measured by cross-correlating that ring with
 * one 2 kpc inside it. Null where the field has no structure outside `inner`.
 */
export function armWinding(n: Float64Array, g: ArmGrid, inner: number): { ref: number; k: number } | null {
  const sd = ringSd(n, g.nR, g.nPhi);
  const i0 = ringOf(g, inner);
  const structured: number[] = [];
  for (let i = i0; i < g.nR; i++) if (sd[i] > 0.02) structured.push(sd[i]);
  if (structured.length < 4) return null;
  const sorted = [...structured].sort((a, b) => a - b);
  const typical = sorted[Math.floor(sorted.length / 2)];
  let ref = -1;
  for (let i = g.nR - 1; i >= i0; i--) {
    if (sd[i] >= 0.5 * typical) {
      ref = i;
      break;
    }
  }
  const dR = g.rHi / g.nR;
  const a = ref - Math.round(2 / dR);
  if (ref < 0 || a < i0 || a < 1) return null;
  const P = g.nPhi;
  let best = 0;
  let bestScore = -Infinity;
  const half = Math.floor(P / 4);
  for (let s = -half; s <= half; s++) {
    let score = 0;
    for (let j = 0; j < P; j++) score += (n[ref * P + j] - 1) * (n[a * P + ((((j - s) % P) + P) % P)] - 1);
    if (score > bestScore) {
      bestScore = score;
      best = s;
    }
  }
  const rRef = (ref + 0.5) * dR;
  const rA = (a + 0.5) * dR;
  const k = ((best * 2 * Math.PI) / P) / Math.log(rRef / rA);
  return { ref, k };
}

/** A ring's normalised values read at a fractional azimuth cell, periodic, linear between cells. */
function readRing(n: Float64Array, ring: number, P: number, cell: number): number {
  const c = ((cell % P) + P) % P;
  const j0 = Math.floor(c);
  const f = c - j0;
  return n[ring * P + j0] * (1 - f) + n[ring * P + ((j0 + 1) % P)] * f;
}

/** The blended contrast, normalised per ring, carried outward past the arms' end along their winding. */
export function armContrast(pattern: ArrayLike<number> | null, gas: ArrayLike<number> | null, g: ArmGrid, shape: Pick<ArmShape, "gasMix" | "extend" | "start">): Float64Array {
  const N = g.nR * g.nPhi;
  const blend = new Float64Array(N);
  const w = pattern ? (gas ? shape.gasMix : 0) : 1;
  for (let k = 0; k < N; k++) blend[k] = (1 - w) * (pattern ? Number(pattern[k]) : 1) + w * (gas ? Number(gas[k]) : 1);
  const n = ringNormalise(blend, g.nR, g.nPhi);
  if (shape.extend <= 0) return n;
  const wind = armWinding(n, g, Math.max(shape.start, 1));
  if (!wind) return n;
  const dR = g.rHi / g.nR;
  const rRef = (wind.ref + 0.5) * dR;
  const P = g.nPhi;
  const refSd = ringSd(n, g.nR, g.nPhi)[wind.ref];
  for (let i = wind.ref + 1; i < g.nR; i++) {
    const r = (i + 0.5) * dR;
    const fade = 1 - smoothstep(rRef + 0.6 * shape.extend, rRef + shape.extend, r);
    const shift = (wind.k * Math.log(r / rRef) * P) / (2 * Math.PI);
    // The model's own ring where it still has more structure than the carried one; else the carried pattern.
    let own = 0;
    for (let j = 0; j < P; j++) own += (n[i * P + j] - 1) ** 2;
    const ownSd = Math.sqrt(own / P);
    if (ownSd >= refSd * fade) continue;
    for (let j = 0; j < P; j++) n[i * P + j] = 1 + (readRing(n, wind.ref, P, j - shift) - 1) * fade;
  }
  return n;
}

/**
 * The map handed to the march, RGBA per texel (index (iPhi * nR + iR) * 4, phi the row as the field's textures are):
 * R the light multiplier, G the arm share (0 between the arms, 1 on a ridge) times the fade, B the young light's
 * multiplier, A the fade outside the bar. Strength 0, or a fade of 0: R = B = 1, G = A = 0.
 */
export function armMap(n: Float64Array, g: ArmGrid, shape: ArmShape, strength: number): Float32Array {
  const { nR, nPhi } = g;
  const dR = g.rHi / nR;
  const sd = ringSd(n, nR, nPhi);
  const even = new Float64Array(nR * nPhi);
  for (let i = 0; i < nR; i++) {
    const gain = sd[i] > 1e-6 ? 1 + shape.equalise * (Math.min(EQUAL_MAX, EQUAL_LEVEL / sd[i]) - 1) : 1;
    for (let j = 0; j < nPhi; j++) even[i * nPhi + j] = Math.max(0, 1 + (n[i * nPhi + j] - 1) * gain);
  }
  const a = sharpen(even, nR, nPhi, shape.power);
  const y = sharpen(even, nR, nPhi, shape.young);
  const out = new Float32Array(nR * nPhi * 4);
  for (let i = 0; i < nR; i++) {
    const f = barFade((i + 0.5) * dR, shape.start, shape.width) * strength;
    const fa = Math.min(1, f);
    for (let j = 0; j < nPhi; j++) {
      const v = a[i * nPhi + j];
      const light = floored(v, shape.floor, shape.cap);
      const o = (j * nR + i) * 4;
      out[o] = Math.max(0, 1 + (light - 1) * f);
      out[o + 1] = fa * smoothstep(1, 2.2, v);
      out[o + 2] = Math.max(0, 1 + (Math.min(shape.cap, y[i * nPhi + j]) - 1) * f);
      out[o + 3] = fa;
    }
  }
  return out;
}

/** The grid an arrays frame is on: the header's R and phi axes, else 400 x 360 over 30 kpc (grids.py). */
export function gridOf(header: { [key: string]: unknown } | undefined, length: number): ArmGrid {
  const axes = ((header?.grid as { axes?: Record<string, { n?: number; hi?: number }> } | undefined)?.axes) ?? {};
  const nR = axes.R?.n ?? 400;
  const nPhi = axes.phi?.n ?? 360;
  const rHi = axes.R?.hi ?? 30;
  if (nR * nPhi !== length) return { nR: 400, nPhi: Math.max(1, Math.round(length / 400)), rHi: 30 };
  return { nR, nPhi, rHi };
}
