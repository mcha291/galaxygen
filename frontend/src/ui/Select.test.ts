import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Select, optionOf } from "./Select";
import { attrs, classes, colourLiterals, cssRule, stylesheet } from "./testing";

const css = stylesheet("Select.module.css");

describe("Select (the design system's components/forms/Select.jsx)", () => {
  it("is a native select its label names, its options words or values with words", () => {
    const html = renderToStaticMarkup(
      h(Select, { label: "Tone mapping", options: ["aces", { value: "agx", label: "AgX", title: "Blender's" }], value: "agx", onChange: () => undefined }),
    );
    const [forId] = attrs(html, "for");
    expect(html).toMatch(new RegExp(`<select id="${forId}"`));
    expect(attrs(html, "value")).toEqual(["aces", "agx"]);
    expect(html).toContain('<option value="agx" title="Blender&#x27;s" selected="">AgX</option>');
    expect(optionOf("x")).toEqual({ value: "x", label: "x" });
  });

  it("is named by aria-label without a label, described by its hint with one", () => {
    const bare = renderToStaticMarkup(h(Select, { "aria-label": "The scale's unit", options: ["arcsec", "kpc"], size: "sm" }));
    expect(bare).not.toContain("<label");
    expect(attrs(bare, "aria-label")).toEqual(["The scale&#x27;s unit"]);
    expect(classes(bare).find((c) => c.startsWith("select"))).toMatch(/sm/);
    const hinted = renderToStaticMarkup(h(Select, { label: "Unit", hint: "per pixel", options: ["kpc"] }));
    const [by] = attrs(hinted, "aria-describedby");
    expect(hinted).toContain(`id="${by}"`);
  });

  it("draws a faint chevron hidden from the reader, and is disabled at 40 %", () => {
    const html = renderToStaticMarkup(h(Select, { label: "x", options: ["a"], disabled: true }));
    expect(html).toMatch(/<svg[^>]*aria-hidden="true"/);
    expect(html).toContain("disabled");
    expect(cssRule(css, ".disabled")).toContain("opacity: 0.4;");
  });

  it("is the inset with the focus ring, no colour of its own", () => {
    expect(cssRule(css, ".select")).toMatch(/appearance: none;[\s\S]*background: var\(--surface-inset\);/);
    expect(cssRule(css, ".select:focus-visible")).toContain("box-shadow: var(--shadow-focus);");
    expect(colourLiterals(css)).toEqual([]);
  });
});
