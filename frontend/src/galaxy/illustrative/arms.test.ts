// The arms (BUILD_VIII row 108): the weight's arithmetic, the sparkle's determinism and placement, the light hook's
// patch, and the controls' defaults.

import { describe, expect, it } from "vitest";
import { fieldFragment } from "../FieldVolume";
import pinned from "../fieldFragment.s78.glsl?raw";
import { arms, barOf, barUniforms, interTint, shapeOf, tint } from "./arms";
import {
  YOUNG_CAP,
  armMap,
  armPlanes,
  armShare,
  armWinding,
  smoothstep,
  barFade,
  breakLines,
  ridgeLines,
  ringLight,
  ringNormalise,
  sharpen,
  type ArmGrid,
  type ArmShape,
} from "./armsField";
import { ILL_MAP } from "./feature";
import { SKEL_CONTRAST_MAX, SKEL_MEAN_SAMPLES } from "./armsSkeleton";
import { buildSparkle, brightness, shareAt, sparkleFlux, type SparkleShape } from "./armsSparkle";
import { MARCH_PATCHES, illDefaults, illGlsl, illustrativeFragment, occurrences } from "./index";

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

describe("the arms' hand-over: two channels of the shared map (S105 fix)", () => {
  it("decodes, as the GLSL does, to armMap's four values at the arm grid's texels", () => {
    const g: ArmGrid = { nR: 120, nPhi: 180, rHi: 30 };
    const shape = { ...SHAPE, equalise: 0.6, cap: 2.2 };
    const n = ringNormalise(spiral(g, 3, 0.3), g.nR, g.nPhi);
    const strength = 1.2;
    const map = armMap(n, g, shape, strength);
    // a grid of odd multiples, so every arm texel's centre is a shared texel's centre (the 8-bit encoding alone measured)
    const W = g.nR * 5;
    const H = g.nPhi * 3;
    const planes = armPlanes(...Object.values(armShare(n, g, shape)) as [Float64Array, Float64Array], g, W, H);
    const flag = (i: number) => Math.floor(planes.flags[i >> 4] / 2 ** (i & 15)) % 2;
    const ring = (s: number, m: number, lo: number, cap: number) => {
      const mean = lo + (1 - lo) * m;
      return mean > 0 ? Math.min(cap, (lo + (1 - lo) * s) / mean) : 1;
    };
    let worst = [0, 0, 0, 0];
    for (const i of [30, 50, 80, 110]) {
      for (let j = 0; j < g.nPhi; j += 7) {
        // the arm texel's centre: shared column 5 i + 2, shared row 3 j + 1
        const at = (p: Uint8Array) => p[(j * 3 + 1) * W + i * 5 + 2] / 255;
        const sb = at(planes.share);
        const s = sb * sb;
        const m = at(planes.mean) * planes.meanMax;
        const r = (i + 0.5) * (g.rHi / g.nR);
        const f = barFade(r, shape.start, shape.width) * strength;
        const fa = Math.min(1, f);
        const got = [
          Math.max(0, 1 + (ring(s, m, shape.floor, shape.cap) - 1) * f),
          fa * smoothstep(0.25, 0.9, s) * flag(i),
          Math.max(0, 1 + (ring(s, m, shape.young, YOUNG_CAP) - 1) * f),
          fa,
        ];
        const o = (j * g.nR + i) * 4;
        worst = worst.map((w, q) => Math.max(w, Math.abs(got[q] - map[o + q]) / Math.max(1, Math.abs(map[o + q]))));
      }
    }
    // 8-bit planes: the light and the young light within 2 %, the tone share within 0.03, the fade exact
    expect(worst[0]).toBeLessThan(0.02);
    expect(worst[1]).toBeLessThan(0.03);
    expect(worst[2]).toBeLessThan(0.02);
    expect(worst[3]).toBeLessThan(1e-12);
  });

  it("names B and A of the shared map and declares no sampler", () => {
    expect(arms.map!.channels).toEqual([2, 3]);
    expect(arms.glsl).not.toMatch(/sampler/);
    expect(arms.map!.build({}, { template: null, frame: null })).toEqual([null, null]);
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
    expect(illGlsl()).toContain("  vec3 illLight(vec2 rp) { return illEdgeDisc(rp) * illGrazeMul3(illArmsLight(rp)) * illGrazeMul3(illBaseLight(rp)); }");
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

describe("the bar's light (S105, tuner M)", () => {
  // A barred frame on the arm grid: an m = 2 pattern laid at 0.6 rad inside the bar.
  const angle = 0.6;
  const pattern = new Float32Array(G.nR * G.nPhi);
  for (let i = 0; i < G.nR; i++)
    for (let j = 0; j < G.nPhi; j++) pattern[i * G.nPhi + j] = 1 + 0.5 * Math.cos(2 * (((j + 0.5) * 2 * Math.PI) / G.nPhi - angle));
  const frame = {
    header: { scalars: { bar_half_length: 4, bar_axis_ratio: 0.35 }, grid: { axes: { R: { n: G.nR, hi: G.rHi }, phi: { n: G.nPhi } } } },
    arrays: { pattern_density_contrast: pattern },
  };
  const own = (template: string | null) =>
    Object.fromEntries(Object.entries(illDefaults(template)).filter(([k]) => k.startsWith("arms.")).map(([k, v]) => [k.slice(5), v]));

  it("reads the bar's ellipse: the published half-length and axis ratio, the angle off the pattern", () => {
    const bar = barOf(frame)!;
    expect(bar.halfLength).toBe(4);
    expect(bar.axisRatio).toBeCloseTo(0.35, 6);
    expect(bar.angle).toBeCloseTo(angle, 6);
    expect(barOf({ header: { scalars: {} }, arrays: { pattern_density_contrast: pattern } })).toBeNull();
  });

  it("is off - the light untouched - at the template-less defaults and at NGC 4414's", () => {
    for (const t of [null, "ngc_4414"]) expect(barUniforms(own(t), frame).illArmsBarOn).toBe(0);
    expect(barUniforms(own("milky_way"), frame).illArmsBarOn).toBe(1);
    expect(barUniforms({ barglow: 2 }, { header: { scalars: {} }, arrays: {} }).illArmsBarOn).toBe(0);
  });

  it("scales the ellipse, carries the light, a cream of unit mean and a dimmed blue ground", () => {
    const u = barUniforms({ barglow: 2, barwarm: 1, bardim: 0.5, barcool: 1, barsize: 0.5 }, frame);
    expect(u.illArmsBar[0]).toBeCloseTo(2, 12);
    expect(u.illArmsBar[3]).toBe(2);
    expect((u.illArmsBarTint[0] + u.illArmsBarTint[1] + u.illArmsBarTint[2]) / 3).toBeCloseTo(1, 12);
    expect(u.illArmsBarTint[0]).toBeGreaterThan(u.illArmsBarTint[2]);
    expect((u.illArmsBarGround[0] + u.illArmsBarGround[1] + u.illArmsBarGround[2]) / 3).toBeCloseTo(0.5, 12);
    expect(u.illArmsBarGround[2]).toBeGreaterThan(u.illArmsBarGround[0]);
  });
});

describe("the model's arm light divided out off the skeleton (S107 NGC2, arms.flat)", () => {
  const g: ArmGrid = { nR: 120, nPhi: 180, rHi: 30 };
  const pattern = spiral(g, 3, 0.3, 5);
  const frame = {
    header: { scalars: {}, grid: { axes: { R: { n: g.nR, hi: g.rHi }, phi: { n: g.nPhi } } } },
    arrays: { pattern_density_contrast: pattern },
  } as unknown as Parameters<NonNullable<typeof arms.uniforms>>[1]["frame"];
  const ctx = { template: "ngc_4414", frame };
  const base = { ...illDefaults("ngc_4414") };
  const local = (flat: number) => {
    const p: Record<string, number> = {};
    for (const [k, v] of Object.entries(base)) if (k.startsWith("arms.")) p[k.slice(5)] = v;
    p.flat = flat;
    return p;
  };

  it("is 0 by default and on both templates", () => {
    expect(illDefaults("milky_way")["arms.flat"]).toBe(0);
    expect(arms.controls.find((c) => c.key === "flat")!.default).toBe(0);
  });

  it("at 0 hands the march exactly the planes and uniforms of before (A the share's ring mean, nothing divided)", () => {
    const u = arms.uniforms!(local(0), ctx) as Record<string, unknown>;
    expect(u.illArmsAc).toBe(0);
    expect(u.illArmsFlatAll).toBe(0);
    expect(u.illArmsSkel).toBe(0);
    const [share, mean] = arms.map!.build(local(0), ctx) as Uint8Array[];
    // A is the ring mean: the same down every row
    expect(mean[5 * ILL_MAP.width + 700]).toBe(mean[1234 * ILL_MAP.width + 700]);
    expect(share.length).toBe(ILL_MAP.width * ILL_MAP.height);
  }, 30000);

  it("above 0 carries the model's contrast in A and the ring means as samples, the share unchanged", () => {
    const [share0] = arms.map!.build(local(0), ctx) as Uint8Array[];
    const [share1, mean1] = arms.map!.build(local(1), ctx) as Uint8Array[];
    expect(share1).toEqual(share0);
    const u = arms.uniforms!(local(1), ctx) as Record<string, number | number[]>;
    expect(u.illArmsAc).toBe(1);
    expect(u.illArmsFlatAll).toBe(1);
    expect(u.illArmsSkel).toBe(0);
    expect(u.illArmsFlat).toBe(1);
    expect((u.illArmsSkelMean as number[]).length).toBe(SKEL_MEAN_SAMPLES);
    // A decodes to the contrast over its ring mean (1 + 0.3 cos(...)) within the byte and its dither
    const n = ringNormalise(pattern, g.nR, g.nPhi);
    for (const [i, j] of [[60, 10], [90, 100], [30, 170]]) {
      const c = Math.round(((i + 0.5) / g.nR) * ILL_MAP.width - 0.5);
      const r = Math.round(((j + 0.5) / g.nPhi) * ILL_MAP.height - 0.5);
      expect(Math.abs((mean1[r * ILL_MAP.width + c] / 255) * SKEL_CONTRAST_MAX - n[i * g.nPhi + j])).toBeLessThan(0.03);
    }
  }, 30000);
});
