import { DataUtils } from "three";
import { describe, expect, it } from "vitest";

import {
  CLOUD_RASTER,
  CLOUD_RASTER_BUDGET_BYTES,
  KEPT_RASTER_BYTES,
  MAG_PER_DEPTH,
  RENDER_GRID,
  cloudDepthScale,
  cloudRaster,
  finestRaster,
  keptCloudRaster,
  keptRasterBytes,
  packRaster,
  rasterKey,
  shareAt,
  texelArea,
} from "./cloudOpacity";
import { depthOf } from "./regimes";

// S64 (BUILD_III V6; RULING_S64 R4): the clouds' raster conserves what the census gives it - each cloud's A_V x area -
// to float32 rounding, at any resolution; the default resolution is the finest a 16 MiB float32 texture holds.

/** A hand-made census of three clouds on a 10 x 64 raster over R in [0, 10) kpc: a sub-texel one at R = 3.3, one that
 * spans several texels at R = 6, and one that straddles phi = 0 (it wraps). */
const THREE = {
  cloud_radius: [3.3, 6.0, 8.2],
  cloud_azimuth: [1.0, 2.5, 0.01],
  cloud_size: [20, 900, 700], // pc: the radius
  cloud_dust_extinction_v: [2.0, 0.5, 4.0],
  cloud_height: [0.05, -0.1, 0.2], // kpc
};
const avArea = (c: typeof THREE) => c.cloud_size.reduce((s, size, i) => s + c.cloud_dust_extinction_v[i] * Math.PI * (size / 1000) ** 2, 0);

function heldOf(av: Float32Array, width: number, height: number, rLo: number, rHi: number): number {
  const dR = (rHi - rLo) / width;
  const dPhi = (2 * Math.PI) / height;
  let held = 0;
  for (let i = 0; i < width; i += 1) for (let j = 0; j < height; j += 1) held += av[j * width + i] * texelArea(i, rLo, dR, dPhi);
  return held;
}

