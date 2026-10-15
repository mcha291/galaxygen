import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import type { GasFluctuationEntry, SpursEntry } from "../api";
import clusteringFixture from "./__fixtures__/clustering_maps.json";
import spurFixture from "./__fixtures__/spur_sum.json";
import { NOISE_GLSL, NOISE_UNIFORMS } from "./noise.glsl";
import {
  CELL_SECTORS,
  type ClusteringTables,
  clusteringMaps,
  fractal,
  gasGaussian,
  gasMap,
  gasSum,
  latticeHash,
  latticeValue,
  lognormalMap,
  noise2,
  noise3,
  prepareGas,
  prepareSpurs,
  reduceTwist,
  shear,
  spurSum,
} from "./noise";

// S66 (BUILD_III Phase V7; D226 R1, R9a): the float32 twin of the layer's noise against the model's committed vectors,
// read where the model writes them (model/galaxy/layer/vectors.json; vitest runs in node, so the file is read from
// disk by its URL - nothing is copied into the frontend).
const VECTORS = JSON.parse(readFileSync(new URL("../../../model/galaxy/layer/vectors.json", import.meta.url), "utf-8"));

/** The largest |a - b| over pairs. */
const worst = (pairs: [number, number][]) => pairs.reduce((m, [a, b]) => Math.max(m, Math.abs(a - b)), 0);

describe("the noise primitives against vectors.json (R1a: bit-exact to float32, within 1e-6 of float64)", () => {
  it("hashes every lattice point to the model's uint32, and its lattice value exactly", () => {
    const rows: [number, number, number, number, number | null, number][] = VECTORS.lattice_hash.rows;
    expect(rows.length).toBe(160);
    for (const [seed, octave, ix, iy, iz, hash] of rows) {
      expect(latticeHash(seed, octave, ix, iy, iz ?? undefined)).toBe(hash);
      expect(latticeValue(hash)).toBe((hash >>> 8) * 2 ** -23 - 1);
    }
  });

  it("noise2 and noise3 are the float32 column to the bit", () => {
    const n2: number[][] = VECTORS.noise2.rows;
    const n3: number[][] = VECTORS.noise3.rows;
    const t2 = n2.map(([s, o, x, y, v, v32]) => [noise2(s, x, y, o), v, v32]);
    const t3 = n3.map(([s, o, x, y, z, v, v32]) => [noise3(s, x, y, z, o), v, v32]);
    for (const [t, , v32] of [...t2, ...t3]) expect(t).toBe(v32);
    expect(worst(t2.map(([t, v]) => [t, v]))).toBeLessThan(1e-6);
    expect(worst(t3.map(([t, v]) => [t, v]))).toBeLessThan(1e-6);
  });

  it("the sheared reads and the fractal sums are the float32 column to the bit", () => {
    for (const [s, o, k, x, y, v, v32] of VECTORS.shear.rows as number[][]) {
      const [xs, ys] = shear(x, y, k);
      const t = noise2(s, xs, ys, o);
      expect(t).toBe(v32);
      expect(Math.abs(t - v)).toBeLessThan(1e-6);
    }
    let n = 0;
    for (const c of VECTORS.fractal.cases) {
      for (const row of c.rows as number[][]) {
        const t = fractal(row.slice(0, c.ndim), c);
        expect(t).toBe(row[c.ndim + 1]);
        expect(Math.abs(t - row[c.ndim])).toBeLessThan(1e-6);
        n += 1;
      }
    }
    expect(n).toBe(120);
  });

  it("the log-normal map is the float32 column to exp's last bit and within 1e-6 of float64, relatively", () => {
    // Its sum is bit-exact (the fractal section); exp is the one operation a C library need not round correctly
    // (noise.py: the section is compared to 1e-12, not to the bit), and numpy's float32 exp and Math.exp rounded to
    // float32 differ by one ulp on some rows: measured 1.57e-7 relative (S66; the probe's 1.6e-7), held to 2.5e-7.
    let ulp = 0;
    for (const c of VECTORS.lognormal.cases) {
      for (const [x, y, v, v32] of c.rows as number[][]) {
        const g = fractal([x, y], c);
        const t = lognormalMap(g, c.sigma, c.normaliser);
        ulp = Math.max(ulp, Math.abs(t / v32 - 1));
        expect(Math.abs(t / v - 1)).toBeLessThan(1e-6);
      }
    }
    expect(ulp).toBeLessThan(2.5e-7);
  });
});

