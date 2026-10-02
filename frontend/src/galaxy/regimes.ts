// The field regime (design brief §3, RENDER_PLAN R3/R4/M4): the galaxy's light as a
// volume the renderer integrates along each line of sight. No three.js here.
//
// Since S38 (BUILD_II V1) the light's colour is the filter integral's, run by the model: the
// viewer sends its filter set (filters.ts) to /api/render and gets back each emitting component's
// response in each filter, and divides each channel by its white point and nothing else (rule D5;
// RENDER_PHYSICS §2, "components, not colours").
//
// Since S39 (BUILD_II V2) every component is placed by the model and spread through a layer the
// model names (the render header's `layers`, each a sech²(z / 2h) / 4h profile): the stars in the thin
// disc; the dust, with its own and its scattered light, in the gas's layer, whose height the model
// publishes ring by ring since D206 (S50) — a few tens of parsecs in the inner disc, flaring outward —
// so an inclined view sees a dark lane inside the stellar disc (until then it shared the stars' one
// height); the HII regions' Hα, placed round each ring by the pattern's contrast, in the clouds' layer;
// the diffuse gas's Hα in its own published 1.4 kpc layer, which a tilted view sees brighten toward
// the limb. The dust dims each filter by its own depth from the grain model's curve, and since D207 its
// column round each ring follows the pattern's contrast, as the model places it (`dust_placement`): heavier on
// an arm than between arms, each ring's total unchanged.
//
// **What the field regime still invents at galaxy scale: nothing structural.** The seeded Hα knots,
// the clump lattice, the dust's lead onto the arms' inner edge, the line's and the dust's crowding
// into the arms at a display power, and the per-channel extinction the viewer held (CHANNEL_EXTINCTION)
// are gone (RENDER_PHYSICS §0's exception, closed by V2). What remains the viewer's is display only:
// the white point, the exposure, the tone curve and the bloom, and the ray-march's own sampling (steps,
// the sub-samples along each step, the jitter that turns banding into grain, the pixel budget). Structure below a (R, φ) cell of the
// model's grid — a knot, a filament — is V3's, from the cloud catalogue.

import type { Axis } from "../preview/axes";

/**
 * The drawn value of one published response: divided by its filter's white point, the tone map's
 * one per-channel step. A missing number (NaN) draws nothing rather than a guess (rule B9).
 */
export function balanced(response: number, white: number): number {
  const v = Number(response) / white;
  return Number.isFinite(v) && v > 0 ? v : 0;
}

/**
 * The optical depth of a face-on column from the share of light it lets through (/api/render's
 * `dust_extinction`, 10^(−0.4 A_λ)): τ = −ln T, which the ray-march spreads through the dust's layer.
 * No dust, or a missing number, is no depth (rule B9: nothing is dimmed on a guess).
 */
/** Two arrays of one shape added element by element (S42: a layer's lines summed); either alone if the other is absent. */
export function summed(x?: ArrayLike<number>, y?: ArrayLike<number>): ArrayLike<number> | undefined {
  if (!x || !y) return x ?? y;
  if (x.length !== y.length) throw new Error(`summed: ${x.length} and ${y.length} values`);
  const out = new Float32Array(x.length);
  for (let i = 0; i < x.length; i += 1) out[i] = Number(x[i]) + Number(y[i]);
  return out;
}

export function depthOf(transmission: number): number {
  const t = Number(transmission);
  return Number.isFinite(t) && t > 0 && t < 1 ? -Math.log(t) : 0;
}

/**
 * The scattered light's phase factor for a view at |cos i| = `cosView` to the disc's axis, read from
 * the model's table (/api/render's `dust_scattered.phase`: a Henyey–Greenstein phase function at the
 * published g, averaged over light arriving in the disc's plane) by linear interpolation between its
 * evenly spaced points. The shader's `phaseAt` is this, line for line. 1 (isotropic) without a table.
 */
export function phaseAt(factor: readonly number[] | null | undefined, cosView: number): number {
  if (!factor || factor.length < 2) return 1;
  const x = Math.min(1, Math.max(0, Math.abs(cosView))) * (factor.length - 1);
  const k = Math.min(factor.length - 2, Math.floor(x));
  return factor[k] + (factor[k + 1] - factor[k]) * (x - k);
}