describe("the clouds' raster (S64, V6)", () => {
  it("conserves the census's A_V x area to float32 rounding: three clouds, one sub-texel, one split, one wrapping", () => {
    const got = cloudRaster(THREE, 0, 10, 10, 64);
    const want = avArea(THREE);
    expect(got.census).toBeCloseTo(want, 12);
    expect(got.outside).toBe(0);
    expect(got.split).toBe(2); // the 900 pc and the 700 pc clouds; the 20 pc one falls whole in its texel
    // My own sum over the texels, from the float32 values: the census's to float32 rounding.
    const held = heldOf(got.av, 10, 64, 0, 10);
    expect(Math.abs(held - want) / want).toBeLessThan(2e-7);
    expect(Math.abs(got.held - held) / want).toBeLessThan(1e-12);
    // The sub-texel cloud is in the one texel holding its centre: R 3.3 -> i 3, phi 1.0 -> j 1.
    const i = 3;
    const j = Math.floor(1.0 / ((2 * Math.PI) / 64));
    expect(got.av[j * 10 + i] * texelArea(i, 0, 1, (2 * Math.PI) / 64)).toBeCloseTo(2.0 * Math.PI * 0.02 ** 2, 9);
    // The wrapping cloud puts some of itself on both sides of phi = 0 (the last row and the first).
    const rowSum = (j: number) => Array.from({ length: 10 }, (_, i) => got.av[j * 10 + i]).reduce((a, b) => a + b, 0);
    expect(rowSum(0)).toBeGreaterThan(0);
    expect(rowSum(63)).toBeGreaterThan(0);
  });

  it("conserves at every resolution, and draws nothing for a cloud with no column or beyond the disc", () => {
    for (const [w, h] of [[1, 1], [37, 29], [400, 360]]) {
      const got = cloudRaster(THREE, 0, 10, w, h);
      const held = heldOf(got.av, w, h, 0, 10);
      expect(Math.abs(held - avArea(THREE)) / avArea(THREE)).toBeLessThan(2e-7);
    }
    const none = cloudRaster({ ...THREE, cloud_dust_extinction_v: [0, Number.NaN, -1] }, 0, 10, 10, 8);
    expect(none.census).toBe(0);
    expect(none.av.every((v) => v === 0)).toBe(true);
    const far = cloudRaster({ cloud_radius: [12], cloud_azimuth: [0], cloud_size: [10], cloud_dust_extinction_v: [1], cloud_height: [0] }, 0, 10, 10, 8);
    expect(far.outside).toBeCloseTo(far.census, 15);
    expect(far.av.every((v) => v === 0)).toBe(true);
  });

  it("spreads a large cloud by a uniform sphere's chord: its centre texel holds the most", () => {
    const big = cloudRaster({ cloud_radius: [5], cloud_azimuth: [Math.PI], cloud_size: [2000], cloud_dust_extinction_v: [1], cloud_height: [0] }, 0, 10, 40, 64);
    let best = -1;
    let at = -1;
    big.av.forEach((v, t) => {
      if (v > best) {
        best = v;
        at = t;
      }
    });
    const i = at % 40;
    expect(Math.abs(i - 20)).toBeLessThanOrEqual(1);
    // A sphere's face-on column at its centre is 1.5 x its disc's mean.
    expect(best).toBeGreaterThan(1.2);
    expect(best).toBeLessThan(1.6);
  });

  it("draws one cloud in a texel as itself, at its own height and extent, and several as one slab spanning them", () => {
    const got = cloudRaster(THREE, 0, 10, 10, 64);
    // The sub-texel cloud (R 3.3, phi 1.0) is alone in its texel: its height and its radius, kpc.
    const t = Math.floor(1.0 / ((2 * Math.PI) / 64)) * 10 + 3;
    expect(got.slab[2 * t]).toBeCloseTo(0.05, 6); // float32
    expect(got.slab[2 * t + 1]).toBeCloseTo(0.02, 6);
    // Every texel the 900 pc cloud alone touches is that cloud: -0.1 kpc, 0.9 kpc.
    const j = Math.floor(2.5 / ((2 * Math.PI) / 64));
    expect(got.slab[2 * (j * 10 + 6)]).toBeCloseTo(-0.1, 6);
    expect(got.slab[2 * (j * 10 + 6) + 1]).toBeCloseTo(0.9, 6);
    // An empty texel has no slab.
    expect([got.slab[0], got.slab[1]]).toEqual([0, 0]);
    // Two sub-texel clouds in one texel, A_V x area 1 : 3 at heights 0 and 0.1 kpc, radii 10 and 20 pc: the
    // A_V-weighted mean height, and the rms about it in quadrature with the mean radius.
    const two = cloudRaster(
      { cloud_radius: [5, 5.01], cloud_azimuth: [1, 1.001], cloud_size: [10, 20], cloud_dust_extinction_v: [4, 3], cloud_height: [0, 0.1] },
      0, 10, 10, 64,
    );
    const k = Math.floor(1 / ((2 * Math.PI) / 64)) * 10 + 5;
    const w = [4 * 0.01 ** 2, 3 * 0.02 ** 2]; // A_V x radius^2: the weights' ratio, 1 : 3
    const mean = (w[1] * 0.1) / (w[0] + w[1]);
    const rms2 = (w[0] * mean ** 2 + w[1] * (0.1 - mean) ** 2) / (w[0] + w[1]);
    const radius = (w[0] * 0.01 + w[1] * 0.02) / (w[0] + w[1]);
    expect(two.slab[2 * k]).toBeCloseTo(mean, 6);
    expect(two.slab[2 * k + 1]).toBeCloseTo(Math.sqrt(rms2 + radius ** 2), 6);
  });

  it("is the finest raster a 16 MiB float32 texture holds on the render grid: 5 texels a cell, 2000 x 1800", () => {
    expect(CLOUD_RASTER_BUDGET_BYTES).toBe(16 * 1024 * 1024);
    expect(CLOUD_RASTER).toBe(5);
    const bytes = (k: number) => RENDER_GRID.R * k * RENDER_GRID.phi * k * 4;
    expect(bytes(CLOUD_RASTER)).toBe(14_400_000);
    expect(bytes(CLOUD_RASTER)).toBeLessThanOrEqual(CLOUD_RASTER_BUDGET_BYTES);
    expect(bytes(CLOUD_RASTER + 1)).toBeGreaterThan(CLOUD_RASTER_BUDGET_BYTES);
    expect(finestRaster(48, 36)).toBe(49);
    expect(finestRaster(1e6, 1e6)).toBe(1);
  });

  it("turns A_V into each channel's depth as the diffuse dust does: A_V x A_lambda/A_V / 1.0857", () => {
    const ratio = [1.31, 1.0, 0.79];
    const scale = cloudDepthScale(ratio);
    for (let k = 0; k < 3; k += 1) {
      // The diffuse dust's depth of a column of 2 mag: -ln 10^(-0.4 x 2 x r).
      expect(2 * scale[k]).toBeCloseTo(depthOf(10 ** (-0.4 * 2 * ratio[k])), 12);
    }
    expect(MAG_PER_DEPTH).toBeCloseTo(1.0857362, 7);
    expect(cloudDepthScale(null)).toEqual([0, 0, 0]);
    expect(cloudDepthScale([1, null, Number.NaN])).toEqual([1 / MAG_PER_DEPTH, 0, 0]);
  });

  it("reads the diffuse share, and all of the dust is diffuse where none is published", () => {
    expect(shareAt([0.4, Number.NaN, -1], 0)).toBe(0.4);
    expect(shareAt([0.4, Number.NaN, -1], 1)).toBe(1);
    expect(shareAt([0.4, Number.NaN, -1], 2)).toBe(1);
    expect(shareAt(null, 3)).toBe(1);
  });
});

