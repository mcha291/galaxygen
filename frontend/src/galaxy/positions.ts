/**
 * Galactocentric (R, phi, z) in kpc and radians to three.js coordinates.
 *
 * three.js is y-up, so the disc lies in the x-z plane and a star's height above
 * the plane is y. phi is measured from +x towards -z, which is counter-clockwise
 * seen from +y: the face-on camera looking down -y sees the same handedness the
 * reference viewer draws (interface/stars.js, screen y flipped).
 */
export function toScene(
  radius: ArrayLike<number>,
  azimuth: ArrayLike<number>,
  height: ArrayLike<number>,
): Float32Array {
  const n = radius.length;
  if (azimuth.length !== n || height.length !== n) {
    throw new Error(`column lengths differ: R ${n}, phi ${azimuth.length}, z ${height.length}`);
  }
  const out = new Float32Array(n * 3);
  for (let i = 0; i < n; i += 1) {
    const r = radius[i];
    const phi = azimuth[i];
    out[3 * i] = r * Math.cos(phi);
    out[3 * i + 1] = height[i];
    out[3 * i + 2] = -r * Math.sin(phi);
  }
  return out;
}

/**
 * The in-plane radius enclosing a share of the points, for framing the camera.
 * A quantile rather than the maximum: the sample's outermost stars sit about
 * twice as far out as the 95th percentile, and framing on them shrinks the disc.
 */
export function extent(positions: Float32Array, share = 0.95): number {
  const n = positions.length / 3;
  if (n === 0) return 0;
  const radii = new Float32Array(n);
  for (let i = 0; i < n; i += 1) radii[i] = Math.hypot(positions[3 * i], positions[3 * i + 2]);
  radii.sort();
  return radii[Math.min(n - 1, Math.floor(share * (n - 1)))];
}
