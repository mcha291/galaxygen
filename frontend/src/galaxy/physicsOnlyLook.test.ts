import { describe, expect, it } from "vitest";

import { LOOKS } from "./illustrative";
import { LOOK_SUSPENDED_WHAT, drawnLook, lookDefaultsFor, lookSuspended, lookSwitchedByTuning } from "./tuning";

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

  it("keeps the stored look when a slider is moved on the drawn look under physics only (S108 review)", () => {
    // A slider moved while physics only suspends the illustrative look: kept under the drawn (physical) look, no switch.
    expect(lookSwitchedByTuning("physical", drawnLook("illustrative", true), "illustrative")).toBeNull();
    // A pasted illustrative box while suspended: kept under its own key; the stored look is already it.
    expect(lookSwitchedByTuning("illustrative", drawnLook("illustrative", true), "illustrative")).toBeNull();
    // Without physics only, as since S105: a box of the other look switches to it, a slider on the drawn look does not.
    expect(lookSwitchedByTuning("illustrative", drawnLook("physical", false), "physical")).toBe("illustrative");
    expect(lookSwitchedByTuning("physical", drawnLook("illustrative", false), "illustrative")).toBe("physical");
    for (const l of LOOKS) expect(lookSwitchedByTuning(l, drawnLook(l, false), l)).toBeNull();
    // Physics only with the physical look stored: an illustrative box switches the stored look (drawn physical still).
    expect(lookSwitchedByTuning("illustrative", drawnLook("physical", true), "physical")).toBe("illustrative");
  });

  it("draws with the physical look's own defaults, no illustrative parameter among them", () => {
    for (const template of ["milky_way", "ngc_4414"]) {
      const drawn = lookDefaultsFor(template, drawnLook("illustrative", true));
      expect(drawn).toEqual(lookDefaultsFor(template, "physical"));
      expect(drawn.ill).toEqual(lookDefaultsFor(template, "physical").ill);
    }
  });
});
