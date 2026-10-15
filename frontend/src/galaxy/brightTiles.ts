// The star-first view's bright stars by tiles (S64, V6, RULING_S64 R8; T28). The view's frustum footprint is resolved
// to level-0 cells - tiles - as the catalogues cut them; ONE threshold per frame is picked from the API's table of
// expected counts per tile (a sum and a comparison, rule D5); each tile is asked at that threshold and held by
// (tile, threshold); the frame's points are the held tiles' rows. Every answer is keyed by cell and threshold, never by
// a window this viewer chose (D222 ruling 14): the rasterisation by window is the viewer's own. The field's remainder
// under the same threshold is two per-ring arrays placed by the render's own weights (api.ts loadRender).
//
// S65 (V6b, RULING_S65 R1): below the stars handover the tiles are level-k cells, k = levelFor(across) - the field
// mode's region rule (region.ts), shared - each level-0 cell cut into 2^k equal sub-rings by 2^k equal sub-sectors as
// systems.cell_bounds cuts it (the table's header `cells.children` states the rule; the level-0 edges are the whole
// table's layout). Their expected counts are the API's for the cells asked (`table=1&cells=&level=`), held per (galaxy,
// level, cell); the threshold is picked over the level-k cells in view by the same rule; the tiles are held by (galaxy,
// level, cell, threshold). A level-k tile's rows are its finest cells' rows in its level-0 tile: the catalogue is one.

import { SLAB_KPC } from "./frustum";
import { type RegionWindow, layerShare } from "./regimes";

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

/**
 * Every level-k cell whose footprint meets `window`: the API's `systems.cells_in` at `level` - the level-0 cells as
 * `tilesIn` finds them, then each one's 4^k children, child q = a 2^k + b the a-th sub-ring by the b-th sub-sector,
 * its edges `lo + (hi - lo) * a / 2^k` as `systems.cell_bounds` computes them, the same overlap test. Ascending ids
 * (c 4^k + q). At level 0, `tilesIn`.
 */
export function cellsIn(window: RegionWindow, layout: CellLayout, level: number): number[] {
  const tiles = tilesIn(window, layout);
  if (!level) return tiles;
  const n = 1 << level;
  const { ring_edges: rings, sector_edges: sectors } = layout;
  const meets = (lo: number, hi: number, a: number, b: number) =>
    (lo < b && a < hi) || (a === b && lo <= a && a <= hi) || (lo === hi && a <= lo && lo <= b);
  const [rLo, rHi] = window.r_min <= window.r_max ? [window.r_min, window.r_max] : [window.r_max, window.r_min];
  const span = Math.min(Math.max(window.phi_max - window.phi_min, 0), TWO_PI);
  let start = window.phi_min % TWO_PI;
  if (start < 0) start += TWO_PI;
  const arcs: [number, number][] = start + span > TWO_PI ? [[start, TWO_PI], [0, start + span - TWO_PI]] : [[start, start + span]];
  const out: number[] = [];
  for (const tile of tiles) {
    const i = Math.floor(tile / layout.sectors);
    const j = tile % layout.sectors;
    const [r0, r1, p0, p1] = [rings[i], rings[i + 1], sectors[j], sectors[j + 1]];
    for (let q = 0; q < n * n; q += 1) {
      const a = Math.floor(q / n);
      const b = q % n;
      const lo = r0 + ((r1 - r0) * a) / n;
      const hi = r0 + ((r1 - r0) * (a + 1)) / n;
      const plo = p0 + ((p1 - p0) * b) / n;
      const phi = p0 + ((p1 - p0) * (b + 1)) / n;
      if (meets(lo, hi, rLo, rHi) && arcs.some(([x, y]) => meets(plo, phi, x, y))) out.push(tile * n * n + q);
    }
  }
  return out;
}

/** The finest level (systems.MAX_LEVEL): a bright star's `cell` is always a level-3 id. */
export const FINEST_LEVEL = 3;

/** The level-k cell a finest (level-3) cell stands in: D190's naming, the API's v6_tiles.tile_of. At level 0, cell / 64. */
export function tileOf(cell: number, level: number): number {
  const per = 1 << FINEST_LEVEL;
  const parent = Math.floor(cell / (per * per));
  const q = cell - parent * per * per;
  const shift = FINEST_LEVEL - level;
  const a = Math.floor(q / per) >> shift;
  const b = (q % per) >> shift;
  return parent * (1 << level) * (1 << level) + a * (1 << level) + b;
}

