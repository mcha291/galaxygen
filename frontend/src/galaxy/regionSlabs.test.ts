import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import * as wire from "@interface/transport.js";

import { orbitPosition } from "./capture";
import {
  FIELD_SLABS,
  MAG_PER_TAU,
  type RegionObjects,
  kappaOfMeanColumn,
  fieldTransmissionBySlabs,
  layerDepthShare,
  marchFieldTransmission,
  marchTransmission,
  packObjects,
  regionFragment,
  sortedFrom,
} from "./region";

// #112's field half (S67, D228): the field's light split into FIELD_SLABS depth slabs along each ray, as the stars'
// layer puts it, each slab dimmed only by the clouds in front of it; and each cloud at its own published column.

const EXT: [number, number, number] = [1.3, 1.0, 0.75];
const H = 0.3; // the stars' layer's scale height, kpc: a synthetic one, of the Milky Way's order
const NONE = { cluster_radius: [] };

/** One smooth cloud at the scene's origin's (x, z) = (8, 0), at height `y` kpc, of `size` pc and mean A_V `av`. */
function cloud(y: number, size: number, av: number) {
  return {
    cloud_radius: [8], cloud_azimuth: [0], cloud_height: [y], cloud_size: [size], cloud_mass: [1], cloud_density_pdf_width: [1.4],
    cloud_density_gradient: [0], cloud_gradient_angle: [0], cloud_cluster_index: [-1], cell: [300], index: [0], cloud_dust_extinction_v: [av],
  };
}
const above: [number, number, number] = [8, 1, 0]; // the camera 1 kpc over the cloud
const down: [number, number, number] = [0, -1, 0]; // looking straight down: face-on
const field = (t: RegionObjects, origin = above, dir = down, weight = 1, h = H, slabs = FIELD_SLABS) =>
  marchFieldTransmission(origin, dir, t.data, t.count, EXT, weight, null, h, slabs);
const whole = (t: RegionObjects, origin = above, dir = down) => marchTransmission(origin, dir, t.data, t.count, EXT, 1, null).trans;
/**
 * What a face-on cloud of radius `r` kpc at height `y` must leave of a field of transmission `t` behind it: the light
 * in front of its first sample (CLOUD_SAMPLES = 4: a quarter of the chord's middle, 3r/4 above its centre) undimmed,
 * the light behind its last (3r/4 below) dimmed by t, the light between them in between - each to half a slab.
 */
function bounds(y: number, r: number, t: number): [number, number] {
  const first = layerDepthShare(above[1], down[1], y + 0.75 * r, H)!;
  const last = layerDepthShare(above[1], down[1], y - 0.75 * r, H)!;
  const slack = 1 / (2 * FIELD_SLABS) + 1e-12;
  return [first + (1 - first) * t - slack, last + (1 - last) * t + slack];
}
const within = (v: number, [lo, hi]: [number, number]) => {
  expect(v).toBeGreaterThanOrEqual(lo);
  expect(v).toBeLessThanOrEqual(hi);
};

