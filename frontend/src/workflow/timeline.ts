// The merger timeline's geometry: time across, mass ratio up on a log axis.
// Ratios run from Sagittarius's 0.02 to an equal-mass 1, and on a linear axis a
// minor merger is a bar too short to see or grab.

export const RATIO_FLOOR = 1e-3;

/** Bar height in [0, 1] for a mass ratio: log from RATIO_FLOOR to 1. */
export function heightOf(ratio: number): number {
  const r = Math.min(Math.max(ratio, RATIO_FLOOR), 1);
  return (Math.log10(r) - Math.log10(RATIO_FLOOR)) / -Math.log10(RATIO_FLOOR);
}

/** A pointer's fraction across the track to a time, clamped to [0, tMax] and rounded to 0.05 Gyr. */
export function timeAt(fraction: number, tMax: number): number {
  const t = Math.min(Math.max(fraction, 0), 1) * tMax;
  return Math.round(t * 20) / 20;
}
