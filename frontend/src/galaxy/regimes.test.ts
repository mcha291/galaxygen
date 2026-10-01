import { describe, expect, it } from "vitest";

import {
  MARCH_SCALE_HEIGHTS,
  RING_ROWS,
  SUB_SAMPLES_MAX,
  balanced,
  depthOf,
  layerShare,
  marchHalfHeight,
  phaseAt,
  planeTexture,
  subSamples,
  summed,
} from "./regimes";

// What /api/render returns since S39, in miniature: per (R, φ, filter) the stars, the HII regions' Hα and the
// scattered light, each already placed by the model's contrast; per (R, filter) the diffuse Hα, the dust's
// face-on transmission and its thermal emission; and the white point.
const R = { unit: "kpc", unit_display: "kpc", n: 40, lo: 0, hi: 20, width: 0.5 };
const phi = { unit: "rad", unit_display: "rad", n: 180, lo: 0, hi: 2 * Math.PI, width: (2 * Math.PI) / 180 };
const contrast = new Float64Array(R.n * phi.n);
for (let i = 0; i < R.n; i += 1) {
  const radius = R.lo + (i + 0.5) * R.width;
  for (let j = 0; j < phi.n; j += 1) {
    const angle = (j + 0.5) * phi.width;
    contrast[i * phi.n + j] = 1 + 0.3 * Math.cos(2 * (angle - Math.log(radius) / Math.tan((15 * Math.PI) / 180)));
  }
}
const white = [0.2, 0.1, 0.05];
const placed = (ring: number[]) => {
  const out = new Float64Array(R.n * phi.n * 3);
  for (let i = 0; i < R.n; i += 1) {
    for (let j = 0; j < phi.n; j += 1) out.set(ring.map((v) => v * contrast[i * phi.n + j]), (i * phi.n + j) * 3);
  }
  return out;
};
const perRing = (ring: (i: number) => number[]) => {
  const out = new Float64Array(R.n * 3);
  for (let i = 0; i < R.n; i += 1) out.set(ring(i), 3 * i);
  return out;
};
const stars = placed([30, 20, 10]);
const hii = placed([0, 2, 0]);
const scattered = placed([3, 2, 1.5]);
const dig = perRing(() => [0, 0.8, 0]);
// A_V of 0.5 through a curve with A_λ/A_V of 0.79, 1 and 1.30 (the grain table at R, V and B).
const extinction = perRing(() => [0.79, 1.0, 1.3].map((r) => 10 ** (-0.4 * 0.5 * r)));
const thermal = perRing((i) => [1e-40 * i, 0, 0]);
const texture = planeTexture({ R, phi, stars, hii, dig, extinction, scattered, thermal, white });

const near = (got: number, want: number, rel = 1e-6) => expect(Math.abs(got - want) / Math.abs(want)).toBeLessThan(rel);
const ring = (row: number, i: number, k: number) => texture.rings[(row * R.n + i) * 4 + k];

