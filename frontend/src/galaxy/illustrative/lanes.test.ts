// The dust lanes (S107, BUILD_VIII row 107): the arm pieces' geometry against model/galaxy/layer/arm_pieces.py's
// convention, the map's determinism, where a lane sits beside its ridge, the bar's angle and sides, and the feature's
// registration. Illustrative: nothing here is a number of the model's but the locus convention.

import { describe, expect, it } from "vitest";

import { fieldFragment } from "../FieldVolume";
import type { IllFrame } from "./feature";
import { features, illArrays, illDefaults, illGlsl, illustrativeFragment, paramsOf } from "./index";
import { lanes, shapeOf } from "./lanes";
import { LANE_ARRAYS, LANE_MAP, type LaneGeometry, type LaneShape, type Piece, barAngle, barRidges, buildLaneMap, chainRidge, geometryOf, pieceLength, piecePoint, shapeAt } from "./lanesMap";

const DEG = Math.PI / 180;
const piece = (over: Partial<Piece>): Piece => ({ chain: 0, order: 0, r0: 4, phi0: 1, pitchDeg: 15, extent: 1.2, join: 0, ...over });

/** One plain strand and nothing else: no wander, no breaks, no branches, no bar. */
const PLAIN: LaneShape = {
  ...shapeOf(paramsOf(lanes, illDefaults(null))),
  offset: 150, width: 100, strands: 1, spread: 0, wiggle: 0, gaps: 0, clump: 0, envelope: 0, followGas: 0, taper: 0, innerRadius: 0, outerRadius: 30,
  featherSpacing: 0, fray: 0, barDepth: 0,
};
const geometry = (pieces: Piece[]): LaneGeometry => ({ rHi: 30, pieces, gas: null, bar: null });

describe("an arm piece's locus (arm_pieces.py Piece.reach / advance / ends, the model's turn +1)", () => {
  it("is ln R = ln r0 + t extent |tan pitch|, phi = phi0 + t extent: one piece worked by hand", () => {
    // r0 = 4 kpc, phi0 = 1 rad, pitch 15 degrees, extent 1.2 rad. tan 15 = 0.2679492.
    // Half way: ln(R / 4) = 0.6 x 0.2679492 = 0.1607695, R = 4 x 1.1744142 = 4.697657; phi = 1 + 0.6 = 1.6.
    const mid = piecePoint(piece({}), 0.5);
    expect(mid.r).toBeCloseTo(4.697657, 5);
    expect(mid.phi).toBeCloseTo(1.6, 12);
    // The outer end: ln(R / 4) = 1.2 x 0.2679492 = 0.3215390, R = 4 x 1.3792488 = 5.516995; phi = 2.2.
    const end = piecePoint(piece({}), 1);
    expect(end.r).toBeCloseTo(5.516995, 5);
    expect(end.phi).toBeCloseTo(2.2, 12);
    expect(piecePoint(piece({}), 0)).toEqual({ r: 4, phi: 1 });
    // Its length along the locus: (R1 - r0) / sin 15 = 1.516995 / 0.2588190 = 5.86122 kpc.
    expect(pieceLength(piece({}))).toBeCloseTo(5.86122, 4);
  });

  it("gains azimuth outward for a positive pitch (trailing: the disc turns the other way) and loses it for a negative one, the radius growing either way", () => {
    // Pitch -10 degrees: tan 10 = 0.1763270, ln(R / 4) = 1.2 x 0.1763270 = 0.2115924, R = 4 x 1.2356441 = 4.942576; phi = 1 - 1.2.
    const back = piecePoint(piece({ pitchDeg: -10 }), 1);
    expect(back.r).toBeCloseTo(4.942576, 5);
    expect(back.phi).toBeCloseTo(-0.2, 12);
    // A pitch of exactly nothing is an arc at its radius, its azimuth growing (advance takes tan >= 0 as positive).
    const arc = piecePoint(piece({ pitchDeg: 0 }), 1);
    expect(arc.r).toBe(4);
    expect(arc.phi).toBeCloseTo(2.2, 12);
    expect(pieceLength(piece({ pitchDeg: 0 }))).toBeCloseTo(4.8, 12);
  });

  it("joins a chain's pieces end to end, a measured piece of negative pitch taken from its high-azimuth end", () => {
    // The Milky Way template's chain 0: a trailing piece, then a measured piece of pitch -1 entered by its inner end,
    // which lies at the HIGH azimuth - its outer end is where the first piece ends.
    const first = piece({ r0: 3.57, phi0: 359 * DEG, pitchDeg: 19.5, extent: 36 * DEG });
    const end = piecePoint(first, 1);
    const second = piece({ order: 1, r0: end.r / Math.exp(13 * DEG * Math.tan(1 * DEG)), phi0: 48 * DEG, pitchDeg: -1, extent: 13 * DEG });
    const ridge = chainRidge([first, second], 0.02);
    let longest = 0;
    for (let i = 1; i < ridge.n; i += 1) longest = Math.max(longest, Math.hypot(ridge.x[i] - ridge.x[i - 1], ridge.y[i] - ridge.y[i - 1]));
    expect(longest).toBeLessThan(0.03); // no jump where the two meet
    const last = ridge.n - 1;
    expect(Math.hypot(ridge.x[last], ridge.y[last])).toBeCloseTo(second.r0, 9);
    expect(Math.atan2(ridge.y[last], ridge.x[last])).toBeCloseTo(48 * DEG, 9);
    expect(ridge.length).toBeCloseTo(pieceLength(first) + pieceLength(second), 2);
    // The normal points to the centre's side everywhere.
    for (let i = 0; i < ridge.n; i += 1) expect(ridge.nx[i] * ridge.x[i] + ridge.ny[i] * ridge.y[i]).toBeLessThan(0);
  });
});

