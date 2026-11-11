import { describe, expect, it } from "vitest";

import { type RegionStars, dropRows, starLoads } from "./regionStars";
import { LOAD_TUNING_KEYS, TUNING_CONTROLS, TUNING_DEFAULTS, drawnTuning, loadTuning } from "./tuning";

// S82 (#172, the owner's ruling of 2026-11-02): the field mode's region regime draws the star-first mode's points by
// default; V3's sample is kept behind the switch.

const POSITIONS: RegionStars[] = ["catalogue", "sampled"];

describe("the region's stars (S82, #172)", () => {
  it("decides the loaders: the catalogue's points or V3's sample below 4 kpc, the default the catalogue", () => {
    expect(TUNING_DEFAULTS.regionStars).toBe("catalogue");
    expect(starLoads("field", "catalogue", true, true)).toEqual({ points: true, sampled: false });
    expect(starLoads("field", "sampled", true, true)).toEqual({ points: false, sampled: true });
    // the points switched off draw no stars there at catalogue; the sampled reading never reads that switch
    expect(starLoads("field", "catalogue", false, true)).toEqual({ points: false, sampled: false });
    expect(starLoads("field", "sampled", false, true)).toEqual({ points: false, sampled: true });
  });

  it("changes nothing above 4 kpc nor in the star-first mode: the galaxy-scale request set is the switch's at both positions", () => {
    for (const compPoints of [true, false]) {
      const above = POSITIONS.map((p) => starLoads("field", p, compPoints, false));
      expect(above).toEqual([{ points: false, sampled: false }, { points: false, sampled: false }]);
      for (const inRegion of [true, false]) {
        const stars = POSITIONS.map((p) => starLoads("stars", p, compPoints, inRegion));
        expect(stars).toEqual([{ points: compPoints, sampled: false }, { points: compPoints, sampled: false }]);
      }
    }
  });

  it("is a per-template switch that keys loaders: a landing's hold takes the live template's", () => {
    expect(LOAD_TUNING_KEYS).toContain("regionStars");
    const control = TUNING_CONTROLS.find((c) => c.key === "regionStars");
    expect(control?.kind).toBe("select");
    expect(control && control.kind === "select" ? control.options.map((o) => o.value) : []).toEqual(POSITIONS);
    expect(control?.about).toMatch(/display choice/);
    const live = { ...TUNING_DEFAULTS, regionStars: "sampled" as const };
    expect(drawnTuning(live, { ...TUNING_DEFAULTS }).regionStars).toBe("sampled");
    // stored per template, an unknown value refused
    const store = (text: string) => ({ getItem: (key: string) => (key.endsWith(".ngc_4414") ? text : null) });
    expect(loadTuning(store(JSON.stringify({ regionStars: "sampled" })), "ngc_4414").regionStars).toBe("sampled");
    expect(loadTuning(store(JSON.stringify({ regionStars: "both" })), "ngc_4414").regionStars).toBe("catalogue");
  });
});

// S93 (T3 / #115): the young population drawn once - the sample's members and the census's dissolved clusters draw nothing.
describe("the young population drawn once (S93, T3 / #115)", () => {
  it("zeroes the rows whose column reads the dropped value, and keeps a response without the column whole", () => {
    const colors = Float32Array.from([1, 2, 3, 4, 5, 6, 7, 8, 9]);
    expect(Array.from(dropRows(colors, [0, 1, 0], 1)!)).toEqual([1, 2, 3, 0, 0, 0, 7, 8, 9]);
    const census = Float32Array.from([1, 1, 1, 2, 2, 2]);
    expect(Array.from(dropRows(census, [2, 0], 2)!)).toEqual([0, 0, 0, 2, 2, 2]);
    const whole = Float32Array.from([1, 2, 3]);
    expect(Array.from(dropRows(whole, undefined, 1)!)).toEqual([1, 2, 3]);
    expect(Array.from(dropRows(whole, [1, 1], 1)!)).toEqual([1, 2, 3]); // a column of another length: drawn whole
    expect(dropRows(null, [1], 1)).toBeNull();
  });
});
