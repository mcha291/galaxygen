// A field as an image, and nothing else.
//
// Three shapes are drawn, because three shapes are published: a profile over R,
// a 2-D field over two axes, and a series over t. Each is turned into pixels by
// the ramp it was declared with — this module never chooses a colour, it only
// decides which value a pixel reads.
//
// **Nearest, never averaged.** Resampling to the canvas takes the value of the
// cell a pixel lands in. Averaging neighbours would put numbers on the screen
// that the model did not compute, at a resolution it does not have; the grid's
// coarseness is a property of the model and the picture should show it.
//
// **The disc is a revolution, and says so.** Every published field is
// axisymmetric — nothing in the model has a phi dependence yet (debt #23) — so a
// face-on galaxy is a radial profile swept around. That is a drawing of the
// field, not an addition to it: no structure appears in the picture that is not
// in the array. When a stage finally publishes a non-axisymmetric density, this
// is the function that stops being enough.

/** The index of the grid cell a coordinate falls in, or -1 when it is off the axis. */
export function cellAt(value, axis) {
  if (!(value >= axis.lo) || !(value <= axis.hi)) return -1;
  const width = (axis.hi - axis.lo) / axis.n;
  return Math.min(axis.n - 1, Math.max(0, Math.floor((value - axis.lo) / width)));
}

/**
 * A 2-D field as an image: first axis down the picture, second across it.
 *
 * `flipRows` puts the first axis's zero at the bottom, which is what a radius
 * wants and what a depth does not; the caller knows which axis it has.
 */
export function imageOf2D(values, rows, cols, ramp, { maxWidth = 512, maxHeight = 512, flipRows = true } = {}) {
  const width = Math.max(1, Math.min(cols, maxWidth));
  const height = Math.max(1, Math.min(rows, maxHeight));
  const data = new Uint8ClampedArray(width * height * 4);
  for (let y = 0; y < height; y += 1) {
    const r = Math.min(rows - 1, Math.floor(((flipRows ? height - 1 - y : y) * rows) / height));
    for (let x = 0; x < width; x += 1) {
      const c = Math.min(cols - 1, Math.floor((x * cols) / width));
      const [red, green, blue, alpha] = ramp.color(values[r * cols + c]);
      const p = (y * width + x) * 4;
      data[p] = red;
      data[p + 1] = green;
      data[p + 2] = blue;
      data[p + 3] = alpha;
    }
  }
  return { data, width, height };
}

/**
 * A radial profile swept into a face-on disc.
 *
 * Pixels outside the grid's outer radius are transparent rather than black:
 * "no value here" and "a low value here" are different answers (rule B9).
 */
export function discOf(profile, axis, ramp, { size = 480, rMax = axis.hi } = {}) {
  const data = new Uint8ClampedArray(size * size * 4);
  const half = size / 2;
  for (let y = 0; y < size; y += 1) {
    const dy = ((y + 0.5 - half) / half) * rMax;
    for (let x = 0; x < size; x += 1) {
      const dx = ((x + 0.5 - half) / half) * rMax;
      const i = cellAt(Math.hypot(dx, dy), axis);
      const p = (y * size + x) * 4;
      if (i < 0) continue; // transparent: off the grid
      const [red, green, blue, alpha] = ramp.color(profile[i]);
      data[p] = red;
      data[p + 1] = green;
      data[p + 2] = blue;
      data[p + 3] = alpha;
    }
  }
  return { data, width: size, height: size };
}

/** Screen radius of a galactocentric radius, for anything drawn over a disc. */
export function discScale(size, rMax) {
  return { half: size / 2, perKpc: size / 2 / rMax, rMax };
}

/**
 * A 1-D field as a polyline in a box, plus the bounds it was drawn against.
 *
 * Non-finite entries break the line rather than joining across them: a gap is
 * what a missing number looks like (rule B9).
 */
export function polylineOf(values, box, { lo = null, hi = null } = {}) {
  let min = lo;
  let max = hi;
  if (min === null || max === null) {
    min = Infinity;
    max = -Infinity;
    for (let i = 0; i < values.length; i += 1) {
      const v = Number(values[i]);
      if (!Number.isFinite(v)) continue;
      if (v < min) min = v;
      if (v > max) max = v;
    }
    if (!Number.isFinite(min)) return { segments: [], lo: null, hi: null };
  }
  if (!(max > min)) max = min + (Math.abs(min) || 1) * 1e-6;

  const segments = [];
  let run = [];
  for (let i = 0; i < values.length; i += 1) {
    const v = Number(values[i]);
    if (!Number.isFinite(v)) {
      if (run.length) segments.push(run);
      run = [];
      continue;
    }
    const x = box.x + (values.length === 1 ? 0 : (i / (values.length - 1)) * box.width);
    const y = box.y + box.height - ((v - min) / (max - min)) * box.height;
    run.push([x, y]);
  }
  if (run.length) segments.push(run);
  return { segments, lo: min, hi: max };
}