describe("the lanes' map", () => {
  const one = piece({ r0: 6, phi0: 0, pitchDeg: 12, extent: 1.5 });

  it("is the same bytes for the same inputs, and another drawing for another seed", () => {
    const shape = { ...shapeOf(paramsOf(lanes, illDefaults("milky_way"))), barDepth: 0 };
    const a = buildLaneMap(geometry([one]), shape, 500, 900);
    const b = buildLaneMap(geometry([one]), { ...shape }, 500, 900);
    expect(a.drawn).toBe(true);
    expect(Buffer.from(a.data).equals(Buffer.from(b.data))).toBe(true);
    const c = buildLaneMap(geometry([one]), { ...shape, seed: shape.seed + 1 }, 500, 900);
    expect(Buffer.from(a.data).equals(Buffer.from(c.data))).toBe(false);
  });

  /** Along the radial cut at azimuth phi: the radius of the deepest texel and its shape. */
  const deepest = (map: ReturnType<typeof buildLaneMap>, phi: number) => {
    const j = Math.floor((phi / (2 * Math.PI)) * map.sectors);
    let best = 0;
    for (let i = 1; i < map.rings; i += 1) if (shapeAt(map, i, j) > shapeAt(map, best, j)) best = i;
    return { r: ((best + 0.5) * 30) / map.rings, shape: shapeAt(map, best, j), phi: ((j + 0.5) * 2 * Math.PI) / map.sectors };
  };

  it("puts a lane to the inner side of its ridge by the offset", () => {
    const cos = Math.cos(12 * DEG);
    for (const offset of [0, 150, 400]) {
      const map = buildLaneMap(geometry([one]), { ...PLAIN, offset });
      const cut = deepest(map, 0.75);
      // The ridge crosses this azimuth at r0 exp(phi tan pitch); a lane `offset` to its inner side, measured across
      // the lane, crosses the same radial line offset / cos(pitch) nearer the centre. One ring is 15 pc.
      const ridge = 6 * Math.exp(cut.phi * Math.tan(12 * DEG));
      expect(Math.abs(cut.r - (ridge - offset / 1000 / cos))).toBeLessThan(0.016);
      expect(cut.shape).toBeGreaterThan(0.9); // one full strand's centre holds a shape of 1
      expect(cut.shape).toBeLessThan(1.1);
    }
    // And to the outer side for an offset below nothing.
    const out = deepest(buildLaneMap(geometry([one]), { ...PLAIN, offset: -200 }), 0.75);
    expect(out.r).toBeGreaterThan(6 * Math.exp(out.phi * Math.tan(12 * DEG)) + 0.15);
  });

  it("draws a strand of the stated width, and nothing where there is no arm piece and no bar", () => {
    const map = buildLaneMap(geometry([one]), PLAIN);
    const j = Math.floor((0.75 / (2 * Math.PI)) * map.sectors);
    let above = 0;
    for (let i = 0; i < map.rings; i += 1) if (shapeAt(map, i, j) >= 0.5) above += 1;
    // 100 pc across the lane is 100 / cos(12 degrees) = 102 pc along the radial cut: seven rings of 15 pc, give or take one.
    expect(Math.abs(above * 15 - 102)).toBeLessThanOrEqual(15);
    expect(buildLaneMap(geometry([]), PLAIN, 200, 360).drawn).toBe(false);
  });
});

