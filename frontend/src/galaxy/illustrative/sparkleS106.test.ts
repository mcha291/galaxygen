// S106: the sparkle's two sizes, its lift on weak ridges, its floor between the arms and its keeping off the lanes.
import { describe, expect, it } from "vitest";
import { buildSparkle, laneShapeAt, sparkleTiers, tierIndices, type SparkleShape } from "./armsSparkle";

const g = { nR: 40, nPhi: 36, rHi: 20 };
/** An arm map (RGBA, index (j nR + i) 4, G the share) with one weak ridge (0.3) along phi cells 0-5, nothing else. */
function maps() {
  const map = new Float32Array(g.nR * g.nPhi * 4);
  const raw = new Float32Array(g.nR * g.nPhi);
  for (let i = 4; i < 36; i++)
    for (let j = 0; j < 6; j++) {
      map[(j * g.nR + i) * 4 + 1] = 0.05;
      raw[j * g.nR + i] = 0.3;
    }
  return { map, raw };
}
const shape: SparkleShape = { count: 3000, clump: 0, groupPc: 100, members: 1, ridge: 1, slope: 1.4, range: 10, rMax: 20, heightPc: 60 };
const inArm = (phi: number) => phi < (7 / 36) * 2 * Math.PI || phi > (35 / 36) * 2 * Math.PI;

describe("the sparkle's S106 shaping (armsSparkle.ts)", () => {
  it("the bright tier holds the brightest share, and a share of 0 none", () => {
    const w = [1, 5, 2, 9, 3, 7, 4, 8, 6, 10];
    const t = sparkleTiers(w, 0.2);
    expect([...tierIndices(t, 1)]).toEqual([3, 9]);
    expect(tierIndices(sparkleTiers(w, 0), 1)).toHaveLength(0);
  });

  it("with a lift a weak ridge is as dense as a full one; without, as the S105 G", () => {
    const { map, raw } = maps();
    const plain = buildSparkle(map, g, shape, 7);
    const lifted = buildSparkle(map, g, { ...shape, lift: 0.3 }, 7, raw);
    expect(lifted.radius.length).toBe(3000);
    // The weak ridge's G of 0.05 rejects most proposals within the bounded tries; lifted, every one in the arm passes.
    expect(lifted.radius.length).toBeGreaterThanOrEqual(plain.radius.length);
    expect([...lifted.azimuth].every(inArm)).toBe(true);
    // Without the raw share the lift reads nothing new: the same points as S105's.
    expect(buildSparkle(map, g, { ...shape, lift: 0.3 }, 7)).toEqual(plain);
  });

  it("the floor puts points between the arms; the lanes keep them off", () => {
    const { map, raw } = maps();
    const floored = buildSparkle(map, g, { ...shape, lift: 0.3, floor: 0.2 }, 7, raw);
    expect([...floored.azimuth].some((p) => !inArm(p))).toBe(true);
    // A lane over the whole of the arm's cells 2-3 in phi (R channel byte 255: shape 4, capped at 1).
    const W = 200;
    const H = 360;
    const data = new Uint8Array(W * H * 4);
    for (let row = 20; row < 40; row++) for (let c = 0; c < W; c++) data[(row * W + c) * 4] = 255;
    const lanes = { data, width: W, height: H, rHi: 20 };
    expect(laneShapeAt(lanes, 10, (30 / 360) * 2 * Math.PI)).toBe(4);
    const kept = buildSparkle(map, g, { ...shape, lift: 0.3, avoid: 1 }, 7, raw, lanes);
    expect([...kept.azimuth].some((p) => p >= (20 / 360) * 2 * Math.PI && p < (40 / 360) * 2 * Math.PI)).toBe(false);
  });
});