/** The gas field's header entry the vectors' inputs define (the two cells they carry; every other normaliser 1). */
function vectorEntry(): GasFluctuationEntry {
  const G = VECTORS.gas_fluctuation;
  const inputs = G.inputs;
  const cells = new Array(1024).fill(1);
  for (const c of G.cells) cells[c.ring * CELL_SECTORS + c.sector] = c.normaliser;
  return {
    seed: inputs.seed, scale: inputs.scale, slope: inputs.slope, change: inputs.change, octaves: inputs.octaves,
    lacunarity: inputs.lacunarity, sense: inputs.sense, edges: inputs.edges,
    ring: { break_octave: inputs.break_octave, sigma: inputs.sigma, strain: inputs.strain, twist: inputs.twist, norm: inputs.sigma.map(() => 1) },
    weights: G.weights, cell_normaliser: cells, rule: "",
  };
}

describe("the gas fluctuation field against vectors.json's gas section (R1b, R1c)", () => {
  const G = VECTORS.gas_fluctuation;
  const rows: number[][] = G.sums.rows;

  it("given numpy's float32 read positions the octave sum is g_f32 to the bit (the gate's 1e-5, met exactly)", () => {
    expect(G.sums.columns).toEqual(["x", "y", "ring", "g", "g_f32", "x_read", "y_read", "x_read_f32", "y_read_f32"]);
    const t = prepareGas(vectorEntry(), false);
    expect(t).not.toBeNull();
    for (const [, , ring, , g32, , , X32, Y32] of rows) expect(gasSum(X32, Y32, ring, t!)).toBe(g32);
  });

  it("read at the twin's own positions g is within 5e-3 of float64 and the map within 1e-3 relative (float32's geometry)", () => {
    // D226 R1c: the declared float32 floor. The read's transcendentals at R up to 26 kpc move the read point by about
    // 0.03 pc (an ulp of 1.9e-6 kpc at 26 kpc is 4e-4 on g by itself); the twist is reduced mod 2 pi in doubles, and
    // the point is rotated by theta rather than rebuilt from atan2 (gasReadPosition): measured 4.85e-4 on g at worst,
    // 2.2e-5 inside 3 kpc, the map 1.9e-4 (the polar form, as numpy writes it: 1.13e-3, 2.8e-5, 2.5e-4).
    const t = prepareGas(vectorEntry())!;
    const errors = rows.map(([x, y, , g]) => Math.abs(gasGaussian(x, y, t) - g));
    const inner = rows.map(([x, y, , g], i) => (Math.hypot(x, y) < 3 ? errors[i] : 0));
    expect(Math.max(...errors)).toBeLessThan(5e-3);
    expect(Math.max(...inner)).toBeLessThan(5e-4);
    for (const [x, y, , , v] of G.maps.rows as number[][]) expect(Math.abs(gasMap(x, y, t) / v - 1)).toBeLessThan(1e-3);
    // the reduction, measured: the largest error with it against without it (S66: 4.85e-4 against 1.85e-3; the map
    // 1.9e-4 against 3.2e-4)
    const raw = prepareGas(vectorEntry(), false)!;
    const unreduced = Math.max(...rows.map(([x, y, , g]) => Math.abs(gasGaussian(x, y, raw) - g)));
    expect(Math.max(...errors)).toBeLessThanOrEqual(unreduced);
  });

  it("reduces the twist by whole turns only", () => {
    for (const tw of VECTORS.gas_fluctuation.inputs.twist as number[]) {
      const r = reduceTwist(tw);
      expect(Math.abs(r)).toBeLessThanOrEqual(Math.PI);
      expect(Math.abs(Math.sin(r) - Math.sin(tw))).toBeLessThan(1e-12);
    }
  });
});

