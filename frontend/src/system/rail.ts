// Where a system's bodies sit along the rail. The log layout is interface/system.js
// (a system spans 0.05 to 30 AU, so a linear axis puts every inner planet on the
// star); this adds the schematic rail the design brief asks for beside it, where
// order is kept and distance is not.
import { layout as logLayout } from "@interface/system.js";

export type RailMode = "log" | "schematic";

export interface Box {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Mark {
  index: number;
  a: number;
  x: number;
  y: number;
  size: number;
}

export interface Band {
  kind: string;
  inner: number;
  outer: number;
  x0: number;
  x1: number;
}

export interface Rail {
  mode: RailMode;
  marks: Mark[];
  bands: Band[];
  ticks: { a: number; x: number }[];
}

export interface Belt {
  kind: string;
  inner: number;
  outer: number;
}

/**
 * The schematic rail: planets evenly spaced in order of semi-major axis, and a
 * belt drawn between the neighbours it falls between. No ticks, because no
 * distance on it means anything.
 */
export function schematic(axes: ArrayLike<number>, radii: ArrayLike<number>, belts: Belt[], box: Box, size: (r: number) => number): Rail {
  const order = Array.from(axes, (a, i) => ({ a: Number(a), i })).filter((p) => Number.isFinite(p.a)).sort((p, q) => p.a - q.a);
  const step = box.width / (order.length + 1);
  const y = box.y + box.height / 2;
  const marks = order.map((p, k) => ({ index: p.i, a: p.a, x: box.x + step * (k + 1), y, size: size(Number(radii[p.i])) }));
  // A distance maps to the rail by interpolating between the marks on either side.
  const xOf = (a: number) => {
    const points = [{ a: 0, x: box.x }, ...marks.map((m) => ({ a: m.a, x: m.x }))];
    for (let k = 1; k < points.length; k += 1) {
      if (a <= points[k].a) return points[k - 1].x + ((a - points[k - 1].a) / (points[k].a - points[k - 1].a)) * (points[k].x - points[k - 1].x);
    }
    return box.x + box.width;
  };
  return { mode: "schematic", marks, bands: belts.map((b) => ({ ...b, x0: xOf(b.inner), x1: xOf(b.outer) })), ticks: [] };
}

export function railOf(mode: RailMode, planets: Record<string, ArrayLike<number>>, belts: Belt[], box: Box, size: (r: number) => number): Rail | null {
  if (mode === "schematic") return schematic(planets.planet_semi_major_axis ?? [], planets.planet_radius ?? [], belts, box, size);
  const laid = logLayout(planets, belts, box);
  return laid ? { mode, marks: laid.marks, bands: laid.bands, ticks: laid.ticks } : null;
}

/** The planet nearest a click on the rail, within its mark or a few pixels of it; -1 for none. */
export function pickMark(rail: Rail, x: number, y: number, slack = 8): number {
  let best = -1;
  let closest = Infinity;
  for (const m of rail.marks) {
    const d = Math.hypot(m.x - x, m.y - y);
    if (d <= Math.max(slack, m.size) && d < closest) {
      closest = d;
      best = m.index;
    }
  }
  return best;
}
