import { describe, expect, it } from "vitest";

import { FIELD_SIGMA, LEVEL_KPC, OCTAVE_NORM, OCTAVE_SIGMA, cloudSeed, densityRatio, hash3, levelFor, unitField, valueNoise } from "./region";
import { REGIME_KPC } from "./regimes";

describe("the level the view asks for", () => {
  it("is 0 above the stars handover and one level per factor four below it", () => {
    expect(LEVEL_KPC[0]).toBe(REGIME_KPC.stars);
    expect(levelFor(30)).toBe(0);
    expect(levelFor(4)).toBe(0);
    expect(levelFor(3.9)).toBe(1);
    expect(levelFor(0.9)).toBe(2);
    expect(levelFor(0.2)).toBe(3);
    expect(levelFor(0.001)).toBe(3);
    for (let k = 1; k < LEVEL_KPC.length; k += 1) expect(LEVEL_KPC[k - 1] / LEVEL_KPC[k]).toBeCloseTo(4, 12);
  });
});

describe("the seeded noise", () => {
  it("is deterministic in its arguments and differs between seeds", () => {
    expect(hash3(3, 4, 5, 77)).toBe(hash3(3, 4, 5, 77));
    expect(hash3(3, 4, 5, 77)).not.toBe(hash3(3, 4, 5, 78));
    expect(valueNoise(0.3, 0.7, 0.1, 9)).toBe(valueNoise(0.3, 0.7, 0.1, 9));
    expect(unitField(0.3, 0.7, 0.1, 9)).toBe(unitField(0.3, 0.7, 0.1, 9));
    expect(unitField(0.3, 0.7, 0.1, 9)).not.toBe(unitField(0.3, 0.7, 0.1, 10));
    // a cloud's seed is its (cell, index) path, and distinct paths give distinct seeds
    expect(cloudSeed(300, 5)).toBe(cloudSeed(300, 5));
    expect(cloudSeed(300, 5)).not.toBe(cloudSeed(301, 5));
    expect(cloudSeed(300, 5)).not.toBe(cloudSeed(300, 6));
  });

  it("has the stated single-octave spread, zero mean and unit variance when summed", () => {
    // Sampled on a fine grid over many lattice cells: the constants the field is normalised by.
    let n = 0, s1 = 0, s2 = 0, u1 = 0, u2 = 0;
    for (let i = 0; i < 40; i += 1) for (let j = 0; j < 40; j += 1) for (let k = 0; k < 40; k += 1) {
      const x = i * 0.37 + 0.13, y = j * 0.29 + 0.41, z = k * 0.43 + 0.07;
      const v = valueNoise(x, y, z, 5) - 0.5;
      const g = unitField(x, y, z, 5);
      n += 1; s1 += v; s2 += v * v; u1 += g; u2 += g * g;
    }
    const sigma = Math.sqrt(s2 / n - (s1 / n) ** 2);
    expect(sigma).toBeCloseTo(OCTAVE_SIGMA, 2);
    expect(Math.abs(u1 / n)).toBeLessThan(0.03);
    expect(Math.sqrt(u2 / n - (u1 / n) ** 2)).toBeCloseTo(1, 1);
    expect(OCTAVE_NORM).toBeCloseTo(Math.sqrt(85 / 64), 12);
    // the measured field spread sits within 2% of the independent-octave figure
    expect(FIELD_SIGMA / (OCTAVE_SIGMA * OCTAVE_NORM)).toBeGreaterThan(0.98);
    expect(FIELD_SIGMA / (OCTAVE_SIGMA * OCTAVE_NORM)).toBeLessThan(1.02);
  });

  it("realises the published log-normal: the density ratio's mean is 1 and its log's spread is sigma_s", () => {
    for (const sigmaS of [0.8, 1.4, 2.0]) {
      let n = 0, m1 = 0, l1 = 0, l2 = 0;
      for (let i = 0; i < 40; i += 1) for (let j = 0; j < 40; j += 1) for (let k = 0; k < 40; k += 1) {
        const x = i * 0.37 + 0.13, y = j * 0.29 + 0.41, z = k * 0.43 + 0.07;
        const rho = densityRatio(x, y, z, 11, sigmaS, 0, 0);
        const l = Math.log(rho);
        n += 1; m1 += rho; l1 += l; l2 += l * l;
      }
      // the mean of exp(sigma g - sigma^2/2) is 1 for a Gaussian g; the octave sum is close to one
      expect(m1 / n).toBeGreaterThan(0.8);
      expect(m1 / n).toBeLessThan(1.25);
      expect(Math.sqrt(l2 / n - (l1 / n) ** 2)).toBeCloseTo(sigmaS, 1);
      expect(l1 / n).toBeCloseTo(-0.5 * sigmaS * sigmaS, 1);
    }
  });

  it("tilts the mean along the gradient and never below the floor", () => {
    const up = densityRatio(0.9, 0, 0, 3, 0.001, 0.5, 0);
    const down = densityRatio(-0.9, 0, 0, 3, 0.001, 0.5, 0);
    expect(up).toBeGreaterThan(down);
    expect(densityRatio(-1, 0, 0, 3, 0.001, 5, 0)).toBeGreaterThan(0);
  });
});
