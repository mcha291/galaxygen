import { describe, expect, it } from "vitest";

import { type BrightTable, type CellLayout, type CountsAnswer, CountRows, type TileAnswer, TileCache, cellsIn, covers, expectedIn, levelCounts, pickThreshold, placeRemainder, splitByTile, tileOf, tilesFrame, tilesIn, unionOf } from "./brightTiles";
import { levelFor } from "./region";

// A layout of the API's shape: 32 rings from 0.0375 to 29.9625 kpc (the default grid's R[0], R[-1]), 32 sectors.
const LAYOUT: CellLayout = {
  rings: 32,
  sectors: 32,
  ring_edges: Array.from({ length: 33 }, (_, i) => 0.0375 + (i * (29.9625 - 0.0375)) / 32),
  sector_edges: Array.from({ length: 33 }, (_, j) => (j * 2 * Math.PI) / 32),
};

// A hand table: four thresholds, every cell holding 100, 40, 10, 0 stars above them, but cell 5 ten times that.
function handTable(): BrightTable {
  const per = [100, 40, 10, 0];
  const expected = new Float32Array(1024 * 4);
  for (let c = 0; c < 1024; c += 1) for (let k = 0; k < 4; k += 1) expected[c * 4 + k] = per[k] * (c === 5 ? 10 : 1);
  return { thresholds: [1000, 1122, 1259, 1413], expected, layout: LAYOUT, rule: "pick the smallest grid threshold at which the sum over the tiles in view is at most the point budget" };
}

describe("tilesIn: the footprint as level-0 cells, as systems.cells_in cuts them", () => {
  it("a window that is exactly a block of cells names that block and no neighbour", () => {
    const e = LAYOUT.ring_edges;
    const s = LAYOUT.sector_edges;
    expect(tilesIn({ r_min: e[8], r_max: e[10], phi_min: s[3], phi_max: s[6] }, LAYOUT)).toEqual([259, 260, 261, 291, 292, 293]);
  });

  it("a window narrower than a cell names the cell holding it; one across φ = 0 names both sides", () => {
    expect(tilesIn({ r_min: 8.0, r_max: 8.01, phi_min: 0.2, phi_max: 0.21 }, LAYOUT)).toEqual([8 * 32 + 1]);
    const s = LAYOUT.sector_edges;
    expect(tilesIn({ r_min: LAYOUT.ring_edges[12], r_max: LAYOUT.ring_edges[13], phi_min: s[31], phi_max: 2 * Math.PI + s[1] - 1e-9 }, LAYOUT)).toEqual([384, 415]);
  });

  it("the whole disc is every cell once", () => {
    const all = tilesIn({ r_min: 0, r_max: 30, phi_min: 0, phi_max: 2 * Math.PI }, LAYOUT);
    expect(all).toHaveLength(1024);
    expect(new Set(all).size).toBe(1024);
  });
});

describe("pickThreshold: the table's rule, a sum and a comparison", () => {
  it("is the smallest grid threshold whose sum over the tiles in view is at most the budget", () => {
    const t = handTable();
    expect(expectedIn(t, [1, 2, 3], 0)).toBe(300);
    expect(pickThreshold(t, [1, 2, 3], 300)).toBe(0); // at most: equal fits
    expect(pickThreshold(t, [1, 2, 3], 299)).toBe(1);
    expect(pickThreshold(t, [1, 2, 3], 100)).toBe(2);
    expect(pickThreshold(t, [1, 5], 100)).toBe(3); // cell 5 holds 100 at the third threshold: 110 > 100
    expect(pickThreshold(t, [5], 0)).toBe(3); // none fits but the last: the last
  });
});

/** A tile answer's columns for `tiles`, `n[t]` stars each, grouped by finest cell ascending: cell = tile * 64 + j. */
function answerOf(tiles: number[], n: Record<number, number>): TileAnswer {
  const cells: bigint[] = [];
  const lum: number[] = [];
  const response: number[] = [];
  for (const t of [...tiles].sort((a, b) => a - b)) {
    for (let i = 0; i < (n[t] ?? 0); i += 1) {
      cells.push(BigInt(t * 64 + (i % 64)));
      lum.push(t * 1000 + i);
      response.push(t, i, -t);
    }
  }
  return {
    columns: { cell: BigInt64Array.from(cells), bright_star_luminosity: Float32Array.from(lum), response: Float32Array.from(response) },
    header: { tile: { cells: [...tiles].sort((a, b) => a - b), l_min_used: 1122 }, cells: { count: 64 * tiles.length }, white: { kelvin: 6500, response: [1, 1, 1] } },
    bytes: cells.length * (8 + 4 + 12),
  };
}