describe("the clustering field's three maps and the spurs' sum against the model's evaluators (fixtures)", () => {
  it("ClusteringField.maps: numpy's float32 path to exp's last bit, float64 within the declared 2e-4 relative", () => {
    // __fixtures__/clustering_maps.json: the Milky Way template's field at 200 float32 positions out to 25 kpc
    // (lattice coordinates up to ~530 cells of the finest octave), written by builder A's fixtures.py (S66). Measured:
    // 1.68e-7 against numpy's float32 maps (the sums bit-exact, exp's last bit), 9.7e-5 against float64 - float32's
    // lattice coordinates at ~500 cells (noise.py: up to 4e-4 on a sum below 1024 cells), declared 2e-4.
    const fx = clusteringFixture as { field: Omit<ClusteringTables, "base_frequency" | "cellMean" | "octaveAgesMyr"> & { scale: number }; rows: number[][] };
    const t: ClusteringTables = { ...fx.field, base_frequency: 1 / fx.field.scale, cellMean: new Float32Array(0), octaveAgesMyr: [] };
    let rel = 0;
    let ulp = 0;
    for (const [x, y, m1, m2, m3, f1, f2, f3] of fx.rows) {
      const got = clusteringMaps(x, y, t);
      [f1, f2, f3].forEach((m, k) => (ulp = Math.max(ulp, Math.abs(got[k] / Math.fround(m) - 1))));
      [m1, m2, m3].forEach((m, k) => (rel = Math.max(rel, Math.abs(got[k] / m - 1))));
    }
    expect(ulp).toBeLessThan(2.5e-7);
    expect(rel).toBeLessThan(2e-4);
  });

  it("Spurs.at: the float32 point function within the declared 1e-3 (1000 points round the 48 spurs)", () => {
    // Measured (S66): 1.9e-5 of the sum's peak (3.46) at worst, 2.5e-4 relative where the sum exceeds 1 % of its peak -
    // float32's ln R and the width's 1/2s^2 of ~5e4 at 8 kpc; declared 1e-3 (the ruling's expectation, R4).
    const fx = spurFixture as unknown as { spurs: SpursEntry; rows: number[][] };
    const t = prepareSpurs({ ...fx.spurs, share: null, constants: {}, rule: "" })!;
    expect(t.count).toBe(48);
    const peak = Math.max(...fx.rows.map((r) => r[2]));
    let abs = 0;
    let rel = 0;
    for (const [R, phi, S] of fx.rows) {
      const got = spurSum(R, phi, t);
      abs = Math.max(abs, Math.abs(got - S));
      if (S > 1e-2 * peak) rel = Math.max(rel, Math.abs(got / S - 1));
    }
    expect(abs / peak).toBeLessThan(1e-3);
    expect(rel).toBeLessThan(1e-3);
  });
});

// The include's text, pinned as the field's fragment is (tuning.test.ts): a change to the GLSL is a change here, made
// knowingly, and the e2e probe (e2e/noise.spec.ts) measures the text on the GPU.
const sha256 = (text: string) => createHash("sha256").update(text.replace(/\r\n/g, "\n"), "utf-8").digest("hex");
const GLSL_SHA256 = "34fc93ab5ccc26e12517cef6eec0675021b2857ffb68c60d3f77f72ee6a3a147";
const UNIFORMS_SHA256 = "6784c35556edc3eab7219616fb88a86c7ffe3064775d5046a6d91445e438f3d6";

describe("the GLSL include (noise.glsl.ts)", () => {
  it("is pinned and names every function its twin has", () => {
    expect(sha256(NOISE_GLSL)).toBe(GLSL_SHA256);
    expect(sha256(NOISE_UNIFORMS)).toBe(UNIFORMS_SHA256);
    for (const name of ["uint layerMix(", "uint layerHash(", "float layerValue(", "float layerNoise2(", "float layerNoise3(",
      "vec3 layerFractal2Coarsest(", "float layerFractal(", "float layerLognormal(", "int layerGasRing(", "int layerGasSector(",
      "vec2 layerGasRead(", "float layerGasSum(", "float layerGasMap(", "vec3 layerClusterMaps(", "bool layerSpurReads(",
      "float layerSpurExcess(", "float layerSpurSum("]) {
      expect(NOISE_GLSL).toContain(name);
    }
    expect(NOISE_GLSL).toContain("0x7feb352du");
    expect(NOISE_GLSL).toContain("0x846ca68bu");
    expect(NOISE_GLSL).toContain("0x9e3779b9u");
  });
});
