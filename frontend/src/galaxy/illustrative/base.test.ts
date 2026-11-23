import { describe, expect, it } from "vitest";

import { fieldFragment } from "../FieldVolume";
import { FLUX_POINTS_SHADER } from "../FluxPoints";
import pinned from "../fieldFragment.s78.glsl?raw";
import { base, baseGas, baseLift } from "./base";
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
    expect(u).toEqual({ illBaseGrain: 0.5, illBaseUnshear: 1, illBaseSize: 2, illBaseDepth: 0.8, illBaseLift: 1, illBaseRadius: 10 });
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
