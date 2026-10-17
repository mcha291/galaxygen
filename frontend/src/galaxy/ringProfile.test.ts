import { describe, expect, it } from "vitest";

import { hernquistWithin, partRings, pointRings, radiusIndex, renderRings, screenRings, spriteRings } from "./ringProfile";
import { psfMean, spriteTexels } from "./sprite";

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

  it("projects the march's Hernquist bulge: its share within R, against the density integrated through cylinders", () => {
    const a = 0.7;
    // rho(r) = a / (2 pi r (r + a)^3) of unit mass; its light within a cylinder of radius R, by shells.
    const within = (R: number) => {
      let m = 0;
      const dr = 1e-4;
      for (let r = dr / 2; r < 400; r += dr * (1 + r)) {
        const step = dr * (1 + r);
        const shell = (a / (2 * Math.PI * r * (r + a) ** 3)) * 4 * Math.PI * r * r * step;
        // A shell's share inside the cylinder: 1 - sqrt(1 - (R/r)^2) where r > R, all of it where r <= R.
        m += shell * (r <= R ? 1 : 1 - Math.sqrt(1 - (R / r) ** 2));
      }
      return m;
    };
    for (const R of [0.1, 0.7, 2, 8]) expect(hernquistWithin(R, a)).toBeCloseTo(within(R), 3);
    expect(hernquistWithin(a, a)).toBeCloseTo(1 / 3, 12);
    expect(hernquistWithin(a * (1 + 1e-3), a)).toBeCloseTo(1 / 3, 3);
    const got = renderRings({ lo: 0, width: 1, n: 2 }, 1, [0, 0], [1], [6], a);
    expect(got.bulgeRings[0][0] + got.bulgeRings[1][0]).toBeCloseTo(6 * hernquistWithin(2, a), 12);
  });

  it("sums an age part placed by its weight, and points by their ring with their squares and their edge light", () => {
    // One ring of two sectors: a part of 2 per pc^2 placed 1.5 and 0.5 round it, the white point 2.
    const got = partRings({ lo: 0, width: 1, n: 1 }, 2, [2, 2, 2], [1.5, 0.5], [2, 2, 2]);
    expect(got[0][0]).toBeCloseTo(Math.PI * 1e6, 6);
    const pts = pointRings([0.5, 0, 0, 0, 0, -1.95, 3, 0, 0], [1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 1, 2], 0.1);
    expect(pts.count).toEqual([1, 1]);
    expect(pts.light[1]).toEqual([4, 5, 6]);
    expect(pts.square[0]).toEqual([1, 4, 9]);
    expect(pts.nearEdge[1]).toEqual([4, 5, 6]); // 1.95 kpc: within 0.1 of the outer edge
    expect(pts.nearEdge[0]).toEqual([0, 0, 0]);
  });

  it("bins a point's sprite where its pixels' rays meet the plane: off the plane outward, near an edge on both sides", () => {
    const tanHalfY = Math.tan((22.5 * Math.PI) / 180);
    const d = 20 / tanHalfY;
    const cam = { eye: [0, d, 0] as const, forward: [0, -1, 0] as const, right: [1, 0, 0] as const, up: [0, 0, -1] as const, tanHalfY };
    const texels = spriteTexels(64);
    const mean = psfMean(64);
    const edges = [0, 10, 15, 15.5, 20];
    // In the plane at 12 kpc: all of its light in the 10-15 ring, to the sprite's sampled sum (within 1.5 %).
    const flat = spriteRings([12, 0, 0], [1, 1, 1], cam, 1024, 1024, 9, texels, 64, mean, edges);
    expect(flat[1][0]).toBeGreaterThan(0.985);
    expect(flat[1][0]).toBeLessThan(1.015);
    expect(flat[0][0] + flat[2][0] + flat[3][0]).toBe(0); // rings 0-10, 15-15.5, 15.5-20
    // 0.5 kpc above the plane at 15.42 kpc: its ray meets the plane at 15.42 d / (d - 0.5) = 15.58 kpc, 4 px out and past 15.5.
    const high = spriteRings([15.42, 0.5, 0], [1, 1, 1], cam, 1024, 1024, 9, texels, 64, mean, edges);
    const low = spriteRings([15.42, 0, 0], [1, 1, 1], cam, 1024, 1024, 9, texels, 64, mean, edges);
    expect(high[2][0]).toBeLessThan(low[2][0]); // 15-15.5 loses it
    expect(high[2][0] + high[3][0]).toBeGreaterThan(0.98 * (low[2][0] + low[3][0])); // the light kept
    expect(high[3][0]).toBeGreaterThan(0.5); // most of it past 15.5 kpc, where its ray meets the plane
  });

  it("finds a radius's ring by its edges", () => {
    expect(radiusIndex(0, [0, 1, 2])).toBe(0);
    expect(radiusIndex(1, [0, 1, 2])).toBe(1);
    expect(radiusIndex(2, [0, 1, 2])).toBe(-1);
    expect(radiusIndex(Number.NaN, [0, 1, 2])).toBe(-1);
  });
});
