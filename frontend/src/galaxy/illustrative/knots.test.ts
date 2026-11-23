// The pink HII regions (S106, BUILD_VIII row 106): the arithmetic of knotsMath.ts and the feature's registration.

import { describe, expect, it } from "vitest";

import { features, illDefaults, illKey } from "./index";
import { knots } from "./knots";
import {
  CORE_COLOUR,
  MAX_BLOBS,
  PINK,
  type Placement,
  armWeight,
  brightest,
  compressLight,
  hash01,
  quantile,
  radialWeight,
  regionAttributes,
  regionBlobs,
  regionColour,
  regionRadius,
  ringContrast,
  ringRanges,
} from "./knotsMath";

describe("the regions' size", () => {
  it("is the radius times the multiplier, clamped to the floor and the ceiling", () => {
    expect(regionRadius(10, 8, 40, 150)).toBe(80);
    expect(regionRadius(2, 8, 40, 150)).toBe(40);
    expect(regionRadius(70, 8, 40, 150)).toBe(150);
    expect(regionRadius(NaN, 8, 40, 150)).toBe(40);
    expect(regionRadius(0, 8, 40, 150)).toBe(40);
    // A ceiling under the floor: the floor.
    expect(regionRadius(10, 8, 100, 50)).toBe(100);
  });
});

describe("the light's compression", () => {
  it("is ref (L / ref)^power: the reference fixed, the range shrunk, nothing for none", () => {
    expect(compressLight(100, 100, 0.3)).toBeCloseTo(100, 12);
    expect(compressLight(1e4, 100, 0.5)).toBeCloseTo(1000, 9);
    expect(compressLight(1, 100, 0.5)).toBeCloseTo(10, 12);
    expect(compressLight(5, 100, 1)).toBeCloseTo(5, 12);
    expect(compressLight(0, 100, 0.5)).toBe(0);
    expect(compressLight(-1, 100, 0.5)).toBe(0);
    expect(compressLight(Infinity, 100, 0.5)).toBe(0);
    // Six decades of H-alpha come out as under two at power 0.3.
    expect(Math.log10(compressLight(1e6, 1, 0.3) / compressLight(1, 1, 0.3))).toBeCloseTo(1.8, 12);
  });

  it("takes its reference at a quantile of the positive values", () => {
    expect(quantile([0, -1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 0.9)).toBe(9);
    expect(quantile([], 0.9)).toBe(0);
  });

  it("keeps the brightest N, brightest first, ties by index", () => {
    expect(brightest([1, 5, 0, 5, 3], 3)).toEqual([1, 3, 4]);
    expect(brightest([1, 5, 0, 5, 3], 10)).toEqual([1, 3, 4, 0]);
  });
});

describe("the arm weight", () => {
  it("is min(1, (t / level)^power)", () => {
    expect(armWeight(0.8, 0.8, 3)).toBe(1);
    expect(armWeight(1, 0.8, 3)).toBe(1);
    expect(armWeight(0.4, 0.8, 3)).toBeCloseTo(0.125, 12);
    expect(armWeight(0, 0.8, 3)).toBe(0);
    expect(armWeight(0.1, 0.8, 0)).toBe(1);
  });

  // A grid of 2 R cells by 4 phi cells: the inner ring with contrast 0.5..2, the outer flat at 1.
  const data = new Float32Array(2 * 4 * 4);
  const contrast = [
    [0.5, 1],
    [1, 1],
    [2, 1],
    [1.5, 1],
  ];
  contrast.forEach((row, j) => row.forEach((c, i) => (data[(j * 2 + i) * 4 + 3] = c)));
  const placement: Placement = { data, width: 2, height: 4, rLo: 0, rHi: 2 };

  it("reads the contrast relative to its own ring, flat where the ring has none", () => {
    const ranges = ringRanges(placement);
    expect(Array.from(ranges)).toEqual([0.5, 2, 1, 1]);
    const at = (j: number) => ((j + 0.5) / 4) * 2 * Math.PI;
    expect(ringContrast(placement, ranges, 0.5, at(0), 0.05)).toBe(0);
    expect(ringContrast(placement, ranges, 0.5, at(2), 0.05)).toBe(1);
    expect(ringContrast(placement, ranges, 0.5, at(3), 0.05)).toBeCloseTo(2 / 3, 6);
    // phi wraps: -pi/4 is the last sector's.
    expect(ringContrast(placement, ranges, 0.5, at(3) - 2 * Math.PI, 0.05)).toBeCloseTo(2 / 3, 6);
    expect(ringContrast(placement, ranges, 1.5, at(2), 0.05)).toBe(0.05);
    expect(ringContrast(placement, ranges, 2.5, at(2), 0.05)).toBeNull();
  });

  it("and the radial fade: 1 inside, nothing past the width, fading in under the inner radius", () => {
    expect(radialWeight(5, 11, 3, 0)).toBe(1);
    expect(radialWeight(12.5, 11, 3, 0)).toBeCloseTo(0.5, 12);
    expect(radialWeight(14, 11, 3, 0)).toBe(0);
    expect(radialWeight(0.2, 11, 3, 1.5)).toBe(0);
    expect(radialWeight(1.5, 11, 3, 1.5)).toBe(1);
  });

  it("weights the regions' attributes, which are compacted to the regions drawn", () => {
    // Three regions on the inner ring at sectors 0, 2, 3, one past the grid.
    const at = (j: number) => ((j + 0.5) / 4) * 2 * Math.PI;
    const places = [
      [0.5, at(0)],
      [0.5, at(2)],
      [0.5, at(3)],
      [1.2, at(1)],
    ];
    const positions = new Float32Array(places.flatMap(([r, phi]) => [r * Math.cos(phi), 0, -r * Math.sin(phi)]));
    const flux = new Float32Array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]);
    const extent = new Float32Array([10, 10, 10, 10]);
    const local = { armPower: 1, armLevel: 1, armFlat: 0.5, fadeR: 30, fadeWidth: 1, innerR: 0, count: 10, lumPower: 1, pink: 0 };
    const a = regionAttributes({ positions, flux, extent }, local, placement);
    // Region 0 at t = 0 is not drawn; region 1 (t = 1) the brightest, then region 2 (t = 2/3), then region 3 (flat, 0.5).
    expect(a.order).toEqual([1, 2, 3]);
    expect(a.light[0]).toBeCloseTo(1, 5);
    expect(a.light[3]).toBeCloseTo(2 / 3, 5);
    expect(a.light[6]).toBeCloseTo(0.5, 5);
    expect(Array.from(a.positions.subarray(0, 3))).toEqual(Array.from(positions.subarray(3, 6)));
    expect(a.radius.length).toBe(3);
    // Without a placement every arm weight is 1.
    expect(regionAttributes({ positions, flux, extent }, local, null).order).toEqual([0, 1, 2, 3]);
  });
});