/**
 * The model's layers, kpc (/api/render's header `layers`); a missing one draws its component nowhere. The dust's
 * is one height or, since D206, the name of the render's per-ring array of heights (`dust_height`).
 */
export interface Layers {
  stars: number | null;
  dust: number | string | null;
  halpha_hii?: number | null;
  halpha_dig?: number | null;
}

export interface PlaneFields {
  R: Axis;
  /** The φ axis of the (R, φ) components: the render's window, the whole ring. */
  phi: Axis;
  /**
   * The stellar component's response per (R, φ) cell and filter, row-major over (R, φ, filter),
   * L☉/pc² through each filter (/api/render's `stars`); non-finite means no light is drawn there.
   */
  stars: ArrayLike<number>;
  /** The HII regions' Hα per (R, φ, filter), placed by the model (`halpha_hii`). */
  hii?: ArrayLike<number>;
  /** The diffuse gas's Hα per (R, filter) (`halpha_dig`). */
  dig?: ArrayLike<number>;
  /** The face-on transmission per (R, filter) (`dust_extinction`). */
  extinction?: ArrayLike<number>;
  /** The scattered light per (R, φ, filter), all directions together (`dust_scattered`). */
  scattered?: ArrayLike<number>;
  /** The dust's thermal emission per (R, filter) (`dust_thermal`). */
  thermal?: ArrayLike<number>;
  /**
   * The dust layer's scale height, kpc: per R cell (`dust_height`, D206) or one height for every ring. Missing,
   * or not a positive number at a ring, is no layer there: the dust is drawn nowhere (rule B9).
   */
  dustHeight?: ArrayLike<number> | number | null;
  /**
   * The dust's column at each (R, φ) cell over its ring's mean, row-major over (R, φ) (`dust_placement`, D207):
   * the pattern's contrast, placed by the model. Missing, or not a number at a cell, is an even ring there: 1.
   */
  dustPlacement?: ArrayLike<number> | null;
  /**
   * The white point: each filter's response to a unit of white light (/api/render's `white`). Every
   * channel is divided by it, so white light draws (1, 1, 1) per unit of light in any filter set.
   */
  white: readonly number[];
}

export interface PlaneTexture {
  /** The stars, in the thin disc's layer: RGB each filter's response over its white point; A unused. */
  data: Float32Array;
  /**
   * The scattered light, in the dust's layer, all directions together (the shader applies the phase). A: the
   * dust's placement (D207), its column at the cell over the ring's mean; 1 where the render places nothing.
   */
  scatter: Float32Array;
  /** The HII regions' Hα, in the clouds' layer, over the white point; A unused. */
  hii: Float32Array;
  /**
   * Per ring, three rows of one texel per R cell: row 0 the dust's face-on optical depth per channel,
   * row 1 the diffuse gas's Hα and row 2 the dust's thermal emission, each over the white point. The spare
   * channel: row 0's is the dust diagnostic's level (D205, written by FieldVolume), row 2's the dust layer's
   * scale height, kpc (D206), row 1's unused.
   */
  rings: Float32Array;
  width: number;
  height: number;
  /**
   * One texel's radial width, kpc: the R axis's span over the textures' width in cells (the polar
   * textures and the ring texture share it). The march sub-samples a step finer than this in the plane.
   */
  cell: number;
}

/** The rows of `PlaneTexture.rings`, and where a shader samples each (texel centres). */
export const RING_ROWS = { depth: 0, dig: 1, thermal: 2, count: 3 } as const;

/**
 * RGBA float textures from the published components, one texel per (R cell, φ cell), row-major with φ as
 * the row, and one row per R cell for the per-ring ones. Every value is the model's, over the white point
 * where it is light, or −ln of its transmission where it is dust: nothing is placed, clumped or recoloured.
 */