describe("splitByTile and unionOf: each tile once, so no star twice", () => {
  it("splits a multi-tile answer by its rows' tile, the response by its own stride, an empty tile held empty", () => {
    const got = answerOf([7, 3, 9], { 3: 2, 7: 0, 9: 3 });
    const parts = splitByTile(got.columns, got.header.tile.cells, 64);
    expect([...parts.keys()]).toEqual([3, 7, 9]);
    expect([3, 7, 9].map((t) => parts.get(t)!.rows)).toEqual([2, 0, 3]);
    expect(Array.from(parts.get(9)!.columns.response as Float32Array)).toEqual([9, 0, -9, 9, 1, -9, 9, 2, -9]);
    const union = unionOf([...parts.values()]);
    expect(union.rows).toBe(5);
    expect(Array.from(union.columns.bright_star_luminosity as Float32Array)).toEqual([3000, 3001, 9000, 9001, 9002]);
    expect(union.columns.cell).toBeInstanceOf(BigInt64Array);
  });

  it("refuses rows outside the tiles asked", () => {
    const got = answerOf([3, 4], { 3: 1, 4: 1 });
    expect(() => splitByTile(got.columns, [3], 64)).toThrow(/outside the tiles/);
  });
});

describe("tilesFrame and TileCache: held by (galaxy, tile, threshold)", () => {
  it("asks only the tiles not held at the frame's threshold, and every tile again at a new one", async () => {
    const asked: [number[], number][] = [];
    const ask = async (cells: number[], lMin: number) => {
      asked.push([cells, lMin]);
      return answerOf(cells, Object.fromEntries(cells.map((c) => [c, 2])));
    };
    const cache = new TileCache();
    const whites = new Map<string, unknown>();
    const t = handTable();
    const a = await tilesFrame(cache, "g", [1, 2], 1, t, ask, whites);
    expect(asked).toEqual([[[1, 2], 1122]]);
    expect([a.header.count.returned, a.header.threshold.l_min, a.header.tiles.fetched]).toEqual([4, 1122, 2]);
    const b = await tilesFrame(cache, "g", [2, 3], 1, t, ask, whites); // pan: tile 2 held, 3 asked
    expect(asked[1]).toEqual([[3], 1122]);
    expect([b.header.count.returned, b.header.tiles.fetched, b.header.count.expected]).toEqual([4, 1, 80]);
    expect(b.header.white).toEqual({ kelvin: 6500, response: [1, 1, 1] });
    const c = await tilesFrame(cache, "g", [2, 3], 1, t, ask, whites); // still: nothing asked
    expect([asked.length, c.header.tiles.fetched]).toEqual([2, 0]);
    // another galaxy (query, filter set or white point) holds its own tiles
    await tilesFrame(cache, "h", [2], 1, t, ask, whites);
    expect(asked[2]).toEqual([[2], 1122]);
    // the cache's key is (galaxy, tile, threshold): a held tile at one threshold is not another threshold's
    expect(cache.get("g", 2, 1)).toBeDefined();
    expect(cache.get("g", 2, 0)).toBeUndefined();
    expect(TileCache.key("g", 2, 1)).not.toBe(TileCache.key("g", 21, 0));
  });

  it("refuses an answer at a threshold other than the one asked", async () => {
    const ask = async (cells: number[]) => ({ ...answerOf(cells, {}), header: { ...answerOf(cells, {}).header, tile: { cells, l_min_used: 999 } } });
    await expect(tilesFrame(new TileCache(), "g", [1], 1, handTable(), ask, new Map())).rejects.toThrow(/asked at 1122/);
  });

  it("drops the least recently used tiles past its row bound", () => {
    const cache = new TileCache(5);
    const rows = (n: number) => ({ rows: n, columns: {} });
    cache.set("g", 1, 0, rows(3));
    cache.set("g", 2, 0, rows(2));
    cache.get("g", 1, 0); // 1 is now the more recent
    cache.set("g", 3, 0, rows(2));
    expect([cache.get("g", 1, 0)?.rows, cache.get("g", 2, 0), cache.get("g", 3, 0)?.rows]).toEqual([3, undefined, 2]);
  });
});

