import { describe, expect, it } from "vitest";

import type { Columns, FieldsPayload } from "../api";
import { srgbToLinear } from "./colors";
import {
  CELL_RINGS,
  CELL_SECTORS,
  CIRCLE_SEGMENTS,
  CLOUD_MIN_PX,
  FIELD_LAYERS,
  GREY_STOPS,
  WHERE_LEVEL,
  WHERE_STOPS,
  brightestLayers,
  cellOutlines,
  cloudColors,
  cloudMarkerPx,
  depthPeak,
  diagnosticOn,
  dustRamp,
  marchWanted,
  rowsInWindow,
  whereLevel,
  whereTint,
} from "./components";
import { LIGHT_PER_LSUN_PC2 } from "./FieldVolume";
import { layerShare } from "./regimes";
import { TUNING_DEFAULTS } from "./tuning";

// The model's own greys and magma stops (model/galaxy/core/cmaps.py), as /api/fields publishes them.
const META = {
  fields: [
    { name: "dust_extinction_v", ramp: { kind: "ramp", cmap: "greys", scale: "linear", lo: null, hi: null } },
    { name: "dust_surface_density", ramp: { kind: "ramp", cmap: "greys", scale: "log", lo: null, hi: null } },
    { name: "cloud_mass", meaningful_zero: true, ramp: { kind: "ramp", cmap: "magma", scale: "log", lo: null, hi: null } },
  ],
  cmaps: {
    greys: { stops: ["#ffffff", "#f0f0f0", "#d9d9d9", "#bdbdbd", "#969696", "#737373", "#525252", "#252525", "#000000"], diverging: false },
    magma: { stops: ["#000004", "#180f3d", "#440f76", "#721f81", "#9e2f7f", "#cd4071", "#f1605d", "#fd9668", "#feca8d", "#fcfdbf"], diverging: false },
  },
} as unknown as FieldsPayload;

const OFF = { stars: 0, gas: 0, dust: 0, dustDepth: 0, where: 0, whereStops: GREY_STOPS };

describe("the march's layers (D205)", () => {
  it("are all on in the field, the dust acting, nothing diagnostic", () => {
    expect(FIELD_LAYERS).toEqual({ stars: 1, gas: 1, dust: 1, dustDepth: 1, where: 0, whereStops: GREY_STOPS });
    expect(GREY_STOPS.length).toBe(WHERE_STOPS);
  });

  it("leave a sub-step's light and depth bit for bit the S46 arithmetic at the field's values", () => {
    // The fragment's per-sub-step terms in float32, before (S46) and after (S50) at FIELD_LAYERS: each new
    // factor is ×1 and the new term adds 0, which IEEE arithmetic leaves exact for every finite value.
    const f = Math.fround;
    const mul = (a: number, b: number) => f(f(a) * f(b));
    const L = FIELD_LAYERS;
    const level = whereLevel(L.where, 3.2, LIGHT_PER_LSUN_PC2);
    expect(level).toBe(0);
    for (const [bulge, n, col, plane, scat, therm, hii, dig, ring] of [
      [3.7e-3, 3, 0.0123, 812.5, 4.1, 0.02, 63.1, 5.5, 0.71],
      [1e-9, 8, 7.9e-7, 1e-3, 0, 0, 1e5, 0, 2.5],
      [0, 1, 0.5, 0, 1e-12, 3.3, 0, 7.7e-3, 0],
    ]) {
      expect(f(mul(bulge, L.stars) / n)).toBe(f(f(bulge) / n));
      expect(mul(col, L.stars)).toBe(f(col));
      expect(mul(col, L.gas)).toBe(f(col));
      const dustLight = mul(f(scat + therm), col);
      expect(mul(dustLight, L.dust)).toBe(dustLight);
      const tau = mul(ring, col);
      expect(mul(tau, L.dustDepth)).toBe(tau);
      const emitted = f(f(plane * col) + f(hii * col) + f(dig * col));
      const tint = whereTint(L.whereStops, 0);
      expect(f(emitted + mul(mul(level, tint[0]), f(tau / 3)))).toBe(emitted);
    }
  });

  it("are all off in the brightest mode by default, and the march is not mounted", () => {
    expect(marchWanted(TUNING_DEFAULTS)).toBe(false);
    expect(diagnosticOn(TUNING_DEFAULTS)).toBe(false);
    expect(brightestLayers(TUNING_DEFAULTS, dustRamp(META))).toEqual(OFF);
  });

  it("switch each layer on at its intensity; the dust's intensity never scales its depth", () => {
    const t = { ...TUNING_DEFAULTS, compStars: true, compGas: true, compDust: true, starsIntensity: 2, gasIntensity: 0.5, dustIntensity: 4 };
    expect(brightestLayers(t, dustRamp(META))).toEqual({ ...OFF, stars: 2, gas: 0.5, dust: 4, dustDepth: 1 });
    expect(marchWanted(t)).toBe(true);
    expect(diagnosticOn(t)).toBe(false);
  });

  it("draw the dust where it is at its intensity, dimming nothing, and nothing without a declared ramp", () => {
    const t = { ...TUNING_DEFAULTS, compDust: true, dustReading: "where" as const, dustIntensity: 2 };
    expect(brightestLayers(t, dustRamp(META))).toEqual({ ...OFF, where: 2 });
    expect(brightestLayers(t, null)).toEqual(OFF);
    expect(diagnosticOn(t)).toBe(true);
    expect(diagnosticOn({ ...TUNING_DEFAULTS, compClouds: true })).toBe(true);
    expect(diagnosticOn({ ...TUNING_DEFAULTS, compCells: true })).toBe(true);
  });
});