describe("the bar's lanes", () => {
  it("reads the bar's angle off the m = 2 phase of a pattern field", () => {
    const rings = 40;
    const sectors = 72;
    const field = new Float64Array(rings * sectors);
    for (let i = 0; i < rings; i += 1) for (let j = 0; j < sectors; j += 1) field[i * sectors + j] = 1 + 0.5 * Math.cos(2 * (((j + 0.5) * 2 * Math.PI) / sectors - 0.4));
    expect(barAngle(field, rings, sectors, 30, 5)).toBeCloseTo(0.4, 9);
    expect(barAngle(field, rings, sectors, 30, NaN)).toBeNaN();
    expect(barAngle(new Float64Array(rings * sectors).fill(1), rings, sectors, 30, 5)).toBeNaN();
  });

  it("lie on each half's leading side: the low-azimuth side of the half along the bar's angle, mirrored through the centre", () => {
    const [first, second] = barRidges({ halfLength: 5, axisRatio: 0.4, angle: 0 }, { ...PLAIN, barDepth: 1, barOffset: 0.4, barCurve: 2.5, barReach: 1 }, 0.02);
    // The disc turns toward decreasing azimuth (the arms trail), so the half along +x leads on its -y side.
    let checked = 0;
    for (let i = 0; i < first.n; i += 1) {
      if (first.x[i] > 1 && first.x[i] < 4.5) {
        expect(first.y[i]).toBeLessThan(0);
        expect(first.y[i]).toBeGreaterThan(-0.4 * 5 * 0.4 - 1e-9); // within the offset: 0.4 of the half-width (2 kpc)
        checked += 1;
      }
      expect(second.x[i]).toBeCloseTo(-first.x[i], 12);
      expect(second.y[i]).toBeCloseTo(-first.y[i], 12);
    }
    expect(checked).toBeGreaterThan(50);
    expect(Math.hypot(first.x[0], first.y[0])).toBeCloseTo(5, 9); // it begins at the bar's end
  });

  it("has no bar where the frame's bar scalars are null (a galaxy without one)", () => {
    const frame = { header: { scalars: { bar_half_length: null, bar_axis_ratio: null } }, arrays: {} } as unknown as IllFrame;
    const g = geometryOf(frame);
    expect(g.bar).toBeNull();
    expect(g.pieces).toEqual([]);
    expect(geometryOf(null).pieces).toEqual([]);
  });
});

describe("the lanes feature", () => {
  it("registers with every default inside its range, and names its arrays", () => {
    const feature = features().find((f) => f.id === "lanes");
    expect(feature).toBe(lanes);
    expect(lanes.controls.length).toBeGreaterThan(10);
    for (const c of lanes.controls) {
      for (const v of [c.default, ...Object.values(c.perTemplate ?? {})]) {
        expect(v, c.key).toBeGreaterThanOrEqual(c.min);
        expect(v, c.key).toBeLessThanOrEqual(c.max);
      }
      expect(c.about, c.key).toMatch(/Illustrative|appearance/);
    }
    expect(new Set(lanes.controls.map((c) => c.key)).size).toBe(lanes.controls.length);
    for (const name of LANE_ARRAYS) expect(illArrays()).toContain(name);
    expect(lanes.hooks).toEqual({ dustAv: "illLanesAv", veil: "illLanesVeil" });
  });

  it("takes part in the march through the dust hook and the veil, and reads a one-texel map until the arrays arrive", () => {
    expect(illGlsl()).toContain("float illLanesAv(vec2 rp)");
    expect(illGlsl()).toMatch(/vec3 illVeil\(vec2 rp\) \{ return .*illLanesVeil\(rp\)/);
    expect(illustrativeFragment(fieldFragment())).toContain("gl_FragColor = vec4(light * illVeil(screenRP) * gain, 1.0);");
    expect(fieldFragment()).not.toContain("illVeil"); // the physical look's fragment is untouched
    const values = lanes.uniforms!(paramsOf(lanes, illDefaults("milky_way")), { template: "milky_way", frame: null });
    const map = values.illLanesMap as { image: { width: number; height: number } };
    expect([map.image.width, map.image.height]).toEqual([1, 1]);
    expect(values.illLanesDepth).toBe(illDefaults("milky_way")["lanes.depth"]);
    expect(LANE_MAP.rings * LANE_MAP.sectors).toBeLessThanOrEqual(8 * 1024 * 1024); // a byte a texel: under 8 MiB
  });
});
