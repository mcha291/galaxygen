import { describe, expect, it } from "vitest";

import { psfProfile } from "./psf";

describe("psfProfile", () => {
  it("is brightest at the centre and zero at the edge", () => {
    expect(psfProfile(0)).toBeCloseTo(1, 6);
    expect(psfProfile(1)).toBe(0);
  });

  it("falls monotonically, with wings wider than the core", () => {
    const samples = Array.from({ length: 21 }, (_, i) => psfProfile(i / 20));
    for (let i = 1; i < samples.length; i += 1) expect(samples[i]).toBeLessThanOrEqual(samples[i - 1]);
    const gaussOnly = (r: number) => Math.exp(-(r * r) / (2 * 0.3 ** 2)) * (1 - r) ** 2;
    expect(psfProfile(0.8)).toBeGreaterThan(gaussOnly(0.8)); // far out, the Moffat wing lifts it above a pure Gaussian
  });
});
