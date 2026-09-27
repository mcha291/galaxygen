import { paintOf } from "@interface/ramp.js";

import type { BlackbodyTable, Columns, FieldsPayload } from "../api";

/** One sRGB channel in 0..1 to linear light (IEC 61966-2-1). */
export function srgbToLinear(c: number): number {
  return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
}

/** The pseudo-field that selects photometric mode: radiance, not a column painted by a ramp. */
export const PHOTOMETRIC = "photometric";

/** Luminosity, in L☉, that renders at unit linear intensity at zero exposure stops. */
export const REFERENCE_LUMINOSITY = 100;

/**
 * A view of stars is exposed to the stars in it, as a photograph is (the design brief's "exposed
 * to the brightest thing in view"): drawn at one fixed exposure, a close view's stars were too
 * faint to see, every one of them far below the galaxy's giants. Not to its single brightest
 * star, though: a giant is in view at nearly every zoom (the brightest of a 3 000-star selection
 * fell only from 2 300 to 1 300 L☉ between the whole galaxy and 3 kpc across) while the stars
 * around it faded twentyfold. Nor to a share of those drawn: asking for more stars adds fainter
 * ones at the bottom, which moved that star and brightened every star already on screen. The
 * exposure is set by the EXPOSED_RANK-th brightest star in view, the same star however many are
 * drawn beyond it, which follows the population as the view closes in; the few above it burn out
 * as they do on film. That star is drawn as EXPOSED_LUMINOSITY at zero stops; 41 L☉ is the
 * hundredth brightest of the whole galaxy, so that view keeps the look it had. The slider's
 * stops ride on top.
 */
export const EXPOSED_RANK = 100;
export const EXPOSED_LUMINOSITY = 41;

/**
 * The stops that expose a set of stars: log₂(EXPOSED_LUMINOSITY / L) for its EXPOSED_RANK-th
 * brightest star with light, or its faintest when fewer are drawn. Zero when none has any.
 */
export function exposureFor(luminosity: ArrayLike<number | bigint>): number {
  const lit: number[] = [];
  for (let i = 0; i < luminosity.length; i += 1) {
    const L = Number(luminosity[i]);
    if (L > 0) lit.push(L);
  }
  if (lit.length === 0) return 0;
  const sorted = Float64Array.from(lit).sort().reverse();
  return Math.log2(EXPOSED_LUMINOSITY / sorted[Math.min(EXPOSED_RANK, sorted.length) - 1]);
}

/**
 * Per-star linear radiance for photometric mode (RENDER_PLAN M2 and R1): the
 * colour is the published blackbody colour of `star_temperature`, looked up
 * through that column's own declared ramp, and the intensity is the published
 * `star_luminosity` against REFERENCE_LUMINOSITY, doubled per exposure stop.
 *
 * Unbounded above on purpose. Stars are summed additively into a float target
 * and tone-mapped once on output, so a giant is thousands of times a dwarf and a
 * dense core saturates gracefully rather than clipping. A star with no light (a
 * dead one: NaN) is black, which adds nothing.
 */
export function photometricColors(meta: FieldsPayload, columns: Columns, stops: number, table: BlackbodyTable | null = null): Float32Array {
  return lightColors(meta, columns, stops, "star_temperature", "star_luminosity", table);
}

/**
 * A point's light per display channel per unit of its light, at a colour temperature (S42): the model's blackbody
 * share through each filter over the white point's, read off `/api/blackbody`'s table - log share linear in log T,
 * as the route says to read it - and clamped at its ends. A white-point star is (1, 1, 1); a hot one puts most of its light below the filters and
 * is dimmer through them than its bolometric light, as it is through a camera's. Null without a white point.
 */
