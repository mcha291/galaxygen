import { describe, expect, it } from "vitest";

import { TAU_PER_MAG, armNoise, balanced, clumpLattice, clumpNoise, clumpedLayer, planeTexture } from "./regimes";

// Two rings of a two-armed log spiral, A = 0.3: enough to check what the texture keeps per ring.
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
// What /api/render returns, in miniature: the stars per (R, φ, filter) already placed by the model's
// contrast, a ring colour of (30, 20, 10) L☉/pc² through the three filters; the line per (R, filter),
// all in the first filter; and the white point, each filter's response to a unit of white light.
const white = [0.2, 0.1, 0.05];
const stars = new Float64Array(R.n * phi.n * 3);
for (let i = 0; i < R.n; i += 1) {
  for (let j = 0; j < phi.n; j += 1) stars.set([30, 20, 10].map((v) => v * contrast[i * phi.n + j]), (i * phi.n + j) * 3);
}
const line = new Float64Array(R.n * 3);
for (let i = 0; i < R.n; i += 1) line.set([2, 0, 0], 3 * i);
const extinction = new Float64Array(R.n).fill(0.5);
const arms = { pitchDeg: 15, multiplicity: 2 };

const texture = planeTexture({ R, phi, stars, line, extinction, white, contrast, arms });

// Channels 0–2 are the light as drawn at a texel: the stars plus the midplane layer's line, clumps
// applied as the shader applies them; 3 is the dust.
type Texture = ReturnType<typeof planeTexture>;
const texel = (tex: Texture, i: number, j: number, channel: number) => {
  const drawn = clumpedLayer(tex, R, phi, i, j);
  if (channel === 3) return drawn[3];
  return tex.data[(j * R.n + i) * 4 + channel] + drawn[channel];
};
const meanOf = (tex: Texture, i: number, channel: number) => {
  let sum = 0;
  for (let j = 0; j < phi.n; j += 1) sum += texel(tex, i, j, channel);
  return sum / phi.n;
};
const ringMean = (i: number, channel: number) => meanOf(texture, i, channel);
// Float32 textures: compared to a relative tolerance, not a count of decimals.
const near = (got: number, want: number, rel = 1e-6) => expect(Math.abs(got - want) / Math.abs(want)).toBeLessThan(rel);
const ringContrast = (i: number) => {
  let sum = 0;
  for (let j = 0; j < phi.n; j += 1) sum += contrast[i * phi.n + j];
  return sum / phi.n;
};