describe("the field's light behind a cloud, not in front of it (#112's field half)", () => {
  it("a cloud at the midplane, face-on, dims a uniform field by the light behind it only: about half at T -> 0", () => {
    const opaque = packObjects(cloud(0, 20, 1000), NONE); // 1000 mag: T is 0 to the last bit
    expect(whole(opaque)).toEqual([0, 0, 0]); // before S67 the field there was black
    const f = field(opaque);
    // The light in front of the cloud's first sample (its chord's first quarter's middle, 15 pc above the plane),
    // to half a slab: the slabs whose middles lie in front of it keep their light, the rest go dark.
    const front = layerDepthShare(above[1], down[1], 0.015, H)!;
    expect(front).toBeCloseTo(0.4692, 4);
    for (const v of f) {
      expect(Math.abs(v - front)).toBeLessThanOrEqual(1 / (2 * FIELD_SLABS) + 1e-12);
      expect(Math.abs(v - 0.5)).toBeLessThan(0.05);
    }
    // a cloud of the census's column, A_V 1.9 mag over its disc: the field keeps its front half and the back half's T
    const typical = packObjects(cloud(0, 20, 1.9), NONE);
    const t = whole(typical);
    const g = field(typical);
    for (let k = 0; k < 3; k += 1) {
      expect(g[k]).toBeGreaterThan(t[k]);
      within(g[k], bounds(0, 0.02, t[k]));
      expect(Math.abs(g[k] - (0.5 + 0.5 * t[k]))).toBeLessThan(0.05);
    }
  });

  it("a cloud high above the midplane dims nearly all of it, as the whole ray's T; one below it next to none", () => {
    // 0.8 kpc up, 2.7 h: 3 % of the layer's light lies between it and the camera (sech²'s tail), and that is all it keeps
    const high = packObjects(cloud(0.8, 20, 1.9), NONE);
    const t = whole(high);
    field(high).forEach((v, k) => {
      within(v, bounds(0.8, 0.02, t[k]));
      expect(Math.abs(v - t[k])).toBeLessThan(0.04);
    });
    const low = packObjects(cloud(-0.8, 20, 1.9), NONE);
    const tl = whole(low);
    field(low).forEach((v, k) => {
      within(v, bounds(-0.8, 0.02, tl[k]));
      expect(v).toBeGreaterThan(0.92); // 6.7 % of the light on this ray lies below 0.8 kpc down, and only that dims
    });
  });

  it("conserves the field's light where the clouds are absent: exactly 1, on every ray", () => {
    const hii = {
      cluster_radius: [8], cluster_azimuth: [0], cluster_height: [0], hii_stromgren_radius: [30], hii_halpha_emissivity: [1e-20],
      bubble_radius: [40], bubble_shell_thickness: [5], bubble_shell_emissivity: [2e-21], cell: [300], index: [0],
    };
    const tables = [packObjects({ cloud_radius: [] }, NONE), packObjects({ cloud_radius: [] }, hii), packObjects(cloud(0, 20, 0), hii)];
    const rays: [number, number, number][] = [down, [0.3, -0.9, 0.1], [0.99, -0.01, 0], [0, 1, 0], [1, 0, 0]];
    for (const t of tables) {
      for (const d of rays) {
        const n = Math.hypot(...d);
        const dir = d.map((v) => v / n) as [number, number, number];
        for (const w of [1, 0.5]) expect(field(t, above, dir, w)).toEqual([1, 1, 1]);
      }
    }
    // the clouds' table with the cloud missed by the ray: 1 too
    expect(field(packObjects(cloud(0, 20, 1.9), NONE), [9, 1, 0])).toEqual([1, 1, 1]);
  });

  it("falls back to the whole ray's T without a layer, or on a ray that leaves the layer away from it", () => {
    const t = packObjects(cloud(0, 20, 1.9), NONE);
    expect(field(t, above, down, 1, 0)).toEqual(whole(t));
    expect(layerDepthShare(100, 1, 100, H)).toBeNull(); // far above, looking up: none of the layer's light
    expect(layerDepthShare(1, -1, 1, 0)).toBeNull();
  });

  it("sums the definition's slabs in march order: the same factor on depth-ordered rays, at every K", () => {
    // Twelve clouds stacked up the line of sight at distinct heights, none overlapping another on any ray here,
    // of sizes and columns that vary, a noisy interior and cavities absent: the march meets their samples in depth
    // order (nearest-first), so the running sum is the slabs' sum to rounding.
    const n = 12;
    const ys = Array.from({ length: n }, (_, i) => -0.55 + 0.1 * i);
    const set = {
      cloud_radius: Array(n).fill(8), cloud_azimuth: Array(n).fill(0), cloud_height: ys, cloud_size: ys.map((_, i) => 8 + 3 * i),
      cloud_mass: ys.map((_, i) => n - i), cloud_density_pdf_width: Array(n).fill(1.4), cloud_density_gradient: Array(n).fill(0),
      cloud_gradient_angle: Array(n).fill(0), cloud_cluster_index: Array(n).fill(-1), cell: Array(n).fill(300),
      index: ys.map((_, i) => i), cloud_dust_extinction_v: ys.map((_, i) => 0.3 + 0.7 * i),
    };
    const t = packObjects(set, NONE);
    const data = sortedFrom(t, above, new Float32Array(t.data.length));
    for (const d of [down, [0.004, -1, 0.002], [-0.003, -1, 0.001]] as [number, number, number][]) {
      const l = Math.hypot(...d);
      const dir = d.map((v) => v / l) as [number, number, number];
      for (const K of [16, 64, FIELD_SLABS]) {
        const a = marchFieldTransmission(above, dir, data, t.count, EXT, 1, null, H, K);
        const b = fieldTransmissionBySlabs(above, dir, data, t.count, EXT, 1, null, H, K);
        a.forEach((v, k) => expect(Math.abs(v - b[k])).toBeLessThan(1e-12));
        expect(a[1]).toBeLessThan(1); // the rays meet the clouds
      }
    }
  });

  it("fades with the regime's weight as the points' T does", () => {
    const t = packObjects(cloud(0, 20, 1.9), NONE);
    const full = field(t);
    field(t, above, down, 0.5).forEach((v, k) => expect(v).toBeCloseTo(0.5 + 0.5 * full[k], 14));
  });

  it("the twin and the shader carry the same expressions", () => {
    const glsl = regionFragment(null);
    expect(glsl).toContain("u0 = tanh(clamp(origin.y / (2.0 * starsHeight), -10.0, 10.0));");
    expect(glsl).toContain("span = (dir.y > 0.0 ? 1.0 : -1.0) - u0;\n      split = abs(span) >= 1e-6;");
    const kf = `${FIELD_SLABS}.0`;
    expect(glsl).toContain(`float first = min(max(floor(q * ${kf} - 0.5) + 1.0, lit), ${kf});`);
    expect(glsl).toContain(`field += (first - lit) / ${kf} * run;\n            run *= exp(-c.z * rho * ds * extRatio);\n            lit = first;`);
    expect(glsl).toContain(`if (split) out3 = field + (${kf} - lit) / ${kf} * run;`);
    const twin = marchFieldTransmission.toString() + layerDepthShare.toString();
    expect(twin).toContain("Math.tanh(Math.min(10, Math.max(-10, v / (2 * h))))");
    expect(twin).toContain("(dy > 0 ? 1 : -1) - u0");
    expect(twin).toContain("Math.abs(span) < 1e-6");
    expect(twin).toMatch(/Math\.min\(Math\.max\(Math\.floor\(q \* slabs - 0?\.5\) \+ 1, lit\), slabs\)/); // the transpiler writes .5
    expect(twin).toContain("field[j] += (first - lit) / slabs * run[j];");
    expect(twin).toContain("run[j] *= Math.exp(-c[2] * rho * ds * extRatio[j]);");
    expect(twin).toContain("field[j] += (slabs - lit) / slabs * run[j];");
  });
});

