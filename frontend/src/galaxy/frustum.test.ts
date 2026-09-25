import { Matrix4, PerspectiveCamera } from "three";
import { describe, expect, it } from "vitest";

import { footprint } from "./frustum";

// The Galaxy tab's camera: 45° across, square here, near and far as GalaxyView sets them for a 20 kpc reach.
function looking(from: [number, number, number], at: [number, number, number]): number[] {
  const camera = new PerspectiveCamera(45, 1, 0.02, 400);
  camera.position.set(...from);
  camera.lookAt(...at);
  camera.updateMatrixWorld();
  return new Matrix4().multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse).elements.slice();
}

describe("footprint", () => {
  it("looking straight down on the centre takes the whole azimuth out to the view's corners", () => {
    const window = footprint(looking([0, 20, 0.0001], [0, 0, 0]), 30);
    // Half-width at the lower slab plane, 23 kpc below the camera: 23 tan 22.5°, times √2 to the corner.
    const corner = 23 * Math.tan(Math.PI / 8) * Math.SQRT2;
    expect(window).not.toBeNull();
    expect(window!.r_min).toBe(0);
    expect(window!.phi_min).toBe(0);
    expect(window!.phi_max).toBeCloseTo(2 * Math.PI, 9);
    expect(window!.r_max).toBeGreaterThan(corner);
    expect(window!.r_max).toBeLessThan(corner * 1.2);
  });

  it("a close look at one spot is a window around it, not the galaxy", () => {
    // Above (x, z) = (0, −12), i.e. φ = π/2, 6 kpc up, looking down.
    const window = footprint(looking([0, 6, -12], [0, 0, -12]), 30)!;
    expect(window.r_min).toBeGreaterThan(6);
    expect(window.r_max).toBeLessThan(18);
    expect(window.phi_min).toBeLessThan(Math.PI / 2);
    expect(window.phi_max).toBeGreaterThan(Math.PI / 2);
    expect(window.phi_max - window.phi_min).toBeLessThan(Math.PI / 2);
  });

  it("a footprint across φ = 0 is asked for at every azimuth", () => {
    const window = footprint(looking([12, 6, 0], [12, 0, 0]), 30)!;
    expect(window.r_min).toBeGreaterThan(6);
    expect(window.phi_min).toBe(0);
    expect(window.phi_max).toBeCloseTo(2 * Math.PI, 9);
  });

  it("keeps the centre when the view holds it but no grid ray lands on it", () => {
    // Fully zoomed out and nudged off the centre by a zoom-to-cursor wheel: the grid's rays land
    // ~14 kpc apart, and the nearest to r = 0 was 7 kpc out, which cut the core out of the pool.
    for (const [x, z] of [[3.5, 2.1], [-6, 4], [1, -8]]) {
      const window = footprint(looking([x, 120, z + 0.0001], [x, 0, z]), 30)!;
      expect(window.r_min).toBe(0);
      expect(window.phi_max - window.phi_min).toBeCloseTo(2 * Math.PI, 9);
    }
  });

  it("finds the inner radius on the frustum's boundary, not on a grid ray", () => {
    // A close, off-centre look whose nearest point to the axis lies between grid rays.
    const window = footprint(looking([7, 5, 0.37], [7, 0, 0.37]), 30)!;
    const halfWidth = 8 * Math.tan(Math.PI / 8); // the far slab plane, 8 kpc below the camera
    expect(window.r_min).toBeGreaterThan(0);
    expect(window.r_min).toBeLessThanOrEqual(7 - halfWidth);
  });

  it("looking away from the disc sees nothing to ask for", () => {
    expect(footprint(looking([0, 200, 0.0001], [0, 400, 0]), 30)).toBeNull();
  });

  it("never asks past the galaxy's edge", () => {
    // Tilted, from far out: the far rays reach hundreds of kpc.
    const window = footprint(looking([0, 30, 50], [0, 0, 0]), 30)!;
    expect(window.r_max).toBeLessThanOrEqual(30);
  });
});
