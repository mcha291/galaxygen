// The framing (S105, BUILD_VIII row 105): the template's stand puts the camera at radius_kpc (half the picture's height
// at the centre), which leaves the disc small in the frame beside the goal pictures. Under the illustrative look the
// stand's radius is multiplied by `scale`, its azimuth turned by `turn`, and the picture rolled by `roll` about the line
// of sight (the camera's up turned about it, so an inclined disc's long axis lies at that angle instead of level); the
// lens and the inclination are the template's. Illustrative (D275): the physical look's stands are untouched.

import type { IllFeature, IllParams } from "./feature";

export const framing: IllFeature = {
  id: "framing",
  label: "framing",
  about: "The template stand under the illustrative look: its framing radius multiplied, its azimuth turned, the picture rolled.",
  controls: [
    {
      key: "scale", label: "framing", min: 0.3, max: 1.5, step: 0.01, unit: "×", default: 1,
      perTemplate: { milky_way: 0.8, ngc_4414: 0.5 },
      about: "A multiplier on the template camera's framing radius (half the picture's height at the centre): below 1 closer. Remakes the view's camera. Illustrative.",
    },
    {
      key: "roll", label: "roll", min: -180, max: 180, step: 1, unit: "°", default: 0, perTemplate: { ngc_4414: -25 },
      about: "The picture turned about the line of sight, degrees, counter-clockwise above 0: an inclined disc's long axis lies at this angle to the horizontal. Remakes the view's camera; orbiting from there turns about the rolled axis. Illustrative.",
    },
    {
      key: "turn", label: "azimuth turn", min: -180, max: 180, step: 1, unit: "°", default: 0,
      about: "Added to the template camera's azimuth, degrees: which side of an inclined disc is near. Remakes the view's camera. Illustrative.",
    },
  ],
};

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
