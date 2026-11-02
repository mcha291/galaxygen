import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { STATUS_TONES, StatusDot } from "./StatusDot";
import { attrs, classes, colourLiterals, cssRule, stylesheet } from "./testing";

const css = stylesheet("StatusDot.module.css");

describe("StatusDot (the design system's components/data/StatusDot.jsx)", () => {
  it("is a dot hidden from the reader and the state in words beside it; idle by default", () => {
    const html = renderToStaticMarkup(h(StatusDot, { label: "Nominal" }));
    expect(attrs(html, "data-tone")).toEqual(["idle"]);
    expect(attrs(html, "aria-hidden")).toEqual(["true"]);
    expect(html).toContain("Nominal</span>");
  });

  it("takes every status tone from the status tokens (the mockup's accent the selected magenta), and glows only when nominal and live", () => {
    for (const tone of STATUS_TONES) expect(cssRule(css, `.${tone}`)).toMatch(/background: var\(--(status-|ink-4|magenta-3)/);
    expect(cssRule(css, ".accent")).toContain("var(--magenta-3)");
    const live = renderToStaticMarkup(h(StatusDot, { tone: "nominal", pulse: true }));
    expect(classes(live)[1]).toMatch(/pulse/);
    const fault = renderToStaticMarkup(h(StatusDot, { tone: "fault", pulse: true }));
    expect(classes(fault)[1]).not.toMatch(/pulse/);
  });

  it("carries a status line's own words after the label, and passes its role on", () => {
    const html = renderToStaticMarkup(h(StatusDot, { tone: "caution", role: "status" }, "Stale · the previous galaxy"));
    expect(html).toMatch(/^<span [^>]*role="status"/);
    expect(html).toContain("Stale · the previous galaxy</span>");
  });

  it("is round and 8 px, with no colour of its own", () => {
    expect(cssRule(css, ".dot")).toMatch(/width: 8px;[\s\S]*border-radius: var\(--radius-full\);/);
    expect(colourLiterals(css)).toEqual([]);
  });
});