describe("planeTexture", () => {
  it("draws each cell's published responses over the white point and nothing else", () => {
    for (const [i, j] of [[3, 0], [10, 47], [30, 179]]) {
      const q = (j * R.n + i) * 4;
      for (let k = 0; k < 3; k += 1) {
        const at = (i * phi.n + j) * 3 + k;
        near(texture.data[q + k], stars[at] / white[k]);
        near(texture.data[q + k] * white[k], stars[at]); // the tone map's inverse is the model's response
        near(texture.scatter[q + k], scattered[at] / white[k]);
        if (hii[at] > 0) near(texture.hii[q + k], hii[at] / white[k]);
        else expect(texture.hii[q + k]).toBe(0);
      }
    }
  });

  it("places nothing: each ring's mean is the published mean, with no renormalisation", () => {
    for (const i of [10, 30]) {
      let sum = 0;
      let want = 0;
      for (let j = 0; j < phi.n; j += 1) {
        sum += texture.hii[(j * R.n + i) * 4 + 1];
        want += hii[(i * phi.n + j) * 3 + 1] / white[1];
      }
      near(sum / phi.n, want / phi.n);
    }
  });

  it("lays the per-ring components in their rows: the dust's depth, the diffuse line, the thermal light", () => {
    for (const i of [0, 17, 39]) {
      [0.79, 1.0, 1.3].forEach((r, k) => near(ring(RING_ROWS.depth, i, k), (0.4 * Math.LN10 * 0.5) * r, 1e-6));
      near(ring(RING_ROWS.dig, i, 1), 0.8 / 0.1);
      expect(ring(RING_ROWS.dig, i, 0)).toBe(0);
    }
    // Light too faint for a float32 texel is drawn as the float holds it, never raised to a guess.
    expect(ring(RING_ROWS.thermal, 20, 0)).toBe(Math.fround(1e-40 * 20 / 0.2));
    expect(texture.rings.length).toBe(R.n * RING_ROWS.count * 4);
  });

  it("dims blue more than red, as the grain table's curve does: occlusion, never an added colour", () => {
    expect(ring(RING_ROWS.depth, 5, 2)).toBeGreaterThan(ring(RING_ROWS.depth, 5, 1));
    expect(ring(RING_ROWS.depth, 5, 1)).toBeGreaterThan(ring(RING_ROWS.depth, 5, 0));
  });

  it("draws the components it is not given as nothing", () => {
    const bare = planeTexture({ R, phi, stars, white });
    expect(bare.hii.every((v) => v === 0) && bare.scatter.every((v) => v === 0) && bare.rings.every((v) => v === 0)).toBe(true);
  });
});

describe("the dust's depth", () => {
  it("is −ln of the transmission, and no dust or a missing number is no depth", () => {
    expect(depthOf(Math.exp(-2))).toBeCloseTo(2, 12);
    expect(depthOf(1)).toBe(0);
    expect(depthOf(Number.NaN)).toBe(0);
    expect(depthOf(0)).toBe(0);
    expect(depthOf(-0.5)).toBe(0);
  });
});

describe("the scattered light's phase factor", () => {
  // A table as the model publishes it: 21 points of |cos i| from edge-on to face-on.
  const table = Array.from({ length: 21 }, (_, k) => 1.5 - k / 20);

  it("reads the table at its points and linearly between them, at either face", () => {
    expect(phaseAt(table, 0)).toBeCloseTo(1.5, 12);
    expect(phaseAt(table, 1)).toBeCloseTo(0.5, 12);
    expect(phaseAt(table, 0.5)).toBeCloseTo(1.0, 12);
    expect(phaseAt(table, 0.525)).toBeCloseTo(0.975, 12);
    expect(phaseAt(table, -0.525)).toBeCloseTo(phaseAt(table, 0.525), 12);
    expect(phaseAt(table, 3)).toBeCloseTo(0.5, 12);
  });

  it("is isotropic without a table", () => {
    expect(phaseAt(null, 0.3)).toBe(1);
    expect(phaseAt([], 0.3)).toBe(1);
  });
});

describe("the layers", () => {
  it("give a ray the whole of a layer's column however it is stepped", () => {
    for (const h of [0.18, 0.36, 1.4]) {
      let steps = 0;
      const edges = Array.from({ length: 41 }, (_, k) => -40 + 2 * k);
      for (let k = 0; k < 40; k += 1) steps += layerShare(edges[k], edges[k + 1], h);
      expect(steps).toBeCloseTo(1, 6);
      expect(layerShare(-50, 50, h)).toBeCloseTo(1, 6);
      expect(layerShare(0, 50, h)).toBeCloseTo(0.5, 6);
    }
  });

  it("march tall enough for the thickest layer: sixteen of the diffuse gas's scale heights (D197)", () => {
    expect(marchHalfHeight({ stars: 0.36, dust: 0.36, halpha_hii: 0.18, halpha_dig: 1.4 }, 0.5)).toBeCloseTo(22.4, 12);
    expect(marchHalfHeight({ stars: 0.36, dust: 0.36 }, 0.1)).toBeCloseTo(5.76, 12);
    expect(marchHalfHeight({ stars: 0.36, dust: 0.36 }, 0.6)).toBeCloseTo(7.2, 12); // the bulge's twelve scale radii
    expect(marchHalfHeight({ stars: null, dust: null }, 0)).toBe(2);
  });

  it("put the box's top and bottom faces where the thickest layer's density is under 10⁻⁶ of its midplane's", () => {
    const sech2 = (x: number) => 1 / Math.cosh(x) ** 2;
    const h = 1.4;
    const y = marchHalfHeight({ stars: 0.36, dust: 0.36, halpha_dig: h }, 0.5);
    expect(sech2(y / (2 * h))).toBeLessThan(1e-6);
    expect(sech2((MARCH_SCALE_HEIGHTS - 2) / 2)).toBeGreaterThan(1e-6); // the smallest even multiple that meets it
    // The column a ray leaves above the faces: 10⁻⁷ of the layer's (ten heights left 4.5 × 10⁻⁵).
    expect(layerShare(y, 1e3, h)).toBeLessThan(2e-7);
    expect(layerShare(10 * h, 1e3, h)).toBeGreaterThan(4e-5);
  });
});

