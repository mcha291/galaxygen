import { readFileSync } from "node:fs";

import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { CORES, MODIFIERS, SPECTRAL_COLORS, SPRITE_URL, StarIcon, starLayers } from "./StarIcon";
import { attrs } from "./testing";

const sprite = readFileSync(new URL("../../public/stellar-icons-modernist.svg", import.meta.url), "utf-8");
const design = readFileSync(new URL("../../../docs/design/stellar-icons-modernist.svg", import.meta.url), "utf-8");
const symbols = new Set([...sprite.matchAll(/<symbol id="([^"]+)"/g)].map((m) => m[1]));

describe("StarIcon (the design system's components/data/StarIcon.jsx)", () => {
  it("draws from the design's own sprite, served under the app's base", () => {
    expect(sprite).toBe(design);
    expect(SPRITE_URL).toBe("/stellar-icons-modernist.svg");
  });

  it("names every core and modifier the sprite carries, and colours the ten classes from the spectral tokens", () => {
    for (const core of CORES) expect(symbols.has(`mo-core-${core}`), core).toBe(true);
    for (const mod of MODIFIERS) expect(symbols.has(`mo-mod-${mod}`), mod).toBe(true);
    expect(Object.keys(SPECTRAL_COLORS).join("")).toBe("OBAFGKMLTY");
    for (const [cls, colour] of Object.entries(SPECTRAL_COLORS)) expect(colour).toBe(`var(--spectral-${cls.toLowerCase()})`);
  });

  it("layers the glyph in the design's z-order", () => {
    expect(starLayers({ core: "giant", spectral: "K", luminosity: 3, modifiers: ["companion", "flare"], refGrid: true, sizeTick: 2 })).toEqual([
      "mo-ref-grid",
      "mo-lum-3",
      "mo-core-giant",
      "mo-mod-companion",
      "mo-mod-flare",
      "mo-cls-K",
      "mo-size-2",
    ]);
    expect(starLayers({ showClass: false })).toEqual(["mo-core-ms"]);
  });

  it("is an image named by its class and core, or its title, recoloured through --sp, --ink and --bg", () => {
    const html = renderToStaticMarkup(h(StarIcon, { spectral: "M", core: "dwarf", size: 24 }));
    expect(html).toMatch(/^<svg width="24" height="24" viewBox="0 0 64 64" role="img" aria-label="M dwarf"/);
    expect(html).toContain("--sp:var(--spectral-m);--ink:var(--ink-2);--bg:var(--void-0)");
    expect(attrs(html, "href")).toEqual(["/stellar-icons-modernist.svg#mo-core-dwarf", "/stellar-icons-modernist.svg#mo-cls-M"]);
    const titled = renderToStaticMarkup(h(StarIcon, { title: "Sun" }));
    expect(attrs(titled, "aria-label")).toEqual(["Sun"]);
    expect(titled).toContain("<title>Sun</title>");
  });
});
