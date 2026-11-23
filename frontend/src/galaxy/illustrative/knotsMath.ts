// The pink HII regions' arithmetic (S106, BUILD_VIII row 106; knots.ts, knotsLayer.tsx): no three.js here, the pure
// parts, tested (knots.test.ts). Display-only (D275): every number here is an illustrative choice, never physics. The
// regions' places and their own light are the model's (/api/clusters, as the field mode's knots are drawn); their size,
// the compression of their light, their colour, their irregular shape and their core are the viewer's.

/** Sub-blobs per region at most (each an attribute vec4: offset x, offset y, sigma, weight; in units of the radius). */
export const MAX_BLOBS = 4;

/** H-alpha pink and magenta as linear RGB, each of mean 1 (colour for appearance; the grade runs after). */
export const PINK: readonly [number, number, number] = norm3([1.0, 0.3, 0.45]);
export const MAGENTA: readonly [number, number, number] = norm3([1.0, 0.25, 0.85]);
/** The young cluster's white-blue (mean 1). */
export const CORE_COLOUR: readonly [number, number, number] = norm3([0.75, 0.9, 1.3]);

function norm3(c: readonly [number, number, number]): [number, number, number] {
  const m = (c[0] + c[1] + c[2]) / 3;
  return m > 0 ? [c[0] / m, c[1] / m, c[2] / m] : [1, 1, 1];
}

/**
 * A stable hash of a region's index and a salt into [0, 1): lowbias32 (the viewer's own seed; never time- or
 * frame-seeded, so a region keeps its shape from frame to frame and across reloads).
 */
export function hash01(index: number, salt: number): number {
  let x = (Math.imul(index | 0, 0x9e3779b1) ^ Math.imul(salt | 0, 0x85ebca6b)) >>> 0;
  x ^= x >>> 16;
  x = Math.imul(x, 0x7feb352d) >>> 0;
  x ^= x >>> 15;
  x = Math.imul(x, 0x846ca68b) >>> 0;
  x ^= x >>> 16;
  return (x >>> 0) / 4294967296;
}

/** The region's drawn radius, pc: its own radius times the multiplier, clamped to [floor, ceiling]. */
export function regionRadius(hiiRadiusPc: number, multiplier: number, floorPc: number, ceilingPc: number): number {
  const r = Number.isFinite(hiiRadiusPc) && hiiRadiusPc > 0 ? hiiRadiusPc * multiplier : 0;
  const hi = Math.max(floorPc, ceilingPc);
  return Math.min(hi, Math.max(floorPc, r));
}

/** A luminosity compressed about a reference: ref (L / ref)^power; 0 for none (power 1 leaves it as it is). */
export function compressLight(l: number, ref: number, power: number): number {
  if (!(l > 0) || !Number.isFinite(l) || !(ref > 0)) return 0;
  return ref * Math.pow(l / ref, power);
}

/** The q-quantile (0..1) of the positive finite values, by sorting a copy; 0 where there is none. */
export function quantile(values: ArrayLike<number>, q: number): number {
  const v = Array.from(values).filter((x) => x > 0 && Number.isFinite(x)).sort((a, b) => a - b);
  if (v.length === 0) return 0;
  const at = Math.min(v.length - 1, Math.max(0, Math.round(q * (v.length - 1))));
  return v[at];
}

/**
 * The weight a region takes from the arm contrast at its place (the dust's placement, the gas's own contrast, D210,
 * taken relative to its ring: ringContrast): min(1, (contrast / level)^power) - at the level and above 1, below it
 * falling as the power. Power 0: 1 everywhere.
 */
export function armWeight(contrast: number, level: number, power: number): number {
  if (power <= 0) return 1;
  const c = Math.max(0, contrast) / Math.max(1e-6, level);
  return Math.min(1, Math.pow(c, power));
}

/**
 * The march's polar placement texture as the CPU holds it (FieldVolume's scatter DataTexture: RGBA float, `width` the
 * R cells over [rLo, rHi], `height` the phi cells over the turn, texel (j * width + i) * 4, alpha the placement).
 */
