import { describe, expect, it } from "vitest";

import { GALAXY_SEEDED, illControls, illDefaults, illReroll, illSeeded, rerolledSeed, withIllReroll } from "./index";
import type { IllFrame } from "./feature";

// S108: the layer's own seeds follow the generated galaxy; the template's own seeds are today's drawing exactly.
const OWN = { milky_way: { world_seed: 0, pattern_seed: 0, systems_seed: 0, planets_seed: 0, texture_seed: 0 }, ngc_4414: { world_seed: 4414, pattern_seed: 4414, systems_seed: 4414, planets_seed: 4414, texture_seed: 4414 } };
const frameOf = (inputs: Record<string, unknown>): IllFrame => ({ header: { scalars: {}, inputs }, arrays: {} });

describe("the layer's seeds follow the galaxy (S108)", () => {
  it("reads no reroll for the template's own seeds, a world_seed alone, or without a template", () => {
    expect(illReroll({ pattern_seed: 0, texture_seed: 0 }, OWN.milky_way)).toBe(0);
    expect(illReroll({ pattern_seed: 4414.0, texture_seed: 4414.0, world_seed: 99 }, OWN.ngc_4414)).toBe(0);
    expect(illReroll({ pattern_seed: 5, texture_seed: 0 }, null)).toBe(0);
    expect(illReroll(undefined, OWN.milky_way)).toBe(0);
  });

  it("reads a non-zero reroll, its own per pair, when the pattern or the texture seed is rerolled", () => {
    const a = illReroll({ pattern_seed: 123, texture_seed: 0 }, OWN.milky_way);
    const b = illReroll({ pattern_seed: 0, texture_seed: 123 }, OWN.milky_way);
    const c = illReroll({ pattern_seed: 123, texture_seed: 456 }, OWN.milky_way);
    for (const r of [a, b, c]) expect(r).not.toBe(0);
    expect(new Set([a, b, c]).size).toBe(3);
  });

  it("draws the template's galaxy with the sliders' own values: the same object", () => {
    for (const t of ["milky_way", "ngc_4414"] as const) {
      const ill = illDefaults(t);
      const frame = withIllReroll(frameOf({ pattern_seed: OWN[t].pattern_seed, texture_seed: OWN[t].texture_seed }), OWN[t]);
      expect(frame.header.illReroll).toBe(0);
      expect(illSeeded(ill, { template: t, frame })).toBe(ill);
      expect(illSeeded(ill, { template: t, frame: null })).toBe(ill);
    }
  });

  it("rerolls exactly the galaxy-seeded sliders, each to another integer in its range, the same for the same galaxy", () => {
    const ill = illDefaults("milky_way");
    const frame = withIllReroll(frameOf({ pattern_seed: 31337, texture_seed: 7 }), OWN.milky_way);
    const got = illSeeded(ill, { template: "milky_way", frame });
    expect(got).not.toBe(ill);
    for (const { key, control } of illControls()) {
      if (!GALAXY_SEEDED.includes(key)) {
        expect(got[key]).toBe(ill[key]);
        continue;
      }
      expect(got[key]).not.toBe(ill[key]);
      expect(Number.isInteger(got[key])).toBe(true);
      expect(got[key]).toBeGreaterThanOrEqual(control.min);
      expect(got[key]).toBeLessThanOrEqual(control.max);
    }
    expect(illSeeded(ill, { template: "milky_way", frame })).toEqual(got);
    // The sky's field stars are the viewer's: never rerolled.
    expect(GALAXY_SEEDED).not.toContain("sky.seed");
    expect(GALAXY_SEEDED).toEqual(["floc.seed", "arms.skelseed", "knots.seed", "lanes.seed"]);
  });

  it("keeps the slider choosing: two slider values stay two drawings under one reroll", () => {
    const control = illControls().find((c) => c.key === "knots.seed")!.control;
    const seen = new Set<number>();
    for (let v = control.min; v <= control.max; v++) seen.add(rerolledSeed(control, "knots.seed", v, 0x9e3779b9));
    expect(seen.size).toBe(control.max - control.min + 1);
  });
});
