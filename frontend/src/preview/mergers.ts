// Checkpoint 2's playback, with no three.js in it so it can be tested.
//
// Checkpoint 2 has no stars and no matter history: those are checkpoint 3's. What
// it publishes is the response to whatever is present when a merger lands — the
// gas each event delivers, the σ_z matter forming at t will carry today, and the
// rms radial scatter matter born at (R, t) takes from the major mergers after it.
// The playback reads those at a cosmic time τ and applies the scatter to
// checkpoint 1's Σ(R) disc, used as a probe: what these mergers do to a disc
// like this one, not the disc as it was at τ.

import type { Axis } from "./axes";

/** The t cell holding τ, clamped to the grid. */
export function cellOf(tau: number, t: Axis): number {
  return Math.min(t.n - 1, Math.max(0, Math.floor((tau - t.lo) / t.width)));
}

/** A field over t read at τ: the value of the cell holding it. */
export function valueAt(field: ArrayLike<number>, tau: number, t: Axis): number {
  return field[cellOf(tau, t)];
}

/**
 * The rms radial scatter, per radius, that the mergers arrived by τ have given
 * matter present from the start.
 *
 * Read off the published field rather than recomputed: disc_radial_spread(R, t)
 * is the quadrature sum over the major mergers at or after birth time t, so the
 * events before τ are what the first cell carries less what matter born just
 * after τ still has to come. `spread` is row-major, spread[i * t.n + j].
 */
export function arrivedSpread(spread: ArrayLike<number>, nR: number, t: Axis, tau: number): Float64Array {
  const out = new Float64Array(nR);
  // The first cell whose centre lies after τ; past the grid, nothing is still to come.
  const after = Math.ceil((tau - t.lo) / t.width - 0.5);
  for (let i = 0; i < nR; i += 1) {
    const all = spread[i * t.n];
    const toCome = after < t.n ? spread[i * t.n + Math.max(0, after)] : 0;
    out[i] = Math.sqrt(Math.max(0, all * all - toCome * toCome));
  }
  return out;
}

/**
 * Move a surface density through a Gaussian in radius of rms `width[i]`,
 * conserving mass: the sfh stage's radial_transport for one time step, ported
 * so the probe disc goes through the model's own operator. Kernels are built on
 * ring masses and row-normalised, so what leaves a ring lands on the grid.
 */
export function radialTransport(profile: ArrayLike<number>, radii: ArrayLike<number>, dR: number, width: ArrayLike<number>): Float64Array {
  const n = profile.length;
  const out = new Float64Array(n);
  const mass = new Float64Array(n);
  for (let i = 0; i < n; i += 1) mass[i] = profile[i] * 2 * Math.PI * radii[i] * dR;
  const row = new Float64Array(n);
  for (let i = 0; i < n; i += 1) {
    if (!(width[i] > 0)) {
      out[i] += mass[i];
      continue;
    }
    const w = width[i];
    let sum = 0;
    for (let k = 0; k < n; k += 1) {
      const d = (radii[k] - radii[i]) / w;
      row[k] = Math.exp(-0.5 * d * d);
      sum += row[k];
    }
    for (let k = 0; k < n; k += 1) out[k] += (mass[i] * row[k]) / sum;
  }
  for (let i = 0; i < n; i += 1) out[i] /= 2 * Math.PI * radii[i] * dR;
  return out;
}

/** Share of the baryon budget delivered by τ: merger_delivery (per Gyr) summed over the cells before it. */
export function deliveredBy(delivery: ArrayLike<number>, t: Axis, tau: number): number {
  let total = 0;
  for (let j = 0; j < t.n; j += 1) {
    const start = t.lo + j * t.width;
    if (start >= tau) break;
    total += delivery[j] * Math.min(t.width, tau - start);
  }
  return total;
}

/**
 * Surface densities worth a ring: whole decades inside the profile's range, top
 * down, at most `count` of them. Log-spaced so an exponential disc gives evenly
 * spaced rings, and fixed values so a ring that moves is the matter moving.
 */
export function ringLevels(profile: ArrayLike<number>, count = 4): number[] {
  let lo = Infinity;
  let hi = 0;
  for (let i = 0; i < profile.length; i += 1) {
    const v = profile[i];
    if (!(v > 0) || !Number.isFinite(v)) continue;
    if (v < lo) lo = v;
    if (v > hi) hi = v;
  }
  const out: number[] = [];
  if (!(hi > 0)) return out;
  // Skip the top decade: its ring sits in the bright core where the eye cannot follow it.
  for (let e = Math.floor(Math.log10(hi)) - 1; out.length < count && 10 ** e >= lo; e -= 1) out.push(10 ** e);
  return out;
}

/**
 * The radius where the profile falls through `level`, interpolated between the
 * two cells that bracket it; the outermost crossing, so a bump does not draw a
 * ring inside a ring. Null when the profile never reaches the level.
 */
export function ringRadius(profile: ArrayLike<number>, radii: ArrayLike<number>, level: number): number | null {
  let found: number | null = null;
  for (let i = 0; i + 1 < profile.length; i += 1) {
    const a = profile[i];
    const b = profile[i + 1];
    if (!Number.isFinite(a) || !Number.isFinite(b) || (a - level) * (b - level) > 0 || a === b) continue;
    found = radii[i] + ((level - a) / (b - a)) * (radii[i + 1] - radii[i]);
  }
  return found;
}
/** Height in the tower for cosmic time τ: the floor is the grid's first moment, the top today, centred on 0. */
export function towerY(tau: number, t: Axis, height: number): number {
  return ((tau - t.lo) / (t.hi - t.lo) - 0.5) * height;
}

/** For each t cell, how many of the (sorted) merger times have landed by its centre. */
export function arrivalsPerCell(times: number[], t: Axis): Int32Array {
  const out = new Int32Array(t.n);
  let k = 0;
  for (let j = 0; j < t.n; j += 1) {
    const centre = t.lo + (j + 0.5) * t.width;
    while (k < times.length && times[k] <= centre) k += 1;
    out[j] = k;
  }
  return out;
}

/**
 * A ring's wall through time as a lathe profile: (radius, height) pairs, two per
 * t cell, so the wall stands straight through each cell and steps outward in a
 * flat annulus where a merger lands between two cells.
 */
export function wallProfile(radiusPerCell: ArrayLike<number>, t: Axis, height: number): Float64Array {
  const out = new Float64Array(t.n * 4);
  for (let j = 0; j < t.n; j += 1) {
    const r = radiusPerCell[j];
    out.set([r, towerY(t.lo + j * t.width, t, height), r, towerY(t.lo + (j + 1) * t.width, t, height)], j * 4);
  }
  return out;
}