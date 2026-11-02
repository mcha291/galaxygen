import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Tooltip } from "./Tooltip";
import { attrs, classes, colourLiterals, cssRule, stylesheet } from "./testing";

const css = stylesheet("Tooltip.module.css");

describe("Tooltip (the design system's components/core/Tooltip.jsx)", () => {
  it("is a tooltip the control it explains is described by", () => {
    const html = renderToStaticMarkup(h(Tooltip, { content: "Each stop doubles the light", children: h("button", null, "exposure") }));
    const [tip] = /<span id="[^"]+" role="tooltip"/.exec(html) ?? [""];
    const id = /id="([^"]+)"/.exec(tip)?.[1];
    expect(id).toBeTruthy();
    expect(attrs(html, "aria-describedby")).toEqual([id]);
    expect(html).toContain("Each stop doubles the light</span>");
  });

  it("keeps a description the control already has beside its own", () => {
    const html = renderToStaticMarkup(h(Tooltip, { content: "x", children: h("button", { "aria-describedby": "hint" }, "b") }));
    expect(attrs(html, "aria-describedby")[0]).toMatch(/^hint \S+$/);
  });

  it("shows on hover and on focus, and hides on Escape; above by default, below or from an edge on request", () => {
    expect(cssRule(css, ".anchor:hover > .tip,\n.anchor:focus-within > .tip")).toContain("opacity: 1;");
    expect(cssRule(css, ".anchor[data-dismissed] > .tip")).toContain("opacity: 0;");
    const top = renderToStaticMarkup(h(Tooltip, { content: "x", children: h("span", null, "y") }));
    expect(classes(top)[1]).toMatch(/top.*center/);
    const below = renderToStaticMarkup(h(Tooltip, { content: "x", placement: "bottom", align: "start", children: h("span", null, "y") }));
    expect(classes(below)[1]).toMatch(/bottom.*start/);
  });

  it("is one line on the raised surface, with no colour of its own", () => {
    expect(cssRule(css, ".tip")).toMatch(/background: var\(--surface-raised\);[\s\S]*white-space: nowrap;/);
    expect(colourLiterals(css)).toEqual([]);
  });
});
