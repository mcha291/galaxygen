// The arms (BUILD_VIII row 108): the weight's arithmetic, the sparkle's determinism and placement, the light hook's
// patch, and the controls' defaults.

import { describe, expect, it } from "vitest";
import { fieldFragment } from "../FieldVolume";
import pinned from "../fieldFragment.s78.glsl?raw";
import { arms, interTint, shapeOf, tint } from "./arms";
import {
  armMap,
  armWinding,
  barFade,
  breakLines,
  ridgeLines,
  ringLight,
  ringNormalise,
  sharpen,
  type ArmGrid,
  type ArmShape,
} from "./armsField";
import { buildSparkle, brightness, shareAt, sparkleFlux, type SparkleShape } from "./armsSparkle";
import { MARCH_PATCHES, illGlsl, illustrativeFragment, occurrences } from "./index";

const G: ArmGrid = { nR: 120, nPhi: 180, rHi: 30 };
const ringMean = (a: ArrayLike<number>, i: number, P: number) => {
  let s = 0;
  for (let j = 0; j < P; j++) s += a[i * P + j];
  return s / P;
};

/** A two-armed log spiral's contrast, (R, phi) row-major: 1 + amp cos(2 (phi - k ln R)). */
function spiral(g: ArmGrid, k: number, amp: number, scale = 1): Float64Array {
  const out = new Float64Array(g.nR * g.nPhi);
  const dR = g.rHi / g.nR;
  for (let i = 0; i < g.nR; i++) {
    const R = (i + 0.5) * dR;
    for (let j = 0; j < g.nPhi; j++) {
      const phi = ((j + 0.5) * 2 * Math.PI) / g.nPhi;
      out[i * g.nPhi + j] = scale * (1 + amp * Math.cos(2 * (phi - k * Math.log(R))));
    }
  }
  return out;
}

const SHAPE: ArmShape = {
  gasMix: 0, power: 4, equalise: 0, floor: 0.4, knee: 3, cap: 3, start: 5, width: 1, extend: 0, young: 0.1,
  lineMix: 1, armWidth: 0.6, fragment: 0, fragScale: 1.5,
};

