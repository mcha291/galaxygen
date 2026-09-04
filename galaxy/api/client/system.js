// One system, laid out for drawing. No DOM, no colour, no physics.
//
// The dynamic range is why this is a module and not four lines in a canvas
// callback: a system runs from 0.05 AU to 30 AU, which is nearly three decades,
// and a linear axis draws every inner planet on top of the star. So the axis is
// logarithmic and the ticks are decades — and because that is a *decision about
// how to read the picture*, it lives where it can be asserted rather than in a
// drawing routine where it can only be looked at.
//
// Sizes are areas, not radii: a marker's radius goes as the square root of the
// planet's, so a Jupiter next to an Earth reads as bigger without being 11 times
// wider than the orbit it sits on. Neither is to scale, and the caption says so.

const PAD = 0.8; // how far past the innermost and outermost thing the axis reaches
const MIN_MARK = 2.2;
const MAX_MARK = 13;

export function domain(planets, belts, { inner = null, outer = null } = {}) {
  const axes = Array.from(planets.planet_semi_major_axis ?? [], Number).filter(Number.isFinite);
  const edges = belts.flatMap((b) => [b.inner, b.outer]).filter(Number.isFinite);
  const all = [...axes, ...edges];
  if (!all.length) return null;
  const lo = inner ?? Math.min(...all) * PAD;
  const hi = outer ?? Math.max(...all) / PAD;
  return { lo: Math.max(lo, 1e-4), hi: Math.max(hi, lo * 10) };
}

/** Decade ticks inside the domain — 0.01, 0.1, 1, 10 … and nothing between them. */
export function ticks(range) {
  const out = [];
  const first = Math.ceil(Math.log10(range.lo));
  for (let e = first; 10 ** e <= range.hi; e += 1) out.push(10 ** e);
  return out;
}

export function markSize(radius) {
  const r = Number(radius);
  if (!Number.isFinite(r) || r <= 0) return MIN_MARK;
  return Math.min(MAX_MARK, Math.max(MIN_MARK, 1.6 * Math.sqrt(r) + 1.2));
}

/**
 * Where everything goes, in box coordinates.
 *
 * Returns the star at the left edge, one mark per planet, one band per belt, and
 * the ticks — everything a caller needs to draw, and nothing about how.
 */
export function layout(planets, belts, box, options = {}) {
  const range = domain(planets, belts, options);
  if (!range) return null;
  const span = Math.log10(range.hi) - Math.log10(range.lo);
  const at = (a) => box.x + ((Math.log10(a) - Math.log10(range.lo)) / span) * box.width;
  const middle = box.y + box.height / 2;
  const axes = Array.from(planets.planet_semi_major_axis ?? [], Number);
  const radii = Array.from(planets.planet_radius ?? [], Number);

  return {
    range,
    axis: { y: middle, x0: box.x, x1: box.x + box.width },
    star: { x: box.x, y: middle },
    ticks: ticks(range).map((a) => ({ a, x: at(a) })),
    bands: belts.map((b) => ({ ...b, x0: at(Math.max(b.inner, range.lo)), x1: at(Math.min(b.outer, range.hi)) })),
    marks: axes.map((a, i) => ({
      index: i,
      a,
      x: at(a),
      y: middle,
      size: markSize(radii[i]),
    })),
  };
}

/** The planet under a click, or -1. Marks are on one line, so this is a distance in x. */
export function pick(layout, x, y, slack = 8) {
  let best = -1;
  let closest = slack;
  for (const mark of layout.marks) {
    const distance = Math.hypot(mark.x - x, mark.y - y);
    if (distance <= Math.max(slack, mark.size) && distance < closest) {
      closest = distance;
      best = mark.index;
    }
  }
  return best;
}
