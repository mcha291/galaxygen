// Value to colour, from the declaration and nothing else (rule A9).
//
// Everything this module needs arrives from /api/fields: which cmap, which
// scale, whether the bounds are pinned, whether zero means something, and the
// stops behind the cmap's name. It holds no colour and no cmap of its own — a
// test asserts that by scanning this file for both.
//
// Two decisions are the viewer's to make, and the declaration says so.
//
//   - **Bounds when the ramp does not pin them.** `lo`/`hi` of null mean "from
//     the data", so the ramp takes the 2nd and 98th percentiles: a single hot
//     cell must not flatten everything else to one colour.
//   - **Where zero sits.** A field with a meaningful zero drawn through a
//     diverging map gets bounds symmetric about zero, so the map's middle stop
//     — its neutral colour — lands on zero rather than near it. A pinned bound
//     always wins: that is the declaration speaking.
//
// A value that is not a number is drawn as nothing at all — alpha zero, no
// colour anywhere on the ramp (rule B9). Zero is a measurement and NaN is not,
// and painting the second one the colour of the first is the lie that rule is
// about.

const HEX = /^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i;
const PERCENTILE_LO = 0.02;
const PERCENTILE_HI = 0.98;
const SAMPLE_MAX = 20000; // enough for a percentile; a 800k-cell field is not sorted twice
const SYMLOG_DECADES = 3; // the linear window of a symlog scale, below the outer bound

/**
 * A value as a number, with JavaScript's most dangerous coercion removed.
 *
 * `Number(null)` is 0, and `null` is exactly how this API publishes a scalar the
 * model has no number for. Left alone, a missing metallicity would be drawn the
 * colour of zero metallicity and read as a measurement — the failure rule B9 is
 * about, arriving through a language feature rather than through a decision.
 * `Number("")` is 0 as well, and an empty form field is not a zero either.
 */
export function numberOf(value) {
  if (value === null || value === undefined || value === "") return NaN;
  return Number(value);
}

export function rgbOf(hex) {
  const m = HEX.exec(hex);
  if (!m) throw new Error(`not a colour: ${hex}`);
  return [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)];
}

/** min, max and the percentile bounds, from a sample when the array is large. */
export function statistics(values) {
  let min = Infinity;
  let max = -Infinity;
  let finite = 0;
  for (let i = 0; i < values.length; i += 1) {
    const v = numberOf(values[i]);
    if (!Number.isFinite(v)) continue;
    finite += 1;
    if (v < min) min = v;
    if (v > max) max = v;
  }
  if (finite === 0) return { min: null, max: null, lo: null, hi: null, finite: 0, count: values.length };

  const step = Math.max(1, Math.floor(values.length / SAMPLE_MAX));
  const sample = [];
  for (let i = 0; i < values.length; i += step) {
    const v = numberOf(values[i]);
    if (Number.isFinite(v)) sample.push(v);
  }
  sample.sort((a, b) => a - b);
  const at = (p) => sample[Math.min(sample.length - 1, Math.max(0, Math.round(p * (sample.length - 1))))];
  return { min, max, lo: at(PERCENTILE_LO), hi: at(PERCENTILE_HI), finite, count: values.length };
}

function smallestPositive(values) {
  let best = Infinity;
  for (let i = 0; i < values.length; i += 1) {
    const v = numberOf(values[i]);
    if (Number.isFinite(v) && v > 0 && v < best) best = v;
  }
  return Number.isFinite(best) ? best : null;
}

/**
 * The ramp for one field over one array of values.
 *
 * `decl` is the field declaration and `cmaps` the table /api/fields publishes.
 * Nothing else is consulted.
 */
export function makeRamp(decl, cmaps, values) {
  const spec = decl.ramp;
  if (!spec || spec.kind !== "ramp") throw new Error(`field ${decl.name} has no ramp to draw with`);
  const table = cmaps[spec.cmap];
  if (!table) throw new Error(`no stops published for ${spec.cmap}`);
  const stops = table.stops.map(rgbOf);
  const stats = statistics(values ?? []);

  let lo = spec.lo ?? stats.lo ?? 0;
  let hi = spec.hi ?? stats.hi ?? 1;
  let scale = spec.scale;
  let note = "";

  if (scale === "log") {
    const floor = spec.lo ?? smallestPositive(values ?? []);
    if (floor === null || floor <= 0 || hi <= 0) {
      scale = "linear";
      note = "log needs positive values; drawn linear";
    } else {
      lo = Math.max(floor, Number.MIN_VALUE);
      hi = Math.max(hi, lo * (1 + 1e-12));
    }
  }
  // A meaningful zero through a diverging map is drawn with zero at the middle
  // stop — but only where the declaration left the bounds open.
  if (table.diverging && decl.meaningful_zero && spec.lo === null && spec.hi === null) {
    const reach = Math.max(Math.abs(lo), Math.abs(hi)) || 1;
    lo = -reach;
    hi = reach;
  }
  if (!(hi > lo)) hi = lo + (Math.abs(lo) || 1) * 1e-6;

  const threshold = Math.max(Math.abs(lo), Math.abs(hi)) / 10 ** SYMLOG_DECADES;

  function position(value) {
    const v = numberOf(value);
    if (!Number.isFinite(v)) return null;
    if (scale === "log") {
      const c = Math.min(Math.max(v, lo), hi);
      return c <= 0 ? 0 : (Math.log(c) - Math.log(lo)) / (Math.log(hi) - Math.log(lo));
    }
    if (scale === "symlog") {
      const f = (x) => (Math.abs(x) <= threshold ? x / threshold : Math.sign(x) * (1 + Math.log10(Math.abs(x) / threshold)));
      const a = f(Math.min(Math.max(v, lo), hi));
      const s = f(lo);
      const e = f(hi);
      return e === s ? 0 : (a - s) / (e - s);
    }
    return Math.min(Math.max((v - lo) / (hi - lo), 0), 1);
  }

  function at(t) {
    const x = Math.min(Math.max(t, 0), 1) * (stops.length - 1);
    const i = Math.min(stops.length - 2, Math.floor(x));
    const f = x - i;
    const a = stops[i];
    const b = stops[i + 1];
    return [
      Math.round(a[0] + (b[0] - a[0]) * f),
      Math.round(a[1] + (b[1] - a[1]) * f),
      Math.round(a[2] + (b[2] - a[2]) * f),
    ];
  }

  function color(value) {
    const t = position(value);
    if (t === null) return [0, 0, 0, 0]; // not a number: nothing is drawn (rule B9)
    const [r, g, b] = at(t);
    return [r, g, b, 255];
  }

  return { field: decl.name, cmap: spec.cmap, scale, lo, hi, note, stats, stops, at, position, color };
}

/** A categorical field's palette: one declared colour per category, by code. */
export function makePalette(decl) {
  const spec = decl.ramp;
  if (!spec || spec.kind !== "palette") throw new Error(`field ${decl.name} has no palette`);
  const colors = spec.colors.map(rgbOf);
  return {
    field: decl.name,
    categories: decl.categories.slice(),
    colors,
    color(code) {
      const i = numberOf(code);
      const c = colors[i];
      return c ? [c[0], c[1], c[2], 255] : [0, 0, 0, 0];
    },
    label(code) {
      return decl.categories[numberOf(code)] ?? "?";
    },
  };
}

/** A strip of the ramp, for a legend. The legend is the ramp, not a copy of it. */
export function legendStops(ramp, n = 32) {
  return Array.from({ length: n }, (_, i) => ramp.at(i / (n - 1)));
}
