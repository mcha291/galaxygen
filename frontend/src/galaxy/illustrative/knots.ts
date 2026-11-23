// The pink HII regions (BUILD_VIII row 106, S106; D275: display-only). The model's own HII regions - the field mode's
// knots, at their places with their own lines' light - drawn at a visible size as soft irregular nebulae in H-alpha's
// pink with a white-blue core (the young cluster), gathered to the arms by the gas's own contrast at each region's
// place (the dust's placement, D210), faded in the far disc, and dimmed by the march's dust as the default knots are.
// In place of the default knots while drawn (replacesKnots). The arithmetic is knotsMath.ts, the drawing knotsLayer.ts.
//
// Why: in the Milky Way goal hundreds of pink regions a few hundred parsecs across string along the arms, fairly even
// in brightness; the model's regions are 5-70 pc (under a pixel at galaxy scale) over six decades of H-alpha. So the
// radius is multiplied and clamped, the light compressed about its 90th percentile, and a weight taken from the arms.
//
// S106 (builder K), `place` = 1 (the Milky Way's default): DISPLAY-ONLY DRAWING OF THE LAYER'S OWN (the lead's ruling
// 12). The model's HII places are not on the drawn arm skeleton (skeleton.ts) - drawn there they float between the arms
// - so the regions are laid by the viewer along the skeleton's ridges at the arms' live parameters with a fixed seed:
// bunches on the inner edge (the dust lane's side), denser where a ridge is strong, a steep size spread, a bright
// complex at each bar end; each a few overlapping lobes of pink-red hues along the arm with a small white core and a
// few blue-white points beside it (knotsPlace.ts; its own shaders in knotsLayer.ts). Only the light's scale is the
// model's. `place` = 0 (ngc_4414) draws exactly as before.

import type { IllControl, IllFeature } from "./feature";
import { KnotsLayer } from "./knotsLayer";