describe("planeTexture", () => {
  it("draws each cell's published responses over the white point and nothing else", () => {
    for (const [i, j] of [[3, 0], [10, 47], [30, 179]]) {
      for (let k = 0; k < 3; k += 1) {
        const q = (j * R.n + i) * 4;
        near(texture.data[q + k], stars[(i * phi.n + j) * 3 + k] / white[k]);
        // The tone map's inverse: the texel times the white point is the model's response, as sent.
        near(texture.data[q + k] * white[k], stars[(i * phi.n + j) * 3 + k]);
      }
    }
  });

  it("keeps each ring's published light and line on average, in every channel", () => {
    for (const i of [10, 30]) {
      const c = ringContrast(i);
      near(ringMean(i, 0), (30 * c) / 0.2 + 2 / 0.2);
      near(ringMean(i, 1), (20 * c) / 0.1);
      near(ringMean(i, 2), (10 * c) / 0.05);
    }
  });

  it("keeps each ring's published values with the clumps on, and moves them with the seed", () => {
    const fields = { R, phi, stars, line, extinction, white, contrast, arms };
    const a = planeTexture({ ...fields, seed: 3 });
    const b = planeTexture({ ...fields, seed: 4 });

    for (const i of [10, 30]) {
      for (const channel of [0, 1, 2, 3]) {
        const want = ringMean(i, channel);
        expect(Math.abs(meanOf(a, i, channel) - want) / want).toBeLessThan(1e-5);
        expect(Math.abs(meanOf(b, i, channel) - want) / want).toBeLessThan(1e-5);
      }
    }
    const drawn = (tex: Texture) => [...Array(phi.n).keys()].map((j) => texel(tex, 30, j, 0));
    expect(drawn(a)).not.toEqual(drawn(texture));
    expect(drawn(a)).not.toEqual(drawn(b));
    expect(drawn(planeTexture({ ...fields, seed: 3 }))).toEqual(drawn(a));
  });

  it("does not clump or recolour the stars: only the line and the dust are placed by the viewer", () => {
    const a = planeTexture({ R, phi, stars, line, extinction, white, contrast, arms, seed: 3 });
    expect(Array.from(a.data)).toEqual(Array.from(texture.data));
    // The colour of the stars at a texel is the ring's published colour, in the arms and between them.
    const i = 20;
    const ratio = (j: number) => a.data[(j * R.n + i) * 4 + 2] / a.data[(j * R.n + i) * 4];
    for (const j of [0, 45, 90, 135]) near(ratio(j), (10 / 0.05) / (30 / 0.2));
  });

  it("gathers the line into knots: a few percent of a ring holds most of its Hα", () => {
    const knotted = planeTexture({ R, phi, stars, line, white, contrast, arms, seed: 3 });
    const i = 30;
    const values = [...Array(phi.n).keys()].map((j) => clumpedLayer(knotted, R, phi, i, j)[0]).sort((a, b) => b - a);
    const total = values.reduce((s, v) => s + v, 0);
    const top = values.slice(0, Math.ceil(0.1 * phi.n)).reduce((s, v) => s + v, 0);
    expect(total).toBeGreaterThan(0);
    expect(top / total).toBeGreaterThan(0.6);
  });

  it("keeps every ring's clump norms bounded, so no knot between texels can run away", () => {
    const tex = planeTexture({ R, phi, stars, line, extinction, white, contrast, arms, seed: 3 });
    for (let i = 0; i < R.n; i += 1) {
      for (let c = 0; c < 2; c += 1) {
        expect(Number.isFinite(tex.norms[4 * i + c])).toBe(true);
        expect(tex.norms[4 * i + c]).toBeLessThanOrEqual(4 + 1e-6);
      }
    }
  });

  it("draws the same noise a whole turn of φ later, at any point", () => {
    const l = clumpLattice(R, phi, 13.4, 5);
    for (const [radius, angle] of [[0.4, 0.1], [3.3, 1.7], [8, 4.2], [17.9, 6.2]]) {
      expect(clumpNoise(l, radius, angle + 2 * Math.PI)).toBeCloseTo(clumpNoise(l, radius, angle), 9);
    }
  });

  it("lays the clumps without a seam at φ = 0", () => {
    const noise = armNoise(R, phi, 15, 3);
    // Neighbouring cells across the wrap differ no more than neighbours elsewhere.
    let seam = 0;
    let inside = 0;
    for (let i = 5; i < R.n; i += 1) {
      seam = Math.max(seam, Math.abs(noise[i * phi.n] - noise[i * phi.n + phi.n - 1]));
      for (let j = 1; j < phi.n; j += 1) inside = Math.max(inside, Math.abs(noise[i * phi.n + j] - noise[i * phi.n + j - 1]));
    }
    expect(seam).toBeLessThanOrEqual(inside);
  });

  it("keeps each ring's published face-on dust", () => {
    for (const i of [10, 30]) expect(ringMean(i, 3)).toBeCloseTo(0.5 * TAU_PER_MAG, 6);
  });

  it("puts the dust lane on the inner side of the arm, not its ridge", () => {
    // At fixed azimuth, find an arm's ridge in radius; the dust just inside it is thicker than on it.
    const j = 0;
    const c = (i: number) => contrast[i * phi.n + j];
    const tau = (i: number) => texel(texture, i, j, 3);
    const ridge = [...Array(R.n - 6).keys()].map((k) => k + 5).find((i) => c(i) > c(i - 1) && c(i) >= c(i + 1));
    expect(ridge).toBeDefined();
    expect(Math.max(tau(ridge! - 1), tau(ridge! - 2))).toBeGreaterThan(tau(ridge!));
  });

  it("draws a missing response as nothing, never as a guess", () => {
    expect(balanced(Number.NaN, 0.2)).toBe(0);
    expect(balanced(-1, 0.2)).toBe(0);
    expect(balanced(3, 0.2)).toBeCloseTo(15, 12);
  });
});
