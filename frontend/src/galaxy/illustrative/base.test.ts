import { describe, expect, it } from "vitest";

import { fieldFragment } from "../FieldVolume";
import { FLUX_POINTS_SHADER } from "../FluxPoints";
import pinned from "../fieldFragment.s78.glsl?raw";
import { base, baseCore, baseGas, baseLift, baseMended, baseTexelAv, regionExtinction } from "./base";
import { MARCH_PATCHES, POINTS_PATCHES, createRuntime, illDefaults, illGlsl, illustrativeFragment, illustrativePointsVertex, occurrences } from "./index";

describe("the base (S106): the gas map's streaks smoothed, the disc lifted", () => {
  it("patches the screen's gas map in the march and the points' gasAt, each anchor found once", () => {
    const march = "    float screenGas = gasFluct > 0.5 ? layerGasMap(screenXY) : 1.0;";
    const points = "      gasAt = layerGasMap(vec2(screen.x, -screen.z));";
    expect(MARCH_PATCHES.some((p) => p.anchor === march)).toBe(true);
    expect(POINTS_PATCHES.some((p) => p.anchor === points)).toBe(true);
    expect(occurrences(fieldFragment(), march)).toBe(1);
    expect(occurrences(FLUX_POINTS_SHADER.vertex, points)).toBe(1);
    const frag = illustrativeFragment(fieldFragment());
    expect(frag).toContain("    float screenGas = gasFluct > 0.5 ? illGas(screenXY, layerGasMap(screenXY)) : 1.0;");
    expect(frag).toContain("float illBaseGasMap(vec2 xy)");
    // the hook's function lies after the noise include it calls, before main
    expect(frag.indexOf("float illBaseGasMap(vec2 xy)")).toBeGreaterThan(frag.indexOf("float layerGasMap(vec2 xy)"));
    expect(frag.indexOf("float illGas(vec2 xy, float g)")).toBeLessThan(frag.indexOf("  void main() {"));
    const vert = illustrativePointsVertex(FLUX_POINTS_SHADER.vertex);
    expect(vert).toContain("gasAt = illGas(vec2(screen.x, -screen.z), layerGasMap(vec2(screen.x, -screen.z)));");
    expect(vert.indexOf("float illBaseGasMap(vec2 xy)")).toBeGreaterThan(vert.indexOf("float layerGasMap(vec2 xy)"));
    expect(fieldFragment()).toBe(pinned);
  });

  it("keeps the noise side out of runtime.glsl (the knots' layer has no noise include)", () => {
    expect(illGlsl()).not.toContain("illBaseGasMap");
    expect(illGlsl()).not.toContain("illGas(");
    expect(illGlsl(true)).toContain("  float illGas(vec2 xy, float g) { g = illBaseGas(xy, g); return g; }");
    expect(createRuntime().glsl).toBe(illGlsl());
    expect(illGlsl()).toContain("illBaseLight(rp)");
  });

  it("smooths the streaks on both templates by default and lifts the Milky Way's disc only", () => {
    const mw = illDefaults("milky_way");
    const ngc = illDefaults("ngc_4414");
    expect(mw["base.grain"]).toBe(0);
    expect(ngc["base.unshear"]).toBe(1);
    expect(mw["base.lift"]).toBeGreaterThan(0);
    expect(ngc["base.lift"]).toBe(0);
    const u = base.uniforms!({ grain: 0.5, unshear: 1, size: 2, depth: 0.8, lift: 1, radius: 10 }, { template: null, frame: null });
    expect(u).toEqual({
      illBaseGrain: 0.5, illBaseUnshear: 1, illBaseSize: 2, illBaseDepth: 0.8, illBaseLift: 1, illBaseRadius: 10,
      illBaseMend: 1, illBaseCore: 0, illBaseCoreRadius: 1, illBaseGrazeDust: 4,
      illGrazeAt: [(72 * Math.PI) / 180, (88 * Math.PI) / 180],
    });
  });

  it("has GLSL twins: the map toward its mean, and the lift's ramp", () => {
    expect(baseGas(3, 0, 1)).toBe(1);
    expect(baseGas(3, 1, 1)).toBe(3);
    expect(baseGas(3, 0.5, 0.5)).toBe(1);
    expect(baseLift(0, 1, 10)).toBe(1);
    expect(baseLift(10, 1, 10)).toBe(2);
    expect(baseLift(20, 1, 10)).toBe(2);
    expect(baseLift(5, 1, 10)).toBeCloseTo(Math.SQRT2, 10);
    expect(baseLift(5, 0, 10)).toBe(1);
  });
});

