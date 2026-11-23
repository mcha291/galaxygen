// The flocculent network (BUILD_VIII row 109, S109, D275): what makes a smooth disc read as HST's NGC 4414 - a network
// of short brown dust filaments winding at the spiral's pitch over the whole disc, the light between them broken into
// patches, white-blue clumps and short fragments of young stars outside, and a warm cream inner disc. ILLUSTRATIVE: the
// model's flocculent pieces are fifteen smooth ridges a kiloparsec and a half wide and its clouds isolated flecks, so no
// published field draws a filament or a patch; this feature draws them itself (flocMap.ts), placed by published
// numbers - the pitch, the gas's radial profile and contrast, the stars' contrast - and shaped by a seeded drawing of
// the viewer's own, fixed in the galaxy's frame.
//
// What it hands the march: ONE byte a texel of the look's shared map (flocMap.ts: the lanes' grid, the dust and the
// light signed about 128 - the march's fragment has no sampler to spare for a map of its own), built once per arrays
// frame and per shaping value, read three ways:
//   dustAv     the share of the depth that is not ink, as face-on A_V in the dust's own layer. The march composes it
//              front to back with the stars and the bulge, so the dust reads darker on the disc's near side (more of
//              the light lies behind it there) - the photograph's asymmetry, by the march's own arithmetic. In that
//              thin layer a filament is smeared along the view by the layer's height and dims at most the light behind
//              it, so it reads as a soft grey shadow: the broad darkening.
//   veil       the ink (the rest of the depth, a screen over the ray's whole light with the grains' reddening
//              steepened: the sharp brown threads, as the lanes'), times the patches (the light swelled and thinned
//              about its mean), times the clumps (a white-blue brightening), times the warmth (a cream tint over the
//              inner disc). The veil is the one multiplier on all of a ray's light the contract has; it may exceed 1.
//   youngGain  the clumps again, as a multiplier on the model's own clustered young light: its blue flecks gathered
//              into the clumps.
// Every depth, gain and colour is a uniform: no rebuild.
//
// S106 third pass (C4), the plane style only: NGC 4414's dust drawn as a MESH in this GLSL, per ray in the veil (no
// map, no rebuild; illFlocMeshShape): filaments on the edges of cellular (Worley) cells drawn out along the spiral, so
// they fork, cross and join at angles; a share of the edges left out (open ends, branches), each edge its own width,
// dark clumps where three meet, a finer mesh on it and a broader soft one, gathered on short flocculent arcs of a
// spiral value noise with a mottled smoke over them; and the light between in puffs of many strengths (Worley hearts),
// stronger beside the drawn dust, blue-white outside. ILLUSTRATIVE, display-only structure of the viewer's own (the
// lead's ruling 12: the goal shows a tangled branching mesh of dust and no published field draws one); its amount
// follows the plane style's ring, near-side bias and the drawn pitch. The map's threads (flocNet.ts) stay as a slider
// (netDepth), off for NGC 4414.

import { createElement, lazy, Suspense } from "react";
import { ILL_MAP_CHANNELS, type IllControl, type IllFeature, type IllFrame, type IllLayerProps, type IllParams, memoOn } from "./feature";
import { type CloudShape, cloudsOf } from "./flocClouds";
import { FLOC_ARRAYS, FLOC_MAP, type FlocShape, SHAPE_KEYS, buildFlocChannel, geometryOf } from "./flocMap";
import { buildNetChannel } from "./flocNet";

