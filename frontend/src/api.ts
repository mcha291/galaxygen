// The app's view of the API. No network code lives here: every request goes
// through interface/transport.js, the project's one fetch (rule D2), and every
// colour comes from the field declarations it returns (rule A9).
import * as wire from "@interface/transport.js";

import { type BrightTable, type CountsAnswer, type TileAnswer, placeRemainder } from "./galaxy/brightTiles";
import type { Curve } from "./galaxy/filters";
import { checkLayer, reportLayerFault } from "./galaxy/layer";
import type { Axis } from "./preview/axes";
import type { Checkpoint, InputDecl } from "./workflow/logic";
import { type Templates, readTemplates } from "./workflow/templates";

/** How many stars the galaxy view asks for: the materialised sample (D61). */
export const STAR_SAMPLE = 20_000;

export type Columns = Record<string, ArrayLike<number | bigint>>;
export type Query = Record<string, unknown>;

// The JSON routes: declarations and tables that take no input vector, so the layer's switch is not theirs.
const { blackbody, fields, get, inputs, stages } = wire;

type Options = { signal?: AbortSignal };
type Answer = { header: unknown; arrays: unknown };

/**
 * A binary route, held to the request that asked it (S55, D214: invariant I5's viewer half). Every route that
 * takes inputs takes `layer` and echoes it in its header; the frame that comes back must say the setting that was
 * asked for (galaxy/layer.ts `checkLayer`), or it is refused here - reported to the page and thrown, so it is not
 * drawn. **Every loader below calls the transport through one of these and through nothing else**: the raw routes
 * are not in this file's scope by name, so a loader added later cannot skip the check (rule B13).
 */
function route<First, Got extends Answer>(path: string, call: (first: First, params: Query, options?: Options) => Promise<Got>) {
  return async (first: First, params: Query, options?: Options): Promise<Got> => {
    const got = await call(first, params, options);
    try {
      checkLayer(path, params, got.header);
    } catch (error) {
      reportLayerFault((error as Error).message);
      throw error;
    }
    return got;
  };
}

const arrays = route("/api/arrays", wire.arrays);
const region = route("/api/region", wire.region);
const render = route("/api/render", wire.render);
const clouds = route("/api/clouds", wire.clouds);
const clusters = route("/api/clusters", wire.clusters);
const remnants = route("/api/remnants", wire.remnants);
const bright = route("/api/bright", wire.bright);

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

/**
 * The templates (S54, D213): `/api/templates`, metadata that runs no stage (rule D4), through the transport's
 * own `get`. **Null where the API has no such route** (a 404: an API from before S54) - the viewer then lands
 * on the default galaxy as it did before the templates, with no switcher (workflow/templates.ts readTemplates).
 */
export async function loadTemplates(signal?: AbortSignal): Promise<Templates | null> {
  return readTemplates(() => get("/api/templates", {}, { signal }));
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
 * The star-first mode's stars by tiles (S64, V6, R8): every disc star above `lMin` in each of `cells` (level-0 cell
 * ids), `lMin` one of the table's grid thresholds, each with its own light through the filter set. Keyed by cell and
 * threshold, never by the view (D222 ruling 14): the same answer every time. 32-bit: the light goes to a texture.
 */
export async function loadBrightTiles(
  cells: number[],
  lMin: number,
  curves: Curve[],
  white: number,
  query: Query,
  signal?: AbortSignal,
  level = 0,
): Promise<TileAnswer> {
  // S65 (V6b): the tiles named at `level`; level 0 asks as S64 did, without the parameter.
  const params = { ...query, cells: cells.join(","), ...(level ? { level } : {}), l_min: lMin, filters: JSON.stringify(curves), white, precision: "f4" };
  const got = await bright({}, params, { signal });
  const columns = got.arrays as TileAnswer["columns"];
  const bytes = Object.values(columns).reduce((s, a) => s + a.byteLength, 0);
  return { columns, header: got.header as TileAnswer["header"], bytes };
}

/**
 * The expected-count table (S64, V6, R8): each level-0 cell's expected count above every grid threshold, the cells'
 * layout and the rule the viewer picks one threshold per frame by. Once per galaxy; the counts float32, the
 * thresholds float64 (each the value a tile is asked at).
 */
export async function loadBrightTable(query: Query, signal?: AbortSignal): Promise<BrightTable> {
  const got = await bright({}, { ...query, table: 1, precision: "f4" }, { signal });
  const header = got.header as { table?: { rule: string }; cells: BrightTable["layout"] };
  const a = got.arrays as Record<string, ArrayLike<number>>;
  return { thresholds: a.threshold, expected: a.expected, layout: header.cells, rule: header.table?.rule ?? "" };
}

/**
 * The expected-count rows of the level-k cells asked (S65, V6b, R1: `table=1&cells=&level=`): each the API's sum over
 * the cell's finest cells, the thresholds float64, the counts float32. Never the whole level-k table.
 */
