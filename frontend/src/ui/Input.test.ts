import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Input } from "./Input";
import { attrs, classes, colourLiterals, cssRule, stylesheet } from "./testing";

const css = stylesheet("Input.module.css");

describe("Input (the design system's components/forms/Input.jsx)", () => {
  it("is a field its label names, with the unit after the value and the hint describing it", () => {
    const html = renderToStaticMarkup(h(Input, { label: "Distance", suffix: "Mpc", hint: "Read at the template's", mono: true, type: "number", value: 19.1, onChange: () => undefined }));
    const [forId] = attrs(html, "for");
    expect(attrs(html, "id")).toContain(forId);
    expect(html).toMatch(new RegExp(`<input id="${forId}"`));
    const [by] = attrs(html, "aria-describedby");
    expect(by).toBe(`${forId}-note`);
    expect(html).toContain(`id="${by}"`);
    expect(html.indexOf('value="19.1"')).toBeLessThan(html.indexOf("Mpc"));
    expect(classes(html).find((c) => c.includes("input"))).toMatch(/mono/);
  });

  it("is named by aria-label where it has no visible label, and keeps the caller's description", () => {
    const html = renderToStaticMarkup(h(Input, { "aria-label": "Event 1 time", "aria-describedby": "row-1", size: "sm" }));
    expect(html).not.toContain("<label");
    expect(attrs(html, "aria-label")).toEqual(["Event 1 time"]);
    expect(attrs(html, "aria-describedby")).toEqual(["row-1"]);
    expect(classes(html)[1]).toMatch(/frame sm/);
  });

  it("marks a fault invalid, says it in place of the hint, in coral", () => {
    const html = renderToStaticMarkup(h(Input, { label: "Scale", hint: "per pixel", error: "The scale must be above zero." }));
    expect(attrs(html, "aria-invalid")).toEqual(["true"]);
    expect(html).toContain("The scale must be above zero.");
    expect(html).not.toContain("per pixel");
    expect(cssRule(css, ".invalid,\n.invalid:focus-within")).toContain("var(--coral-4)");
  });

  it("draws the focus ring on its frame, sizes from the control tokens, disabled at 40 %, no colour of its own", () => {
    expect(cssRule(css, ".frame:focus-within")).toContain("box-shadow: var(--shadow-focus);");
    expect(cssRule(css, ".lg")).toContain("height: var(--control-lg);");
    expect(cssRule(css, ".disabled")).toContain("opacity: 0.4;");
    expect(renderToStaticMarkup(h(Input, { label: "x", disabled: true }))).toContain("disabled");
    expect(colourLiterals(css)).toEqual([]);
  });
});
