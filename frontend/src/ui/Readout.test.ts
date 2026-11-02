import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Readout } from "./Readout";
import { attrs, classes, classOf, colourLiterals, cssRule, stylesheet } from "./testing";

const css = stylesheet("Readout.module.css");

describe("Readout (the design system's components/data/Readout.jsx)", () => {
  it("is the label, then the value with its unit, then the delta", () => {
    const html = renderToStaticMarkup(h(Readout, { label: "Seeing", value: "0.42", unit: "″", delta: "± 0.03" }));
    const order = ["Seeing", "0.42", "″", "± 0.03"].map((t) => html.indexOf(t));
    expect(order.every((at, k) => at >= 0 && (k === 0 || at > order[k - 1]))).toBe(true);
  });

  it("leaves out the unit and the delta when there are none", () => {
    const html = renderToStaticMarkup(h(Readout, { label: "Objects", value: "1,847" }));
    expect(html.match(/<span/g)).toHaveLength(1);
    expect(html.match(/<div/g)).toHaveLength(3);
  });

  it("comes in the design's three sizes and four tones, md and the primary ink by default, aligned left or right", () => {
    const plain = renderToStaticMarkup(h(Readout, { label: "a", value: 1 }));
    expect(classes(plain)[3]).toMatch(/value md$/);
    expect(classes(renderToStaticMarkup(h(Readout, { label: "a", value: 1, size: "lg", tone: "caution" })))[3]).toMatch(/lg caution$/);
    expect(classOf(renderToStaticMarkup(h(Readout, { label: "a", value: 1, align: "right" })))).toContain("right");
    expect(cssRule(css, ".lg")).toContain("var(--size-2xl)");
    expect(cssRule(css, ".sm")).toContain("var(--size-md)");
    expect(cssRule(css, ".value")).toMatch(/var\(--font-mono\);[\s\S]*var\(--weight-light\);/);
    expect(colourLiterals(css)).toEqual([]);
  });
});