describe("the colour", () => {
  it("mixes the region's own colour toward the pink, at mean 1", () => {
    expect(regionColour([2, 2, 2], 0, 0).map((v) => +v.toFixed(12))).toEqual([1, 1, 1]);
    const pink = regionColour([1, 1, 1], 1, 0);
    pink.forEach((v, k) => expect(v).toBeCloseTo(PINK[k], 12));
    const half = regionColour([1, 1, 1], 0.5, 0);
    expect((half[0] + half[1] + half[2]) / 3).toBeCloseTo(1, 12);
    expect(half[0]).toBeGreaterThan(1);
    expect(CORE_COLOUR[2]).toBeGreaterThan(CORE_COLOUR[0]);
  });

  it("goes past the pink toward a deep red below 0 on the magenta slider, every channel positive to its end", () => {
    const red = regionColour([1, 1, 1], 1, -1);
    expect((red[0] + red[1] + red[2]) / 3).toBeCloseTo(1, 12);
    red.forEach((v) => expect(v).toBeGreaterThan(0));
    expect(red[2] / red[0]).toBeLessThan(PINK[2] / PINK[0]);
  });
});

describe("the hash and the shape", () => {
  it("is stable: the same index and salt give the same value, in [0, 1)", () => {
    expect(hash01(12345, 7)).toBe(hash01(12345, 7));
    expect(hash01(0, 0)).toBe(0);
    const seen = new Set<number>();
    for (let i = 1; i < 2000; i += 1) {
      const v = hash01(i, 3);
      expect(v).toBeGreaterThanOrEqual(0);
      expect(v).toBeLessThan(1);
      seen.add(v);
    }
    expect(seen.size).toBe(1999);
    // Its mean is about a half.
    let s = 0;
    for (let i = 0; i < 10000; i += 1) s += hash01(i, 11);
    expect(s / 10000).toBeGreaterThan(0.48);
    expect(s / 10000).toBeLessThan(0.52);
    expect(regionBlobs(42, 4, 1, 1)).toEqual(regionBlobs(42, 4, 1, 1));
  });

  it("gives each region its sub-blobs, weights summing to 1, the unused weighing nothing", () => {
    const b = regionBlobs(7, 2, 1, 1);
    expect(b.length).toBe(MAX_BLOBS);
    expect(b[0][3] + b[1][3]).toBeCloseTo(1, 12);
    expect(b[2][3]).toBe(0);
    expect(b[3][3]).toBe(0);
    expect(Math.hypot(b[0][0], b[0][1])).toBeLessThanOrEqual(0.25 + 1e-12);
    expect(Math.hypot(b[1][0], b[1][1])).toBeGreaterThanOrEqual(0.5 - 1e-12);
    const round = regionBlobs(7, 4, 0, 1);
    for (const blob of round) expect(Math.hypot(blob[0], blob[1])).toBe(0);
    expect(regionBlobs(7, 4, 1, 2)[0][2]).toBeCloseTo(2 * regionBlobs(7, 4, 1, 1)[0][2], 12);
  });
});

describe("the feature", () => {
  it("registers, draws in place of the knots by default, and every default lies in its control's range", () => {
    expect(features()).toContain(knots);
    expect(knots.layer).toBeDefined();
    for (const template of [null, "milky_way", "ngc_4414"]) {
      const d = illDefaults(template);
      for (const c of knots.controls) {
        const v = d[illKey(knots, c)];
        expect(v).toBeGreaterThanOrEqual(c.min);
        expect(v).toBeLessThanOrEqual(c.max);
        expect(c.about).toMatch(/Illustrative|appearance/);
        if (c.log) expect(c.min).toBeGreaterThan(0);
      }
    }
    expect(knots.replacesKnots?.({ draw: 1 })).toBe(true);
    expect(knots.replacesKnots?.({ draw: 0 })).toBe(false);
    expect(new Set(knots.controls.map((c) => c.key)).size).toBe(knots.controls.length);
  });
});
