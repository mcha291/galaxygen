// The app's view of the API. No network code lives here: every request goes
// through interface/transport.js, the project's one fetch (rule D2), and every
// colour comes from the field declarations it returns (rule A9).
import { arrays, blackbody, bright, clouds, clusters, fields, inputs, region, remnants, render, stages } from "@interface/transport.js";

import type { Curve } from "./galaxy/filters";
import type { Axis } from "./preview/axes";
import type { Checkpoint, InputDecl } from "./workflow/logic";

/** How many stars the galaxy view asks for: the materialised sample (D61). */
export const STAR_SAMPLE = 20_000;

export type Columns = Record<string, ArrayLike<number | bigint>>;
export type Query = Record<string, unknown>;

export interface FieldDecl {
  name: string;
  label: string;
  unit: string;
  ramp?: { kind: "ramp" | "palette" } & Record<string, unknown>;
  categories?: string[];
  [key: string]: unknown;
}

export interface FieldsPayload {
  model: string;
  grid: { axes: Record<string, Axis> };
  fields: FieldDecl[];
  cmaps: Record<string, unknown>;
}

export interface StagesPayload {
  model: string;
  models: string[];
  order: string[];
  checkpoints: Omit<Checkpoint, "inputs">[];
}

export interface InputsPayload {
  model: string;
  controls: InputDecl[];
  seeds: InputDecl[];
  events: InputDecl[];
}

export interface Sample {
  columns: Columns;
  header: {
    cells: { ids: number[]; counts: number[]; count: number; of: number };
    stars: { materialised: number; requested: number; seed: number };
    /** Set on a brightest-N response: the pool the rows were chosen from, and how many were in view. */
    brightest?: { requested: number; pool: number; in_view: number; returned: number } | null;
    [key: string]: unknown;
  };
}

export async function loadFields(model?: string, signal?: AbortSignal): Promise<FieldsPayload> {
  return (await fields({ model, signal })) as FieldsPayload;
}

/** What the workflow walks: a model's checkpoints and the inputs that belong to them. */
export async function loadDeclarations(
  model?: string,
  signal?: AbortSignal,
): Promise<{ stages: StagesPayload; inputs: InputsPayload }> {
  const [s, i] = await Promise.all([stages({ model, signal }), inputs({ model, signal })]);
  return { stages: s as StagesPayload, inputs: i as InputsPayload };
}

/** A lighter download of a history: fewer time steps and/or 32-bit floats. The model still runs at full resolution. */
export interface Sampling {
  tSamples?: number;
  precision?: "f4" | "f8";
}

/** What the history views ask for: 200 of the 2000 time steps at 32 bits, 400 KB a field instead of 6.4 MB. */
export const HISTORY_SAMPLING: Sampling = { tSamples: 200, precision: "f4" };

export interface Frame {
  header: {
    grid: { axes: Record<string, Axis> };
    scalars: Record<string, number>;
    stages: string[];
    [key: string]: unknown;
  };
  /** f8 fields as Float64Array, f4 as Float32Array; categorical (i8) ones as BigInt64Array. */
  arrays: Record<string, Float64Array | Float32Array | BigInt64Array>;
}

/**
 * Named fields for one input vector. The server runs only the stages those
 * fields need (the frame's `stages`), so a checkpoint-1 preview never pays for
 * the star catalogue.
 */
export async function loadArrays(names: string[], query: Query = {}, signal?: AbortSignal, sampling?: Sampling): Promise<Frame> {
  const params = sampling ? { ...query, t_samples: sampling.tSamples, precision: sampling.precision } : query;
  const got = await arrays(names, params, { signal });
  return { header: got.header as Frame["header"], arrays: got.arrays as Frame["arrays"] };
}

/** The whole-galaxy star sample for one input vector: every cell, STAR_SAMPLE stars in all. */
export async function loadSample(query: Query = {}, signal?: AbortSignal): Promise<Sample> {
  const got = await region({}, { ...query, stars: STAR_SAMPLE }, { signal });
  return { columns: got.arrays as Columns, header: got.header as Sample["header"] };
}

/**
 * The stars regime: one window's stars, materialised at a larger whole-galaxy sample size so a
 * close view is dense. The same stars the full sweep at that size would put there (D60).
 */
export async function loadRegion(
  window: { r_min: number; r_max: number; phi_min: number; phi_max: number },
  stars: number,
  query: Query,
  signal?: AbortSignal,
): Promise<Sample> {
  const got = await region(window, { ...query, stars }, { signal });
  return { columns: got.arrays as Columns, header: got.header as Sample["header"] };
}

/** The white point a response is drawn over (/api/render's, /api/bright's and /api/clusters' header `white`). */
export type WhitePoint = { kelvin: number; response: (number | null)[] } | null;

/**
 * The bright catalogue's stars for one view (S48, `/api/bright`): rows brightest first, each named by its level-3
 * `cell` and its `rank` there, with `response` (N × filters, L☉ through each curve) when filters were sent.
 */
export interface BrightFrame {
  columns: Columns;
  header: {
    columns: string[];
    /** What the body is complete above: the luminosity the field's remainder must be asked at (D208). */
    threshold: { l_min: number; complete: boolean; why: string; prefix: string };
    count: { returned: number; expected: number };
    light: { returned: number; expected: number };
    white?: WhitePoint;
    [key: string]: unknown;
  };
}

