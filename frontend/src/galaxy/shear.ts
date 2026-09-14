// Differential rotation, made visible. Tracer points ride rings of the disc, each
// ring orbiting at the circular speed its radius publishes, so the inner rings
// pull ahead of the outer ones.
//
// Only kinematics of a published field: angle = Ω(R) t with Ω = v_c(R) / R.
// Circular orbits, no dispersion, no pattern speed.

/** 1 km/s/kpc in radians per Myr: 1 km/s × 1 Myr / 1 kpc = 3.156e13 km / 3.0857e16 km. */
export const RAD_PER_MYR_PER_KMS_PER_KPC = 1.0227e-3;

/** Linear interpolation of v at r on a monotonic radius grid, clamped at the ends. */
export function interp(r: number, R: ArrayLike<number>, v: ArrayLike<number>): number {
  const n = R.length;
  if (r <= R[0]) return v[0];
  if (r >= R[n - 1]) return v[n - 1];
  let lo = 0;
  let hi = n - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (R[mid] <= r) lo = mid;
    else hi = mid;
  }
  const f = (r - R[lo]) / (R[hi] - R[lo]);
  return v[lo] + f * (v[hi] - v[lo]);
}

/** Angular speed Ω = v / r in rad per Myr at each of `radii`. */
export function omegas(radii: ArrayLike<number>, R: ArrayLike<number>, v: ArrayLike<number>): Float64Array {
  const out = new Float64Array(radii.length);
  for (let i = 0; i < radii.length; i += 1) {
    const r = radii[i];
    out[i] = r > 0 ? (interp(r, R, v) / r) * RAD_PER_MYR_PER_KMS_PER_KPC : 0;
  }
  return out;
}

/** Orbital period at radius r, Myr. */
export function periodMyr(r: number, R: ArrayLike<number>, v: ArrayLike<number>): number {
  const vr = interp(r, R, v);
  return vr > 0 && r > 0 ? (2 * Math.PI) / ((vr / r) * RAD_PER_MYR_PER_KMS_PER_KPC) : Infinity;
}

/** Start-angle stagger between rings, the golden angle, so the tracers never line up into spokes. */
export const RING_STAGGER = Math.PI * (3 - Math.sqrt(5));

/**
 * Scene positions of `perRing` tracer points on each ring at time t (Myr). Each
 * ring turns rigidly at its own Ω, so the rotation curve shows as rings sliding
 * past each other rather than as lines winding into a tangle. Same frame as the
 * stars: x = r cos φ, z = −r sin φ, at y = lift.
 */
export function tracerPositions(
  radii: ArrayLike<number>,
  omega: ArrayLike<number>,
  perRing: number,
  tMyr: number,
  lift = 0,
  out?: Float32Array,
): Float32Array {
  const size = radii.length * perRing * 3;
  const buffer = out && out.length === size ? out : new Float32Array(size);
  let p = 0;
  for (let i = 0; i < radii.length; i += 1) {
    const turned = i * RING_STAGGER + omega[i] * tMyr;
    for (let k = 0; k < perRing; k += 1) {
      const phi = turned + (2 * Math.PI * k) / perRing;
      buffer[p++] = radii[i] * Math.cos(phi);
      buffer[p++] = lift;
      buffer[p++] = -radii[i] * Math.sin(phi);
    }
  }
  return buffer;
}