describe("each cloud at its own published column (#167's region half, S67)", () => {
  it("is a uniform sphere whose face-on mean column is the published A_V", () => {
    // The chords through the sphere, averaged over its projected disc by area (a midpoint rule in the impact parameter).
    const r = 0.015;
    const av = 1.897; // the Milky Way census's median (#167)
    const kappa = kappaOfMeanColumn(av, r);
    const n = 20000;
    let mean = 0;
    for (let i = 0; i < n; i += 1) {
      const b = ((i + 0.5) / n) * r;
      mean += 2 * kappa * Math.sqrt(r * r - b * b) * ((2 * b) / (r * r)) * (r / n);
    }
    expect(Math.abs((mean * MAG_PER_TAU) / av - 1)).toBeLessThan(1e-6);
    // and the table carries it: the clouds' own numbers, not the census's law
    const t = packObjects(cloud(0, 15, av), NONE);
    expect(Math.abs(t.data[10] / kappa - 1)).toBeLessThan(1e-6);
  });

  it("draws no cloud whose column is missing (B9)", () => {
    expect(packObjects(cloud(0, 15, Number.NaN), NONE).count).toBe(0);
    expect(packObjects(cloud(0, 15, -1), NONE).count).toBe(0);
    const { cloud_dust_extinction_v: _, ...without } = cloud(0, 15, 1);
    expect(packObjects(without, NONE).count).toBe(0);
  });
});

