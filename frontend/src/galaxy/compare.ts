// "Compare with a picture" (T16 ii; S54, D213 ruling 7): what the caption under the render states, so a picture
// set beside it is compared with something named - the galaxy, the filter set, the scale and the inclination.
// Pure: the numbers are the camera's own (GalaxyView's ViewState), read back through capture.ts. Nothing here is
// physics (rule D5): a scale in kiloparsecs per pixel is the camera's geometry, and its angle on the sky is that
// length over the distance the template states.

import { formatNumber } from "../workflow/logic";
import { standOf } from "./capture";

/** Arcseconds in a radian. */
const ARCSEC_PER_RADIAN = (180 * 3600) / Math.PI;

export interface CompareView {
  /** Screen pixels per kpc at the orbit target (ViewState.pxPerKpc). */
  pxPerKpc: number;
  /** The camera's lens, degrees (ViewState.fov). */
  fov: number;
  /** Where the camera is and what it looks at, in the scene's frame, kpc. */
  position: readonly number[];
  target: readonly number[];
}

export interface CompareGalaxy {
  /** The template's label with "edited" where it applies (templates.ts templateLabel); null where the API has no templates. */
  label: string | null;
  /** The filter set's label, as its button reads. */
  filters: string;
  /** The distance the template states for the galaxy, Mpc; null where it states none. */
  distanceMpc: number | null;
}

export interface CompareCaption {
  /** What the render is of. */
  galaxy: string;
  /** What it is seen through. */
  filters: string;
  /** Kiloparsecs one screen pixel covers at the centre of the view. */
  kpcPerPixel: number;
  /** The same as an angle on the sky at the template's distance, arcseconds; null without a distance. */
  arcsecPerPixel: number | null;
  /** The line of sight's angle from the disc's axis, degrees: 0 face-on, 90 edge-on. */
  inclinationDeg: number;
  fovDeg: number;
  /** The caption's lines, as shown. */
  lines: string[];
}

/** One screen pixel at the centre of the view, kpc: the inverse of the scale bar's pixels per kpc. */
export function kpcPerPixel(pxPerKpc: number): number {
  return 1 / pxPerKpc;
}

/**
 * A length across the line of sight as an angle at a distance, arcseconds (small angles): what a pixel of the
 * render is on the sky for a galaxy at the template's distance, to set against a picture's own pixel scale.
 */
export function arcsecOf(kpc: number, distanceMpc: number): number {
  return (kpc / (distanceMpc * 1000)) * ARCSEC_PER_RADIAN;
}

/** An angle on the sky at a distance as a length across the line of sight, kpc (small angles): arcsecOf's inverse. */
export function kpcOfArcsec(arcsec: number, distanceMpc: number): number {
  return (arcsec / ARCSEC_PER_RADIAN) * distanceMpc * 1000;
}

/**
 * A picture's pixel scale as the user states it (T16 ii, S83): kiloparsecs per pixel, or arcseconds per pixel with the
 * distance that makes them a length.
 */
export type PictureScale = { unit: "kpc"; perPixel: number } | { unit: "arcsec"; perPixel: number; distanceMpc: number };

/** Kiloparsecs one pixel of the picture covers, or null where the statement is not a scale (empty, zero, negative). */
export function kpcPerPicturePixel(scale: PictureScale): number | null {
  const ok = (v: number) => Number.isFinite(v) && v > 0;
  if (!ok(scale.perPixel)) return null;
  if (scale.unit === "kpc") return scale.perPixel;
  return ok(scale.distanceMpc) ? kpcOfArcsec(scale.perPixel, scale.distanceMpc) : null;
}

/**
 * The width a picture is drawn at beside the render, CSS pixels: its own width in kpc (pixels x kpc per pixel) at the
 * render's pixels per kpc (ViewState.pxPerKpc, the scale bar's). The two panes are the same width, so the picture's
 * pane is then the same kpc across as the render's - the left pane's across at its orbit target - and the scale bar
 * reads the same on both. The browser resamples it; nothing here is physics (rule D5).
 */
export function pictureWidthPx(imagePx: number, kpcPerPx: number, pxPerKpc: number): number {
  return imagePx * kpcPerPx * pxPerKpc;
}

/** The picture's caption: its file, the band the user states, and its scale - stated, and as drawn. */
export function pictureCaption(name: string, band: string, scale: PictureScale, imagePx: number | null): string[] {
  const kpc = kpcPerPicturePixel(scale);
  const stated =
    scale.unit === "kpc"
      ? `${formatNumber(scale.perPixel, 3)} kpc per pixel`
      : `${formatNumber(scale.perPixel, 3)}″ per pixel at ${formatNumber(scale.distanceMpc, 3)} Mpc`;
  const across = kpc !== null && imagePx !== null ? ` · ${imagePx} px = ${formatNumber(imagePx * kpc, 3)} kpc across` : "";
  return [
    `Picture: ${name}${band.trim() ? `, in ${band.trim()}` : ", band not stated"}.`,
    kpc === null ? "Scale not stated: drawn to fit the pane, not to the render's scale." : `${stated}${scale.unit === "arcsec" ? ` (${formatNumber(kpc, 3)} kpc)` : ""}${across}`,
  ];
}

/**
 * What the render is, for a picture set beside it: the template (and whether it has been edited), the filter
 * set, the scale at the centre of the view and the inclination, each read from the view as it stands now - an
 * orbit or a zoom changes the caption with the picture.
 */
export function compareCaption(view: CompareView, galaxy: CompareGalaxy): CompareCaption {
  const stand = standOf(view.position, view.target, view.fov);
  const scale = kpcPerPixel(view.pxPerKpc);
  const arcsec = galaxy.distanceMpc !== null && galaxy.distanceMpc > 0 ? arcsecOf(scale, galaxy.distanceMpc) : null;
  const name = galaxy.label ?? "the default galaxy";
  const onSky = arcsec === null ? "" : ` (${formatNumber(arcsec, 3)}″ at ${formatNumber(galaxy.distanceMpc!, 3)} Mpc)`;
  return {
    galaxy: name,
    filters: galaxy.filters,
    kpcPerPixel: scale,
    arcsecPerPixel: arcsec,
    inclinationDeg: stand.inclination_deg,
    fovDeg: view.fov,
    lines: [
      `Render: ${name}, through the ${galaxy.filters} filters.`,
      `${formatNumber(scale, 3)} kpc per pixel at the centre${onSky} · inclination ${stand.inclination_deg.toFixed(1)}° · ${formatNumber(view.fov, 3)}° lens`,
    ],
  };
}
