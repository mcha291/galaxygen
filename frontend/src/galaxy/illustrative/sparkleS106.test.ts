// S106: the sparkle's two sizes, its lift on weak ridges, its floor between the arms and its keeping off the lanes.
import { describe, expect, it } from "vitest";
import { buildSparkle, bunchNoise, laneShapeAt, sparkleTiers, tierIndices, type SparkleShape } from "./armsSparkle";

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

  it("bunching gathers the points where the noise is high, deterministically; 0 the even grain (S106 B5)", () => {
    const { map, raw } = maps();
    const plain = buildSparkle(map, g, { ...shape, lift: 0.3 }, 7, raw);
    expect(buildSparkle(map, g, { ...shape, lift: 0.3, bunch: 0, bunchBright: 0 }, 7, raw)).toEqual(plain);
    const s = { ...shape, lift: 0.3, bunch: 1, bunchPc: 500, bunchBright: 1 };
    const lumpy = buildSparkle(map, g, s, 7, raw);
    expect(buildSparkle(map, g, s, 7, raw)).toEqual(lumpy);
    const meanNoise = (sp: typeof plain) => {
      let t = 0;
      for (let i = 0; i < sp.radius.length; i++) t += bunchNoise((sp.radius[i] * Math.cos(sp.azimuth[i])) / 0.5, (sp.radius[i] * Math.sin(sp.azimuth[i])) / 0.5);
      return t / sp.radius.length;
    };
    expect(meanNoise(lumpy)).toBeGreaterThan(meanNoise(plain) + 0.05);
  });

  it("S110: the gaps empty the arm where the noise is below their level; 0 the S106 drawing bit for bit", () => {
    const { map, raw } = maps();
    const s = { ...shape, lift: 0.3, bunch: 1, bunchPc: 500, bunchBright: 1 };
    expect(buildSparkle(map, g, { ...s, gap: 0 }, 7, raw)).toEqual(buildSparkle(map, g, s, 7, raw));
    const gapped = buildSparkle(map, g, { ...s, gap: 0.5, gapSoft: 0.02 }, 7, raw);
    expect(buildSparkle(map, g, { ...s, gap: 0.5, gapSoft: 0.02 }, 7, raw)).toEqual(gapped);
    expect(gapped.radius.length).toBeGreaterThan(0);
    for (let i = 0; i < gapped.radius.length; i++) {
      const n = bunchNoise((gapped.radius[i] * Math.cos(gapped.azimuth[i])) / 0.5, (gapped.radius[i] * Math.sin(gapped.azimuth[i])) / 0.5);
      expect(n).toBeGreaterThan(0.48);
    }
  });
});

describe("the sparkle drawn through its density's envelope (S107, MW2: shape.direct)", () => {
  // A narrow log-spiral ridge (FWHM about 0.5 kpc) with a floor: most of the disc rejects the area-uniform proposals.
  const tan = Math.tan((14 * Math.PI) / 180);
  const levelOf = (r: number, phi: number) => {
    if (r < 2) return 0;
    const d = phi - Math.log(r) / tan;
    const w = Math.atan2(Math.sin(2 * d), Math.cos(2 * d)) / 2;
    const x = (r * w * Math.sin(Math.atan(tan))) / 0.21;
    return Math.exp(-0.5 * x * x);
  };
  const s: SparkleShape = { ...shape, count: 20000, clump: 0.3, members: 4, groupPc: 80, floor: 0.02, rMax: 16, bunch: 0.5, bunchPc: 400 };
  const { map } = maps();

  it("draws the same law as the rejection: the same share on the ridge and the same radial spread", () => {
    const a = buildSparkle(map, g, s, 11, null, null, levelOf);
    const b = buildSparkle(map, g, { ...s, direct: true }, 11, null, null, levelOf);
    expect(b.radius.length).toBe(a.radius.length);
    const onRidge = (p: { radius: Float32Array; azimuth: Float32Array }) => {
      let n = 0;
      for (let i = 0; i < p.radius.length; i++) if (levelOf(p.radius[i], p.azimuth[i]) > 0.5) n++;
      return n / p.radius.length;
    };
    expect(Math.abs(onRidge(a) - onRidge(b))).toBeLessThan(0.03);
    const mean = (v: Float32Array) => v.reduce((x, y) => x + y, 0) / v.length;
    expect(Math.abs(mean(a.radius) - mean(b.radius))).toBeLessThan(0.15);
    for (const q of [0.25, 0.5, 0.75]) {
      const at = (v: Float32Array) => Float32Array.from(v).sort()[Math.floor(q * v.length)];
      expect(Math.abs(at(a.radius) - at(b.radius))).toBeLessThan(0.25);
    }
  });

  it("is deterministic and faster", () => {
    const t0 = performance.now();
    const a = buildSparkle(map, g, s, 5, null, null, levelOf);
    const t1 = performance.now();
    const b = buildSparkle(map, g, { ...s, direct: true }, 5, null, null, levelOf);
    const t2 = performance.now();
    expect(buildSparkle(map, g, { ...s, direct: true }, 5, null, null, levelOf)).toEqual(b);
    expect(b.radius.length).toBe(a.radius.length);
    expect(t2 - t1).toBeLessThan(t1 - t0);
  });
});