describe("the arms' weight (armsField.ts)", () => {
  it("normalises each ring by its own mean", () => {
    const n = ringNormalise(spiral(G, 3, 0.3, 7), G.nR, G.nPhi);
    for (const i of [10, 50, 110]) expect(ringMean(n, i, G.nPhi)).toBeCloseTo(1, 10);
  });

  it("raises to the power and keeps the ring's mean at 1", () => {
    const n = ringNormalise(spiral(G, 3, 0.3), G.nR, G.nPhi);
    const a = sharpen(n, G.nR, G.nPhi, 4);
    const i = 60;
    expect(ringMean(a, i, G.nPhi)).toBeCloseTo(1, 10);
    // a = n^4 / <n^4>: the ratio of two texels is the ratio of n to the fourth.
    const P = G.nPhi;
    expect(a[i * P + 3] / a[i * P + 50]).toBeCloseTo((n[i * P + 3] / n[i * P + 50]) ** 4, 8);
  });

  it("lays the floor: the gap at `floor` of a full ridge, the ring mean kept below the cap", () => {
    const P = 8;
    const share = Float64Array.from([1, 1, 0, 0, 0, 0, 0, 0]);
    const L = ringLight(share, 1, P, 0.25, 99);
    expect(L[2] / L[0]).toBeCloseTo(0.25, 12);
    expect(ringMean(L, 0, P)).toBeCloseTo(1, 12);
    // A cap binds the ridge.
    expect(Math.max(...ringLight(share, 1, P, 0.25, 1.5))).toBeCloseTo(1.5, 12);
  });

  it("fades in outside the bar: nothing inside the start, everything from start + width", () => {
    expect(barFade(4.9, 5, 1)).toBe(0);
    expect(barFade(5.5, 5, 1)).toBeCloseTo(0.5, 12);
    expect(barFade(6.01, 5, 1)).toBe(1);
    const n = ringNormalise(spiral(G, 3, 0.3), G.nR, G.nPhi);
    const m = armMap(n, G, SHAPE, 1);
    const ring = (r: number) => Math.round(r / (G.rHi / G.nR) - 0.5);
    for (let j = 0; j < G.nPhi; j++) {
      const o = (j * G.nR + ring(3)) * 4;
      expect([m[o], m[o + 1], m[o + 2], m[o + 3]]).toEqual([1, 0, 1, 0]);
    }
    const o = ring(10);
    let lo = Infinity;
    let hi = -Infinity;
    for (let j = 0; j < G.nPhi; j++) {
      lo = Math.min(lo, m[(j * G.nR + o) * 4]);
      hi = Math.max(hi, m[(j * G.nR + o) * 4]);
    }
    // A sinusoid's ridge stands 0.3 / (2 x 0.3 / sqrt 2) = 0.71 of a full one high: gap / ridge = 0.4 / (0.4 + 0.6 x 0.71).
    expect(lo / hi).toBeCloseTo(0.4 / (0.4 + 0.6 * Math.SQRT1_2), 2);
    expect(lo).toBeLessThan(1);
    expect(hi).toBeGreaterThan(1);
  });

  it("is neutral at strength 0", () => {
    const n = ringNormalise(spiral(G, 3, 0.3), G.nR, G.nPhi);
    const m = armMap(n, G, SHAPE, 0);
    for (let k = 0; k < m.length; k += 4) expect([m[k], m[k + 1], m[k + 2], m[k + 3]]).toEqual([1, 0, 1, 0]);
  });

  it("measures the arms' winding from the field", () => {
    const n = ringNormalise(spiral({ nR: 400, nPhi: 360, rHi: 30 }, 3, 0.3), 400, 360);
    const w = armWinding(n, { nR: 400, nPhi: 360, rHi: 30 }, 2);
    expect(w).not.toBeNull();
    expect(w!.k).toBeGreaterThan(2.3);
    expect(w!.k).toBeLessThan(3.7);
  });

  it("draws ridge lines of the slider's width across the arm", () => {
    const g: ArmGrid = { nR: 400, nPhi: 3600, rHi: 30 };
    const k = 3;
    const n = ringNormalise(spiral(g, k, 0.3), g.nR, g.nPhi);
    const lines = ridgeLines(n, g, 0.8, k);
    const i = Math.round(10 / 0.075);
    const R = (i + 0.5) * 0.075;
    const row = Array.from(lines.subarray(i * g.nPhi, (i + 1) * g.nPhi));
    const above = row.filter((v) => v >= 0.5 * Math.max(...row)).length;
    // Two arms; each above half its height over 0.8 kpc across, i.e. 0.8 / (R sin pitch) radians of azimuth.
    const sinPitch = 1 / Math.sqrt(1 + k * k);
    const expected = (2 * (0.8 / (R * sinPitch))) / ((2 * Math.PI) / g.nPhi);
    expect(above / expected).toBeGreaterThan(0.85);
    expect(above / expected).toBeLessThan(1.15);
  });

  it("breaks the lines deterministically into fragments", () => {
    const n = ringNormalise(spiral(G, 3, 0.3), G.nR, G.nPhi);
    const a = ridgeLines(n, G, 0.8, 3);
    const b = Float64Array.from(a);
    const c = Float64Array.from(a);
    breakLines(b, G, 0.5, 1);
    breakLines(c, G, 0.5, 1);
    expect(Array.from(b)).toEqual(Array.from(c));
    const sum = (x: Float64Array) => x.reduce((s, v) => s + v, 0);
    expect(sum(b)).toBeLessThan(0.8 * sum(a));
    expect(sum(b)).toBeGreaterThan(0.1 * sum(a));
  });
});

