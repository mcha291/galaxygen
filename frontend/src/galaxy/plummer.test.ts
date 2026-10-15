import { describe, expect, it } from "vitest";

import {
  DISC_LOOP_HALF,
  PLUMMER_HALF_MASS,
  PLUMMER_REACH,
  discBoxSum,
  discCover,
  plummerCorner,
  plummerRect,
  profileWeights,
  resolvedAt,
} from "./plummer";

const sum = (a: ArrayLike<number>) => Array.from(a).reduce((s, v) => s + v, 0);

describe("the Plummer profile (S64, V6, R7; T6)", () => {
  it("takes a = r_h / 1.3048 (the plan's 1.305), the radius holding half the mass in three dimensions", () => {
    expect(PLUMMER_HALF_MASS).toBeCloseTo(1.305, 3);
    // M(<r) = r^3 / (r^2 + a^2)^(3/2) is a half at r_h.
    const a = 1;
    const r = PLUMMER_HALF_MASS * a;
    expect(r ** 3 / (r * r + a * a) ** 1.5).toBeCloseTo(0.5, 12);
  });

  it("integrates its projected profile exactly over a rectangle: the corner's mixed derivative is the profile", () => {
    const a = 0.7;
    const h = 1e-4;
    for (const [x, y] of [[0.3, 0.2], [1.5, -0.4], [-2, 3]]) {
      const mixed = (plummerCorner(x + h, y + h, a) - plummerCorner(x - h, y + h, a) - plummerCorner(x + h, y - h, a) + plummerCorner(x - h, y - h, a)) / (4 * h * h);
      expect(mixed / (a * a / (Math.PI * (a * a + x * x + y * y) ** 2))).toBeCloseTo(1, 5);
    }
    // The whole plane holds all the light; a disc of radius R holds R^2 / (R^2 + a^2) and the square round it more.
    expect(plummerRect(-1e7, 1e7, -1e7, 1e7, a)).toBeCloseTo(1, 6);
    expect(plummerRect(-8 * a, 8 * a, -8 * a, 8 * a, a)).toBeGreaterThan(64 / 65);
  });

  it("sums its box's pixels to the cluster's light to 1e-3 at every pixel scale (the gate; here to 1e-12)", () => {
    for (const aPx of [0.383, 0.6, 1, 2.5, 7]) {
      for (const [cx, cy] of [[100.5, 80.5], [33.17, 9.91], [512.999, 0.001]]) {
        const { weights, side } = profileWeights(1, cx, cy, aPx);
        expect(Math.abs(sum(weights) - 1)).toBeLessThan(1e-12);
        expect(side).toBe(2 * Math.max(1, Math.min(60, Math.ceil(PLUMMER_REACH * aPx))) + 1);
        expect(Math.min(...weights)).toBeGreaterThan(0);
      }
    }
  });

  it("is the Plummer in its box: the central pixel's share is the profile's over that pixel, over the box's", () => {
    const aPx = 2;
    const { weights, side, x0, y0 } = profileWeights(1, 50.5, 50.5, aPx);
    const centre = (50 - y0) * side + (50 - x0);
    const box = plummerRect(x0 - 50.5, x0 + side - 50.5, y0 - 50.5, y0 + side - 50.5, aPx);
    expect(weights[centre]).toBeCloseTo(plummerRect(-0.5, 0.5, -0.5, 0.5, aPx) / box, 14);
    // Within the box the light past it is 1.5 % or less, put back in.
    expect(box).toBeGreaterThan(1 - 1 / (1 + PLUMMER_REACH ** 2));
  });
});

describe("the knot's disc and the switch (S64, V6, R6)", () => {
  it("is a point until its diameter fills a pixel, then drawn with its extent", () => {
    expect(resolvedAt(0.4, 1)).toBe(false);
    expect(resolvedAt(0.5, 1)).toBe(true);
    expect(resolvedAt(0, 1)).toBe(false);
    // The Milky Way's Stromgren radii (median 0.72 pc, max 20.7) on a 1024-pixel frame 40 kpc wide (39 pc a pixel):
    // the median a point, the largest a disc of half a pixel's radius and more.
    expect(resolvedAt(0.72, 40_000 / 1024)).toBe(false);
    expect(resolvedAt(20.7, 40_000 / 1024)).toBe(true);
  });

  it("sums its disc's pixels to the knot's light: the loop's box to rounding, the area beyond it to 1e-3", () => {
    for (const r of [0.5, 0.8, 1.7, 3.2, DISC_LOOP_HALF - 1]) {
      for (const [cx, cy] of [[10.5, 10.5], [7.13, 3.77]]) {
        const { weights } = profileWeights(2, cx, cy, r);
        expect(Math.abs(sum(weights) - 1)).toBeLessThan(1e-12);
      }
    }
    // Past the loop the normaliser is the disc's area: the anti-aliased edge's sum is it to well under 1e-3.
    for (const r of [DISC_LOOP_HALF, 27.3, 33.6, 40.2]) {
      for (const [cx, cy] of [[100.5, 100.5], [101.13, 99.77]]) {
        expect(Math.abs(discBoxSum(cx, cy, r) / (Math.PI * r * r) - 1)).toBeLessThan(1e-3);
      }
    }
    expect(discCover(0, 0, 0.5)).toBe(1);
    expect(discCover(3, 0, 1)).toBe(0);
  });
});