/**
 * K's measurement (rule A9), recorded: the ray's summed light (the field's factor, V) against K = 1, 2, 4, ... on the
 * Milky Way's zoom stand in the field mode (e2e/captures.json milky_way-zoom: face-on, 0.25 kpc, the 45 degree lens),
 * over a 128 x 128 grid of the frame's rays through the region's own table - the census the viewer asked for there,
 * at the render header's stars' height. `worst` is the largest change of one ray's factor from K / 2 to K, `frame` the
 * change of the frame's mean factor. K is the first at which the worst ray moves by less than 1e-3.
 */
const FIELD_SLABS_MEASURED = {
  stand: "milky_way-zoom, field mode (S67, 2026-10-18; the camera at [2.3112, 0.6036, 7.8024] kpc, face-on)",
  starsHeight: 0.35569922843325036, // kpc, the render header's layers.stars
  clouds: 44, // of the region table's 112 objects (the rest HII regions and shells)
  rays: 128 * 128,
  steps: [
    { K: 2, worst: 0.48637654402951713, frame: 0.0008191948264617555 },
    { K: 4, worst: 0.24318827201475857, frame: 0.00016764823054071787 },
    { K: 8, worst: 0.12159413600737934, frame: 0.00008382411527041445 },
    { K: 16, worst: 0.0036392604219348534, frame: 7.174341392079953e-7 },
    { K: 32, worst: 0.03011003676524826, frame: 0.000033675964248858214 },
    { K: 64, worst: 0.011402142016912475, frame: 0.0000032195440681226373 },
    { K: 128, worst: 0.0058107457204972235, frame: 0.000002108876882456201 },
    { K: 256, worst: 0.002741446008626025, frame: 0.0000010821822691298166 },
    { K: 512, worst: 0.0012932880911203926, frame: 1.2622987144439435e-7 },
    { K: 1024, worst: 0.0009045913380282267, frame: 1.1809320921152278e-7 },
    { K: 2048, worst: 0.0003842239069572484, frame: 2.212537197898712e-8 },
    { K: 4096, worst: 0.00017403963923801058, frame: 4.0306535886713846e-9 },
  ],
  // the frame's mean factor at FIELD_SLABS, and what the whole ray's T gave it before S67
  meanField: 0.9985653159385555,
  meanWhole: 0.9970204245027512,
};

describe("K, as recorded", () => {
  it("is the first K at which the worst ray moved by under 1e-3, and every doubling after it stayed under", () => {
    const steps = FIELD_SLABS_MEASURED.steps;
    const first = steps.findIndex((s) => s.worst < 1e-3);
    expect(steps[first].K).toBe(FIELD_SLABS);
    for (const s of steps.slice(first)) expect(s.worst).toBeLessThan(1e-3);
    // the frame's mean had settled long before: under 1e-6 from K = 512 on
    for (const s of steps.filter((x) => x.K >= 512)) expect(s.frame).toBeLessThan(1e-6);
  });
});