describe("the sparkle (armsSparkle.ts)", () => {
  const n = ringNormalise(spiral(G, 3, 0.3), G.nR, G.nPhi);
  const map = armMap(n, G, { ...SHAPE, start: 3, width: 0.5 }, 1);
  const shape: SparkleShape = { count: 6000, clump: 0.6, groupPc: 120, members: 8, ridge: 2, slope: 1.4, range: 20, rMax: 20, heightPc: 60 };

  it("is the same for the same inputs, and another for another seed", () => {
    const a = buildSparkle(map, G, shape, 1234);
    const b = buildSparkle(map, G, shape, 1234);
    for (const key of ["radius", "azimuth", "height", "weight"] as const) expect(Array.from(a[key])).toEqual(Array.from(b[key]));
    expect(Array.from(buildSparkle(map, G, shape, 99).radius)).not.toEqual(Array.from(a.radius));
  });

  it("lies on the ridges, not between the arms nor inside the start", () => {
    const s = buildSparkle(map, G, shape, 7);
    expect(s.radius.length).toBeGreaterThan(5000);
    let on = 0;
    let off = 0;
    let inside = 0;
    for (let i = 0; i < s.radius.length; i++) {
      const share = shareAt(map, G, s.radius[i], s.azimuth[i]);
      if (share > 0.5) on++;
      else if (share < 0.05) off++;
      if (s.radius[i] < 2.5) inside++;
    }
    expect(on).toBeGreaterThan(10 * Math.max(1, off));
    expect(inside).toBeLessThan(s.radius.length * 0.01);
  });

  it("has many faint points and few bright", () => {
    const w = Array.from(buildSparkle(map, G, shape, 7).weight);
    const faint = w.filter((v) => v < 2).length;
    const bright = w.filter((v) => v > 10).length;
    expect(faint).toBeGreaterThan(5 * bright);
    expect(Math.max(...w)).toBeLessThanOrEqual(20);
    expect(brightness(0, 1.4, 20)).toBe(1);
  });

  it("fades outward with the scale length from the start", () => {
    const f = sparkleFlux([1, 1, 1], [3, 5, 7.5], 10, [1, 2, 3], 5, 2.5);
    expect(Array.from(f.subarray(0, 3))).toEqual([10, 20, 30]);
    expect(f[3]).toBe(10);
    expect(f[6]).toBeCloseTo(10 * Math.exp(-1), 5);
  });
});

describe("the light hook (index.ts)", () => {
  it("patches the march once at an anchor that occurs once, and leaves the physical fragment as pinned", () => {
    const base = fieldFragment();
    expect(base).toBe(pinned);
    const anchor = "          float level = readLevel(rp.x);";
    expect(MARCH_PATCHES.some((p) => p.anchor === anchor)).toBe(true);
    expect(occurrences(base, anchor)).toBe(1);
    const ill = illustrativeFragment(base);
    expect(occurrences(ill, "          starsLight *= illLight(rp);\n" + anchor)).toBe(1);
    expect(illGlsl()).toContain("  vec3 illLight(vec2 rp) { return illArmsLight(rp); }");
    expect(fieldFragment()).toBe(pinned);
  });

  it("composes the young hook with the edge's", () => {
    expect(illGlsl()).toContain("illArmsYoung(rp)");
  });
});

describe("the arms' controls", () => {
  it("has every default and per-template value inside its range", () => {
    for (const c of arms.controls) {
      expect(c.default, c.key).toBeGreaterThanOrEqual(c.min);
      expect(c.default, c.key).toBeLessThanOrEqual(c.max);
      for (const [t, v] of Object.entries(c.perTemplate ?? {})) {
        expect(v, `${c.key} ${t}`).toBeGreaterThanOrEqual(c.min);
        expect(v, `${c.key} ${t}`).toBeLessThanOrEqual(c.max);
      }
      expect(c.about.length, c.key).toBeGreaterThan(10);
    }
    expect(new Set(arms.controls.map((c) => c.key)).size).toBe(arms.controls.length);
  });

  it("starts the shaping at the bar's end where the galaxy is barred, else at the inner radius", () => {
    const frame = (bar: number | null) => ({ header: { scalars: { bar_half_length: bar as number } }, arrays: {} });
    expect(shapeOf({ barfade: 1.2, inner: 2 }, frame(5)).start).toBeCloseTo(6, 12);
    expect(shapeOf({ barfade: 1.2, inner: 2 }, frame(null)).start).toBe(2);
  });

  it("tints with unit mean, lavender one way and warm the other", () => {
    for (const t of [tint([0.8, 1.04, 1.16], 0.7), interTint(0.5), interTint(-0.5)]) expect((t[0] + t[1] + t[2]) / 3).toBeCloseTo(1, 12);
    expect(interTint(-1)[0]).toBeGreaterThan(interTint(-1)[2]);
    expect(interTint(1)[2]).toBeGreaterThan(interTint(1)[1]);
    expect(interTint(0)).toEqual([1, 1, 1]);
  });
});