const CONTROLS: readonly IllControl[] = [
  {
    key: "depth", label: "network depth", min: 0, max: 10, step: 0.05, unit: "mag", default: 0, perTemplate: { milky_way: 0, ngc_4414: 2 },
    about: "The depth at the centre of one full filament of the dust network, magnitudes of A_V; 0 no network. Illustrative.",
  },
  {
    key: "ink", label: "network ink", min: 0, max: 1, step: 0.01, unit: "", default: 0.75, perTemplate: { ngc_4414: 1 },
    about: "The share of the depth drawn as a veil over all the light on its line of sight (sharp brown threads, the same on both sides of the disc); the rest is dust in the dust's own thin layer, which the march makes darker on the near side. Illustrative.",
  },
  { key: "redness", label: "network redness", min: 0, max: 4, step: 0.05, unit: "×", default: 1.5, perTemplate: { ngc_4414: 1.3 }, about: "The veil's colour: 0 a grey veil, 1 the dust grains' own reddening, higher a redder brown. Colour for appearance." },
  { key: "hardness", label: "filament edge", min: 0, max: 1, step: 0.01, unit: "", default: 0.3, perTemplate: { ngc_4414: 0 }, about: "How crisp a filament's edge is: 0 a soft stroke, 1 an inked one with its faint margins gone. Illustrative." },
  {
    key: "patch", label: "patch contrast", min: 0, max: 2, step: 0.01, unit: "×", default: 0, perTemplate: { milky_way: 0, ngc_4414: 0.8 },
    about: "How far the disc's light swells and thins in soft patches about its mean (a multiplier on all the light at each place); 0 a smooth disc. Illustrative.",
  },
  {
    key: "clump", label: "clump glow", min: 0, max: 8, step: 0.05, unit: "×", default: 0, perTemplate: { milky_way: 0, ngc_4414: 3 },
    about: "How much brighter all the light is at the centre of a young clump (a multiplier of 1 plus this, in the clump tint); 0 none. Illustrative.",
  },
  {
    key: "young", label: "clump young light", min: 0, max: 30, step: 0.1, unit: "×", default: 0, perTemplate: { milky_way: 0, ngc_4414: 2 },
    about: "How much more of the model's own clustered young light a clump holds (1 plus this at its centre): its blue flecks gathered into the clumps. Read only while the young light is clustered in the march. Illustrative.",
  },
  { key: "blue", label: "clump tint", min: 0, max: 1, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 0.6 }, about: "The clump glow's colour: 0 the light's own, 1 a blue-white. Colour for appearance." },
  {
    key: "warmth", label: "inner warmth", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 0.35 },
    about: "A cream tint over the inner disc's light, fading outward: the old disc of the photograph. Colour for appearance.",
  },
  { key: "warmRadius", label: "warmth radius", min: 0.5, max: 15, step: 0.1, unit: "kpc", default: 4.5, perTemplate: { ngc_4414: 3 }, about: "The radius at which the warm tint has fallen to 1/e, kpc. Colour for appearance." },
  { key: "density", label: "filaments", min: 0, max: 12, step: 0.05, unit: "/kpc²", default: 0.5, perTemplate: { ngc_4414: 4 }, about: "Trunk filaments per square kiloparsec where the gas is at its mean (branches and bands come with them). Illustrative." },
  { key: "length", label: "filament length", min: 0.2, max: 5, step: 0.05, unit: "kpc", default: 1.4, about: "A trunk's typical length, kpc (each between 0.45 and 1.75 of it): a short piece of a turn. Illustrative." },
  { key: "width", label: "filament width", min: 30, max: 400, step: 5, unit: "pc", default: 55, perTemplate: { ngc_4414: 40 }, about: "A filament's typical full width at half depth, parsecs (each between 0.6 and 2.2 of it, most thin). Illustrative." },
  { key: "pitch", label: "pitch", min: 0.2, max: 2, step: 0.01, unit: "×", default: 1, perTemplate: { ngc_4414: 0.75 }, about: "The filaments' pitch as a share of the galaxy's published pitch angle. Illustrative." },
  { key: "pitchSpread", label: "pitch spread", min: 0, max: 30, step: 0.5, unit: "°", default: 8, about: "The spread of the trunks' own pitches about it, degrees. Illustrative." },
  { key: "wiggle", label: "wiggle", min: 0, max: 45, step: 0.5, unit: "°", default: 24, about: "How far a filament's heading wanders along its length, degrees. Illustrative." },
  { key: "branches", label: "branches", min: 0, max: 6, step: 0.1, unit: "", default: 1.5, perTemplate: { ngc_4414: 3 }, about: "Branches per trunk of typical length (each carries half as many twigs): the network's forks and cross-links. Illustrative." },
  { key: "branchAngle", label: "branch angle", min: 0, max: 80, step: 1, unit: "°", default: 40, about: "The angle a branch leaves its filament at, degrees (each between half and one and a half of it); it turns back to the spiral along its length. Illustrative." },
  { key: "bands", label: "wide bands", min: 0, max: 2, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.3 }, about: "Short wide bands per trunk: the thick mottled strands. Illustrative." },
  { key: "bandWidth", label: "band width", min: 100, max: 900, step: 10, unit: "pc", default: 320, about: "A band's full width at half depth, parsecs (each between 0.6 and 1.4 of it). Illustrative." },
  { key: "swell", label: "knots", min: 0, max: 1, step: 0.01, unit: "", default: 0.7, about: "How much a filament swells into dark knots and thins to threads along its length. Illustrative." },
  { key: "mottle", label: "mottle", min: 0, max: 1, step: 0.01, unit: "", default: 0.7, about: "How much the dust's depth swells and thins from place to place: a band broken into blotches and holes. Illustrative." },
  { key: "grain", label: "mottle grain", min: 20, max: 600, step: 5, unit: "pc", default: 90, about: "The size of the mottle's patches, parsecs (a finer set a third of it rides on them). Illustrative." },
  { key: "gather", label: "bundling", min: 0, max: 1, step: 0.01, unit: "", default: 0.8, perTemplate: { ngc_4414: 0.4 }, about: "How far the filaments gather into bundles along spiral pieces of the viewer's own: 0 spread evenly. Illustrative." },
  { key: "bundle", label: "bundle width", min: 150, max: 3000, step: 10, unit: "pc", default: 500, about: "The width across the spiral of the bundles the dust gathers into, parsecs (each about four times as long). Illustrative." },
  { key: "followGas", label: "follows the gas", min: 0, max: 1, step: 0.01, unit: "", default: 0.3, perTemplate: { ngc_4414: 0.1 }, about: "How far the filaments' number follows the published gas contrast: 0 the same everywhere, 1 none where the gas is thin. Illustrative." },
  { key: "radial", label: "radial fall", min: 0, max: 2, step: 0.01, unit: "power", default: 1.1, about: "The filaments' number follows the published gas surface density's radial profile to this power: 0 the same at every radius. Illustrative." },
  { key: "innerRadius", label: "inner radius", min: 0, max: 8, step: 0.05, unit: "kpc", default: 0.5, about: "The network fades to nothing inside this radius, kpc. Illustrative." },
  { key: "outerRadius", label: "outer radius", min: 2, max: 23, step: 0.5, unit: "kpc", default: 9, perTemplate: { ngc_4414: 11 }, about: "The network fades from 0.7 of this radius to nothing at it, kpc; the patches and clumps reach 1.3 of it. Illustrative." },
  { key: "patchSize", label: "patch size", min: 60, max: 900, step: 10, unit: "pc", default: 260, about: "A light patch's size, parsecs (each between 0.55 and 1.45 of it, in irregular threes along the spiral). Illustrative." },
  { key: "clumpDensity", label: "clump strings", min: 0, max: 4, step: 0.01, unit: "/kpc²", default: 0.8, perTemplate: { ngc_4414: 1.5 }, about: "Strings of young clumps per square kiloparsec on the flocculent pieces (each two to seven clumps along the spiral). Illustrative." },
  { key: "clumpSize", label: "clump size", min: 40, max: 600, step: 5, unit: "pc", default: 120, perTemplate: { ngc_4414: 50 }, about: "A young clump's size, parsecs (each between 0.45 and 1.25 of it). Illustrative." },
  { key: "clumpInner", label: "clumps from", min: 0, max: 15, step: 0.1, unit: "kpc", default: 3, about: "The clumps come in over this radius, kpc: the inner disc is old light. Illustrative." },
  { key: "clumpFollow", label: "clumps on the pieces", min: 0, max: 1, step: 0.01, unit: "", default: 0.85, perTemplate: { ngc_4414: 0 }, about: "How far the clumps keep to the published stars' contrast (the flocculent pieces): 0 anywhere. Illustrative." },
  { key: "lace", label: "lace depth", min: 0, max: 3, step: 0.01, unit: "×", default: 1.5, perTemplate: { ngc_4414: 1.3 }, about: "The lace - the fine network of threads that close into cells between the filaments - its depth as a share of a filament's; 0 none. Illustrative." },
  { key: "cell", label: "lace cell", min: 80, max: 1500, step: 10, unit: "pc", default: 160, perTemplate: { ngc_4414: 120 }, about: "The size of the lace's cells across the spiral, parsecs (within a fifth, by radius). Illustrative." },
  { key: "thread", label: "lace thread", min: 0.02, max: 1, step: 0.01, unit: "", default: 0.16, about: "How thick the lace's threads are, as a share of a cell (thicker where the filaments gather, running together into blotches). Illustrative." },
  { key: "stretch", label: "lace stretch", min: 0.5, max: 6, step: 0.1, unit: "×", default: 3.2, perTemplate: { ngc_4414: 5 }, about: "How many times longer along the spiral than across it a cell of the lace is. Illustrative." },
  { key: "blotch", label: "lace blotches", min: 0, max: 1, step: 0.01, unit: "", default: 0.3, about: "How far the lace's threads thicken and run together into mottled blotches where the dust gathers; 0 threads only. Illustrative." },
  { key: "seed", label: "network seed", min: 0, max: 999, step: 1, unit: "", default: 11, about: "The seed of the drawing: another number, another network of the same kind. Illustrative." },
  // S106 (builders C, C3): the network drawn in the disc's plane (flocNet.ts) - thin dust threads strung into many narrow spiral arcs, cream clouds between.
  {
    key: "style", label: "network style", min: 0, max: 1, step: 1, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 1 },
    about: "0: S105's strands and lace on spiral lattices; 1: S106's network drawn in the disc's plane - thin feathered dust threads strung into many narrow spiral arcs, and grainy cream clouds of light between them. Illustrative.",
  },
  { key: "netScale", label: "dust piece size", min: 60, max: 1500, step: 10, unit: "pc", default: 350, perTemplate: { ngc_4414: 350 }, about: "The plane style: the size of the noise that cuts the threads into pieces, parsecs (a piece is about this long). Illustrative." },
  { key: "netWarp", label: "dust wiggle", min: 0, max: 3, step: 0.01, unit: "×", default: 0.8, perTemplate: { ngc_4414: 0.7 }, about: "How far the plane is pushed about before the threads are drawn, as a share of their spacing: a thread wanders (much above 1, it curls). Illustrative." },
  { key: "netGaps", label: "dust gaps", min: 0, max: 1, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 0.42 }, about: "The level of the pieces' noise under which a thread is broken: higher, shorter pieces and wider gaps. Illustrative." },
  { key: "netSoft", label: "dust softness", min: 0.01, max: 0.5, step: 0.01, unit: "", default: 0.12, perTemplate: { ngc_4414: 0.1 }, about: "How softly a piece's ends fade out. Illustrative." },
  { key: "netFeather", label: "dust feathers", min: 0, max: 1, step: 0.01, unit: "", default: 0.7, perTemplate: { ngc_4414: 0.6 }, about: "How far a thread's width swells into knots and thins to hairs along it; 0 an even width. Illustrative." },
  { key: "netArc", label: "dust on arcs", min: 0, max: 1, step: 0.01, unit: "", default: 0.6, perTemplate: { ngc_4414: 0.75 }, about: "How far the threads gather into broad arcs on the drawn spiral (lighter disc between); 0 even. Illustrative." },
  { key: "arcWidth", label: "arc width", min: 100, max: 3000, step: 10, unit: "pc", default: 500, perTemplate: { ngc_4414: 400 }, about: "A broad arc's width across the spiral, parsecs. Illustrative." },
  { key: "arcStretch", label: "arc length", min: 0.5, max: 10, step: 0.1, unit: "×", default: 3, perTemplate: { ngc_4414: 5 }, about: "A broad arc's length along the spiral over its width. Illustrative." },
  { key: "netDepth", label: "dust drawn", min: 0, max: 4, step: 0.01, unit: "×", default: 1.6, perTemplate: { ngc_4414: 0 }, about: "The plane style's drawn depth, in full filaments (the network depth scales it again, without a rebuild). Illustrative." },
  // S106 second pass (C3): the plane style's threads and the dust's amount by place.
  { key: "filSpacing", label: "thread spacing", min: 40, max: 1500, step: 5, unit: "pc", default: 220, perTemplate: { ngc_4414: 200 }, about: "The plane style: the spacing of the dust threads across the spiral, parsecs (the finer wisps at half of it). Illustrative." },
  { key: "filRun", label: "thread run", min: 1, max: 30, step: 0.1, unit: "×", default: 8, perTemplate: { ngc_4414: 6 }, about: "How many times longer along the spiral than their spacing the threads' noise cells are: longer, straighter arcs. Illustrative." },
  { key: "wisps", label: "wisps", min: 0, max: 1.5, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 1 }, about: "The finer wisps between the threads, as a share of a thread's depth; 0 none. Illustrative." },
  { key: "haze", label: "dust haze", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.08 }, about: "The plane style: a smooth brown haze where the threads gather (the smoky lanes they lie in), as a share of a thread's depth; 0 threads only. Illustrative." },
  { key: "ringIn", label: "dust ring from", min: 0, max: 1, step: 0.01, unit: "× outer", default: 0.25, perTemplate: { ngc_4414: 0.12 }, about: "The dust comes in to its full amount at this share of the network's outer radius (the nuclear region inside holds the nuclear dust's share of it). Illustrative." },
  { key: "ringOut", label: "dust ring to", min: 0, max: 1, step: 0.01, unit: "× outer", default: 0.7, perTemplate: { ngc_4414: 0.5 }, about: "The dust thins from this share of the outer radius to the outer dust's share of its amount near the edge. Illustrative." },
  { key: "core", label: "nuclear dust", min: 0, max: 1, step: 0.01, unit: "", default: 0.15, perTemplate: { ngc_4414: 0.4 }, about: "The dust's amount in the nuclear region, as a share of the ring's. Illustrative." },
  { key: "rim", label: "outer dust", min: 0, max: 1, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 0 }, about: "The dust's amount in the outer disc, as a share of the ring's. Illustrative." },
  { key: "nearBias", label: "near-side dust", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.3 }, about: "How much more dust lies toward the near-side azimuth (and less opposite): 1 twice the mean there, none opposite. Illustrative." },
  { key: "nearAz", label: "near-side azimuth", min: 0, max: 360, step: 1, unit: "°", default: 0, perTemplate: { ngc_4414: 300 }, about: "The galactocentric azimuth of the most dust, degrees. Illustrative." },
  { key: "litScale", label: "light cloud size", min: 40, max: 1500, step: 10, unit: "pc", default: 220, perTemplate: { ngc_4414: 120 }, about: "The size of the cream clouds of light between the dust, parsecs. Illustrative." },
  { key: "litKnots", label: "bright grains", min: 0, max: 3, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 2 }, about: "How bright the brightest of the light's grains are (the grain's peaks, in the clump tint). Illustrative." },
  { key: "litReach", label: "light reach", min: 1, max: 3, step: 0.05, unit: "× outer", default: 1.7, perTemplate: { ngc_4414: 1.3 }, about: "How far the plane style's clouds of light reach, as a multiple of the network's outer radius. Illustrative." },
  // S106 second pass (C3): the light's grain and its radial colour, drawn in the march (no rebuild).
  { key: "litGrain", label: "light grain", min: 0, max: 3, step: 0.01, unit: "×", default: 0, perTemplate: { milky_way: 0, ngc_4414: 1.6 }, about: "The plane style: how far the starlight between the dust is broken into small bright puffs (a multiplier about 1); 0 smooth. Illustrative." },
  { key: "litGrainSize", label: "grain size", min: 10, max: 300, step: 1, unit: "pc", default: 40, perTemplate: { ngc_4414: 12 }, about: "A puff of the light's grain, parsecs (a finer one at under half of it rides on it). Illustrative." },
  { key: "litGrainNear", label: "grain by the dust", min: 0, max: 5, step: 0.05, unit: "×", default: 1.5, perTemplate: { ngc_4414: 0 }, about: "How much stronger the grain is just outside a dust thread (the young light along the arcs). Illustrative." },
  { key: "cool", label: "outer blue", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 0 }, about: "The plane style: a blue-white tint over the outer disc's light, from the outer blue's radius outward (warm cream inside). Colour for appearance." },
  { key: "coolRadius", label: "outer blue from", min: 0.5, max: 20, step: 0.1, unit: "kpc", default: 5, about: "The tint is none at 0.7 of this radius and full at 1.5 of it, kpc. Colour for appearance." },
  {
    key: "cap", label: "dust ceiling", min: 0.1, max: 20, step: 0.05, unit: "mag", default: 20, perTemplate: { ngc_4414: 2.2 },
    about: "The veil's depth saturates softly toward this many magnitudes: the thickest dust stays a deep red-brown, never black. Colour for appearance.",
  },
  {
    key: "nucleus", label: "nucleus cream", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 0 },
    about: "A cream-yellow tint over the nucleus's light (its march draws a blue-cyan core under the stretch): 0 none, 1 full. Colour for appearance.",
  },
  // S106: the star clouds (flocClouds.ts, FlocClouds.tsx), a points layer of the feature's own, drawn in the plane style.
  {
    key: "cloudCount", label: "star cloud points", min: 0, max: 80000, step: 500, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 26000 },
    about: "How many points the star clouds hold (in the plane style only): loose groups over the bright light between the dust, densest in the outer disc; 0 none. Illustrative.",
  },
  { key: "cloudGain", label: "star cloud brightness", min: 10, max: 1e7, step: 0.01, log: true, unit: "L☉", default: 3000, perTemplate: { ngc_4414: 35000 }, about: "The faintest star cloud point's light, L☉ over the white point (the field's scale, with the exposure). Illustrative." },
  { key: "cloudRange", label: "star cloud range", min: 1, max: 1000, step: 0.01, log: true, unit: "×", default: 20, about: "The brightest star cloud point over the faintest. Illustrative." },
  { key: "cloudSlope", label: "star cloud slope", min: 0.3, max: 4, step: 0.05, unit: "", default: 1.3, about: "The brightness law's index: smaller, more bright points. Illustrative." },
  { key: "cloudSize", label: "star cloud point size", min: 0.5, max: 4, step: 0.1, unit: "px", default: 1.5, perTemplate: { ngc_4414: 2.2 }, about: "A star cloud point's sprite, pixels. Illustrative." },
  { key: "cloudGroup", label: "star cloud size", min: 10, max: 800, step: 5, unit: "pc", default: 120, perTemplate: { ngc_4414: 90 }, about: "A star cloud's gaussian radius, parsecs (each between half and one and a half of it). Illustrative." },
  { key: "cloudMembers", label: "star cloud members", min: 1, max: 60, step: 1, unit: "", default: 8, perTemplate: { ngc_4414: 18 }, about: "A star cloud's mean number of points. Illustrative." },
  { key: "cloudStart", label: "star clouds from", min: 0, max: 2, step: 0.01, unit: "× outer", default: 0.7, perTemplate: { ngc_4414: 0.35 }, about: "Where the star clouds come in to their full number, as a multiple of the network's outer radius (a quarter of it inside). Illustrative." },
  { key: "cloudReach", label: "star cloud reach", min: 0.5, max: 3, step: 0.01, unit: "× outer", default: 1.5, perTemplate: { ngc_4414: 0.78 }, about: "How far the star clouds reach, as a multiple of the network's outer radius, the edge pushed in and out by a noise: a ragged rim. Illustrative." },
  { key: "cloudBlue", label: "star cloud blue", min: 0, max: 1.5, step: 0.01, unit: "", default: 1, perTemplate: { ngc_4414: 0.5 }, about: "How far the outer clouds' colour goes from cream to blue-white. Colour for appearance." },
  { key: "cloudWarmR", label: "star cloud cream radius", min: 0.5, max: 20, step: 0.1, unit: "kpc", default: 5, about: "The clouds are cream inside 0.6 of this radius and blue-white outside 1.6 of it, kpc. Colour for appearance." },
  { key: "cloudRich", label: "star cloud sectors", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.5 }, about: "How far the star clouds keep to two or three rich stretches about the star cloud azimuth; 0 all round. Illustrative." },
  { key: "cloudAz", label: "star cloud azimuth", min: 0, max: 360, step: 1, unit: "°", default: 0, perTemplate: { ngc_4414: 320 }, about: "The galactocentric azimuth of the richest star clouds, degrees. Illustrative." },
  { key: "cloudGlow", label: "star cloud glow", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 1 }, about: "A soft glow under each star cloud's group (the map's clump level: the clump glow's gain and tint); 0 none. Illustrative." },
  { key: "cloudComplex", label: "star cloud complexes", min: 0, max: 0.5, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.12 }, about: "The share of the star clouds that are large complexes: four times the points over a wider glow. Illustrative." },
  { key: "nucleusRadius", label: "nucleus radius", min: 0.05, max: 5, step: 0.01, unit: "kpc", default: 0.8, about: "The radius at which the nucleus's tint has fallen to 1/e, kpc. Colour for appearance." },
  // S106 third pass (C4): the plane style's dust as a tangled mesh of many widths - broad soft lanes carrying feathers and
  // spurs, threads that diverge and merge, wisps, tapered ends.
  { key: "laneDepth", label: "broad lanes", min: 0, max: 3, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0 }, about: "The plane style: the depth of the broad soft dust lanes in short flocculent arcs, in full threads; 0 none. Illustrative." },
  { key: "laneWidth", label: "lane width", min: 60, max: 800, step: 5, unit: "pc", default: 250, about: "A broad lane's full width at half depth, parsecs. Illustrative." },
  { key: "laneSpacing", label: "lane spacing", min: 300, max: 4000, step: 10, unit: "pc", default: 1200, about: "The broad lanes' spacing across the spiral, parsecs. Illustrative." },
  { key: "laneRun", label: "lane run", min: 1, max: 12, step: 0.1, unit: "×", default: 3, about: "How many times longer along the spiral than their spacing the broad lanes' noise cells are. Illustrative." },
  { key: "feathers", label: "feathers on lanes", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0 }, about: "How far the threads and wisps gather along the broad lanes' sides (the feathers a lane carries); 0 everywhere alike. Illustrative." },
  { key: "spurs", label: "spurs", min: 0, max: 2, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0 }, about: "Short threads leaving the lanes and threads at an angle to the spiral, as a share of a thread's depth; 0 none. Illustrative." },
  { key: "spurAngle", label: "spur angle", min: 10, max: 80, step: 1, unit: "°", default: 40, about: "The spurs' angle to the spiral, degrees. Illustrative." },
  { key: "tangle", label: "tangle", min: 0, max: 3, step: 0.01, unit: "×", default: 0, perTemplate: { ngc_4414: 0 }, about: "How far the threads' plane is pushed about (exactly, over a few spacings), as a share of their spacing: the threads diverge, cross and merge; 0 none. Illustrative." },
  { key: "wispWidth", label: "wisp width", min: 0.1, max: 2, step: 0.01, unit: "×", default: 0.75, about: "The wisps' width as a share of a thread's. Illustrative." },
  { key: "wispRun", label: "wisp run", min: 0.1, max: 2, step: 0.01, unit: "×", default: 0.7, about: "The wisps' run as a share of the threads'. Illustrative." },
  { key: "meshDepth", label: "dust mesh", min: 0, max: 3, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 2.8 }, about: "The plane style: the depth of a tangled mesh of dust filaments on the edges of cells stretched along the spiral (they fork and join at angles), in full threads; 0 none. Illustrative." },
  { key: "meshCell", label: "mesh cell", min: 60, max: 2000, step: 10, unit: "pc", default: 300, perTemplate: { ngc_4414: 220 }, about: "A mesh cell's size across the spiral, parsecs: the cream light between the filaments. Illustrative." },
  { key: "meshWidth", label: "mesh filament", min: 10, max: 300, step: 1, unit: "pc", default: 40, perTemplate: { ngc_4414: 22 }, about: "A mesh filament's typical full width at half depth, parsecs (each edge between half and 1.7 of it). Illustrative." },
  { key: "meshStretch", label: "mesh stretch", min: 1, max: 2.5, step: 0.05, unit: "×", default: 1.8, about: "How many times longer along the spiral than across a mesh cell is. Illustrative." },
  { key: "meshOpen", label: "mesh open", min: 0, max: 0.95, step: 0.01, unit: "", default: 0.35, perTemplate: { ngc_4414: 0.45 }, about: "The share of the mesh's edges left out: an open, branching mesh with loose ends. Illustrative." },
  { key: "meshFine", label: "fine mesh", min: 0, max: 2, step: 0.01, unit: "", default: 0.6, perTemplate: { ngc_4414: 1.0 }, about: "A finer mesh (cells and filaments at half the size) as a share of the mesh's depth. Illustrative." },
  { key: "meshKnot", label: "mesh knots", min: 0, max: 3, step: 0.01, unit: "", default: 0.8, about: "The dark clumps where three of the mesh's edges meet, as a share of a filament's depth. Illustrative." },
  { key: "meshBroad", label: "broad mesh", min: 0, max: 2, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 1.0 }, about: "A coarser mesh (cells twice the size, soft filaments two and a half times as wide) as a share of the mesh's depth: the broad lanes. Illustrative." },
  { key: "meshFollow", label: "mesh on the dust", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0 }, about: "How far the mesh gathers where the drawn dust is (the map's threads and lanes within 150 pc); 0 alike everywhere. Illustrative." },
  { key: "puffs", label: "light puffs", min: 0, max: 3, step: 0.01, unit: "×", default: 0, perTemplate: { ngc_4414: 0.5 }, about: "The plane style: how far the light between the dust gathers into puffs a few hundred parsecs across (a multiplier about 1, brightest at a puff's heart); 0 none. Illustrative." },
  { key: "puffSize", label: "puff size", min: 40, max: 1000, step: 5, unit: "pc", default: 220, about: "A light puff's size, parsecs (a finer set at under half of it rides on them). Illustrative." },
  { key: "puffNear", label: "puffs by the dust", min: 0, max: 4, step: 0.05, unit: "×", default: 1, about: "How much stronger the puffs are where dust lies within 150 parsecs. Illustrative." },
  { key: "puffBlue", label: "outer puffs blue", min: 0, max: 1.5, step: 0.01, unit: "", default: 0.8, perTemplate: { ngc_4414: 0 }, about: "How far the puffs turn blue-white in the outer disc (from the outer blue's radius). Colour for appearance." },
  { key: "meshArc", label: "mesh on arcs", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0 }, about: "How far the mesh gathers into short flocculent arcs on the spiral (cream disc between); 0 even. Illustrative." },
  { key: "meshArcWidth", label: "mesh arc width", min: 200, max: 4000, step: 10, unit: "pc", default: 900, perTemplate: { ngc_4414: 600 }, about: "A mesh arc's width across the spiral at half the network's outer radius, parsecs (in proportion to the radius). Illustrative." },
  { key: "meshArcRun", label: "mesh arc length", min: 1, max: 12, step: 0.1, unit: "×", default: 3, perTemplate: { ngc_4414: 4 }, about: "A mesh arc's length along the spiral over its width. Illustrative." },
  { key: "meshHaze", label: "lane smoke", min: 0, max: 2, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.4 }, about: "A soft mottled brown smoke over the mesh's arcs (the broad lanes the filaments lie in), in full threads; 0 none. Illustrative." },
  { key: "meshPiece", label: "mesh patches", min: 100, max: 5000, step: 10, unit: "pc", default: 1200, about: "The size of the noise that breaks the mesh into patches with clear disc between, parsecs. Illustrative." },
  { key: "meshGaps", label: "mesh gaps", min: 0, max: 1, step: 0.01, unit: "", default: 0.4, perTemplate: { ngc_4414: 0.35 }, about: "The level of the patches' noise under which the mesh is left out: higher, more clear disc. Illustrative." },
  { key: "meshWarp", label: "mesh wiggle", min: 0, max: 1.5, step: 0.01, unit: "×", default: 0.4, about: "How far the mesh's plane is pushed about, as a share of a cell: its filaments bend. Illustrative." },
  { key: "taper", label: "taper", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0 }, about: "How far a thread thins toward the ends of its piece; 0 an even width to the end. Illustrative." },
  // S107 (builder NGC): ALL the plane style's dust - the map's threads and the march's mesh alike - gathered on the mesh's
  // arcs (one field), with clear zones of starlight between them; drawn in the march (no rebuild).
  { key: "arcGate", label: "dust gathered on arcs", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 1 }, about: "The plane style: how far all the drawn dust (threads and mesh alike) keeps to the mesh's arcs, clear starlight between; 0 as drawn. Illustrative." },
  { key: "arcClear", label: "dust between arcs", min: 0, max: 1, step: 0.01, unit: "", default: 0.1, perTemplate: { ngc_4414: 0.02 }, about: "The share of the drawn dust left in the clear zones between the arcs (faint wisps). Illustrative." },
  { key: "arcLevel", label: "arc share", min: 0, max: 1, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 0.6 }, about: "The level of the arcs' noise above which the dust is kept: higher, narrower arcs and broader clear zones. Illustrative." },
  { key: "grainDim", label: "grain shade", min: 0, max: 1, step: 0.01, unit: "", default: 1, perTemplate: { ngc_4414: 0 }, about: "How far the light's grain dims the light between its puffs: 1 as drawn (bright and dark), 0 bright points only. Illustrative." },
  { key: "puffDim", label: "puff shade", min: 0, max: 1, step: 0.01, unit: "", default: 1, perTemplate: { ngc_4414: 0.3 }, about: "How far the light's puffs dim the light between them: 1 as drawn, 0 brightening only. Illustrative." },
  { key: "clearFloor", label: "clear zone floor", min: 0, max: 1, step: 0.01, unit: "", default: 0.45, about: "Where the arcs' gate takes the dust away, the light's patches are held at least at this level (0.5 their mean): the clear zones' starlight unshaded. Illustrative." },
  { key: "coreGain", label: "nucleus point", min: 0, max: 20, step: 0.05, unit: "×", default: 0, perTemplate: { milky_way: 0, ngc_4414: 20 }, about: "A compact bright point at the nucleus: the light there lifted by 1 plus this, falling off over the point's radius (the broad glow kept). Illustrative." },
  { key: "coreRadius", label: "nucleus point radius", min: 0.01, max: 1, step: 0.005, log: true, unit: "kpc", default: 0.12, perTemplate: { ngc_4414: 0.12 }, about: "The nucleus point's radius at 1/e, kpc. Illustrative." },
  { key: "coreWhite", label: "nucleus point white", min: 0, max: 1, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 0.9 }, about: "How far the nucleus point's lift goes toward a blue-white (it whitens a cream core). Colour for appearance." },
  { key: "glowDim", label: "nucleus glow dimmed", min: 0, max: 0.95, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 0.95 }, about: "The share of the light taken off the nucleus's broad glow at its centre (a gaussian), so the stretch does not flatten it into a blob. Colour for appearance." },
  { key: "glowRadius", label: "nucleus glow radius", min: 0.1, max: 5, step: 0.05, log: true, unit: "kpc", default: 1, perTemplate: { ngc_4414: 1.5 }, about: "The radius at 1/e of the glow's dimming, kpc. Colour for appearance." },
  { key: "arcPeak", label: "dust on arc crests", min: 0, max: 3, step: 0.01, unit: "×", default: 1, perTemplate: { ngc_4414: 1.2 }, about: "The drawn dust's depth on the arcs' crests, a multiplier. Illustrative." },
  // S107 (builder NGC3): the gate's arcs as MANY NARROW LANES - thin soft-edged spiral ribbons at an open pitch, wandering,
  // broken into pieces of varied strength - in place of the noise's broad bands; inside them a pale veil with sparse dark
  // cores, and wisps feathering off their edges at an angle. Drawn in the march (no rebuild).
  { key: "laneForm", label: "narrow dust lanes", min: 0, max: 1, step: 1, unit: "", default: 0, perTemplate: { ngc_4414: 1 }, about: "The plane style's arcs: 0 the broad arcs of a spiral noise; 1 many narrow lanes along an open spiral, broken into pieces. Illustrative." },
  { key: "laneSpacing", label: "dust lane spacing", min: 100, max: 2000, step: 10, unit: "pc", default: 450, perTemplate: { ngc_4414: 1000 }, about: "The narrow lanes' spacing across the spiral at half the network's outer radius, parsecs (in proportion to the radius). Illustrative." },
  { key: "lanePitch", label: "dust lane pitch", min: 0.3, max: 3, step: 0.01, unit: "×", default: 1, perTemplate: { ngc_4414: 1.3 }, about: "The narrow lanes' pitch as a multiple of the drawn pitch (the network's): higher, a more open spiral. Illustrative." },
  { key: "laneCrest", label: "dust lane width", min: 0.05, max: 0.8, step: 0.01, unit: "×", default: 0.3, perTemplate: { ngc_4414: 0.3 }, about: "A narrow lane's full width at half depth as a share of the spacing (a soft gaussian edge). Illustrative." },
  { key: "laneWander", label: "dust lane wander", min: 0, max: 2, step: 0.01, unit: "×", default: 0.6, perTemplate: { ngc_4414: 0.8 }, about: "How far a lane wanders across the spiral, as a share of the spacing (lanes come near, part and join). Illustrative." },
  { key: "laneWanderSize", label: "dust lane wander size", min: 200, max: 6000, step: 10, unit: "pc", default: 1800, perTemplate: { ngc_4414: 1800 }, about: "The size of the noise that makes the lanes wander, parsecs. Illustrative." },
  { key: "lanePiece", label: "dust lane pieces", min: 200, max: 6000, step: 10, unit: "pc", default: 1500, perTemplate: { ngc_4414: 1300 }, about: "The size of the noise that breaks the lanes into pieces, parsecs (a piece is about this long). Illustrative." },
  { key: "laneGaps", label: "dust lane gaps", min: 0, max: 1, step: 0.01, unit: "", default: 0.4, perTemplate: { ngc_4414: 0.4 }, about: "The level of the pieces' noise under which a lane is broken: higher, shorter pieces and wider gaps. Illustrative." },
  { key: "laneVary", label: "dust lane strength spread", min: 0, max: 1, step: 0.01, unit: "", default: 0.6, perTemplate: { ngc_4414: 0.7 }, about: "How far the pieces' depth varies from one to the next (0 all alike). Illustrative." },
  { key: "laneBranch", label: "dust lane branches", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.6 }, about: "A second set of lanes at a steeper pitch crossing the first (forks and joins), as a share of their depth; 0 none. Illustrative." },
  { key: "laneVeil", label: "dust lane veil", min: 0, max: 2, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.6 }, about: "A smooth pale tan veil filling each lane, in full threads (the light dust the filaments lie in); 0 none. Illustrative." },
  { key: "meshLight", label: "mesh lightness", min: 0, max: 1, step: 0.01, unit: "", default: 1, perTemplate: { ngc_4414: 0.4 }, about: "The share of the mesh's depth drawn outside the dark cores (1 as drawn, lower a paler mesh). Illustrative." },
  { key: "coreShare", label: "dark cores", min: 0, max: 0.6, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.35 }, about: "The share of a lane in dark cores, where the mesh keeps its full depth and more; 0 none. Illustrative." },
  { key: "coreSize", label: "dark core size", min: 30, max: 1000, step: 5, unit: "pc", default: 150, perTemplate: { ngc_4414: 140 }, about: "The size of the noise that places the dark cores, parsecs. Illustrative." },
  { key: "coreDepth", label: "dark core depth", min: 0, max: 5, step: 0.05, unit: "×", default: 2, perTemplate: { ngc_4414: 4 }, about: "The mesh's depth in a core as a multiple of its full depth. Illustrative." },
  { key: "laneWisps", label: "lane wisps", min: 0, max: 2, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.8 }, about: "Fine wisps leaving a lane's edges at an angle, in full threads; 0 none. Illustrative." },
  { key: "grainReach", label: "grain reach", min: 0.3, max: 1.5, step: 0.01, unit: "× outer", default: 1, perTemplate: { ngc_4414: 1 }, about: "How far the light's grain and puffs reach, as a multiple of the network's outer radius (they fade over its outer quarter): the disc's rim left smooth. Illustrative." },
  { key: "wispAngle", label: "lane wisp angle", min: 0, max: 80, step: 1, unit: "°", default: 35, about: "The wisps' angle to their lane, degrees. Illustrative." },
];

