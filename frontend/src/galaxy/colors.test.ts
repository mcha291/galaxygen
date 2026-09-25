import { describe, expect, it } from "vitest";

import type { Columns, FieldsPayload } from "../api";
import { EXPOSED_LUMINOSITY, EXPOSED_RANK, REFERENCE_LUMINOSITY, exposureFor, photometricColors, srgbToLinear } from "./colors";

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

describe("exposureFor", () => {
  // Stars 1000, 999, … L☉ in a shuffled order, with a giant on top that must not set the exposure.
  const population = (n: number) => [10_000, ...Array.from({ length: n }, (_, i) => n - i)].sort(() => 0.5 - Math.random());

  it("exposes the EXPOSED_RANK-th brightest star as EXPOSED_LUMINOSITY, and lets the ones above it burn out", () => {
    // Ranks: the giant is 1st, 1000 L☉ is 2nd, so the 100th brightest is 902 L☉.
    expect(exposureFor(population(1000))).toBeCloseTo(Math.log2(EXPOSED_LUMINOSITY / (1000 - (EXPOSED_RANK - 2))), 9);
    expect(exposureFor([EXPOSED_LUMINOSITY])).toBe(0);
  });

  it("does not move when more, fainter stars are drawn", () => {
    const stars = population(1000);
    const more = [...stars, ...Array.from({ length: 4000 }, (_, i) => 1 / (i + 2))];
    expect(exposureFor(more)).toBeCloseTo(exposureFor(stars), 9);
  });

  it("rises as the whole population fades, as a closer view's does", () => {
    const stars = population(1000);
    expect(exposureFor(stars.map((L) => L / 100)) - exposureFor(stars)).toBeCloseTo(Math.log2(100), 9);
  });

  it("uses the faintest star drawn when fewer than EXPOSED_RANK are", () => {
    expect(exposureFor([EXPOSED_LUMINOSITY * 8, EXPOSED_LUMINOSITY * 4, EXPOSED_LUMINOSITY * 2])).toBeCloseTo(-1, 9);
  });

  it("ignores stars with no light and gives up nothing when none has any", () => {
    expect(exposureFor([Number.NaN, EXPOSED_LUMINOSITY / 2, Number.NaN])).toBeCloseTo(1, 9);
    expect(exposureFor([Number.NaN, 0])).toBe(0);
    expect(exposureFor([])).toBe(0);
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