/**
 * The star-first mode's stars (D208): the `n` most luminous disc stars inside the camera's frustum, complete above
 * the header's threshold, each with its own light through the filter set. 32-bit: the light goes to a texture.
 */
export async function loadBright(
  window: { r_min: number; r_max: number; phi_min: number; phi_max: number },
  n: number,
  view: ArrayLike<number>,
  curves: Curve[],
  white: number,
  query: Query,
  signal?: AbortSignal,
): Promise<BrightFrame> {
  const params = { ...query, n, view: Array.from(view), filters: JSON.stringify(curves), white, precision: "f4" };
  const got = await bright(window, params, { signal });
  return { columns: got.arrays as Columns, header: got.header as BrightFrame["header"] };
}

/** A census of one window (S40, V3): the columns as arrays and the header the route wrote. */
export interface Census {
  columns: Columns;
  header: { level: number; cells: { ids: number[]; counts: number[] }; columns: string[]; white?: WhitePoint; [key: string]: unknown };
}

export type RegionWindowQuery = { r_min: number; r_max: number; phi_min: number; phi_max: number; level?: number };

/** The clouds of a window, at a level (the census the region regime synthesises interiors from). */
export async function loadClouds(window: RegionWindowQuery, query: Query, signal?: AbortSignal): Promise<Census> {
  const got = await clouds(window, query, { signal });
  return { columns: got.arrays as Columns, header: got.header as Census["header"] };
}

/**
 * The clusters of a window with their HII regions' and bubbles' columns; with `light` (a filter set's curves and a
 * white point, S48) each cluster's `response` too, its own band light through each curve.
 */
export async function loadClusters(
  window: RegionWindowQuery,
  query: Query,
  signal?: AbortSignal,
  light?: { curves: Curve[]; white: number },
): Promise<Census> {
  const params = light ? { ...query, filters: JSON.stringify(light.curves), white: light.white } : query;
  const got = await clusters(window, params, { signal });
  return { columns: got.arrays as Columns, header: got.header as Census["header"] };
}

/** The supernova remnants of a window. */
export async function loadRemnants(window: RegionWindowQuery, query: Query, signal?: AbortSignal): Promise<Census> {
  const got = await remnants(window, query, { signal });
  return { columns: got.arrays as Columns, header: got.header as Census["header"] };
}

/** One render (S38): each published component's response per cell in each filter of the set sent. */
export interface RenderFrame {
  header: {
    set: string | null;
    filters: Curve[];
    window: {
      R: { first: number; n: number; lo: number; width: number };
      phi: { first: number; n: number; lo: number; width: number; wraps: boolean };
    };
    /** The bulge's response per filter, L☉; null when the model publishes no bulge. */
    bulge: (number | null)[] | null;
    white: { kelvin: number; response: (number | null)[] } | null;
    absent: { lines: string[]; why: string };
    stages: string[];
    /**
     * Each component's vertical layer, kpc (S39): a sech²(z / 2h) / 4h profile at each scale height. The dust's is
     * one height or, since D206, the name of the per-ring array of heights among `arrays` (`dust_height`).
     */
    layers?: {
      stars: number | null;
      dust: number | string | null;
      halpha_hii?: number | null;
      halpha_dig?: number | null;
      lines_hii?: number | null;
      lines_dig?: number | null;
    };
    /** The dust round each ring (D207): the name of the (R, φ) array among `arrays` that places it; null when even. */
    placement?: { dust?: string } | null;
    /** What each component reads and is; the scattered light's phase table rides here (S39). */
    components?: { dust_scattered?: { phase?: { cos_view: number[]; factor: number[] } } } & Record<string, unknown>;
    [key: string]: unknown;
  };
  /**
   * Row-major: stars, halpha_hii, lines_hii, dust_scattered (R, φ, filter); halpha_dig, lines_dig, dust_extinction,
   * dust_thermal (R, filter) (S39; the lines_ components since S42); dust_height (R), kpc (D206); dust_placement
   * (R, φ) (D207).
   */
  arrays: Record<string, Float32Array | Float64Array>;
}

/** Each filter's share of a blackbody's light per temperature, and the white point's (S42, `/api/blackbody`). */
export interface BlackbodyTable {
  kelvin: number[];
  /** Per temperature, per filter. */
  share: number[][];
  white: { kelvin: number; response: number[] } | null;
}

export async function loadBlackbody(curves: Curve[], white: number, signal?: AbortSignal): Promise<BlackbodyTable> {
  return (await blackbody(curves, { white }, { signal })) as BlackbodyTable;
}

/**
 * The whole galaxy through a filter set, at 32 bits (a texture holds no more). The filter integral
 * is the model's: the viewer sends its curves and a white point and only tone-maps what comes back.
 */
export async function loadRender(curves: Curve[], white: number, query: Query = {}, signal?: AbortSignal, lMin?: number | null): Promise<RenderFrame> {
  // With `lMin` (D208) the render adds `stars_unresolved`: the stars' light no point carries, above that luminosity.
  const params = lMin != null && lMin > 0 ? { ...query, white, precision: "f4", l_min: lMin } : { ...query, white, precision: "f4" };
  const got = await render(curves, params, { signal });
  return { header: got.header as RenderFrame["header"], arrays: got.arrays as RenderFrame["arrays"] };
}
