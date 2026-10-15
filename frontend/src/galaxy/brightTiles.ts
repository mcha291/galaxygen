// The star-first view's bright stars by tiles (S64, V6, RULING_S64 R8; T28). The view's frustum footprint is resolved
// to level-0 cells - tiles - as the catalogues cut them; ONE threshold per frame is picked from the API's table of
// expected counts per tile (a sum and a comparison, rule D5); each tile is asked at that threshold and held by
// (tile, threshold); the frame's points are the held tiles' rows. Every answer is keyed by cell and threshold, never by
// a window this viewer chose (D222 ruling 14): the rasterisation by window is the viewer's own. The field's remainder
// under the same threshold is two per-ring arrays placed by the render's own weights (api.ts loadRender).

import type { RegionWindow } from "./regimes";

/** The level-0 cells as the API publishes them (`/api/bright?table=1`'s header `cells`: systems.cell_edges). */
export interface CellLayout {
  rings: number;
  sectors: number;
  ring_edges: number[];
  sector_edges: number[];
}

/** `/api/bright?table=1`: per level-0 cell (row-major, `cells` rows) the expected count above each grid threshold. */
export interface BrightTable {
  /** Lsun, float64: the grid's thresholds, each the value a tile is asked at and answered at. */
  thresholds: ArrayLike<number>;
  /** cells x thresholds, row-major. */
  expected: ArrayLike<number>;
  layout: CellLayout;
  /** The rule the header states; this file applies it (`pickThreshold`). */
  rule: string;
}

/**
 * The tiles held between frames, rows: about 100 bytes a star at three filters, so some 40 MB. A memory bound, not a
 * display choice; past it the least recently used tiles go and are asked again when seen.
 */
export const TILE_CACHE_ROWS = 400_000;

const TWO_PI = 2 * Math.PI;

/**
 * Every level-0 cell whose footprint meets `window` - the API's `systems.cells_in` at level 0, the same overlap test
 * (open on both sides, so a window that is exactly a block of cells names no neighbour), φ wrapping past 2π.
 */
export function tilesIn(window: RegionWindow, layout: CellLayout): number[] {
  const { ring_edges: rings, sector_edges: sectors } = layout;
  const meets = (lo: number, hi: number, a: number, b: number) =>
    (lo < b && a < hi) || (a === b && lo <= a && a <= hi) || (lo === hi && a <= lo && lo <= b);
  const [rLo, rHi] = window.r_min <= window.r_max ? [window.r_min, window.r_max] : [window.r_max, window.r_min];
  const span = Math.min(Math.max(window.phi_max - window.phi_min, 0), TWO_PI);
  // As Python's % (non-negative), without a round trip through + 2π that would move an edge by a rounding.
  let start = window.phi_min % TWO_PI;
  if (start < 0) start += TWO_PI;
  const arcs: [number, number][] = start + span > TWO_PI ? [[start, TWO_PI], [0, start + span - TWO_PI]] : [[start, start + span]];
  const out: number[] = [];
  for (let i = 0; i < layout.rings; i += 1) {
    if (!meets(rings[i], rings[i + 1], rLo, rHi)) continue;
    for (let j = 0; j < layout.sectors; j += 1) {
      if (arcs.some(([a, b]) => meets(sectors[j], sectors[j + 1], a, b))) out.push(i * layout.sectors + j);
    }
  }
  return out;
}

/** The table's expected count over `tiles` above threshold `k`: a sum. */
export function expectedIn(table: BrightTable, tiles: readonly number[], k: number): number {
  const n = table.thresholds.length;
  let sum = 0;
  for (const c of tiles) sum += Number(table.expected[c * n + k]);
  return sum;
}

/**
 * The frame's one threshold (its index in the table): the table's rule - the smallest grid threshold at which the sum
 * over the tiles in view is at most the point budget. The counts fall along the grid, so the first that fits is it;
 * the last threshold if none does (no tile holds a star that bright).
 */
