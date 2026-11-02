import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Switch } from "./Switch";
import { attrs, classes, colourLiterals, cssRule, stylesheet } from "./testing";

const css = stylesheet("Switch.module.css");

describe("Switch (the design system's components/forms/Switch.jsx)", () => {
  it("is a native checkbox with the switch role inside its label, so the label names it and Space flips it", () => {
    const html = renderToStaticMarkup(h(Switch, { label: "diffraction spikes", onChange: () => undefined }));
    expect(html).toMatch(/^<label[^>]*><input type="checkbox" role="switch"/);
    expect(html).toContain("diffraction spikes</span>");
    expect(html).not.toContain("checked=");
  });

  it("says its state through the native box, and draws it on the track", () => {
    const on = renderToStaticMarkup(h(Switch, { label: "x", checked: true, onChange: () => undefined }));
    expect(on).toContain('checked=""');
    expect(classes(on)[2]).toMatch(/track on/);
    const off = renderToStaticMarkup(h(Switch, { label: "x", onChange: () => undefined }));
    expect(classes(off)[2]).toMatch(/track$/);
  });

  it("is disabled at 40 % and takes a title", () => {
    const html = renderToStaticMarkup(h(Switch, { label: "x", disabled: true, title: "Why it is off" }));
    expect(html).toContain("disabled");
    expect(attrs(html, "title")).toEqual(["Why it is off"]);
    expect(cssRule(css, ".disabled")).toContain("opacity: 0.4;");
  });

  it("is round, magenta when on, ringed on the keyboard's focus, with no colour of its own", () => {
    expect(cssRule(css, ".track")).toMatch(/width: 30px;[\s\S]*height: 16px;[\s\S]*border-radius: var\(--radius-full\);/);
    expect(cssRule(css, ".on,\n.switch:hover .on")).toContain("background: var(--magenta-4);");
    expect(cssRule(css, ".on .knob")).toContain("var(--magenta-1)");
    expect(cssRule(css, ".input:focus-visible + .track")).toContain("box-shadow: var(--shadow-focus);");
    expect(colourLiterals(css)).toEqual([]);
  });
});