export async function loadBrightCounts(cells: number[], level: number, query: Query, signal?: AbortSignal): Promise<CountsAnswer> {
  const got = await bright({}, { ...query, table: 1, cells: cells.join(","), level, precision: "f4" }, { signal });
  const header = got.header as { table?: { cells: number[] } };
  const a = got.arrays as Record<string, ArrayLike<number>>;
  return { thresholds: a.threshold, expected: a.expected, cells: header.table?.cells ?? [] };
}

/** A census of one window (S40, V3): the columns as arrays and the header the route wrote. */
export interface Census {
  columns: Columns;
  header: { level: number; cells: { ids: number[]; counts: number[] }; columns: string[]; white?: WhitePoint; [key: string]: unknown };
}

export type RegionWindowQuery = { r_min: number; r_max: number; phi_min: number; phi_max: number; level?: number };

/**
 * The clouds of a window, at a level (the census the region regime synthesises interiors from). `precision` "f4" asks
 * for float32 (S64): the whole disc's census the clouds' opacity raster is built from, about 1.6 MB against 2.8.
 */
export async function loadClouds(window: RegionWindowQuery, query: Query, signal?: AbortSignal, precision?: "f4" | "f8"): Promise<Census> {
  const got = await clouds(window, precision ? { ...query, precision } : query, { signal });
  return { columns: got.arrays as Columns, header: got.header as Census["header"] };
}

/**
 * The clusters of a window with their HII regions' and bubbles' columns; with `light` (a filter set's curves and a
 * white point, S48) each cluster's `response` too, its own band light through each curve, and since S64 (V6, R5) its HII
 * region's `line_response`, the region's lines through each curve (the knots' light); the header's `knots` entry, with
 * or without `light`, names the knots' columns, the level-0 cells and the rule (galaxy/knots.ts knotsOf).
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

/**
 * The render header's `gas_fluctuation` (S66, V7, D226 R6): the gas fluctuation field, every number the model's
 * (galaxy.layer.gas_fluctuation). With the layer off every value but the form's numbers and the rule is null.
 */
export interface GasFluctuationEntry {
  seed: number | null;
  scale: number;
  slope: number;
  change: number;
  octaves: number;
  lacunarity: number;
  /** The disc's rotation in φ (-1: towards decreasing φ). */
  sense: number | null;
  /** The 33 level-0 ring edges, kpc. */
  edges: number[] | null;
  /** Per level-0 ring (32): the break index, the log-normal width, the strain, the twist at the inner edge (rad), the sum's normaliser. */
  ring: { break_octave: number[]; sigma: number[]; strain: number[]; twist: number[]; norm: number[] } | null;
  /** (octaves + 1) × octaves: the ladder's amplitude times its normaliser for each break index. */
  weights: number[][] | null;
  /** Per level-0 cell (1024, ring-major): the map's normaliser. */
  cell_normaliser: number[] | null;
  rule: string;
}

/** The render header's `census_clustering` (S66, V7, D226 R5c, R6): the clustering field and its k-octave cell means. */
export interface ClusteringEntry {
  seed: number | null;
  scale: number;
  octaves: number;
  lacunarity: number;
  slope: number;
  sigma: number;
  gain: number;
  top: number;
  norm: number;
  table_points: number;
  /** Myr, coarsest octave first: the age past which a star drops each octave. */
  octave_ages_myr: number[];
  /** Per kept octave count ("3", "2", "1"): the k-octave map's mean in each level-0 cell (1024, ring-major). */
  cell_mean: Record<string, number[]> | null;
  rule: string;
}

