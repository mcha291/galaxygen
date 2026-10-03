import { createHash } from "node:crypto";

import { describe, expect, it } from "vitest";

import {
  BUDGET,
  CLOUD_SAMPLES,
  ERG_S_CM3_TO_LSUN_PC3,
  FIELD_SIGMA_MEASURED,
  INTERIOR_KEY,
  type InteriorNoise,
  KIND,
  LEVEL_KPC,
  MAG_PER_TAU,
  MAX_OBJECTS,
  OBJECT_FLOATS,
  OCTAVE_SIGMA,
  cloudInterior,
  cloudSeed,
  densityRatio,
  glslFloat,
  hash3,
  interiorNoise,
  interiorOf,
  levelFor,
  octaveNorm,
  packObjects,
  regionFragment,
  regionLineColour,
  sortedFrom,
  unitField,
  valueNoise,
} from "./region";
import { REGIME_KPC } from "./regimes";

// What `/api/clouds`' header carries (S55, D214 §5 as gate G1 ruled it): the interior noise's three parameters
// under `cloud_interior` - constants of the model, the same with the layer on and off, and no stage's scalars -
// beside the census's scalars. A fixture of the route's shape: the viewer's interior is evaluated with whatever
// arrives, and these are the values the pins below were computed at (JSON's 2.0 is the number 2).
const INTERIOR = { octaves: 4, lacunarity: 2.0, gain: 0.5 };
const PUBLISHED = { layer: "on", scalars: { cloud_extinction_v: 2.9696 }, cloud_interior: INTERIOR };
const NOISE = interiorNoise(interiorOf(PUBLISHED))!;

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
    expect(unitField(0.3, 0.7, 0.1, 9, NOISE)).toBe(unitField(0.3, 0.7, 0.1, 9, NOISE));
    expect(unitField(0.3, 0.7, 0.1, 9, NOISE)).not.toBe(unitField(0.3, 0.7, 0.1, 10, NOISE));
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
      const g = unitField(x, y, z, 5, NOISE);
      n += 1; s1 += v; s2 += v * v; u1 += g; u2 += g * g;
    }
    const sigma = Math.sqrt(s2 / n - (s1 / n) ** 2);
    expect(sigma).toBeCloseTo(OCTAVE_SIGMA, 2);
    expect(Math.abs(u1 / n)).toBeLessThan(0.03);
    expect(Math.sqrt(u2 / n - (u1 / n) ** 2)).toBeCloseTo(1, 1);
    // the independent-octave figure, derived from the published count and gain: sqrt(1 + 1/4 + 1/16 + 1/64)
    expect(octaveNorm(NOISE)).toBe(Math.sqrt(1 + 1 / 4 + 1 / 16 + 1 / 64));
    expect(octaveNorm(NOISE)).toBeCloseTo(Math.sqrt(85 / 64), 12);
    // the measured field spread sits within 2% of the independent-octave figure, for the set it was measured for
    expect(NOISE.sigma).toBe(FIELD_SIGMA_MEASURED.sigma);
    expect(NOISE.sigma / (OCTAVE_SIGMA * octaveNorm(NOISE))).toBeGreaterThan(0.98);
    expect(NOISE.sigma / (OCTAVE_SIGMA * octaveNorm(NOISE))).toBeLessThan(1.02);
  });

  it("realises the published log-normal: the density ratio's mean is 1 and its log's spread is sigma_s", () => {
    for (const sigmaS of [0.8, 1.4, 2.0]) {
      let n = 0, m1 = 0, l1 = 0, l2 = 0;
      for (let i = 0; i < 40; i += 1) for (let j = 0; j < 40; j += 1) for (let k = 0; k < 40; k += 1) {
        const x = i * 0.37 + 0.13, y = j * 0.29 + 0.41, z = k * 0.43 + 0.07;
        const rho = densityRatio(x, y, z, 11, sigmaS, 0, 0, NOISE);
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
    const up = densityRatio(0.9, 0, 0, 3, 0.001, 0.5, 0, NOISE);
    const down = densityRatio(-0.9, 0, 0, 3, 0.001, 0.5, 0, NOISE);
    expect(up).toBeGreaterThan(down);
    expect(densityRatio(-1, 0, 0, 3, 0.001, 5, 0, NOISE)).toBeGreaterThan(0);
  });
});

