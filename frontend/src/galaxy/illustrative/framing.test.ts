import { describe, expect, it } from "vitest";

import { PerspectiveCamera, Vector3 } from "three";
import { OrbitControls } from "three-stdlib";

import { orbitPosition } from "../capture";
import { framing, rollAfterLookAt, rolledUp, standTilt, tiltedInclination } from "./framing";
import { illDefaults } from "./index";

describe("the framing's tilt (S106)", () => {
  it("adds the tilt to the stand's inclination, held to [0, 89], 0 by default and 6 on NGC 4414", () => {
    expect(framing.controls.some((c) => c.key === "tilt")).toBe(true);
    expect(illDefaults("milky_way")["framing.tilt"]).toBe(0);
    expect(illDefaults("ngc_4414")["framing.tilt"]).toBe(6);
    expect(standTilt({})).toBe(0);
    expect(standTilt({ tilt: 6 })).toBe(6);
    expect(tiltedInclination(50, 6)).toBe(56);
    expect(tiltedInclination(50, 0)).toBe(50);
    expect(tiltedInclination(85, 10)).toBe(89);
    expect(tiltedInclination(5, -10)).toBe(0);
  });
});

describe("the roll held through the orbit (S108)", () => {
  // The disc's axis (scene y) projected on the screen: its angle counter-clockwise from the screen's up, degrees. The
  // physical look's camera (up the disc's axis) reads 0 at every azimuth.
  const axisAngle = (camera: PerspectiveCamera): number => {
    const local = new Vector3(0, 1, 0).applyQuaternion(camera.quaternion.clone().invert());
    return (Math.atan2(-local.x, local.y) * 180) / Math.PI;
  };
  const stand = (azimuth: number, inclination: number): [number, number, number] => orbitPosition({ inclination_deg: inclination, azimuth_deg: azimuth, radius_kpc: 20 }, 5);

  for (const [template, roll, inclination] of [["ngc_4414", -25, 61], ["milky_way", 25, 0.0005729578166155337]] as const) {
    it(`keeps ${template}'s roll of ${roll} degrees at every azimuth, and its stand's orientation as before`, () => {
      // Before S108: the up turned once (rolledUp) and the camera looked at the centre.
      const old = new PerspectiveCamera(5);
      old.position.set(...stand(270, inclination));
      old.up.set(...rolledUp(old.position.toArray(), roll));
      old.lookAt(0, 0, 0);
      const camera = new PerspectiveCamera(5);
      camera.position.set(...stand(270, inclination));
      camera.lookAt(0, 0, 0);
      const undo = rollAfterLookAt(camera, roll);
      const controls = new OrbitControls(camera);
      controls.update();
      expect(Math.abs(camera.quaternion.dot(old.quaternion))).toBeGreaterThan(1 - 1e-12);
      if (inclination > 1) expect(axisAngle(camera)).toBeCloseTo(roll, 9);
      // The orbit, as a drag in azimuth: about the disc's axis (the camera's height kept), the roll the same.
      controls.autoRotate = true;
      controls.autoRotateSpeed = 900; // a quarter turn per update
      const height = camera.position.y;
      for (let k = 0; k < 4; k += 1) {
        controls.update();
        expect(camera.position.y).toBeCloseTo(height, 9);
        if (inclination > 1) expect(axisAngle(camera)).toBeCloseTo(roll, 9);
      }
      controls.autoRotate = false;
      // And at other stands set by hand (the capture's place): rolled the same, still looking at the target.
      for (const az of [0, 45, 90, 180, 300]) {
        camera.position.set(...stand(az, inclination));
        controls.update();
        if (inclination > 1) expect(axisAngle(camera)).toBeCloseTo(roll, 9);
        const forward = new Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
        const toTarget = controls.target.clone().sub(camera.position).normalize();
        expect(forward.dot(toTarget)).toBeGreaterThan(1 - 1e-12);
      }
      // Still: a second update moves nothing (the march's motion check, T14; before S108 the Milky Way's stand drifted).
      for (let k = 0; k < 8; k += 1) controls.update(); // the spherical round trip's last ulp settled
      camera.updateMatrixWorld();
      const before = camera.matrixWorld.clone();
      for (let k = 0; k < 8; k += 1) controls.update();
      camera.updateMatrixWorld();
      expect(camera.matrixWorld.equals(before)).toBe(true);
      undo();
      camera.lookAt(0, 0, 0);
      if (inclination > 1) expect(axisAngle(camera)).toBeCloseTo(0, 9);
      controls.dispose();
    });
  }

  it("changes nothing without a roll", () => {
    const camera = new PerspectiveCamera(45);
    const before = camera.lookAt;
    rollAfterLookAt(camera, 0)();
    expect(camera.lookAt).toBe(before);
    expect(Object.prototype.hasOwnProperty.call(camera, "lookAt")).toBe(false);
  });
});
