import { describe, expect, it } from "vitest";

import { framing, standTilt, tiltedInclination } from "./framing";
import { illDefaults } from "./index";

describe("the framing's tilt (S106)", () => {
  it("adds the tilt to the stand's inclination, held to [0, 89], 0 by default and 6 on NGC 4414", () => {
    expect(framing.controls.some((c) => c.key === "tilt")).toBe(true);
    expect(illDefaults("milky_way")["framing.tilt"]).toBe(0);
    expect(illDefaults("ngc_4414")["framing.tilt"]).toBe(6);
    expect(standTilt({})).toBe(0);
    expect(standTilt({ tilt: 6 })).toBe(6);
    expect(tiltedInclination(50, 6)).toBe(56);
    expect(tiltedInclination(50, 0)).toBe(50);
    expect(tiltedInclination(85, 10)).toBe(89);
    expect(tiltedInclination(5, -10)).toBe(0);
  });
});