export function planeTexture(fields: PlaneFields): PlaneTexture {
  const { R, phi, stars, hii, dig, extinction, scattered, thermal, dustHeight, dustPlacement, white } = fields;
  const nPhi = phi.n;
  const nF = white.length;
  const data = new Float32Array(R.n * nPhi * 4);
  const scatter = new Float32Array(R.n * nPhi * 4);
  const line = new Float32Array(R.n * nPhi * 4);
  const rings = new Float32Array(R.n * RING_ROWS.count * 4);
  for (let i = 0; i < R.n; i += 1) {
    const h = Number(typeof dustHeight === "number" ? dustHeight : (dustHeight?.[i] ?? 0));
    rings[(RING_ROWS.thermal * R.n + i) * 4 + 3] = Number.isFinite(h) && h > 0 ? h : 0;
    for (let k = 0; k < 3 && k < nF; k += 1) {
      rings[(RING_ROWS.depth * R.n + i) * 4 + k] = extinction ? depthOf(Number(extinction[i * nF + k])) : 0;
      rings[(RING_ROWS.dig * R.n + i) * 4 + k] = dig ? balanced(Number(dig[i * nF + k]), white[k]) : 0;
      rings[(RING_ROWS.thermal * R.n + i) * 4 + k] = thermal ? balanced(Number(thermal[i * nF + k]), white[k]) : 0;
    }
    for (let j = 0; j < nPhi; j += 1) {
      const q = (j * R.n + i) * 4;
      const at = (i * nPhi + j) * nF;
      const place = dustPlacement ? Number(dustPlacement[i * nPhi + j]) : 1;
      scatter[q + 3] = Number.isFinite(place) && place >= 0 ? place : 1;
      for (let k = 0; k < 3 && k < nF; k += 1) {
        data[q + k] = balanced(Number(stars[at + k]), white[k]);
        scatter[q + k] = scattered ? balanced(Number(scattered[at + k]), white[k]) : 0;
        line[q + k] = hii ? balanced(Number(hii[at + k]), white[k]) : 0;
      }
    }
  }
  return { data, scatter, hii: line, rings, width: R.n, height: nPhi, cell: (R.hi - R.lo) / R.n };
}

/**
 * The most sub-samples the march reads along one step (D197 (3)). At a grazing view a step's in-plane
 * extent spans many cells of the plane texture; read once, neighbouring pixels quantise R at the same
 * step boundaries and the disc draws as concentric terraces. A GLSL loop needs a constant bound.
 */
export const SUB_SAMPLES_MAX = 8;

/**
 * How many sub-samples the march reads along a step whose in-plane length is `inPlane` kpc, over a plane
 * texture of radial cell `cell` kpc: one per cell the step crosses, at least 1, at most `max`. The
 * shader's `n` in the march, line for line.
 */
export function subSamples(inPlane: number, cell: number, max: number = SUB_SAMPLES_MAX): number {
  const n = Math.ceil(inPlane / cell);
  return Number.isNaN(n) ? 1 : Math.min(max, Math.max(1, n));
}

/**
 * The share of a sech²(y / 2h) / 4h layer's column between heights y0 and y1 — the shader's `column` over
 * a unit path, line for line: a difference of tanh, so a step takes its layer's exact column however
 * coarse the step and however thin the layer.
 */
export function layerShare(y0: number, y1: number, h: number): number {
  const t = (y: number) => Math.tanh(Math.min(10, Math.max(-10, y / (2 * h))));
  return Math.abs(t(y1) - t(y0)) / 2;
}

/**
 * The column of a sech²(y / 2h) / 4h layer along a ray from height y0 to y1 over a path `ds` — the shader's
 * `column`, line for line: its share of height over the ray's slope, or for a ray running level the density at
 * its height times the path. No layer (h ≤ 0) is no column.
 */
export function layerColumn(y0: number, y1: number, h: number, ds: number): number {
  if (!(h > 0)) return 0;
  const dy = y1 - y0;
  if (Math.abs(dy) < 1e-4 * h) return (1 / Math.cosh(Math.min(30, Math.max(-30, (0.5 * (y0 + y1)) / (2 * h)))) ** 2 / (4 * h)) * ds;
  return (layerShare(y0, y1, h) * ds) / Math.abs(dy);
}

/**
 * Where the march cuts a sub-step that crosses the dust's layer, in the dust's own scale heights about the
 * midplane (D206). Since the dust has its own height a sub-step may span the whole of a layer far thinner than
 * the stars': treated as one mixed slab (S39's `(1 − e^−τ)/τ`, exact only when light and dust share a profile)
 * it would dim the stars in front of the layer as if they were inside it. Cut here, each piece is composed in
 * order along the ray, and inside a piece the mixing is a small error: beyond the last cut 1.7 × 10⁻⁵ of the
 * dust is left, between two cuts the stars' share is a few of the dust's heights over four of their own. The
 * march's sampling, not physics: `regimes.test.ts` holds it against a quadrature of the two layers (within
 * 0.6 % of the unattenuated light from face-on to cos i = 0.1 over the default galaxy's rings; eight cuts at
 * ±1, ±2.5, ±5 and ±8 left 3.6 %).
 */
