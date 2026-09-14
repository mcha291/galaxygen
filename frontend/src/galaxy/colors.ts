import { paintOf } from "@interface/ramp.js";

import type { Columns, FieldsPayload } from "../api";

/** One sRGB channel in 0..1 to linear light (IEC 61966-2-1). */
export function srgbToLinear(c: number): number {
  return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
}

/** The pseudo-field that selects photometric mode: radiance, not a column painted by a ramp. */
export const PHOTOMETRIC = "photometric";

/** Luminosity, in L☉, that renders at unit linear intensity at zero exposure stops. */
export const REFERENCE_LUMINOSITY = 100;

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
export function photometricColors(meta: FieldsPayload, columns: Columns, stops: number): Float32Array {
  const decl = meta.fields.find((f) => f.name === "star_temperature");
  const temperature = columns.star_temperature;
  const luminosity = columns.star_luminosity;
  if (!decl || !temperature || !luminosity) throw new Error("this sample carries no photometry");
  const paint = paintOf(decl, meta.cmaps, temperature);
  const gain = 2 ** stops / REFERENCE_LUMINOSITY;
  const out = new Float32Array(temperature.length * 3);
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
