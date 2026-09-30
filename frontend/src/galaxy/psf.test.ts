import { describe, expect, it } from "vitest";

import { AIRY_FIRST_RING, airy, airyFirstZero, airyTexture, besselJ1, instrumentPsf, psfProfile } from "./psf";
import { FILTER_SETS } from "./filters";

describe("psfProfile", () => {
  it("is brightest at the centre and zero at the edge", () => {
    expect(psfProfile(0)).toBeCloseTo(1, 6);
    expect(psfProfile(1)).toBe(0);
  });

  it("falls monotonically, with wings wider than the core", () => {
    const samples = Array.from({ length: 21 }, (_, i) => psfProfile(i / 20));
    for (let i = 1; i < samples.length; i += 1) expect(samples[i]).toBeLessThanOrEqual(samples[i - 1]);
    const gaussOnly = (r: number) => Math.exp(-(r * r) / (2 * 0.3 ** 2)) * (1 - r) ** 2;
    expect(psfProfile(0.8)).toBeGreaterThan(gaussOnly(0.8)); // far out, the Moffat wing lifts it above a pure Gaussian
  });
});

describe("the named instrument's Airy sprite (S42)", () => {
  it("computes J1 as its power series does, and finds the Rayleigh zero at 1.22 pi", () => {
    const series = (x: number) => {
      let sum = 0;
      let term = x / 2; // m = 0: (x/2)^1 / (0! 1!)
      for (let m = 0; m < 40; m += 1) {
        sum += term;
        term *= -((x / 2) ** 2) / ((m + 1) * (m + 2));
      }
      return sum;
    };
    for (const x of [0.5, 2, 5, 10]) expect(besselJ1(x)).toBeCloseTo(series(x), 10);
    expect(airy(0)).toBe(1);
    expect(airyFirstZero() / Math.PI).toBeCloseTo(1.2197, 4);
    expect(airy(airyFirstZero())).toBeLessThan(1e-20);
    // The first bright ring: a local maximum a little under 2 % of the core, between the first two zeros.
    const ring = Math.max(...Array.from({ length: 200 }, (_, k) => airy(4 + (k * 3) / 200)));
    expect(ring).toBeGreaterThan(0.015);
    expect(ring).toBeLessThan(0.02);
  });

  it("draws each channel at its wavelength: the red ring outside the blue", () => {
    const size = 400;
    const t = airyTexture([8000, 5300, 4300], size);
    const px = (x: number, y: number) => Array.from((t.image.data as Float32Array).slice((y * size + x) * 4, (y * size + x) * 4 + 4));
    const centre = px(size / 2, size / 2);
    expect(centre[3]).toBeGreaterThan(0.95); // the pixel's centre is half a pixel off the pattern's
    // Along a row from the centre, each channel's first dark ring: the red's is outside the blue's by their
    // wavelengths' ratio, to a pixel.
    const firstDark = (k: number) => {
      let last = Infinity;
      for (let x = size / 2; x < size; x += 1) {
        const [r, g, b, a] = px(x, size / 2);
        const v = [r, g, b][k] * a;
        if (v > last) return x - 1 - size / 2 + 0.5;
        last = v;
      }
      return Number.NaN;
    };
    expect(firstDark(0) / (size / 2)).toBeCloseTo(AIRY_FIRST_RING, 1);
    expect(firstDark(0) / firstDark(2)).toBeCloseTo(8000 / 4300, 0);
    expect(firstDark(0)).toBeGreaterThan(firstDark(1));
    expect(firstDark(1)).toBeGreaterThan(firstDark(2));
    expect(px(0, 0)[3]).toBe(0); // outside the circle: nothing
  });

  it("belongs to the instrument sets only", () => {
    expect(instrumentPsf(FILTER_SETS.rgb)).toBeNull();
    expect(instrumentPsf(FILTER_SETS.sho)).toBeNull();
    const wfc3 = instrumentPsf(FILTER_SETS.wfc3);
    expect(wfc3?.size).toBe(25);
    expect(instrumentPsf(FILTER_SETS.wfc3)).toBe(wfc3); // one texture per set
  });
});
