import { describe, expect, it } from "vitest";

import { MIN_INCLINATION, distanceFor, orbitPosition } from "./capture";
import { toScene } from "./positions";
import { acrossOf } from "./zoom";

const FOV = 45;

describe("the capture camera (T12)", () => {
  it("frames the stated radius: half the picture's height at the centre is the radius", () => {
    const d = distanceFor(20, FOV);
    // zoom.ts's own width of the view, for a square picture: twice the radius.
    expect(acrossOf(d, FOV, 1)).toBeCloseTo(40, 12);
    expect(Math.hypot(...orbitPosition({ inclination_deg: 55, azimuth_deg: 30, radius_kpc: 20 }, FOV))).toBeCloseTo(d, 12);
  });

  it("stands at the stated inclination from the disc's axis", () => {
    for (const inclination of [10, 55, 90, 120]) {
      const [x, y, z] = orbitPosition({ inclination_deg: inclination, azimuth_deg: 77, radius_kpc: 12 }, FOV);
      const fromAxis = (Math.atan2(Math.hypot(x, z), y) * 180) / Math.PI;
      expect(fromAxis).toBeCloseTo(inclination, 9);
    }
  });

  it("stands over the model's azimuth: the same frame the stars are placed in", () => {
    for (const azimuth of [0, 45, 90, 200, 270]) {
      const [x, , z] = orbitPosition({ inclination_deg: 55, azimuth_deg: azimuth, radius_kpc: 20 }, FOV);
      const star = toScene([1], [(azimuth * Math.PI) / 180], [0]);
      const h = Math.hypot(x, z);
      expect(x / h).toBeCloseTo(star[0], 6);
      expect(z / h).toBeCloseTo(star[2], 6);
    }
  });

  it("face-on is a camera on the axis, turned by the azimuth: 270 is the app's preset", () => {
    const [x, y, z] = orbitPosition({ inclination_deg: 0, azimuth_deg: 270, radius_kpc: 20 }, FOV);
    const d = distanceFor(20, FOV);
    expect(y).toBeCloseTo(d, 6);
    // The preset stands at [0, d, +0.0001]: off the axis towards +z, so that "up" is defined.
    expect(z).toBeGreaterThan(0);
    expect(z).toBeCloseTo(d * Math.sin(MIN_INCLINATION), 12);
    expect(Math.abs(x)).toBeLessThan(1e-12);
    // Off the axis by less than a hundredth of a 1024 px picture's pixel.
    expect((d * Math.sin(MIN_INCLINATION)) / (40 / 1024)).toBeLessThan(0.02);
  });

  it("refuses a camera that is not one", () => {
    expect(() => orbitPosition({ inclination_deg: 55, azimuth_deg: 0, radius_kpc: 0 }, FOV)).toThrow(/capture camera/);
    expect(() => orbitPosition({ inclination_deg: -1, azimuth_deg: 0, radius_kpc: 20 }, FOV)).toThrow(/capture camera/);
    expect(() => orbitPosition({ inclination_deg: Number.NaN, azimuth_deg: 0, radius_kpc: 20 }, FOV)).toThrow(/capture camera/);
  });
});
