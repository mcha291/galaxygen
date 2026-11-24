// S110 (A2): the sparkle's level table and its field stars (armsSparkle.ts).
import { describe, expect, it } from "vitest";
import { buildSparkle, fieldStars, tabulated, TABLE_RINGS, type SparkleShape } from "./armsSparkle";

const g = { nR: 40, nPhi: 36, rHi: 20 };
/** An arm map (RGBA, G the share) with one ridge (0.6) along phi cells 0-5. */
function armMap() {
  const map = new Float32Array(g.nR * g.nPhi * 4);
  for (let i = 4; i < 36; i++) for (let j = 0; j < 6; j++) map[(j * g.nR + i) * 4 + 1] = 0.6;
  return map;
}
const shape: SparkleShape = { count: 4000, clump: 0.3, groupPc: 100, members: 4, ridge: 1, slope: 1.4, range: 10, rMax: 20, heightPc: 60, direct: true };

describe("the sparkle's S110 level table and field stars", () => {
  it("reads a table that agrees with the function at its corners and between them, 0 past rMax", () => {
    const f = (r: number, phi: number) => Math.exp(-r / 5) * (1 + 0.5 * Math.cos(phi));
    const t = tabulated(f, 10);
    const dR = 10 / TABLE_RINGS;
    expect(t(10 * dR, 0)).toBeCloseTo(f(10 * dR, 0), 6);
    for (const [r, phi] of [[1.234, 0.5], [7.7, 3.1], [9.99, 6.2]]) expect(Math.abs(t(r, phi) - f(r, phi))).toBeLessThan(2e-3);
    expect(t(10.5, 1)).toBe(0);
    expect(t(3, -1)).toBeCloseTo(t(3, 2 * Math.PI - 1), 6);
  });

  it("draws the table's points on the same ridge, and the field stars after the arms' points, leaving those unchanged", () => {
    const map = armMap();
    const exact = buildSparkle(map, g, shape, 11);
    const table = buildSparkle(map, g, { ...shape, table: 1 }, 11);
    const onRidge = (s: { azimuth: Float32Array }) => Array.from(s.azimuth).filter((p) => p < (7 / 36) * 2 * Math.PI || p > (35 / 36) * 2 * Math.PI).length / s.azimuth.length;
    expect(table.radius.length).toBe(exact.radius.length);
    expect(onRidge(table)).toBeGreaterThan(0.9);
    const withField = buildSparkle(map, g, { ...shape, field: 1000, fieldScale: 4, fieldEdge: 16, fieldDim: 0.3 }, 11);
    const n = exact.radius.length;
    expect(withField.field).toBe(1000);
    expect(withField.radius.length).toBe(n + 1000);
    expect(Array.from(withField.radius.subarray(0, n))).toEqual(Array.from(exact.radius));
    expect(Array.from(withField.weight.subarray(0, n))).toEqual(Array.from(exact.weight));
    expect(exact.field).toBeUndefined();
  });

  it("lays the field stars over the whole disc inside its edge, dimmer, thinning outward", () => {
    const f = fieldStars(5000, { ...shape, fieldScale: 4, fieldEdge: 16, fieldDim: 0.3 }, 3);
    expect(f.radius.length).toBe(5000);
    expect(Math.max(...f.radius)).toBeLessThan(16);
    const inner = Array.from(f.radius).filter((r) => r < 4).length;
    const outer = Array.from(f.radius).filter((r) => r > 10).length;
    expect(inner).toBeGreaterThan(outer);
    expect(Math.max(...f.weight)).toBeLessThanOrEqual(0.3 * 10 + 1e-6);
    expect(Math.min(...f.weight)).toBeGreaterThanOrEqual(0.3 - 1e-6);
    // between the arms too: every quarter of the turn holds some
    for (let q = 0; q < 4; q++) expect(Array.from(f.azimuth).filter((p) => Math.floor(p / (Math.PI / 2)) === q).length).toBeGreaterThan(800);
  });
});
