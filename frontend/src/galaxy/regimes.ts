// The field regime (design brief §3, RENDER_PLAN R3/R4/M4): the galaxy's light as a
// volume the renderer integrates along each line of sight. No three.js here.
//
// Since S38 (BUILD_II V1) the light's colour is the filter integral's, run by the model: the
// viewer sends its filter set (filters.ts) to /api/render and gets back each emitting component's
// response in each filter, and divides each channel by its white point and nothing else (rule D5;
// RENDER_PHYSICS §2, "components, not colours").
//
// Since S39 (BUILD_II V2) every component is placed by the model and spread through a layer the
// model names (the render header's `layers`, each a sech²(z / 2h) / 4h profile): the stars and the
// dust's own light and scattered light in the thin disc, where the dust is mixed with them (the dust
// stage's heating geometry); the HII regions' Hα, placed round each ring by the pattern's contrast, in
// the clouds' layer; the diffuse gas's Hα in its own published 1.4 kpc layer, which a tilted view sees
// brighten toward the limb. The dust dims each filter by its own depth from the grain model's curve.
//
// **What the field regime still invents at galaxy scale: nothing structural.** The seeded Hα knots,
// the clump lattice, the dust's lead onto the arms' inner edge, the line's and the dust's crowding
// into the arms at a display power, and the per-channel extinction the viewer held (CHANNEL_EXTINCTION)
// are gone (RENDER_PHYSICS §0's exception, closed by V2). What remains the viewer's is display only:
// the white point, the exposure, the tone curve and the bloom, and the ray-march's own sampling (steps,
// the jitter that turns banding into grain, the pixel budget). Structure below a (R, φ) cell of the
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

/** The model's layers, kpc (/api/render's header `layers`); a missing one draws its component nowhere. */
export interface Layers {
  stars: number | null;
  dust: number | null;
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
   * The white point: each filter's response to a unit of white light (/api/render's `white`). Every
   * channel is divided by it, so white light draws (1, 1, 1) per unit of light in any filter set.
   */
  white: readonly number[];
}

export interface PlaneTexture {
  /** The stars, in the thin disc's layer: RGB each filter's response over its white point; A unused. */
  data: Float32Array;
  /** The scattered light, in the dust's layer, all directions together (the shader applies the phase); A unused. */
  scatter: Float32Array;
  /** The HII regions' Hα, in the clouds' layer, over the white point; A unused. */
  hii: Float32Array;
  /**
   * Per ring, three rows of one texel per R cell: row 0 the dust's face-on optical depth per channel,
   * row 1 the diffuse gas's Hα and row 2 the dust's thermal emission, each over the white point; A unused.
   */
  rings: Float32Array;
  width: number;
  height: number;
}

/** The rows of `PlaneTexture.rings`, and where a shader samples each (texel centres). */
export const RING_ROWS = { depth: 0, dig: 1, thermal: 2, count: 3 } as const;

/**
 * RGBA float textures from the published components, one texel per (R cell, φ cell), row-major with φ as
 * the row, and one row per R cell for the per-ring ones. Every value is the model's, over the white point
 * where it is light, or −ln of its transmission where it is dust: nothing is placed, clumped or recoloured.
 */
export function planeTexture(fields: PlaneFields): PlaneTexture {
  const { R, phi, stars, hii, dig, extinction, scattered, thermal, white } = fields;
  const nPhi = phi.n;
  const nF = white.length;
  const data = new Float32Array(R.n * nPhi * 4);
  const scatter = new Float32Array(R.n * nPhi * 4);
  const line = new Float32Array(R.n * nPhi * 4);
  const rings = new Float32Array(R.n * RING_ROWS.count * 4);
  for (let i = 0; i < R.n; i += 1) {
    for (let k = 0; k < 3 && k < nF; k += 1) {
      rings[(RING_ROWS.depth * R.n + i) * 4 + k] = extinction ? depthOf(Number(extinction[i * nF + k])) : 0;
      rings[(RING_ROWS.dig * R.n + i) * 4 + k] = dig ? balanced(Number(dig[i * nF + k]), white[k]) : 0;
      rings[(RING_ROWS.thermal * R.n + i) * 4 + k] = thermal ? balanced(Number(thermal[i * nF + k]), white[k]) : 0;
    }
    for (let j = 0; j < nPhi; j += 1) {
      const q = (j * R.n + i) * 4;
      const at = (i * nPhi + j) * nF;
      for (let k = 0; k < 3 && k < nF; k += 1) {
        data[q + k] = balanced(Number(stars[at + k]), white[k]);
        scatter[q + k] = scattered ? balanced(Number(scattered[at + k]), white[k]) : 0;
        line[q + k] = hii ? balanced(Number(hii[at + k]), white[k]) : 0;
      }
    }
  }
  return { data, scatter, hii: line, rings, width: R.n, height: nPhi };
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
 * Where the march reads the model's layers: tall enough that the thickest layer's sech² has fallen under
 * 2 × 10⁻⁴ of its midplane value (ten scale heights) and the bulge has faded, and never under 2 kpc.
 */
export function marchHalfHeight(layers: Layers, bulgeScale: number): number {
  const heights = [layers.stars, layers.dust, layers.halpha_hii, layers.halpha_dig].map((h) => Number(h ?? 0)).filter(Number.isFinite);
  return Math.max(10 * Math.max(0, ...heights), 12 * bulgeScale, 2);
}

/**
 * How visible each regime is at a view `across` kpc wide. The field is the whole galaxy and
 * never goes fully away (most stars stay unresolved at any zoom); the sample fades in as the
 * galaxy fills the view and out again when a region's own stars take over.
 */
export function regimeWeights(across: number): { field: number; sampled: number; stars: number; active: "field" | "sampled" | "stars" } {
  const ramp = (x: number, from: number, to: number) => Math.min(1, Math.max(0, (Math.log(from) - Math.log(x)) / (Math.log(from) - Math.log(to))));
  const stars = ramp(across, REGIME_KPC.stars, REGIME_KPC.stars / 2);
  const sampled = ramp(across, REGIME_KPC.field * 2, REGIME_KPC.field * 0.6) * (1 - stars);
  // Close up the region's own stars carry the light, so the field steps back to a faint glow of
  // what stays unresolved. Left at a third, the bulge's surface brightness — which does not fall
  // as the camera closes in — flooded a close view white and hid every star in it.
  const field = 1 - 0.7 * ramp(across, REGIME_KPC.field, REGIME_KPC.stars) - 0.27 * stars;
  const active = across >= REGIME_KPC.field ? "field" : across >= REGIME_KPC.stars ? "sampled" : "stars";
  return { field, sampled, stars, active };
}

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
