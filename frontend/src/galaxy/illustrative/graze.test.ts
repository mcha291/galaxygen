// S108 (the grazing handover; index.ts GRAZE_DEFAULT): the layer's face-on drawing handed over to the model's own
// edge-on look by a weight per ray and per point, exactly 1 up to the handover's start.

import { describe, expect, it } from "vitest";

import { fieldFragment } from "../FieldVolume";
import { FLUX_POINTS_SHADER } from "../FluxPoints";
import { GRAZE_FROM, GRAZE_TO, base, grazeAt, grazeWeight } from "./base";
import { GRAZE_DEFAULT, illDefaults, illGlsl, illustrativeFragment, illustrativePointsVertex, occurrences } from "./index";

describe("the grazing handover (S108)", () => {
  it("weighs a sight line 1 up to the start, 0 from the end, smoothly between", () => {
    expect(grazeWeight(0, GRAZE_FROM, GRAZE_TO)).toBe(1);
    expect(grazeWeight(GRAZE_FROM, GRAZE_FROM, GRAZE_TO)).toBe(1);
    expect(grazeWeight(GRAZE_TO, GRAZE_FROM, GRAZE_TO)).toBe(0);
    expect(grazeWeight(90, GRAZE_FROM, GRAZE_TO)).toBe(0);
    let last = 1;
    for (let a = GRAZE_FROM; a <= GRAZE_TO; a += 0.25) {
      const g = grazeWeight(a, GRAZE_FROM, GRAZE_TO);
      expect(g).toBeLessThanOrEqual(last);
      expect(last - g).toBeLessThan(0.05);
      last = g;
    }
    expect(grazeAt(72, 88)).toEqual([(72 * Math.PI) / 180, (88 * Math.PI) / 180]);
  });

  it("starts above every ray the tuned stands reach (the Milky Way face-on, 45 degree lens; NGC 4414 at ~61, 5 degrees)", () => {
    // The corner ray of a square 45 degree frame is 30.4 degrees off the view axis; NGC 4414's stand is under 65 degrees
    // with its lens; its close-up stand at 55 degrees with the same lens.
    const corner = (Math.atan(Math.tan((22.5 * Math.PI) / 180) * Math.SQRT2) * 180) / Math.PI;
    expect(corner).toBeLessThan(31);
    for (const t of ["milky_way", "ngc_4414"]) expect(illDefaults(t)["base.grazeFrom"]).toBeGreaterThan(Math.max(corner, 65));
  });

  it("is the registry's: the weight set once per ray in the march and once per point, the veil and the tints faded", () => {
    const glsl = illGlsl(true);
    expect(glsl).toContain("float illGraze = 1.0;");
    expect(glsl).toContain("uniform vec2 illGrazeAt;");
    expect(glsl).toMatch(/vec3 illVeil\(vec2 rp\) \{ return illGrazeMul3\(illFlocVeil\(rp\)\) \* illGrazeMul3\(illLanesVeil\(rp\)\)|vec3 illVeil\(vec2 rp\) \{ return illGrazeMul3\(illLanesVeil\(rp\)\) \* illGrazeMul3\(illFlocVeil\(rp\)\)/);
    // The edge's light is the bulge dimming's give-back, kept (its share is handed over inside edge.ts).
    expect(glsl).toContain("illLight(vec2 rp) { return illEdgeDisc(rp) *");
    // 3-D structure (the dust's own layer, the young light, the taper) is kept.
    expect(glsl).toContain("float illDustAv(vec2 rp) { return illLanesAv(rp) + illFlocAv(rp); }");
    expect(GRAZE_DEFAULT.veil).toBe("fade");
    expect(GRAZE_DEFAULT.dustAv).toBe("keep");
    const march = illustrativeFragment(fieldFragment());
    expect(occurrences(march, "    illGraze = illGrazeOf(dir);")).toBe(1);
    expect(occurrences(march, "    screenClumps = illGrazeMul3(screenClumps);")).toBe(1);
    const points = illustrativePointsVertex(FLUX_POINTS_SHADER.vertex);
    expect(occurrences(points, "    illPointsPlace();")).toBe(1);
    expect(occurrences(points, "  #define position illPointsPos")).toBe(1);
    // The define comes after the wings' check (which reads the point where it is) and before dustTo and main.
    expect(points.indexOf("bool wingDrawn()")).toBeLessThan(points.indexOf("#define position"));
    expect(points.indexOf("#define position")).toBeLessThan(points.indexOf("vec3 dustTo(vec3 p)"));
  });

  it("hands the base's removals back: its uniforms carry the angles and the edge-on dust", () => {
    const u = base.uniforms!({ grazeFrom: 70, grazeTo: 85, grazeDust: 3 }, { template: null, frame: null });
    expect(u.illGrazeAt).toEqual(grazeAt(70, 85));
    expect(u.illBaseGrazeDust).toBe(3);
  });
});