// The measurement itself, run against a live API when GALAXYGEN_MEASURE is the path of a record of the requests the
// viewer made at the stand (JSON: `asked`, each /api request's url, method and body; `camera`; `at`, the orbit
// target - S67's harness that wrote it is kept in the session's notes, not here) and GALAXYGEN_MEASURE_API its origin.
const MEASURE = process.env.GALAXYGEN_MEASURE;
const ORIGIN = process.env.GALAXYGEN_MEASURE_API;
describe.skipIf(!MEASURE || !ORIGIN)("K, measured on the zoom stand", () => {
  it("converges: the worst ray moves by under 1e-3 at FIELD_SLABS", { timeout: 600_000 }, async () => {
    const record = JSON.parse(readFileSync(MEASURE!, "utf-8")) as {
      asked: { url: string; method: string; body: string | null }[];
      camera: { inclination_deg: number; azimuth_deg: number; radius_kpc: number; fov_deg: number };
      at: [number, number, number];
    };
    const params = (url: string, body: string | null) => {
      const u = new URL(url);
      const q = Object.fromEntries(new URLSearchParams(body ?? u.search));
      return { path: u.pathname, q };
    };
    const regionOf = (path: string) =>
      record.asked.map((a) => params(a.url, a.body)).filter((a) => a.path === path && a.q.precision !== "f4" && a.q.level !== undefined).at(-1)!;
    const got = async (path: string) => {
      const { q } = regionOf(path);
      return wire.frame(path, q, { origin: ORIGIN, method: "GET" });
    };
    const clouds = await got("/api/clouds");
    const clusters = await got("/api/clusters");
    const render = record.asked.map((a) => params(a.url, a.body)).filter((a) => a.path === "/api/render").at(-1)!;
    const rendered = await wire.frame("/api/render", render.q, { origin: ORIGIN });
    const h = Number((rendered.header as { layers?: { stars?: number } }).layers?.stars);
    const table = packObjects(clouds.arrays as never, clusters.arrays as never);
    const at = record.at;
    const o = orbitPosition(record.camera, record.camera.fov_deg);
    const eye: [number, number, number] = [at[0] + o[0], at[1] + o[1], at[2] + o[2]];
    const data = sortedFrom(table, eye, new Float32Array(table.data.length));
    // The camera's frame: looking at the target, the picture's up any perpendicular (a square grid's statistic).
    const fwd = [at[0] - eye[0], at[1] - eye[1], at[2] - eye[2]];
    const fl = Math.hypot(...fwd);
    const f = fwd.map((v) => v / fl);
    const ref = Math.abs(f[1]) > 0.9 ? [1, 0, 0] : [0, 1, 0];
    const rx = [f[1] * ref[2] - f[2] * ref[1], f[2] * ref[0] - f[0] * ref[2], f[0] * ref[1] - f[1] * ref[0]];
    const rl = Math.hypot(...rx);
    const right = rx.map((v) => v / rl);
    const up = [right[1] * f[2] - right[2] * f[1], right[2] * f[0] - right[0] * f[2], right[0] * f[1] - right[1] * f[0]];
    const half = Math.tan((record.camera.fov_deg * Math.PI) / 360);
    const n = 128;
    const dirs: [number, number, number][] = [];
    for (let i = 0; i < n; i += 1) for (let j = 0; j < n; j += 1) {
      const sx = (((i + 0.5) / n) * 2 - 1) * half, sy = (((j + 0.5) / n) * 2 - 1) * half;
      const d = [0, 1, 2].map((k) => f[k] + sx * right[k] + sy * up[k]);
      const l = Math.hypot(...d);
      dirs.push(d.map((v) => v / l) as [number, number, number]);
    }
    const factor = (K: number) => dirs.map((d) => marchFieldTransmission(eye, d, data, table.count, [1, 1, 1], 1, null, h, K)[0]);
    let last = factor(1);
    const steps: { K: number; worst: number; frame: number }[] = [];
    for (let K = 2; K <= 4096; K *= 2) {
      const now = factor(K);
      let worst = 0, a = 0, b = 0;
      now.forEach((v, r) => { worst = Math.max(worst, Math.abs(v - last[r])); a += v; b += last[r]; });
      steps.push({ K, worst, frame: Math.abs(a - b) / dirs.length });
      last = now;
    }
    const whole = dirs.map((d) => marchTransmission(eye, d, data, table.count, [1, 1, 1], 1, null).trans[0]);
    const meanWhole = whole.reduce((s, v) => s + v, 0) / whole.length;
    const meanField = factor(FIELD_SLABS).reduce((s, v) => s + v, 0) / dirs.length;
    const nClouds = Array.from({ length: table.count }, (_, k) => data[k * 16 + 4]).filter((v) => v === 0).length;
    console.log(JSON.stringify({ starsHeight: h, clouds: nClouds, objects: table.count, eye, steps, meanWhole, meanField }));
    const first = steps.find((s) => s.worst < 1e-3)!;
    expect(first.K).toBe(FIELD_SLABS);
    // and the census and the camera still give the recorded numbers
    steps.forEach((s, k) => expect(s.worst).toBeCloseTo(FIELD_SLABS_MEASURED.steps[k].worst, 9));
  });
});