const DEFAULTS: Readonly<Record<string, number>> = Object.fromEntries(CONTROLS.map((c) => [c.key, c.default]));

/** The shaping parameters among the feature's own (the others are uniforms). */
export function shapeOf(p: IllParams): FlocShape {
  return Object.fromEntries(SHAPE_KEYS.map((k) => [k, p[k] ?? DEFAULTS[k]])) as unknown as FlocShape;
}

/** The star clouds' shaping values among the feature's own. */
export function cloudShapeOf(p: IllParams): CloudShape {
  return cloudsOf(shapeOf(p));
}

// The e2e tools type-check this registry without JSX (e2e/tsconfig.json): the drawing is a .tsx they never load.
// @ts-ignore TS6142 under the e2e tools' compiler options only
const Clouds = lazy(() => import("./CloudsLayer"));
/** The star clouds' drawing, loaded apart from the registry (it draws through FluxPoints, which imports the registry). */
function FlocLayer(props: IllLayerProps) {
  return createElement(Suspense, { fallback: null }, createElement(Clouds, props));
}

/** Whether anything of the feature is drawn at these parameters (nothing is built otherwise). */
export const flocDrawn = (p: IllParams): boolean => ["depth", "patch", "clump", "young"].some((k) => (p[k] ?? DEFAULTS[k]) > 0);