/** The render header's `spurs` (S66, V7, D226 R4): the gas spurs' table, their ring mean per render ring, the rule. */
export interface SpursEntry {
  rows: {
    chain: number[];
    radius: number[];
    azimuth: number[];
    contrast: number[];
    pitch: number[];
    length: number[];
    width: number[];
    fall: number[];
  } | null;
  /** The sense ψ is taken in from a spur's foot: +1 where an arm's azimuth grows outward. */
  turn: number | null;
  /** ⟨S⟩ round each render ring (the grid's R rows). */
  share: number[] | null;
  reach: number;
  fwhm_per_sigma: number;
  constants: Record<string, number>;
  rule: string;
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
    /**
     * The dust round each ring (D207): the name of the (R, φ) array among `arrays` that places it; null when even.
     * Since S66 (V7, D226 R4), with the layer on, `dust_unspurred` names the placement without the gas spurs.
     */
    placement?: { dust?: string; dust_unspurred?: string } | null;
    /** The gas fluctuation field the march reads once per ray at the midplane (S66, V7, D226 R3 as amended, R6); its values null with the layer off. */
    gas_fluctuation?: GasFluctuationEntry | null;
    /** The clustering field's form and its k-octave cell means (S66, V7, D226 R5c, R6); null values with the layer off. */
    census_clustering?: ClusteringEntry | null;
    /** The gas spurs' table and ring mean (S66, V7, D226 R4); null values with the layer off. */
    spurs?: SpursEntry | null;
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

/** The window and level parameters: a render asked with any of them is a region's, not the whole grid's. */
const REGION_PARAMS = ["r_min", "r_max", "phi_min", "phi_max", "level"];
/**
 * The whole renders held (S64, V6; T28): the field mode's and the star-first mode's frames share the one whole render
 * of a (filter set, white point, query), so a new threshold asks the remainder alone. Two: the galaxy and the one
 * before it. Fetched without a caller's signal - two loaders may wait on it - and each caller stops waiting on its own.
 */
const WHOLE_RENDERS_HELD = 2;
const wholeRenders = new Map<string, Promise<RenderFrame>>();

/** Drop the held whole renders (tests: each stands its own API up). */
export function forgetRenders(): void {
  wholeRenders.clear();
}

function untilAborted<T>(promise: Promise<T>, signal?: AbortSignal): Promise<T> {
  if (!signal) return promise;
  if (signal.aborted) return Promise.reject(new DOMException("aborted", "AbortError"));
  return new Promise<T>((resolve, reject) => {
    const stop = () => reject(new DOMException("aborted", "AbortError"));
    signal.addEventListener("abort", stop, { once: true });
    promise.then(
      (v) => {
        signal.removeEventListener("abort", stop);
        resolve(v);
      },
      (e) => {
        signal.removeEventListener("abort", stop);
        reject(e);
      },
    );
  });
}

function wholeRender(curves: Curve[], white: number, query: Query): Promise<RenderFrame> {
  const key = JSON.stringify([curves, white, query]);
  let held = wholeRenders.get(key);
  if (held) {
    wholeRenders.delete(key);
  } else {
    held = render(curves, { ...query, white, precision: "f4" }).then((got) => ({
      header: got.header as RenderFrame["header"],
      arrays: got.arrays as RenderFrame["arrays"],
    }));
    held.catch(() => wholeRenders.delete(key));
  }
  wholeRenders.set(key, held);
  while (wholeRenders.size > WHOLE_RENDERS_HELD) wholeRenders.delete(wholeRenders.keys().next().value as string);
  return held;
}

/** `/api/render?only=remainder` (S64, V6, R8): the field's light under `lMin` as two per-ring arrays and their rule. */
export interface RemainderFrame {
  header: {
    window: { R: { n: number } };
    remainder: { rule: string; parts: Record<"middle" | "old", { array: string; weight: string }> };
    resolved: unknown;
    [key: string]: unknown;
  };
  arrays: Record<string, Float32Array | Float64Array>;
}

export async function loadRemainder(curves: Curve[], white: number, query: Query, lMin: number, signal?: AbortSignal): Promise<RemainderFrame> {
  const got = await render(curves, { ...query, white, precision: "f4", l_min: lMin, only: "remainder" }, { signal });
  return { header: got.header as RemainderFrame["header"], arrays: got.arrays as RemainderFrame["arrays"] };
}

/**
 * The whole galaxy through a filter set, at 32 bits (a texture holds no more). The filter integral
 * is the model's: the viewer sends its curves and a white point and only tone-maps what comes back.
 *
 * With `lMin` (D208) the frame adds `stars_unresolved`, the stars' light no point carries above that luminosity: since
 * S64 (T28) the held whole render plus `only=remainder`'s two per-ring arrays, placed by the render's own weights as
 * the remainder's header states (brightTiles.ts placeRemainder) - a new threshold asks about 10 kB, never the render.
 */
export async function loadRender(curves: Curve[], white: number, query: Query = {}, signal?: AbortSignal, lMin?: number | null): Promise<RenderFrame> {
  const whole = !REGION_PARAMS.some((p) => p in query);
  if (!whole) {
    const got = await render(curves, { ...query, white, precision: "f4" }, { signal });
    return { header: got.header as RenderFrame["header"], arrays: got.arrays as RenderFrame["arrays"] };
  }
  if (lMin == null || !(lMin > 0)) return untilAborted(wholeRender(curves, white, query), signal);
  const [frame, rest] = await Promise.all([untilAborted(wholeRender(curves, white, query), signal), loadRemainder(curves, white, query, lMin, signal)]);
  const parts = rest.header.remainder?.parts;
  const a = frame.arrays;
  const placed = parts
    ? placeRemainder(rest.arrays[parts.middle.array], rest.arrays[parts.old.array], a[parts.middle.weight], a[parts.old.weight], rest.header.window?.R?.n)
    : null;
  return {
    header: { ...frame.header, resolved: rest.header.resolved, remainder: rest.header.remainder },
    arrays: placed ? { ...a, stars_unresolved: placed } : a,
  };
}