/**
 * Expected counts per cell at every grid threshold, wherever they come from: the whole level-0 table (`BrightTable`)
 * or the rows of the level-k cells asked (`CountRows.at`).
 */
export interface CellCounts {
  thresholds: ArrayLike<number>;
  /** The cell's expected count above threshold k; undefined where its row is not held. */
  count(cell: number, k: number): number | undefined;
}

function countOf(table: BrightTable | CellCounts, cell: number, k: number): number {
  if ("count" in table) return table.count(cell, k) ?? Number.NaN;
  return Number(table.expected[cell * table.thresholds.length + k]);
}

/** The table's expected count over `tiles` above threshold `k`: a sum. */
export function expectedIn(table: BrightTable | CellCounts, tiles: readonly number[], k: number): number {
  let sum = 0;
  for (const c of tiles) sum += countOf(table, c, k);
  return sum;
}

/** Whether `counts` holds a row for every cell of `cells`: a pick over a cell not held would be a guess (B9). */
export function covers(counts: BrightTable | CellCounts, cells: readonly number[]): boolean {
  return cells.every((c) => Number.isFinite(countOf(counts, c, 0)));
}

/**
 * The heights at which a vertical line through the disc at scene (x, z) lies inside the frustum of `viewProjection`
 * (column-major, as three.js writes it), clipped to |y| <= `slab`: the line is (x, y, z), so each of the clip space's
 * six inequalities -w <= c_i <= w (i = x, y, z) is linear in y - c = a + b y with a the matrix applied to (x, 0, z, 1)
 * and b its second column - and the interval is their intersection with the slab. Null where the line misses the
 * frustum. Geometry, no physics (D5).
 */
export function verticalExtent(viewProjection: ArrayLike<number>, x: number, z: number, slab = SLAB_KPC): [number, number] | null {
  const m = viewProjection;
  const a = (i: number) => Number(m[i]) * x + Number(m[8 + i]) * z + Number(m[12 + i]);
  const b = (i: number) => Number(m[4 + i]);
  let lo = -slab;
  let hi = slab;
  for (let i = 0; i < 3; i += 1) {
    for (const sign of [-1, 1]) {
      // w + sign * c_i >= 0, as p + q y >= 0
      const p = a(3) + sign * a(i);
      const q = b(3) + sign * b(i);
      if (Math.abs(q) < 1e-15) {
        if (p < 0) return null;
      } else if (q > 0) lo = Math.max(lo, -p / q);
      else hi = Math.min(hi, -p / q);
    }
  }
  return lo < hi ? [lo, hi] : null;
}

/** The (R, phi) centre of a level-k cell: the middle of its sub-ring and sub-sector, as systems.cell_bounds cuts it. */
export function cellCentre(cell: number, layout: CellLayout, level: number): { r: number; phi: number } {
  const n = 1 << level;
  const tile = Math.floor(cell / (n * n));
  const q = cell - tile * n * n;
  const i = Math.floor(tile / layout.sectors);
  const j = tile % layout.sectors;
  const [r0, r1] = [layout.ring_edges[i], layout.ring_edges[i + 1]];
  const [p0, p1] = [layout.sector_edges[j], layout.sector_edges[j + 1]];
  const a = Math.floor(q / n);
  const b = q % n;
  return { r: r0 + ((r1 - r0) * (a + 0.5)) / n, phi: p0 + ((p1 - p0) * (b + 0.5)) / n };
}

/**
 * Each level-k cell's weight in the frame's budget (S65, V6b; the lead's ruling on the zoomed footprint): the share of
 * the stars' published layer - sech^2(z / 2h) / 4h, h the render header's `layers.stars`, kpc - that lies inside the
 * frustum's height range over the cell's centre (`verticalExtent`, clipped to the footprint's slab), evaluated by
 * `layerShare`, the march's own function. 1 for a cell whose layer the camera sees whole, 0 for one it sees none of.
 * The footprint still asks every cell the frustum meets (a star high above a cell may be in view); the budget counts
 * the stars the camera can see.
 */
export function frustumWeights(
  cells: readonly number[],
  layout: CellLayout,
  level: number,
  viewProjection: ArrayLike<number>,
  h: number,
  slab = SLAB_KPC,
): Map<number, number> {
  const out = new Map<number, number>();
  for (const c of cells) {
    const { r, phi } = cellCentre(c, layout, level);
    const span = verticalExtent(viewProjection, r * Math.cos(phi), -r * Math.sin(phi), slab);
    out.set(c, span ? layerShare(span[0], span[1], h) : 0);
  }
  return out;
}

