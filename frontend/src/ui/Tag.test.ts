import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Tag } from "./Tag";
import { attrs, classOf, colourLiterals, cssRule, stylesheet } from "./testing";

const css = stylesheet("Tag.module.css");

describe("Tag (the design system's components/core/Tag.jsx)", () => {
  it("is a mono chip with its text and no button when nothing removes it", () => {
    const html = renderToStaticMarkup(h(Tag, null, "F814W"));
    expect(classOf(html)).toContain("tag");
    expect(html).toContain("F814W");
    expect(html).not.toContain("<button");
    expect(cssRule(css, ".tag")).toMatch(/height: 22px;[\s\S]*var\(--font-mono\)/);
  });

  it("names its remove button, the design's word by default or the caller's", () => {
    const plain = renderToStaticMarkup(h(Tag, { onRemove: () => undefined }, "G"));
    expect(attrs(plain, "aria-label")).toEqual(["Remove"]);
    expect(plain).toContain('type="button"');
    const named = renderToStaticMarkup(h(Tag, { onRemove: () => undefined, removeLabel: "Remove event 2" }, "t 8.8 Gyr"));
    expect(attrs(named, "aria-label")).toEqual(["Remove event 2"]);
  });

  it("draws a data colour as a swatch hidden from the reader, and holds no colour of its own", () => {
    const html = renderToStaticMarkup(h(Tag, { color: "var(--spectral-k)" }, "K"));
    expect(html).toContain('style="background:var(--spectral-k)"');
    expect(html).toContain('aria-hidden="true"');
    expect(colourLiterals(css)).toEqual([]);
  });
});
