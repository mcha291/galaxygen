import { describe, expect, it } from "vitest";

import type { Axis } from "../preview/axes";
import { CHANNEL_EXTINCTION, farFieldImage, mixedSlab } from "./unresolved";

const R: Axis = { lo: 0, hi: 10, n: 10, width: 1 } as Axis;
const PHI: Axis = { lo: 0, hi: 2 * Math.PI, n: 4, width: Math.PI / 2 } as Axis;
const FLAT = new Float64Array(10).fill(100);
const WHITE = new Float64Array(30).fill(1);

/** The pixel nearest scene position (u, v) on a `size` image over ±R.hi. */
function pixel(img: Float32Array, size: number, u: number, v: number): number[] {
  const x = Math.floor(((u / R.hi) * size) / 2 + size / 2);
  const y = Math.floor(((v / R.hi) * size) / 2 + size / 2);
  const p = (y * size + x) * 4;
  return Array.from(img.slice(p, p + 4));
}

describe("farFieldImage", () => {
  it("draws surface brightness times gain in the radius's colour, and nothing off the grid", () => {
    const colour = new Float64Array(30);
    for (let i = 0; i < 10; i += 1) colour.set([1, 0.5, 0.25], 3 * i);
    const img = farFieldImage(FLAT, colour, R, 0.01, 64);
    const [r, g, b, a] = pixel(img, 64, 3, 2);
    expect(r).toBeCloseTo(1, 5);
    expect(g).toBeCloseTo(0.5, 5);
    expect(b).toBeCloseTo(0.25, 5);
    expect(a).toBe(1);
    expect(pixel(img, 64, 9.9, 9.9)).toEqual([0, 0, 0, 0]); // r > R.hi
  });

  it("leaves a radius with no number black rather than drawing it as zero light", () => {
    const colour = Float64Array.from(WHITE);
    colour.fill(Number.NaN, 0, 9); // cells 0-2
    const img = farFieldImage(FLAT, colour, R, 0.01, 64);
    expect(pixel(img, 64, 1, 0)[3]).toBe(0);
    expect(pixel(img, 64, 6, 0)[3]).toBe(1);
  });

  it("multiplies by the contrast at the pixel's own azimuth", () => {
    // Contrast 2 in the first quadrant sector (φ in [0, π/2)), 0 elsewhere, at every radius.
    const contrast = new Float64Array(10 * 4);
    for (let i = 0; i < 10; i += 1) contrast[i * 4] = 2;
    const img = farFieldImage(FLAT, WHITE, R, 0.01, 128, { values: contrast, phi: PHI });
    // φ = π/4 is the sector's centre: full contrast. φ = 5π/4 is in a zero sector.
    expect(pixel(img, 128, 4, 4)[0]).toBeCloseTo(2, 1);
    expect(pixel(img, 128, -4, -4)[0]).toBeCloseTo(0, 5);
  });

  it("dims and reddens where there is dust, and never adds light", () => {
    const clear = farFieldImage(FLAT, WHITE, R, 0.01, 64);
    const dusty = farFieldImage(FLAT, WHITE, R, 0.01, 64, undefined, new Float64Array(10).fill(2));
    const [r0, g0, b0] = pixel(clear, 64, 3, 2);
    const [r1, g1, b1] = pixel(dusty, 64, 3, 2);
    expect(r1).toBeLessThan(r0);
    expect(r1 / r0).toBeGreaterThan(g1 / g0);
    expect(g1 / g0).toBeGreaterThan(b1 / b0);
    expect(g1 / g0).toBeCloseTo(mixedSlab(2 * CHANNEL_EXTINCTION[1]), 5);
  });
});

describe("mixedSlab", () => {
  it("lets all the light out with no dust and half of it at an optical depth near 1.6", () => {
    expect(mixedSlab(0)).toBe(1);
    expect(mixedSlab(1.086 * 1.5936)).toBeCloseTo(0.5, 3);
    expect(mixedSlab(10)).toBeLessThan(0.11);
  });
});
