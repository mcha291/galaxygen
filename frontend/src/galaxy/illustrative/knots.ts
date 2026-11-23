// The pink HII regions (BUILD_VIII row 106, S106; D275: display-only). The model's own HII regions - the field mode's
// knots, at their places with their own lines' light - drawn at a visible size as soft irregular nebulae in H-alpha's
// pink with a white-blue core (the young cluster), gathered to the arms by the gas's own contrast at each region's
// place (the dust's placement, D210), faded in the far disc, and dimmed by the march's dust as the default knots are.
// In place of the default knots while drawn (replacesKnots). The arithmetic is knotsMath.ts, the drawing knotsLayer.ts.
//
// Why: in the Milky Way goal hundreds of pink regions a few hundred parsecs across string along the arms, fairly even
// in brightness; the model's regions are 5-70 pc (under a pixel at galaxy scale) over six decades of H-alpha. So the
// radius is multiplied and clamped, the light compressed about its 90th percentile, and a weight taken from the arms.

import type { IllControl, IllFeature } from "./feature";
import { KnotsLayer } from "./knotsLayer";

const CONTROLS: readonly IllControl[] = [
  { key: "draw", label: "regions drawn", min: 0, max: 1, step: 1, default: 1, about: "1: the HII regions drawn as illustrative nebulae in place of the knots; 0: the default knots. Illustrative." },
  {
    key: "gain", label: "regions gain", min: 0.01, max: 1000, step: 0.01, log: true, unit: "×", default: 100, perTemplate: { milky_way: 250, ngc_4414: 40 },
    about: "A multiplier on the regions' light over the knots' gain (the field's scale and the exposure). Illustrative.",
  },
  {
    key: "lumPower", label: "light compression", min: 0.05, max: 1, step: 0.01, unit: "power", default: 0.3, perTemplate: { milky_way: 0.45, ngc_4414: 0.35 },
    about: "Each region's light drawn as ref (L / ref)^power, ref the 90th percentile: below 1 the string reads evenly, not as a few bright dots. Illustrative.",
  },
  {
    key: "count", label: "regions drawn (brightest)", min: 100, max: 20000, step: 100, default: 2000, perTemplate: { milky_way: 1200, ngc_4414: 3000 },
    about: "Only the brightest this many regions by their weighted, compressed light are drawn. Illustrative.",
  },
  {
    key: "size", label: "region size", min: 0.5, max: 40, step: 0.1, log: true, unit: "×", default: 8, perTemplate: { milky_way: 2.5, ngc_4414: 6 },
    about: "A multiplier on each region's own radius (hii_radius) for its drawn radius. Illustrative.",
  },
  {
    key: "sizeMin", label: "region radius floor", min: 0, max: 400, step: 5, unit: "pc", default: 40, perTemplate: { milky_way: 12, ngc_4414: 50 },
    about: "The smallest drawn radius, pc: regions read as blobs at galaxy scale. Illustrative.",
  },
  {
    key: "sizeMax", label: "region radius ceiling", min: 10, max: 1000, step: 5, unit: "pc", default: 150, perTemplate: { milky_way: 60, ngc_4414: 180 },
    about: "The largest drawn radius, pc. Illustrative.",
  },
  {
    key: "armPower", label: "arm weight power", min: 0, max: 8, step: 0.1, unit: "power", default: 3, perTemplate: { milky_way: 6, ngc_4414: 1 },
    about: "Each region weighted by min(1, (t / level)^power), t the gas's own contrast at its place (the dust's placement) between its ring's 10th (0) and 95th (1) percentiles: regions between the arms fade. 0: none. Illustrative.",
  },
  {
    key: "armLevel", label: "arm weight level", min: 0.05, max: 1, step: 0.01, unit: "", default: 0.8, perTemplate: { milky_way: 0.9, ngc_4414: 0.5 },
    about: "The ring-relative contrast t at and above which a region is drawn whole. Illustrative.",
  },
  {
    key: "armFlat", label: "arm weight off the arms' reach", min: 0, max: 1, step: 0.01, unit: "", default: 0.05,
    about: "The t taken where a ring has no contrast (no arm placed there, the far disc). Illustrative.",
  },
  {
    key: "fadeR", label: "regions fade radius", min: 1, max: 30, step: 0.5, unit: "kpc", default: 11, perTemplate: { milky_way: 9, ngc_4414: 5.5 },
    about: "Past this radius the regions fade out, over the fade width. Illustrative.",
  },
  { key: "fadeWidth", label: "regions fade width", min: 0.5, max: 15, step: 0.5, unit: "kpc", default: 3, about: "The width of the outer fade, kpc. Illustrative." },
  {
    key: "innerR", label: "regions inner radius", min: 0, max: 8, step: 0.1, unit: "kpc", default: 0, perTemplate: { milky_way: 1, ngc_4414: 1 },
    about: "Inside this radius the regions fade in over the kpc below it (0: none). Illustrative.",
  },
  {
    key: "pink", label: "pink", min: 0, max: 1, step: 0.01, unit: "", default: 0.9, perTemplate: { milky_way: 1, ngc_4414: 0.2 },
    about: "The regions' colour mixed from their own lines' colour (0) toward H-alpha pink (1). Colour for appearance.",
  },
  {
    key: "magenta", label: "pink to magenta", min: -1, max: 1, step: 0.01, unit: "", default: 0.15, perTemplate: { milky_way: -0.4, ngc_4414: 0.1 },
    about: "The pink's hue, from a red pink (0) to magenta (1); below 0 past the pink toward a deep red (S105: the grade's cool tint turns a pink violet). Colour for appearance.",
  },
  { key: "blobs", label: "sub-blobs", min: 1, max: 4, step: 1, default: 4, about: "Each region drawn as this many soft sub-blobs, placed by a hash of its index (stable). Illustrative." },
  {
    key: "irregular", label: "irregularity", min: 0, max: 1.5, step: 0.01, unit: "", default: 1, perTemplate: { milky_way: 1.4 },
    about: "How far the sub-blobs lie from the centre, in region radii: 0 one round blob. Illustrative.",
  },
  { key: "soft", label: "softness", min: 0.2, max: 2, step: 0.01, unit: "×", default: 1, perTemplate: { milky_way: 0.6 }, about: "A multiplier on every sub-blob's Gaussian width. Illustrative." },
  {
    key: "coreGain", label: "core gain", min: 0, max: 5, step: 0.01, unit: "×", default: 0.8, perTemplate: { milky_way: 0.8, ngc_4414: 2 },
    about: "The white-blue core's light (the young cluster) over the region's own. Illustrative.",
  },
  { key: "coreSize", label: "core size", min: 0.02, max: 0.6, step: 0.01, unit: "×", default: 0.1, about: "The core's Gaussian width in region radii (at least 0.6 px). Illustrative." },
  {
    key: "coreShare", label: "regions with a core", min: 0, max: 1, step: 0.01, unit: "", default: 0.6, perTemplate: { milky_way: 0.6, ngc_4414: 0.9 },
    about: "The share of the regions that carry a core, by a stable hash of their index. Illustrative.",
  },
  {
    key: "dust", label: "regions' dust", min: 0, max: 1.5, step: 0.01, unit: "×", default: 1, perTemplate: { milky_way: 0.4 },
    about: "The march's dust to each region (as the knots are dimmed), multiplied: 0 none. Illustrative.",
  },
];

export const knots: IllFeature = {
  id: "knots",
  label: "HII regions",
  about: "The model's HII regions drawn as pink nebulae at a visible size with a white-blue core, gathered to the arms by the gas's contrast.",
  controls: CONTROLS,
  layer: KnotsLayer,
  replacesKnots: (p) => (p.draw ?? 1) >= 0.5,
};
