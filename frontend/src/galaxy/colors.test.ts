import { describe, expect, it } from "vitest";

import type { Columns, FieldsPayload } from "../api";
import { REFERENCE_LUMINOSITY, photometricColors, srgbToLinear } from "./colors";

// A two-stop stand-in for the published blackbody map: red at 2000 K, blue at 40000 K.
const META = {
  fields: [{ name: "star_temperature", ramp: { kind: "ramp", cmap: "blackbody", scale: "log", lo: 2000, hi: 40000 } }],
  cmaps: { blackbody: { stops: ["#ff0000", "#0000ff"], diverging: false } },
} as unknown as FieldsPayload;

describe("photometricColors", () => {
  const columns = {
    star_temperature: new Float64Array([2000, 40000, 2000, Number.NaN]),
    star_luminosity: new Float64Array([REFERENCE_LUMINOSITY, REFERENCE_LUMINOSITY, REFERENCE_LUMINOSITY * 1000, Number.NaN]),
  } as unknown as Columns;

  it("colours by temperature and scales by luminosity, unbounded above", () => {
    const rgb = photometricColors(META, columns, 0);
    expect(Array.from(rgb.slice(0, 3))).toEqual([1, 0, 0]); // the reference luminosity at unit intensity
    expect(Array.from(rgb.slice(3, 6))).toEqual([0, 0, 1]);
    expect(rgb[6]).toBeCloseTo(1000, 3); // a giant is not clipped: tone mapping happens on output
  });

  it("doubles per exposure stop", () => {
    expect(photometricColors(META, columns, 2)[0]).toBeCloseTo(4, 6);
  });

  it("gives a star with no light nothing to add", () => {
    expect(Array.from(photometricColors(META, columns, 0).slice(9, 12))).toEqual([0, 0, 0]);
  });
});

describe("srgbToLinear", () => {
  it("keeps the endpoints", () => {
    expect(srgbToLinear(0)).toBe(0);
    expect(srgbToLinear(1)).toBeCloseTo(1, 12);
  });

  it("darkens the middle: sRGB 0.5 is about 21% linear light", () => {
    expect(srgbToLinear(0.5)).toBeCloseTo(0.214, 3);
  });
});
