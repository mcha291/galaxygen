import { paintOf } from "@interface/ramp.js";

import type { Columns, FieldsPayload } from "../api";

/** One sRGB channel in 0..1 to linear light (IEC 61966-2-1). */
export function srgbToLinear(c: number): number {
  return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
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