export function pickThreshold(table: BrightTable, tiles: readonly number[], budget: number): number {
  const n = table.thresholds.length;
  for (let k = 0; k < n; k += 1) if (expectedIn(table, tiles, k) <= budget) return k;
  return n - 1;
}

export type ColumnArray = Float32Array | Float64Array | BigInt64Array | Int32Array | Uint32Array;
export type TileColumns = Record<string, ColumnArray>;
/** One tile's rows at one threshold. */
export interface TileRows {
  rows: number;
  columns: TileColumns;
}

/**
 * A multi-tile answer split into its tiles: the rows come grouped by finest cell ascending, so each tile's rows are one
 * run; a row's tile is its finest `cell` over `perTile` (the header's cells.count over its tile.cells, 64). Every
 * asked tile gets an entry, an empty one where it holds no star, so it is held and not asked again. A column of
 * several values a row (`response`, rows x filters) is split by its own stride.
 */
export function splitByTile(columns: TileColumns, asked: readonly number[], perTile: number): Map<number, TileRows> {
  const cell = columns.cell;
  const total = cell ? cell.length : 0;
  const out = new Map<number, TileRows>();
  let start = 0;
  for (const tile of [...asked].sort((a, b) => a - b)) {
    let end = start;
    while (end < total && Math.floor(Number(cell[end]) / perTile) === tile) end += 1;
    const part: TileColumns = {};
    for (const [name, col] of Object.entries(columns)) {
      const stride = total ? col.length / total : 1;
      part[name] = col.subarray(start * stride, end * stride) as ColumnArray;
    }
    out.set(tile, { rows: end - start, columns: part });
    start = end;
  }
  if (start !== total) throw new Error(`a tile answer held ${total - start} rows outside the tiles it was asked for`);
  return out;
}

/** The held tiles' rows, one after another: each tile once, so no star twice (a tile is one level-0 cell). */
export function unionOf(parts: readonly TileRows[]): { rows: number; columns: TileColumns } {
  const rows = parts.reduce((s, p) => s + p.rows, 0);
  const names = parts.length ? Object.keys(parts[0].columns) : [];
  const columns: TileColumns = {};
  for (const name of names) {
    const first = parts[0].columns[name];
    const length = parts.reduce((s, p) => s + p.columns[name].length, 0);
    const out = new (first.constructor as new (n: number) => ColumnArray)(length);
    let at = 0;
    for (const p of parts) {
      (out as Float64Array).set(p.columns[name] as Float64Array, at);
      at += p.columns[name].length;
    }
    columns[name] = out;
  }
  return { rows, columns };
}

/** The tiles held, by (galaxy, tile, threshold): least recently used out first past `maxRows`. */
export class TileCache {
  private held = new Map<string, TileRows>();
  private rows = 0;
  constructor(private maxRows = TILE_CACHE_ROWS) {}

  static key(galaxy: string, tile: number, k: number): string {
    return `${galaxy}|${tile}|${k}`;
  }

  get(galaxy: string, tile: number, k: number): TileRows | undefined {
    const key = TileCache.key(galaxy, tile, k);
    const found = this.held.get(key);
    if (found) {
      this.held.delete(key);
      this.held.set(key, found);
    }
    return found;
  }

  set(galaxy: string, tile: number, k: number, rows: TileRows): void {
    const key = TileCache.key(galaxy, tile, k);
    const old = this.held.get(key);
    if (old) this.rows -= Math.max(old.rows, 1);
    this.held.delete(key);
    this.held.set(key, rows);
    this.rows += Math.max(rows.rows, 1);
    while (this.rows > this.maxRows && this.held.size > 1) {
      const [first, dropped] = this.held.entries().next().value as [string, TileRows];
      this.held.delete(first);
      this.rows -= Math.max(dropped.rows, 1);
    }
  }

  get size(): number {
    return this.held.size;
  }
}

