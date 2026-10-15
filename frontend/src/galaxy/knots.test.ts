import { describe, expect, it } from "vitest";

import type { CellLayout } from "./brightTiles";
import { cellAt, evenLayout, undrawnShare } from "./knots";
import { PLUMMER_HALF_MASS, resolvedAt } from "./plummer";

// Four cells: two rings by two sectors, as systems.cell_edges cuts them.
const LAYOUT: CellLayout = { rings: 2, sectors: 2, ring_edges: [0.5, 10.25, 20], sector_edges: [0, Math.PI, 2 * Math.PI] };

// A hand census: each knot's naming cell and Halpha (Lsun); cell 3 names none. The field's Halpha per cell (Lsun).
const CELLS = [0, 0, 1, 2, 2, 2];
const LIGHT = [3e5, 1e5, 2.5e4, 7e3, 0, 4.2e6];
const FIELD = [2.0e5, 1.0e5, 3.3e6, 8.0e4];

const sum = (a: ArrayLike<number>) => Array.from(a).reduce((s, v) => s + v, 0);

describe("the field's undrawn share (S64, V6, R5)", () => {
  it("is 0 in every cell when all are drawn - the knotless cell 3 too (1 - d, d = 1) - and 1 everywhere when none is", () => {
    expect(Array.from(undrawnShare(CELLS, LIGHT, true, LAYOUT))).toEqual([0, 0, 0, 0]);
    expect(Array.from(undrawnShare(CELLS, LIGHT, false, LAYOUT))).toEqual([1, 1, 1, 1]);
  });

  it("closes on the hand census: points + scaled field = the census where every knot is drawn, the field where none, to 1e-12", () => {
    const K = [4e5, 2.5e4, 7e3 + 4.2e6, 0];
    for (const [drawn, want] of [
      [true, sum(K)],
      [false, sum(FIELD)],
    ] as const) {
      const share = undrawnShare(CELLS, LIGHT, drawn, LAYOUT);
      const points = drawn ? sum(LIGHT) : 0;
      const field = FIELD.reduce((s, f, c) => s + f * share[c], 0);
      expect(Math.abs(points + field - want) / want).toBeLessThan(1e-12);
    }
  });

  it("is the undrawn fraction between, in [0, 1] whatever the census against the field", () => {
    // Every other knot drawn: cell 0 keeps 1e5 of 4e5, cell 1 none, cell 2 all (its drawn knot is dark); the mask by
    // row of the bright one alone keeps cell 2's 7e3 of 4.207e6.
    const share = undrawnShare(CELLS, LIGHT, [1, 0, 1, 0, 1, 0], LAYOUT);
    expect(share[0]).toBeCloseTo(0.25, 7);
    expect(share[1]).toBe(0);
    expect(share[2]).toBe(1);
    expect(undrawnShare(CELLS, LIGHT, [0, 0, 0, 0, 0, 1], LAYOUT)[2]).toBeCloseTo(7e3 / 4.207e6, 7);
    // The knotless cell takes the disc's undrawn share: 1 - 3.25e5 / 4.632e6.
    expect(share[3]).toBeCloseTo(1 - 3.25e5 / 4.632e6, 7);
    for (const v of share) expect(v >= 0 && v <= 1).toBe(true);
    // Half the census's light drawn: the knotless cells (2 and 3) at 0.5, a cell all drawn at 0, one undrawn at 1.
    expect(Array.from(undrawnShare([0, 1], [5e4, 5e4], [1, 0], LAYOUT))).toEqual([0, 1, 0.5, 0.5]);
    // A missing or negative light names nothing (B9).
    expect(Array.from(undrawnShare([0, 1], [Number.NaN, -1], true, LAYOUT))).toEqual([1, 1, 1, 1]);
  });

  it("finds a place's level-0 cell by the layout's edges, as the march does", () => {
    expect(evenLayout(LAYOUT)).toBe(true);
    expect(cellAt(3, 0.1, LAYOUT)).toBe(0);
    expect(cellAt(3, 4, LAYOUT)).toBe(1);
    expect(cellAt(12, 0.1, LAYOUT)).toBe(2);
    expect(cellAt(12, -0.1, LAYOUT)).toBe(3);
    expect(cellAt(0.2, 1, LAYOUT)).toBe(-1);
    expect(cellAt(20, 1, LAYOUT)).toBe(-1);
    expect(evenLayout({ ...LAYOUT, ring_edges: [0.5, 9, 20] })).toBe(false);
  });
});

describe("the clusters with their radius at the picture test's frames (S64, V6, R7: T6's gate)", () => {
  it("draws no cluster with its profile in a star-first capture: the frame is the same bytes on and off", () => {
    // e2e/captures.json's star-first captures: 1024 px; the Milky Way face-on, 20 kpc half-height (39.1 pc a pixel at
    // the centre's distance); NGC 4414 at 55 degrees, 15 kpc, through its capture's 5 degree lens (fov_deg 5): the
    // camera 343.6 kpc off, its nearest disc point, 15 kpc toward the camera, at 0.964 of the centre's distance (28.25
    // pc a pixel; S64's gate first wrote 19.3 pc, under a 45 degree lens that is not the capture's). The largest
    // half-mass radius is 3.00 pc (Milky Way) and 3.11 pc (NGC 4414): S64's probe, REPORT.md section 1C.
    const centre = (radiusKpc: number, px: number) => (2 * radiusKpc * 1000) / px;
    const camera = 15 / Math.tan((2.5 * Math.PI) / 180);
    const nearest = (camera - 15 * Math.sin((55 * Math.PI) / 180)) / camera;
    expect(camera).toBeCloseTo(343.6, 1);
    expect(centre(15, 1024) * nearest).toBeCloseTo(28.25, 2);
    expect(resolvedAt(3.0, centre(20, 1024))).toBe(false);
    expect(resolvedAt(3.11, centre(15, 1024) * nearest)).toBe(false);
    // The median cluster (0.445 pc) fills a pixel below a 0.91 kpc wide view of 1024 pixels; the largest below 6.1.
    expect(resolvedAt(0.445, 910 / 1024)).toBe(true);
    expect(resolvedAt(3.0, 6100 / 1024)).toBe(true);
    expect(resolvedAt(3.0, 6200 / 1024)).toBe(false);
    expect(PLUMMER_HALF_MASS).toBeGreaterThan(1.3);
  });
});
