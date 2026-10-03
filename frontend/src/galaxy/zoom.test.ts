import { describe, expect, it } from "vitest";

import { distanceFor } from "./capture";
import { ZOOM_SPAN, acrossOf, clipPlanes, distanceOf, scaleBar, zoomOf, zoomRange } from "./zoom";

const R = { min: 0.1, max: 100 };

describe("the zoom's range through a lens (S54, D213 ruling 5)", () => {
  it("at 45° is the range the view has always had: reach / 200 to 8 reach, planes at reach / 1000 and 20 reach", () => {
    const range = zoomRange(30, 45);
    expect(range).toEqual({ min: 30 / 200, max: 240 });
    expect(zoomRange(30)).toEqual(range); // the default lens
    expect(range.max / range.min).toBeCloseTo(ZOOM_SPAN, 9);
    const planes = clipPlanes(range);
    expect(planes.near).toBeCloseTo(30 / 1000, 12);
    expect(planes.far).toBe(600);
  });

  it("through a 5° lens spans the same widths of view from 9.49 times further, and the planes follow", () => {
    const wide = zoomRange(30, 45);
    const long = zoomRange(30, 5);
    expect(long.min / wide.min).toBeCloseTo(9.487, 3);
    expect(long.max / long.min).toBeCloseTo(ZOOM_SPAN, 9);
    // The closest and the farthest view are the same number of kiloparsecs across.
    expect(acrossOf(long.min, 5, 1)).toBeCloseTo(acrossOf(wide.min, 45, 1), 10);
    expect(acrossOf(long.max, 5, 1)).toBeCloseTo(acrossOf(wide.max, 45, 1), 10);
    // The template's stand (20 kpc framed: 458 kpc away) is inside the range, and the galaxy inside the far plane:
    // left at 20 reach, the plane would stand at 600 kpc and the 45° range would stop at 240.
    const stand = distanceFor(20, 5);
    expect(stand).toBeGreaterThan(long.min);
    expect(stand).toBeLessThan(long.max);
    expect(clipPlanes(long).far).toBeGreaterThan(long.max + 60);
    expect(clipPlanes(long).near).toBeLessThan(long.min);
  });

  it("holds a stand the view is given, where a compact galaxy's own reach would not", () => {
    // A galaxy whose sample reaches 5 kpc, framed at 20 kpc by its template: 8 reach is 40 kpc, the stand 48.3.
    expect(distanceFor(20, 45)).toBeGreaterThan(zoomRange(5, 45).max);
    for (const fov of [45, 5]) {
      const range = zoomRange(5, fov, 20);
      expect(distanceFor(20, fov)).toBeLessThan(range.max / 1.2);
      expect(range.max / range.min).toBeCloseTo(ZOOM_SPAN, 9);
    }
    // And changes nothing where the reach already holds it.
    expect(zoomRange(30, 45, 20)).toEqual(zoomRange(30, 45));
  });
});

describe("zoom", () => {
  it("maps distance to [0, 1] logarithmically and back", () => {
    expect(zoomOf(100, R)).toBe(0);
    expect(zoomOf(0.1, R)).toBe(1);
    expect(zoomOf(Math.sqrt(10), R)).toBeCloseTo(0.5, 12);
    expect(distanceOf(zoomOf(7, R), R)).toBeCloseTo(7, 9);
  });

  it("clamps outside the range", () => {
    expect(zoomOf(1e6, R)).toBe(0);
    expect(distanceOf(2, R)).toBeCloseTo(0.1, 12);
  });
});

describe("acrossOf", () => {
  it("is 2 d tan(fov/2) times the aspect", () => {
    expect(acrossOf(10, 90, 1)).toBeCloseTo(20, 9);
    expect(acrossOf(10, 90, 2)).toBeCloseTo(40, 9);
  });
});

describe("scaleBar", () => {
  it("picks the largest 1, 2 or 5 × 10^k that fits", () => {
    expect(scaleBar(10)).toEqual({ kpc: 10, px: 100 });
    expect(scaleBar(30)).toEqual({ kpc: 2, px: 60 });
    expect(scaleBar(2000).kpc).toBeCloseTo(0.05, 12);
  });
});