describe("the cloud interior's parameters are the model's (S55, D214 section 5; rule D5 as amended)", () => {
  it("reads the three from the clouds header's cloud_interior and fills nothing in", () => {
    expect(INTERIOR_KEY).toBe("cloud_interior");
    expect(interiorOf(PUBLISHED)).toEqual({ octaves: 4, lacunarity: 2, gain: 0.5 });
    // the header as the wire carries it, parsed: {"octaves": 4, "lacunarity": 2.0, "gain": 0.5}
    expect(interiorOf(JSON.parse('{"layer": "off", "cloud_interior": {"octaves": 4, "lacunarity": 2.0, "gain": 0.5}}'))).toEqual({ octaves: 4, lacunarity: 2, gain: 0.5 });
    // whatever the model publishes is what is read: another set arrives as itself
    expect(interiorOf({ cloud_interior: { octaves: 6, lacunarity: 2.5, gain: 0.4 } })).toEqual({ octaves: 6, lacunarity: 2.5, gain: 0.4 });
    // an API that publishes none, and a number that is not there, is not invented
    expect(interiorOf({ layer: "on", scalars: { cloud_extinction_v: 2.9696 } })).toBeNull();
    expect(interiorOf(undefined)).toBeNull();
    expect(interiorOf(null)).toBeNull();
    for (const carried of [null, 4, "4, 2, 0.5", [4, 2, 0.5], {}]) expect(interiorOf({ cloud_interior: carried })).toBeNull();
    for (const [key, bad] of [
      ["octaves", 3.5], ["octaves", 0], ["octaves", "4"], ["octaves", undefined], ["lacunarity", Number.NaN],
      ["lacunarity", 0], ["gain", -0.5], ["gain", Number.POSITIVE_INFINITY], ["gain", null],
    ] as const) {
      expect(interiorOf({ ...PUBLISHED, cloud_interior: { ...INTERIOR, [key]: bad } })).toBeNull();
    }
  });

  it("does not read the shape that is gone: the three among the header's scalars are not parameters", () => {
    // For a few commits of S55 the three were a layer stage's scalars; gate G1 made them constants under their own
    // key. One shape is read, not both: a header of the old shape publishes, to this viewer, no interior noise.
    const old = { layer: "on", scalars: { cloud_extinction_v: 2.9696, cloud_interior_octaves: 4, cloud_interior_lacunarity: 2, cloud_interior_gain: 0.5 } };
    expect(interiorOf(old)).toBeNull();
    expect(interiorOf(old.scalars)).toBeNull();
    expect(cloudInterior(false, old)).toEqual({ noise: null, note: expect.stringMatching(/publishes no cloud-interior noise \(\/api\/clouds' header carries no cloud_interior\)/) });
  });

  it("reproduces, to the bit, what the viewer drew while the parameters were its own", () => {
    // Computed at S55 before any code moved, from region.ts as S54 left it (OCTAVES 4, frequencies doubling,
    // weights halving, FIELD_SIGMA 0.2088): the same points through the published parameters are the same float64s.
    const field: [number, number, number, number, number][] = [
      [0.3, 0.7, 0.1, 9, 0.4807823754651735],
      [-0.62, 0.15, 0.48, 9830405, -0.5778688569543368],
      [0.9, -0.2, -0.75, 9830400, 1.1898472214024067],
      [0.013, 0.5, -0.99, 4242, -0.6251998632279009],
      [-0.4, -0.4, 0.4, 2147483000, -0.9080227713635907],
    ];
    for (const [x, y, z, seed, was] of field) expect(unitField(x, y, z, seed, NOISE)).toBe(was);
    const ratio: [number, number, number, number, number, number, number, number][] = [
      [0.3, 0.7, 0.1, 9, 1.4, 0, 0, 0.7357207306223994],
      [-0.62, 0.15, 0.48, 9830405, 1.4, 0.3, 0.5, 0.15138250388946017],
      [0.9, -0.2, -0.75, 9830400, 2.0, 0.8, 4.1, 1.5745353479260258],
      [0.013, 0.5, -0.99, 4242, 0.8, 5, 1, 0.09479624350988633],
      [-0.9, 0, 0, 3, 0.001, 0.5, 0, 0.5509317024188803],
    ];
    for (const [x, y, z, seed, sigmaS, gradient, angle, was] of ratio) expect(densityRatio(x, y, z, seed, sigmaS, gradient, angle, NOISE)).toBe(was);
  });

  it("evaluates with the values it is given, not with values of its own", () => {
    // One octave is the value noise itself, over the divisor.
    const one: InteriorNoise = { octaves: 1, lacunarity: 2, gain: 0.5, sigma: 0.25 };
    expect(unitField(0.3, 0.7, 0.1, 9, one)).toBe((valueNoise(0.3, 0.7, 0.1, 9) - 0.5) / 0.25);
    // Two octaves at another lacunarity and gain: the second at three times the frequency and 0.4 of the weight.
    const two: InteriorNoise = { octaves: 2, lacunarity: 3, gain: 0.4, sigma: 0.2 };
    const second = valueNoise(0.3 * 3 + 17.3, 0.7 * 3 + 31.7, 0.1 * 3 + 47.1, 9 + 1013) - 0.5;
    expect(unitField(0.3, 0.7, 0.1, 9, two)).toBe((valueNoise(0.3, 0.7, 0.1, 9) - 0.5 + second * 0.4) / 0.2);
    expect(octaveNorm({ octaves: 1, lacunarity: 2, gain: 0.5 })).toBe(1);
    expect(octaveNorm({ octaves: 2, lacunarity: 3, gain: 0.4 })).toBe(Math.sqrt(1 + 0.4 * 0.4));
  });

  it("normalises only the set its standard deviation was measured for, and says why a cloud is smooth otherwise", () => {
    // The measured constant belongs to one parameter set; today it is the published one.
    expect(FIELD_SIGMA_MEASURED.measuredFor).toEqual(interiorOf(PUBLISHED));
    expect(NOISE).toEqual({ octaves: 4, lacunarity: 2, gain: 0.5, sigma: 0.2088 });
    expect(interiorNoise(null)).toBeNull();
    for (const other of [{ octaves: 5, lacunarity: 2, gain: 0.5 }, { octaves: 4, lacunarity: 2.2, gain: 0.5 }, { octaves: 4, lacunarity: 2, gain: 0.6 }]) {
      expect(interiorNoise(other)).toBeNull();
    }
    expect(cloudInterior(false, PUBLISHED)).toEqual({ noise: NOISE, note: null });
    const unmeasured = cloudInterior(false, { ...PUBLISHED, cloud_interior: { ...INTERIOR, octaves: 6 } });
    expect(unmeasured.noise).toBeNull();
    expect(unmeasured.note).toMatch(/drawn smooth: the model publishes a noise of 6 octaves, lacunarity 2, gain 0.5, and the viewer's normaliser was measured for 4, 2, 0.5/);
    const unpublished = cloudInterior(false, { layer: "on", scalars: { cloud_extinction_v: 2.9696 } });
    expect(unpublished.noise).toBeNull();
    expect(unpublished.note).toMatch(/publishes no cloud-interior noise/);
  });
});

describe("with the layer off the interior is smooth (S55, invariant I5)", () => {
  it("draws no noise under layer=off, whatever is published, and says nothing: it is the switch", () => {
    expect(cloudInterior(true, PUBLISHED)).toEqual({ noise: null, note: null });
    expect(cloudInterior(true, undefined)).toEqual({ noise: null, note: null });
  });

  it("is the cloud's mean density everywhere: the log-normal factor is 1 and the model sends no gradient", () => {
    // Layer-off, cloud_density_gradient and cloud_gradient_angle arrive as 0: the ratio is exactly 1 at every
    // point, for every seed and width - the cloud is its published mass in its published radius, nothing else.
    for (const [x, y, z] of [[0, 0, 0], [0.3, 0.7, 0.1], [-0.9, 0.2, 0.3], [0.5, -0.5, 0.5]]) {
      for (const sigmaS of [0.8, 1.4, 2.0]) expect(densityRatio(x, y, z, cloudSeed(300, 5), sigmaS, 0, 0, null)).toBe(1);
    }
    // So the column along any chord, sampled as the shader samples it, is the chord's length: the mean column.
    const a = [-0.8, 0.3, 0.52], b = [0.8, 0.3, -0.52];
    const length = Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]);
    let column = 0;
    for (let k = 0; k < CLOUD_SAMPLES; k += 1) {
      const t = (k + 0.5) / CLOUD_SAMPLES;
      column += densityRatio(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t, 7, 1.4, 0, 0, null) * (length / CLOUD_SAMPLES);
    }
    expect(column).toBeCloseTo(length, 12);
    // A gradient the model did send (the layer on, a set the viewer cannot normalise) still tilts a smooth cloud.
    expect(densityRatio(0.9, 0, 0, 3, 1.4, 0.5, 0, null)).toBe(1 + 0.5 * 0.9);
  });

  it("is the mean of the noisy interior: the volume mean of the published log-normal, as measured", () => {
    // The noisy cloud's density ratio averaged over the field, at the published parameters: 1 to the extent the
    // octave sum is Gaussian. Measured at S55: +1.6 % at sigma_s 0.8, -0.7 % at 1.4, -11 % at 2.0 (the sum of four
    // bounded octaves has no tail beyond 4.5 sigma, and exp(sigma g) at sigma 2 lives in the tail). The smooth
    // cloud's is 1 exactly: the two hold the same mass to those figures.
    const measured: Record<string, number> = { "0.8": 1.016, "1.4": 0.993, "2": 0.888 };
    for (const sigmaS of [0.8, 1.4, 2.0]) {
      let n = 0, mean = 0;
      for (let i = 0; i < 40; i += 1) for (let j = 0; j < 40; j += 1) for (let k = 0; k < 40; k += 1) {
        mean += densityRatio(i * 0.37 + 0.13, j * 0.29 + 0.41, k * 0.43 + 0.07, 11, sigmaS, 0, 0, NOISE);
        n += 1;
      }
      expect(mean / n).toBeCloseTo(measured[String(sigmaS)], 3);
    }
  });
});

describe("the march's shader draws the published interior (S55)", () => {
  const sha256 = (text: string) => createHash("sha256").update(text, "utf-8").digest("hex");

  it("is, at the published values, byte for byte the shader the viewer drew with before", () => {
    // The fragment source RegionVolume.tsx held at S54 (OCTAVES 4, f *= 2.0, w *= 0.5, FIELD_SIGMA.toFixed(6)),
    // hashed at S55 before any code moved. The same text is the same program: the picture cannot have moved.
    const fragment = regionFragment(NOISE);
    expect(fragment.length).toBe(4181);
    expect(sha256(fragment)).toBe("da30e55df935257fcfd2ac99ed6b5e2179f0c676f1ae30dfd90b3fd86194e415");
    expect(fragment).toContain("for (int k = 0; k < 4; k++) {\n      vec3 q = p * f + vec3(17.3, 31.7, 47.1) * float(k);");
    expect(fragment).toContain("f *= 2.0;\n      w *= 0.5;\n    }\n    return sum / 0.208800;");
    expect(fragment).toContain(`for (int i = 0; i < ${MAX_OBJECTS}; i++)`);
  });

  it("writes whatever noise it is given into the source: no literal of its own stands in", () => {
    const other = regionFragment({ octaves: 3, lacunarity: 2.5, gain: 0.4, sigma: 0.3 });
    expect(other).toContain("for (int k = 0; k < 3; k++) {\n      vec3 q");
    expect(other).toContain("f *= 2.5;\n      w *= 0.4;\n    }\n    return sum / 0.300000;");
    expect(other).not.toContain("0.208800");
    expect(glslFloat(2)).toBe("2.0");
    expect(glslFloat(0.5)).toBe("0.5");
    expect(glslFloat(3)).toBe("3.0");
  });

  it("draws a smooth cloud without the noise: the tilt alone", () => {
    const smooth = regionFragment(null);
    expect(smooth).not.toContain("unitField");
    expect(smooth).not.toContain("exp(sigmaS");
    expect(smooth).toContain("float densityRatio(vec3 p, int seed, float sigmaS, float gradient, float angle) {\n    return max(0.05, 1.0 + min(0.95, abs(gradient)) * (p.x * cos(angle) + p.z * sin(angle)));\n  }");
    // everything else is the same program: the head and the march
    const noisy = regionFragment(NOISE);
    expect(smooth.slice(0, smooth.indexOf("  float densityRatio"))).toBe(noisy.slice(0, noisy.indexOf("  float unitField")));
    expect(smooth.slice(smooth.indexOf("  vec4 obj("))).toBe(noisy.slice(noisy.indexOf("  vec4 obj(")));
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