/** Counts weighted cell by cell: what the frame's threshold is picked over below the stars handover. */
export function weighted(counts: BrightTable | CellCounts, weights: ReadonlyMap<number, number>): CellCounts {
  return {
    thresholds: counts.thresholds,
    count: (cell, k) => {
      const w = weights.get(cell);
      return w === undefined ? undefined : w * countOf(counts, cell, k);
    },
  };
}

/**
 * The cells a zoomed frame asks (S65, the lead's ruling on the fetch): those expected to show at least one star in view
 * at the frame's threshold - weighted count f_c x expected_c(k) >= 1, the unit of the thing counted (B8), no other
 * constant. The rule's loss is what it skips: `loss`, the expected stars in view in the cells not asked, beside
 * `inView`, the expected stars in view over every cell. A cell with no count held is asked (never guessed away).
 */
export function cellsToFetch(counts: CellCounts, cells: readonly number[], k: number): { fetch: number[]; loss: number; inView: number } {
  const fetch: number[] = [];
  let loss = 0;
  let inView = 0;
  for (const c of cells) {
    const n = counts.count(c, k);
    if (n === undefined || !Number.isFinite(n)) {
      fetch.push(c);
      continue;
    }
    inView += n;
    if (n >= 1) fetch.push(c);
    else loss += n;
  }
  return { fetch, loss, inView };
}

/** What `table=1&cells=&level=` returns (api.ts loadBrightCounts): the thresholds and a row per cell asked. */
export interface CountsAnswer {
  thresholds: ArrayLike<number>;
  expected: ArrayLike<number>;
  cells: number[];
}

/**
 * The level-k cells' expected-count rows, held by (galaxy, level, cell) - each row the API's sum over the cell's finest
 * cells, never the viewer's. A memory bound, not a display choice: 153 float32 a row, so the bound is some 25 MB.
 */
export class CountRows {
  private held = new Map<string, ArrayLike<number>>();
  private grids = new Map<string, ArrayLike<number>>();
  constructor(private maxRows = 40_000) {}

  static key(galaxy: string, level: number, cell: number): string {
    return `${galaxy}|${level}|${cell}`;
  }

  has(galaxy: string, level: number, cell: number): boolean {
    return this.held.has(CountRows.key(galaxy, level, cell));
  }

  /** Hold an answer's rows. */
  hold(galaxy: string, level: number, answer: CountsAnswer): void {
    const n = answer.thresholds.length;
    this.grids.set(galaxy, answer.thresholds);
    answer.cells.forEach((cell, i) => {
      const key = CountRows.key(galaxy, level, cell);
      this.held.delete(key);
      this.held.set(key, Array.prototype.slice.call(answer.expected, i * n, (i + 1) * n) as number[]);
    });
    while (this.held.size > this.maxRows) this.held.delete(this.held.keys().next().value as string);
  }

  /** The held rows at a level as `CellCounts`; null until a row of this galaxy has been held. */
  at(galaxy: string, level: number): CellCounts | null {
    const thresholds = this.grids.get(galaxy);
    if (!thresholds) return null;
    return { thresholds, count: (cell, k) => this.held.get(CountRows.key(galaxy, level, cell))?.[k] };
  }
}

/** The level-k cells' rows, the ones not held asked in one request, and the held rows as `CellCounts`. */
export async function levelCounts(
  rows: CountRows,
  galaxy: string,
  level: number,
  cells: readonly number[],
  ask: (cells: number[], level: number, signal?: AbortSignal) => Promise<CountsAnswer>,
  signal?: AbortSignal,
): Promise<CellCounts> {
  const missing = cells.filter((c) => !rows.has(galaxy, level, c));
  if (missing.length) {
    const got = await ask([...missing], level, signal);
    if (got.cells.length !== missing.length) throw new Error(`the table answered ${got.cells.length} cells, asked ${missing.length}`);
    rows.hold(galaxy, level, got);
  }
  const counts = rows.at(galaxy, level);
  if (!counts) throw new Error("no expected-count row is held for this galaxy");
  return counts;
}

/**
 * The frame's one threshold (its index in the table): the table's rule - the smallest grid threshold at which the sum
 * over the tiles in view is at most the point budget. The counts fall along the grid, so the first that fits is it;
 * the last threshold if none does (no tile holds a star that bright).
 */
