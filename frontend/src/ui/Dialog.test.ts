import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { Dialog, trappedFocus } from "./Dialog";
import { attrs, colourLiterals, cssRule, stylesheet } from "./testing";

const css = stylesheet("Dialog.module.css");
const noop = () => undefined;

describe("Dialog (the design system's components/core/Dialog.jsx)", () => {
  it("draws nothing while closed", () => {
    expect(renderToStaticMarkup(h(Dialog, { open: false, title: "Discard the draft", onClose: noop }, "x"))).toBe("");
  });

  it("is a modal dialog named by its title, with the label, the body, the footer and a named close button", () => {
    const html = renderToStaticMarkup(
      h(Dialog, { open: true, title: "Discard the draft", label: "Edit galaxy", footer: h("button", null, "Discard"), onClose: noop }, "Two groups changed."),
    );
    expect(html).toContain('role="dialog"');
    expect(html).toContain('aria-modal="true"');
    const [labelledBy] = attrs(html, "aria-labelledby");
    expect(html).toContain(`id="${labelledBy}"`);
    expect(html).toContain('tabindex="-1"');
    expect(attrs(html, "aria-label")).toEqual(["Close"]);
    for (const text of ["Edit galaxy", "Discard the draft", "Two groups changed.", "<footer", "Discard</button>"]) expect(html).toContain(text);
    expect(html).toContain('style="max-width:480px"');
  });

  it("can be an alert dialog, and takes its width", () => {
    const html = renderToStaticMarkup(h(Dialog, { open: true, title: "This view failed", role: "alertdialog", width: 360, onClose: noop }));
    expect(html).toContain('role="alertdialog"');
    expect(html).toContain('style="max-width:360px"');
    expect(html).not.toContain("<footer");
  });

  it("keeps Tab inside: last to first, first back to last, the panel's own focus to either end", () => {
    expect(trappedFocus(3, 2, false)).toBe(0);
    expect(trappedFocus(3, 0, true)).toBe(2);
    expect(trappedFocus(3, -1, false)).toBe(0);
    expect(trappedFocus(3, -1, true)).toBe(2);
    expect(trappedFocus(3, 1, false)).toBeNull();
    expect(trappedFocus(3, 1, true)).toBeNull();
    expect(trappedFocus(0, -1, false)).toBe(-1);
  });

  it("blurs what is behind it under the scrim and lifts the panel by --shadow-3, with no colour of its own", () => {
    expect(cssRule(css, ".scrim")).toMatch(/background: var\(--scrim\);[\s\S]*backdrop-filter: var\(--blur-md\);/);
    expect(cssRule(css, ".panel")).toMatch(/border-radius: var\(--radius-lg\);[\s\S]*box-shadow: var\(--shadow-3\);/);
    expect(colourLiterals(css)).toEqual([]);
  });
});