describe("placeRemainder: the remainder's rule, a product and a sum", () => {
  it("is middle(R, f) · w_middle(R, φ) + old(R, f) · w_old(R, φ), row-major (R, φ, filter)", () => {
    const middle = [1, 2, 3, 4]; // 2 rings x 2 filters
    const old = [10, 20, 30, 40];
    const wm = [0, 1, 2, 0.5, 0.5, 0.5]; // 2 rings x 3 sectors
    const wo = [1, 1, 1, 2, 0, 1];
    const got = placeRemainder(middle, old, wm, wo, 2)!;
    expect(Array.from(got)).toEqual([10, 20, 11, 22, 12, 24, 61.5, 82, 1.5, 2, 31.5, 42]);
  });

  it("is null where an array is missing or the shapes disagree (B9: no remainder, not a guess)", () => {
    expect(placeRemainder(undefined, [1], [1], [1], 1)).toBeNull();
    expect(placeRemainder([1, 2], [1], [1], [1], 1)).toBeNull();
    expect(placeRemainder([1, 2, 3], [1, 2, 3], [1, 1], [1, 1], 2)).toBeNull();
  });
});

// --- S65 (V6b, RULING_S65 R1): the tiles at level k ------------------------------------------------------------------

describe("cellsIn and tileOf: the footprint as level-k cells, as systems.cells_in and cell_bounds cut them", () => {
  it("is tilesIn at level 0, and at level k each level-0 cell's 4^k children that meet the window, ascending", () => {
    const w = { r_min: 8.0, r_max: 8.6, phi_min: 1.0, phi_max: 1.2 };
    expect(cellsIn(w, LAYOUT, 0)).toEqual(tilesIn(w, LAYOUT));
    for (const level of [1, 2, 3]) {
      const got = cellsIn(w, LAYOUT, level);
      expect([...got].sort((a, b) => a - b)).toEqual(got);
      // every one stands in a level-0 cell the window meets, and the level-0 cells are exactly those
      expect([...new Set(got.map((c) => Math.floor(c / 4 ** level)))]).toEqual(tilesIn(w, LAYOUT));
      expect(got.length).toBeLessThan(tilesIn(w, LAYOUT).length * 4 ** level);
    }
  });

  it("a window that is exactly one level-k cell names that cell and no neighbour", () => {
    const e = LAYOUT.ring_edges;
    const s = LAYOUT.sector_edges;
    // tile 261 (ring 8, sector 5); at level 1 its child q = 2 is sub-ring 1, sub-sector 0
    const r0 = e[8] + ((e[9] - e[8]) * 1) / 2;
    const r1 = e[8] + ((e[9] - e[8]) * 2) / 2;
    const p0 = s[5];
    const p1 = s[5] + ((s[6] - s[5]) * 1) / 2;
    const w = { r_min: r0, r_max: r1, phi_min: p0, phi_max: p1 };
    expect(cellsIn(w, LAYOUT, 1)).toEqual([261 * 4 + 2]);
    // its four level-2 children (sub-rings 2-3, sub-sectors 0-1), and at level 3 its sixteen
    expect(cellsIn(w, LAYOUT, 2)).toEqual([4184, 4185, 4188, 4189]);
    expect(cellsIn(w, LAYOUT, 3)).toHaveLength(16);
  });

  it("the whole disc is every level-k cell once", () => {
    for (const level of [1, 2]) {
      const all = cellsIn({ r_min: 0, r_max: 30, phi_min: 0, phi_max: 2 * Math.PI }, LAYOUT, level);
      expect(all).toHaveLength(1024 * 4 ** level);
      expect(new Set(all).size).toBe(all.length);
    }
  });

  it("tileOf names the level-k cell a finest cell stands in: cell / 64 at level 0, the finest cell itself at level 3", () => {
    expect(tileOf(261 * 64 + 63, 0)).toBe(261);
    expect(tileOf(16747, 3)).toBe(16747);
    // finest cell 261*64 + (5*8 + 6): sub-ring 5, sub-sector 6 of tile 261 -> level 1: (1, 1) = q 3; level 2: (2, 3) = q 11
    const c = 261 * 64 + 5 * 8 + 6;
    expect([tileOf(c, 1), tileOf(c, 2)]).toEqual([261 * 4 + 3, 261 * 16 + 11]);
  });

  it("the level the star-first view asks is the field mode's levelFor: 0 from 4 kpc, 1 to 1, 2 to 0.25, 3 below", () => {
    expect([20, 15, 4, 3.9, 1, 0.99, 0.5, 0.25, 0.24, 0.062].map(levelFor)).toEqual([0, 0, 0, 1, 1, 2, 2, 2, 3, 3]);
  });
});