export function pickThreshold(table: BrightTable | CellCounts, tiles: readonly number[], budget: number): number {
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
 * A multi-tile answer split into its tiles: the rows come grouped by tile ascending (at level 0 by finest cell
 * ascending, the same), so each tile's rows are one run; a row's tile is its finest `cell` over `perTile` (the header's
 * cells.count over its tile.cells, 64) at level 0, and `tileOf(cell, level)` at level k. Every asked tile gets an
 * entry, an empty one where it holds no star, so it is held and not asked again. A column of several values a row
 * (`response`, rows x filters) is split by its own stride.
 */
export function splitByTile(columns: TileColumns, asked: readonly number[], perTile: number, level = 0): Map<number, TileRows> {
  const cell = columns.cell;
  const of = level ? (c: number) => tileOf(c, level) : (c: number) => Math.floor(c / perTile);
  const total = cell ? cell.length : 0;
  const out = new Map<number, TileRows>();
  let start = 0;
  for (const tile of [...asked].sort((a, b) => a - b)) {
    let end = start;
    while (end < total && of(Number(cell[end])) === tile) end += 1;
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

/** The tiles held, by (galaxy, level, tile, threshold): least recently used out first past `maxRows`. */
export class TileCache {
  private held = new Map<string, TileRows>();
  private rows = 0;
  constructor(private maxRows = TILE_CACHE_ROWS) {}

  static key(galaxy: string, tile: number, k: number, level = 0): string {
    return `${galaxy}|${level}|${tile}|${k}`;
  }

  get(galaxy: string, tile: number, k: number, level = 0): TileRows | undefined {
    const key = TileCache.key(galaxy, tile, k, level);
    const found = this.held.get(key);
    if (found) {
      this.held.delete(key);
      this.held.set(key, found);
    }
    return found;
  }

  set(galaxy: string, tile: number, k: number, rows: TileRows, level = 0): void {
    const key = TileCache.key(galaxy, tile, k, level);
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
  header: { tile: { cells: number[]; l_min_used: number; level?: number }; cells: { count: number }; white?: unknown };
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
    tiles: { inView: number; fetched: number; bytes: number; level: number };
  };
}

/**
 * The frame's stars: the tiles in view at threshold `k`, those not held asked in one request (the API refuses past
 * its cap, which the table's pick keeps under: the budget is at most 10⁵ and the cap 2 × 10⁵), held, and the union of
 * every tile in view returned. `galaxy` names what a tile's rows depend on besides (level, tile, threshold): the
 * query, the filter set and the white point. `level` is the tiles' (S65): 0 above the stars handover.
 */
export async function tilesFrame(
  cache: TileCache,
  galaxy: string,
  tiles: readonly number[],
  k: number,
  table: BrightTable | CellCounts,
  ask: (cells: number[], lMin: number, signal?: AbortSignal) => Promise<TileAnswer>,
  whites: Map<string, unknown>,
  signal?: AbortSignal,
  level = 0,
): Promise<TilesFrame> {
  const lMin = Number(table.thresholds[k]);
  const missing = tiles.filter((t) => !cache.get(galaxy, t, k, level));
  let bytes = 0;
  if (missing.length) {
    const got = await ask([...missing], lMin, signal);
    if (got.header.tile.l_min_used !== lMin) throw new Error(`tiles answered at ${got.header.tile.l_min_used} Lsun, asked at ${lMin}`);
    if ((got.header.tile.level ?? 0) !== level) throw new Error(`tiles answered at level ${got.header.tile.level}, asked at ${level}`);
    const perTile = got.header.cells.count / got.header.tile.cells.length;
    for (const [tile, rows] of splitByTile(got.columns, got.header.tile.cells, perTile, level)) cache.set(galaxy, tile, k, rows, level);
    whites.set(galaxy, got.header.white);
    bytes = got.bytes;
  }
  const parts = tiles.map((t) => cache.get(galaxy, t, k, level)).filter((p): p is TileRows => Boolean(p));
  const { rows, columns } = unionOf(parts);
  return {
    columns,
    header: {
      threshold: { l_min: lMin, index: k },
      count: { returned: rows, expected: expectedIn(table, tiles, k) },
      white: whites.get(galaxy),
      tiles: { inView: tiles.length, fetched: missing.length, bytes, level },
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
