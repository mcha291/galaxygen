// S78 (R2): cloudRaster's sample azimuths' cosines and sines hoisted out of the split loop into a per-cloud table. The
// raster must be the same bits as before: here the pre-hoist function, copied from cloudOpacity.ts as it was at S77
// (de6344f), is the reference, and every float of the raster - the A_V, the slab, the counts, and the slab's half
// floats as the field packs them - is compared with Object.is on a synthetic census built to reach every branch:
// sub-texel clouds, split ones, clouds wrapping phi = 0, clouds round the centre whose span is the whole ring, clouds
// past the raster's radii, no-column clouds, and ellipses at many angles and ratios under each shape.
import { DataUtils } from "three";
import { describe, expect, it } from "vitest";

import { type CloudColumns, type CloudRaster, type RasterShape, SPLIT_SAMPLES, cloudEllipse, cloudRaster, packRaster, texelArea } from "./cloudOpacity";

/** cloudRaster as it was before the hoist (cloudOpacity.ts at de6344f), verbatim but for its name. */
function referenceRaster(clouds: CloudColumns, rLo: number, rHi: number, width: number, height: number, shape: RasterShape = {}): CloudRaster {
  const cap = shape.verticalCap ?? Infinity;
  const elongation = shape.elongation ?? 0;
  const ratios = clouds.cloud_axis_ratio;
  const angles = clouds.cloud_angle;
  const shaped = elongation > 0 && Boolean(ratios && angles);
  const dR = (rHi - rLo) / width;
  const dPhi = (2 * Math.PI) / height;
  const sum = new Float64Array(width * height); // A_V x area per texel, mag kpc^2
  const slot = new Int32Array(width * height).fill(-1);
  const wz: number[] = [];
  const wz2: number[] = [];
  const ws: number[] = [];
  const least: number[] = [];
  let z = 0;
  let s = 0;
  let sv = 0;
  const deposit = (t: number, part: number) => {
    sum[t] += part;
    let k = slot[t];
    if (k < 0) {
      k = slot[t] = wz.length;
      wz.push(0);
      wz2.push(0);
      ws.push(0);
      least.push(Infinity);
    }
    wz[k] += part * z;
    wz2[k] += part * z * z;
    ws[k] += part * sv;
    if (sv < least[k]) least[k] = sv;
  };
  let census = 0;
  let outside = 0;
  let split = 0;
  const texelOf = (x: number, y: number): number => {
    const r = Math.hypot(x, y);
    const i = Math.floor((r - rLo) / dR);
    if (!(i >= 0 && i < width)) return -1;
    let phi = Math.atan2(y, x);
    if (phi < 0) phi += 2 * Math.PI;
    const j = Math.min(height - 1, Math.floor(phi / dPhi));
    return j * width + i;
  };
  const n = clouds.cloud_radius.length;
  for (let c = 0; c < n; c += 1) {
    const av = Number(clouds.cloud_dust_extinction_v[c]);
    s = Number(clouds.cloud_size[c]) / 1000;
    sv = Math.min(s, cap);
    z = Number(clouds.cloud_height[c]);
    const r = Number(clouds.cloud_radius[c]);
    const phi = Number(clouds.cloud_azimuth[c]);
    if (!(av > 0) || !(s > 0) || !Number.isFinite(r) || !Number.isFinite(phi) || !Number.isFinite(z)) continue;
    const total = av * Math.PI * s * s;
    census += total;
    const x = r * Math.cos(phi);
    const y = r * Math.sin(phi);
    const side = Math.min(dR, Math.max(r, 0.5 * dR) * dPhi);
    const ell = shaped ? cloudEllipse(Number(ratios![c]), Number(angles![c]), elongation) : null;
    const q = ell ? ell.ratio : 1;
    const along = s * Math.sqrt(q);
    const across = s / Math.sqrt(q);
    const e1x = ell ? Math.cos(ell.angle) * Math.cos(phi) - Math.sin(ell.angle) * Math.sin(phi) : 1;
    const e1y = ell ? Math.cos(ell.angle) * Math.sin(phi) + Math.sin(ell.angle) * Math.cos(phi) : 0;
    if (2 * along < side) {
      const t = texelOf(x, y);
      if (t < 0) outside += total;
      else deposit(t, total);
      continue;
    }
    split += 1;
    const i0 = Math.floor((Math.max(0, r - along) - rLo) / dR);
    const i1 = Math.floor((r + along - rLo) / dR);
    const half = along < r ? Math.asin(along / r) : Math.PI;
    let j0 = Math.floor((phi - half) / dPhi);
    let j1 = Math.floor((phi + half) / dPhi);
    if (j1 - j0 + 1 >= height) {
      j0 = 0;
      j1 = height - 1;
    }
    const at: number[] = [];
    const weight: number[] = [];
    let w = 0;
    const m = SPLIT_SAMPLES;
    for (let i = i0; i <= i1; i += 1) {
      for (let j = j0; j <= j1; j += 1) {
        let got = 0;
        for (let a = 0; a < m; a += 1) {
          const ra = rLo + (i + (a + 0.5) / m) * dR;
          if (!(ra > 0)) continue;
          for (let b = 0; b < m; b += 1) {
            const pb = (j + (b + 0.5) / m) * dPhi;
            const dx = ra * Math.cos(pb) - x;
            const dy = ra * Math.sin(pb) - y;
            const rho2 = q === 1 ? (dx * dx + dy * dy) / (s * s) : ((dx * e1x + dy * e1y) / along) ** 2 + ((dy * e1x - dx * e1y) / across) ** 2;
            if (rho2 < 1) got += Math.sqrt(1 - rho2) * ra;
          }
        }
        if (!(got > 0)) continue;
        at.push(i >= 0 && i < width ? (((j % height) + height) % height) * width + i : -1);
        weight.push(got);
        w += got;
      }
    }
    if (!(w > 0)) {
      const t = texelOf(x, y);
      if (t < 0) outside += total;
      else deposit(t, total);
      continue;
    }
    for (let q = 0; q < at.length; q += 1) {
      const part = (total * weight[q]) / w;
      if (at[q] < 0) outside += part;
      else deposit(at[q], part);
    }
  }
  const av = new Float32Array(width * height);
  const slab = new Float32Array(width * height * 2);
  let held = 0;
  for (let i = 0; i < width; i += 1) {
    const area = texelArea(i, rLo, dR, dPhi);
    for (let j = 0; j < height; j += 1) {
      const t = j * width + i;
      if (sum[t] === 0) continue;
      av[t] = sum[t] / area;
      held += av[t] * area;
      const k = slot[t];
      const mean = wz[k] / sum[t];
      const spread = Math.max(0, wz2[k] / sum[t] - mean * mean);
      const radius = ws[k] / sum[t];
      slab[2 * t] = mean;
      slab[2 * t + 1] = Math.max(Math.sqrt(spread + radius * radius), least[k]);
    }
  }
  return { av, width, height, rLo, rHi, census, held, outside, split, slab };
}

