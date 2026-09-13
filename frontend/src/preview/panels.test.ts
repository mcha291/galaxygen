import { describe, expect, it } from "vitest";

import type { FieldDecl } from "../api";
import { panelsAt, wantedAt } from "./panels";

function decl(name: string, over: Partial<Record<string, unknown>>): FieldDecl {
  return {
    name, label: name, unit: "km/s", unit_display: "km/s", kind: "field", domain: "grid",
    axes: ["R"], checkpoint: 1, stage: "halo", ramp: { kind: "ramp", scale: "linear" }, ...over,
  } as FieldDecl;
}

const FIELDS = [
  decl("circular_velocity", {}),
  decl("halo_circular_velocity", {}),
  decl("disc_surface_density", { unit: "Msun/pc2", ramp: { kind: "ramp", scale: "log" } }),
  decl("infall_tail_surface_density", { unit: "Msun/pc2", ramp: { kind: "ramp", scale: "log" } }),
  decl("halo_potential", { unit: "km2/s2", axes: ["R", "z"] }),
  decl("halo_virial_mass", { unit: "Msun", kind: "scalar", domain: "galaxy", axes: [] }),
  decl("disc_heating", { axes: ["t"], checkpoint: 2, stage: "assembly" }),
  decl("star_radius", { unit: "kpc", kind: "column", domain: "object", axes: [], checkpoint: 5, stage: "systems" }),
];

describe("panelsAt", () => {
  it("puts profiles sharing an axis and a unit on one plot", () => {
    const p = panelsAt(FIELDS, 1);
    expect(p.lines.map((l) => [l.key, l.fields.map((f) => f.name)])).toEqual([
      ["R:km/s", ["circular_velocity", "halo_circular_velocity"]],
      ["R:Msun/pc2", ["disc_surface_density", "infall_tail_surface_density"]],
    ]);
  });

  it("draws a plot in log only when every series on it is declared log", () => {
    const p = panelsAt(FIELDS, 1);
    expect(p.lines.map((l) => l.log)).toEqual([false, true]);
  });

  it("leaves 2D fields out of the line plots, takes the scalars, and knows when stars exist", () => {
    const p = panelsAt(FIELDS, 1);
    expect(p.lines.flatMap((l) => l.fields.map((f) => f.name))).not.toContain("halo_potential");
    expect(p.scalars.map((f) => f.name)).toEqual(["halo_virial_mass"]);
    expect(p.catalogue).toBe(false);
    expect(panelsAt(FIELDS, 5).catalogue).toBe(true);
  });

  it("reads only the checkpoint asked for", () => {
    expect(panelsAt(FIELDS, 2).lines.map((l) => l.key)).toEqual(["t:km/s"]);
  });
});

describe("wantedAt", () => {
  it("asks for every plotted field and every scalar", () => {
    expect(wantedAt(panelsAt(FIELDS, 1))).toEqual([
      "circular_velocity", "halo_circular_velocity", "disc_surface_density", "infall_tail_surface_density", "halo_virial_mass",
    ]);
  });
});
