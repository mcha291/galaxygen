// The brightest mode's component layers (D205, S50): switches that show where the model puts its
// starlight, ionized gas and dust, its molecular clouds and its level-0 cells, so the owner can see
// what the model holds. No three.js here: the pure parts, tested.
//
// Every layer is a published field or census (rule D5): the starlight, the gas and the dust are the
// field's own march (/api/render) with some of its terms switched off; the clouds are /api/clouds'
// census at its published positions and sizes; the cell outlines are the grid's own edges. Two readings
// are diagnostics, not pictures, and are labelled so on screen: the dust "where it is" (its optical
// depth drawn as light) and the clouds' and cells' markers (RENDER_PHYSICS §8 forbids colour applied
// for appearance; a declared false-colour view of a published field is the viewer's scientific mode).

import { makeRamp, paintOf } from "@interface/ramp.js";

import type { Columns, FieldsPayload } from "../api";
import { srgbToLinear } from "./colors";
import type { RegionWindow } from "./regimes";
import type { Tuning } from "./tuning";

export type Rgb = [number, number, number];

/** The colours the "where it is" reading's ramp is held at in the shader, evenly spaced from τ = 0 to the peak. */
export const WHERE_STOPS = 8;

/**
 * The march's layer switches, as its uniforms take them: each emitting layer's multiplier (0 is off),
 * the dust's depth switch (1: it dims what lies behind it), and the "where it is" reading's intensity
 * (0: not drawn; FieldVolume normalises it by the depth ring's peak, whereLevel) and its ramp's stops.
 */
export interface MarchLayers {
  stars: number;
  gas: number;
  dust: number;
  dustDepth: number;
  where: number;
  whereStops: readonly Rgb[];
}

/** A grey ramp kept grey: every stop white, so the drawn level alone carries the depth. */
export const GREY_STOPS: readonly Rgb[] = Object.freeze(Array.from({ length: WHERE_STOPS }, () => [1, 1, 1] as Rgb));

/**
 * The field mode's layers: everything on, the dust acting, nothing diagnostic. Each term of the march is
 * multiplied by one of these or has the zero added, so the field's picture is the march's to the bit
 * (x × 1 = x and x + 0 = x for every finite x; tuning.test.ts undoes the edits against S46's source).
 */
export const FIELD_LAYERS: Readonly<MarchLayers> = Object.freeze({ stars: 1, gas: 1, dust: 1, dustDepth: 1, where: 0, whereStops: GREY_STOPS });

/**
 * The level the densest ring's face-on dust column draws at in the "where it is" reading, linear, before
 * tone mapping, at intensity ×1, zero stops and a field gain of 1. **A display normalisation of a
 * diagnostic, not physics**: the reading is scaled by the reciprocal of the depth ring's own peak, so it is
 * readable whatever the galaxy's dust, and the caption states that peak so the picture stays quantitative.
 */
export const WHERE_LEVEL = 0.5;

/**
 * The depth ring's peak: the largest channel-mean face-on optical depth over the rings (regimes.ts
 * planeTexture's `rings`, row RING_ROWS.depth = 0, RGBA per R cell). Zero when there is no dust.
 */
export function depthPeak(rings: ArrayLike<number>, width: number): number {
  let peak = 0;
  for (let i = 0; i < width; i += 1) {
    const mean = (Number(rings[i * 4]) + Number(rings[i * 4 + 1]) + Number(rings[i * 4 + 2])) / 3;
    if (Number.isFinite(mean) && mean > peak) peak = mean;
  }
  return peak;
}

/**
 * The march's "where it is" multiplier, per unit of channel-mean optical depth in the march's units: the
 * layer's intensity times WHERE_LEVEL over the peak, over the field's light per L☉/pc² (`lightPerUnit`,
 * FieldVolume's LIGHT_PER_LSUN_PC2, which the march's gain multiplies back). A face-on ray through the
 * densest ring takes its whole column, τ = peak, so it draws at WHERE_LEVEL × intensity. Zero without dust.
 */
export function whereLevel(intensity: number, peak: number, lightPerUnit: number): number {
  return intensity > 0 && peak > 0 && lightPerUnit > 0 ? (WHERE_LEVEL * intensity) / (peak * lightPerUnit) : 0;
}