/** The last build's time, ms, and how many were built (a diagnostic: nothing is drawn from it). */
export const flocBuild = { ms: 0, count: 0 };

const now = () => (typeof performance !== "undefined" ? performance.now() : 0);

/** The feature's channel for a frame and a shape: built once per (frame, drawn or not, shaping values); null while nothing is drawn. */
const channel = memoOn((frame: unknown, drawn: unknown, ...values: unknown[]): Uint8Array | null => {
  if (!frame || !drawn) return null;
  const shape = Object.fromEntries(SHAPE_KEYS.map((k, i) => [k, values[i] as number])) as unknown as FlocShape;
  const started = now();
  const g = geometryOf(frame as IllFrame);
  const map = shape.style >= 0.5 ? buildNetChannel(g, shape) : buildFlocChannel(g, shape);
  flocBuild.ms = now() - started;
  // S106 (C4): the build's time as a performance measure, readable in a browser (performance.getEntriesByName).
  if (typeof performance !== "undefined" && typeof performance.measure === "function") performance.measure("illustrative floc map", { start: started, duration: flocBuild.ms });
  flocBuild.count += 1;
  return map;
}, "floc.channel");

/** The feature's channel of the shared map at these parameters, for this frame; null where it draws nothing. */
export function flocChannel(p: IllParams, frame: IllFrame | null): Uint8Array | null {
  const shape = shapeOf(p);
  return channel(frame, flocDrawn(p), ...SHAPE_KEYS.map((k) => shape[k]));
}

