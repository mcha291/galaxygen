// The arms' weight over the disc (BUILD_VIII row 108): pure arithmetic on the model's published arm contrast, shaped
// into a polar map of the illustrative look's own. Display-only (D275): nothing here is a published number.
//
// From the published (R, phi) contrast - the stars' pattern_density_contrast blended with gas_density_contrast - each
// ring is normalised by its own mean (n = c / <c>), its deviation optionally evened across radii (so the outer arms,
// whose model amplitude is a fifth of the inner ones', read as strongly), raised to a power and normalised again
// (a = n^p / <n^p>: the ridge narrows), saturated into a ridge share (1 - e^-a) with a floor laid under it between the
// arms, L = floor + (1 - floor)(1 - e^-a), and divided by its ring mean (the ring's mean light kept). Inside the bar (bar_half_length) or an inner radius it fades to
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
  /** Where the ridge share saturates, in sharpened units (ring mean 1): higher keeps a strong arm brighter than a weak one. */
  knee: number;
  /** The highest light multiplier on a ridge. */
  cap: number;
  /** Where the effect starts, kpc (bar_half_length times barFade, else `inner`). */
  start: number;
  /** The fade-in's width, kpc. */
  width: number;
  /** How far past the model's arms' end the pattern is carried, kpc. */
  extend: number;
  /** The clustered young light's floor between the arms, as a share of a full ridge's (1: as the model places it). */
  young: number;
  /** The ridge lines' share in the ridge (0 the sharpened contrast alone, 1 the lines alone). */
  lineMix: number;
  /** The ridge lines' full width at half maximum across the arm, kpc. */
  armWidth: number;
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
  const span = Math.round(3 / dR);
  const gap = Math.max(1, Math.round(0.3 / dR));
  if (ref < 0 || ref - span - gap < Math.max(i0, 1)) return null;
  // The winding ring by ring: the best small shift between rings `gap` apart over the last 3 kpc inside the end, each
  // a dphi / dlnR; their median (a single wide correlation across kpc locks onto the wrong arm).
  const P = g.nPhi;
  const half = Math.max(2, Math.round(P / 30));
  const ks: number[] = [];
  for (let i = ref - span; i <= ref; i += 2) {
    const a = i - gap;
    let best = 0;
    let bestScore = -Infinity;
    for (let s = -half; s <= half; s++) {
      let score = 0;
      for (let j = 0; j < P; j++) score += (n[i * P + j] - 1) * (n[a * P + ((((j - s) % P) + P) % P)] - 1);
      if (score > bestScore) {
        bestScore = score;
        best = s;
      }
    }
    ks.push(((best * 2 * Math.PI) / P) / Math.log((i + 0.5) / (a + 0.5)));
  }
  ks.sort((x, y) => x - y);
  return { ref, k: ks[Math.floor(ks.length / 2)] };
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
  // The ridge share: the sharpened contrast's (1 - e^(-a / knee)) mixed with the ridge lines' narrow profile.
  const share = new Float64Array(nR * nPhi);
  for (let k = 0; k < share.length; k++) share[k] = ridge(a[k], shape.knee);
  if (shape.lineMix > 0) {
    const wind = armWinding(n, g, Math.max(shape.start, 1));
    const lines = ridgeLines(even, g, shape.armWidth, wind ? wind.k : DEFAULT_WINDING);
    for (let k = 0; k < share.length; k++) share[k] = share[k] * (1 - shape.lineMix) + lines[k] * shape.lineMix;
  }
  const light = ringLight(share, nR, nPhi, shape.floor, shape.cap);
  const young = ringLight(share, nR, nPhi, shape.young, YOUNG_CAP);
  const out = new Float32Array(nR * nPhi * 4);
  for (let i = 0; i < nR; i++) {
    const f = barFade((i + 0.5) * dR, shape.start, shape.width) * strength;
    const fa = Math.min(1, f);
    for (let j = 0; j < nPhi; j++) {
      const k = i * nPhi + j;
      const o = (j * nR + i) * 4;
      out[o] = Math.max(0, 1 + (light[k] - 1) * f);
      out[o + 1] = fa * smoothstep(0.25, 0.9, share[k]) * (sd[i] > 0.02 ? 1 : 0);
      out[o + 2] = Math.max(0, 1 + (young[k] - 1) * f);
      out[o + 3] = fa;
    }
  }
  return out;
}

