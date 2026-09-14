// Surface-plot geometry with no three.js in it, so it can be tested.
//
// Checkpoints 1 and 2 publish radial profiles: Σ(R) and nothing more. Drawn as a
// face-on disc they are a 1D function sprayed across a 2D image, where the second
// axis carries no information and the resemblance to a galaxy is doing the
// talking. Drawn as a *surface* — height for the value, labelled axes, contour
// rings — the same function reads as what it is, and the height channel is free
// because a chart's vertical axis means whatever it is labelled, while a scene's
// means kiloparsecs above the midplane.
//
// The disc is still swept through φ here. That is honest in a chart: it is a
// surface of revolution of a radial profile, and the rings are what carry the
// scale length.

export interface HeightScale {
  lo: number;
  hi: number;
  log: boolean;
}

const DECADES_SHOWN = 4; // below this the surface is floor, as in axes.rangeOf

/**
 * The height scale for a profile. Log once it spans more than a decade, which an
 * exponential disc always does: linear height would give a spike at the centre
 * and a flat plain everywhere else. The cost is that height is then no longer
 * proportional to mass, which is why the axis has to carry its scale — see
 * `heightAxisLabel`.
 */
export function heightScaleOf(profile: ArrayLike<number>): HeightScale | null {
  let lo = Infinity;
  let hi = -Infinity;
  for (let i = 0; i < profile.length; i += 1) {
    const v = profile[i];
    if (!Number.isFinite(v)) continue;
    if (v < lo) lo = v;
    if (v > hi) hi = v;
  }
  if (!Number.isFinite(lo) || !Number.isFinite(hi) || hi <= 0) return null;
  const positive = hi > 0 && lo > 0;
  if (positive && hi / lo > 10) {
    const floor = Math.max(lo, hi * 10 ** -DECADES_SHOWN);
    return { lo: 10 ** Math.floor(Math.log10(floor)), hi: 10 ** Math.ceil(Math.log10(hi)), log: true };
  }
  if (hi === lo) return { lo: lo - (Math.abs(lo) * 0.05 || 1), hi: hi + (Math.abs(lo) * 0.05 || 1), log: false };
  return { lo: Math.min(lo, 0), hi, log: false };
}

/** Height in [0, 1]. Values under the floor sit on it rather than falling through. */
export function heightOf(value: number, scale: HeightScale): number {
  if (!Number.isFinite(value)) return 0;
  if (scale.log) {
    if (value <= scale.lo) return 0;
    return Math.min(1, Math.log10(value / scale.lo) / Math.log10(scale.hi / scale.lo));
  }
  return Math.max(0, Math.min(1, (value - scale.lo) / (scale.hi - scale.lo)));
}

/**
 * Contour levels. Log-spaced at a fixed factor per step, so an exponential disc
 * gives evenly spaced rings and the spacing *is* the scale length — which is the
 * whole reason to draw them. Linear contours would bunch at the centre and
 * vanish outside.
 */
export function contourLevels(scale: HeightScale, perDecade = 2): number[] {
  const out: number[] = [];
  if (scale.log) {
    const step = 1 / perDecade;
    const first = Math.ceil(Math.log10(scale.lo) / step - 1e-9) * step;
    for (let e = first; e <= Math.log10(scale.hi) + 1e-9; e += step) out.push(10 ** Number(e.toPrecision(12)));
    return out;
  }
  const span = scale.hi - scale.lo;
  const step = 10 ** Math.floor(Math.log10(span / 5));
  for (let v = Math.ceil(scale.lo / step) * step; v <= scale.hi + step * 1e-9; v += step) {
    if (v > scale.lo) out.push(Number(v.toPrecision(12)));
  }
  return out;
}

export interface Ring {
  level: number;
  radius: number;
}

/**
 * Where each contour level crosses the profile, innermost ring first, linearly
 * interpolated between the two cells that bracket it. Only the outermost
 * crossing of a given level is kept: a profile
 * that is not monotonic would otherwise give a level several rings, and a ring
 * inside a ring of the same value reads as noise rather than as structure.
 */
export function contourRings(profile: ArrayLike<number>, radii: ArrayLike<number>, levels: number[]): Ring[] {
  const out: Ring[] = [];
  for (const level of levels) {
    let found = -1;
    for (let i = 0; i + 1 < profile.length; i += 1) {
      const a = profile[i];
      const b = profile[i + 1];
      if (!Number.isFinite(a) || !Number.isFinite(b)) continue;
      if ((a - level) * (b - level) > 0) continue; // no crossing in this cell
      const t = a === b ? 0 : (level - a) / (b - a);
      found = radii[i] + t * (radii[i + 1] - radii[i]);
    }
    if (found >= 0) out.push({ level, radius: found });
  }
  // Innermost first: the drawing order, and the order the eye reads them in.
  return out.sort((a, b) => a.radius - b.radius);
}

export interface SurfaceMesh {
  positions: Float32Array;
  indices: Uint32Array;
  rings: number;
  spokes: number;
}

/**
 * A surface of revolution: the profile swept through φ, with height for the
 * value. x and y are kpc, z is the normalised height in [0, 1] — the caller
 * scales it, so the exaggeration is a display choice made in one place.
 */
export function polarSurface(
  profile: ArrayLike<number>,
  radii: ArrayLike<number>,
  scale: HeightScale,
  spokes = 96,
): SurfaceMesh {
  const rings = profile.length;
  const positions = new Float32Array(rings * spokes * 3);
  for (let i = 0; i < rings; i += 1) {
    const r = radii[i];
    const z = heightOf(profile[i], scale);
    for (let j = 0; j < spokes; j += 1) {
      const phi = (j / spokes) * Math.PI * 2;
      const k = (i * spokes + j) * 3;
      positions[k] = r * Math.cos(phi);
      positions[k + 1] = r * Math.sin(phi);
      positions[k + 2] = z;
    }
  }
  const indices = new Uint32Array((rings - 1) * spokes * 6);
  let n = 0;
  for (let i = 0; i + 1 < rings; i += 1) {
    for (let j = 0; j < spokes; j += 1) {
      const a = i * spokes + j;
      const b = i * spokes + ((j + 1) % spokes);
      const c = (i + 1) * spokes + j;
      const d = (i + 1) * spokes + ((j + 1) % spokes);
      indices[n++] = a; indices[n++] = c; indices[n++] = b;
      indices[n++] = b; indices[n++] = c; indices[n++] = d;
    }
  }
  return { positions, indices, rings, spokes };
}

/**
 * What the vertical axis is, said in full. A log height is not proportional to
 * the quantity, and a surface that does not say so is the misleading thing this
 * whole construction exists to avoid.
 */
export function heightAxisLabel(label: string, unitDisplay: string, scale: HeightScale): string {
  const unit = unitDisplay ? ` (${unitDisplay})` : "";
  return scale.log ? `log₁₀ ${label}${unit}` : `${label}${unit}`;
}
