import { describe, expect, it } from "vitest";

import { pickMark, railOf, schematic } from "./rail";

const BOX = { x: 0, y: 0, width: 100, height: 20 };
const size = () => 4;

describe("schematic", () => {
  it("spaces planets evenly in order of distance, keeping their indices", () => {
    const r = schematic([5, 0.1, 1], [1, 1, 1], [], BOX, size);
    expect(r.marks.map((m) => [m.index, m.x])).toEqual([[1, 25], [2, 50], [0, 75]]);
    expect(r.ticks).toEqual([]);
  });

  it("puts a belt between the planets it lies between", () => {
    const r = schematic([1, 5], [1, 1], [{ kind: "asteroid", inner: 2, outer: 3 }], BOX, size);
    const [band] = r.bands;
    expect(band.x0).toBeGreaterThan(33.3);
    expect(band.x1).toBeLessThan(66.7);
    expect(band.x0).toBeLessThan(band.x1);
  });

  it("drops planets with no finite orbit", () => {
    expect(schematic([NaN, 2], [1, 1], [], BOX, size).marks.map((m) => m.index)).toEqual([1]);
  });
});

describe("railOf", () => {
  it("lays the log rail out with decade ticks", () => {
    const r = railOf("log", { planet_semi_major_axis: [0.1, 10], planet_radius: [1, 11] }, [], BOX, size)!;
    expect(r.ticks.map((t) => t.a)).toEqual([0.1, 1, 10]);
    expect(r.marks[0].x).toBeLessThan(r.marks[1].x);
  });
});

describe("pickMark", () => {
  it("finds the nearest mark within reach and nothing outside it", () => {
    const r = schematic([1, 2], [1, 1], [], BOX, size);
    expect(pickMark(r, 34, 10)).toBe(0);
    expect(pickMark(r, 66, 11)).toBe(1);
    expect(pickMark(r, 50, 10)).toBe(-1);
  });
});
