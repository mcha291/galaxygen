import { describe, expect, it } from "vitest";

import type { Axis } from "./axes";
import { arrivedSpread, cellOf, deliveredBy, radialTransport, ringLevels, ringRadius, valueAt } from "./mergers";

const T: Axis = { lo: 0, hi: 10, n: 10, width: 1 } as Axis;

/** A two-radius spread field for major mergers at 3.5 and 6.5 Gyr of rms a and b. */
function spreadFor(a: number, b: number): Float64Array {
  const out = new Float64Array(2 * T.n);
  for (let i = 0; i < 2; i += 1) {
    for (let j = 0; j < T.n; j += 1) {
      const centre = j + 0.5;
      const s2 = (centre <= 3.5 ? a * a : 0) + (centre <= 6.5 ? b * b : 0);
      out[i * T.n + j] = Math.sqrt(s2) * (i + 1);
    }
  }
  return out;
}

describe("cellOf and valueAt", () => {
  it("reads the cell holding tau, clamped", () => {
    expect(cellOf(2.3, T)).toBe(2);
    expect(cellOf(-1, T)).toBe(0);
    expect(cellOf(99, T)).toBe(9);
    expect(valueAt([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 7.9, T)).toBe(7);
  });
});

describe("arrivedSpread", () => {
  const spread = spreadFor(3, 4);

  it("is zero before any merger has landed", () => {
    expect(Array.from(arrivedSpread(spread, 2, T, 1))).toEqual([0, 0]);
  });

  it("carries only the first merger between the two", () => {
    const s = arrivedSpread(spread, 2, T, 5);
    expect(s[0]).toBeCloseTo(3, 9);
    expect(s[1]).toBeCloseTo(6, 9); // the outer radius scatters twice as far
  });

  it("carries both, in quadrature, once both have landed", () => {
    const s = arrivedSpread(spread, 2, T, 9.9);
    expect(s[0]).toBeCloseTo(5, 9);
  });
});

describe("radialTransport", () => {
  const n = 120;
  const radii = Float64Array.from({ length: n }, (_, i) => (i + 0.5) * 0.25);
  const profile = Float64Array.from(radii, (r) => 800 * Math.exp(-r / 2.6));
  const massOf = (p: ArrayLike<number>) => Array.from(p).reduce((sum, v, i) => sum + v * radii[i], 0);

  it("leaves the disc alone where there is no scatter", () => {
    const out = radialTransport(profile, radii, 0.25, new Float64Array(n));
    out.forEach((v, i) => expect(v).toBeCloseTo(profile[i], 9));
  });

  it("conserves mass and moves it outward from a centrally concentrated disc", () => {
    const width = Float64Array.from(radii, (r) => 0.2 * r);
    const out = radialTransport(profile, radii, 0.25, width);
    expect(massOf(out) / massOf(profile)).toBeCloseTo(1, 9);
    expect(out[n - 20]).toBeGreaterThan(profile[n - 20]);
  });
});

describe("deliveredBy", () => {
  it("sums the rate over whole and partial cells", () => {
    const rate = [0, 0, 0.5, 0.5, 0, 0, 0, 0, 0, 0];
    expect(deliveredBy(rate, T, 2)).toBe(0);
    expect(deliveredBy(rate, T, 3.5)).toBeCloseTo(0.75, 9);
    expect(deliveredBy(rate, T, 10)).toBeCloseTo(1, 9);
  });
});

describe("rings", () => {
  const radii = Float64Array.from({ length: 400 }, (_, i) => (i + 0.5) * 0.075);
  const profile = Float64Array.from(radii, (r) => 900 * Math.exp(-r / 2.6));

  it("picks whole decades below the top one, inside the range", () => {
    expect(ringLevels(profile)).toEqual([10, 1, 0.1, 0.01]);
    expect(ringLevels(profile, 2)).toEqual([10, 1]);
    expect(ringLevels([0, Number.NaN])).toEqual([]);
  });

  it("finds a decade of an exponential disc one ln(10) scale length further out", () => {
    const r10 = ringRadius(profile, radii, 10)!;
    const r1 = ringRadius(profile, radii, 1)!;
    expect(r1 - r10).toBeCloseTo(Math.LN10 * 2.6, 2);
    expect(ringRadius(profile, radii, 1e6)).toBeNull();
  });

  it("moves outward once the disc has been scattered", () => {
    const moved = radialTransport(profile, radii, 0.075, Float64Array.from(radii, (r) => 0.15 * r));
    expect(ringRadius(moved, radii, 1)!).toBeGreaterThan(ringRadius(profile, radii, 1)!);
  });
});