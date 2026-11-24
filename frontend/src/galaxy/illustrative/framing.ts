// The framing (S105, BUILD_VIII row 105): the template's stand puts the camera at radius_kpc (half the picture's height
// at the centre), which leaves the disc small in the frame beside the goal pictures. Under the illustrative look the
// stand's radius is multiplied by `scale`, its azimuth turned by `turn`, and the picture rolled by `roll` about the line
// of sight (the camera's up turned about it, so an inclined disc's long axis lies at that angle instead of level), and
// (S106) its inclination tilted by `tilt` (the sum held to [0, 89] degrees); the lens is the template's. Illustrative (D275): the physical look's stands are untouched.
//
// S108 (the roll through the orbit): the roll was the camera's up turned once, at the stand, and the orbit controls then
// orbited about that tilted up - so an orbit in azimuth swung the disc's long axis (NGC 4414: -25 degrees at azimuth 0,
// level at 90 and 270, +25 at 180). Now the camera's up stays the disc's axis (the controls orbit about it as under the
// physical look) and the roll is applied after every look-at (rollAfterLookAt): the camera turned about its own line of
// sight, so the picture keeps its angle from every azimuth. At the stand itself the orientation is the old one.

import type { Object3D } from "three";

import type { IllFeature, IllParams } from "./feature";

export const framing: IllFeature = {
  id: "framing",
  label: "framing",
  about: "The template stand under the illustrative look: its framing radius multiplied, its azimuth turned, the picture rolled.",
  controls: [
    {
      key: "scale", label: "framing", min: 0.3, max: 1.5, step: 0.01, unit: "×", default: 1,
      perTemplate: { milky_way: 0.77, ngc_4414: 0.45 },
      about: "A multiplier on the template camera's framing radius (half the picture's height at the centre): below 1 closer. Remakes the view's camera. Illustrative.",
    },
    {
      key: "roll", label: "roll", min: -180, max: 180, step: 1, unit: "°", default: 0, perTemplate: { milky_way: 15, ngc_4414: -25 },
      about: "The picture turned about the line of sight, degrees, counter-clockwise above 0: an inclined disc's long axis lies at this angle to the horizontal. Remakes the view's camera; held through any orbit, zoom or pan (the camera turned about its line of sight after each move). Illustrative.",
    },
    {
      key: "turn", label: "azimuth turn", min: -180, max: 180, step: 1, unit: "°", default: 0,
      about: "Added to the template camera's azimuth, degrees: which side of an inclined disc is near. Remakes the view's camera. Illustrative.",
    },
    {
      key: "tilt", label: "tilt", min: -45, max: 45, step: 0.5, unit: "°", default: 0, perTemplate: { ngc_4414: 6 },
      about: "Added to the template camera's inclination, degrees, the sum held to [0, 89]: above 0 the disc more edge-on (a narrower ellipse). Remakes the view's camera. Illustrative.",
    },
  ],
};

/** The tilt, degrees added to the stand's inclination (S106). */
export const standTilt = (p: IllParams): number => p.tilt ?? 0;
/** The stand's inclination under the tilt, degrees, held to [0, 89]. */
export const tiltedInclination = (inclinationDeg: number, tiltDeg: number): number => Math.min(89, Math.max(0, inclinationDeg + tiltDeg));

/** The stand's radius multiplier. */
export const standScale = (p: IllParams): number => p.scale ?? 1;
/** The picture's roll, degrees counter-clockwise. */
export const standRoll = (p: IllParams): number => p.roll ?? 0;
/** The azimuth's turn, degrees. */
export const standTurn = (p: IllParams): number => p.turn ?? 0;

/**
 * The camera's up vector (scene frame, y the disc's axis) for a camera at `position` looking at the origin with the
 * picture rolled `rollDeg` counter-clockwise: the disc's axis turned about the line of sight by -rollDeg (the camera's
 * up turned clockwise turns what it sees counter-clockwise). Rodrigues' rotation; [0, 1, 0] at no roll.
 */
export function rolledUp(position: readonly number[], rollDeg: number): [number, number, number] {
  // (S108: the old stand's up, kept as the reference the roll's test holds rollAfterLookAt to.)
  if (!rollDeg) return [0, 1, 0];
  const n = Math.hypot(position[0], position[1], position[2]);
  const k = [position[0] / n, position[1] / n, position[2] / n];
  const a = (-rollDeg * Math.PI) / 180;
  const cos = Math.cos(a);
  const sin = Math.sin(a);
  // v = (0, 1, 0): k x v = (-k_z, 0, k_x), k . v = k_y.
  const cross = [-k[2], 0, k[0]];
  const up = [0, 1, 0].map((v, i) => v * cos + cross[i] * sin + k[i] * k[1] * (1 - cos));
  const m = Math.hypot(up[0], up[1], up[2]);
  return [up[0] / m, up[1] / m, up[2] / m];
}

/**
 * (S108) The roll held through the orbit: `camera.lookAt` made the prototype's look-at followed by a turn of
 * `rollDeg` about the camera's own line of sight (counter-clockwise on screen above 0; rotateZ by -rollDeg, as
 * rolledUp turns the up). The camera's `up` is left as it is (the disc's axis), so the orbit controls - whose every
 * update ends in a look-at - orbit about the disc's axis and the picture keeps its roll at every azimuth. Returns the
 * undo. No roll: nothing changed.
 */
export function rollAfterLookAt(camera: Object3D, rollDeg: number): () => void {
  if (!rollDeg) return () => {};
  const own = Object.prototype.hasOwnProperty.call(camera, "lookAt") ? camera.lookAt : null;
  const base = camera.lookAt;
  const turn = (-rollDeg * Math.PI) / 180;
  const rolled = function (this: Object3D, ...args: Parameters<Object3D["lookAt"]>) {
    base.apply(this, args);
    this.rotateZ(turn);
  };
  camera.lookAt = rolled as Object3D["lookAt"];
  return () => {
    if (camera.lookAt !== rolled) return;
    if (own) camera.lookAt = own;
    else delete (camera as { lookAt?: unknown }).lookAt;
  };
}
