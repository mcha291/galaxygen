// The field regime (design brief §3, RENDER_PLAN R3/R4/M4): the galaxy's light as a
// volume the renderer integrates along each line of sight. No three.js here.
//
// Everything in the volume is published. In the plane: the disc's surface brightness,
// the colour of that light, its Hα, and the dust's face-on extinction, each times the
// (R, φ) pattern contrast. Out of the plane: the thin disc's sech² scale height for the
// light, and a thinner layer for the dust. In the middle: the Hernquist bulge. The
// viewer lays these out as one polar texture and a few numbers and marches rays
// through them, adding light and taking away what the dust in front absorbs.

import type { Axis } from "../preview/axes";

/**
 * Linear sRGB of an HII region's light: Hα 656.3 nm and Hβ 486.1 nm at the case-B ratio
 * 2.86 : 1, through the same CIE 1931 fit and XYZ-to-sRGB matrix as the blackbody cmap
 * (galaxy/core/cmaps.py), brightest channel at 1. Computed there once and copied here,
 * because a line colour is not a field and has no ramp.
 * [recall: Osterbrock & Ferland 2006, case B Hα/Hβ = 2.86 at 10⁴ K]
 */
export const HII_RGB = [1.0, 0.1607, 0.5032] as const;

/**
 * The line's weight against the starlight in the viewer's channels. Starlight is drawn at
 * its bolometric luminosity, of which a population puts roughly a fifth into the red
 * channel; the line puts all of its light there. A display correction of that mismatch,
 * not a measured ratio.
 */
export const LINE_CHANNEL_WEIGHT = 5;

/**
 * How much harder the line crowds into the arms than the starlight: the contrast raised to
 * this power, renormalised around each ring so the ring still carries its published Hα.
 * Star formation goes as gas density to the Kennicutt–Schmidt power and the arms are where
 * the gas is; the exponent is a display choice standing in for that, not a derivation.
 */
export const LINE_CLUMP = 3;

/** Optical depth per magnitude: τ = A / 1.086. */
export const TAU_PER_MAG = 1 / 1.086;

export interface PlaneFields {
  R: Axis;
  /** Surface brightness per R cell, L☉/pc². */
  brightness: ArrayLike<number>;
  /** Linear RGB of the light per R cell, three per cell; non-finite means no light is drawn there. */
  colour: ArrayLike<number>;
  /** Hα surface brightness per R cell, L☉/pc². */
  halpha?: ArrayLike<number>;
  /** Face-on A_V per R cell. */
  extinction?: ArrayLike<number>;
  /** The (R, φ) contrast, row-major over (R, φ), when the model publishes one. */
  contrast?: { values: ArrayLike<number>; phi: Axis };
}

/**
 * One RGBA float texel per (R cell, φ cell), row-major with φ as the row: RGB is the light
 * emitted through a face-on column (L☉/pc², linear colour), A is the dust's face-on optical
 * depth in V. Without a contrast the disc is axisymmetric and one φ row serves.
 */
export function planeTexture(fields: PlaneFields): { data: Float32Array; width: number; height: number } {
  const { R, brightness, colour, halpha, extinction, contrast } = fields;
  const nPhi = contrast ? contrast.phi.n : 1;
  const data = new Float32Array(R.n * nPhi * 4);
  const at = (i: number, j: number) => (contrast ? Math.max(0, Number(contrast.values[i * contrast.phi.n + j])) : 1);

  for (let i = 0; i < R.n; i += 1) {
    const light = Number(brightness[i]);
    const [r, g, b] = [Number(colour[3 * i]), Number(colour[3 * i + 1]), Number(colour[3 * i + 2])];
    const lit = light > 0 && Number.isFinite(r) && Number.isFinite(g) && Number.isFinite(b);
    const line = halpha ? Math.max(0, Number(halpha[i]) || 0) * LINE_CHANNEL_WEIGHT : 0;
    const av = extinction ? Math.max(0, Number(extinction[i]) || 0) : 0;

    // The line's clumping, renormalised so the ring's mean is its published value.
    let clumpMean = 0;
    for (let j = 0; j < nPhi; j += 1) clumpMean += at(i, j) ** LINE_CLUMP;
    clumpMean = clumpMean / nPhi || 1;

    for (let j = 0; j < nPhi; j += 1) {
      const c = at(i, j);
      const p = (j * R.n + i) * 4;
      const stars = lit ? light * c : 0;
      const knots = (line * c ** LINE_CLUMP) / clumpMean;
      data[p] = (lit ? r * stars : 0) + HII_RGB[0] * knots;
      data[p + 1] = (lit ? g * stars : 0) + HII_RGB[1] * knots;
      data[p + 2] = (lit ? b * stars : 0) + HII_RGB[2] * knots;
      data[p + 3] = av * c * TAU_PER_MAG;
    }
  }
  return { data, width: R.n, height: nPhi };
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
