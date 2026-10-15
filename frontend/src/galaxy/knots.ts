// The HII regions as knots (S64, BUILD_III V6; RULING_S64 R5, R6). No three.js here: the pure parts, tested.
//
// Each cluster's HII region is a point of its own lines through the filter set - /api/clusters' `line_response` over
// the white point, as every point's light is (flux.ts fluxOf) - sized by its Stromgren radius (plummer.ts: a disc once
// its diameter fills a pixel). Where the viewer draws knots it takes the same light out of the field: in each level-0
// cell c the field's HII layers (the render's halpha_hii and lines_hii) are scaled by 1 - D_c / K_c, D_c the Halpha of
// the knots drawn in c and K_c the Halpha of every knot the cell names (the clusters' `cell` column); a cell that
// names no knot (no HII region realised there) by 1 - d, d the drawn share of the whole census's Halpha - the clusters
// header's `knots.rule`, applied here (D5: sums, a quotient, a guard). The screen then carries the census exactly where
// every knot is drawn and the field where none is, never both whole. The cells are the header's layout
// (`knots.layout`, systems.cell_edges), the same the catalogues are cut by.

import type { Census } from "../api";
import type { CellLayout } from "./brightTiles";

/** `/api/clusters`' `knots` header entry (api/v6_knots.py): what a knot is drawn from and the rule. */
export interface KnotsHeader {
  light: string;
  size: string;
  cell: string;
  column: string;
  lines: Record<string, { wavelength: number; from: string }>;
  unmatched: string[];
  layout: CellLayout;
  rule: string;
  closure: string;
  about: string;
}

/** The census's knots entry, or null where the route sends none (an API from before S64, or no region light). */
export function knotsOf(census: Census | null | undefined): KnotsHeader | null {
  const k = census?.header.knots as KnotsHeader | undefined;
  return k && k.layout && Array.isArray(k.layout.ring_edges) ? k : null;
}

/**
 * Per level-0 cell (ring-major, layout.rings x layout.sectors), the share of the field's HII light that stays drawn:
 * 1 - D_c / K_c, D_c the Halpha of the knots `drawn` names in cell c, K_c the Halpha of every knot c names; where K_c
 * is 0 (no region realised), 1 - d, d the drawn share of the whole census's Halpha (sum D over sum K: 1 with none drawn,
 * 0 with all). `drawn` is every knot (true), none (false), or a mask by row. A non-finite or negative light counts as
 * none (B9). Computed in double, sent as float32: in [0, 1], never negative.
 */
export function undrawnShare(
  cells: ArrayLike<number | bigint>,
  light: ArrayLike<number>,
  drawn: boolean | ArrayLike<boolean | number>,
  layout: Pick<CellLayout, "rings" | "sectors">,
): Float32Array {
  const count = layout.rings * layout.sectors;
  const K = new Float64Array(count);
  const D = new Float64Array(count);
  for (let i = 0; i < light.length; i += 1) {
    const c = Number(cells[i]);
    const l = Number(light[i]);
    if (!(c >= 0 && c < count) || !(l > 0) || !Number.isFinite(l)) continue;
    K[c] += l;
    if (drawn === true || (typeof drawn === "object" && drawn[i])) D[c] += l;
  }
  let sumK = 0;
  let sumD = 0;
  for (let c = 0; c < count; c += 1) {
    sumK += K[c];
    sumD += D[c];
  }
  const undrawn = sumK > 0 ? Math.min(1, Math.max(0, 1 - sumD / sumK)) : 1;
  const share = new Float32Array(count);
  for (let c = 0; c < count; c += 1) share[c] = K[c] > 0 ? Math.min(1, Math.max(0, 1 - D[c] / K[c])) : undrawn;
  return share;
}

/** The level-0 cell a place (r, phi) lies in by the layout's edges, ring-major; -1 outside them (the march's lookup). */
export function cellAt(r: number, phi: number, layout: CellLayout): number {
  const rings = layout.ring_edges;
  const lo = rings[0];
  const hi = rings[rings.length - 1];
  if (!(r >= lo && r < hi)) return -1;
  const ring = Math.min(layout.rings - 1, Math.floor(((r - lo) / (hi - lo)) * layout.rings));
  const turn = ((phi % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);
  const sector = Math.min(layout.sectors - 1, Math.floor((turn / (2 * Math.PI)) * layout.sectors));
  return ring * layout.sectors + sector;
}

/** The layout's rings are evenly spaced and its sectors cover the turn evenly (systems.cell_edges): what cellAt assumes. */
export function evenLayout(layout: CellLayout): boolean {
  const even = (e: number[], n: number) =>
    e.length === n + 1 && e.every((v, i) => Math.abs(v - (e[0] + ((e[n] - e[0]) * i) / n)) <= 1e-9 * Math.max(1, Math.abs(e[n])));
  return even(layout.ring_edges, layout.rings) && even(layout.sector_edges, layout.sectors) && layout.sector_edges[0] === 0 &&
    Math.abs(layout.sector_edges[layout.sectors] - 2 * Math.PI) < 1e-12;
}