/** The mesh's arcs: arms and cells of the spiral lattice for an arc's width at half the outer radius, tan(pitch), the share. */
function arcUniform(widthPc: number, run: number, outer: number, pitch: number, share: number): number[] {
  const r = 0.5 * outer;
  const across = Math.max(widthPc, 50) * 1e-3;
  const m = Math.max(2, Math.round((2 * Math.PI * r * Math.sin(pitch)) / across));
  const cells = Math.max(3, Math.round((2 * Math.PI * r) / (Math.cos(pitch) * across * Math.max(run, 0.5))));
  return [m, cells, Math.tan(pitch), share];
}

/** The mesh's uniforms (floc.ts GLSL illFlocMeshShape): its own values and the plane style's ring. */
function meshUniforms(p: IllParams, frame: IllFrame | null): Record<string, unknown> {
  const v = (k: string) => p[k] ?? DEFAULTS[k];
  const outer = Math.max(v("innerRadius") + 0.1, v("outerRadius"));
  const pitch = Math.min(80, Math.max(1, geometryOf(frame).pitchDeg * v("pitch"))) * (Math.PI / 180);
  return {
    illFlocMesh: v("style") >= 0.5 ? v("meshDepth") : 0,
    illFlocMeshA: [Math.max(v("meshCell"), 20) * 1e-3, (Math.max(v("meshWidth"), 4) * 1e-3) / 2, Math.min(2.5, Math.max(1, v("meshStretch"))), Math.min(0.95, Math.max(0, v("meshOpen")))],
    illFlocMeshB: [v("meshFine"), v("meshKnot"), pitch, v("meshBroad")],
    illFlocMeshC: [Math.max(v("meshPiece"), 50) * 1e-3, v("meshGaps"), v("meshWarp"), v("meshFollow")],
    illFlocArc: arcUniform(v("meshArcWidth"), v("meshArcRun"), outer, pitch, v("meshArc")),
    illFlocHaze: v("meshHaze"),
    illFlocGate: [v("style") >= 0.5 ? v("arcGate") : 0, v("arcClear"), v("arcLevel"), v("arcPeak")],
    illFlocPuff: [v("style") >= 0.5 ? v("puffs") : 0, Math.max(v("puffSize"), 10) * 1e-3, v("puffNear"), v("puffBlue")],
    illFlocRingA: [Math.max(0, v("innerRadius")), Math.max(0.01, v("ringIn")) * outer, Math.max(0.02, v("ringOut")) * outer, outer],
    illFlocRingB: [v("core"), v("rim"), v("nearBias"), (v("nearAz") * Math.PI) / 180],
    ...laneUniforms(v, outer, pitch),
  };
}

/** S107 (NGC3): the narrow lanes' uniforms (floc.ts GLSL illFlocLanes): lanes per turn, the pitch's tangent, the rest. */
function laneUniforms(v: (k: string) => number, outer: number, pitch: number): Record<string, unknown> {
  const lp = Math.min(70, Math.max(2, (pitch * 180) / Math.PI * v("lanePitch"))) * (Math.PI / 180);
  const r = 0.5 * outer;
  const lanes = Math.max(2, Math.round((2 * Math.PI * r * Math.tan(lp)) / (Math.max(v("laneSpacing"), 20) * 1e-3)));
  const branch = Math.max(2, Math.round(lanes * 0.6));
  return {
    illFlocLaneA: [v("style") >= 0.5 && v("laneForm") >= 0.5 ? 1 : 0, lanes, Math.tan(lp), Math.max(0.02, v("laneCrest"))],
    illFlocLaneB: [v("laneWander"), Math.max(v("laneWanderSize"), 50) * 1e-3, Math.max(v("lanePiece"), 50) * 1e-3, v("laneGaps")],
    illFlocLaneC: [v("laneVary"), v("laneBranch"), v("laneVeil"), v("laneWisps")],
    illFlocLaneD: [branch, Math.tan(Math.min(75, ((lp * 180) / Math.PI) * 1.6) * (Math.PI / 180)), (v("wispAngle") * Math.PI) / 180, lp],
    illFlocCore: [v("meshLight"), v("coreShare"), Math.max(v("coreSize"), 10) * 1e-3, v("coreDepth")],
  };
}

const MAX = FLOC_MAP.shapeMax.toFixed(1);
const FLOOR = FLOC_MAP.lightFloor.toFixed(2);

