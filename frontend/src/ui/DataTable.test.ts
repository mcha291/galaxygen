import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { type Column, DataTable, selectsRow } from "./DataTable";
import { attrs, classes, colourLiterals, cssRule, stylesheet } from "./testing";

const css = stylesheet("DataTable.module.css");

interface Star {
  id: string;
  name: string;
  mag: number;
}
const COLUMNS: Column<Star>[] = [
  { key: "name", label: "Object" },
  { key: "mag", label: "V", align: "right", mono: true, render: (r) => `${r.mag.toFixed(2)} mag`, width: "30%" },
];
const ROWS: Star[] = [
  { id: "a", name: "Vega", mag: 0.03 },
  { id: "b", name: "Deneb", mag: 1.25 },
];

describe("DataTable (the design system's components/data/DataTable.jsx)", () => {
  it("is a named table, its headers columns, numbers mono and right-aligned through `render`", () => {
    const html = renderToStaticMarkup(h(DataTable<Star>, { columns: COLUMNS, rows: ROWS, "aria-label": "Catalogue" }));
    expect(html).toMatch(/^<table [^>]*aria-label="Catalogue"/);
    expect(attrs(html, "scope")).toEqual(["col", "col"]);
    expect(html).toContain("0.03 mag");
    expect(html).toContain('style="width:30%"');
    expect(classes(html).filter((c) => c.endsWith("head"))[1]).toBe("cell mono right head");
    expect(html).not.toContain("tabindex");
    expect(html).not.toContain("aria-selected");
  });

  it("makes rows choosable when it is told how, the chosen one selected", () => {
    const html = renderToStaticMarkup(h(DataTable<Star>, { columns: COLUMNS, rows: ROWS, selectedId: "b", onSelectRow: () => undefined }));
    expect(attrs(html, "aria-selected")).toEqual(["false", "true"]);
    expect(attrs(html, "tabindex")).toEqual(["0", "0"]);
    expect(selectsRow("Enter")).toBe(true);
    expect(selectsRow(" ")).toBe(true);
    expect(selectsRow("a")).toBe(false);
  });

  it("says what the window lacks where there are no rows", () => {
    expect(renderToStaticMarkup(h(DataTable<Star>, { columns: COLUMNS, rows: [] }))).toContain("No rows in this window.");
    expect(renderToStaticMarkup(h(DataTable<Star>, { columns: COLUMNS, rows: [], empty: "No mergers." }))).toContain("No mergers.");
  });

  it("comes at the telemetry density on request, its cells on the 2 / 4 px steps", () => {
    expect(classes(renderToStaticMarkup(h(DataTable<Star>, { columns: COLUMNS, rows: ROWS, dense: true })))[0]).toBe("table dense");
    expect(classes(renderToStaticMarkup(h(DataTable<Star>, { columns: COLUMNS, rows: ROWS })))[0]).toBe("table");
    expect(cssRule(css, ".dense .cell")).toContain("padding: var(--space-1) var(--space-2);");
    // A column of long names wraps where the others end in an ellipsis.
    const wrapped = renderToStaticMarkup(h(DataTable<Star>, { columns: [{ key: "name", label: "Object", wrap: true }], rows: ROWS }));
    expect(classes(wrapped).filter((c) => c.startsWith("cell"))).toEqual(["cell wrap head", "cell wrap", "cell wrap"]);
    expect(cssRule(css, ".wrap")).toContain("white-space: normal;");
  });

  it("draws the selected row's rule and the header from the tokens, with no colour of its own", () => {
    expect(cssRule(css, ".selected")).toContain("box-shadow: inset 2px 0 0 var(--magenta-3);");
    expect(cssRule(css, ".head")).toContain("font: var(--text-label);");
    expect(colourLiterals(css)).toEqual([]);
  });
});
