import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Checkbox } from "./Checkbox";
import { attrs, classes, colourLiterals, cssRule, stylesheet } from "./testing";

const css = stylesheet("Checkbox.module.css");

describe("Checkbox (the design system's components/forms/Checkbox.jsx)", () => {
  it("is a native checkbox inside its label, so the label names it and Space toggles it", () => {
    const html = renderToStaticMarkup(h(Checkbox, { label: "Thick disc", onChange: () => undefined }));
    expect(html).toMatch(/^<label[^>]*><input type="checkbox"/);
    expect(html).toContain("Thick disc</span>");
    expect(html).not.toContain("checked=");
    expect(html).not.toContain("<svg");
  });

  it("draws the knockout tick when checked, the bar and aria-checked mixed when indeterminate", () => {
    const on = renderToStaticMarkup(h(Checkbox, { label: "x", checked: true, onChange: () => undefined }));
    expect(on).toContain('checked=""');
    expect(on).toContain('<path d="M5 13l4 4L19 7">');
    expect(classes(on)[2]).toMatch(/box on/);
    const mixed = renderToStaticMarkup(h(Checkbox, { label: "x", indeterminate: true }));
    expect(attrs(mixed, "aria-checked")).toEqual(["mixed"]);
    expect(mixed).not.toContain("<svg");
  });

  it("is described by its description, and disabled at 40 %", () => {
    const html = renderToStaticMarkup(h(Checkbox, { label: "x", description: "Stars older than 8 Gyr", disabled: true }));
    const [by] = attrs(html, "aria-describedby");
    expect(html).toContain(`id="${by}"`);
    expect(html).toContain("disabled");
    expect(cssRule(css, ".disabled")).toContain("opacity: 0.4;");
  });

  it("rings the box when the hidden input has the keyboard's focus, and holds no colour of its own", () => {
    expect(cssRule(css, ".input:focus-visible + .box")).toContain("box-shadow: var(--shadow-focus);");
    expect(cssRule(css, ".input")).toMatch(/inset: 0;[\s\S]*opacity: 0;/);
    expect(cssRule(css, ".input")).not.toContain("pointer-events");
    expect(cssRule(css, ".on,\n.checkbox:hover .on")).toContain("background: var(--magenta-3);");
    expect(colourLiterals(css)).toEqual([]);
  });
});
