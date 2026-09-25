// What part of the galaxy a camera can see, as the (R, φ) window the brightest-N mode asks the
// catalogue for. The frustum is a volume; the catalogue is materialised by cells in the plane; so
// the window is the in-plane footprint of the frustum cut by a slab about the midplane. The
// server then keeps only the stars inside the frustum itself (service.py `_brightest`).

import { Matrix4, Vector3, Vector4 } from "three";

import type { RegionWindow } from "./regimes";

/**
 * Half-thickness of the slab the frustum is cut by, kpc: the thin disc and most of the thick
 * disc. A halo star higher than this, seen by a camera looking past the disc's edge, can fall
 * outside the window and go unconsidered; a display choice for the window's size.
 */
export const SLAB_KPC = 3;
/**
 * Rays cast across the screen (a grid) and along its edges. The footprint's outer radius sits at
 * a corner, so a coarse grid finds it; its inner radius sits on the frustum's boundary, so the
 * edges are sampled finely. The one point neither can be trusted to find is the galaxy's centre,
 * which is tested against the frustum directly: fully zoomed out the grid's rays land 14 kpc apart,
 * and once a wheel zoom has nudged the orbit target off the centre none of them lands near
 * r = 0, so the innermost cells were never asked for and the core rendered as a hole.
 */
const GRID_RAYS = 9;
const EDGE_RAYS = 48;
/** The window's margin outside the hits, kpc and as a share of its size. */
const PAD_KPC = 0.25;
const PAD_SHARE = 0.05;
/** A footprint spanning more than this much azimuth is asked for whole. */
const FULL_TURN = 1.5 * Math.PI;

/**
 * The (R, φ) window holding every star inside the frustum of `viewProjection` (column-major,
 * the scene's x = R cos φ, y = height, z = −R sin φ) with |height| ≤ `slab`, out to `rMax`.
 * Null when the frustum meets no part of the slab: the camera is looking at empty sky.
 *
 * Rays through a grid of screen points and along the screen's edges are cut by the planes y = 0
 * and y = ±slab, and the near corners themselves count when they lie in the slab (the camera can
 * be inside the disc). The frustum ∩ slab is convex, so its nearest and farthest points from the
 * axis lie on its boundary, which the edge rays trace; the galaxy's centre is tested against the
 * frustum itself. Their (R, φ) hull, padded, covers the footprint. One that holds the centre, or
 * wraps past φ = 0, is asked for at every azimuth.
 */
export function footprint(viewProjection: ArrayLike<number>, rMax: number, slab = SLAB_KPC): RegionWindow | null {
  const forward = new Matrix4().fromArray(Array.from(viewProjection));
  const inverse = forward.clone().invert();
  const near = new Vector3();
  const far = new Vector3();
  const radii: number[] = [];
  const azimuths: number[] = [];
  const hit = (x: number, z: number) => {
    radii.push(Math.min(Math.hypot(x, z), rMax));
    let phi = Math.atan2(-z, x);
    if (phi < 0) phi += 2 * Math.PI;
    azimuths.push(phi);
  };
  const cast = (u: number, v: number) => {
    near.set(u, v, -1).applyMatrix4(inverse);
    far.set(u, v, 1).applyMatrix4(inverse);
    if (Math.abs(near.y) <= slab) hit(near.x, near.z);
    const dy = far.y - near.y;
    if (Math.abs(dy) < 1e-9) return;
    for (const h of [-slab, 0, slab]) {
      const t = (h - near.y) / dy;
      if (t < 0 || t > 1) continue;
      hit(near.x + t * (far.x - near.x), near.z + t * (far.z - near.z));
    }
  };
  for (let i = 0; i < GRID_RAYS; i += 1) {
    for (let j = 0; j < GRID_RAYS; j += 1) cast(-1 + (2 * i) / (GRID_RAYS - 1), -1 + (2 * j) / (GRID_RAYS - 1));
  }
  for (let k = 0; k < EDGE_RAYS; k += 1) {
    const s = -1 + (2 * k) / (EDGE_RAYS - 1);
    cast(s, -1);
    cast(s, 1);
    cast(-1, s);
    cast(1, s);
  }
  // The galaxy's centre, at each slab height: inside the frustum, the window starts at r = 0.
  const clip = new Vector4();
  let centreInView = false;
  for (const h of [-slab, 0, slab]) {
    clip.set(0, h, 0, 1).applyMatrix4(forward);
    if (clip.w > 0 && Math.abs(clip.x) <= clip.w && Math.abs(clip.y) <= clip.w && Math.abs(clip.z) <= clip.w) centreInView = true;
  }
  if (centreInView) radii.push(0);
  if (radii.length === 0) return null;

  let rLo = Infinity;
  let rHi = 0;
  for (const r of radii) {
    rLo = Math.min(rLo, r);
    rHi = Math.max(rHi, r);
  }
  const pad = PAD_KPC + PAD_SHARE * (rHi - rLo);
  const r_min = Math.max(0, rLo - pad);
  const r_max = Math.min(rMax, rHi + pad);
  const whole = { r_min, r_max, phi_min: 0, phi_max: 2 * Math.PI };
  if (r_min <= 0) return whole;

  // The smallest arc holding every azimuth: the complement of the largest gap between them.
  const sorted = [...azimuths].sort((a, b) => a - b);
  let gapStart = sorted[sorted.length - 1];
  let gap = sorted[0] + 2 * Math.PI - gapStart;
  for (let k = 1; k < sorted.length; k += 1) {
    if (sorted[k] - sorted[k - 1] > gap) {
      gap = sorted[k] - sorted[k - 1];
      gapStart = sorted[k - 1];
    }
  }
  const span = 2 * Math.PI - gap;
  if (span >= FULL_TURN) return whole;
  const dPhi = pad / r_min;
  let phi_min = gapStart + gap - dPhi;
  let phi_max = phi_min + span + 2 * dPhi;
  if (phi_min >= 2 * Math.PI) {
    phi_min -= 2 * Math.PI;
    phi_max -= 2 * Math.PI;
  }
  if (phi_min < 0 || phi_max > 2 * Math.PI) return whole;
  return { r_min, r_max, phi_min, phi_max };
}
