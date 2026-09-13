import { describe, expect, it } from "vitest";

import { extent, toScene } from "./positions";

describe("toScene", () => {
  it("puts the disc in the x-z plane and height on y", () => {
    const p = toScene([8, 8], [0, Math.PI / 2], [0.3, -0.1]);
    expect(p[0]).toBeCloseTo(8, 6);
    expect(p[1]).toBeCloseTo(0.3, 6);
    expect(p[2]).toBeCloseTo(0, 6);
    expect(p[3]).toBeCloseTo(0, 6);
    expect(p[4]).toBeCloseTo(-0.1, 6);
    expect(p[5]).toBeCloseTo(-8, 6);
  });

  it("refuses columns of different lengths", () => {
    expect(() => toScene([1, 2], [0], [0, 0])).toThrow(/lengths differ/);
  });
});

describe("extent", () => {
  it("is an in-plane radius, ignoring height", () => {
    expect(extent(toScene([3, 12.5], [1, 2], [40, 0]), 1)).toBeCloseTo(12.5, 5);
  });

  it("frames on the quantile, not the outlier", () => {
    const radii = Array.from({ length: 100 }, (_, i) => i + 1);
    radii[99] = 1000;
    const p = toScene(radii, new Array(100).fill(0), new Array(100).fill(0));
    expect(extent(p, 0.95)).toBeCloseTo(95, 5);
  });
});
