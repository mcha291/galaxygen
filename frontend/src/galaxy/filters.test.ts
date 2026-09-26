import { url } from "@interface/transport.js";
import { describe, expect, it } from "vitest";

import { FILTER_SETS, FILTER_SET_NAMES, WHITE_KELVIN, bulgeLight, curvesOf, whiteOf } from "./filters";
import type { Curve } from "./filters";

// The line wavelengths the narrow sets are named for, Å in air (stages/spectra.py's LINE_WAVELENGTHS).
const HALPHA = 6562.8;
const OIII = 5006.8;
const SII = [6716.4, 6730.8];

const passes = (curve: Curve, lambda: number) => {
  if (curve.shape === "box") return Math.abs(lambda - curve.centre) <= curve.width / 2;
  if (curve.shape === "gaussian") return Math.abs(lambda - curve.centre) <= curve.fwhm / 2;
  return lambda >= curve.wavelength[0] && lambda <= curve.wavelength[curve.wavelength.length - 1];
};

describe("the filter sets", () => {
  it("offers RGB, SHO and HOO, three curves each, red to blue", () => {
    expect(FILTER_SET_NAMES).toEqual(["rgb", "sho", "hoo"]);
    for (const name of FILTER_SET_NAMES) expect(FILTER_SETS[name].curves).toHaveLength(3);
    const [r, v, b] = FILTER_SETS.rgb.curves;
    expect(r.shape === "gaussian" && v.shape === "gaussian" && b.shape === "gaussian").toBe(true);
    if (r.shape === "gaussian" && v.shape === "gaussian" && b.shape === "gaussian") {
      expect(r.centre).toBeGreaterThan(v.centre);
      expect(v.centre).toBeGreaterThan(b.centre);
    }
    expect(FILTER_SETS.rgb.curves.map((c) => c.name)).toEqual(["R", "V", "B"]); // the gate reads B and V
  });

  it("passes the lines each narrow set is named for, and no other", () => {
    const [s, h, o] = FILTER_SETS.sho.curves;
    for (const l of SII) expect(passes(s, l)).toBe(true);
    expect(passes(h, HALPHA)).toBe(true);
    expect(passes(o, OIII)).toBe(true);
    expect(passes(s, HALPHA) || passes(o, HALPHA) || passes(h, OIII)).toBe(false);
    const [hh, o1, o2] = FILTER_SETS.hoo.curves;
    expect(passes(hh, HALPHA) && passes(o1, OIII) && passes(o2, OIII)).toBe(true);
  });

  it("sends the curves as numbers, and the request carries them intact", () => {
    const curves = curvesOf("sho");
    expect(curves).toEqual(FILTER_SETS.sho.curves);
    curves[0].name = "changed";
    expect(FILTER_SETS.sho.curves[0].name).toBe("[S II]"); // a copy: the data stays the viewer's
    const sent = new URL(url("/api/render", { filters: JSON.stringify(curvesOf("rgb")), white: WHITE_KELVIN }, "http://x"));
    expect(JSON.parse(sent.searchParams.get("filters")!)).toEqual(FILTER_SETS.rgb.curves);
    expect(Number(sent.searchParams.get("white"))).toBe(WHITE_KELVIN);
  });
});

describe("the white point", () => {
  it("is the header's response per filter, or nothing when one is missing", () => {
    expect(whiteOf({ white: { response: [0.19, 0.12, 0.14] } })).toEqual([0.19, 0.12, 0.14]);
    expect(whiteOf({ white: null })).toBeNull();
    expect(whiteOf({})).toBeNull();
    expect(whiteOf({ white: { response: [0.19, null, 0.14] } })).toBeNull();
    expect(whiteOf({ white: { response: [0.19, 0, 0.14] } })).toBeNull();
  });

  it("puts the bulge through the same one step as the disc", () => {
    expect(bulgeLight([7.6e8, 3.7e8, 2.7e8], [0.19, 0.12, 0.14])).toEqual([7.6e8 / 0.19, 3.7e8 / 0.12, 2.7e8 / 0.14]);
    expect(bulgeLight(null, [0.19, 0.12, 0.14])).toEqual([0, 0, 0]);
    expect(bulgeLight([null, 1, Number.NaN], [1, 1, 1])).toEqual([0, 1, 0]);
  });

  it("makes white light white and keeps a response's colour otherwise", () => {
    const white = [0.1878, 0.1199, 0.1369];
    // A source whose responses are the white point's, times any light, draws equal in every channel.
    expect(bulgeLight(white.map((w) => 5 * w), white).map((v) => v.toFixed(9))).toEqual(["5.000000000", "5.000000000", "5.000000000"]);
    // A redder source keeps its ratio: the tone map divides every cell by the same three numbers.
    const [r, , b] = bulgeLight([0.3, 0.1, 0.05], white);
    expect(r / b).toBeCloseTo((0.3 / 0.05) * (0.1369 / 0.1878), 12);
  });
});