/** A deterministic census (mulberry32): `n` clouds across and past [rLo, rHi), at every size and shape. */
function census(n: number, seed: number, rLo: number, rHi: number, f4: boolean): CloudColumns {
  let t = seed >>> 0;
  const rand = () => {
    t = (t + 0x6d2b79f5) >>> 0;
    let x = Math.imul(t ^ (t >>> 15), 1 | t);
    x ^= x + Math.imul(x ^ (x >>> 7), 61 | x);
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
  const make = () => (f4 ? new Float32Array(n) : new Float64Array(n));
  const c = {
    cloud_radius: make(), cloud_azimuth: make(), cloud_size: make(), cloud_dust_extinction_v: make(), cloud_height: make(),
    cloud_axis_ratio: make(), cloud_angle: make(),
  };
  for (let k = 0; k < n; k += 1) {
    const kind = k % 10;
    // radii: most inside, some at the centre, some past either edge
    c.cloud_radius[k] = kind === 0 ? 0.05 + 0.3 * rand() : kind === 1 ? rHi - 0.2 + 0.6 * rand() : rLo + (rHi - rLo) * rand();
    // azimuths: anywhere, and some just either side of phi = 0
    c.cloud_azimuth[k] = kind === 2 ? 2 * Math.PI - 0.01 * rand() : kind === 3 ? 0.01 * rand() : 2 * Math.PI * rand();
    // sizes, pc: from far under a texel to many texels across
    c.cloud_size[k] = kind === 4 ? 2 + 10 * rand() : kind === 5 ? 300 + 600 * rand() : 20 + 150 * rand();
    c.cloud_dust_extinction_v[k] = kind === 6 && rand() < 0.3 ? (rand() < 0.5 ? 0 : Number.NaN) : 0.05 + 3 * rand();
    c.cloud_height[k] = (rand() - 0.5) * 0.2;
    c.cloud_axis_ratio[k] = kind === 7 ? 1 : 1 + 4 * rand();
    c.cloud_angle[k] = (rand() - 0.5) * 2 * Math.PI;
  }
  return c;
}

function expectSameBits(got: CloudRaster, want: CloudRaster) {
  for (const k of ["width", "height", "rLo", "rHi", "census", "held", "outside", "split"] as const) expect(Object.is(got[k], want[k]), k).toBe(true);
  expect(got.av.length).toBe(want.av.length);
  expect(got.slab.length).toBe(want.slab.length);
  let differ = 0;
  for (let t = 0; t < want.av.length; t += 1) if (!Object.is(got.av[t], want.av[t])) differ += 1;
  for (let t = 0; t < want.slab.length; t += 1) if (!Object.is(got.slab[t], want.slab[t])) differ += 1;
  expect(differ).toBe(0);
  // the field's packed form: the slab's half floats and its top, the same too
  const p = packRaster(got, DataUtils.toHalfFloat);
  const q = packRaster(want, DataUtils.toHalfFloat);
  expect(Object.is(p.top, q.top)).toBe(true);
  let halves = 0;
  for (let t = 0; t < q.halves.length; t += 1) if (p.halves[t] !== q.halves[t]) halves += 1;
  expect(halves).toBe(0);
}

const SHAPES: [string, RasterShape][] = [
  ["round, no cap", {}],
  ["the published ellipses, the Milky Way's cap", { elongation: 1, verticalCap: 1.7627 * 0.034 }],
  ["half the elongation", { elongation: 0.5, verticalCap: 0.08 }],
];

describe("cloudRaster with its trig hoisted (S78, R2): the same bits as before", () => {
  for (const [name, shape] of SHAPES) {
    it(`on a 600-cloud float32 census over a 0-20 kpc raster, ${name}`, () => {
      const clouds = census(600, 78, 0, 20, true);
      const got = cloudRaster(clouds, 0, 20, 200, 180, shape);
      const want = referenceRaster(clouds, 0, 20, 200, 180, shape);
      expect(want.split).toBeGreaterThan(100); // the split loop is the hoisted one: most of the census goes through it
      expectSameBits(got, want);
    });
  }

  it("on a float64 census over a raster that starts off the centre, at odd texel counts", () => {
    const clouds = census(400, 4414, 0.6, 15.3, false);
    for (const [, shape] of SHAPES) expectSameBits(cloudRaster(clouds, 0.6, 15.3, 157, 211, shape), referenceRaster(clouds, 0.6, 15.3, 157, 211, shape));
  });
});
