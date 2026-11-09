import { describe, expect, it } from "vitest";

import type { Columns, FieldsPayload } from "../api";
import { EXPOSED_LUMINOSITY, EXPOSED_RANK, REFERENCE_LUMINOSITY, channelShare, exposureFor, lightColors, photometricColors, responseColors, srgbToLinear } from "./colors";
import { fluxOf } from "./flux";

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

describe("points through the filter set (S42, P6)", () => {
  // A miniature /api/blackbody table: three rows, three filters, and the white point's response.
  const table = {
    kelvin: [1000, 10000, 100000],
    share: [
      [1e-4, 1e-6, 1e-8],
      [0.1, 0.2, 0.3],
      [0.01, 0.02, 0.04],
    ],
    white: { kelvin: 10000, response: [0.1, 0.2, 0.3] },
  };

  it("is one at the white point, log-linear between rows, and clamped at the ends", () => {
    const share = channelShare(table)!;
    expect(share(10000)).toEqual([1, 1, 1]);
    // Halfway in log T between 1e4 and 1e5: the geometric mean of the rows, over the white.
    const [r, , b] = share(Math.sqrt(1e4 * 1e5));
    expect(r).toBeCloseTo(Math.sqrt(0.1 * 0.01) / 0.1, 12);
    expect(b).toBeCloseTo(Math.sqrt(0.3 * 0.04) / 0.3, 12);
    expect(share(1e6)).toEqual(share(1e5));
    expect(share(10)).toEqual(share(1000));
    expect(channelShare({ ...table, white: null })).toBeNull();
  });

  it("draws a star's light per channel through the table instead of the ramp", () => {
    const meta = { fields: [{ name: "star_temperature", ramp: { name: "blackbody" } }], cmaps: {} } as unknown as FieldsPayload;
    const columns = { star_temperature: [10000, 100000, 5000], star_luminosity: [100, 100, Number.NaN] };
    const out = photometricColors(meta, columns, 0, table);
    expect(Array.from(out.slice(0, 3))).toEqual([1, 1, 1]); // 100 Lsun at the white point, zero stops
    expect(out[3]).toBeCloseTo(0.1, 6); // a hotter star, a tenth of its light in the red filter
    expect(Array.from(out.slice(6, 9))).toEqual([0, 0, 0]); // no light, nothing drawn
  });
});

describe("a cluster's point through its own band light (S91, T2 / #114)", () => {
  // Three clusters' responses through a four-filter set (row-major, N x filters) and the white point's: the eighth
  // filter of a set beyond the display's three channels is carried and not drawn, as fluxOf reads it.
  const white = [0.5, 0.25, 0.125, 1];
  const response = new Float64Array([50, 25, 12.5, 9, 100, 10, 1, 9, Number.NaN, -1, 0, 9]);

  it("is the response over the white point per channel, on the display scale the sampled stars are drawn at", () => {
    const out = responseColors(response, white, 3, 0)!;
    // 100 Lsun through each channel over the white point's at zero stops: REFERENCE_LUMINOSITY, unit intensity.
    expect(Array.from(out.slice(0, 3))).toEqual([1, 1, 1]);
    // float32 light: equal to its float32 rounding
    [200, 40, 8].forEach((v, k) => expect(out[3 + k] * REFERENCE_LUMINOSITY).toBeCloseTo(v, 4));
    // a missing or negative number is no light (B9)
    expect(Array.from(out.slice(6, 9))).toEqual([0, 0, 0]);
  });

  it("divided by its gain is fluxOf exactly: the star-first points' reading, doubled per stop and times the point gain", () => {
    const flux = fluxOf(response, white, 3)!;
    for (const [stops, gain] of [[0, 1], [2, 1], [-1.5, 3]]) {
      const out = responseColors(response, white, 3, stops, gain)!;
      const scale = 2 ** stops / (REFERENCE_LUMINOSITY / gain);
      out.forEach((v, i) => expect(Math.abs(v / scale - flux[i])).toBeLessThanOrEqual(1e-6 * Math.abs(flux[i])));
    }
  });

  it("draws nothing on a guess: no response, no white point, or a response of the wrong length", () => {
    expect(responseColors(undefined, white, 3, 0)).toBeNull();
    expect(responseColors(response, null, 3, 0)).toBeNull();
    expect(responseColors(response, [0.5, 0, 0.125], 3, 0)).toBeNull();
    expect(responseColors(response, white, 4, 0)).toBeNull();
  });

  it("is not the blackbody share of the bolometric light: an old cluster's band light is not a blackbody's", () => {
    // One cluster of 100 Lsun at the white point's temperature: the ramp paints it (1, 1, 1) whatever its spectrum;
    // its own band light, here half the white point's response per Lsun in the blue, reads half there.
    const table = { kelvin: [1000, 10000, 100000], share: [[1e-4, 1e-6, 1e-8], [0.5, 0.25, 0.125], [0.01, 0.02, 0.04]], white: { kelvin: 10000, response: [0.5, 0.25, 0.125] } };
    const meta = { fields: [{ name: "cluster_light_temperature", ramp: { name: "blackbody" } }], cmaps: {} } as unknown as FieldsPayload;
    const columns = { cluster_light_temperature: [10000], cluster_luminosity: [100] } as unknown as Columns;
    const ramp = lightColors(meta, columns, 0, "cluster_light_temperature", "cluster_luminosity", table, 1);
    expect(Array.from(ramp)).toEqual([1, 1, 1]);
    const own = responseColors([50, 25, 6.25], [0.5, 0.25, 0.125], 1, 0)!;
    expect(Array.from(own)).toEqual([1, 1, 0.5]);
  });
});
