import { describe, expect, it } from "vitest";

import { polarImage } from "./polar";

const R = { unit: "kpc", unit_display: "kpc", n: 2, lo: 0, hi: 2, width: 1 };
const PHI = { unit: "rad", unit_display: "rad", n: 4, lo: 0, hi: 2 * Math.PI, width: Math.PI / 2 };
// Paint the value straight into the red channel.
const paint = { color: (v: number) => [v, 0, 0, 255] };

describe("polarImage", () => {
  it("multiplies the profile by the contrast of the pixel's own (R, φ) cell", () => {
    const profile = [10, 20];
    // contrast[i * n_phi + j]: ring 1 (R 1-2 kpc) is 2 in the first quadrant, 1 elsewhere.
    const contrast = [1, 1, 1, 1, 2, 1, 1, 1];
    const { data, width } = polarImage(profile, contrast, R, PHI, paint, 8);
    const at = (x: number, y: number) => data[(y * width + x) * 4];
    expect(at(7, 5)).toBe(40); // u ≈ +1.75, v ≈ +0.25: φ in the first quadrant, outer ring
    expect(at(0, 5)).toBe(20); // u ≈ −1.75: φ ≈ π, outer ring
    expect(at(4, 4)).toBe(10); // the middle: inner ring
  });

  it("leaves pixels off the grid transparent", () => {
    const { data, width } = polarImage([1, 1], new Array(8).fill(1), R, PHI, paint, 8);
    expect(data[(0 * width + 0) * 4 + 3]).toBe(0); // a corner is outside R.hi
  });
});
