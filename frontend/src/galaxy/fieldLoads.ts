// The field's loads, named once (S80, #208 (a)): what the field volume asks (the arrays, the whole render, the layer's
// tables) and what the Galaxy tab asks for the clouds' layer (the whole disc's census), so that App can ask the same
// requests beside the star sample, before the tab has mounted - the landing's chain no longer waits on the sample's
// answer and the tab's mount to begin them (S78's profile, D242: ~0.3 s). Every key here is the one its loader builds
// from the same function, so the head start is the loader's own request asked earlier (api.ts askAhead), never another.

import { FIELD_SCALARS } from "@interface/ages.js";

import { type FieldsPayload, type Query, askArraysAhead, askCloudsAhead, askLayerAhead, askRenderAhead } from "../api";
import { type FilterSetName, curvesOf } from "./filters";
import type { Tuning } from "./tuning";

/** The framing radius of the view, kpc, where the grid names no radial extent (GalaxyTab's DISC_RADIUS). */
const DISC_RADIUS = 20;

/** The scalar arrays the field volume asks: the bulge's scale radius and the rest (FieldVolume's SCALARS), as declared. */
export function fieldArrayNames(meta: FieldsPayload): string[] {
  return FIELD_SCALARS.filter((n: string) => meta.fields.some((f) => f.name === n));
}

/** Whether the model declares the light the field is drawn from: without it the field volume asks nothing. */
export function fieldLit(meta: FieldsPayload): boolean {
  const declared = (name: string) => meta.fields.some((f) => f.name === name);
  return declared("disc_surface_brightness") && declared("disc_light_temperature");
}

/** The whole disc as a window: the census the clouds' layer is rasterised from (GalaxyTab), at level 0. */
export function wholeDiscOf(meta: FieldsPayload): { r_min: number; r_max: number; phi_min: number; phi_max: number; level: number } {
  const R = meta.grid.axes.R;
  return { r_min: R?.lo ?? 0, r_max: R?.hi ?? DISC_RADIUS * 1.5, phi_min: 0, phi_max: 2 * Math.PI, level: 0 };
}

/**
 * Ask, now, what the Galaxy tab will ask on its mount in the field mode: the field volume's arrays, its whole render
 * (no threshold: the field mode has none) through `filterSet` at the tuning's white point, the layer's tables, and -
 * where the tuning draws the clouds as extinction - the whole disc's census. `query` is the Galaxy view's (App's
 * galaxyQuery), `tuning` the one the tab will read for the template (tuning.ts loadTuning). Nothing is asked for a
 * model that declares no light, as the volume asks nothing then.
 */
export function askFieldAhead(meta: FieldsPayload, query: Query, filterSet: FilterSetName, tuning: Tuning): void {
  if (!fieldLit(meta)) return;
  askArraysAhead(fieldArrayNames(meta), query);
  askRenderAhead(curvesOf(filterSet), tuning.whiteKelvin, query);
  askLayerAhead(query);
  if (tuning.cloudsExtinction) askCloudsAhead(wholeDiscOf(meta), query, "f4");
}
