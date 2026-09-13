// What a checkpoint's preview shows, read off the field declarations rather than
// written down per checkpoint: every one-dimensional profile the checkpoint
// publishes, grouped onto one plot per (axis, unit); its galaxy-level scalars;
// and whether the star catalogue exists yet. A field a model adds (the advanced
// model's [α/Fe] profiles) appears with no change here.
import { hasCatalogue, scalarsAt } from "@interface/view.js";

import type { FieldDecl } from "../api";

export interface LinePanel {
  key: string;
  axis: string;
  unit: string;
  unitDisplay: string;
  log: boolean;
  fields: FieldDecl[];
}

export interface Panels {
  lines: LinePanel[];
  scalars: FieldDecl[];
  catalogue: boolean;
}

interface Declared extends FieldDecl {
  domain: string;
  axes: string[];
  checkpoint: number;
  unit_display?: string;
  kind: string;
}

export function panelsAt(fields: FieldDecl[], n: number): Panels {
  const declared = fields as Declared[];
  const groups = new Map<string, LinePanel>();
  for (const f of declared) {
    if (f.checkpoint !== n || f.domain !== "grid" || f.axes.length !== 1 || f.kind !== "field") continue;
    const key = `${f.axes[0]}:${f.unit}`;
    let panel = groups.get(key);
    if (!panel) {
      panel = { key, axis: f.axes[0], unit: f.unit, unitDisplay: f.unit_display ?? f.unit, log: true, fields: [] };
      groups.set(key, panel);
    }
    panel.fields.push(f);
    // Log only when every series on the panel is declared log: one linear series
    // among log ones would be drawn with its zero thrown away.
    panel.log &&= f.ramp?.scale === "log";
  }
  return {
    lines: [...groups.values()],
    scalars: scalarsAt(fields, n) as FieldDecl[],
    catalogue: hasCatalogue(fields, n) as boolean,
  };
}

/** Every field name a preview needs from /api/arrays (scalars ride along in the header). */
export function wantedAt(panels: Panels): string[] {
  return [...panels.lines.flatMap((p) => p.fields.map((f) => f.name)), ...panels.scalars.map((f) => f.name)];
}