export interface Placement {
  data: ArrayLike<number>;
  width: number;
  height: number;
  rLo: number;
  rHi: number;
}

/** Each ring's (R cell's) low and high placement - its 10th and 95th percentiles round the turn - as [lo, hi] pairs. */
export function ringRanges(p: Placement): Float64Array {
  const out = new Float64Array(2 * p.width);
  const row = new Float64Array(p.height);
  for (let i = 0; i < p.width; i += 1) {
    for (let j = 0; j < p.height; j += 1) row[j] = Number(p.data[(j * p.width + i) * 4 + 3]);
    const s = Array.from(row).sort((a, b) => a - b);
    out[2 * i] = s[Math.round(0.1 * (s.length - 1))];
    out[2 * i + 1] = s[Math.round(0.95 * (s.length - 1))];
  }
  return out;
}

/**
 * A place's arm contrast relative to its own ring: (c - lo) / (hi - lo) clamped to [0, 1], lo and hi the ring's
 * (ringRanges), so the arms carry the regions at every radius however weak their contrast there; where the ring has no
 * contrast (hi - lo under 0.02: no arm placed) `flat`. Null without a place on the grid.
 */
export function ringContrast(p: Placement, ranges: Float64Array, r: number, phi: number, flat: number): number | null {
  const x = (r - p.rLo) / (p.rHi - p.rLo);
  if (!(x >= 0 && x < 1)) return null;
  const i = Math.min(p.width - 1, Math.floor(x * p.width));
  const turn = ((phi % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);
  const j = Math.min(p.height - 1, Math.floor((turn / (2 * Math.PI)) * p.height));
  const lo = ranges[2 * i];
  const hi = ranges[2 * i + 1];
  if (!(hi - lo >= 0.02)) return flat;
  const c = Number(p.data[(j * p.width + i) * 4 + 3]);
  return Math.min(1, Math.max(0, (c - lo) / (hi - lo)));
}

/** GLSL's smoothstep. */
export function smoothstep(e0: number, e1: number, x: number): number {
  const t = Math.min(1, Math.max(0, (x - e0) / (e1 - e0 || 1e-6)));
  return t * t * (3 - 2 * t);
}

/** The radial fade: 1 inside `fade`, to 0 over `width` past it; and fading in over the kpc below `inner` (0: none). */
export function radialWeight(r: number, fade: number, width: number, inner: number): number {
  const out = 1 - smoothstep(fade, fade + Math.max(width, 1e-3), r);
  const inn = inner > 0 ? smoothstep(inner - 1, inner, r) : 1;
  return out * inn;
}

/** The region's colour: its own line colour (its light per channel over their mean) mixed toward the pink, mean 1. */
export function regionColour(own: readonly [number, number, number], pink: number, magenta: number): [number, number, number] {
  const o = norm3(own);
  const target = [0, 1, 2].map((k) => PINK[k] * (1 - magenta) + MAGENTA[k] * magenta);
  return norm3([0, 1, 2].map((k) => o[k] * (1 - pink) + target[k] * pink) as [number, number, number]);
}

/**
 * A region's sub-blobs from its index: `count` (1..MAX_BLOBS) Gaussians, each [offset x, offset y, sigma, weight] in
 * units of the drawn radius, the weights summing to 1; the unused ones weight 0. The first lies near the centre and is
 * the widest; the others scattered `irregular` radii out. `soft` scales every sigma.
 */
export function regionBlobs(index: number, count: number, irregular: number, soft: number): number[][] {
  const n = Math.max(1, Math.min(MAX_BLOBS, Math.round(count)));
  const out: number[][] = [];
  let total = 0;
  for (let k = 0; k < MAX_BLOBS; k += 1) {
    if (k >= n) {
      out.push([0, 0, 0.5 * soft, 0]);
      continue;
    }
    const a = 2 * Math.PI * hash01(index, 4 * k + 1);
    const reach = (k === 0 ? 0.25 : 0.5 + 0.5 * hash01(index, 4 * k + 2)) * irregular;
    const sigma = (k === 0 ? 0.55 : 0.3 + 0.25 * hash01(index, 4 * k + 3)) * soft;
    const w = k === 0 ? 1 : 0.35 + 0.65 * hash01(index, 4 * k + 4);
    out.push([reach * Math.cos(a), reach * Math.sin(a), sigma, w]);
    total += w;
  }
  for (const b of out) b[3] /= total;
  return out;
}

/** Whether a region carries its young cluster's core: a stable share of them. */
export const hasCore = (index: number, share: number): boolean => hash01(index, 97) < share;

/** The indices of the `limit` brightest (by `light`), brightest first; ties by index. */
export function brightest(light: ArrayLike<number>, limit: number): number[] {
  const idx = Array.from({ length: light.length }, (_, i) => i).filter((i) => light[i] > 0 && Number.isFinite(light[i]));
  idx.sort((a, b) => light[b] - light[a] || a - b);
  return idx.slice(0, Math.max(0, Math.round(limit)));
}

/** The regions' parameters as regionAttributes reads them (knots.ts's controls, by their local keys). */
export type RegionParams = Readonly<Record<string, number>>;

/**
 * The CPU side's attribute values for the regions at these parameters, compacted to the regions drawn: each region's
 * light compressed about the 90th percentile, weighted by the arm (ring-relative contrast at its place, armWeight) and
 * the radial fade, coloured; the brightest `count` of them by that weighted light; their drawn radius, their sub-blobs
 * and their core. Without a placement every arm weight is 1.
 */
export function regionAttributes(
  knots: { positions: Float32Array; flux: Float32Array; extent: Float32Array },
  p: RegionParams,
  placement: Placement | null,
) {
  const n = knots.extent.length;
  const lum = new Float64Array(n);
  for (let i = 0; i < n; i += 1) lum[i] = (knots.flux[3 * i] + knots.flux[3 * i + 1] + knots.flux[3 * i + 2]) / 3;
  const ref = quantile(lum, 0.9);
  const ranges = placement ? ringRanges(placement) : null;
  const weighted = new Float64Array(n);
  for (let i = 0; i < n; i += 1) {
    const x = knots.positions[3 * i];
    const z = knots.positions[3 * i + 2];
    const r = Math.hypot(x, z);
    const phi = Math.atan2(-z, x);
    const t = placement && ranges ? ringContrast(placement, ranges, r, phi, p.armFlat ?? 0.2) : null;
    const w = (t === null ? 1 : armWeight(t, p.armLevel ?? 0.6, p.armPower ?? 2)) * radialWeight(r, p.fadeR ?? 14, p.fadeWidth ?? 4, p.innerR ?? 0);
    weighted[i] = w > 1e-3 ? w * compressLight(lum[i], ref, p.lumPower ?? 0.35) : 0;
  }
  const order = brightest(weighted, p.count ?? n);
  const m = order.length;
  const out = {
    order,
    positions: new Float32Array(3 * m),
    light: new Float32Array(3 * m),
    core: new Float32Array(3 * m),
    radius: new Float32Array(m),
    blobs: Array.from({ length: MAX_BLOBS }, () => new Float32Array(4 * m)),
  };
  order.forEach((i, k) => {
    out.positions.set(knots.positions.subarray(3 * i, 3 * i + 3), 3 * k);
    const own: [number, number, number] = [knots.flux[3 * i], knots.flux[3 * i + 1], knots.flux[3 * i + 2]];
    const c = regionColour(own, p.pink ?? 0.8, p.magenta ?? 0.4);
    const core = hasCore(i, p.coreShare ?? 0.6);
    for (let ch = 0; ch < 3; ch += 1) {
      out.light[3 * k + ch] = weighted[i] * c[ch];
      out.core[3 * k + ch] = core ? weighted[i] * CORE_COLOUR[ch] : 0;
    }
    out.radius[k] = regionRadius(knots.extent[i], p.size ?? 8, p.sizeMin ?? 60, p.sizeMax ?? 300);
    regionBlobs(i, p.blobs ?? 3, p.irregular ?? 0.7, p.soft ?? 1).forEach((b, j) => out.blobs[j].set(b, 4 * k));
  });
  return out;
}
