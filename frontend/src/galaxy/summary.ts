// What a click on a star-first point opens (S50, D208, T23): the object's own published columns, each under
// its declared label and unit. A bright star is named by its cell and rank and has no planetary system yet
// (T27), so there is nothing to open but what the model says about it. Pure: no three.js, no React.

import type { Columns, FieldsPayload } from "../api";
import { formatNumber } from "../workflow/logic";

export interface SummaryRow {
  label: string;
  value: string;
}

/** The columns a bright star's summary shows, in order (the bright catalogue's, `/api/bright`). */
export const STAR_SUMMARY = [
  "bright_star_luminosity",
  "bright_star_temperature",
  "bright_star_phase",
  "bright_star_age",
  "bright_star_mass",
  "bright_star_metallicity",
  ...["u", "b", "v", "r", "i", "j", "h", "k"].map((band) => `bright_star_magnitude_${band}`),
] as const;

/** The columns a cluster's summary shows, in order (the cluster census's, `/api/clusters`). */
export const CLUSTER_SUMMARY = [
  "cluster_mass",
  "cluster_age",
  "cluster_luminosity",
  "cluster_light_temperature",
  "cluster_metallicity",
  "cluster_half_mass_radius",
  "cluster_bound",
  "cluster_ionizing_photons",
] as const;

/**
 * One object's rows: for each named column the object carries and the model declares, its declared label and
 * its value at `row` — a category by its declared name, a number at four figures with its declared unit
 * (no unit for a dimensionless one). A column the object lacks, or the model does not declare, is left out:
 * nothing is labelled by the viewer (rule A9).
 */
export function summaryRows(meta: Pick<FieldsPayload, "fields">, columns: Columns, row: number, names: readonly string[]): SummaryRow[] {
  const out: SummaryRow[] = [];
  for (const name of names) {
    const decl = meta.fields.find((f) => f.name === name);
    const column = columns[name];
    if (!decl || !column || row < 0 || row >= column.length) continue;
    const raw = Number(column[row]);
    const categories = decl.categories;
    if (categories && categories.length > 0) {
      out.push({ label: decl.label, value: Number.isInteger(raw) && raw >= 0 && raw < categories.length ? categories[raw] : "—" });
      continue;
    }
    const unit = String(decl.unit_display ?? decl.unit ?? "");
    const shown = formatNumber(raw, 4);
    out.push({ label: decl.label, value: unit && unit !== "dimensionless" && shown !== "—" ? `${shown} ${unit}` : shown });
  }
  return out;
}
