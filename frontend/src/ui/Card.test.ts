import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Card } from "./Card";
import { attrs, classOf, colourLiterals, cssRule, stylesheet } from "./testing";

const css = stylesheet("Card.module.css");

describe("Card (the design system's components/core/Card.jsx)", () => {
  it("is a section named by its title, with the label above it and the actions beside", () => {
    const html = renderToStaticMarkup(h(Card, { title: "Deep Field 07", label: "Survey", actions: h("button", null, "Export CSV") }, "body"));
    expect(html.startsWith("<section")).toBe(true);
    const [labelledBy] = attrs(html, "aria-labelledby");
    expect(labelledBy).toBeTruthy();
    expect(html).toContain(`id="${labelledBy}"`);
    expect(html.indexOf("Survey")).toBeLessThan(html.indexOf("Deep Field 07"));
    expect(html).toContain("<header");
    expect(html).toContain("Export CSV");
  });

  it("has no header and no name without a title, label or actions", () => {
    const html = renderToStaticMarkup(h(Card, null, "body"));
    expect(html).not.toContain("<header");
    expect(html).not.toContain("aria-labelledby");
    expect(classOf(html)).toContain("card");
  });

  it("takes the body's padding as a token, and is drawn by the hairline and the inset highlight, no drop shadow", () => {
    expect(renderToStaticMarkup(h(Card, { padding: "var(--space-3)" }, "x"))).toContain('style="padding:var(--space-3)"');
    const card = cssRule(css, ".card");
    expect(card).toContain("background: var(--surface-card);");
    expect(card).toContain("box-shadow: var(--shadow-inset);");
    expect(card).toContain("border-radius: var(--radius-md);");
    expect(colourLiterals(css)).toEqual([]);
  });
});