describe("the base's mend and core (S106, builder E): NGC 4414's underflowed depths rebuilt, the core thinned", () => {
  // NGC 4414's published ratio (A_lambda / A_V per filter over 2.5 / ln 10) and its first rings as the viewer reads them.
  const ext = [0.7935279772252049, 0.9981880848868092, 1.3021217020257043].map((r) => r / (2.5 / Math.LN10)) as unknown as [number, number, number];
  const av = (a: number) => ext.map((e) => a * e) as unknown as [number, number, number];
  const healthy: [number, number, number][] = [av(49.7), av(51.6), av(48.8), av(46), av(43), av(0.002), [0, 0, 0], [0, 0, 0]];
  const ngc: [number, number, number][] = [
    [96.96, 0, 0], [0, 0, 0], [100.28, 0, 0], [90.98, 0, 0], [81.5, 102.59, 0], [72.6, 91.32, 0], [64.51, 81.15, 0], av(57.3 / ext[0]), av(50.92 / ext[0]),
  ];

  it("is a no-op, the same object, wherever no channel is lost (the Milky Way, healthy rings, the empty edge)", () => {
    for (let r = 0; r < 0.6; r += 0.0137) {
      const d = av(40);
      expect(baseMended(d, r, healthy, ext, 0, 0.6)).toBe(d);
    }
  });

  it("rebuilds a lost channel in the ratio from the deepest surviving one", () => {
    // ring 3's centre (0.2625 kpc on a 0.075 kpc grid): R survives, G and B lost
    const r = 0.075 * 3.5;
    const got = baseMended([90.98, 0, 0], r, ngc, ext, 0, 0.675);
    expect(got[0]).toBeCloseTo(90.98, 6);
    expect(got[1] / got[0]).toBeCloseTo(ext[1] / ext[0], 6);
    expect(got[2] / got[0]).toBeCloseTo(ext[2] / ext[0], 6);
    // ring 5: R and G survive, B rebuilt
    const g5 = baseMended([72.6, 91.32, 0], 0.075 * 5.5, ngc, ext, 0, 0.675);
    expect(g5[2] / g5[0]).toBeCloseTo(ext[2] / ext[0], 6);
    // half mended
    const half = baseMended([90.98, 0, 0], r, ngc, ext, 0, 0.675, 0.5);
    expect(half[2]).toBeCloseTo(0.5 * got[2], 6);
  });

  it("floors the ring where all three channels are lost from its deep neighbours", () => {
    const got = baseMended([0, 0, 0], 0.075 * 1.5, ngc, ext, 0, 0.675);
    const mean = (0.5 * (96.96 + 100.28)) / ext[0];
    expect(baseTexelAv(ngc, 1, ext).lost).toBe(true);
    expect(baseTexelAv(ngc, 1, ext).av).toBeCloseTo(mean, 9);
    expect(got[0]).toBeCloseTo(mean * ext[0], 6);
    expect(got[2]).toBeCloseTo(mean * ext[2], 6);
    // an empty texel beside shallow ones is no dust, not a loss
    expect(baseTexelAv(healthy, 6, ext)).toEqual({ av: 0, lost: false });
  });

  it("has a smooth core ramp, 10^-core at the centre and 1 from its radius out", () => {
    expect(baseCore(0, 2, 1)).toBeCloseTo(0.01, 12);
    expect(baseCore(1, 2, 1)).toBe(1);
    expect(baseCore(3, 2, 1)).toBe(1);
    expect(baseCore(0.5, 0, 1)).toBe(1);
    let last = 0;
    for (let r = 0; r <= 1.0001; r += 0.01) {
      const v = baseCore(r, 2, 1);
      expect(v).toBeGreaterThanOrEqual(last);
      expect(v - last).toBeLessThan(0.05);
      last = v;
    }
    expect(1 - baseCore(0.99, 2, 1)).toBeLessThan(0.01);
  });

  it("composes the depth hook into the march's tau and the points' face, each anchor once, before the layer's dust", () => {
    const tau = "          tau = readRing(rp.x, 0.0) * place * readRing(rp.x, 3.0).r * dustDepth;";
    expect(occurrences(fieldFragment(), tau)).toBe(1);
    const frag = illustrativeFragment(fieldFragment());
    expect(occurrences(frag, "          tau = illDepth(readRing(rp.x, 0.0), rp) * place * readRing(rp.x, 3.0).r * dustDepth;")).toBe(1);
    expect(frag.indexOf("tau = illDepth(")).toBeLessThan(frag.indexOf("tau += illDustAv(rp) * cloudExt * dustDepth;"));
    expect(occurrences(frag, "  vec3 illDepth(vec3 d, vec2 rp) { d = illBaseDepthOf(d, rp); return d; }")).toBe(1);
    const vert = illustrativePointsVertex(FLUX_POINTS_SHADER.vertex);
    expect(occurrences(vert, "      tau += illDepth(face, vec2(r, phi)) * place * gasAt * share * column(")).toBe(1);
    expect(occurrences(vert, "  vec3 illDepth(vec3 d, vec2 rp)")).toBe(1);
    expect(illGlsl()).not.toContain("illDepth");
    expect(illDefaults("milky_way")["base.mend"]).toBe(1);
    expect(illDefaults("ngc_4414")["base.mend"]).toBe(1);
    expect(illDefaults("milky_way")["base.core"]).toBe(0);
    expect(illDefaults("ngc_4414")["base.core"]).toBe(0.6);
    // S109 (B3): NGC 4414's clearing reaches 2 kpc (the nucleus's glow not greyed by the dust round it); the Milky Way's 1.
    expect(illDefaults("ngc_4414")["base.coreRadius"]).toBe(2);
    expect(illDefaults("milky_way")["base.coreRadius"]).toBe(1);
  });
});

describe("the near regime's clouds under the look (S108 J3, base.nearClouds)", () => {
  it("leaves the physical look's strength as it is and takes the clouds out by default on both templates", () => {
    expect(regionExtinction(1.6, null)).toBe(1.6);
    for (const t of ["milky_way", "ngc_4414"]) expect(illDefaults(t)["base.nearClouds"]).toBe(0);
    expect(regionExtinction(1.6, { nearClouds: 1 })).toBe(1.6);
    expect(regionExtinction(2, { nearClouds: 0.25 })).toBe(0.5);
  });
});