describe("CountRows and levelCounts: the level-k rows held by (galaxy, level, cell)", () => {
  const answer = (cells: number[]): CountsAnswer => ({
    thresholds: [1000, 1122, 1259, 1413],
    expected: Float32Array.from(cells.flatMap((c) => [100, 40, 10, 0].map((v) => v * (c === 7 ? 10 : 1)))),
    cells: [...cells].sort((a, b) => a - b),
  });

  it("asks only the rows not held, and picks the threshold over the level-k cells by the table's rule", async () => {
    const asked: [number[], number][] = [];
    const ask = async (cells: number[], level: number) => {
      asked.push([cells, level]);
      return answer(cells);
    };
    const rows = new CountRows();
    const a = await levelCounts(rows, "g", 2, [5, 6], ask);
    expect(asked).toEqual([[[5, 6], 2]]);
    expect([covers(a, [5, 6]), covers(a, [5, 7])]).toEqual([true, false]);
    const b = await levelCounts(rows, "g", 2, [6, 7], ask);
    expect(asked[1]).toEqual([[7], 2]);
    expect(expectedIn(b, [6, 7], 0)).toBe(1100);
    expect(pickThreshold(b, [5, 6], 80)).toBe(1);
    expect(pickThreshold(b, [5, 7], 100)).toBe(3); // cell 7 holds 100 at the third threshold
    // another level and another galaxy hold their own rows
    await levelCounts(rows, "g", 3, [5], ask);
    await levelCounts(rows, "h", 2, [5], ask);
    expect(asked.slice(2)).toEqual([[[5], 3], [[5], 2]]);
    expect(CountRows.key("g", 2, 5)).not.toBe(CountRows.key("g", 3, 5));
  });

  it("refuses an answer that names other cells than asked", async () => {
    const ask = async () => answer([1]);
    await expect(levelCounts(new CountRows(), "g", 1, [1, 2], ask)).rejects.toThrow(/answered 1 cells, asked 2/);
  });
});

describe("tilesFrame at level k: held by (galaxy, level, tile, threshold), split by tileOf", () => {
  /** A level-2 answer: each tile's rows in its first two finest cells, by tile ascending. */
  function levelAnswer(tiles: number[], n: number, level = 2): TileAnswer {
    const cells: bigint[] = [];
    const lum: number[] = [];
    for (const t of [...tiles].sort((a, b) => a - b)) {
      const parent = Math.floor(t / 16);
      const q = t % 16;
      const finest = parent * 64 + Math.floor(q / 4) * 2 * 8 + (q % 4) * 2; // its first finest cell
      for (let i = 0; i < n; i += 1) {
        cells.push(BigInt(finest + (i % 2)));
        lum.push(t + i);
      }
    }
    return {
      columns: { cell: BigInt64Array.from(cells), bright_star_luminosity: Float32Array.from(lum) },
      header: { tile: { cells: [...tiles].sort((a, b) => a - b), l_min_used: 1122, level }, cells: { count: 4 * tiles.length }, white: null },
      bytes: cells.length * 12,
    };
  }

  it("splits each level-k tile's run, holds it at its level and asks with that level", async () => {
    const asked: number[][] = [];
    const ask = async (cells: number[]) => {
      asked.push(cells);
      return levelAnswer(cells, 3);
    };
    const cache = new TileCache();
    const rows = new CountRows();
    const table = async (c: number[]): Promise<CountsAnswer> => ({ thresholds: [1000, 1122], expected: Float32Array.from(c.flatMap(() => [50, 5])), cells: c });
    await levelCounts(rows, "g", 2, [4176, 4177, 4190], table);
    const counts = rows.at("g", 2)!;
    const f = await tilesFrame(cache, "g", [4176, 4177, 4190], 1, counts, ask, new Map(), undefined, 2);
    expect([f.header.count.returned, f.header.count.expected, f.header.tiles.level]).toEqual([9, 15, 2]);
    expect(cache.get("g", 4190, 1, 2)?.rows).toBe(3);
    expect(cache.get("g", 4190, 1, 0)).toBeUndefined(); // the level is in the key
    await tilesFrame(cache, "g", [4177, 4190], 1, counts, ask, new Map(), undefined, 2);
    expect(asked).toEqual([[4176, 4177, 4190]]);
    // an answer at another level than asked is refused
    const wrong = async (c: number[]) => levelAnswer(c, 1, 1);
    await expect(tilesFrame(new TileCache(), "g", [4176], 1, counts, wrong, new Map(), undefined, 2)).rejects.toThrow(/level 1, asked at 2/);
  });
});
