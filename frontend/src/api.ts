// The app's view of the API. No network code lives here: every request goes
// through interface/transport.js, the project's one fetch (rule D2), and every
// colour comes from the field declarations it returns (rule A9).
import { arrays, fields, inputs, region, stages, system } from "@interface/transport.js";

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

export interface SystemFrame {
  header: {
    star: Record<string, number>;
    cell: number;
    index: number;
    planets: number;
    belts: { kind: string; inner: number; outer: number }[];
    columns: string[];
    stars: { requested: number; seed: number; planets_seed: number };
    stages: string[];
  };
  arrays: Record<string, Float64Array | BigInt64Array>;
}

/**
 * One star's planets and belts, by the (cell, index) the region response named
 * it with. The server materialises that one cell, not the galaxy, and asks for
 * the same sample size so the same star is the same star.
 */
/**
 * A star's name: its cell, its index there, and the whole-galaxy sample size it was named in.
 * The index only means something at that size, so a star picked in a close region view
 * (a larger sample) opens with that size and not the base one.
 */
export interface StarName {
  cell: number;
  index: number;
  stars?: number;
}

export async function loadSystem(star: StarName, query: Query, signal?: AbortSignal): Promise<SystemFrame> {
  const { cell, index } = star;
  const got = await system({ cell, index }, { ...query, stars: star.stars ?? STAR_SAMPLE }, { signal });
  return { header: got.header as SystemFrame["header"], arrays: got.arrays as SystemFrame["arrays"] };
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

/**
 * The brightest-N mode: the `brightest` most luminous stars inside the camera's frustum, from the
 * window materialised at whole-galaxy sample size `stars`. Rows come brightest first, each named
 * by its own `cell` and `index` columns.
 */
export async function loadBrightest(
  window: { r_min: number; r_max: number; phi_min: number; phi_max: number },
  stars: number,
  brightest: number,
  view: ArrayLike<number>,
  query: Query,
  signal?: AbortSignal,
): Promise<Sample> {
  const got = await region(window, { ...query, stars, brightest, view: Array.from(view) }, { signal });
  return { columns: got.arrays as Columns, header: got.header as Sample["header"] };
}