/** The shader's whereTint, line for line: the stops read linearly at τ / τ_peak, clamped to the ramp. */
export function whereTint(stops: readonly Rgb[], t: number): Rgb {
  const x = Math.min(1, Math.max(0, t)) * (stops.length - 1);
  const k = Math.min(stops.length - 2, Math.floor(x));
  const f = x - k;
  return [0, 1, 2].map((c) => stops[k][c] + (stops[k + 1][c] - stops[k][c]) * f) as Rgb;
}

/** Does any switch ask for the march in the brightest mode? */
export function marchWanted(t: Pick<Tuning, "compStars" | "compGas" | "compDust">): boolean {
  return t.compStars || t.compGas || t.compDust;
}

/** Is a diagnostic reading on (the dust where it is, the clouds, the cell outlines)? The mode's card says so when one is. */
export function diagnosticOn(t: Pick<Tuning, "compDust" | "dustReading" | "compClouds" | "compCells">): boolean {
  return (t.compDust && t.dustReading === "where") || t.compClouds || t.compCells;
}

/**
 * The march's layers for the brightest mode's switches: a switched-on layer at its intensity, the rest
 * at zero. The dust "as it acts" emits its scattered and thermal light at its intensity and dims what
 * lies behind it at its published depth (the intensity never scales a depth: that would be physics);
 * "where it is" draws its depth as light through `ramp` at its intensity (normalised to the peak by the
 * march) and dims nothing; without a declared ramp it draws nothing (rule A9).
 */
export function brightestLayers(
  t: Pick<Tuning, "compStars" | "compGas" | "compDust" | "dustReading" | "starsIntensity" | "gasIntensity" | "dustIntensity">,
  ramp: DustRamp | null,
): MarchLayers {
  const where = t.compDust && t.dustReading === "where";
  const acts = t.compDust && t.dustReading === "acts";
  return {
    stars: t.compStars ? t.starsIntensity : 0,
    gas: t.compGas ? t.gasIntensity : 0,
    dust: acts ? t.dustIntensity : 0,
    dustDepth: acts ? 1 : 0,
    where: where && ramp ? t.dustIntensity : 0,
    whereStops: ramp?.stops ?? GREY_STOPS,
  };
}

/** The dust fields whose declared ramp paints the "where it is" reading, in order of preference. */
export const DUST_TINT_FIELDS = ["dust_extinction_v", "dust_surface_density"] as const;

/** The ramp the "where it is" reading is painted with: whose declaration it is, its stops (linear light), and whether it has colour. */
export interface DustRamp {
  field: string;
  stops: readonly Rgb[];
  coloured: boolean;
}

/**
 * The "where it is" reading's ramp (rule A9: from a declaration, never the viewer's). The first of
 * DUST_TINT_FIELDS whose declared ramp has colour, its cmap's stops read by ramp.js at WHERE_STOPS even
 * positions, as linear light: the march reads it at τ / τ_peak. If every declared one is grey, the last of
 * them is kept grey — every stop white, so the drawn level alone (normalised to the peak) carries the depth:
 * a grey ramp mapped literally would draw the densest dust black, which on black is nothing. Null when no
 * dust field is declared with a ramp.
 */
export function dustRamp(meta: Pick<FieldsPayload, "fields" | "cmaps">): DustRamp | null {
  let grey: DustRamp | null = null;
  for (const name of DUST_TINT_FIELDS) {
    const decl = meta.fields.find((f) => f.name === name);
    if (!decl?.ramp || decl.ramp.kind !== "ramp") continue;
    try {
      const ramp = makeRamp(decl, meta.cmaps, []) as { at(t: number): number[]; stops: number[][] };
      const coloured = ramp.stops.some(([r, g, b]) => r !== g || g !== b);
      if (!coloured) {
        grey = { field: name, stops: GREY_STOPS, coloured: false };
        continue;
      }
      const stops = Array.from({ length: WHERE_STOPS }, (_, i) => ramp.at(i / (WHERE_STOPS - 1)).map((v) => srgbToLinear(v / 255)) as Rgb);
      return { field: name, stops, coloured: true };
    } catch {
      continue;
    }
  }
  return grey;
}

/** The level-0 cell grid's rings and sectors (the catalogue's cells: 32 × 32 over the model's radial extent). */
export const CELL_RINGS = 32;
export const CELL_SECTORS = 32;
/** Straight segments per ring circle: a display choice, smooth at any zoom the view allows. */
export const CIRCLE_SEGMENTS = 256;

