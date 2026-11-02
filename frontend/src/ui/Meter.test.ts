import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Meter, meterPercent } from "./Meter";
import { attrs, classes, colourLiterals, cssRule, stylesheet } from "./testing";

const css = stylesheet("Meter.module.css");

describe("Meter (the design system's components/data/Meter.jsx)", () => {
  it("is a progress bar named by its label, its value and range said, its value text the label's at the right", () => {
    const html = renderToStaticMarkup(h(Meter, { value: 9000, max: 20000, label: "Point budget", valueLabel: "9,000 stars" }));
    expect(html).toContain('role="progressbar"');
    expect(attrs(html, "aria-valuenow")).toEqual(["9000"]);
    expect(attrs(html, "aria-valuemin")).toEqual(["0"]);
    expect(attrs(html, "aria-valuemax")).toEqual(["20000"]);
    expect(attrs(html, "aria-label")).toEqual(["Point budget"]);
    expect(attrs(html, "aria-valuetext")).toEqual(["9,000 stars"]);
    expect(html).toContain('style="width:45%"');
    expect(html).toContain('style="height:4px"');
  });

  it("holds the fill to 0-100 %", () => {
    expect(meterPercent(50, 100)).toBe(50);
    expect(meterPercent(150, 100)).toBe(100);
    expect(meterPercent(-1, 100)).toBe(0);
    expect(meterPercent(1, 0)).toBe(0);
    expect(meterPercent(Number.NaN, 10)).toBe(0);
  });

  it("has no head without a label or a value, and fills in the tone's colour; accent by default", () => {
    const bare = renderToStaticMarkup(h(Meter, { value: 1, max: 4 }));
    expect(bare).not.toContain("aria-label");
    expect(classes(bare).at(-1)).toMatch(/accent/);
    expect(classes(renderToStaticMarkup(h(Meter, { value: 1, tone: "fault" }))).at(-1)).toMatch(/fault/);
    expect(cssRule(css, ".nominal")).toContain("var(--aqua-3)");
    expect(cssRule(css, ".track")).toContain("background: var(--surface-inset);");
    expect(colourLiterals(css)).toEqual([]);
  });
});