export const DUST_CUTS = [-11, -8, -6, -4.5, -3, -2, -1, 1, 2, 3, 4.5, 6, 8, 11] as const;

/**
 * One sub-step of the march through the stars and the dust, composed in order — the shader's piece loop, line for
 * line, for a unit face-on column of starlight in a layer `hStars` and a dust of face-on optical depth `tau` in a
 * layer `hDust`, along a ray from height y0 to y1 over a path `path` (the same units as the heights). Returns the
 * light that leaves the sub-step's near end and the share of what lies behind it that the sub-step lets through.
 */
export function composeStep(y0: number, y1: number, path: number, hStars: number, hDust: number, tau: number): { light: number; transmitted: number } {
  // Heights run upward along the ray in u: the layers are symmetric about the midplane, so a descending ray is
  // the ascending one mirrored.
  const sign = y1 >= y0 ? 1 : -1;
  const u0 = sign * y0;
  const u1 = sign * y1;
  const du = u1 - u0;
  const whole = !(hDust > 0) || du <= 1e-6 * hDust;
  let light = 0;
  let transmitted = 1;
  for (let m = 0; m <= DUST_CUTS.length; m += 1) {
    let a = u0;
    let b = u1;
    let share = 1;
    if (whole) {
      if (m > 0) break;
    } else {
      a = Math.max(u0, m === 0 ? -1e9 : DUST_CUTS[m - 1] * hDust);
      b = Math.min(u1, m === DUST_CUTS.length ? 1e9 : DUST_CUTS[m] * hDust);
      if (b <= a) continue;
      share = (b - a) / du;
    }
    const ds = path * share;
    const depth = tau * layerColumn(a, b, hDust, ds);
    const own = depth >= 1e-3 ? (1 - Math.exp(-depth)) / Math.max(depth, 1e-6) : 1 - 0.5 * depth;
    light += transmitted * layerColumn(a, b, hStars, ds) * own;
    transmitted *= Math.exp(-depth);
  }
  return { light, transmitted };
}

/**
 * Where the march reads the model's layers: tall enough that the thickest layer's sech²(y / 2h) is under
 * 10⁻⁶ of its midplane value at the box's top and bottom faces (D197 (3)), and the bulge has faded, and
 * never under 2 kpc. At ten scale heights (S39 to S46) the faces cut the diffuse gas's layer at
 * sech²(5) ≈ 1.8 × 10⁻⁴ of its midplane density, which a grazing ray carries across the whole box and a
 * raised exposure shows as a straight edge. Fourteen leave sech²(7) ≈ 3.3 × 10⁻⁶, still over the ruled
 * 10⁻⁶; sixteen leave sech²(8) ≈ 4.5 × 10⁻⁷. A dust layer given per ring (D206) does not size the box: its
 * height passes the stars' only in the outer disc, where the dust's depth is a hundredth or less, and the
 * formula it comes from diverges beyond the stellar disc, where there is no dust to cut.
 */
export function marchHalfHeight(layers: Layers, bulgeScale: number): number {
  const dust = typeof layers.dust === "number" ? layers.dust : 0;
  const heights = [layers.stars, dust, layers.halpha_hii, layers.halpha_dig].map((h) => Number(h ?? 0)).filter(Number.isFinite);
  return Math.max(MARCH_SCALE_HEIGHTS * Math.max(0, ...heights), 12 * bulgeScale, 2);
}

/** The box's half-height in the thickest layer's scale heights: sech²(16 / 2) ≈ 4.5 × 10⁻⁷ at the faces. */
export const MARCH_SCALE_HEIGHTS = 16;

/**
 * How visible each regime is at a view `across` kpc wide. The field is the whole galaxy and
 * never goes fully away (most stars stay unresolved at any zoom); the sample fades in as the
 * galaxy fills the view and out again when a region's own stars take over.
 */
