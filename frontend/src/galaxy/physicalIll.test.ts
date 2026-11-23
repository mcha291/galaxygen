import { describe, expect, it } from "vitest";

import { copyBoxText, defaultsFor, illustrativeDefaultsFor, loadTuning, lookDefaultsFor, parseCombination, saveTuning, storageKeyFor, type Look } from "./tuning";

// S105 fix R4: the physical look holds no illustrative parameters - not from a paste, not in its storage, not in its box.
function memory() {
  const store = new Map<string, string>();
  return {
    store,
    getItem: (k: string) => store.get(k) ?? null,
    setItem: (k: string, v: string) => void store.set(k, v),
    removeItem: (k: string) => void store.delete(k),
  };
}

const of = (look: Look) => lookDefaultsFor("ngc_4414", look);
const BOX = JSON.stringify({ template: "ngc_4414", filters: "rgb", exposure: 0, fieldGain: 1.5, ill: { "grade.saturation": 2.2 } });

describe("a box with ill but no look, under the physical look (S105 fix R4)", () => {
  it("is applied without its ill, which is listed as ignored", () => {
    const c = parseCombination(BOX, defaultsFor("ngc_4414"), of);
    expect(c.look).toBeNull();
    expect(c.tuning!.fieldGain).toBe(1.5);
    expect(c.tuning!.ill).toEqual(defaultsFor("ngc_4414").ill);
    expect(c.ignored).toEqual(["ill"]);
    expect(c.rejected).toEqual([]);
  });

  it("is read by the look on screen where no look's defaults are given: physical drops ill, illustrative keeps it", () => {
    const p = parseCombination(BOX, defaultsFor("ngc_4414"), undefined, "physical");
    expect(p.tuning!.ill).toEqual(defaultsFor("ngc_4414").ill);
    expect(p.ignored).toEqual(["ill"]);
    const i = parseCombination(BOX, illustrativeDefaultsFor("ngc_4414"), undefined, "illustrative");
    expect(i.tuning!.ill["grade.saturation"]).toBe(2.2);
    expect(i.ignored).toEqual([]);
    // a box naming the illustrative look keeps its ill
    const named = parseCombination(JSON.stringify({ look: "illustrative", ill: { "grade.saturation": 2.2 } }), defaultsFor("ngc_4414"), of);
    expect(named.look).toBe("illustrative");
    expect(named.tuning!.ill["grade.saturation"]).toBe(2.2);
  });

  it("never writes ill under the physical key nor prints it in the physical box; a stored physical ill is not read", () => {
    const m = memory();
    const d = defaultsFor("ngc_4414");
    const t = { ...d, fieldGain: 1.5, ill: { ...d.ill, "grade.saturation": 2.2 } };
    saveTuning(t, m, "ngc_4414", "physical");
    expect(JSON.parse(m.store.get(storageKeyFor("ngc_4414", "physical"))!)).toEqual({ fieldGain: 1.5 });
    expect(copyBoxText(t, d, "ngc_4414", "rgb", 0)).toBe(JSON.stringify({ template: "ngc_4414", filters: "rgb", exposure: 0, fieldGain: 1.5 }));
    expect(copyBoxText(t, d, "ngc_4414", "rgb", 0, "physical")).not.toContain("ill");
    // an entry stored before the fix
    m.store.set(storageKeyFor("ngc_4414", "physical"), JSON.stringify({ fieldGain: 2, ill: { "grade.saturation": 2.5 } }));
    const back = loadTuning(m, "ngc_4414", "physical");
    expect(back.fieldGain).toBe(2);
    expect(back.ill).toEqual(d.ill);
    // the illustrative look's own key still keeps and reads its ill
    const it = illustrativeDefaultsFor("ngc_4414");
    saveTuning({ ...it, ill: { ...it.ill, "grade.saturation": 2.2 } }, m, "ngc_4414", "illustrative");
    expect(loadTuning(m, "ngc_4414", "illustrative").ill["grade.saturation"]).toBe(2.2);
  });
});
