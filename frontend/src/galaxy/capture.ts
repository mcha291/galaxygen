// The picture test's camera (T12, BUILD_III Phase 0): where a capture sees the galaxy from, as three
// numbers about the galaxy's centre, turned into the scene's coordinates. Display plumbing only (rule D5):
// no physics, and no parameter of the picture that the orbit controls do not already reach by a drag.

/** A capture's camera, about the galaxy's centre. */
export interface CaptureCamera {
  /** The angle between the line of sight and the disc's axis, degrees: 0 is face-on, 90 edge-on. */
  inclination_deg: number;
  /**
   * The galactocentric azimuth the galaxy is seen from, degrees, in the model's own φ (positions.ts): the
   * near side of an inclined disc is the side at this azimuth, drawn at the bottom of the picture. Face-on
   * it only turns the picture: the app's "face-on" preset is 270.
   */
  azimuth_deg: number;
  /** Half the picture's height at the centre's distance, kpc: the framing radius. */
  radius_kpc: number;
}

/**
 * The smallest inclination placed, radians. The orbit controls keep "up" along the disc's axis, which is
 * undefined looking straight down it, so face-on stands this far off (the preset stands 2e-6 off): a
 * hundredth of a pixel across a 1024 px picture, and the azimuth then says which way the picture is turned.
 */
export const MIN_INCLINATION = 1e-5;

/** The camera's distance from the centre for a framing radius, through a perspective camera's vertical field of view. */
export function distanceFor(radiusKpc: number, fovDegrees: number): number {
  return radiusKpc / Math.tan((fovDegrees * Math.PI) / 360);
}

/**
 * Where the camera stands, in the scene's frame (positions.ts: the disc in x-z, y its axis, φ from +x
 * towards -z), looking at the centre.
 */
export function orbitPosition(view: CaptureCamera, fovDegrees: number): [number, number, number] {
  const { inclination_deg, azimuth_deg, radius_kpc } = view;
  if (![inclination_deg, azimuth_deg, radius_kpc].every(Number.isFinite) || radius_kpc <= 0 || inclination_deg < 0 || inclination_deg > 180) {
    throw new Error(`capture camera: inclination ${inclination_deg}, azimuth ${azimuth_deg}, radius ${radius_kpc}`);
  }
  const d = distanceFor(radius_kpc, fovDegrees);
  const i = Math.min(Math.PI - MIN_INCLINATION, Math.max(MIN_INCLINATION, (inclination_deg * Math.PI) / 180));
  const phi = (azimuth_deg * Math.PI) / 180;
  const h = d * Math.sin(i);
  return [h * Math.cos(phi), d * Math.cos(i), -h * Math.sin(phi)];
}
