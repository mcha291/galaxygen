// Where a camera stands about the galaxy's centre, as numbers: the picture test's camera (T12, BUILD_III Phase 0)
// and, since S54, a template's (D213 ruling 5) - an inclination, an azimuth, a framing radius and a lens, turned
// into the scene's coordinates and back. Display plumbing only (rule D5): no physics, and no parameter of the
// picture that the orbit controls do not already reach by a drag, but the lens.

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

/** A camera with its lens: a template's (`/api/templates`), and what a capture states. */
export interface LensCamera extends CaptureCamera {
  /** The perspective camera's vertical field of view, degrees. */
  fov_deg: number;
}

/**
 * The viewer's lens where no template names one: a 45° vertical field of view, the constant every view had
 * until S54 and the one `milky_way` keeps (D213 ruling 5).
 */
export const DEFAULT_FOV = 45;

/**
 * The smallest inclination placed, radians. The orbit controls keep "up" along the disc's axis, which is
 * undefined looking straight down it, so face-on stands this far off (the preset stands 2e-6 off): a
 * hundredth of a pixel across a 1024 px picture, and the azimuth then says which way the picture is turned.
 */
export const MIN_INCLINATION = 1e-5;

const halfTan = (fovDegrees: number) => Math.tan((fovDegrees * Math.PI) / 360);

/** A lens the camera can have: a perspective's vertical field of view, strictly between 0° and 180°. */
export function isLens(fovDegrees: number): boolean {
  return Number.isFinite(fovDegrees) && fovDegrees > 0 && fovDegrees < 180;
}

/** The camera's distance from the centre for a framing radius, through a perspective camera's vertical field of view. */
export function distanceFor(radiusKpc: number, fovDegrees: number): number {
  return radiusKpc / halfTan(fovDegrees);
}

/**
 * How many times further a lens stands than the 45° one to frame the same radius: 1 at 45° exactly, 9.49 at
 * 5° (458 kpc for a 20 kpc radius against 48.3). Every distance the view holds that was written for the 45°
 * lens - the presets' stand, the zoom's range, the near and far planes - is multiplied by this, so a view is
 * the same number of kiloparsecs across whatever the lens.
 */
export function lensScale(fovDegrees: number): number {
  return fovDegrees === DEFAULT_FOV ? 1 : halfTan(DEFAULT_FOV) / halfTan(fovDegrees);
}

/**
 * Where the camera stands, in the scene's frame (positions.ts: the disc in x-z, y its axis, φ from +x
 * towards -z), looking at the centre.
 */
export function orbitPosition(view: CaptureCamera, fovDegrees: number): [number, number, number] {
  const { inclination_deg, azimuth_deg, radius_kpc } = view;
  if (![inclination_deg, azimuth_deg, radius_kpc].every(Number.isFinite) || !isLens(fovDegrees) || radius_kpc <= 0 || inclination_deg < 0 || inclination_deg > 180) {
    throw new Error(`capture camera: inclination ${inclination_deg}, azimuth ${azimuth_deg}, radius ${radius_kpc}, field of view ${fovDegrees}`);
  }
  const d = distanceFor(radius_kpc, fovDegrees);
  const i = Math.min(Math.PI - MIN_INCLINATION, Math.max(MIN_INCLINATION, (inclination_deg * Math.PI) / 180));
  const phi = (azimuth_deg * Math.PI) / 180;
  const h = d * Math.sin(i);
  return [h * Math.cos(phi), d * Math.cos(i), -h * Math.sin(phi)];
}

/**
 * The stand a camera has, read back from where it is and what it looks at: `orbitPosition`'s inverse. The
 * inclination of the line of sight from the disc's axis, the azimuth it stands over in [0, 360), and the
 * framing radius its lens gives at the target's distance. What a caption and a capture's record state.
 */
export function standOf(position: readonly number[], target: readonly number[], fovDegrees: number): LensCamera {
  const x = position[0] - target[0];
  const y = position[1] - target[1];
  const z = position[2] - target[2];
  const d = Math.hypot(x, y, z);
  // atan2, not acos of y / d: near face-on the cosine is flat and would lose the angle's last digits.
  const inclination = (Math.atan2(Math.hypot(x, z), y) * 180) / Math.PI;
  let azimuth = (Math.atan2(-z, x) * 180) / Math.PI;
  if (azimuth < 0) azimuth += 360;
  return { inclination_deg: inclination, azimuth_deg: azimuth >= 360 ? 0 : azimuth, radius_kpc: d * halfTan(fovDegrees), fov_deg: fovDegrees };
}