export const floc: IllFeature = {
  id: "floc",
  label: "flocculent network",
  about: "A flocculent disc's network of short dust filaments, its light broken into patches, young clumps outside and a warm inner disc: placed by the published pitch, gas and stars' contrast, the drawing the viewer's own.",
  controls: CONTROLS,
  glsl: /* glsl */ `
  uniform float illFlocDepth;
  uniform float illFlocInk;
  uniform float illFlocRed;
  uniform float illFlocHard;
  uniform float illFlocPatch;
  uniform float illFlocClump;
  uniform float illFlocYoungGain;
  uniform float illFlocBlue;
  uniform float illFlocWarm;
  uniform float illFlocWarmR;
  uniform float illFlocCap;
  uniform float illFlocNuc;
  uniform float illFlocNucR;
  uniform float illFlocStyle;
  uniform float illFlocGrain;
  uniform float illFlocGrainS;
  uniform float illFlocGrainNear;
  uniform float illFlocGrainR;
  uniform float illFlocKnots;
  uniform float illFlocCool;
  uniform float illFlocCoolR;
  // S107 (NGC): how far the grain (x) and the puffs (y) dim the light between them (1 as S106, 0 brightening only).
  uniform vec4 illFlocLitDim;
  uniform vec4 illFlocNucPt;
  // S106 (C3): value noise over the plane in [0, 1], its lattice at the integers (a hash of the cell, computed: no texture read).
  float illFlocHash(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
  }
  float illFlocVN(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    float a = illFlocHash(i);
    float b = illFlocHash(i + vec2(1.0, 0.0));
    float c = illFlocHash(i + vec2(0.0, 1.0));
    float d = illFlocHash(i + vec2(1.0, 1.0));
    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
  }
  // S106 third pass (C4): the dust mesh, drawn here per ray (no map, no rebuild): filaments on the edges of the cells
  // of a cellular (Worley) network in kpc, one jittered point a cell, the cells drawn out along the spiral, so they fork
  // and join at angles; a share of the edges left out (open ends, branches), each edge its own width, dark clumps where
  // three meet, a finer mesh on it. Its amount: the plane style's ring, near-side bias and a patch noise.
  uniform float illFlocMesh;
  uniform vec4 illFlocPuff;
  uniform vec4 illFlocMeshA;
  uniform vec4 illFlocMeshB;
  uniform vec4 illFlocMeshC;
  uniform vec4 illFlocRingA;
  uniform vec4 illFlocRingB;
  uniform vec4 illFlocArc;
  uniform float illFlocHaze;
  // Value noise on the log spiral (X along, Y across; m arms, cells along a turn), the azimuth's wrap joined:
  // the lattice point (X + cells, Y - m) is (X, Y).
  float illFlocSpiralCorner(vec2 i, float m, float cells, float k) {
    float q = floor(i.x / cells);
    return illFlocHash(vec2(i.x - q * cells, i.y + q * m) + vec2(k, 0.61 * k));
  }
  float illFlocSpiralVN(vec2 rp, float m, float cells, float k) {
    vec2 p = vec2(rp.y * cells, m * (log(max(rp.x, 0.05)) / illFlocArc.z - rp.y)) / 6.2831853;
    vec2 i = floor(p);
    vec2 f = p - i;
    vec2 u = f * f * (3.0 - 2.0 * f);
    float a = illFlocSpiralCorner(i, m, cells, k);
    float b = illFlocSpiralCorner(i + vec2(1.0, 0.0), m, cells, k);
    float c = illFlocSpiralCorner(i + vec2(0.0, 1.0), m, cells, k);
    float d = illFlocSpiralCorner(i + vec2(1.0, 1.0), m, cells, k);
    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
  }
  // S107 (NGC): the gate - all the drawn dust gathered on the mesh's arcs (x its strength, y the share left between
  // them, z the arcs' level, w the depth on their crests); 1 where it is off.
  uniform vec4 illFlocGate;
  // S107 (NGC3): the narrow lanes - x on, y lanes per turn, z tan(their pitch), w a lane's width at half depth over the
  // spacing; B the wander (spacings) and its size (kpc), the pieces' size (kpc) and gap level; C the pieces' strength
  // spread, the branch set's share, the veil, the wisps; D the branch set's lanes per turn and tan(pitch), the wisps'
  // angle (rad), the lanes' pitch (rad).
  uniform vec4 illFlocLaneA;
  uniform vec4 illFlocLaneB;
  uniform vec4 illFlocLaneC;
  uniform vec4 illFlocLaneD;
  // x the mesh's share outside the dark cores, y the cores' share, z their noise's size (kpc), w the depth in them.
  uniform vec4 illFlocCore;
  // One set of lanes at xy (kpc): x the lane's depth in [0, 1] (its soft crest, its piece, the piece's strength), y the
  // margin beside the crest where wisps leave it.
  vec2 illFlocLaneSet(vec2 rp, vec2 xy, float n, float tA, float k) {
    float v = n * (log(max(rp.x, 0.05)) / tA - rp.y) / 6.2831853;
    vec2 wq = xy / illFlocLaneB.y;
    v += illFlocLaneB.x * 2.0 * (0.65 * illFlocVN(wq + vec2(k, 2.3)) + 0.35 * illFlocVN(2.5 * wq + vec2(4.1, k)) - 0.5);
    float j = floor(v);
    float f = v - j - 0.5;
    float s = f / max(illFlocLaneA.w, 0.02);
    float crest = exp(-2.773 * s * s);
    float margin = max(exp(-0.693 * s * s) - crest, 0.0) * (1.0 - smoothstep(0.32, 0.5, abs(f)));
    // Each lane its own pieces (the lane's index taken round the turn, so the azimuth's wrap joins).
    float jm = mod(j, n);
    vec2 o = vec2(fract(jm * 0.6180339) * 97.0, fract(jm * 0.4142136) * 89.0 + k);
    float pn = 0.7 * illFlocVN(xy / illFlocLaneB.z + o) + 0.3 * illFlocVN(xy / (0.4 * illFlocLaneB.z) + o.yx);
    float piece = smoothstep(illFlocLaneB.w - 0.1, illFlocLaneB.w + 0.1, pn);
    float strength = 1.0 - illFlocLaneC.x + illFlocLaneC.x * smoothstep(illFlocLaneB.w, min(illFlocLaneB.w + 0.35, 1.0), pn);
    return vec2(crest, margin) * piece * strength;
  }
  vec2 illFlocLanes(vec2 rp) {
    vec2 xy = rp.x * vec2(cos(rp.y), sin(rp.y));
    vec2 l = illFlocLaneSet(rp, xy, illFlocLaneA.y, illFlocLaneA.z, 1.3);
    if (illFlocLaneC.y > 0.0) l = max(l, illFlocLaneC.y * illFlocLaneSet(rp, xy, illFlocLaneD.x, illFlocLaneD.y, 7.9));
    return l;
  }
  float illFlocGateAt(vec2 rp) {
    if (illFlocGate.x <= 0.0) return 1.0;
    float m;
    if (illFlocLaneA.x > 0.5) m = illFlocLanes(rp).x;
    else {
      float sn = 0.7 * illFlocSpiralVN(rp, illFlocArc.x, illFlocArc.y, 1.7) + 0.3 * illFlocSpiralVN(rp, 2.0 * illFlocArc.x, 2.0 * illFlocArc.y, 8.3);
      float lv = 0.3 + 0.4 * illFlocGate.z;
      m = smoothstep(lv - 0.07, lv + 0.07, sn);
    }
    return mix(1.0, illFlocGate.y + (illFlocGate.w - illFlocGate.y) * m, illFlocGate.x);
  }
  vec2 illFlocMeshPt(vec2 c, float k) {
    return vec2(illFlocHash(c + vec2(k, 0.37 * k)), illFlocHash(c + vec2(17.31 + k, 41.7)));
  }
  // The distance (kpc) from the origin to the bisector of a and b given in the drawn-out metric (along / S, across).
  float illFlocEdgeD(vec2 a, vec2 b, float S) {
    vec2 n = normalize(b - a + vec2(1e-7));
    return abs(0.5 * dot(a + b, n)) / max(length(vec2(n.x / S, n.y)), 1e-6);
  }
  // An edge's weight in [0, 1): the same from either side (the pair's sum and spread).
  float illFlocEdgeW(vec2 a, vec2 b, float k) {
    return illFlocHash(a + b + vec2(0.5 * k, 3.7) + abs(a - b) * vec2(5.13, 2.71));
  }
  // The mesh's filaments at xy (kpc) for cells cell kpc across, along t drawn out S times: the edge's profile (each edge
  // between half and 1.7 of the width h), the junctions' clumps (knot), none on an edge left out (w under open).
  float illFlocCells(vec2 xy, vec2 t, float cell, float h, float S, float open, float knot, float k) {
    vec2 c0 = floor(xy / cell);
    float b1 = 1e9; float b2 = 1e9; float b3 = 1e9;
    vec2 q1 = vec2(0.0); vec2 q2 = vec2(0.0); vec2 q3 = vec2(0.0);
    vec2 c1 = vec2(0.0); vec2 c2 = vec2(0.0); vec2 c3 = vec2(0.0);
    for (int i = -2; i <= 2; i++) {
      for (int j = -2; j <= 2; j++) {
        vec2 c = c0 + vec2(float(i), float(j));
        vec2 d = (c + illFlocMeshPt(c, k)) * cell - xy;
        vec2 q = vec2(dot(d, t) / S, d.y * t.x - d.x * t.y);
        float d2 = dot(q, q);
        if (d2 < b3) {
          if (d2 < b2) {
            b3 = b2; q3 = q2; c3 = c2;
            if (d2 < b1) { b2 = b1; q2 = q1; c2 = c1; b1 = d2; q1 = q; c1 = c; }
            else { b2 = d2; q2 = q; c2 = c; }
          } else { b3 = d2; q3 = q; c3 = c; }
        }
      }
    }
    float w = illFlocEdgeW(c1, c2, k);
    if (w < open) return 0.0;
    float hw = h * (0.5 + 1.2 * (w - open) / max(1.0 - open, 1e-3)) * (0.55 + 0.9 * illFlocVN(xy / (0.8 * cell) + vec2(k)));
    float e = illFlocEdgeD(q1, q2, S) / hw;
    float prof = exp(-0.693 * e * e);
    if (knot > 0.0 && illFlocEdgeW(c1, c3, k) >= open) {
      float e3 = illFlocEdgeD(q1, q3, S) / (2.5 * hw);
      prof += knot * prof * exp(-0.693 * e3 * e3);
    }
    return prof;
  }
  // The plane style's ring: the dust's amount by radius and near-side azimuth.
  float illFlocRingAt(vec2 rp) {
    float r = rp.x;
    float inner = illFlocRingA.x;
    return (inner > 0.0 ? smoothstep(0.5 * inner, 1.5 * inner, r) : 1.0)
      * (illFlocRingB.x + (1.0 - illFlocRingB.x) * smoothstep(0.4 * illFlocRingA.y, illFlocRingA.y, r))
      * (1.0 - (1.0 - illFlocRingB.y) * smoothstep(illFlocRingA.z, max(illFlocRingA.z + 0.01, 0.95 * illFlocRingA.w), r))
      * (1.0 - smoothstep(0.88 * illFlocRingA.w, illFlocRingA.w, r))
      * max(1.0 + illFlocRingB.z * cos(rp.y - illFlocRingB.w), 0.0);
  }
  float illFlocMeshShape(vec2 rp, float near) {
    float r = rp.x;
    if (illFlocMesh <= 0.0 || r >= illFlocRingA.w) return 0.0;
    float ring = illFlocRingAt(rp);
    vec2 xy = r * vec2(cos(rp.y), sin(rp.y));
    float pc = illFlocMeshC.x;
    float n = 0.65 * illFlocVN(xy / pc + vec2(5.9, 13.3)) + 0.35 * illFlocVN(xy / (0.45 * pc) + vec2(3.7, 9.1));
    float a = illFlocMesh * ring * smoothstep(illFlocMeshC.y - 0.12, illFlocMeshC.y + 0.12, n) * (1.0 - illFlocMeshC.w + illFlocMeshC.w * 2.0 * near);
    // The arcs: short flocculent pieces of the spiral (two octaves), the mesh gathered on them, the smoke over them.
    float arc = 1.0;
    if (illFlocArc.w > 0.0 || illFlocHaze > 0.0) {
      float sn = 0.7 * illFlocSpiralVN(rp, illFlocArc.x, illFlocArc.y, 1.7) + 0.3 * illFlocSpiralVN(rp, 2.0 * illFlocArc.x, 2.0 * illFlocArc.y, 8.3);
      arc = smoothstep(0.4, 0.72, sn);
    }
    float smoke = illFlocHaze * illFlocMesh * ring * arc * max(0.0, 1.8 * (0.6 * illFlocVN(xy / 0.25 + vec2(2.9, 6.1)) + 0.4 * illFlocVN(xy / 0.1 + vec2(9.3, 1.7))) - 0.5);
    a *= 1.0 - illFlocArc.w + illFlocArc.w * 2.2 * arc;
    if (a <= 0.0) return smoke;
    float cell = illFlocMeshA.x;
    // The plane pushed about by a share of a cell over three cells: the filaments bend.
    vec2 wq = xy / (3.0 * cell);
    xy += illFlocMeshC.z * cell * (vec2(illFlocVN(wq + vec2(41.2, 13.7)), illFlocVN(wq + vec2(7.1, 29.3))) - 0.5) * 2.0;
    float p = illFlocMeshB.z;
    vec2 t = vec2(sin(p) * cos(rp.y) - cos(p) * sin(rp.y), sin(p) * sin(rp.y) + cos(p) * cos(rp.y));
    float v = illFlocCells(xy, t, cell, illFlocMeshA.y, illFlocMeshA.z, illFlocMeshA.w, illFlocMeshB.y, 3.1);
    if (illFlocMeshB.x > 0.0) v += illFlocMeshB.x * illFlocCells(xy, t, 0.5 * cell, 0.6 * illFlocMeshA.y, illFlocMeshA.z, illFlocMeshA.w, illFlocMeshB.y, 11.7);
    if (illFlocMeshB.w > 0.0) v += illFlocMeshB.w * illFlocCells(xy, t, 2.0 * cell, 2.5 * illFlocMeshA.y, illFlocMeshA.z, 0.5 * illFlocMeshA.w, illFlocMeshB.y, 23.9);
    return a * v + smoke;
  }
  // The feature's byte of the shared map read (flocMap.ts: signed about 128): x the dust, sqrt(shape / ${MAX}); y the
  // patches' level about their mean, in [-0.5, 0.5] (0, which changes nothing, where the light is not known: under a
  // filament, beyond the light's reach, where there is no map - a byte of 0 is never written); z a young clump's
  // level (0 its edge, 1 its centre).
  // S106, the plane style (illFlocStyle 1; flocNet.ts): y the clouds' brightening in [0, 1], its neutral 0.5 and 0 at a
  // dust margin (the byte next to 128, so the filter's passage into the dust draws no dark rim), z a knot's level.
  vec3 illFlocRead(vec2 rp) {
    float b = rp.x < rHi ? illMap(rp).g * 255.0 : 0.0;
    if (b < 0.5) return vec3(0.0, illFlocStyle > 0.5 ? 0.5 : 0.0, 0.0);
    float s = (b - 128.0) / 127.0;
    float l = max(-s, 0.0);
    if (illFlocStyle > 0.5) return vec3(max(s, 0.0), min(l, 0.6) / 0.6, clamp((l - 0.6) / 0.4, 0.0, 1.0));
    float level = clamp((l - ${FLOOR}) / (0.5 - ${FLOOR}), 0.0, 1.0) - 0.5;
    return vec3(max(s, 0.0), level * smoothstep(0.0, ${FLOOR}, l), clamp((l - 0.5) * 2.0, 0.0, 1.0));
  }
  // S106 (C4): the light's puffs - the nearest of one jittered point a cell, over the cell (0 at a puff's heart).
  // Each puff its own brightness (y, in [0, 1)): heaps of light of many strengths, not a foam of equal bubbles.
  vec2 illFlocPuffD(vec2 xy, float k) {
    vec2 c0 = floor(xy);
    vec2 b = vec2(9.0, 0.0);
    for (int i = -1; i <= 1; i++) {
      for (int j = -1; j <= 1; j++) {
        vec2 c = c0 + vec2(float(i), float(j));
        vec2 h = illFlocMeshPt(c, k);
        float d = length(c + 0.15 + 0.7 * h - xy);
        if (d < b.x) b = vec2(d, fract(h.x * 7.13 + h.y * 3.71));
      }
    }
    return b;
  }
  // How much drawn dust lies within 150 pc of rp, in [0, 1]: four reads of the map about it.
  float illFlocNear(vec2 rp) {
    float da = 0.15 / max(rp.x, 0.3);
    float s = illFlocRead(rp + vec2(0.15, 0.0)).x + illFlocRead(rp - vec2(0.15, 0.0)).x + illFlocRead(rp + vec2(0.0, da)).x + illFlocRead(rp - vec2(0.0, da)).x;
    return smoothstep(0.05, 1.2, s);
  }
  // The dust's shape from its byte: 1 at the centre of one full filament, more where filaments cross. The edge:
  // between the soft stroke as drawn and an inked one, as the lanes'.
  float illFlocShape(float s) {
    float shape = ${MAX} * s * s;
    if (illFlocDepth <= 0.0 || shape <= 0.0) return 0.0;
    float inked = smoothstep(0.25, 0.6, shape) * (1.0 + 0.5 * max(shape - 1.0, 0.0));
    return min(mix(shape, inked, illFlocHard), 2.0);
  }
  float illFlocAv(vec2 rp) {
    if (illFlocDepth <= 0.0 || illFlocInk >= 1.0) return 0.0;
    return illFlocDepth * (1.0 - illFlocInk) * illFlocShape(illFlocRead(rp).x) * (illFlocStyle > 0.5 ? illFlocGateAt(rp) : 1.0);
  }
  float illFlocYoung(vec2 rp) {
    if (illFlocYoungGain <= 0.0) return 1.0;
    return 1.0 + illFlocYoungGain * illFlocRead(rp).z;
  }
  vec3 illFlocVeil(vec2 rp) {
    vec3 veil = vec3(1.0);
    vec3 map = illFlocRead(rp);
    // S107 (NGC): the gate on the arcs, once per ray.
    // S107 (NGC3): with the narrow lanes, the lanes read once (x their depth, y the margins the wisps leave from).
    bool lanes = illFlocStyle > 0.5 && illFlocLaneA.x > 0.5 && illFlocGate.x > 0.0;
    vec2 lane = lanes ? illFlocLanes(rp) : vec2(0.0);
    float gate = lanes ? mix(1.0, illFlocGate.y + (illFlocGate.w - illFlocGate.y) * lane.x, illFlocGate.x) : (illFlocStyle > 0.5 ? illFlocGateAt(rp) : 1.0);
    // The ink: the grains' own depth per magnitude in each channel, its spread about the middle channel's times the
    // redness (0 grey, 1 the grains' own).
    float av = illFlocDepth * illFlocInk * illFlocShape(map.x);
    if (illFlocStyle > 0.5 && illFlocMesh > 0.0) {
      float mesh = illFlocMeshShape(rp, illFlocMeshC.w > 0.0 ? illFlocNear(rp) : 0.5);
      // S107 (NGC3): the mesh pale (its light share) but in sparse dark cores on the lanes' crests.
      if (lanes) {
        float core = 0.0;
        if (illFlocCore.y > 0.0 && mesh > 0.0) {
          vec2 cq = rp.x * vec2(cos(rp.y), sin(rp.y)) / illFlocCore.z;
          float cn = 0.65 * illFlocVN(cq + vec2(31.7, 5.3)) + 0.35 * illFlocVN(2.7 * cq + vec2(2.2, 47.1));
          core = smoothstep(0.78 - 0.4 * illFlocCore.y, 0.9 - 0.4 * illFlocCore.y, cn) * smoothstep(0.3, 0.8, lane.x);
        }
        mesh *= mix(illFlocCore.x, illFlocCore.w, core);
      }
      av += illFlocDepth * illFlocInk * mesh;
    }
    if (illFlocStyle > 0.5 && av > 0.0) av *= gate;
    // S107 (NGC3): the lanes' pale veil and the wisps feathering off their edges at an angle (a sparse cellular mesh
    // drawn out along the wisps' heading), both in the plane style's ring.
    if (lanes && (illFlocLaneC.z > 0.0 || illFlocLaneC.w > 0.0) && rp.x < illFlocRingA.w) {
      float ring = illFlocRingAt(rp);
      av += illFlocDepth * illFlocInk * illFlocLaneC.z * ring * lane.x;
      if (illFlocLaneC.w > 0.0 && lane.y * ring > 0.02) {
        float p = illFlocLaneD.w + illFlocLaneD.z;
        vec2 t = vec2(sin(p) * cos(rp.y) - cos(p) * sin(rp.y), sin(p) * sin(rp.y) + cos(p) * cos(rp.y));
        vec2 xy = rp.x * vec2(cos(rp.y), sin(rp.y));
        float w = illFlocCells(xy, t, 0.7 * illFlocMeshA.x, 0.7 * illFlocMeshA.y, 2.5, 0.55, 0.0, 19.3);
        av += illFlocDepth * illFlocInk * illFlocLaneC.w * ring * lane.y * w;
      }
    }
    if (av > 0.0) {
      // S106: the ceiling - the depth saturates softly toward illFlocCap magnitudes (a brown, never black).
      av = illFlocCap * (1.0 - exp(-av / illFlocCap));
      vec3 law = max(vec3(cloudExt.g) + illFlocRed * (cloudExt - vec3(cloudExt.g)), vec3(0.02 * cloudExt.g));
      vec3 dv = exp(-av * law);
      veil *= dv;
    }
    // The patches: the light swelled and thinned about the patches' mean level.
    if (illFlocStyle > 0.5) {
      // S107 (NGC): where the gate takes a thread away, so goes the shade the map draws on it and at its margins (the
      // clouds' level held up to its floor illFlocLitDim.z): no grey ghost of the thread in a clear zone.
      float lit = illFlocGate.x > 0.0 ? mix(max(map.y, illFlocLitDim.z), map.y, clamp(gate, 0.0, 1.0)) : map.y;
      veil *= (1.0 + illFlocPatch * lit) / (1.0 + 0.5 * illFlocPatch);
      // S106 (C3): the light's grain - small bright puffs, stronger just outside a dust thread (the map read 60 pc in
      // and out along the radius: the threads run mostly along the azimuth), none on the dust itself.
      if (illFlocGrain > 0.0 && rp.x < rHi) {
        vec2 xy = rp.x * vec2(cos(rp.y), sin(rp.y)) / max(illFlocGrainS, 1e-3);
        float n = 0.6 * illFlocVN(xy) + 0.4 * illFlocVN(mat2(0.6, -0.8, 0.8, 0.6) * xy * 2.31 + vec2(7.3, 1.9));
        float puff = smoothstep(0.42, 0.86, n);
        float side = max(illFlocRead(rp + vec2(0.06, 0.0)).x, illFlocRead(rp - vec2(0.06, 0.0)).x);
        float bare = 1.0 - smoothstep(0.0, 0.25, map.x);
        // Fading out over the outer fifth of the network's radius: the disc's faint rim is not broken into puffs.
        float amt = illFlocGrain * (1.0 + illFlocGrainNear * smoothstep(0.05, 0.35, side)) * bare * (1.0 - smoothstep(0.75 * illFlocGrainR, illFlocGrainR, rp.x));
        veil *= max(1.0 + amt * (puff - 0.3 * illFlocLitDim.x), 0.0);
        float peak = illFlocKnots * amt * smoothstep(0.8, 0.95, n);
        veil *= vec3(1.0) + peak * mix(vec3(1.0), vec3(0.78, 0.98, 1.35), illFlocBlue);
      }
      // S106 (C4): the puffs - cream-white heaps of light a few hundred parsecs across with gaps between, stronger
      // beside the dust, blue-white outside; none on the dust itself.
      if (illFlocPuff.x > 0.0 && rp.x < rHi) {
        vec2 xy = rp.x * vec2(cos(rp.y), sin(rp.y)) / illFlocPuff.y;
        vec2 pa = illFlocPuffD(xy, 5.3);
        vec2 pb = illFlocPuffD(xy * 2.3 + vec2(3.1, 7.7), 9.1);
        float heap = (1.0 - smoothstep(0.0, 0.7, pa.x)) * pa.y * pa.y * 1.6 + 0.5 * (1.0 - smoothstep(0.0, 0.6, pb.x)) * pb.y;
        float bare = 1.0 - smoothstep(0.0, 0.3, map.x);
        float edge = 1.0 - smoothstep(0.8 * illFlocGrainR, 1.15 * illFlocGrainR, rp.x);
        float amt = illFlocPuff.x * bare * edge * (1.0 + illFlocPuff.z * (illFlocPuff.z > 0.0 ? illFlocNear(rp) : 0.0));
        float cool = illFlocPuff.w * smoothstep(0.7 * illFlocCoolR, 1.5 * illFlocCoolR, rp.x);
        veil *= max(vec3(1.0) + amt * (heap - 0.25 * illFlocLitDim.y) * mix(vec3(1.0), vec3(0.8, 0.97, 1.3), min(cool, 1.0)), vec3(0.0));
      }
      // S106 (C3): the outer disc's light toward a blue-white, the inner left cream.
      if (illFlocCool > 0.0) veil *= mix(vec3(1.0), vec3(0.84, 0.97, 1.24), illFlocCool * smoothstep(0.7 * illFlocCoolR, 1.5 * illFlocCoolR, rp.x));
    }
    else veil *= max(1.0 + illFlocPatch * map.y, 0.0);
    // The clumps: brighter, toward a blue-white.
    veil *= vec3(1.0) + illFlocClump * map.z * mix(vec3(1.0), vec3(0.78, 0.98, 1.35), illFlocBlue);
    // The warmth: a cream tint over the inner disc.
    if (illFlocWarm > 0.0) {
      float w = illFlocWarm * exp(-(rp.x * rp.x) / max(illFlocWarmR * illFlocWarmR, 1e-6));
      veil *= vec3(1.0 + 0.2 * w, 1.0 + 0.03 * w, 1.0 - 0.32 * w);
    }
    // S106: the nucleus's cream-yellow (its own light reads blue-cyan under the stretch).
    if (illFlocNuc > 0.0) {
      float n = illFlocNuc * exp(-(rp.x * rp.x) / max(illFlocNucR * illFlocNucR, 1e-6));
      veil *= mix(vec3(1.0), vec3(1.25, 0.98, 0.55), n);
    }
    // S107 (NGC): the nucleus's sharp point - the light lifted by a narrow gaussian toward a near-white (x the gain,
    // y the radius at 1/e, kpc, z how white), in the broad glow kept.
    // S107 (NGC): the broad glow dimmed toward the centre (z the share taken at the centre, w its radius at 1/e, kpc),
    // so the stretch's shoulder no longer flattens it into a blob and the point reads inside it.
    if (illFlocNucPt.z > 0.0) {
      float q = rp.x / max(illFlocNucPt.w, 1e-3);
      veil *= 1.0 - illFlocNucPt.z * exp(-q * q);
    }
    if (illFlocLitDim.w > 0.0) {
      float q = rp.x / max(illFlocNucPt.x, 1e-3);
      veil *= vec3(1.0) + illFlocLitDim.w * exp(-q * q) * mix(vec3(1.0), vec3(0.85, 0.97, 1.25), illFlocNucPt.y);
    }
    return veil;
  }
`,
  hooks: { dustAv: "illFlocAv", youngGain: "illFlocYoung", veil: "illFlocVeil" },
  arrays: FLOC_ARRAYS,
  layer: FlocLayer,
  map: { channels: ILL_MAP_CHANNELS.floc, build: (p, context) => [flocChannel(p, context.frame)] },
  uniforms: (p, context) => {
    return {
      illFlocDepth: p.depth ?? DEFAULTS.depth,
      illFlocInk: p.ink ?? DEFAULTS.ink,
      illFlocRed: p.redness ?? DEFAULTS.redness,
      illFlocHard: p.hardness ?? DEFAULTS.hardness,
      illFlocPatch: p.patch ?? DEFAULTS.patch,
      illFlocClump: p.clump ?? DEFAULTS.clump,
      illFlocYoungGain: p.young ?? DEFAULTS.young,
      illFlocBlue: p.blue ?? DEFAULTS.blue,
      illFlocWarm: p.warmth ?? DEFAULTS.warmth,
      illFlocWarmR: p.warmRadius ?? DEFAULTS.warmRadius,
      illFlocCap: p.cap ?? DEFAULTS.cap,
      illFlocNuc: p.nucleus ?? DEFAULTS.nucleus,
      illFlocNucR: p.nucleusRadius ?? DEFAULTS.nucleusRadius,
      illFlocStyle: p.style ?? DEFAULTS.style,
      illFlocGrain: p.litGrain ?? DEFAULTS.litGrain,
      illFlocGrainS: (p.litGrainSize ?? DEFAULTS.litGrainSize) * 1e-3,
      illFlocGrainNear: p.litGrainNear ?? DEFAULTS.litGrainNear,
      illFlocGrainR: (p.outerRadius ?? DEFAULTS.outerRadius) * (p.grainReach ?? DEFAULTS.grainReach),
      illFlocKnots: p.litKnots ?? DEFAULTS.litKnots,
      illFlocCool: p.cool ?? DEFAULTS.cool,
      illFlocCoolR: p.coolRadius ?? DEFAULTS.coolRadius,
      illFlocLitDim: [p.grainDim ?? DEFAULTS.grainDim, p.puffDim ?? DEFAULTS.puffDim, p.clearFloor ?? DEFAULTS.clearFloor, p.coreGain ?? DEFAULTS.coreGain],
      illFlocNucPt: [p.coreRadius ?? DEFAULTS.coreRadius, p.coreWhite ?? DEFAULTS.coreWhite, p.glowDim ?? DEFAULTS.glowDim, p.glowRadius ?? DEFAULTS.glowRadius],
      ...meshUniforms(p, context.frame),
    };
  },
};