describe("the dust diagnostic's normalisation (a display choice)", () => {
  // Three R cells of the ring texture's depth row (RGBA): channel means 0.5, 3.2 and 1.
  const rings = new Float32Array([0.6, 0.5, 0.4, 0, 3.6, 3.2, 2.8, 0, 1, 1, 1, 0, /* the next row, not depth */ 99, 99, 99, 0]);

  it("is the depth ring's largest channel-mean face-on optical depth", () => {
    expect(depthPeak(rings, 3)).toBeCloseTo(3.2, 6);
    expect(depthPeak(new Float32Array(12), 3)).toBe(0);
    expect(depthPeak(new Float32Array([Number.NaN, 1, 1, 0]), 1)).toBe(0);
  });

  it("draws the densest ring's face-on column at WHERE_LEVEL × intensity, before tone mapping, at zero stops", () => {
    expect(WHERE_LEVEL).toBe(0.5);
    const peak = depthPeak(rings, 3);
    // A face-on ray takes the whole layer's column, Σ cDust = 1 (regimes.ts layerShare over all heights), so τ = peak;
    // the march multiplies by the field's gain, LIGHT_PER_LSUN_PC2 at a field gain of 1 and zero stops.
    expect(layerShare(-1e3, 1e3, 0.2)).toBeCloseTo(1, 8); // tanh clamped at ±10: 1 − 4e−9
    for (const intensity of [1, 0.25, 4]) {
      const drawn = whereLevel(intensity, peak, LIGHT_PER_LSUN_PC2) * peak * whereTint(GREY_STOPS, 1)[0] * LIGHT_PER_LSUN_PC2;
      expect(drawn).toBeCloseTo(WHERE_LEVEL * intensity, 12);
    }
    expect(whereLevel(1, 0, LIGHT_PER_LSUN_PC2)).toBe(0); // no dust: nothing drawn, no division by zero
    expect(whereLevel(0, 3.2, LIGHT_PER_LSUN_PC2)).toBe(0);
  });

  it("is painted by a declared ramp: a coloured one read at τ / τ_peak, grey ones kept grey", () => {
    // The model's two dust ramps are both greys: dust_surface_density's is kept, every stop white.
    expect(dustRamp(META)).toEqual({ field: "dust_surface_density", stops: GREY_STOPS, coloured: false });
    // A coloured dust_extinction_v ramp wins; its stops are its cmap's, as linear light, from τ = 0 to the peak.
    const coloured = {
      ...META,
      fields: [{ name: "dust_extinction_v", ramp: { kind: "ramp", cmap: "magma", scale: "linear", lo: null, hi: null } }, ...META.fields.slice(1)],
    } as unknown as FieldsPayload;
    const r = dustRamp(coloured)!;
    expect(r.field).toBe("dust_extinction_v");
    expect(r.coloured).toBe(true);
    expect(r.stops.length).toBe(WHERE_STOPS);
    expect(r.stops[0][2]).toBeCloseTo(srgbToLinear(4 / 255), 9);
    expect(r.stops[WHERE_STOPS - 1][0]).toBeCloseTo(srgbToLinear(0xfc / 255), 9);
    // Grey first, coloured second: the coloured one is used.
    const second = {
      ...META,
      fields: [META.fields[0], { name: "dust_surface_density", ramp: { kind: "ramp", cmap: "magma", scale: "log", lo: null, hi: null } }],
    } as unknown as FieldsPayload;
    expect(dustRamp(second)!.field).toBe("dust_surface_density");
    expect(dustRamp(second)!.coloured).toBe(true);
    expect(dustRamp({ fields: [], cmaps: {} } as unknown as FieldsPayload)).toBeNull();
  });

  it("reads the stops linearly, clamped at the ramp's ends (the shader's whereTint)", () => {
    const stops = Array.from({ length: WHERE_STOPS }, (_, i) => [i, 2 * i, 0] as [number, number, number]);
    expect(whereTint(stops, 0)).toEqual([0, 0, 0]);
    expect(whereTint(stops, 1)).toEqual([7, 14, 0]);
    expect(whereTint(stops, 2)).toEqual([7, 14, 0]);
    expect(whereTint(stops, -1)).toEqual([0, 0, 0]);
    expect(whereTint(stops, 0.5)[0]).toBeCloseTo(3.5, 12);
  });
});