export function channelShare(table: BlackbodyTable): ((kelvin: number) => [number, number, number]) | null {
  const white = table.white?.response;
  if (!white || white.length < 3 || !white.slice(0, 3).every((w) => w > 0)) return null;
  const logK = table.kelvin.map(Math.log10);
  const last = logK.length - 1;
  return (kelvin: number) => {
    const x = Math.min(logK[last], Math.max(logK[0], Math.log10(kelvin)));
    let i = Math.min(last - 1, Math.max(0, Math.floor(((x - logK[0]) / (logK[last] - logK[0])) * last)));
    while (i > 0 && logK[i] > x) i -= 1;
    while (i < last - 1 && logK[i + 1] < x) i += 1;
    const f = (x - logK[i]) / (logK[i + 1] - logK[i]);
    const at = (k: number) => {
      const a = table.share[i][k];
      const b = table.share[i + 1][k];
      // The Wien side is exponential in 1/T: its logarithm is the smooth thing to interpolate (a zero row stays linear).
      const s = a > 0 && b > 0 ? a * (b / a) ** f : a + (b - a) * f;
      return s / white[k];
    };
    return [at(0), at(1), at(2)];
  };
}

/**
 * photometricColors for any object that publishes a luminosity and a colour temperature with the blackbody
 * ramp: a star, or since S41 a cluster (`cluster_light_temperature`, `cluster_luminosity`) - the same mapping,
 * so a cluster is a point of the light its stars sum to, painted as a star of its temperature.
 */
export function lightColors(
  meta: FieldsPayload,
  columns: Columns,
  stops: number,
  temperatureName: string,
  luminosityName: string,
  table: BlackbodyTable | null = null,
): Float32Array {
  const decl = meta.fields.find((f) => f.name === temperatureName);
  const temperature = columns[temperatureName];
  const luminosity = columns[luminosityName];
  if (!decl || !temperature || !luminosity) throw new Error(`these objects carry no ${temperatureName} and ${luminosityName}`);
  const gain = 2 ** stops / REFERENCE_LUMINOSITY;
  const out = new Float32Array(temperature.length * 3);
  // Through the filter set when its table has come (S42, P6): the point's light in each channel, as the field's.
  const share = table ? channelShare(table) : null;
  if (share) {
    for (let i = 0; i < temperature.length; i += 1) {
      const L = Number(luminosity[i]);
      const T = Number(temperature[i]);
      if (!(L > 0) || !(T > 0)) continue;
      const s = share(T);
      for (let k = 0; k < 3; k += 1) out[3 * i + k] = s[k] * L * gain;
    }
    return out;
  }
  const paint = paintOf(decl, meta.cmaps, temperature);
  for (let i = 0; i < temperature.length; i += 1) {
    const L = Number(luminosity[i]);
    if (!(L > 0)) continue;
    const [r, g, b, a] = paint.color(temperature[i]);
    if (a === 0) continue;
    out[3 * i] = srgbToLinear(r / 255) * L * gain;
    out[3 * i + 1] = srgbToLinear(g / 255) * L * gain;
    out[3 * i + 2] = srgbToLinear(b / 255) * L * gain;
  }
  return out;
}

/**
 * Per-star RGB for a column, painted by the ramp or palette its field
 * declaration names. The mapping is ramp.js's, shared with the reference viewer;
 * nothing here knows a colour. Non-finite values come back black.
 *
 * The result is **linear** light: three.js treats vertex colours as linear and
 * encodes to sRGB on output, so the ramps' sRGB stops are converted here. Left
 * as sRGB they are encoded twice and every colour renders washed out.
 */
export function starColors(meta: FieldsPayload, columns: Columns, field: string): Float32Array {
  const decl = meta.fields.find((f) => f.name === field);
  const values = columns[field];
  if (!decl || !values) throw new Error(`no field ${field} in this sample`);
  const paint = paintOf(decl, meta.cmaps, values);
  const out = new Float32Array(values.length * 3);
  for (let i = 0; i < values.length; i += 1) {
    const [r, g, b] = paint.color(values[i]);
    out[3 * i] = srgbToLinear(r / 255);
    out[3 * i + 1] = srgbToLinear(g / 255);
    out[3 * i + 2] = srgbToLinear(b / 255);
  }
  return out;
}