const CONTROLS: readonly IllControl[] = [
  { key: "draw", label: "regions drawn", min: 0, max: 1, step: 1, default: 1, about: "1: the HII regions drawn as illustrative nebulae in place of the knots; 0: the default knots. Illustrative." },
  {
    key: "gain", label: "regions gain", min: 0.01, max: 1000, step: 0.01, log: true, unit: "×", default: 100, perTemplate: { milky_way: 80, ngc_4414: 8 },
    about: "A multiplier on the regions' light over the knots' gain (the field's scale and the exposure). Illustrative.",
  },
  {
    key: "lumPower", label: "light compression", min: 0.05, max: 1, step: 0.01, unit: "power", default: 0.3, perTemplate: { milky_way: 0.45, ngc_4414: 0.35 },
    about: "Each region's light drawn as ref (L / ref)^power, ref the 90th percentile: below 1 the string reads evenly, not as a few bright dots. Illustrative.",
  },
  {
    key: "count", label: "regions drawn (brightest)", min: 100, max: 20000, step: 100, default: 2000, perTemplate: { milky_way: 300, ngc_4414: 300 },
    about: "Only the brightest this many regions by their weighted, compressed light are drawn. Illustrative.",
  },
  {
    key: "size", label: "region size", min: 0.5, max: 40, step: 0.1, log: true, unit: "×", default: 8, perTemplate: { milky_way: 2.0, ngc_4414: 6 },
    about: "A multiplier on each region's own radius (hii_radius) for its drawn radius. Illustrative.",
  },
  {
    key: "sizeMin", label: "region radius floor", min: 0, max: 400, step: 5, unit: "pc", default: 40, perTemplate: { milky_way: 25, ngc_4414: 50 },
    about: "The smallest drawn radius, pc: regions read as blobs at galaxy scale. Illustrative.",
  },
  {
    key: "sizeMax", label: "region radius ceiling", min: 10, max: 1000, step: 5, unit: "pc", default: 150, perTemplate: { milky_way: 180, ngc_4414: 180 },
    about: "The largest drawn radius, pc. Illustrative.",
  },
  {
    key: "armPower", label: "arm weight power", min: 0, max: 8, step: 0.1, unit: "power", default: 3, perTemplate: { milky_way: 8, ngc_4414: 1 },
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
    key: "fadeR", label: "regions fade radius", min: 1, max: 30, step: 0.5, unit: "kpc", default: 11, perTemplate: { milky_way: 14, ngc_4414: 5.5 },
    about: "Past this radius the regions fade out, over the fade width. Illustrative.",
  },
  { key: "fadeWidth", label: "regions fade width", min: 0.5, max: 15, step: 0.5, unit: "kpc", default: 3, about: "The width of the outer fade, kpc. Illustrative." },
  {
    key: "innerR", label: "regions inner radius", min: 0, max: 8, step: 0.1, unit: "kpc", default: 0, perTemplate: { milky_way: 1, ngc_4414: 1 },
    about: "Inside this radius the regions fade in over the kpc below it (0: none). Illustrative.",
  },
  {
    key: "pink", label: "pink", min: 0, max: 1, step: 0.01, unit: "", default: 0.9, perTemplate: { milky_way: 1, ngc_4414: 0 },
    about: "The regions' colour mixed from their own lines' colour (0) toward H-alpha pink (1). Colour for appearance.",
  },
  {
    key: "magenta", label: "pink to magenta", min: -1, max: 1, step: 0.01, unit: "", default: 0.15, perTemplate: { milky_way: -0.2, ngc_4414: 0.1 },
    about: "The pink's hue, from a red pink (0) to magenta (1); below 0 past the pink toward a deep red (S105: the grade's cool tint turns a pink violet). Colour for appearance.",
  },
  { key: "blobs", label: "sub-blobs", min: 1, max: 4, step: 1, default: 4, about: "Each region drawn as this many soft sub-blobs, placed by a hash of its index (stable). Illustrative." },
  {
    key: "irregular", label: "irregularity", min: 0, max: 1.5, step: 0.01, unit: "", default: 1, perTemplate: { milky_way: 1.4 },
    about: "How far the sub-blobs lie from the centre, in region radii: 0 one round blob. Illustrative.",
  },
  { key: "soft", label: "softness", min: 0.2, max: 2, step: 0.01, unit: "×", default: 1, perTemplate: { milky_way: 0.8 }, about: "A multiplier on every sub-blob's Gaussian width. Illustrative." },
  {
    key: "coreGain", label: "core gain", min: 0, max: 5, step: 0.01, unit: "×", default: 0.8, perTemplate: { milky_way: 0.4, ngc_4414: 2 },
    about: "The white-blue core's light (the young cluster) over the region's own. Illustrative.",
  },
  { key: "coreSize", label: "core size", min: 0.02, max: 0.6, step: 0.01, unit: "×", default: 0.1, perTemplate: { milky_way: 0.05 }, about: "The core's Gaussian width in region radii (at least 0.6 px). Illustrative." },
  {
    key: "coreShare", label: "regions with a core", min: 0, max: 1, step: 0.01, unit: "", default: 0.6, perTemplate: { milky_way: 0.9, ngc_4414: 0.9 },
    about: "The share of the regions that carry a core, by a stable hash of their index. Illustrative.",
  },
  // S106 (builder K): the regions laid on the arm skeleton (knotsPlace.ts), display-only drawing of the layer's own.
  {
    key: "place", label: "regions on the skeleton", min: 0, max: 1, step: 1, default: 0, perTemplate: { milky_way: 1, ngc_4414: 0 },
    about: "1: the regions laid by the viewer along the arm skeleton's ridges (bunches on the inner edge, a fixed seed; the model's regions only set the light's scale); 0: at the model's own HII places. Illustrative (S106).",
  },
  { key: "total", label: "skeleton: regions", min: 20, max: 2000, step: 10, default: 600, perTemplate: { milky_way: 1100 }, about: "About how many regions are laid on the skeleton (bar-end complexes and blue-white points apart). Illustrative (S106)." },
  { key: "bunch", label: "skeleton: bunch size", min: 1, max: 10, step: 0.1, default: 4, about: "The mean number of regions in a bunch (each bunch 0.3-1.7 times it). Illustrative (S106)." },
  { key: "gap", label: "skeleton: gap", min: 0, max: 4, step: 0.05, unit: "kpc", default: 1.2, perTemplate: { milky_way: 0.6 }, about: "No two bunches' centres closer than this, kpc: the gaps along a ridge. Illustrative (S106)." },
  { key: "bunchLen", label: "skeleton: bunch length", min: 0, max: 1.5, step: 0.01, unit: "kpc", default: 0.18, about: "A bunch's members spread along the arm by a Gaussian of this sigma, kpc. Illustrative (S106)." },
  { key: "inner", label: "skeleton: inner-edge bias", min: -1, max: 2, step: 0.01, unit: "widths", default: 0.35, about: "The regions set this many ridge widths (FWHM) to the ridge's inner side, the dust lane's (negative: outer). Illustrative (S106)." },
  { key: "across", label: "skeleton: scatter across", min: 0, max: 1.5, step: 0.01, unit: "widths", default: 0.15, perTemplate: { milky_way: 0.4 }, about: "The regions scattered across the arm by a Gaussian of this many ridge widths. Illustrative (S106)." },
  { key: "ridgePow", label: "skeleton: ridge-strength power", min: 0, max: 6, step: 0.1, unit: "power", default: 1.5, perTemplate: { milky_way: 2.5 }, about: "A bunch is kept with the ridge's strength to this power: denser where the ridge is strong. Illustrative (S106)." },
  { key: "slope", label: "skeleton: size spread", min: 0.3, max: 4, step: 0.05, unit: "slope", default: 1, perTemplate: { milky_way: 1.8 }, about: "Radii drawn as floor u^(-1/slope) up to the ceiling: lower, more large regions; higher, nearly all at the floor. Illustrative (S106)." },
  { key: "lightSize", label: "skeleton: light with size", min: 0, max: 3, step: 0.05, unit: "power", default: 1, about: "A region's light as (radius / floor)^power: the large complexes the bright ones. Illustrative (S106)." },
  { key: "barEnds", label: "skeleton: bar-end complexes", min: 0, max: 20, step: 0.1, unit: "×", default: 8, about: "A bright complex at each bar end (the major arms' starts), its members this many times a region's light; 0 none. Illustrative (S106)." },
  { key: "elong", label: "skeleton: along the arm", min: 1, max: 6, step: 0.05, unit: "×", default: 2.5, perTemplate: { milky_way: 3.5 }, about: "Each region's lobes spread this many times further along the arm than across it. Illustrative (S106)." },
  { key: "hue", label: "skeleton: lobes' hue spread", min: 0, max: 1.5, step: 0.01, unit: "", default: 0.5, about: "The lobes' hues spread this far about the pink-to-magenta setting (each lobe its own). Colour for appearance (S106)." },
  { key: "coreBlue", label: "core: white to blue", min: 0, max: 1, step: 0.01, unit: "", default: 1, perTemplate: { milky_way: 0 }, about: "The skeleton regions' cores from white (0) to the knots' white-blue (1). Colour for appearance (S106)." },
  { key: "sparkle", label: "skeleton: blue-white points", min: 0, max: 8, step: 1, default: 3, about: "Up to this many blue-white points beside each larger region (fewer for small ones). Illustrative (S106)." },
  { key: "sparkleGain", label: "skeleton: points' light", min: 0, max: 2, step: 0.01, unit: "×", default: 0.15, about: "Each blue-white point's light against its region's. Illustrative (S106)." },
  { key: "minStrength", label: "skeleton: least ridge", min: 0, max: 1, step: 0.01, default: 0, perTemplate: { milky_way: 0.25 }, about: "No bunch of regions where the ridge's strength is under this (a faded arm end); 0 anywhere on a ridge. Illustrative (S107)." },
  { key: "patchPow", label: "skeleton: on the bright stretches", min: 0, max: 6, step: 0.1, unit: "power", default: 0, perTemplate: { milky_way: 1 }, about: "A bunch kept with the arm's clumps (the arms' patchy arms) to this power: the regions gather in the arms' bright stretches, with long empty ones between; 0 as the ridge's strength alone. Illustrative (S107)." },
  { key: "complexes", label: "skeleton: large complexes", min: 0, max: 40, step: 1, default: 0, perTemplate: { milky_way: 12 }, about: "This many large ragged complexes (several lobes, a white core, bright points about them) along the two major arms; 0 none. Illustrative (S107)." },
  { key: "complexGain", label: "skeleton: complexes' light", min: 0, max: 20, step: 0.1, unit: "×", default: 3, perTemplate: { milky_way: 5 }, about: "A large complex's members' light, times a region's. Illustrative (S107)." },
  // S107 (MW2): the large complexes made to read at full frame, ragged lobes, the spurs' regions on their crests.
  { key: "complexMembers", label: "skeleton: complexes' members", min: 0.5, max: 4, step: 0.05, unit: "×", default: 1, perTemplate: { milky_way: 1.2 }, about: "A large complex's (and a bar end's) members, times as many as before. Illustrative (S107)." },
  { key: "complexSpread", label: "skeleton: complexes' length", min: 0.5, max: 6, step: 0.05, unit: "×", default: 1, perTemplate: { milky_way: 1.0 }, about: "A large complex's members spread this many times the bunch length along the arm: an elongated complex. Illustrative (S107)." },
  { key: "satellites", label: "skeleton: complexes' satellites", min: 0, max: 20, step: 1, default: 0, perTemplate: { milky_way: 4 }, about: "This many tiny regions scattered about each large complex (and bar end), just beyond its members; 0 none. Illustrative (S107)." },
  { key: "halo", label: "skeleton: complexes' halo", min: 0, max: 3, step: 0.01, unit: "×", default: 0, perTemplate: { milky_way: 0 }, about: "A soft pink envelope along the arm round each large complex (and bar end), its light this share of the complex's largest member; 0 none. Illustrative (S107)." },
  { key: "haloSize", label: "skeleton: halo size", min: 0.5, max: 10, step: 0.1, unit: "×", default: 3, perTemplate: { milky_way: 2 }, about: "The halo's radius, times the regions' radius ceiling. Illustrative (S107)." },
  { key: "ragged", label: "ragged lobes", min: 0, max: 2, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1.6 }, about: "On the skeleton's regions, each lobe's light broken by a fixed noise at a few cells per region radius by this share: ragged outlines, wisps and holes; 0 smooth lobes. Illustrative (S107)." },
  { key: "spurCrest", label: "skeleton: spurs' regions on the crest", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1 }, about: "The regions on a spur drawn onto its crest by this share (0: set to the inner side and scattered as on an arm, so they sit off the short spur). Illustrative (S107)." },
  { key: "seed", label: "skeleton: seed", min: 1, max: 99, step: 1, default: 7, about: "The placement's fixed seed (the viewer's own). Illustrative (S106)." },
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
