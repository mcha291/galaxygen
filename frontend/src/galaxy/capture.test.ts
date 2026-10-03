import { describe, expect, it } from "vitest";

import { DEFAULT_FOV, MIN_INCLINATION, distanceFor, isLens, lensScale, orbitPosition, standOf } from "./capture";
import { toScene } from "./positions";
import { acrossOf } from "./zoom";

const FOV = 45;

describe("the camera's lens (S54, D213 ruling 5)", () => {
  it("the default is the 45° every view had, and scales nothing", () => {
    expect(DEFAULT_FOV).toBe(45);
    expect(lensScale(45)).toBe(1); // exactly: the presets and the zoom's range at 45° are the numbers they were
  });

  it("a 5° lens stands 9.49 times further for the same framing: 458 kpc for a 20 kpc radius", () => {
    expect(distanceFor(20, 45)).toBeCloseTo(48.284, 3);
    expect(distanceFor(20, 5)).toBeCloseTo(458.075, 3);
    expect(lensScale(5)).toBeCloseTo(distanceFor(20, 5) / distanceFor(20, 45), 12);
    expect(lensScale(5)).toBeCloseTo(9.487, 3);
    // And the width of the view is the same through either: twice the framing radius for a square picture.
    for (const fov of [5, 20, 45, 70]) expect(acrossOf(distanceFor(20, fov), fov, 1)).toBeCloseTo(40, 10);
  });

  it("at 5° the near side of a disc inclined 55° is magnified by under 4 % (D213), against 51 % at 45°", () => {
    // A point 20 kpc out on the near side stands 20 sin(i) closer to the camera than the centre.
    const magnified = (fov: number) => distanceFor(20, fov) / (distanceFor(20, fov) - 20 * Math.sin((55 * Math.PI) / 180));
    expect(magnified(5)).toBeLessThan(1.04);
    expect(magnified(5)).toBeCloseTo(1.037, 3);
    expect(magnified(45)).toBeCloseTo(1.514, 3);
  });

  it("orbitPosition stands at the lens's distance, in the same direction", () => {
    const view = { inclination_deg: 55, azimuth_deg: 0, radius_kpc: 20 };
    const wide = orbitPosition(view, 45);
    const long = orbitPosition(view, 5);
    expect(Math.hypot(...long)).toBeCloseTo(458.075, 3);
    for (let k = 0; k < 3; k += 1) expect(long[k] / Math.hypot(...long)).toBeCloseTo(wide[k] / Math.hypot(...wide), 12);
  });

  it("standOf reads a stand back: orbitPosition's inverse, lens and all", () => {
    for (const view of [
      { inclination_deg: 55, azimuth_deg: 0, radius_kpc: 20, fov_deg: 5 },
      { inclination_deg: 30, azimuth_deg: 200, radius_kpc: 12, fov_deg: 45 },
      { inclination_deg: 90, azimuth_deg: 359, radius_kpc: 3, fov_deg: 20 },
    ]) {
      const back = standOf(orbitPosition(view, view.fov_deg), [0, 0, 0], view.fov_deg);
      expect(back.inclination_deg).toBeCloseTo(view.inclination_deg, 9);
      expect(back.azimuth_deg).toBeCloseTo(view.azimuth_deg, 9);
      expect(back.radius_kpc).toBeCloseTo(view.radius_kpc, 9);
      expect(back.fov_deg).toBe(view.fov_deg);
    }
    // Face-on stands MIN_INCLINATION off the axis, and its azimuth is still the one asked for.
    const faceOn = standOf(orbitPosition({ inclination_deg: 0, azimuth_deg: 270, radius_kpc: 20 }, 45), [0, 0, 0], 45);
    expect(faceOn.inclination_deg).toBeCloseTo((MIN_INCLINATION * 180) / Math.PI, 9); // 0.0006°
    expect(faceOn.azimuth_deg).toBeCloseTo(270, 6);
    // About a target that is not the centre: the stand is the camera's offset from what it looks at.
    const panned = standOf([3, 10, 4], [3, 0, 4], 45);
    expect(panned.inclination_deg).toBeCloseTo(0, 9);
    expect(panned.radius_kpc).toBeCloseTo(10 * Math.tan(Math.PI / 8), 12);
  });

  it("a lens is a field of view strictly between 0° and 180°, and a camera without one is refused", () => {
    expect([5, 45, 179].every(isLens)).toBe(true);
    expect([0, -5, 180, Number.NaN, Number.POSITIVE_INFINITY].some(isLens)).toBe(false);
    expect(() => orbitPosition({ inclination_deg: 55, azimuth_deg: 0, radius_kpc: 20 }, 0)).toThrow(/field of view 0/);
    expect(() => orbitPosition({ inclination_deg: 55, azimuth_deg: 0, radius_kpc: 20 }, Number.NaN)).toThrow(/capture camera/);
  });
});

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