export function regimeWeights(
  across: number,
  floor: number = CLOSE_FIELD_FLOOR,
): { field: number; sampled: number; stars: number; active: "field" | "sampled" | "stars" } {
  const ramp = (x: number, from: number, to: number) => Math.min(1, Math.max(0, (Math.log(from) - Math.log(x)) / (Math.log(from) - Math.log(to))));
  const stars = ramp(across, REGIME_KPC.stars, REGIME_KPC.stars / 2);
  const sampled = ramp(across, REGIME_KPC.field * 2, REGIME_KPC.field * 0.6) * (1 - stars);
  // Close up the region's own stars carry the light, so the field steps back to a faint glow of
  // what stays unresolved. Left at a third, the bulge's surface brightness — which does not fall
  // as the camera closes in — flooded a close view white and hid every star in it. The floor is the
  // Tuning panel's (D199): its offset from CLOSE_FIELD_FLOOR is added, so at the default it adds an
  // exact zero and the weight is the S40 formula to the bit.
  const field = 1 - 0.7 * ramp(across, REGIME_KPC.field, REGIME_KPC.stars) - 0.27 * stars + (floor - CLOSE_FIELD_FLOOR) * stars;
  const active = across >= REGIME_KPC.field ? "field" : across >= REGIME_KPC.stars ? "sampled" : "stars";
  return { field, sampled, stars, active };
}

/** The field's weight at the closest zoom, 1 − 0.7 − 0.27: a display choice (D199's field floor). */
export const CLOSE_FIELD_FLOOR = 0.03;

/** The view widths, kpc, where the regimes hand over: the field above the first, a region's stars below the second. */
export const REGIME_KPC = { field: 25, stars: 4 };

export interface RegionWindow {
  r_min: number;
  r_max: number;
  phi_min: number;
  phi_max: number;
}

/**
 * The region a close view asks the catalogue for: a box `half` kpc around the orbit target,
 * as radius and azimuth bounds, snapped so small camera moves reuse a response. A window
 * that holds the centre or crosses φ = 0 asks for every azimuth.
 */
export function regionAround(x: number, z: number, half: number): RegionWindow {
  const snap = (v: number, step: number) => Math.round(v / step) * step;
  const h = 2 ** Math.ceil(Math.log2(Math.max(0.5, half)));
  const r0 = snap(Math.hypot(x, z), h / 2);
  const r_min = Math.max(0, r0 - h);
  const r_max = r0 + h;
  if (r0 <= h) return { r_min: 0, r_max, phi_min: 0, phi_max: 2 * Math.PI };
  let phi0 = Math.atan2(-z, x);
  if (phi0 < 0) phi0 += 2 * Math.PI;
  const dPhi = Math.min(Math.PI, Math.asin(Math.min(1, h / r0)) * 1.2);
  const step = Math.PI / 64;
  const phi_min = snap(phi0 - dPhi, step);
  const phi_max = snap(phi0 + dPhi, step);
  if (phi_min < 0 || phi_max > 2 * Math.PI) return { r_min, r_max, phi_min: 0, phi_max: 2 * Math.PI };
  return { r_min, r_max, phi_min, phi_max };
}

/** How many of the sample's stars fall inside a window: its share of the galaxy's stars, measured rather than guessed. */
export function starsInWindow(radius: ArrayLike<number>, azimuth: ArrayLike<number>, window: RegionWindow): number {
  let n = 0;
  for (let i = 0; i < radius.length; i += 1) {
    const r = radius[i];
    const a = azimuth[i];
    if (r >= window.r_min && r <= window.r_max && a >= window.phi_min && a <= window.phi_max) n += 1;
  }
  return n;
}

/**
 * The whole-galaxy sample size a region is materialised at, so that about `target` stars land
 * in it: the base sample scaled by the share of its stars the window already holds (the centre
 * is dense and the outskirts are not, so the share is counted, not taken from the area). A
 * power of two times the base, so it changes in steps and a nudge reuses a response.
 */
export function regionSampleSize(base: number, inWindow: number, target: number, max: number): number {
  const share = Math.max(inWindow, 1) / base;
  const scale = 2 ** Math.floor(Math.log2(Math.max(1, target / (share * base))));
  return Math.min(max, base * scale);
}
