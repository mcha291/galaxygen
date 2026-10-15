// The noise's GLSL on the GPU (S66, BUILD_III Phase V7; D226 R9b): `window.__galaxygenNoiseProbe` (GalaxyView's
// NoiseProbe, an instrument that draws nothing the user sees) evaluates the include's functions (src/galaxy/
// noise.glsl.ts) at the model's committed vectors (model/galaxy/layer/vectors.json, read from disk here) and at the
// twin's two fixtures. The primitives - the hash, the lattice value, value noise in two and three dimensions, the
// sheared read, the octave sums, the log-normal map - are held to 1e-5 of numpy's float32 column (the gate's words);
// the composed fields' errors against float64 are measured on this machine's GPU and printed, a record (not a pin).
//
// Run alone: `npx playwright test e2e/noise.spec.ts` from frontend/ (the config starts the API on its own port, 8019).

import { readFileSync } from "node:fs";

import { expect, test } from "@playwright/test";

import { READY } from "./settings";

type Row = { u?: number[]; f?: number[] };
type Tables = Record<string, unknown>;

declare global {
  interface Window {
    __galaxygenNoiseProbe?: (kind: string, rows: Row[], tables?: Tables) => number[];
  }
}

const read = (path: string) => JSON.parse(readFileSync(new URL(path, import.meta.url), "utf-8"));
const VECTORS = read("../../model/galaxy/layer/vectors.json");
const CLUSTERING = read("../src/galaxy/__fixtures__/clustering_maps.json");
const SPURS = read("../src/galaxy/__fixtures__/spur_sum.json");
const PRIMITIVE_TOLERANCE = 1e-5;

/** The gas field's header entry the vectors' inputs define (the two cells they carry; every other normaliser 1). */
function vectorGasEntry(): Tables {
  const G = VECTORS.gas_fluctuation;
  const inputs = G.inputs;
  const cells = new Array(1024).fill(1);
  for (const c of G.cells) cells[c.ring * 32 + c.sector] = c.normaliser;
  return {
    seed: inputs.seed, scale: inputs.scale, slope: inputs.slope, change: inputs.change, octaves: inputs.octaves,
    lacunarity: inputs.lacunarity, sense: inputs.sense, edges: inputs.edges,
    ring: { break_octave: inputs.break_octave, sigma: inputs.sigma, strain: inputs.strain, twist: inputs.twist, norm: inputs.sigma.map(() => 1) },
    weights: G.weights, cell_normaliser: cells, rule: "",
  };
}

const worst = (values: number[]) => values.reduce((m, v) => Math.max(m, Math.abs(v)), 0);