describe("the raster kept across remounts (S76, D240 F1)", () => {
  const toHalf = DataUtils.toHalfFloat;
  it("returns the kept raster for the same census content and shape, in a new object as a second answer would be", () => {
    const first = keptCloudRaster(THREE, 0, 10, 10, 64, { verticalCap: 0.06, elongation: 1 }, toHalf);
    const again = keptCloudRaster(structuredClone(THREE), 0, 10, 10, 64, { verticalCap: 0.06, elongation: 1 }, toHalf);
    expect(again).toBe(first);
    // What is kept is what the field reads, the same bits as a fresh build packed: the A_V, the slab's halves, its top.
    const fresh = packRaster(cloudRaster(THREE, 0, 10, 10, 64, { verticalCap: 0.06, elongation: 1 }), toHalf);
    expect(Array.from(first.av)).toEqual(Array.from(fresh.av));
    expect(Array.from(first.halves)).toEqual(Array.from(fresh.halves));
    expect(first.top).toBe(fresh.top);
    expect(first.top).toBeGreaterThan(0);
    expect([first.width, first.height, first.census, first.held, first.outside, first.split]).toEqual([fresh.width, fresh.height, fresh.census, fresh.held, fresh.outside, fresh.split]);
    // The float32 slab the halves are made from is not kept (the review's G6).
    expect(Object.keys(first).sort()).toEqual(["av", "census", "halves", "height", "held", "outside", "split", "top", "width"]);
  });
  it("builds again when a column's value, a radius, the texels, the cap or the elongation differ", () => {
    const base = rasterKey(THREE, 0, 10, 10, 64, { verticalCap: 0.06, elongation: 1 });
    const moved = { ...THREE, cloud_height: [0.05, -0.1, 0.2000001] };
    expect(rasterKey(moved, 0, 10, 10, 64, { verticalCap: 0.06, elongation: 1 })).not.toBe(base);
    expect(rasterKey(THREE, 0.5, 10, 10, 64, { verticalCap: 0.06, elongation: 1 })).not.toBe(base);
    expect(rasterKey(THREE, 0, 10, 20, 64, { verticalCap: 0.06, elongation: 1 })).not.toBe(base);
    expect(rasterKey(THREE, 0, 10, 10, 64, { verticalCap: 0.07, elongation: 1 })).not.toBe(base);
    expect(rasterKey(THREE, 0, 10, 10, 64, { verticalCap: 0.06, elongation: 0.5 })).not.toBe(base);
    expect(rasterKey({ ...THREE, cloud_axis_ratio: [1, 2, 3] }, 0, 10, 10, 64, { verticalCap: 0.06, elongation: 1 })).not.toBe(base);
    expect(rasterKey(new Proxy(THREE, {}), 0, 10, 10, 64, { verticalCap: 0.06, elongation: 1 })).toBe(base);
  });
  it("keeps at most the cap's bytes, the least recently asked dropped first, and never one raster over the cap alone", () => {
    expect(KEPT_RASTER_BYTES).toBe(96 * 1024 * 1024);
    // A 10 x 64 raster kept is 640 float32 A_V and 1280 half floats: 5120 bytes. A cap of two and a half holds two.
    const one = 10 * 64 * (4 + 2 * 2);
    const cap = 2.5 * one;
    const a = keptCloudRaster(THREE, 0, 21, 10, 64, {}, toHalf, cap);
    const b = keptCloudRaster(THREE, 0, 22, 10, 64, {}, toHalf, cap);
    expect(a.av.byteLength + a.halves.byteLength).toBe(one);
    expect(keptCloudRaster(THREE, 0, 21, 10, 64, {}, toHalf, cap)).toBe(a); // a asked again: b is now the oldest
    keptCloudRaster(THREE, 0, 23, 10, 64, {}, toHalf, cap); // c: over the cap, b dropped
    expect(keptRasterBytes()).toBeLessThanOrEqual(cap);
    expect(keptCloudRaster(THREE, 0, 21, 10, 64, {}, toHalf, cap)).toBe(a);
    const b2 = keptCloudRaster(THREE, 0, 22, 10, 64, {}, toHalf, cap);
    expect(b2).not.toBe(b);
    expect(Array.from(b2.halves)).toEqual(Array.from(b.halves)); // built again, the same bits
    // A cap under one raster keeps nothing: the next ask builds afresh, and nothing is held.
    const lone = keptCloudRaster(THREE, 0, 24, 10, 64, {}, toHalf, one / 2);
    expect(keptRasterBytes()).toBe(0);
    expect(keptCloudRaster(THREE, 0, 24, 10, 64, {}, toHalf, one / 2)).not.toBe(lone);
  });
});