/** What a tile request returns (api.ts loadBrightTiles): its rows and the header's tile and white point. */
export interface TileAnswer {
  columns: TileColumns;
  header: { tile: { cells: number[]; l_min_used: number }; cells: { count: number }; white?: unknown };
  bytes: number;
}

/** The frame's bright stars: the held tiles' rows in view, at the frame's one threshold. */
export interface TilesFrame {
  columns: TileColumns;
  header: {
    /** The luminosity the points are complete above in every tile in view: the grid threshold asked. */
    threshold: { l_min: number; index: number };
    count: { returned: number; expected: number };
    white?: unknown;
    tiles: { inView: number; fetched: number; bytes: number };
  };
}

/**
 * The frame's stars: the tiles in view at threshold `k`, those not held asked in one request (the API refuses past
 * its cap, which the table's pick keeps under: the budget is at most 10⁵ and the cap 2 × 10⁵), held, and the union of
 * every tile in view returned. `galaxy` names what a tile's rows depend on besides (tile, threshold): the query, the
 * filter set and the white point.
 */
export async function tilesFrame(
  cache: TileCache,
  galaxy: string,
  tiles: readonly number[],
  k: number,
  table: BrightTable,
  ask: (cells: number[], lMin: number, signal?: AbortSignal) => Promise<TileAnswer>,
  whites: Map<string, unknown>,
  signal?: AbortSignal,
): Promise<TilesFrame> {
  const lMin = Number(table.thresholds[k]);
  const missing = tiles.filter((t) => !cache.get(galaxy, t, k));
  let bytes = 0;
  if (missing.length) {
    const got = await ask([...missing], lMin, signal);
    if (got.header.tile.l_min_used !== lMin) throw new Error(`tiles answered at ${got.header.tile.l_min_used} Lsun, asked at ${lMin}`);
    const perTile = got.header.cells.count / got.header.tile.cells.length;
    for (const [tile, rows] of splitByTile(got.columns, got.header.tile.cells, perTile)) cache.set(galaxy, tile, k, rows);
    whites.set(galaxy, got.header.white);
    bytes = got.bytes;
  }
  const parts = tiles.map((t) => cache.get(galaxy, t, k)).filter((p): p is TileRows => Boolean(p));
  const { rows, columns } = unionOf(parts);
  return {
    columns,
    header: {
      threshold: { l_min: lMin, index: k },
      count: { returned: rows, expected: expectedIn(table, tiles, k) },
      white: whites.get(galaxy),
      tiles: { inView: tiles.length, fetched: missing.length, bytes },
    },
  };
}

/**
 * The field's remainder under the frame's threshold, on the render's (R, φ, filter) grid, from `/api/render?only=
 * remainder` and the render's own weights - the rule its header states, a product and a sum (D5):
 * stars_unresolved(R, φ, f) = middle(R, f) · w_middle(R, φ) + old(R, f) · w_old(R, φ).
 * Null where any of the four arrays is missing or the shapes disagree: the frame then has no remainder (B9).
 */
export function placeRemainder(
  middle: ArrayLike<number> | undefined,
  old: ArrayLike<number> | undefined,
  wMiddle: ArrayLike<number> | undefined,
  wOld: ArrayLike<number> | undefined,
  nR: number,
): Float32Array | null {
  if (!middle || !old || !wMiddle || !wOld || !nR) return null;
  const nF = middle.length / nR;
  const nPhi = wMiddle.length / nR;
  if (!Number.isInteger(nF) || !Number.isInteger(nPhi) || old.length !== middle.length || wOld.length !== wMiddle.length) return null;
  const out = new Float32Array(nR * nPhi * nF);
  for (let r = 0; r < nR; r += 1) {
    for (let p = 0; p < nPhi; p += 1) {
      const a = Number(wMiddle[r * nPhi + p]);
      const b = Number(wOld[r * nPhi + p]);
      const at = (r * nPhi + p) * nF;
      for (let f = 0; f < nF; f += 1) out[at + f] = Number(middle[r * nF + f]) * a + Number(old[r * nF + f]) * b;
    }
  }
  return out;
}
