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
