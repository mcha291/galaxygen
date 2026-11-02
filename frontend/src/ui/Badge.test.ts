import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { BADGE_TONES, Badge } from "./Badge";
import { classOf, colourLiterals, cssRule, stylesheet } from "./testing";

const css = stylesheet("Badge.module.css");

describe("Badge (the design system's components/core/Badge.jsx)", () => {
  it("is a span with its text, neutral by default", () => {
    const html = renderToStaticMarkup(h(Badge, null, "changed"));
    expect(html).toMatch(/^<span [^>]*data-tone="neutral"[^>]*>changed<\/span>$/);
    expect(classOf(html)).toContain("badge");
    expect(classOf(html)).toContain("neutral");
  });

  it("takes every tone of the design, each a rule of the tokens' own colours", () => {
    for (const tone of BADGE_TONES) {
      const html = renderToStaticMarkup(h(Badge, { tone }, tone));
      expect(html).toContain(`data-tone="${tone}"`);
      expect(cssRule(css, `.${tone}`)).toMatch(/color: var\(--/);
    }
    expect(cssRule(css, ".caution")).toContain("var(--amber-2)");
    expect(cssRule(css, ".accent")).toContain("var(--magenta-2)");
  });

  it("is mono, uppercase and 18 px high, and passes its attributes on", () => {
    expect(cssRule(css, ".badge")).toMatch(/height: 18px;[\s\S]*font: var\(--text-label\);[\s\S]*text-transform: uppercase;/);
    const html = renderToStaticMarkup(h(Badge, { tone: "caution", title: "An input differs" }, "changed"));
    expect(html).toContain('title="An input differs"');
  });

  it("holds no colour of its own: every colour is a token", () => {
    expect(colourLiterals(css)).toEqual([]);
  });
});
