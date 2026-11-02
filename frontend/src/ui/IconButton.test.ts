import { X } from "lucide-react";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { IconButton } from "./IconButton";
import { attrs, classOf, colourLiterals, cssRule, stylesheet } from "./testing";

const css = stylesheet("IconButton.module.css");

describe("IconButton (the design system's components/core/IconButton.jsx)", () => {
  it("is a button named by its label, which is also its title", () => {
    const html = renderToStaticMarkup(h(IconButton, { label: "Close the edit panel" }, h(X)));
    expect(html.startsWith("<button")).toBe(true);
    expect(attrs(html, "aria-label")).toEqual(["Close the edit panel"]);
    expect(attrs(html, "title")).toEqual(["Close the edit panel"]);
    expect(html).toContain('type="button"');
    expect(html).not.toContain("aria-pressed");
  });

  it("comes in the design's three sizes, 24 / 32 / 40 px, md by default", () => {
    expect(classOf(renderToStaticMarkup(h(IconButton, { label: "x" })))).toContain("md");
    for (const [size, token] of [["sm", "--control-sm"], ["md", "--control-md"], ["lg", "--control-lg"]] as const) {
      expect(classOf(renderToStaticMarkup(h(IconButton, { label: "x", size })))).toContain(size);
      expect(cssRule(css, `.${size}`)).toContain(`width: var(${token});`);
    }
  });

  it("says a toggle's state as aria-pressed and draws it magenta; disabled is 40 %", () => {
    const on = renderToStaticMarkup(h(IconButton, { label: "Fold", selected: true }));
    expect(on).toContain('aria-pressed="true"');
    expect(classOf(on)).toContain("selected");
    expect(renderToStaticMarkup(h(IconButton, { label: "Fold", selected: false }))).toContain('aria-pressed="false"');
    expect(cssRule(css, ".button:disabled")).toContain("opacity: 0.4;");
    expect(renderToStaticMarkup(h(IconButton, { label: "x", disabled: true }))).toContain("disabled");
  });

  it("holds no colour of its own", () => {
    expect(colourLiterals(css)).toEqual([]);
  });
});