test("the noise's GLSL against the model's vectors on this GPU", async ({ page }) => {
  test.setTimeout(READY.timeoutMs + 60_000);
  await page.goto("/");
  await page.waitForFunction(() => !!window.__galaxygenNoiseProbe, null, { timeout: READY.timeoutMs });
  const probe = (kind: string, rows: Row[], tables?: Tables) =>
    page.evaluate(([k, r, t]) => window.__galaxygenNoiseProbe!(k, r, t), [kind, rows, tables ?? {}] as const);
  const record: Record<string, number> = {};

  // The hash: integers end to end, so exactly the model's.
  const hashRows: (number | null)[][] = VECTORS.lattice_hash.rows;
  const hashes = await probe("hash", hashRows.map(([s, o, ix, iy, iz]) => ({
    u: [s as number, o as number, (ix as number) >>> 0, (iy as number) >>> 0, iz === null ? 0 : (iz as number) >>> 0, iz === null ? 0 : 1],
  })));
  hashRows.forEach((row, i) => {
    expect(hashes[4 * i] * 65536 + hashes[4 * i + 1], `hash row ${i}`).toBe(row[5]);
    expect(hashes[4 * i + 2]).toBe(((row[5] as number) >>> 8) * 2 ** -23 - 1);
  });

  // The primitives: one octave, the sheared read, the sums, the map - to 1e-5 of numpy's float32.
  const sections: [string, number[][], (r: number[]) => Row, (r: number[]) => [number, number], boolean][] = [
    ["noise2", VECTORS.noise2.rows, ([s, o, x, y]) => ({ u: [s, o], f: [x, y] }), (r) => [r[4], r[5]], false],
    ["noise3", VECTORS.noise3.rows, ([s, o, x, y, z]) => ({ u: [s, o], f: [x, y, z] }), (r) => [r[5], r[6]], false],
    ["shear", VECTORS.shear.rows, ([s, o, k, x, y]) => ({ u: [s, o], f: [x, y, k] }), (r) => [r[5], r[6]], false],
  ];
  const fractalRows: number[][] = [];
  const fractalInputs: Row[] = [];
  for (const c of VECTORS.fractal.cases) {
    for (const row of c.rows as number[][]) {
      const p = [...row.slice(0, c.ndim), 0, 0, 0].slice(0, 4); // texel 0: the position; texel 1: the sum's numbers
      fractalInputs.push({ u: [c.seed, c.octaves, c.ndim], f: [...p, c.base_frequency, c.lacunarity, c.gain, c.top, c.norm] });
      fractalRows.push([row[c.ndim], row[c.ndim + 1]]);
    }
  }
  const lognormalRows: number[][] = [];
  const lognormalInputs: Row[] = [];
  for (const c of VECTORS.lognormal.cases) {
    for (const [x, y, v, v32] of c.rows as number[][]) {
      lognormalInputs.push({ u: [c.seed, c.octaves, 2], f: [x, y, 0, 0, c.base_frequency, c.lacunarity, c.gain, c.top, c.norm, c.sigma, c.normaliser] });
      lognormalRows.push([v, v32]);
    }
  }
  for (const [name, rows, input, want] of sections) {
    const got = await probe(name, rows.map(input));
    record[`${name}_f32`] = worst(rows.map((r, i) => got[4 * i] - want(r)[1]));
    record[`${name}_f64`] = worst(rows.map((r, i) => got[4 * i] - want(r)[0]));
  }
  const fr = await probe("fractal", fractalInputs);
  record.fractal_f32 = worst(fractalRows.map(([, v32], i) => fr[4 * i] - v32));
  record.fractal_f64 = worst(fractalRows.map(([v], i) => fr[4 * i] - v));
  const ln = await probe("lognormal", lognormalInputs);
  record.lognormal_f32 = worst(lognormalRows.map(([, v32], i) => ln[4 * i] / v32 - 1));
  record.lognormal_f64 = worst(lognormalRows.map(([v], i) => ln[4 * i] / v - 1));
  for (const name of ["noise2", "noise3", "shear", "fractal", "lognormal"]) {
    expect(record[`${name}_f32`], `${name} against numpy's float32`).toBeLessThan(PRIMITIVE_TOLERANCE);
  }

  // The composed fields: a record of this GPU's errors, not a pin (R9b).
  const G = VECTORS.gas_fluctuation;
  const sums: number[][] = G.sums.rows;
  const gasRaw = { gas: vectorGasEntry(), reduceTwist: false };
  const atRead = await probe("gasSum", sums.map((r) => ({ u: [r[2]], f: [r[7], r[8]] })), gasRaw);
  record.gas_sum_at_read_f32 = worst(sums.map((r, i) => atRead[4 * i] - r[4]));
  const composed = await probe("gasMap", sums.map((r) => ({ f: [r[0], r[1]] })), { gas: vectorGasEntry(), reduceTwist: true });
  record.gas_g_f64 = worst(sums.map((r, i) => composed[4 * i + 1] - r[3]));
  record.gas_g_f64_inside_3kpc = worst(sums.map((r, i) => (Math.hypot(r[0], r[1]) < 3 ? composed[4 * i + 1] - r[3] : 0)));
  const maps: number[][] = G.maps.rows;
  const mapped = await probe("gasMap", maps.map((r) => ({ f: [r[0], r[1]] })), { gas: vectorGasEntry(), reduceTwist: true });
  record.gas_map_f64_relative = worst(maps.map((r, i) => mapped[4 * i] / r[4] - 1));
  const cell_mean = { 1: new Array(1024).fill(1), 2: new Array(1024).fill(1), 3: new Array(1024).fill(1) };
  const clustering = { ...CLUSTERING.field, table_points: 2, octave_ages_myr: [], cell_mean, rule: "" };
  const cl = await probe("clusterMaps", CLUSTERING.rows.map((r: number[]) => ({ f: [r[0], r[1]] })), { clustering });
  record.cluster_maps_f64_relative = worst((CLUSTERING.rows as number[][]).flatMap((r, i) => [0, 1, 2].map((k) => cl[4 * i + k] / r[2 + k] - 1)));
  record.cluster_maps_f32_relative = worst((CLUSTERING.rows as number[][]).flatMap((r, i) => [0, 1, 2].map((k) => cl[4 * i + k] / r[5 + k] - 1)));
  const spurs = { ...SPURS.spurs, share: null, constants: {}, rule: "" };
  const sp = await probe("spurSum", SPURS.rows.map((r: number[]) => ({ f: [r[0], r[1]] })), { spurs });
  const peak = Math.max(...SPURS.rows.map((r: number[]) => r[2]));
  record.spur_sum_over_peak = worst((SPURS.rows as number[][]).map((r, i) => (sp[4 * i] - r[2]) / peak));
  console.log(`noise probe (this GPU): ${JSON.stringify(record)}`);
  expect(record.gas_sum_at_read_f32, "the gas sum at numpy's own read positions").toBeLessThan(PRIMITIVE_TOLERANCE);
});
