// The materialised catalogue on screen: where a star is drawn, and which one was
// clicked.
//
// The columns arrive from /api/region as typed arrays — radius, azimuth, height,
// age, metallicity, mass, and a population code that is a BigInt because the
// model publishes an int64. Nothing here computes anything about a star; it
// places one, finds one, and reads its columns back out with the labels and
// units its declarations carry (rule D5).
//
// A star is drawn where its own radius and azimuth put it. The cell that drew it
// may not be the cell its radius falls in — inverting a ring's CDF can place a
// star up to one R-spacing outside its own ring (D69) — so anything drawing cell
// boundaries must expect a few stars just outside theirs. That is the model
// being honest about where a sample comes from, not an error to clamp away.

import { numberOf } from "./ramp.js";

/** Face-on projection: radius and azimuth to canvas pixels. */
export function project(columns, scale, size) {
  const radius = columns.star_radius;
  const azimuth = columns.star_azimuth;
  const n = radius ? radius.length : 0;
  const sx = new Float32Array(n);
  const sy = new Float32Array(n);
  const half = size / 2;
  for (let i = 0; i < n; i += 1) {
    const r = radius[i];
    const phi = azimuth[i];
    sx[i] = half + Math.cos(phi) * r * scale.perKpc;
    sy[i] = half - Math.sin(phi) * r * scale.perKpc; // screen y grows downward
  }
  return { sx, sy, n };
}

/** The star nearest a point, within `within` pixels. -1 when the click hit nothing. */
export function nearest(px, py, { sx, sy, n }, within = 8) {
  let best = -1;
  let bestDistance = within * within;
  for (let i = 0; i < n; i += 1) {
    const dx = sx[i] - px;
    const dy = sy[i] - py;
    const d = dx * dx + dy * dy;
    if (d <= bestDistance) {
      bestDistance = d;
      best = i;
    }
  }
  return best;
}

/** A number as text: four significant figures, exponential where that is clearer. */
export function format(value) {
  const v = numberOf(value);
  if (!Number.isFinite(v)) return "—"; // an em dash: there is no number here (rule B9)
  if (v === 0) return "0";
  const size = Math.abs(v);
  if (size >= 1e5 || size < 1e-3) return v.toExponential(3);
  return String(Number(v.toPrecision(4)));
}

/**
 * One star, as rows for a panel: label, value, unit — every one of them from the
 * field declaration that published the column.
 */
export function describe(index, columns, declarations) {
  const rows = [];
  for (const [name, column] of Object.entries(columns)) {
    const decl = declarations[name];
    if (!decl || index < 0 || index >= column.length) continue;
    const raw = column[index];
    if (decl.categorical) {
      rows.push({ name, label: decl.label, value: decl.categories[numberOf(raw)] ?? "?", unit: "" });
    } else {
      rows.push({ name, label: decl.label, value: format(raw), unit: decl.unit_display || "" });
    }
  }
  return rows;
}

/** How many stars a region query got, against how many it asked the galaxy for. */
export function census(header) {
  return {
    materialised: header.stars.materialised,
    requested: header.stars.requested,
    cells: header.cells.count,
    of: header.cells.of,
    seed: header.stars.seed,
  };
}
