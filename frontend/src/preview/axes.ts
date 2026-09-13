// Plot geometry with no canvas in it, so it can be tested.

export interface Axis {
  unit: string;
  unit_display: string;
  n: number;
  lo: number;
  hi: number;
  width: number;
}

/** The value at the centre of each cell of a grid axis. */
export function centres(axis: Axis): Float64Array {
  const out = new Float64Array(axis.n);
  for (let i = 0; i < axis.n; i += 1) out[i] = axis.lo + (i + 0.5) * axis.width;
  return out;
}

/** Ticks at 1, 2 or 5 × 10^k, about `count` of them, covering [lo, hi]. */
export function linearTicks(lo: number, hi: number, count = 5): number[] {
  if (!(hi > lo)) return [lo];
  const span = hi - lo;
  const power = 10 ** Math.floor(Math.log10(span / count));
  // The nice step whose interval count is closest to the one asked for.
  const step = [1, 2, 5, 10]
    .map((m) => m * power)
    .reduce((best, s) => (Math.abs(span / s - count) < Math.abs(span / best - count) ? s : best));
  const out: number[] = [];
  // The tolerance is for -0.6 / 0.2 = -2.9999999999999996, which would skip -0.6.
  for (let k = Math.ceil(lo / step - 1e-9); k * step <= hi + step * 1e-9; k += 1) out.push(Number((k * step).toPrecision(12)));
  return out;
}

/** One tick per decade inside [lo, hi], both positive. */
export function logTicks(lo: number, hi: number): number[] {
  const out: number[] = [];
  for (let k = Math.ceil(Math.log10(lo) - 1e-9); k <= Math.floor(Math.log10(hi) + 1e-9); k += 1) out.push(10 ** k);
  return out;
}

export interface Range {
  lo: number;
  hi: number;
}

/**
 * The y range of a set of series: finite values only, and positive ones only on
 * a log axis. A flat series gets a small pad so it draws as a line, not nothing.
 * Linear ranges that come close to zero include it, so a profile is not
 * magnified into a trend.
 */
export function rangeOf(series: ArrayLike<number>[], log: boolean): Range | null {
  let lo = Infinity;
  let hi = -Infinity;
  for (const values of series) {
    for (let i = 0; i < values.length; i += 1) {
      const v = values[i];
      if (!Number.isFinite(v) || (log && v <= 0)) continue;
      if (v < lo) lo = v;
      if (v > hi) hi = v;
    }
  }
  if (lo === Infinity) return null;
  if (log) {
    const floor = Math.max(lo, hi * 1e-6); // six decades is as much as a panel can show
    return { lo: 10 ** Math.floor(Math.log10(floor)), hi: 10 ** Math.ceil(Math.log10(hi)) };
  }
  if (hi === lo) {
    const pad = Math.abs(lo) * 0.05 || 1;
    return { lo: lo - pad, hi: hi + pad };
  }
  if (lo > 0 && lo < (hi - lo) * 0.5) lo = 0;
  if (hi < 0 && -hi < (hi - lo) * 0.5) hi = 0;
  return { lo, hi };
}

/** Map a value into [0, 1] along a range, linear or log. */
export function position(value: number, range: Range, log: boolean): number {
  return log
    ? (Math.log10(value) - Math.log10(range.lo)) / (Math.log10(range.hi) - Math.log10(range.lo))
    : (value - range.lo) / (range.hi - range.lo);
}
