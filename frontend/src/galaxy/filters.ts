// The viewer's filter sets (RENDER_PHYSICS §2a: the viewer holds the filters; S38, BUILD_II V1).
// Data, in filters.json, sent to /api/render as curves: the model runs every filter integral and
// returns responses, and the viewer divides each channel by its white point and multiplies by the
// exposure. Nothing here evaluates a spectrum (rule D5).

import data from "./filters.json";

/** One filter's transmission, as the model's spectrum function takes it (stages/spectra.py). Å, air. */
export type Curve =
  | { name: string; shape: "gaussian"; centre: number; fwhm: number }
  | { name: string; shape: "box"; centre: number; width: number }
  | { name: string; shape: "sampled"; wavelength: number[]; transmission: number[] };

export interface FilterSet {
  label: string;
  about: string;
  /** Red, green, blue: the display channel each filter is drawn in. */
  curves: Curve[];
}

export type FilterSetName = "rgb" | "sho" | "hoo";

/** The sets the selector offers, in its order. */
export const FILTER_SETS = data.sets as Record<FilterSetName, FilterSet>;
export const FILTER_SET_NAMES = Object.keys(FILTER_SETS) as FilterSetName[];

/** The white point's colour temperature, K, sent with every render: a display choice (filters.json). */
export const WHITE_KELVIN: number = data.white.kelvin;

/** A set's curves as numbers, as the request sends them: no prose on the wire. */
export function curvesOf(name: FilterSetName): Curve[] {
  return FILTER_SETS[name].curves.map((c) => ({ ...c }));
}

/**
 * The white point per filter from a render's header, or null if the response carries none or one
 * of them is not a positive number (then nothing is drawn rather than a channel divided by zero).
 */
export function whiteOf(header: { white?: { response?: (number | null)[] } | null }): number[] | null {
  const response = header.white?.response;
  if (!response || response.length === 0) return null;
  const out = response.map((v) => Number(v));
  return out.every((v) => Number.isFinite(v) && v > 0) ? out : null;
}

/**
 * The bulge's drawn light per channel: its response in each filter over the white point, so the
 * bulge and the disc go through the same one step.
 */
export function bulgeLight(bulge: (number | null)[] | null | undefined, white: readonly number[]): [number, number, number] {
  const out: [number, number, number] = [0, 0, 0];
  if (!bulge) return out;
  for (let k = 0; k < 3 && k < white.length; k += 1) {
    const v = Number(bulge[k]) / white[k];
    out[k] = Number.isFinite(v) && v > 0 ? v : 0;
  }
  return out;
}
