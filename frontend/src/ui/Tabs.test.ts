import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Tabs, tabKeyTarget } from "./Tabs";
import { attrs, colourLiterals, cssRule, stylesheet } from "./testing";

const css = stylesheet("Tabs.module.css");
const ITEMS = [
  { value: "science", label: "Science", title: "Every group's fields, previewed" },
  { value: "galaxy", label: "Galaxy" },
  { value: "system", label: "System", count: 3 },
] as const;

describe("Tabs (the design system's components/core/Tabs.jsx)", () => {
  it("is a named tab list of tabs, the selected one alone in the Tab order", () => {
    const html = renderToStaticMarkup(h(Tabs<(typeof ITEMS)[number]["value"]>, { items: ITEMS, value: "galaxy", onChange: () => undefined, "aria-label": "View" }));
    expect(html).toMatch(/^<div role="tablist" aria-label="View"/);
    expect(attrs(html, "role").filter((r) => r === "tab")).toHaveLength(3);
    expect(attrs(html, "aria-selected")).toEqual(["false", "true", "false"]);
    expect(attrs(html, "tabindex")).toEqual(["-1", "0", "-1"]);
    expect(attrs(html, "title")).toEqual(["Every group&#x27;s fields, previewed"]);
    expect(html).toContain(">3</span>");
  });

  it("moves with the arrow keys, wrapping, and to either end with Home and End", () => {
    expect(tabKeyTarget(3, 0, "ArrowRight")).toBe(1);
    expect(tabKeyTarget(3, 2, "ArrowRight")).toBe(0);
    expect(tabKeyTarget(3, 0, "ArrowLeft")).toBe(2);
    expect(tabKeyTarget(3, 1, "ArrowDown")).toBe(2);
    expect(tabKeyTarget(3, 1, "ArrowUp")).toBe(0);
    expect(tabKeyTarget(3, 1, "Home")).toBe(0);
    expect(tabKeyTarget(3, 1, "End")).toBe(2);
    expect(tabKeyTarget(3, 1, "Enter")).toBeNull();
    expect(tabKeyTarget(0, 0, "ArrowRight")).toBeNull();
  });

  it("draws the selected tab's magenta rule from the tokens, and holds no colour of its own", () => {
    expect(cssRule(css, ".selected,\n.selected:hover")).toContain("box-shadow: inset 0 -1px 0 var(--magenta-3);");
    expect(cssRule(css, ".tabs")).toContain("gap: var(--space-7);");
    expect(colourLiterals(css)).toEqual([]);
  });
});
