import { describe, expect, it } from "vitest";

import { FLUX_POINTS_SHADER } from "../FluxPoints";
import { edgeRamp } from "./edge";
import { createRuntime, features, illDefaults, illGlsl, illustrativePointsVertex } from "./index";
import { points } from "./points";

// S108: the points FluxPoints draws (the star-first mode's stars, the region's, the knots) fade with the field's edge.
describe("the points' edge (S108)", () => {
  it("is registered after the edge, whose taper it reads, with its share at 1 on both templates", () => {
    const ids = features().map((f) => f.id);
    expect(ids.indexOf("points")).toBeGreaterThan(ids.indexOf("edge"));
    for (const t of ["milky_way", "ngc_4414"]) expect(illDefaults(t)["points.edge"]).toBe(1);
    expect(points.hooks?.points).toBe("illPointsAt");
  });

  it("multiplies every point's light by the composed points hook in the illustrative vertex shader only", () => {
    const vert = illustrativePointsVertex(FLUX_POINTS_SHADER.vertex);
    expect(vert).toContain("float illPoints(vec2 rp) { return illPointsAt(rp); }");
    expect(vert).toMatch(/light \*= illPoints\(vec2\(length\(position\.xz\), [^\n]+\)\);\n {4}light = illPointsCapped\(light\);\n {4}vLight = light;/);
    // The physical look's shader is FluxPoints' own: nothing of the layer.
    expect(FLUX_POINTS_SHADER.vertex).not.toContain("illPoints");
    // The march carries the function (the layer's GLSL is one text) and never calls it.
    expect(illGlsl()).toContain("float illPoints(vec2 rp)");
  });

  it("hands the share to its uniform", () => {
    expect(createRuntime(illDefaults("ngc_4414"), { template: "ngc_4414", frame: null }).uniforms.illPointsEdge.value).toBe(1);
    expect(points.uniforms?.({ edge: 0.25 }, { template: null, frame: null })).toEqual({ illPointsEdge: 0.25, illPointsCap: 0 });
  });

  it("takes the edge's taper: whole inside radius - width, nothing from the radius on (NGC 4414: 7 and 11 kpc)", () => {
    // The GLSL's twin (edge.ts edgeRamp) at NGC 4414's defaults.
    const d = illDefaults("ngc_4414");
    const at = (r: number) => edgeRamp(r, Math.min(d["edge.radius"], 30), d["edge.width"]);
    expect(at(6.9)).toBe(1);
    expect(at(9)).toBeCloseTo(0.5, 6);
    expect(at(11)).toBe(0);
    expect(at(20)).toBe(0);
  });
});

describe("the sparkle's brightness cap (S108 J4, arms.sparklecap)", () => {
  it("is the Milky Way's alone, 0 (none) on NGC 4414, and never set on the runtime the other points share", () => {
    expect(illDefaults("milky_way")["arms.sparklecap"]).toBe(30);
    expect(illDefaults("ngc_4414")["arms.sparklecap"]).toBe(0);
    expect(createRuntime(illDefaults("milky_way"), { template: "milky_way", frame: null }).uniforms.illPointsCap.value).toBe(0);
  });
});
