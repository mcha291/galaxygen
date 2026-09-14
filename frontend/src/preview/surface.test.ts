import { describe, expect, it } from "vitest";

import { contourLevels, contourRings, heightAxisLabel, heightOf, heightScaleOf, polarSurface } from "./surface";

/** Σ = Σ₀ exp(-R/h) on a 0–30 kpc grid, the shape every checkpoint-1 profile has. */
function exponentialDisc(h: number, n = 400, rMax = 30): { profile: Float64Array; radii: Float64Array } {
  const profile = new Float64Array(n);
  const radii = new Float64Array(n);
  for (let i = 0; i < n; i += 1) {
    radii[i] = ((i + 0.5) / n) * rMax;
    profile[i] = 1000 * Math.exp(-radii[i] / h);
  }
  return { profile, radii };
}

describe("heightScaleOf", () => {
  it("goes log for a profile spanning more than a decade", () => {
    const { profile } = exponentialDisc(2.6);
    expect(heightScaleOf(profile)?.log).toBe(true);
  });

  it("stays linear for a shallow one", () => {
    expect(heightScaleOf([10, 11, 12, 13])?.log).toBe(false);
  });

  it("floors at four decades, so the outskirts sit on the base and do not fall through", () => {
    const { profile } = exponentialDisc(2.6);
    const scale = heightScaleOf(profile)!;
    expect(Math.log10(scale.hi / scale.lo)).toBeLessThanOrEqual(5);
    expect(heightOf(profile[profile.length - 1], scale)).toBe(0);
  });

  it("returns null rather than a scale for an empty or non-positive profile", () => {
    expect(heightScaleOf([])).toBeNull();
    expect(heightScaleOf([0, -1, Number.NaN])).toBeNull();
  });
});

describe("heightOf", () => {
  it("spans [0, 1] and clamps outside", () => {
    const scale = { lo: 1, hi: 1000, log: true };
    expect(heightOf(1, scale)).toBeCloseTo(0);
    expect(heightOf(1000, scale)).toBeCloseTo(1);
    expect(heightOf(1e6, scale)).toBe(1);
    expect(heightOf(1e-6, scale)).toBe(0);
  });

  it("puts a decade at a third of the height on a three-decade scale", () => {
    expect(heightOf(10, { lo: 1, hi: 1000, log: true })).toBeCloseTo(1 / 3, 6);
  });
});

describe("contourRings", () => {
  // The claim the rings are drawn for: on an exponential disc, log-spaced
  // contours land at evenly spaced radii, so the ring spacing IS the scale
  // length and can be read off the picture without a colour bar.
  it("spaces rings evenly for an exponential disc, at the scale length", () => {
    const h = 2.6;
    const { profile, radii } = exponentialDisc(h);
    const scale = heightScaleOf(profile)!;
    const rings = contourRings(profile, radii, contourLevels(scale, 2));
    expect(rings.length).toBeGreaterThan(3);

    const gaps: number[] = [];
    for (let i = 1; i < rings.length; i += 1) gaps.push(rings[i].radius - rings[i - 1].radius);
    const mean = gaps.reduce((a, b) => a + b, 0) / gaps.length;
    for (const g of gaps) expect(Math.abs(g - mean) / mean).toBeLessThan(0.02);

    // Half a decade of Σ is ln(10)/2 × h in radius for an exponential.
    expect(mean).toBeCloseTo((Math.LN10 / 2) * h, 1);
  });

  it("comes back innermost first, with the level falling outward", () => {
    const { profile, radii } = exponentialDisc(2.6);
    const scale = heightScaleOf(profile)!;
    const rings = contourRings(profile, radii, contourLevels(scale, 2));
    for (let i = 1; i < rings.length; i += 1) {
      expect(rings[i].radius).toBeGreaterThan(rings[i - 1].radius);
      expect(rings[i].level).toBeLessThan(rings[i - 1].level);
    }
  });

  it("keeps only the outermost crossing, so a bump does not draw a ring inside a ring", () => {
    const profile = [10, 5, 8, 5, 1];
    const radii = [0, 1, 2, 3, 4];
    const rings = contourRings(profile, radii, [5]);
    expect(rings).toHaveLength(1);
    expect(rings[0].radius).toBeGreaterThan(2);
  });

  it("drops levels the profile never reaches", () => {
    const { profile, radii } = exponentialDisc(2.6);
    expect(contourRings(profile, radii, [1e9])).toHaveLength(0);
  });
});

describe("contourLevels", () => {
  it("gives the asked-for number per decade", () => {
    const levels = contourLevels({ lo: 1, hi: 1000, log: true }, 2);
    for (let i = 1; i < levels.length; i += 1) expect(levels[i] / levels[i - 1]).toBeCloseTo(10 ** 0.5, 6);
  });

  it("stays inside the scale", () => {
    const scale = { lo: 1, hi: 1000, log: true };
    for (const v of contourLevels(scale, 2)) {
      expect(v).toBeGreaterThanOrEqual(scale.lo);
      expect(v).toBeLessThanOrEqual(scale.hi);
    }
  });
});

describe("polarSurface", () => {
  it("builds a closed surface of revolution with the right vertex and index counts", () => {
    const { profile, radii } = exponentialDisc(2.6, 40);
    const scale = heightScaleOf(profile)!;
    const mesh = polarSurface(profile, radii, scale, 32);
    expect(mesh.positions).toHaveLength(40 * 32 * 3);
    expect(mesh.indices).toHaveLength((40 - 1) * 32 * 6);
    expect(Math.max(...mesh.indices)).toBeLessThan(40 * 32);
  });

  it("is axisymmetric: every vertex on a ring shares a height and a radius", () => {
    const { profile, radii } = exponentialDisc(2.6, 20);
    const scale = heightScaleOf(profile)!;
    const mesh = polarSurface(profile, radii, scale, 16);
    for (let i = 0; i < 20; i += 1) {
      const base = i * 16 * 3;
      const z = mesh.positions[base + 2];
      for (let j = 1; j < 16; j += 1) {
        const k = base + j * 3;
        expect(mesh.positions[k + 2]).toBeCloseTo(z, 6);
        expect(Math.hypot(mesh.positions[k], mesh.positions[k + 1])).toBeCloseTo(radii[i], 4);
      }
    }
  });
});

describe("heightAxisLabel", () => {
  it("says log when the height is log, because then it is not proportional to the quantity", () => {
    expect(heightAxisLabel("Σ", "M☉/pc²", { lo: 1, hi: 1e4, log: true })).toBe("log₁₀ Σ (M☉/pc²)");
    expect(heightAxisLabel("Σ", "M☉/pc²", { lo: 0, hi: 10, log: false })).toBe("Σ (M☉/pc²)");
  });
});
