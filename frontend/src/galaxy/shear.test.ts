import { describe, expect, it } from "vitest";

import { RAD_PER_MYR_PER_KMS_PER_KPC, interp, omegas, periodMyr, spokeSegments } from "./shear";

const R = [1, 2, 4, 8];
const FLAT = [220, 220, 220, 220];

describe("interp", () => {
  it("interpolates between grid points and clamps outside", () => {
    expect(interp(3, [2, 4], [100, 200])).toBe(150);
    expect(interp(0, R, [1, 2, 3, 4])).toBe(1);
    expect(interp(99, R, [1, 2, 3, 4])).toBe(4);
  });
});

describe("the unit conversion", () => {
  it("gives the Sun's orbit about 225 Myr at 220 km/s and 8 kpc", () => {
    expect(periodMyr(8, R, FLAT)).toBeCloseTo((2 * Math.PI) / ((220 / 8) * RAD_PER_MYR_PER_KMS_PER_KPC), 6);
    expect(periodMyr(8, R, FLAT)).toBeGreaterThan(220);
    expect(periodMyr(8, R, FLAT)).toBeLessThan(230);
  });
});

describe("omegas", () => {
  it("falls as 1/r for a flat curve: the inner disc turns faster", () => {
    const w = omegas([2, 4], R, FLAT);
    expect(w[0] / w[1]).toBeCloseTo(2, 9);
  });
});

describe("spokeSegments", () => {
  it("starts as straight radial lines in the stars' frame", () => {
    const radii = [1, 2];
    const seg = spokeSegments(radii, omegas(radii, R, FLAT), 4, 0);
    expect(seg.length).toBe(4 * 1 * 2 * 3);
    // spoke 0 lies along +x; spoke 1 (φ = π/2) along −z
    [1, 0, 0, 2, 0, 0].forEach((want, i) => expect(seg[i]).toBeCloseTo(want, 9));
    expect(seg[8]).toBeCloseTo(-1, 9);
    expect(seg[11]).toBeCloseTo(-2, 9);
  });

  it("drapes over a surface when given one height per radius", () => {
    const radii = [1, 2];
    const seg = spokeSegments(radii, omegas(radii, R, FLAT), 1, 0, [5, 3]);
    expect(seg[1]).toBe(5);
    expect(seg[4]).toBe(3);
  });

  it("winds: after time t the inner point has turned further than the outer", () => {
    const radii = [2, 4];
    const w = omegas(radii, R, FLAT);
    const seg = spokeSegments(radii, w, 1, 10); // short enough that neither angle wraps
    const inner = Math.atan2(-seg[2], seg[0]);
    const outer = Math.atan2(-seg[5], seg[3]);
    expect(inner).toBeCloseTo(w[0] * 10, 6);
    expect(inner).toBeGreaterThan(outer);
  });
});
