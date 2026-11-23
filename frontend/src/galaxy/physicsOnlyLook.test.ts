import { describe, expect, it } from "vitest";

import { LOOKS } from "./illustrative";
import { LOOK_SUSPENDED_WHAT, drawnLook, drawnTuningFor, loadTuning, lookDefaultsFor, lookSuspended } from "./tuning";

// S108 (the lead's ruling): "physics only" is a study of the physical model; while it is on the view draws the
// physical look whatever look is stored, and the stored look returns when it is released.
describe("the look drawn under physics only (S108)", () => {
  it("draws the physical look while physics only is on, whatever look is stored", () => {
    for (const stored of LOOKS) expect(drawnLook(stored, true)).toBe("physical");
  });

  it("draws the stored look while physics only is off", () => {
    for (const stored of LOOKS) expect(drawnLook(stored, false)).toBe(stored);
  });

  it("says the illustrative look is suspended only where physics only sets it aside", () => {
    expect(lookSuspended("illustrative", true)).toBe(true);
    expect(lookSuspended("illustrative", false)).toBe(false);
    expect(lookSuspended("physical", true)).toBe(false);
    expect(lookSuspended("physical", false)).toBe(false);
    expect(LOOK_SUSPENDED_WHAT).toMatch(/^illustrative suspended: physics only/);
  });

  it("draws with the physical look's own defaults, no illustrative parameter among them", () => {
    for (const template of ["milky_way", "ngc_4414"]) {
      const drawn = lookDefaultsFor(template, drawnLook("illustrative", true));
      expect(drawn).toEqual(lookDefaultsFor(template, "physical"));
      expect(drawn.ill).toEqual(lookDefaultsFor(template, "physical").ill);
    }
  });
});

// S108 J5: App's head start on the field's loads asks with the tuning of the look drawn, not the stored look's.
describe("the tuning the field's loads are asked ahead with (S108 J5)", () => {
  const stored = (key: string): string | null => (key.includes("illustrative") ? JSON.stringify({ ill: { "arms.strength": 0.5 } }) : null);
  const storage = { getItem: stored };
  it("is the physical look's under physics only, whatever look is stored", () => {
    for (const template of ["milky_way", "ngc_4414"]) {
      expect(drawnTuningFor(storage, template, "illustrative", true)).toEqual(loadTuning(storage, template, "physical"));
      expect(drawnTuningFor(storage, template, "illustrative", false)).toEqual(loadTuning(storage, template, "illustrative"));
    }
  });
});
