import { describe, expect, it } from "vitest";

import { RAD_PER_MYR_PER_KMS_PER_KPC, RING_STAGGER, interp, omegas, periodMyr, tracerPositions } from "./shear";

const R = [1, 2, 4, 8];
const FLAT = [220, 220, 220, 220];

describe("interp", () => {
  it("interpolates between grid points and clamps outside", () => {
    expect(interp(3, [2, 4], [100, 200])).toBe(150);
    expect(interp(0, R, [1, 2, 3, 4])).toBe(1);
    expect(interp(99, R, [1, 2, 3, 4])).toBe(4);
  });
});

describe("the unit conversion", () => {
  it("gives the Sun's orbit about 225 Myr at 220 km/s and 8 kpc", () => {
    expect(periodMyr(8, R, FLAT)).toBeCloseTo((2 * Math.PI) / ((220 / 8) * RAD_PER_MYR_PER_KMS_PER_KPC), 6);
    expect(periodMyr(8, R, FLAT)).toBeGreaterThan(220);
    expect(periodMyr(8, R, FLAT)).toBeLessThan(230);
  });
});

describe("omegas", () => {
  it("falls as 1/r for a flat curve: the inner disc turns faster", () => {
    const w = omegas([2, 4], R, FLAT);
    expect(w[0] / w[1]).toBeCloseTo(2, 9);
  });
});

describe("tracerPositions", () => {
  it("spaces each ring's tracers evenly, starting staggered from the ring inside", () => {
    const radii = [1, 2];
    const pos = tracerPositions(radii, [0, 0], 4, 0);
    expect(pos).toHaveLength(2 * 4 * 3);
    // ring 0, tracer 0 on +x; tracer 1 a quarter turn on, along −z
    [1, 0, 0].forEach((want, i) => expect(pos[i]).toBeCloseTo(want, 9));
    expect(pos[5]).toBeCloseTo(-1, 9);
    // ring 1 starts the golden angle round
    expect(Math.atan2(-pos[14], pos[12])).toBeCloseTo(RING_STAGGER, 6); // float32 positions
  });

  it("turns each ring rigidly at its own angular speed", () => {
    const radii = [2, 4];
    const w = omegas(radii, R, FLAT);
    const at0 = tracerPositions(radii, w, 3, 0);
    const at10 = tracerPositions(radii, w, 3, 10);
    const angle = (p: Float32Array, i: number) => Math.atan2(-p[i * 3 + 2], p[i * 3]);
    // wrapped into (−π, π]: the turns here are well under half an orbit
    const turned = (i: number) => ((((angle(at10, i) - angle(at0, i)) % (2 * Math.PI)) + 3 * Math.PI) % (2 * Math.PI)) - Math.PI;
    expect(turned(0)).toBeCloseTo(w[0] * 10, 5);
    expect(turned(1)).toBeCloseTo(w[0] * 10, 5); // same ring, same turn
    expect(turned(3)).toBeCloseTo(w[1] * 10, 5);
    expect(turned(0)).toBeGreaterThan(turned(3));
  });
});