describe("the march's sub-samples along a step (D197)", () => {
  it("take the plane texture's radial cell from its width in cells", () => {
    expect(texture.cell).toBeCloseTo(0.5, 12);
    expect(texture.cell).toBeCloseTo((R.hi - R.lo) / texture.width, 12);
    expect(planeTexture({ R: { ...R, n: 400, lo: 0, hi: 30, width: 0.075 }, phi, stars: new Float64Array(400 * phi.n * 3), white }).cell).toBeCloseTo(0.075, 12);
  });

  it("read one per plane cell the step crosses in the plane, at least one and at most the cap", () => {
    expect(SUB_SAMPLES_MAX).toBe(8);
    expect(subSamples(0, 0.075)).toBe(1); // a face-on step: one read, as before
    expect(subSamples(0.05, 0.075)).toBe(1);
    expect(subSamples(0.075, 0.075)).toBe(1);
    expect(subSamples(0.076, 0.075)).toBe(2);
    expect(subSamples(0.3, 0.075)).toBe(4);
    expect(subSamples(0.6, 0.075)).toBe(8);
    expect(subSamples(5, 0.075)).toBe(SUB_SAMPLES_MAX); // a grazing step: capped
    expect(subSamples(5, 0.075, 3)).toBe(3);
    expect(subSamples(Number.NaN, 0.075)).toBe(1);
  });

  it("carry the step's exact column between them: the sub-steps' columns add to the step's, so nothing is added", () => {
    // A straight ray's height is monotonic along a step, so the differences of tanh telescope.
    for (const h of [0.18, 0.36, 1.4]) {
      for (const [y0, y1] of [[-0.4, 0.3], [0.05, 0.02], [2, -3], [-0.01, 0.01]]) {
        for (const n of [1, 2, 5, SUB_SAMPLES_MAX]) {
          let parts = 0;
          for (let j = 0; j < n; j += 1) parts += layerShare(y0 + ((y1 - y0) * j) / n, y0 + ((y1 - y0) * (j + 1)) / n, h);
          expect(parts).toBeCloseTo(layerShare(y0, y1, h), 12);
        }
      }
    }
  });
});

describe("balanced", () => {
  it("draws a missing response as nothing, never as a guess", () => {
    expect(balanced(Number.NaN, 0.2)).toBe(0);
    expect(balanced(-1, 0.2)).toBe(0);
    expect(balanced(3, 0.2)).toBeCloseTo(15, 12);
  });
});

describe("a layer's lines summed (S42)", () => {
  it("adds element by element, passes one through alone, and refuses two shapes", () => {
    expect(Array.from(summed([1, 2], new Float64Array([0.5, 0.25])) ?? [])).toEqual([1.5, 2.25]);
    const alone = [3, 4];
    expect(summed(alone, undefined)).toBe(alone);
    expect(summed(undefined, alone)).toBe(alone);
    expect(summed(undefined, undefined)).toBeUndefined();
    expect(() => summed([1], [1, 2])).toThrow();
  });
});
