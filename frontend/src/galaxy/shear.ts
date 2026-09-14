// Differential rotation, made visible. A spoke starts as a straight radial line;
// every point on it then orbits at the circular speed its radius publishes, so
// the inner disc pulls ahead and the spoke winds into a trailing spiral.
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

/**
 * Scene positions of `spokes` spokes at time t (Myr), as line segments for
 * THREE.LineSegments: each spoke's consecutive points joined pairwise.
 * Same frame as the stars: x = r cos φ, z = −r sin φ, in the plane y = lift.
 */
export function spokeSegments(
  radii: ArrayLike<number>,
  omega: ArrayLike<number>,
  spokes: number,
  tMyr: number,
  lift = 0,
  out?: Float32Array,
): Float32Array {
  const n = radii.length;
  const size = spokes * (n - 1) * 2 * 3;
  const buffer = out && out.length === size ? out : new Float32Array(size);
  let p = 0;
  for (let s = 0; s < spokes; s += 1) {
    const start = (2 * Math.PI * s) / spokes;
    for (let i = 0; i < n - 1; i += 1) {
      for (const k of [i, i + 1]) {
        const phi = start + omega[k] * tMyr;
        buffer[p++] = radii[k] * Math.cos(phi);
        buffer[p++] = lift;
        buffer[p++] = -radii[k] * Math.sin(phi);
      }
    }
  }
  return buffer;
}
