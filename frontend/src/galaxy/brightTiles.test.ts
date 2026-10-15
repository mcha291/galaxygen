import { describe, expect, it } from "vitest";

import { type BrightTable, type CellLayout, type TileAnswer, TileCache, expectedIn, pickThreshold, placeRemainder, splitByTile, tilesFrame, tilesIn, unionOf } from "./brightTiles";

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
