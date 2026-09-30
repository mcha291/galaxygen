import { describe, expect, it } from "vitest";

import {
  BUDGET,
  ERG_S_CM3_TO_LSUN_PC3,
  FIELD_SIGMA,
  KIND,
  LEVEL_KPC,
  MAG_PER_TAU,
  OBJECT_FLOATS,
  OCTAVE_NORM,
  OCTAVE_SIGMA,
  cloudSeed,
  densityRatio,
  hash3,
  levelFor,
  packObjects,
  regionLineColour,
  sortedFrom,
  unitField,
  valueNoise,
} from "./region";
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

describe("the region's object table", () => {
  const clouds = {
    cloud_radius: [8, 8.1], cloud_azimuth: [0, 0.01], cloud_height: [0, 0.01], cloud_size: [10, 20], cloud_mass: [1e5, 2e5],
    cloud_density_pdf_width: [1.4, 1.2], cloud_density_gradient: [0.3, 0.1], cloud_gradient_angle: [0.5, 1],
    cloud_cluster_index: [0, -1], cell: [300, 300], index: [0, 1],
  };
  const clusters = {
    cluster_radius: [8.001], cluster_azimuth: [0], cluster_height: [0], hii_stromgren_radius: [2], hii_halpha_emissivity: [1e-20],
    bubble_radius: [9], bubble_shell_thickness: [1.5], bubble_shell_emissivity: [2e-21], cell: [300], index: [0],
  };

  it("packs clouds, regions and shells with their units and cavities", () => {
    const t = packObjects(clouds, clusters, 2.9696);
    expect(t.count).toBe(4);
    // the heaviest cloud first: the 2e5 one, radius 20 pc
    expect(t.data[3]).toBeCloseTo(0.02, 6);
    expect(t.data[4]).toBe(KIND.cloud);
    // kappa_V: the central tau over the diameter, per kpc
    expect(t.data[10]).toBeCloseTo(2.9696 / MAG_PER_TAU / 0.04, 2);
    // the 1e5 cloud (second) carries its cluster's cavity: 2 pc at the cluster
    const second = OBJECT_FLOATS;
    expect(t.data[second + 15]).toBeCloseTo(0.002, 6);
    expect(t.data[second + 12]).toBeCloseTo(8.001, 5);
    // an HII sphere and a shell, emissivities in Lsun/pc^3 (float32 storage)
    const hii = 2 * OBJECT_FLOATS;
    expect(t.data[hii + 4]).toBe(KIND.hii);
    expect(t.data[hii + 8] / (1e-20 * ERG_S_CM3_TO_LSUN_PC3)).toBeCloseTo(1, 5);
    expect(t.data[3 * OBJECT_FLOATS + 4]).toBe(KIND.shell);
    expect(t.data[3 * OBJECT_FLOATS + 9]).toBeCloseTo(0.0015, 6);
    expect(t.min[0]).toBeLessThan(8);
    expect(t.max[0]).toBeGreaterThan(8);
  });

  it("colours a region by all its lines through the filters (S42)", () => {
    const withLines = {
      ...clusters, hii_balmer_decrement: [2.86], hii_oiii_5007_ratio: [0.5], hii_nii_6583_ratio: [0.2],
      hii_sii_6716_ratio: [0.05], hii_sii_6731_ratio: [Number.NaN],
    };
    // The Hubble palette in miniature: [S II] in red, Halpha in green, [O III] in blue; Hbeta and [N II] in none.
    const lines = {
      halpha: [0, 1, 0], hbeta: [0, 0, 0], oiii_5007: [0, 0, 1], nii_6583: [0, 0, 0], sii_6716: [1, 0, 0], sii_6731: [1, 0, 0],
    } as const;
    expect(regionLineColour(withLines, 0, lines)).toEqual([0.05, 1, 0.5]); // a NaN ratio adds nothing
    // Through one broad filter every line adds: 1 + 1/2.86 + 0.5 + 0.2 + 0.05.
    const broad = { halpha: [1, 1, 1], hbeta: [1, 1, 1], oiii_5007: [1, 1, 1], nii_6583: [1, 1, 1], sii_6716: [1, 1, 1] } as const;
    expect(regionLineColour(withLines, 0, broad)[0]).toBeCloseTo(1 + 1 / 2.86 + 0.75, 12);
    const t = packObjects(clouds, withLines, 2.9696, undefined, {}, lines);
    const hii = 2 * OBJECT_FLOATS;
    expect(t.data[hii + 4]).toBe(KIND.hii);
    expect(Array.from(t.data.slice(hii + 9, hii + 12)).map((v) => Number(v.toFixed(6)))).toEqual([0.05, 1, 0.5]);
    // Without line weights a region is its Halpha alone, in every channel (the default).
    expect(Array.from(packObjects(clouds, clusters, 2.9696).data.slice(hii + 9, hii + 12))).toEqual([1, 1, 1]);
  });

  it("draws a remnant's shell and skips a Sedov-phase remnant's NaN emissivity", () => {
    const remnants = {
      remnant_radius: [8, 8.2], remnant_azimuth: [0.1, 0.2], remnant_height: [0, 0], remnant_size: [18, 5],
      remnant_shell_thickness: [1.2, 0.5], remnant_shell_emissivity: [5e-22, Number.NaN], cell: [300, 301], index: [0, 0],
    };
    const t = packObjects(clouds, clusters, 2.9696, undefined, remnants);
    expect(t.count).toBe(5); // two clouds, one region, the bubble's shell and the radiative remnant's
    const kinds = Array.from({ length: t.count }, (_, k) => t.data[k * OBJECT_FLOATS + 4]);
    expect(kinds.filter((k) => k === KIND.shell).length).toBe(2);
  });

  it("keeps the budget and sorts nearest-first", () => {
    const n = 300;
    const many = {
      cloud_radius: Array(n).fill(8), cloud_azimuth: Array.from({ length: n }, (_, i) => i * 1e-3), cloud_height: Array(n).fill(0),
      cloud_size: Array(n).fill(5), cloud_mass: Array.from({ length: n }, (_, i) => i + 1), cloud_density_pdf_width: Array(n).fill(1),
      cloud_density_gradient: Array(n).fill(0), cloud_gradient_angle: Array(n).fill(0), cloud_cluster_index: Array(n).fill(-1),
      cell: Array(n).fill(1), index: Array.from({ length: n }, (_, i) => i),
    };
    const t = packObjects(many, { cluster_radius: [] }, 3);
    expect(t.count).toBe(BUDGET.clouds);
    expect(t.data[6]).toBe(n - 1); // the heaviest kept first
    const out = sortedFrom(t, [8, 0, -0.3], new Float32Array(t.data.length));
    const dist = (k: number) => Math.hypot(out[k * OBJECT_FLOATS] - 8, out[k * OBJECT_FLOATS + 1], out[k * OBJECT_FLOATS + 2] + 0.3);
    expect(dist(0)).toBeLessThanOrEqual(dist(1));
    expect(dist(1)).toBeLessThanOrEqual(dist(t.count - 1));
  });
});
