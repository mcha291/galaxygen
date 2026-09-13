import { describe, expect, it } from "vitest";

import { RATIO_FLOOR, heightOf, timeAt } from "./timeline";

describe("heightOf", () => {
  it("is log from the floor to an equal-mass merger", () => {
    expect(heightOf(1)).toBe(1);
    expect(heightOf(RATIO_FLOOR)).toBe(0);
    expect(heightOf(0.1)).toBeCloseTo(2 / 3, 12);
  });

  it("keeps a minor merger tall enough to grab", () => {
    expect(heightOf(0.02)).toBeGreaterThan(0.4);
  });
});

describe("timeAt", () => {
  it("clamps to the time axis and rounds to 0.05 Gyr", () => {
    expect(timeAt(0.5, 13.8)).toBe(6.9);
    expect(timeAt(-1, 13.8)).toBe(0);
    expect(timeAt(2, 13.8)).toBe(13.8);
    expect(timeAt(0.2757, 13.8)).toBe(3.8);
  });
});
