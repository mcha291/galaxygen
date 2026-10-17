import { describe, expect, it } from "vitest";

import { radiusIndex, renderRings, screenRings } from "./ringProfile";

describe("the surface-brightness gate's two sides (S67, D227 R5)", () => {
  it("sums the render's stars round each ring over the white point, times the cells' area", () => {
    // Two rings of two sectors, two filters: 1 and 2 L_sun/pc^2 in the inner ring's cells, the white point 2 and 4.
    const stars = [2, 4, 2, 4, 6, 8, 6, 8];
    const got = renderRings({ lo: 0, width: 1, n: 2 }, 2, stars, [2, 4], [10, 20]);
    expect(got.edges).toEqual([0, 1, 2]);
    expect(got.light[0][0]).toBeCloseTo(Math.PI * 1e6, 6); // 1 per pc^2 over pi kpc^2
    expect(got.light[0][1]).toBeCloseTo(Math.PI * 1e6, 6);
    expect(got.light[1][0]).toBeCloseTo(3 * Math.PI * 3e6, 3);
    expect(got.light[0][2]).toBe(0);
    expect(got.bulge).toEqual([5, 5, 0]);
  });

  it("turns a face-on frame of a uniform disc back into its light, the lens's obliquity included", () => {
    // A camera 48.3 kpc over the centre (the Milky Way template's: 20 kpc framed through 45 degrees), looking down.
    const tanHalfY = Math.tan((22.5 * Math.PI) / 180);
    const d = 20 / tanHalfY;
    const cam = { eye: [0, d, 0] as const, forward: [0, -1, 0] as const, right: [1, 0, 0] as const, up: [0, 0, -1] as const, tanHalfY };
    const size = 400;
    const f = size / (2 * tanHalfY);
    // The march's value for a face-on surface brightness S seen at angle theta: S / cos(theta) (the column's slant).
    const S = 3;
    const pixels = new Float32Array(size * size * 4);
    for (let y = 0; y < size; y += 1) {
      for (let x = 0; x < size; x += 1) {
        const u = (x + 0.5 - size / 2) / f;
        const v = (y + 0.5 - size / 2) / f;
        const cos = 1 / Math.hypot(1, u, v);
        pixels.set([S / cos, S / cos, 0, 1], (y * size + x) * 4);
      }
    }
    const edges = [0, 5, 10, 15];
    const got = screenRings(pixels, size, size, cam, edges);
    for (let i = 0; i < 3; i += 1) {
      const area = Math.PI * (edges[i + 1] ** 2 - edges[i] ** 2) * 1e6;
      expect(got.rings[i][0] / (S * area)).toBeCloseTo(1, 2); // the pixels' squares against the ring's circles
    }
    expect(got.pixels[0]).toBeGreaterThan(0);
    expect(got.outside[0]).toBeGreaterThan(0); // the frame's corners lie past 15 kpc
  });

  it("finds a radius's ring by its edges", () => {
    expect(radiusIndex(0, [0, 1, 2])).toBe(0);
    expect(radiusIndex(1, [0, 1, 2])).toBe(1);
    expect(radiusIndex(2, [0, 1, 2])).toBe(-1);
    expect(radiusIndex(Number.NaN, [0, 1, 2])).toBe(-1);
  });
});
