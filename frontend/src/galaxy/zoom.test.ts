import { describe, expect, it } from "vitest";

import { acrossOf, distanceOf, scaleBar, zoomOf } from "./zoom";

const R = { min: 0.1, max: 100 };

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