describe("the cell outlines", () => {
  it("are the level-0 grid: 33 circles from R.lo to R.hi and 32 spokes, in the disc plane", () => {
    const { positions, radii, circles, spokes } = cellOutlines(0.5, 30.5);
    expect([CELL_RINGS, CELL_SECTORS]).toEqual([32, 32]);
    expect(circles).toBe(33);
    expect(spokes).toBe(32);
    expect(radii[0]).toBe(0.5);
    expect(radii[32]).toBe(30.5);
    for (let i = 0; i <= 32; i += 1) expect(radii[i]).toBeCloseTo(0.5 + (30 * i) / 32, 12);
    expect(positions.length).toBe((33 * CIRCLE_SEGMENTS + 32) * 6);
    for (let i = 1; i < positions.length; i += 3) expect(positions[i]).toBe(0);
    // Each circle's vertices sit at its radius; each spoke runs from R.lo to R.hi along its sector edge.
    for (let c = 0; c < 33; c += 1) {
      const o = c * CIRCLE_SEGMENTS * 6;
      expect(Math.hypot(positions[o], positions[o + 2])).toBeCloseTo(radii[c], 5);
      expect(Math.hypot(positions[o + 3], positions[o + 5])).toBeCloseTo(radii[c], 5);
    }
    for (let k = 0; k < 32; k += 1) {
      const o = (33 * CIRCLE_SEGMENTS + k) * 6;
      const phi = (2 * Math.PI * k) / 32;
      expect(Math.hypot(positions[o], positions[o + 2])).toBeCloseTo(0.5, 5);
      expect(Math.hypot(positions[o + 3], positions[o + 5])).toBeCloseTo(30.5, 5);
      expect(Math.atan2(-positions[o + 5], positions[o + 3])).toBeCloseTo(phi > Math.PI ? phi - 2 * Math.PI : phi, 5);
    }
  });
});

describe("the cloud markers", () => {
  it("are the cloud's diameter projected at its depth, never under 2 px", () => {
    expect(CLOUD_MIN_PX).toBe(2);
    // A 50 pc radius cloud, 1 kpc away, with 1000 px per unit at unit depth: 0.1 kpc × 1000 / 1 = 100 px.
    expect(cloudMarkerPx(50, 1, 1000)).toBeCloseTo(100, 12);
    expect(cloudMarkerPx(50, 2, 1000)).toBeCloseTo(50, 12);
    expect(cloudMarkerPx(10, 40, 1000)).toBe(2); // 0.5 px: the floor
    expect(cloudMarkerPx(10, 40, 1000, 3)).toBe(3);
    expect(cloudMarkerPx(10, 0, 1000)).toBe(2); // at or behind the eye
    expect(cloudMarkerPx(Number.NaN, 1, 1000)).toBe(2);
  });

  it("are painted by cloud_mass's declared ramp, bounds over the whole census, times the brightness", () => {
    const columns = { cloud_mass: new Float64Array([1e3, 1e5, 1e7, Number.NaN]) } as unknown as Columns;
    const rgba = cloudColors(META, columns, 2);
    expect(rgba.length).toBe(16);
    const low = srgbToLinear(0 / 255) * 2;
    expect(rgba[0]).toBeCloseTo(low, 6); // the log ramp's floor is the lowest mass: magma's first stop
    expect(rgba[8]).toBeCloseTo(srgbToLinear(0xfc / 255) * 2, 6); // the highest: its last
    expect(rgba[3]).toBe(1);
    expect(rgba[15]).toBe(0); // no mass: not drawn (rule B9)
  });

  it("are cut to the footprint by radius and azimuth", () => {
    const rows = rowsInWindow([1, 5, 9, 5], [0.1, 1, 1, 3], { r_min: 4, r_max: 10, phi_min: 0.5, phi_max: 2 });
    expect(Array.from(rows)).toEqual([1, 2]);
  });
});
