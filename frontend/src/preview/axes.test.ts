import { describe, expect, it } from "vitest";

import { centres, linearTicks, logTicks, position, rangeOf } from "./axes";

describe("centres", () => {
  it("is the middle of each cell", () => {
    expect(Array.from(centres({ unit: "kpc", unit_display: "kpc", n: 4, lo: 0, hi: 2, width: 0.5 }))).toEqual([0.25, 0.75, 1.25, 1.75]);
  });
});

describe("linearTicks", () => {
  it("steps by 1, 2 or 5 × 10^k", () => {
    expect(linearTicks(0, 30, 3)).toEqual([0, 10, 20, 30]);
    expect(linearTicks(0, 250, 5)).toEqual([0, 50, 100, 150, 200, 250]);
    expect(linearTicks(-0.6, 0.35, 4)).toEqual([-0.6, -0.4, -0.2, 0, 0.2]);
  });
});

describe("logTicks", () => {
  it("puts one tick on each decade", () => {
    expect(logTicks(0.1, 1000)).toEqual([0.1, 1, 10, 100, 1000]);
  });
});

describe("rangeOf", () => {
  it("skips non-finite values, and non-positive ones on a log axis", () => {
    expect(rangeOf([[NaN, 1, 5]], false)).toEqual({ lo: 0, hi: 5 });
    expect(rangeOf([[0, -1, 3, 300]], true)).toEqual({ lo: 1, hi: 1000 });
  });

  it("keeps an offset profile off zero when zero is far away", () => {
    expect(rangeOf([[200, 240]], false)).toEqual({ lo: 200, hi: 240 });
  });

  it("pads a flat series and has no range for an empty one", () => {
    expect(rangeOf([[3, 3]], false)).toEqual({ lo: 2.85, hi: 3.15 });
    expect(rangeOf([[NaN]], false)).toBeNull();
  });
});

describe("position", () => {
  it("is linear or logarithmic", () => {
    expect(position(5, { lo: 0, hi: 10 }, false)).toBe(0.5);
    expect(position(10, { lo: 1, hi: 100 }, true)).toBeCloseTo(0.5, 12);
  });
});