/**
 * The level-0 cells' edges as line segments in the disc plane (scene x = R cos φ, y = 0, z = −R sin φ):
 * `rings + 1` circles at radii evenly spaced from `lo` to `hi`, and `sectors` spokes from `lo` to `hi`
 * every 2π / sectors. Three floats per vertex, two vertices per segment, for a LineSegments.
 */
export function cellOutlines(
  lo: number,
  hi: number,
  rings: number = CELL_RINGS,
  sectors: number = CELL_SECTORS,
  segments: number = CIRCLE_SEGMENTS,
): { positions: Float32Array; radii: number[]; circles: number; spokes: number } {
  const radii = Array.from({ length: rings + 1 }, (_, i) => lo + ((hi - lo) * i) / rings);
  const drawn = radii; // an edge at r = 0 is the centre and draws as nothing: kept, so every grid has rings + 1
  const out = new Float32Array((drawn.length * segments + sectors) * 6);
  let o = 0;
  const put = (r: number, phi: number) => {
    out[o++] = r * Math.cos(phi);
    out[o++] = 0;
    out[o++] = -r * Math.sin(phi);
  };
  for (const r of drawn) {
    for (let s = 0; s < segments; s += 1) {
      put(r, (2 * Math.PI * s) / segments);
      put(r, (2 * Math.PI * (s + 1)) / segments);
    }
  }
  for (let k = 0; k < sectors; k += 1) {
    const phi = (2 * Math.PI * k) / sectors;
    put(lo, phi);
    put(hi, phi);
  }
  return { positions: out, radii, circles: drawn.length, spokes: sectors };
}

/** A cloud marker's smallest size on screen, CSS px. */
export const CLOUD_MIN_PX = 2;

/**
 * A cloud marker's diameter on screen, px: the cloud's published radius `sizePc` (`cloud_size`, pc) as a
 * diameter in kpc, projected at its depth (`depth`, kpc along the view axis) by a perspective camera whose
 * `pxPerUnit` is the drawing buffer's height over 2 tan(fov / 2); never under `minPx`. The marker shader's
 * gl_PointSize, line for line.
 */
export function cloudMarkerPx(sizePc: number, depth: number, pxPerUnit: number, minPx: number = CLOUD_MIN_PX): number {
  const diameter = (2 * sizePc) / 1000;
  const px = depth > 0 ? (diameter * pxPerUnit) / depth : 0;
  return Math.max(minPx, Number.isFinite(px) ? px : 0);
}

/** The rows of a census inside a window, by its radius and azimuth columns (the footprint the brightest mode asks for). */
export function rowsInWindow(radius: ArrayLike<number>, azimuth: ArrayLike<number>, window: RegionWindow): Uint32Array {
  const rows: number[] = [];
  for (let i = 0; i < radius.length; i += 1) {
    const r = Number(radius[i]);
    const a = Number(azimuth[i]);
    if (r >= window.r_min && r <= window.r_max && a >= window.phi_min && a <= window.phi_max) rows.push(i);
  }
  return Uint32Array.from(rows);
}

/** The cloud columns the markers read. */
export const CLOUD_COLUMNS = ["cloud_radius", "cloud_azimuth", "cloud_height", "cloud_size", "cloud_mass"] as const;

/**
 * Each cloud's marker colour, linear light: `cloud_mass` through its declared ramp (ramp.js, rule A9),
 * the bounds taken over the whole census so a colour does not move as the view does, times `brightness`
 * (the tuning panel's marker intensity). A cloud with no mass is drawn black and transparent: alpha 0.
 */
export function cloudColors(meta: Pick<FieldsPayload, "fields" | "cmaps">, columns: Columns, brightness: number): Float32Array {
  const decl = meta.fields.find((f) => f.name === "cloud_mass");
  const mass = columns.cloud_mass as ArrayLike<number> | undefined;
  if (!decl || !mass) throw new Error("this census carries no cloud_mass");
  const paint = paintOf(decl, meta.cmaps, mass) as { color(v: number): number[] };
  const out = new Float32Array(mass.length * 4);
  for (let i = 0; i < mass.length; i += 1) {
    const [r, g, b, a] = paint.color(mass[i]);
    out[4 * i] = srgbToLinear(r / 255) * brightness;
    out[4 * i + 1] = srgbToLinear(g / 255) * brightness;
    out[4 * i + 2] = srgbToLinear(b / 255) * brightness;
    out[4 * i + 3] = a / 255;
  }
  return out;
}