/** The young light's cap on a ridge. */
export const YOUNG_CAP = 4;
/** dphi / dlnR where the field's winding cannot be measured (a pitch of about 18 degrees). */
export const DEFAULT_WINDING = 3;

/** The ridge's share from a sharpened value (ring mean 1): 0 between the arms, toward 1 on a ridge, saturating. */
export const ridge = (a: number, knee = 1): number => 1 - Math.exp(-Math.max(0, a) / Math.max(1e-3, knee));

/**
 * The ridge lines: on each ring the local maxima of the (evened, lightly smoothed) contrast that stand above the ring by
 * a third of its deviation, each drawn as a flat-topped profile across the arm of full width at half maximum `width` kpc - the
 * distance across an arm at (R, dphi) being R dphi sin(pitch), the pitch from the winding k (tan pitch = 1 / |k|) -
 * and of height its prominence over twice the ring's deviation (at most 1). A share in [0, 1], 0 between the arms:
 * the arm's width the slider's whatever the model's ridge's.
 */
export function ridgeLines(even: Float64Array, g: ArmGrid, width: number, k: number): Float64Array {
  const { nR, nPhi: P } = g;
  const dR = g.rHi / nR;
  const out = new Float64Array(nR * P);
  const sinPitch = 1 / Math.sqrt(1 + k * k);
  // A flat-topped profile with sharp edges, exp(-(d / s)^4 / 2): half its height at d = 1.0845 s.
  const sigma = Math.max(0.01, width) / (2 * 1.0845);
  const smooth = new Float64Array(P);
  const sd = ringSd(even, nR, P);
  for (let i = 0; i < nR; i++) {
    if (sd[i] <= 0.02) continue;
    const R = (i + 0.5) * dR;
    for (let j = 0; j < P; j++) {
      let s = 0;
      for (let q = -2; q <= 2; q++) s += even[i * P + ((((j + q) % P) + P) % P)];
      smooth[j] = s / 5;
    }
    // The profile's reach in cells: 2 s across the arm (where it is e^-8).
    const cellAcross = (R * ((2 * Math.PI) / P)) * sinPitch;
    const reach = Math.min(Math.floor(P / 2), Math.ceil((2 * sigma) / Math.max(1e-6, cellAcross)));
    for (let j = 0; j < P; j++) {
      const v = smooth[j];
      const dev = v - 1;
      if (dev < sd[i] / 3) continue;
      let peak = true;
      for (let q = 1; q <= 4 && peak; q++) if (smooth[(j + q) % P] > v || smooth[(j - q + P) % P] >= v) peak = false;
      if (!peak) continue;
      const height = Math.min(1, dev / (2 * sd[i]));
      for (let q = -reach; q <= reach; q++) {
        const d = q * cellAcross;
        const x2 = (d * d) / (sigma * sigma);
        const w = height * Math.exp(-0.5 * x2 * x2);
        const o = i * P + ((((j + q) % P) + P) % P);
        if (w > out[o]) out[o] = w;
      }
    }
  }
  return out;
}

/**
 * The light over a ring from its ridge share: floor + (1 - floor) share - the gaps at `floor` of a full ridge's light
 * whatever the arm's own amplitude - divided by the ring's mean (the ring's mean light kept) and capped.
 */
export function ringLight(share: Float64Array, nR: number, nPhi: number, floor: number, cap: number): Float64Array {
  const out = new Float64Array(nR * nPhi);
  for (let i = 0; i < nR; i++) {
    let s = 0;
    for (let j = 0; j < nPhi; j++) {
      const v = floor + (1 - floor) * share[i * nPhi + j];
      out[i * nPhi + j] = v;
      s += v;
    }
    const mean = s / nPhi;
    for (let j = 0; j < nPhi; j++) out[i * nPhi + j] = mean > 0 ? Math.min(cap, out[i * nPhi + j] / mean) : 1;
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
