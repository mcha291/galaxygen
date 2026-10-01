import { describe, expect, it } from "vitest";

import type { Columns, FieldsPayload } from "../api";
import { srgbToLinear } from "./colors";
import {
  CELL_RINGS,
  CELL_SECTORS,
  CIRCLE_SEGMENTS,
  CLOUD_MIN_PX,
  FIELD_LAYERS,
  WHERE_PER_TAU,
  brightestLayers,
  cellOutlines,
  cloudColors,
  cloudMarkerPx,
  diagnosticOn,
  dustTint,
  marchWanted,
  rowsInWindow,
} from "./components";
import { LIGHT_PER_LSUN_PC2 } from "./FieldVolume";
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

describe("the march's layers (D205)", () => {
  it("are all on in the field, the dust acting, nothing diagnostic", () => {
    expect(FIELD_LAYERS).toEqual({ stars: 1, gas: 1, dust: 1, dustDepth: 1, where: [0, 0, 0] });
  });

  it("leave a sub-step's light and depth bit for bit the S46 arithmetic at the field's values", () => {
    // The fragment's per-sub-step terms in float32, before (S46) and after (S50) at FIELD_LAYERS: each new
    // factor is ×1 and the new term adds 0, which IEEE arithmetic leaves exact for every finite value.
    const f = Math.fround;
    const mul = (a: number, b: number) => f(f(a) * f(b));
    const L = FIELD_LAYERS;
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
      expect(f(emitted + mul(L.where[0], f(tau / 3)))).toBe(emitted);
    }
  });

  it("are all off in the brightest mode by default, and the march is not mounted", () => {
    expect(marchWanted(TUNING_DEFAULTS)).toBe(false);
    expect(diagnosticOn(TUNING_DEFAULTS)).toBe(false);
    expect(brightestLayers(TUNING_DEFAULTS, [1, 1, 1])).toEqual({ stars: 0, gas: 0, dust: 0, dustDepth: 0, where: [0, 0, 0] });
  });

  it("switch each layer on at its intensity; the dust's intensity never scales its depth", () => {
    const t = { ...TUNING_DEFAULTS, compStars: true, compGas: true, compDust: true, starsIntensity: 2, gasIntensity: 0.5, dustIntensity: 4 };
    expect(brightestLayers(t, [1, 1, 1])).toEqual({ stars: 2, gas: 0.5, dust: 4, dustDepth: 1, where: [0, 0, 0] });
    expect(marchWanted(t)).toBe(true);
    expect(diagnosticOn(t)).toBe(false);
  });

  it("draw the dust where it is in one tint per unit depth, and dim nothing", () => {
    const t = { ...TUNING_DEFAULTS, compDust: true, dustReading: "where" as const, dustIntensity: 2 };
    const layers = brightestLayers(t, [1, 0.5, 0.25]);
    expect(layers).toEqual({ stars: 0, gas: 0, dust: 0, dustDepth: 0, where: [800, 400, 200] });
    // A column of unit depth draws at unit linear intensity at zero stops and intensity 1: WHERE_PER_TAU × the field's gain.
    expect(WHERE_PER_TAU * LIGHT_PER_LSUN_PC2).toBe(1);
    expect(diagnosticOn(t)).toBe(true);
    expect(diagnosticOn({ ...TUNING_DEFAULTS, compClouds: true })).toBe(true);
    expect(diagnosticOn({ ...TUNING_DEFAULTS, compCells: true })).toBe(true);
  });

  it("take the dust's tint from its declared ramp, at the end that draws on black", () => {
    expect(dustTint(META)).toEqual({ field: "dust_extinction_v", tint: [1, 1, 1] });
    const reversed = { ...META, cmaps: { ...META.cmaps, greys: { stops: ["#000000", "#808080"], diverging: false } } } as unknown as FieldsPayload;
    const g = srgbToLinear(0x80 / 255);
    expect(dustTint(reversed)!.tint).toEqual([g, g, g]);
    expect(dustTint({ fields: META.fields.slice(1), cmaps: META.cmaps } as FieldsPayload)!.field).toBe("dust_surface_density");
    expect(dustTint({ fields: [], cmaps: {} } as unknown as FieldsPayload)).toBeNull();
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
