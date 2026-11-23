// S106: the arms' crests traced into ridges (lanesMap.ts traceRidges).
import { describe, expect, it } from "vitest";
import { traceRidges, type TracePeak } from "./lanesMap";

const grid = { nR: 400, nPhi: 360, rHi: 30 };
const k = 3;

/** Two log-spiral arms' crests, ring by ring, as the ridge lines' peak finder would hand them. */
function spiralPeaks(): TracePeak[] {
  const out: TracePeak[] = [];
  for (let i = 40; i < 200; i++) {
    const R = (i + 0.5) * (grid.rHi / grid.nR);
    for (const phase of [0, Math.PI]) {
      const phi = (((phase + k * Math.log(R / 3)) % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);
      out.push({ i, j: Math.floor((phi / (2 * Math.PI)) * grid.nPhi), height: 0.8 });
    }
  }
  return out;
}

describe("traceRidges", () => {
  it("links two spiral arms' crests into two long ridges along them", () => {
    const ridges = traceRidges(spiralPeaks(), grid, k, 0.02);
    expect(ridges.length).toBe(2);
    for (const r of ridges) {
      expect(r.length).toBeGreaterThan(20);
      // Every point on its spiral: R and phi agree with phi = phase + k ln(R / 3) to within two cells.
      for (let q = 0; q < r.n; q += 50) {
        const R = Math.hypot(r.x[q], r.y[q]);
        const phi = Math.atan2(r.y[q], r.x[q]);
        const d0 = Math.cos(phi - k * Math.log(R / 3));
        expect(Math.abs(Math.abs(d0) - 1)).toBeLessThan(0.01);
      }
      // Even spacing (drawChain reads it).
      expect(Math.abs(r.s[1] - r.s[0] - 0.02)).toBeLessThan(1e-6);
    }
  });

  it("drops short tracks and weak peaks", () => {
    const peaks = spiralPeaks().filter((p) => p.i < 46);
    expect(traceRidges(peaks, grid, k, 0.02)).toHaveLength(0);
    expect(traceRidges(spiralPeaks().map((p) => ({ ...p, height: 0.05 })), grid, k, 0.02)).toHaveLength(0);
  });
});
