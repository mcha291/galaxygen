import { describe, expect, it } from "vitest";

import { CLUSTER_SUMMARY, STAR_SUMMARY, summaryRows } from "./summary";

const meta = {
  fields: [
    { name: "bright_star_luminosity", label: "Luminosity", unit: "Lsun", unit_display: "L☉" },
    { name: "bright_star_temperature", label: "Effective temperature", unit: "K" },
    { name: "bright_star_phase", label: "Evolutionary phase", unit: "dimensionless", categories: ["main sequence", "giant", "AGB"] },
    { name: "bright_star_metallicity", label: "[Fe/H]", unit: "dimensionless" },
    { name: "bright_star_magnitude_v", label: "M_V", unit: "mag" },
  ],
};
const columns = {
  bright_star_luminosity: Float32Array.from([97756.27, 34000]),
  bright_star_temperature: Float32Array.from([4046.006, 3624.268]),
  bright_star_phase: Float32Array.from([2, 7]),
  bright_star_metallicity: Float32Array.from([-0.31, Number.NaN]),
  bright_star_magnitude_v: Float32Array.from([-5.12, -4.4]),
  undeclared_column: Float32Array.from([1, 2]),
};

describe("a picked point's summary (T23, D208)", () => {
  it("shows each declared column the object carries under its declared label, with its unit", () => {
    expect(summaryRows(meta, columns, 0, STAR_SUMMARY)).toEqual([
      { label: "Luminosity", value: "97760 L☉" },
      { label: "Effective temperature", value: "4046 K" },
      { label: "Evolutionary phase", value: "AGB" },
      { label: "[Fe/H]", value: "−0.31" }, // dimensionless: no unit
      { label: "M_V", value: "−5.12 mag" },
    ]);
  });

  it("says a missing number is missing, and a category outside the declaration too", () => {
    const rows = summaryRows(meta, columns, 1, STAR_SUMMARY);
    expect(rows.find((r) => r.label === "[Fe/H]")!.value).toBe("—");
    expect(rows.find((r) => r.label === "Evolutionary phase")!.value).toBe("—");
  });

  it("leaves out what the model does not declare or the object does not carry, and a row out of range", () => {
    expect(summaryRows(meta, columns, 0, ["undeclared_column", "bright_star_age"])).toEqual([]);
    expect(summaryRows(meta, columns, 5, STAR_SUMMARY)).toEqual([]);
    expect(summaryRows(meta, {}, 0, CLUSTER_SUMMARY)).toEqual([]);
  });

  it("asks for the bright catalogue's columns and the cluster census's by their published names", () => {
    expect(STAR_SUMMARY).toContain("bright_star_magnitude_k");
    expect(STAR_SUMMARY).toHaveLength(14);
    expect(CLUSTER_SUMMARY[0]).toBe("cluster_mass");
  });
});
