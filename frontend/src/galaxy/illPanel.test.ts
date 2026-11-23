import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { features, illControls } from "./illustrative";
import { ILL_OPEN_FEATURE, TuningPanel, illGroups, illName } from "./TuningPanel";
import { TUNING_CONTROLS, illustrativeDefaultsFor } from "./tuning";

// S105 fix R3: the Illustrative group by feature, collapsible, every slider named uniquely, and a filter.
const STATS = { width: 0, height: 0, ms: 0 };
const decode = (s: string) => s.replace(/&quot;/g, '"').replace(/&#x27;/g, "'").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const labels = (html: string) => [...html.matchAll(/aria-label="([^"]*)"/g)].map((m) => decode(m[1]));

function panel(filter = "") {
  const t = illustrativeDefaultsFor("ngc_4414");
  return renderToStaticMarkup(
    h(TuningPanel, { tuning: t, defaults: t, onChange: () => {}, stats: STATS, template: "ngc_4414", filterSet: "rgb", exposure: 0, initiallyOpen: true, look: "illustrative", initialIllFilter: filter }),
  );
}

describe("the Illustrative group (S105 fix R3)", () => {
  it("names every illustrative slider uniquely, its feature's label first, apart from every other control's name", () => {
    const names = illControls().map(({ feature, control }) => illName(feature, control));
    expect(new Set(names).size).toBe(names.length);
    expect(names.length).toBeGreaterThan(150);
    const lanes = features().find((f) => f.id === "lanes")!;
    const floc = features().find((f) => f.id === "floc")!;
    const mottle = (f: typeof lanes) => illName(f, f.controls.find((c) => c.key === "mottle")!);
    expect(mottle(lanes)).toBe(`${lanes.label}: mottle`);
    expect(mottle(floc)).toBe(`${floc.label}: mottle`);
    expect(mottle(lanes)).not.toBe(mottle(floc));
    const others = new Set(TUNING_CONTROLS.map((c) => c.label));
    for (const n of names) expect(others.has(n)).toBe(false);
  });

  it("draws one collapsible heading per feature with its about, only the grade's block open, and unique names on the page", () => {
    const html = panel();
    for (const f of features()) {
      expect(html).toContain(`data-ill-feature="${f.id}"`);
      expect(decode(html)).toContain(f.about);
    }
    const open = [...html.matchAll(/aria-expanded="(true|false)"[^>]*data-ill-feature="([a-z]+)"/g)].map((m) => [m[2], m[1]]);
    expect(open.length).toBe(features().length);
    for (const [id, expanded] of open) expect(expanded).toBe(id === ILL_OPEN_FEATURE ? "true" : "false");
    const shown = labels(html);
    expect(new Set(shown).size).toBe(shown.length);
    const grade = features().find((f) => f.id === ILL_OPEN_FEATURE)!;
    for (const c of grade.controls) expect(shown).toContain(illName(grade, c));
    const lanes = features().find((f) => f.id === "lanes")!;
    for (const c of lanes.controls) expect(shown).not.toContain(illName(lanes, c));
    // the copy box and the paste box as they were
    expect(shown).toContain("The changed display choices, as JSON");
    expect(shown).toContain("A combination to load, as the copy box's JSON");
    expect(shown).toContain("Filter the illustrative controls");
  });

  it("filters to the controls whose label or about holds the word, every matching feature opened", () => {
    const groups = illGroups("bar");
    const matched = groups.flatMap((g) => g.controls.map((c) => illName(g.feature, c.control)));
    expect(matched.length).toBeGreaterThan(0);
    for (const g of groups) for (const { control } of g.controls) expect(`${control.label} ${control.about}`.toLowerCase()).toContain("bar");
    // every control that holds it is listed, and nothing else
    const all = illControls().filter(({ control }) => `${control.label}\n${control.about}`.toLowerCase().includes("bar"));
    expect(matched.length).toBe(all.length);
    expect(illGroups("BAR").length).toBe(groups.length);
    expect(illGroups("").flatMap((g) => g.controls).length).toBe(illControls().length);
    const shown = labels(panel("bar")).filter((n) => matched.includes(n) || illControls().some(({ feature, control }) => illName(feature, control) === n));
    expect(shown.sort()).toEqual([...matched].sort());
    expect(illGroups("no such word anywhere")).toEqual([]);
  });
});
