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
    key: "depth", label: "network depth", min: 0, max: 10, step: 0.05, unit: "mag", default: 0, perTemplate: { milky_way: 0, ngc_4414: 3.4},
    about: "The depth at the centre of one full filament of the dust network, magnitudes of A_V; 0 no network. Illustrative.",
  },
  {
    key: "ink", label: "network ink", min: 0, max: 1, step: 0.01, unit: "", default: 0.75, perTemplate: { ngc_4414: 1 },
    about: "The share of the depth drawn as a veil over all the light on its line of sight (sharp brown threads, the same on both sides of the disc); the rest is dust in the dust's own thin layer, which the march makes darker on the near side. Illustrative.",
  },
  { key: "redness", label: "network redness", min: 0, max: 4, step: 0.05, unit: "×", default: 1.5, perTemplate: { ngc_4414: 1.4}, about: "The veil's colour: 0 a grey veil, 1 the dust grains' own reddening, higher a redder brown. Colour for appearance." },
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
    key: "warmth", label: "inner warmth", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 0.15},
    about: "A cream tint over the inner disc's light, fading outward: the old disc of the photograph. Colour for appearance.",
  },
  { key: "warmYellow", label: "warmth yellow", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 1 }, about: "The inner warmth's hue: 0 the S106 cream-orange, 1 a yellow-tan (more green kept, less red added), S110. Colour for appearance." },
  { key: "warmRadius", label: "warmth radius", min: 0.5, max: 15, step: 0.1, unit: "kpc", default: 4.5, perTemplate: { ngc_4414: 4}, about: "The radius at which the warm tint has fallen to 1/e, kpc. Colour for appearance." },
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
  { key: "haze", label: "dust haze", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.08}, about: "The plane style: a smooth brown haze where the threads gather (the smoky lanes they lie in), as a share of a thread's depth; 0 threads only. Illustrative." },
  { key: "ringIn", label: "dust ring from", min: 0, max: 1, step: 0.01, unit: "× outer", default: 0.25, perTemplate: { ngc_4414: 0.12 }, about: "The dust comes in to its full amount at this share of the network's outer radius (the nuclear region inside holds the nuclear dust's share of it). Illustrative." },
  { key: "ringOut", label: "dust ring to", min: 0, max: 1, step: 0.01, unit: "× outer", default: 0.7, perTemplate: { ngc_4414: 0.45 }, about: "The dust thins from this share of the outer radius to the outer dust's share of its amount near the edge. Illustrative." },
  { key: "core", label: "nuclear dust", min: 0, max: 1, step: 0.01, unit: "", default: 0.15, perTemplate: { ngc_4414: 0.4 }, about: "The dust's amount in the nuclear region, as a share of the ring's. Illustrative." },
  { key: "rim", label: "outer dust", min: 0, max: 1, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 0 }, about: "The dust's amount in the outer disc, as a share of the ring's. Illustrative." },
  { key: "nearBias", label: "near-side dust", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.3 }, about: "How much more dust lies toward the near-side azimuth (and less opposite): 1 twice the mean there, none opposite. Illustrative." },
  { key: "nearAz", label: "near-side azimuth", min: 0, max: 360, step: 1, unit: "°", default: 0, perTemplate: { ngc_4414: 300 }, about: "The galactocentric azimuth of the most dust, degrees. Illustrative." },
  { key: "litScale", label: "light cloud size", min: 40, max: 1500, step: 10, unit: "pc", default: 220, perTemplate: { ngc_4414: 120 }, about: "The size of the cream clouds of light between the dust, parsecs. Illustrative." },
  { key: "litKnots", label: "bright grains", min: 0, max: 3, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 1.4 }, about: "How bright the brightest of the light's grains are (the grain's peaks, in the clump tint). Illustrative." },
  { key: "litReach", label: "light reach", min: 1, max: 3, step: 0.05, unit: "× outer", default: 1.7, perTemplate: { ngc_4414: 1.3 }, about: "How far the plane style's clouds of light reach, as a multiple of the network's outer radius. Illustrative." },
  // S106 second pass (C3): the light's grain and its radial colour, drawn in the march (no rebuild).
  { key: "litGrain", label: "light grain", min: 0, max: 3, step: 0.01, unit: "×", default: 0, perTemplate: { milky_way: 0, ngc_4414: 1.3}, about: "The plane style: how far the starlight between the dust is broken into small bright puffs (a multiplier about 1); 0 smooth. Illustrative." },
  { key: "litGrainSize", label: "grain size", min: 10, max: 300, step: 1, unit: "pc", default: 40, perTemplate: { ngc_4414: 12 }, about: "A puff of the light's grain, parsecs (a finer one at under half of it rides on it). Illustrative." },
  { key: "litGrainNear", label: "grain by the dust", min: 0, max: 5, step: 0.05, unit: "×", default: 1.5, perTemplate: { ngc_4414: 0 }, about: "How much stronger the grain is just outside a dust thread (the young light along the arcs). Illustrative." },
  { key: "cool", label: "outer blue", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 0.6}, about: "The plane style: a blue-white tint over the outer disc's light, from the outer blue's radius outward (warm cream inside). Colour for appearance." },
  { key: "coolRadius", label: "outer blue from", min: 0.5, max: 20, step: 0.1, unit: "kpc", default: 5, perTemplate: { ngc_4414: 4.5 }, about: "The tint is none at 0.7 of this radius and full at 1.5 of it, kpc. Colour for appearance." },
  {
    key: "cap", label: "dust ceiling", min: 0.1, max: 20, step: 0.05, unit: "mag", default: 20, perTemplate: { ngc_4414: 2.6},
    about: "The veil's depth saturates softly toward this many magnitudes: the thickest dust stays a deep red-brown, never black. Colour for appearance.",
  },
  {
    key: "nucleus", label: "nucleus cream", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 0},
    about: "A cream-yellow tint over the nucleus's light (its march draws a blue-cyan core under the stretch): 0 none, 1 full. Colour for appearance.",
  },
  // S106: the star clouds (flocClouds.ts, FlocClouds.tsx), a points layer of the feature's own, drawn in the plane style.
  {
    key: "cloudCount", label: "star cloud points", min: 0, max: 80000, step: 500, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 15000},
    about: "How many points the star clouds hold (in the plane style only): loose groups over the bright light between the dust, densest in the outer disc; 0 none. Illustrative.",
  },
  { key: "cloudGain", label: "star cloud brightness", min: 10, max: 1e7, step: 0.01, log: true, unit: "L☉", default: 3000, perTemplate: { ngc_4414: 35000 }, about: "The faintest star cloud point's light, L☉ over the white point (the field's scale, with the exposure). Illustrative." },
  { key: "cloudRange", label: "star cloud range", min: 1, max: 1000, step: 0.01, log: true, unit: "×", default: 20, perTemplate: { ngc_4414: 80 }, about: "The brightest star cloud point over the faintest. Illustrative." },
  { key: "cloudSlope", label: "star cloud slope", min: 0.3, max: 4, step: 0.05, unit: "", default: 1.3, perTemplate: { ngc_4414: 1.0 }, about: "The brightness law's index: smaller, more bright points. Illustrative." },
  { key: "cloudSize", label: "star cloud point size", min: 0.5, max: 4, step: 0.1, unit: "px", default: 1.5, perTemplate: { ngc_4414: 2.2 }, about: "A star cloud point's sprite, pixels. Illustrative." },
  { key: "cloudGroup", label: "star cloud size", min: 10, max: 800, step: 5, unit: "pc", default: 120, perTemplate: { ngc_4414: 90 }, about: "A star cloud's gaussian radius, parsecs (each between half and one and a half of it). Illustrative." },
  { key: "cloudMembers", label: "star cloud members", min: 1, max: 60, step: 1, unit: "", default: 8, perTemplate: { ngc_4414: 18 }, about: "A star cloud's mean number of points. Illustrative." },
  { key: "cloudStart", label: "star clouds from", min: 0, max: 2, step: 0.01, unit: "× outer", default: 0.7, perTemplate: { ngc_4414: 0.35 }, about: "Where the star clouds come in to their full number, as a multiple of the network's outer radius (a quarter of it inside). Illustrative." },
  { key: "cloudReach", label: "star cloud reach", min: 0.5, max: 3, step: 0.01, unit: "× outer", default: 1.5, perTemplate: { ngc_4414: 0.75}, about: "How far the star clouds reach, as a multiple of the network's outer radius, the edge pushed in and out by a noise: a ragged rim. Illustrative." },
  { key: "cloudBlue", label: "star cloud blue", min: 0, max: 1.5, step: 0.01, unit: "", default: 1, perTemplate: { ngc_4414: 1.0}, about: "How far the outer clouds' colour goes from cream to blue-white. Colour for appearance." },
  { key: "cloudWarmR", label: "star cloud cream radius", min: 0.5, max: 20, step: 0.1, unit: "kpc", default: 5, perTemplate: { ngc_4414: 4 }, about: "The clouds are cream inside 0.6 of this radius and blue-white outside 1.6 of it, kpc. Colour for appearance." },
  { key: "cloudRich", label: "star cloud sectors", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.5 }, about: "How far the star clouds keep to two or three rich stretches about the star cloud azimuth; 0 all round. Illustrative." },
  { key: "cloudAz", label: "star cloud azimuth", min: 0, max: 360, step: 1, unit: "°", default: 0, perTemplate: { ngc_4414: 320 }, about: "The galactocentric azimuth of the richest star clouds, degrees. Illustrative." },
  { key: "cloudGlow", label: "star cloud glow", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0 }, about: "A soft glow under each star cloud's group (the map's clump level: the clump glow's gain and tint); 0 none. Illustrative." },
  { key: "cloudComplex", label: "star cloud complexes", min: 0, max: 0.5, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0 }, about: "The share of the star clouds that are large complexes: four times the points over a wider glow. Illustrative." },
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
  { key: "meshDepth", label: "dust mesh", min: 0, max: 3, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 1.4}, about: "The plane style: the depth of a tangled mesh of dust filaments on the edges of cells stretched along the spiral (they fork and join at angles), in full threads; 0 none. Illustrative." },
  { key: "meshCell", label: "mesh cell", min: 60, max: 2000, step: 10, unit: "pc", default: 300, perTemplate: { ngc_4414: 220 }, about: "A mesh cell's size across the spiral, parsecs: the cream light between the filaments. Illustrative." },
  { key: "meshWidth", label: "mesh filament", min: 10, max: 300, step: 1, unit: "pc", default: 40, perTemplate: { ngc_4414: 24}, about: "A mesh filament's typical full width at half depth, parsecs (each edge between half and 1.7 of it). Illustrative." },
  { key: "meshStretch", label: "mesh stretch", min: 1, max: 2.5, step: 0.05, unit: "×", default: 1.8, about: "How many times longer along the spiral than across a mesh cell is. Illustrative." },
  { key: "meshOpen", label: "mesh open", min: 0, max: 0.95, step: 0.01, unit: "", default: 0.35, perTemplate: { ngc_4414: 0.45 }, about: "The share of the mesh's edges left out: an open, branching mesh with loose ends. Illustrative." },
  { key: "meshFine", label: "fine mesh", min: 0, max: 2, step: 0.01, unit: "", default: 0.6, perTemplate: { ngc_4414: 1.0 }, about: "A finer mesh (cells and filaments at half the size) as a share of the mesh's depth. Illustrative." },
  { key: "meshKnot", label: "mesh knots", min: 0, max: 3, step: 0.01, unit: "", default: 0.8, about: "The dark clumps where three of the mesh's edges meet, as a share of a filament's depth. Illustrative." },
  { key: "meshBroad", label: "broad mesh", min: 0, max: 2, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 1.0 }, about: "A coarser mesh (cells twice the size, soft filaments two and a half times as wide) as a share of the mesh's depth: the broad lanes. Illustrative." },
  { key: "meshFollow", label: "mesh on the dust", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0 }, about: "How far the mesh gathers where the drawn dust is (the map's threads and lanes within 150 pc); 0 alike everywhere. Illustrative." },
  { key: "puffs", label: "light puffs", min: 0, max: 3, step: 0.01, unit: "×", default: 0, perTemplate: { ngc_4414: 0.2}, about: "The plane style: how far the light between the dust gathers into puffs a few hundred parsecs across (a multiplier about 1, brightest at a puff's heart); 0 none. Illustrative." },
  { key: "puffSize", label: "puff size", min: 40, max: 1000, step: 5, unit: "pc", default: 220, about: "A light puff's size, parsecs (a finer set at under half of it rides on them). Illustrative." },
  { key: "puffNear", label: "puffs by the dust", min: 0, max: 4, step: 0.05, unit: "×", default: 1, about: "How much stronger the puffs are where dust lies within 150 parsecs. Illustrative." },
  { key: "puffBlue", label: "outer puffs blue", min: 0, max: 1.5, step: 0.01, unit: "", default: 0.8, perTemplate: { ngc_4414: 0 }, about: "How far the puffs turn blue-white in the outer disc (from the outer blue's radius). Colour for appearance." },
  { key: "meshArc", label: "mesh on arcs", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0 }, about: "How far the mesh gathers into short flocculent arcs on the spiral (cream disc between); 0 even. Illustrative." },
  { key: "meshArcWidth", label: "mesh arc width", min: 200, max: 4000, step: 10, unit: "pc", default: 900, perTemplate: { ngc_4414: 600 }, about: "A mesh arc's width across the spiral at half the network's outer radius, parsecs (in proportion to the radius). Illustrative." },
  { key: "meshArcRun", label: "mesh arc length", min: 1, max: 12, step: 0.1, unit: "×", default: 3, perTemplate: { ngc_4414: 4 }, about: "A mesh arc's length along the spiral over its width. Illustrative." },
  { key: "meshHaze", label: "lane smoke", min: 0, max: 2, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.4}, about: "A soft mottled brown smoke over the mesh's arcs (the broad lanes the filaments lie in), in full threads; 0 none. Illustrative." },
  { key: "meshPiece", label: "mesh patches", min: 100, max: 5000, step: 10, unit: "pc", default: 1200, about: "The size of the noise that breaks the mesh into patches with clear disc between, parsecs. Illustrative." },
  { key: "meshGaps", label: "mesh gaps", min: 0, max: 1, step: 0.01, unit: "", default: 0.4, perTemplate: { ngc_4414: 0.27}, about: "The level of the patches' noise under which the mesh is left out: higher, more clear disc. Illustrative." },
  { key: "meshWarp", label: "mesh wiggle", min: 0, max: 1.5, step: 0.01, unit: "×", default: 0.4, about: "How far the mesh's plane is pushed about, as a share of a cell: its filaments bend. Illustrative." },
  { key: "taper", label: "taper", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0 }, about: "How far a thread thins toward the ends of its piece; 0 an even width to the end. Illustrative." },
  // S107 (builder NGC): ALL the plane style's dust - the map's threads and the march's mesh alike - gathered on the mesh's
  // arcs (one field), with clear zones of starlight between them; drawn in the march (no rebuild).
  { key: "arcGate", label: "dust gathered on arcs", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 1 }, about: "The plane style: how far all the drawn dust (threads and mesh alike) keeps to the mesh's arcs, clear starlight between; 0 as drawn. Illustrative." },
  { key: "arcClear", label: "dust between arcs", min: 0, max: 1, step: 0.01, unit: "", default: 0.1, perTemplate: { ngc_4414: 0.2}, about: "The share of the drawn dust left in the clear zones between the arcs (faint wisps). Illustrative." },
  { key: "arcLevel", label: "arc share", min: 0, max: 1, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 0.6 }, about: "The level of the arcs' noise above which the dust is kept: higher, narrower arcs and broader clear zones. Illustrative." },
  { key: "grainDim", label: "grain shade", min: 0, max: 1, step: 0.01, unit: "", default: 1, perTemplate: { ngc_4414: 0 }, about: "How far the light's grain dims the light between its puffs: 1 as drawn (bright and dark), 0 bright points only. Illustrative." },
  { key: "puffDim", label: "puff shade", min: 0, max: 1, step: 0.01, unit: "", default: 1, perTemplate: { ngc_4414: 0.3 }, about: "How far the light's puffs dim the light between them: 1 as drawn, 0 brightening only. Illustrative." },
  { key: "clearFloor", label: "clear zone floor", min: 0, max: 1, step: 0.01, unit: "", default: 0.45, about: "Where the arcs' gate takes the dust away, the light's patches are held at least at this level (0.5 their mean): the clear zones' starlight unshaded. Illustrative." },
  { key: "coreGain", label: "nucleus point", min: 0, max: 20, step: 0.05, unit: "×", default: 0, perTemplate: { milky_way: 0, ngc_4414: 3 }, about: "A compact bright point at the nucleus: the light there lifted by 1 plus this, falling off over the point's radius (the broad glow kept). Illustrative." },
  { key: "coreRadius", label: "nucleus point radius", min: 0.01, max: 1, step: 0.005, log: true, unit: "kpc", default: 0.12, perTemplate: { ngc_4414: 0.12 }, about: "The nucleus point's radius at 1/e, kpc. Illustrative." },
  { key: "coreWhite", label: "nucleus point white", min: 0, max: 1, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 0.9 }, about: "How far the nucleus point's lift goes toward a blue-white (it whitens a cream core). Colour for appearance." },
  { key: "glowDim", label: "nucleus glow dimmed", min: 0, max: 0.995, step: 0.005, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 0.97}, about: "The share of the light taken off the nucleus's broad glow at its centre (a gaussian), so the stretch does not flatten it into a blob. Colour for appearance." },
  { key: "glowRadius", label: "nucleus glow radius", min: 0.1, max: 5, step: 0.05, log: true, unit: "kpc", default: 1, perTemplate: { ngc_4414: 0.8}, about: "The radius at 1/e of the glow's dimming, kpc. Colour for appearance." },
  { key: "arcPeak", label: "dust on arc crests", min: 0, max: 3, step: 0.01, unit: "×", default: 1, perTemplate: { ngc_4414: 1.2 }, about: "The drawn dust's depth on the arcs' crests, a multiplier. Illustrative." },
  // S107 (builder NGC3): the gate's arcs as MANY NARROW LANES - thin soft-edged spiral ribbons at an open pitch, wandering,
  // broken into pieces of varied strength - in place of the noise's broad bands; inside them a pale veil with sparse dark
  // cores, and wisps feathering off their edges at an angle. Drawn in the march (no rebuild).
  { key: "laneForm", label: "narrow dust lanes", min: 0, max: 1, step: 1, unit: "", default: 0, perTemplate: { ngc_4414: 1 }, about: "The plane style's arcs: 0 the broad arcs of a spiral noise; 1 many narrow lanes along an open spiral, broken into pieces. Illustrative." },
  { key: "laneStep", label: "dust lane spacing", min: 100, max: 2000, step: 10, unit: "pc", default: 450, perTemplate: { ngc_4414: 1000 }, about: "The narrow lanes' spacing across the spiral at half the network's outer radius, parsecs (in proportion to the radius). Illustrative." },
  { key: "lanePitch", label: "dust lane pitch", min: 0.3, max: 3, step: 0.01, unit: "×", default: 1, perTemplate: { ngc_4414: 1.3 }, about: "The narrow lanes' pitch as a multiple of the drawn pitch (the network's): higher, a more open spiral. Illustrative." },
  { key: "laneCrest", label: "dust lane width", min: 0.05, max: 0.8, step: 0.01, unit: "×", default: 0.3, perTemplate: { ngc_4414: 0.3 }, about: "A narrow lane's full width at half depth as a share of the spacing (a soft gaussian edge). Illustrative." },
  { key: "laneWander", label: "dust lane wander", min: 0, max: 2, step: 0.01, unit: "×", default: 0.6, perTemplate: { ngc_4414: 0.8 }, about: "How far a lane wanders across the spiral, as a share of the spacing (lanes come near, part and join). Illustrative." },
  { key: "laneWanderSize", label: "dust lane wander size", min: 200, max: 6000, step: 10, unit: "pc", default: 1800, perTemplate: { ngc_4414: 1800 }, about: "The size of the noise that makes the lanes wander, parsecs. Illustrative." },
  { key: "lanePiece", label: "dust lane pieces", min: 200, max: 6000, step: 10, unit: "pc", default: 1500, perTemplate: { ngc_4414: 1300 }, about: "The size of the noise that breaks the lanes into pieces, parsecs (a piece is about this long). Illustrative." },
  { key: "laneGaps", label: "dust lane gaps", min: 0, max: 1, step: 0.01, unit: "", default: 0.4, perTemplate: { ngc_4414: 0.47}, about: "The level of the pieces' noise under which a lane is broken: higher, shorter pieces and wider gaps. Illustrative." },
  { key: "laneVary", label: "dust lane strength spread", min: 0, max: 1, step: 0.01, unit: "", default: 0.6, perTemplate: { ngc_4414: 0.7 }, about: "How far the pieces' depth varies from one to the next (0 all alike). Illustrative." },
  { key: "laneBranch", label: "dust lane branches", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.6 }, about: "A second set of lanes at a steeper pitch crossing the first (forks and joins), as a share of their depth; 0 none. Illustrative." },
  { key: "laneVeil", label: "dust lane veil", min: 0, max: 2, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.45 }, about: "A smooth pale tan veil filling each lane, in full threads (the light dust the filaments lie in); 0 none. Illustrative." },
  { key: "meshLight", label: "mesh lightness", min: 0, max: 1, step: 0.01, unit: "", default: 1, perTemplate: { ngc_4414: 0.3 }, about: "The share of the mesh's depth drawn outside the dark cores (1 as drawn, lower a paler mesh). Illustrative." },
  { key: "coreShare", label: "dark cores", min: 0, max: 0.6, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.35 }, about: "The share of a lane in dark cores, where the mesh keeps its full depth and more; 0 none. Illustrative." },
  { key: "coreSize", label: "dark core size", min: 30, max: 1000, step: 5, unit: "pc", default: 150, perTemplate: { ngc_4414: 140 }, about: "The size of the noise that places the dark cores, parsecs. Illustrative." },
  { key: "coreDepth", label: "dark core depth", min: 0, max: 5, step: 0.05, unit: "×", default: 2, perTemplate: { ngc_4414: 4 }, about: "The mesh's depth in a core as a multiple of its full depth. Illustrative." },
  { key: "laneWisps", label: "lane wisps", min: 0, max: 2, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.8 }, about: "Fine wisps leaving a lane's edges at an angle, in full threads; 0 none. Illustrative." },
  { key: "grainReach", label: "grain reach", min: 0.3, max: 1.5, step: 0.01, unit: "× outer", default: 1, perTemplate: { ngc_4414: 0.8 }, about: "How far the light's grain and puffs reach, as a multiple of the network's outer radius (they fade over its outer quarter): the disc's rim left smooth. Illustrative." },
  { key: "wispAngle", label: "lane wisp angle", min: 0, max: 80, step: 1, unit: "°", default: 35, about: "The wisps' angle to their lane, degrees. Illustrative." },
  // S109 (builder B): the disc's radial fall-off and the dust's broad bands, drawn in the march (uniforms, no rebuild).
  { key: "fall", label: "disc fall-off", min: 0, max: 8, step: 0.05, unit: "stops", default: 0, perTemplate: { milky_way: 0, ngc_4414: 2.0}, about: "All the disc's light (the field's and the points') dimmed by this many stops from the fall-off's start to its end radius, smoothly: the outer disc fainter than the inner; 0 none. (S109) Illustrative." },
  { key: "fallIn", label: "fall-off from", min: 0, max: 20, step: 0.1, unit: "kpc", default: 1, perTemplate: { ngc_4414: 7}, about: "Where the disc's fall-off starts, kpc. (S109) Illustrative." },
  { key: "fallOut", label: "fall-off to", min: 0.5, max: 30, step: 0.1, unit: "kpc", default: 10, perTemplate: { ngc_4414: 17 }, about: "Where the disc's fall-off is full, kpc (beyond it the fall-off holds). (S109) Illustrative." },
  { key: "fallCurve", label: "fall-off curve", min: 0.3, max: 3, step: 0.01, unit: "power", default: 1, perTemplate: { ngc_4414: 0.7}, about: "The fall-off's shape between its radii: below 1 it drops early, above 1 late. (S109) Illustrative." },
  { key: "fallPoints", label: "points fall-off", min: 0, max: 1, step: 0.01, unit: "", default: 1, about: "The share of the fall-off the points (star clouds, stars, knots) take. (S109) Illustrative." },
  { key: "dustArms", label: "dust arms", min: 0, max: 6, step: 1, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 4 }, about: "The plane style's drawn dust gathered into this many broad spiral bands (log-spiral arms of the viewer's own), clear zones of starlight between; 0 none (the dust as drawn). Display-only structure of the viewer's own (S109). Illustrative." },
  { key: "dustArmPitch", label: "dust arm pitch", min: 3, max: 45, step: 0.5, unit: "°", default: 18, perTemplate: { ngc_4414: 26}, about: "The dust bands' pitch angle, degrees. (S109) Illustrative." },
  { key: "dustArmWidth", label: "dust arm width", min: 0.05, max: 0.9, step: 0.01, unit: "", default: 0.4, about: "A band's full width as a share of the spacing between bands (a soft edge). (S109) Illustrative." },
  { key: "dustArmClear", label: "dust between dust arms", min: 0, max: 1, step: 0.01, unit: "", default: 0.15, perTemplate: { ngc_4414: 0.82}, about: "The share of the drawn dust left between the bands. (S109) Illustrative." },
  { key: "dustArmDeep", label: "dust on dust arms", min: 0, max: 3, step: 0.01, unit: "×", default: 1.2, perTemplate: { ngc_4414: 1.3}, about: "The drawn dust's depth on a band's crest, a multiplier. (S109) Illustrative." },
  { key: "dustArmPhase", label: "dust arm phase", min: 0, max: 360, step: 1, unit: "°", default: 0, about: "The dust arms turned about the centre, degrees; a network seed other than its default turns them further by golden-angle steps (a rerolled galaxy's arms lie elsewhere). (S109) Illustrative." },
  { key: "dustArmWander", label: "dust arm wander", min: 0, max: 0.5, step: 0.01, unit: "", default: 0.12, perTemplate: { ngc_4414: 0.5}, about: "How far a band wanders across the spiral, as a share of the spacing. (S109) Illustrative." },
  { key: "dustArmBreak", label: "dust arm breaks", min: 0, max: 1, step: 0.01, unit: "", default: 0.3, perTemplate: { ngc_4414: 0.85}, about: "How far a band is broken along its length into stronger and weaker stretches. (S109) Illustrative." },
  { key: "dustArmLit", label: "light between dust arms", min: 0, max: 4, step: 0.05, unit: "×", default: 0, perTemplate: { ngc_4414: 2.0}, about: "The light's puffs and bright grains made this much stronger between the bands (the star clouds' zones), weaker in them. (S109) Illustrative." },
  { key: "dustArmFrom", label: "dust arms from", min: 0, max: 10, step: 0.1, unit: "kpc", default: 0.8, about: "The bands come in over this radius, kpc (the dust inside as drawn). (S109) Illustrative." },
  // S109 (B2): the bands as swarms of the crisp narrow lanes (their number and depth), not a smooth veil.
  { key: "dustArmGaps", label: "dust arm lanes", min: 0, max: 0.6, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 0}, about: "How far the bands set how many narrow lanes there are: the lanes' gap level raised by this between the bands (lanes broken away) and lowered on them (a swarm of lanes); 0 the lanes as drawn. (S109) Illustrative." },
  { key: "dustArmNear", label: "dust arm near side", min: -1, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 0.4 }, about: "How much stronger the bands are toward the near-side azimuth (and weaker opposite); 0 alike all round. (S109) Illustrative." },
  { key: "cloudFall", label: "star clouds by the fall-off", min: 0, max: 2, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 2}, about: "The star clouds' number thinned by the disc's fall-off, this share of its stops (the dim outskirts carry few clouds: none left floating alone in the dark); 0 the clouds as drawn. (S109) Illustrative." },
  { key: "dustArmVary", label: "dust arm spread", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 0.9}, about: "How far the bands differ from one another in width and strength; 0 all alike. (S109) Illustrative." },
  { key: "inkTint", label: "ink brown", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 1 }, about: "How far the drawn dust's shade over the starlight goes to a warm sienna brown (its depth kept), in place of the grains' grey-red. (S109) Colour for appearance." },
  { key: "outerBlue", label: "outer disc blue", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 1}, about: "A blue-grey tint over the disc's light growing with the fall-off (none at its start, full at its end). (S109) Colour for appearance." },
  // S109 (B3): the star-cloud field - the light between the dust gathered into clumps of all sizes (an intermittent
  // field of several octaves: most of the disc quiet, some places bright heaps, heaps of heaps), drawn in the march.
  { key: "scAmt", label: "star cloud field", min: 0, max: 6, step: 0.05, unit: "×", default: 0, perTemplate: { milky_way: 0, ngc_4414: 2.6}, about: "How much brighter the light is at the heart of a clump of the star-cloud field (1 plus this, toward the clump tint); 0 none. Display-only structure of the viewer's own (S109). Illustrative." },
  { key: "scSize", label: "star cloud field size", min: 0.1, max: 4, step: 0.05, unit: "kpc", default: 0.8, perTemplate: { ngc_4414: 0.5 }, about: "The size of the field's largest heaps (the complexes), kpc; the clumps in them at a third, a sixth and a twelfth of it. (S109) Illustrative." },
  { key: "scSparse", label: "star cloud field sparseness", min: 0, max: 1, step: 0.01, unit: "", default: 0.55, perTemplate: { ngc_4414: 0.6 }, about: "How sparse the complexes are: higher, fewer and smaller heaps with more quiet disc between. (S109) Illustrative." },
  { key: "scGrain", label: "grain in the clouds", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.5 }, about: "How far the light's fine grain gathers into the field's heaps (1 only there, the disc between smooth); 0 the grain as drawn. (S109) Illustrative." },
  { key: "scBlue", label: "star cloud field blue", min: 0, max: 1.5, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 1}, about: "How far the heaps go blue-white outward (with the disc's fall-off); they are white inside. (S109) Colour for appearance." },
  { key: "scFrom", label: "star cloud field from", min: 0, max: 10, step: 0.1, unit: "kpc", default: 2, perTemplate: { ngc_4414: 4.5 }, about: "The field's heaps come in over this radius, kpc (from half of it). (S109) Illustrative." },
  { key: "scBands", label: "star clouds between bands", min: 0, max: 1, step: 0.01, unit: "", default: 0.7, about: "How far the heaps keep to the clear zones between the dust bands; 0 alike everywhere. (S109) Illustrative." },
  { key: "inkOpaque", label: "ink opaque brown", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.5}, about: "How far the drawn dust's shade is an opaque dark brown over the light (a grey dimming with the lost light replaced by brown) in place of a coloured extinction: a thin skirt keeps the disc's own colour, no orange fringe; 0 the extinction as drawn. (S109) Colour for appearance." },
  { key: "inkBrown", label: "ink brown light", min: 0, max: 2, step: 0.01, unit: "×", default: 1, perTemplate: { ngc_4414: 1.2}, about: "Under the opaque ink: how much of the lost light comes back as brown (1 a mid brown; lower a darker, deeper core). (S109) Colour for appearance." },
  { key: "scCrisp", label: "star cloud field grain", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 0.8 }, about: "How far a heap's light is broken into the light grain's puffs (a cluster of bright grains and knots); 0 a smooth glow. (S109) Illustrative." },
  { key: "dustArmInner", label: "dust arm breaks inside", min: 0.05, max: 1, step: 0.01, unit: "×", default: 1, perTemplate: { ngc_4414: 0.2}, about: "The size of the noises that break and bend the bands, at the centre, as a share of theirs at half the network's outer radius (1 the same everywhere; lower, the inner bands broken into shorter pieces). (S109) Illustrative." },
  { key: "dustArmFork", label: "dust arm forks", min: 0, max: 1.5, step: 0.01, unit: "", default: 0, about: "A second set of bands at a steeper pitch, as a share of the first's strength: forks, spurs and restarts; 0 none. (S109) Illustrative." },
  { key: "glowShape", label:"nucleus glow dim shape", min: 0.3, max: 2, step: 0.01, unit: "power", default: 2, perTemplate: { ngc_4414: 1 }, about: "The power in the glow's dimming, exp(-(r / radius)^power): 2 a gaussian (as before), lower a cusp that takes most off the very centre and leaves the glow round it graded. (S109) Colour for appearance." },
  { key: "glowLift", label: "nucleus glow lift", min: 0, max: 3, step: 0.01, unit: "×", default: 0, perTemplate: { ngc_4414: 1.5 }, about: "A broad soft glow lifted over the nucleus (1 plus this at the centre, falling as exp(-r / radius) over the glow-lift radius), toward a pale yellow-cream; 0 none. (S109) Colour for appearance." },
  { key: "glowLiftRadius", label: "nucleus glow lift radius", min: 0.1, max: 6, step: 0.05, unit: "kpc", default: 1.5, perTemplate: { ngc_4414: 0.25 }, about: "The lifted glow's radius at 1/e, kpc. (S109) Colour for appearance." },
  { key: "glowCream", label: "nucleus glow cream", min: 0, max: 1, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 0 }, about: "How far the lifted glow goes toward a pale yellow-cream (0 the light's own colour). (S109) Colour for appearance." },
  { key: "scSpots", label:"star cloud field spots", min: 0, max: 3, step: 0.05, unit: "", default: 0, perTemplate: { ngc_4414: 1 }, about: "Small isolated bright knots (tens of parsecs) scattered over the field's zone, in the heaps' tint, as a share of a heap's brightness; 0 none. (S109) Illustrative." },
  // S109 (B4): the star cloud points' brightness capped before the bloom (FluxPoints' illCap, CloudsLayer.tsx): the
  // brightest of them were spread by the bloom into soft round discs; capped they stay crisp points.
  { key: "cloudCap", label: "star cloud brightness cap", min: 0, max: 5000, step: 1, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 3}, about: "The brightest a star cloud point may be (its largest channel in the frame's linear light, before the bloom): the bright ones stay crisp points, not soft discs; 0 none. (S109) Illustrative." },
  { key: "coreHot", label: "nucleus white core", min: 0, max: 30, step: 0.1, unit: "×", default: 0, perTemplate: { milky_way: 0, ngc_4414: 3}, about: "A small white-hot core inside the nucleus's cream glow: the light lifted by 1 plus this at the centre, bluer than the glow, falling as a gaussian over its radius; 0 none. (S109) Colour for appearance." },
  { key: "coreHotRadius", label: "nucleus white core radius", min: 0.005, max: 0.5, step: 0.005, log: true, unit: "kpc", default: 0.04, perTemplate: { ngc_4414: 0.09 }, about: "The white core's radius at 1/e, kpc. (S109) Colour for appearance." },
  // S110 (B2): the light's lumps - soft-edged white clumps of light of many sizes (an irregular field: several octaves
  // of noise over a warped plane, thresholded, so the lumps differ in size, merge into banks and leave real gaps; no
  // lattice, no one cell size), packed between the dust, smooth inside. Drawn in the march (uniforms, no rebuild).
  { key: "lumps", label: "light lumps", min: 0, max: 6, step: 0.05, unit: "×", default: 0, perTemplate: { milky_way: 0, ngc_4414: 1.0}, about: "How much brighter the light is inside a lump (1 plus this, toward the lumps' white); 0 none. Display-only structure of the viewer's own (S110). Illustrative." },
  { key: "lumpSize", label: "lump size", min: 40, max: 2000, step: 5, unit: "pc", default: 300, perTemplate: { ngc_4414: 160}, about: "The lumps' largest scale, parsecs (finer octaves at a half, a quarter and an eighth of it shape their edges). (S110) Illustrative." },
  { key: "lumpCover", label: "lump cover", min: 0, max: 1, step: 0.01, unit: "", default: 0.45, perTemplate: { ngc_4414: 0.5}, about: "How much of the disc the lumps cover: higher, more and larger lumps running together into banks. (S110) Illustrative." },
  { key: "lumpSoft", label: "lump edge", min: 0.01, max: 0.3, step: 0.005, unit: "", default: 0.06, perTemplate: { ngc_4414: 0.3}, about: "How soft a lump's edge is (the width of the threshold): small, a crisp outline. (S110) Illustrative." },
  { key: "lumpWarp", label: "lump warp", min: 0, max: 3, step: 0.01, unit: "", default: 1.2, perTemplate: { ngc_4414: 0.6 }, about: "How far the plane is pushed about before the lumps are drawn, in lumps: irregular outlines, no lattice. (S110) Illustrative." },
  { key: "lumpBanks", label: "lump banks", min: 0, max: 1, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 0.5 }, about: "How far the cover varies over a few kiloparsecs: banks of merged lumps here, gaps of plain disc there. (S110) Illustrative." },
  { key: "lumpNear", label: "lumps by the dust", min: 0, max: 1, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 0.5 }, about: "How far the lumps gather beside the dust lanes (the cover raised at a lane's margin, lowered on its crest). (S110) Illustrative." },
  { key: "lumpWhite", label: "lump white", min: 0, max: 1.5, step: 0.01, unit: "", default: 1, perTemplate: { ngc_4414: 1.2}, about: "How far a lump's light goes from the disc's own colour to white (blue-white outward, with the star clouds' blue). (S110) Colour for appearance." },
  { key: "lumpFrom", label: "lumps from", min: 0, max: 10, step: 0.1, unit: "kpc", default: 1.5, perTemplate: { ngc_4414: 1.5 }, about: "The lumps come in over this radius, kpc (from half of it). (S110) Illustrative." },
  { key: "lumpTo", label: "lumps full to", min: 0.5, max: 25, step: 0.1, unit: "kpc", default: 6, perTemplate: { ngc_4414: 6 }, about: "The lumps are at their brightest out to this radius, kpc, and fall to the outer share by 1.8 of it. (S110) Illustrative." },
  { key: "lumpRim", label: "outer lumps", min: 0, max: 1, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 0}, about: "The lumps' brightness in the outer disc as a share of the ring's. (S110) Illustrative." },
  { key: "lumpGrain", label: "grain in the lumps", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { ngc_4414: 1 }, about: "How far the light's fine grain is taken out of the lumps (1 none inside them: smooth lumps); 0 the grain as drawn. (S110) Illustrative." },
  // S110 (B2): the disc's hue - red taken off the disc's light outside the nucleus, so a salmon-orange reads yellow-tan.
  { key: "tanHue", label: "disc yellow", min: 0, max: 0.3, step: 0.005, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 0.05}, about: "The share of red taken off the disc's light (green given half of it, blue a tenth), from the yellow's radius outward: a salmon disc toward a yellow-tan; 0 none. (S110) Colour for appearance." },
  { key: "tanFrom", label: "disc yellow from", min: 0, max: 5, step: 0.05, unit: "kpc", default: 0.6, perTemplate: { ngc_4414: 0.6 }, about: "The yellow comes in over this radius, kpc (from half of it): the nucleus keeps its own colour. (S110) Colour for appearance." },
  // S110 (B2): the sparks (flocClouds.ts buildSparks, CloudsLayer.tsx) - a sparse tier of single sharp bright points.
  { key: "sparkCount", label: "sparks", min: 0, max: 2000, step: 1, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 0 }, about: "How many single sharp bright points (blue-white stars and young clusters) lie over the disc, most in its outer zone; 0 none. Display-only, of the viewer's own (S110). Illustrative." },
  { key: "sparkGain", label: "spark brightness", min: 10, max: 1e7, step: 0.01, log: true, unit: "L☉", default: 30000, perTemplate: { ngc_4414: 30000 }, about: "The faintest spark's light, L☉ over the white point (the field's scale, with the exposure). (S110) Illustrative." },
  { key: "sparkRange", label: "spark range", min: 1, max: 1000, step: 0.01, log: true, unit: "×", default: 30, perTemplate: { ngc_4414: 30 }, about: "The brightest spark over the faintest. (S110) Illustrative." },
  { key: "sparkSlope", label: "spark slope", min: 0.3, max: 4, step: 0.05, unit: "", default: 1.2, perTemplate: { ngc_4414: 1.2 }, about: "The sparks' brightness law's index: smaller, more bright ones. (S110) Illustrative." },
  { key: "sparkSize", label: "spark size", min: 0.3, max: 3, step: 0.05, unit: "px", default: 0.8, perTemplate: { ngc_4414: 0.8 }, about: "A spark's sprite, pixels: small, a sharp point. (S110) Illustrative." },
  { key: "sparkFrom", label: "sparks from", min: 0.2, max: 20, step: 0.1, unit: "kpc", default: 5, perTemplate: { ngc_4414: 5 }, about: "The outer zone the most of the sparks lie in starts here, kpc. (S110) Illustrative." },
  { key: "sparkTo", label: "sparks to", min: 1, max: 25, step: 0.1, unit: "kpc", default: 12, perTemplate: { ngc_4414: 12 }, about: "The sparks' outer zone ends here, kpc. (S110) Illustrative." },
  { key: "sparkInner", label: "inner sparks", min: 0, max: 1, step: 0.01, unit: "", default: 0.15, perTemplate: { ngc_4414: 0.15 }, about: "The share of the sparks inside the outer zone (cream-white there). (S110) Illustrative." },
  { key: "sparkCap", label: "spark brightness cap", min: 0, max: 5000, step: 0.1, unit: "", default: 0, perTemplate: { ngc_4414: 0 }, about: "The brightest a spark may be (its largest channel in the frame's linear light, before the bloom): bright sparks stay sharp points, not the bloom's soft discs; 0 none. (S110) Illustrative." },
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

/**
 * S107 fix F2: what the plane style's channel reads with no threads drawn (`netDepth` 0, NGC 4414's default: its dust
 * is the march's mesh) - flocNet.ts buildNetChannel then builds no dust grid and paints only the light between (its
 * clouds: `litScale`, its reach: `litReach` x `outerRadius`, its seed) and the star clouds' glow (flocClouds.ts
 * buildClouds: the cloud controls, the network's outer radius - `innerRadius`, `outerRadius` - and the seed; the dust it
 * reads there is none). Every other shaping value (the threads' controls - spacing, piece size, gaps, wiggle, feathers,
 * arcs, the ring, the mesh of lanes and spurs - and the S105 style's) changes no byte of it.
 */
const LIGHT_ONLY_KEYS: ReadonlySet<string> = new Set([
  "style", "netDepth", "seed", "litScale", "litReach", "innerRadius", "outerRadius",
  "cloudCount", "cloudGroup", "cloudMembers", "cloudReach", "cloudStart", "cloudSlope", "cloudRange", "cloudRich", "cloudAz", "cloudGlow", "cloudComplex",
]);

/**
 * The shaping values the channel is keyed on (and built from): all of them, but in the plane style with no threads
 * drawn the values it does not read are held at the feature's defaults, so moving one rebuilds nothing (S107 fix F2:
 * NGC 4414's "thread spacing" and "dust piece size" rebuilt the plane, 0.1-0.2 s in the worker and a 28.8 MB upload,
 * for the same bytes).
 */
export function channelShapeOf(p: IllParams): FlocShape {
  const shape = shapeOf(p);
  if (shape.style < 0.5 || shape.netDepth > 0) return shape;
  const out = { ...shape } as unknown as Record<string, number>;
  for (const k of SHAPE_KEYS) if (!LIGHT_ONLY_KEYS.has(k)) out[k] = DEFAULTS[k];
  return out as unknown as FlocShape;
}

/** The feature's channel of the shared map at these parameters, for this frame; null where it draws nothing. */
export function flocChannel(p: IllParams, frame: IllFrame | null): Uint8Array | null {
  const shape = channelShapeOf(p);
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
  const lanes = Math.max(2, Math.round((2 * Math.PI * r * Math.tan(lp)) / (Math.max(v("laneStep"), 20) * 1e-3)));
  const branch = Math.max(2, Math.round(lanes * 0.6));
  return {
    illFlocLaneA: [v("style") >= 0.5 && v("laneForm") >= 0.5 ? 1 : 0, lanes, Math.tan(lp), Math.max(0.02, v("laneCrest"))],
    illFlocLaneB: [v("laneWander"), Math.max(v("laneWanderSize"), 50) * 1e-3, Math.max(v("lanePiece"), 50) * 1e-3, v("laneGaps")],
    illFlocLaneC: [v("laneVary"), v("laneBranch"), v("laneVeil"), v("laneWisps")],
    illFlocLaneD: [branch, Math.tan(Math.min(75, ((lp * 180) / Math.PI) * 1.6) * (Math.PI / 180)), (v("wispAngle") * Math.PI) / 180, lp],
    illFlocCore: [v("meshLight"), v("coreShare"), Math.max(v("coreSize"), 10) * 1e-3, v("coreDepth")],
  };
}

/**
 * S109 (B2): the star clouds thinned by the disc's fall-off (the GLSL's illFlocFallAt, its share `cloudFall`): their
 * density times the light's multiplier there, so the dim outskirts carry few clouds. Undefined where it changes
 * nothing (the clouds as drawn, bit for bit); the values it is built from, for the layer's memo key.
 */
export function cloudThin(p: IllParams): { key: number[]; thin: ((r: number) => number) | undefined } {
  const v = (k: string) => p[k] ?? DEFAULTS[k];
  const stops = v("fall") * v("cloudFall");
  const from = v("fallIn");
  const to = Math.max(v("fallOut"), from + 0.01);
  const curve = v("fallCurve");
  if (!(stops > 0)) return { key: [0], thin: undefined };
  const thin = (r: number) => {
    const t = Math.min(1, Math.max(0, (r - from) / (to - from)));
    return 2 ** (-stops * (t * t * (3 - 2 * t)) ** curve);
  };
  return { key: [stops, from, to, curve], thin };
}

/** S109 (B): the fall-off's and the bands' uniforms (floc.ts GLSL illFlocFallAt, illFlocBand). */
export function fallBandUniforms(p: IllParams): Record<string, number[]> {
  const v = (k: string) => p[k] ?? DEFAULTS[k];
  const rad = Math.PI / 180;
  return {
    illFlocFall: [v("fall"), v("fallIn"), Math.max(v("fallOut"), v("fallIn") + 0.01), v("fallCurve")],
    illFlocFallB: [v("fallPoints"), v("outerBlue"), v("inkTint"), v("inkOpaque")],
    illFlocBandA: [Math.round(v("dustArms")), Math.tan(Math.min(45, Math.max(3, v("dustArmPitch"))) * rad), v("dustArmWidth"), (v("dustArmPhase") + (v("seed") === DEFAULTS.seed ? 0 : 137.508 * v("seed"))) * rad],
    illFlocBandB: [v("dustArmClear"), v("dustArmDeep"), v("dustArmWander"), v("dustArmBreak")],
    illFlocBandC: [v("dustArmLit"), v("dustArmFrom"), v("dustArmGaps"), v("dustArmNear")],
    illFlocBandD: [v("dustArmVary"), v("nearAz") * rad, v("dustArmInner"), v("dustArmFork")],
    illFlocScA: [v("style") >= 0.5 ? v("scAmt") : 0, Math.max(v("scSize"), 0.05), v("scSparse"), v("scGrain")],
    illFlocScB: [v("scBlue"), v("scFrom"), v("scBands"), v("scSpots")],
    // z: the heaps moved with a network seed other than its default (a rerolled galaxy's heaps lie elsewhere; 0 at it).
    // w: the seed's own turn of the bands (rad; 0 at the default seed), which alone re-rolls the bands' widths and
    // strengths: the phase slider turns them and re-rolls nothing (S109 review: 360 degrees draws what 0 draws).
    illFlocScC: [v("scCrisp"), v("inkBrown"), v("seed") === DEFAULTS.seed ? 0 : (37.17 * v("seed")) % 97, v("seed") === DEFAULTS.seed ? 0 : 137.508 * v("seed") * rad],
    illFlocGlow: [v("glowShape"), v("glowLift"), Math.max(v("glowLiftRadius"), 0.05), v("glowCream")],
    illFlocHot: [v("coreHot"), Math.max(v("coreHotRadius"), 0.005), 0, 0],
    // S110 (B2): the lumps and the disc's yellow.
    illFlocLumpA: [v("style") >= 0.5 ? v("lumps") : 0, Math.max(v("lumpSize"), 10) * 1e-3, v("lumpCover"), Math.max(v("lumpSoft"), 0.005)],
    illFlocLumpB: [v("lumpWarp"), v("lumpBanks"), v("lumpNear"), v("lumpWhite")],
    illFlocLumpC: [v("lumpFrom"), Math.max(v("lumpTo"), 0.1), v("lumpRim"), v("lumpGrain")],
    // The hue is the plane style's, as the lumps are: on another style the slider draws nothing (S110 review: it moved
    // the Milky Way's frame).
    illFlocTan: [v("style") >= 0.5 ? v("tanHue") : 0, v("tanFrom"), 0, 0],
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
  // S110 (B2): the warmth's hue toward a yellow-tan (0 as S106).
  uniform float illFlocWarmY;
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
  // S109 (B): the fall-off - x stops, y from (kpc), z to (kpc), w the curve's power; and (illFlocFallB) x the points'
  // share, y the outer blue, z the ink's brown.
  uniform vec4 illFlocFall;
  uniform vec4 illFlocFallB;
  // S109 (B): the bands - A: x arms (0 off), y tan(pitch), z the width over the spacing, w the phase (rad); B: x the dust
  // left between, y the depth on a crest, z the wander (spacings), w the breaks; C: x the light between, y from (kpc).
  uniform vec4 illFlocBandA;
  uniform vec4 illFlocBandB;
  uniform vec4 illFlocBandC;
  // S109 (B2): C z how far the bands set the narrow lanes' gaps (fewer pieces between, more on them), w the near side's
  // bias; D x how far the bands differ in width and strength, y the near side's azimuth (rad, the plane style's).
  uniform vec4 illFlocBandD;
  // The plane style's ring (declared here for the bands' inner scale: S109 B3): x the inner radius, y and z the ring's
  // in and out (kpc), w the network's outer radius.
  uniform vec4 illFlocRingA;
  // S109 (B3): the star-cloud field - A: x its gain (0 off), y the complexes' size (kpc), z the sparseness, w how far the
  // fine grain gathers into it; B: x the blue outward, y from (kpc), z how far it keeps between the bands, w the spots.
  uniform vec4 illFlocScA;
  uniform vec4 illFlocScB;
  // x how far a heap's light is broken into the grain's puffs; y the ink's brown's darkness (a share of its colour); z
  // the heaps' shift and w the bands' turn with a network seed other than its default (both 0 at it).
  uniform vec4 illFlocScC;
  // S109 (B3): the nucleus's glow - x the power of its dimming (2 a gaussian), y a broad lift's gain, z its radius
  // (kpc), w how far the lift goes to a pale yellow-cream.
  uniform vec4 illFlocGlow;
  // S109 (B4): the nucleus's white-hot core - x its gain (0 none), y its radius at 1/e (kpc).
  uniform vec4 illFlocHot;
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
  // S109 (B): the fall-off's progress at radius r (0 inside its start, 1 from its end, the curve's power between) and
  // its multiplier on the light (1 where it is off: exactly, so a template without it is drawn bit for bit).
  float illFlocFallT(float r) {
    return pow(smoothstep(illFlocFall.y, max(illFlocFall.z, illFlocFall.y + 0.01), r), illFlocFall.w);
  }
  float illFlocFallAt(float r) {
    return illFlocFall.x > 0.0 ? exp2(-illFlocFall.x * illFlocFallT(r)) : 1.0;
  }
  // The points' share of it (the hook points).
  float illFlocPts(vec2 rp) {
    return illFlocFall.x > 0.0 && illFlocFallB.x > 0.0 ? exp2(-illFlocFall.x * illFlocFallB.x * illFlocFallT(rp.x)) : 1.0;
  }
  // S109 (B): the broad dust bands - a few log-spiral arms of the viewer's own, wandering and broken along their length.
  // x the multiplier on the drawn dust (1 where the bands are off or inside their start), y the band's level in [0, 1],
  // z the clear zone's (1 - the level); y and z 0 where the bands are off or inside their start.
  // One set of bands' level at rp (xy its place, kpc): tp tan(pitch), ph the phase, k the set's noise offset, sc the
  // noises' scale (1 as drawn; S109 B3 smaller toward the centre, so the inner bands break as often as the outer).
  float illFlocBandE(vec2 rp, vec2 xy, float r, float tp, float ph, float k, float sc) {
    float v = illFlocBandA.x * (log(r) / tp - rp.y + ph) / 6.2831853;
    v += illFlocBandB.z * 2.0 * (0.65 * illFlocVN(xy / (3.0 * sc) + vec2(13.1 + k, 4.7)) + 0.35 * illFlocVN(xy / (1.2 * sc) + vec2(2.9, 21.3 + k)) - 0.5);
    float f = fract(v) - 0.5;
    // S109 (B2): each band its own width and strength (a hash of its index round the turn, turned with the seed), and
    // the near side's bands the stronger (the plane style's near azimuth).
    float id = mod(floor(v), illFlocBandA.x) + 5.7 * k;
    float hw = illFlocBandD.x > 0.0 ? mix(1.0, 0.55 + 0.9 * illFlocHash(vec2(id + 3.1 * illFlocScC.w, 1.9)), illFlocBandD.x) : 1.0;
    float s = f / max(illFlocBandA.z * hw, 0.02);
    float e = exp(-2.773 * s * s);
    if (illFlocBandD.x > 0.0) e *= mix(1.0, 0.4 + 1.2 * illFlocHash(vec2(id + 3.1 * illFlocScC.w, 7.3)), illFlocBandD.x);
    if (illFlocBandB.w > 0.0) e *= 1.0 - illFlocBandB.w * (1.0 - smoothstep(0.25, 0.7, illFlocVN(xy / (2.5 * sc) + vec2(17.1 + k, 3.3))));
    return e;
  }
  vec3 illFlocBand(vec2 rp) {
    if (illFlocBandA.x < 0.5) return vec3(1.0, 0.0, 0.0);
    float r = max(rp.x, 0.05);
    vec2 xy = r * vec2(cos(rp.y), sin(rp.y));
    // S109 (B3): BandD z the noises' scale at the centre (1 as before: the same at every radius), w a second set of
    // bands at a steeper pitch (forks, restarts), its share; the scale is full from half the network's outer radius.
    float sc = illFlocBandD.z < 1.0 ? mix(max(illFlocBandD.z, 0.05), 1.0, smoothstep(0.0, 0.5 * illFlocRingA.w, r)) : 1.0;
    float e = illFlocBandE(rp, xy, r, illFlocBandA.y, illFlocBandA.w, 0.0, sc);
    if (illFlocBandD.w > 0.0) e = max(e, illFlocBandD.w * illFlocBandE(rp, xy, r, 1.45 * illFlocBandA.y, illFlocBandA.w + 1.3, 31.7, sc));
    if (illFlocBandC.w != 0.0) e *= max(1.0 + illFlocBandC.w * cos(rp.y - illFlocBandD.y), 0.0);
    float w = illFlocBandC.y > 0.0 ? smoothstep(0.5 * illFlocBandC.y, illFlocBandC.y, r) : 1.0;
    float e1 = min(e, 1.0);
    // x the dust's multiplier, at most 1 (the dust left between the bands); the depth on a crest is the caller's (the
    // crisp lanes' and mesh's only: illFlocVeil), y the level (above 1 on a strong near-side band), z the clear zone's.
    return vec3(mix(1.0, mix(illFlocBandB.x, 1.0, e1), w), e * w, (1.0 - e1) * w);
  }
  // S109 (B3): the star-cloud field at xy (kpc): x the heaps' level (0 quiet disc, about 1 at a bright heap's heart: a
  // heavy tail, most of the disc near 0), y the complexes' soft mask (where the grain gathers), z the spots. Several
  // octaves multiplied (a cascade): the complexes' mask, the clumps in them at a third, a sixth, a twelfth of their size.
  vec3 illFlocSc(vec2 xy) {
    float s = illFlocScA.y;
    xy += vec2(illFlocScC.z, 0.61 * illFlocScC.z);
    float lv = 0.36 + 0.3 * illFlocScA.z;
    float mn = 0.65 * illFlocVN(xy / s + vec2(19.3, 7.1)) + 0.35 * illFlocVN(xy / (0.5 * s) + vec2(3.3, 41.9));
    float m = smoothstep(lv, lv + 0.2, mn);
    float c = 0.5 * illFlocVN(xy / (0.33 * s) + vec2(11.7, 2.9)) + 0.3 * illFlocVN(xy / (0.16 * s) + vec2(5.1, 23.3)) + 0.2 * illFlocVN(xy / (0.08 * s) + vec2(29.9, 13.7));
    // A clump's edge crisp and ragged (the fine octaves in the threshold: a cauliflower outline), its inside knotted;
    // the clumps sparse outside the complexes, many and bright in them (the threshold lowered there).
    float k = smoothstep(0.58, 0.64, c + 0.14 * m);
    float knot = 0.5 + 0.5 * smoothstep(0.35, 0.75, illFlocVN(xy / (0.035 * s) + vec2(7.7, 51.3)));
    float spot = 0.0;
    if (illFlocScB.w > 0.0) spot = illFlocScB.w * smoothstep(0.86, 0.97, illFlocVN(xy / (0.05 * s) + vec2(37.1, 3.9))) * (0.3 + 0.7 * m);
    return vec3((0.3 + 0.7 * m) * k * knot * (0.5 + 0.5 * smoothstep(0.62, 0.8, c + 0.14 * m)), m, spot);
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
  vec2 illFlocLaneSet(vec2 rp, vec2 xy, float n, float tA, float k, float gl) {
    float v = n * (log(max(rp.x, 0.05)) / tA - rp.y) / 6.2831853;
    // The noises' sizes shrink toward the centre (to 0.35 of them at the axis, all of them from half the outer radius):
    // the inner lanes, crowded by the spiral, broken as often per lane as the outer.
    float inScale = mix(0.35, 1.0, smoothstep(0.0, 0.5 * illFlocRingA.w, rp.x));
    vec2 wq = xy / (illFlocLaneB.y * inScale);
    v += illFlocLaneB.x * 2.0 * (0.65 * illFlocVN(wq + vec2(k, 2.3)) + 0.35 * illFlocVN(2.5 * wq + vec2(4.1, k)) - 0.5);
    float j = floor(v);
    float f = v - j - 0.5;
    float s = f / max(illFlocLaneA.w, 0.02);
    float crest = exp(-2.773 * s * s);
    float margin = max(exp(-0.693 * s * s) - crest, 0.0) * (1.0 - smoothstep(0.32, 0.5, abs(f)));
    // Each lane its own pieces (the lane's index taken round the turn, so the azimuth's wrap joins).
    float jm = mod(j, n);
    vec2 o = vec2(fract(jm * 0.6180339) * 97.0, fract(jm * 0.4142136) * 89.0 + k);
    float pl = illFlocLaneB.z * inScale;
    float pn = 0.7 * illFlocVN(xy / pl + o) + 0.3 * illFlocVN(xy / (0.4 * pl) + o.yx);
    float piece = smoothstep(gl - 0.1, gl + 0.1, pn);
    float strength = 1.0 - illFlocLaneC.x + illFlocLaneC.x * smoothstep(gl, min(gl + 0.35, 1.0), pn);
    return vec2(crest, margin) * piece * strength;
  }
  vec2 illFlocLanes(vec2 rp) {
    vec2 xy = rp.x * vec2(cos(rp.y), sin(rp.y));
    // S109 (B2): the broad bands set how many of the narrow lanes there are - the pieces' gap level raised between the
    // bands (the lanes broken away: clear zones of starlight) and lowered on them (a swarm of crisp lanes).
    float gl = illFlocLaneB.w;
    if (illFlocBandA.x > 0.5 && illFlocBandC.z != 0.0) {
      vec3 b = illFlocBand(rp);
      gl = clamp(gl + illFlocBandC.z * (b.z - min(b.y, 1.0)), 0.0, 1.0);
    }
    vec2 l = illFlocLaneSet(rp, xy, illFlocLaneA.y, illFlocLaneA.z, 1.3, gl);
    if (illFlocLaneC.y > 0.0) l = max(l, illFlocLaneC.y * illFlocLaneSet(rp, xy, illFlocLaneD.x, illFlocLaneD.y, 7.9, gl));
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
  // S108 (the grazing handover, index.ts illGraze): the ink's share (a veil on the thin screen, faded toward edge-on
  // by the registry) handed to the dust's own layer as the ray grazes, so the edge-on disc keeps the network's dust as
  // a lane in its layer rather than losing it with the veil.
  float illFlocAv(vec2 rp) {
    float ink = illGraze >= 1.0 ? illFlocInk : illFlocInk * illGraze;
    if (illFlocDepth <= 0.0 || ink >= 1.0) return 0.0;
    return illFlocDepth * (1.0 - ink) * illFlocShape(illFlocRead(rp).x) * (illFlocStyle > 0.5 ? illFlocGateAt(rp) * illFlocBand(rp).x : 1.0);
  }
  float illFlocYoung(vec2 rp) {
    if (illFlocYoungGain <= 0.0) return 1.0;
    return 1.0 + illFlocYoungGain * illFlocRead(rp).z;
  }
  // S110 (B2): the light's lumps - A: x the gain (0 off), y the largest scale (kpc), z the cover, w the edge's softness;
  // B: x the warp (lumps), y the banks, z the gathering beside the lanes, w the white; C: x from (kpc), y full to (kpc),
  // z the outer share, w how far the grain is taken out of them. illFlocTan: x the red taken off the disc, y from (kpc).
  uniform vec4 illFlocLumpA;
  uniform vec4 illFlocLumpB;
  uniform vec4 illFlocLumpC;
  uniform vec4 illFlocTan;
  // The lumps' field at xy (kpc) and a shift of the threshold (dl, the lanes' gathering): in [0, 1], 0 the plain disc,
  // 1 inside a lump (a gentle dome, smooth inside, the edge as soft as illFlocLumpA.w). The plane warped twice over (a
  // lump and three lumps across), then four octaves of value noise, each turned off the lattice's axes, and a broad
  // octave that sets the cover by region (banks and gaps): no lattice, no one size.
  float illFlocLumpField(vec2 xy, float dl) {
    // The lumps move with a network seed other than its default, as the star clouds do (illFlocScC.z, 0 at the
    // default): a rerolled galaxy's lumps lie elsewhere (S110 review: they sat still under a reroll).
    vec2 q = xy / illFlocLumpA.y + vec2(illFlocScC.z, 0.61 * illFlocScC.z);
    vec2 w1 = vec2(illFlocVN(0.33 * q + vec2(3.1, 17.9)), illFlocVN(0.33 * q + vec2(27.3, 5.4))) - 0.5;
    vec2 w2 = vec2(illFlocVN(mat2(0.8, 0.6, -0.6, 0.8) * q * 1.1 + vec2(8.8, 1.2)), illFlocVN(mat2(0.8, 0.6, -0.6, 0.8) * q * 1.1 + vec2(4.4, 33.1))) - 0.5;
    q += illFlocLumpB.x * (2.0 * w1 + 0.7 * w2);
    // Five octaves (the finest at a sixteenth: a lump's outline bumpy, a cauliflower's, not a smooth blob).
    float f = 0.42 * illFlocVN(q + vec2(11.3, 2.7))
      + 0.26 * illFlocVN(mat2(0.6, -0.8, 0.8, 0.6) * q * 2.07 + vec2(1.7, 9.2))
      + 0.16 * illFlocVN(mat2(-0.28, 0.96, -0.96, -0.28) * q * 4.13 + vec2(23.5, 6.1))
      + 0.10 * illFlocVN(mat2(0.96, 0.28, -0.28, 0.96) * q * 8.31 + vec2(5.9, 41.3))
      + 0.06 * illFlocVN(mat2(0.28, -0.96, 0.96, 0.28) * q * 16.7 + vec2(31.1, 17.3));
    float bank = illFlocLumpB.y * 0.16 * (illFlocVN(0.12 * q + vec2(13.7, 29.1)) - 0.5) * 2.0;
    float lv = mix(0.64, 0.4, illFlocLumpA.z) - bank - dl;
    float l = smoothstep(lv, lv + illFlocLumpA.w, f);
    return l * (0.6 + 0.4 * smoothstep(lv, lv + 0.15, f));
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
    // S109 (B): the broad bands (x the dust's multiplier; z the clear zone's weight, where the light's puffs gather).
    vec3 band = illFlocStyle > 0.5 ? illFlocBand(rp) : vec3(1.0, 0.0, 0.0);
    // S109 (B2): the depth on a band's crest taken by the crisp filaments and cores only (not the lanes' smooth veil
    // added below): a band is a swarm of deeper lanes, not a smooth stripe.
    if (band.y > 0.0 && av > 0.0) av *= mix(1.0, illFlocBandB.y, band.y);
    float bandLit = illFlocBandC.x > 0.0 ? mix(1.0, 1.0 + illFlocBandC.x, band.z) / (1.0 + 0.5 * illFlocBandC.x * band.y) : 1.0;
    // S107 (NGC3): the lanes' pale veil and the wisps feathering off their edges at an angle (a sparse cellular mesh
    // drawn out along the wisps' heading), both in the plane style's ring.
    if (lanes && (illFlocLaneC.z > 0.0 || illFlocLaneC.w > 0.0) && rp.x < illFlocRingA.w) {
      float ring = illFlocRingAt(rp);
      // The veil reaches past the filaments into the margins, fading: the lane's edge feathered.
      av += illFlocDepth * illFlocInk * illFlocLaneC.z * ring * (lane.x + 0.6 * lane.y);
      if (illFlocLaneC.w > 0.0 && lane.y * ring > 0.02) {
        float p = illFlocLaneD.w + illFlocLaneD.z;
        vec2 t = vec2(sin(p) * cos(rp.y) - cos(p) * sin(rp.y), sin(p) * sin(rp.y) + cos(p) * cos(rp.y));
        vec2 xy = rp.x * vec2(cos(rp.y), sin(rp.y));
        float w = illFlocCells(xy, t, 0.7 * illFlocMeshA.x, 0.7 * illFlocMeshA.y, 2.5, 0.55, 0.0, 19.3);
        av += illFlocDepth * illFlocInk * illFlocLaneC.w * ring * lane.y * w;
      }
    }
    if (band.x != 1.0) av *= band.x;
    if (av > 0.0) {
      // S106: the ceiling - the depth saturates softly toward illFlocCap magnitudes (a brown, never black).
      av = illFlocCap * (1.0 - exp(-av / illFlocCap));
      vec3 law = max(vec3(cloudExt.g) + illFlocRed * (cloudExt - vec3(cloudExt.g)), vec3(0.02 * cloudExt.g));
      // S109 (B): the ink toward a warm sienna (red kept, blue taken), the middle channel's depth kept.
      if (illFlocFallB.z > 0.0) law = mix(law, cloudExt.g * vec3(0.42, 1.0, 1.75), illFlocFallB.z);
      vec3 dv = exp(-av * law);
      // S109 (B3): the ink as an opaque brown - the light dimmed grey by the middle channel's depth and the lost light
      // replaced by a dark brown share of it: a thin skirt shades the disc's own colour (no orange fringe), a deep core
      // goes to the brown.
      if (illFlocFallB.w > 0.0) {
        float tg = exp(-av * cloudExt.g);
        dv = mix(dv, vec3(tg) + (1.0 - tg) * illFlocScC.y * vec3(0.30, 0.17, 0.09), illFlocFallB.w);
      }
      veil *= dv;
    }
    // The patches: the light swelled and thinned about the patches' mean level.
    if (illFlocStyle > 0.5) {
      // S107 (NGC): where the gate takes a thread away, so goes the shade the map draws on it and at its margins (the
      // clouds' level held up to its floor illFlocLitDim.z): no grey ghost of the thread in a clear zone.
      float lit = illFlocGate.x > 0.0 ? mix(max(map.y, illFlocLitDim.z), map.y, clamp(gate, 0.0, 1.0)) : map.y;
      veil *= (1.0 + illFlocPatch * lit) / (1.0 + 0.5 * illFlocPatch);
      // S109 (B3): the star-cloud field (heaps of all sizes between the dust, white inside, blue-white outward), and
      // its complexes' mask for the grain below; none on the dust, none inside its start.
      vec3 sc = vec3(0.0, 1.0, 0.0);
      if (illFlocScA.x > 0.0 && rp.x < rHi) {
        sc = illFlocSc(rp.x * vec2(cos(rp.y), sin(rp.y)));
        float from = smoothstep(0.5 * illFlocScB.y, max(illFlocScB.y, 0.01), rp.x);
        // The grain gathers into the complexes, and is gone inside the field's start (a smooth inner disc).
        sc.y *= from;
        float g = (1.0 - smoothstep(0.0, 0.3, map.x)) * from * mix(1.0, band.z, illFlocScB.z);        float t = clamp(illFlocScB.x * (illFlocFall.x > 0.0 ? illFlocFallT(rp.x) : 0.0), 0.0, 1.0);
        // A heap's light broken into the grain's own puffs (illFlocScC.x of it): a heap is a cluster of bright grains
        // and knots, not a smooth glow, at every range.
        float tex = 1.0;
        if (illFlocScC.x > 0.0) {
          vec2 gq = rp.x * vec2(cos(rp.y), sin(rp.y)) / max(illFlocGrainS, 1e-3);
          float pn = 0.6 * illFlocVN(gq + vec2(3.7, 8.1)) + 0.4 * illFlocVN(mat2(0.6, -0.8, 0.8, 0.6) * gq * 2.31 + vec2(1.3, 9.9));
          tex = mix(1.0, 0.2 + 1.8 * smoothstep(0.4, 0.8, pn), illFlocScC.x);
        }
        veil *= vec3(1.0) + illFlocScA.x * g * (sc.x * tex + sc.z) * mix(vec3(0.86, 1.0, 1.22), vec3(0.74, 0.98, 1.45), t);
      }
      // S110 (B2): the lumps' field here (the lanes' margins raise the cover, their crests lower it).
      float lump = 0.0;
      if (illFlocLumpA.x > 0.0 && rp.x < rHi) lump = illFlocLumpField(rp.x * vec2(cos(rp.y), sin(rp.y)), illFlocLumpB.z * 0.08 * (2.0 * lane.y - lane.x));
      // S106 (C3): the light's grain - small bright puffs, stronger just outside a dust thread (the map read 60 pc in
      // and out along the radius: the threads run mostly along the azimuth), none on the dust itself.
      if (illFlocGrain > 0.0 && rp.x < rHi) {
        vec2 xy = rp.x * vec2(cos(rp.y), sin(rp.y)) / max(illFlocGrainS, 1e-3);
        float n = 0.6 * illFlocVN(xy) + 0.4 * illFlocVN(mat2(0.6, -0.8, 0.8, 0.6) * xy * 2.31 + vec2(7.3, 1.9));
        float puff = smoothstep(0.42, 0.86, n);
        float side = max(illFlocRead(rp + vec2(0.06, 0.0)).x, illFlocRead(rp - vec2(0.06, 0.0)).x);
        float bare = 1.0 - smoothstep(0.0, 0.25, map.x);
        // Fading out over the outer fifth of the network's radius: the disc's faint rim is not broken into puffs.
        float amt = bandLit * illFlocGrain * (1.0 + illFlocGrainNear * smoothstep(0.05, 0.35, side)) * bare * (1.0 - smoothstep(0.75 * illFlocGrainR, illFlocGrainR, rp.x));
        if (illFlocScA.w > 0.0 && illFlocScA.x > 0.0) amt *= mix(1.0, 1.8 * sc.y, illFlocScA.w);
        if (illFlocLumpC.w > 0.0) amt *= 1.0 - illFlocLumpC.w * lump;
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
        float amt = bandLit * illFlocPuff.x * bare * edge * (1.0 +illFlocPuff.z * (illFlocPuff.z > 0.0 ? illFlocNear(rp) : 0.0));
        float cool = illFlocPuff.w * smoothstep(0.7 * illFlocCoolR, 1.5 * illFlocCoolR, rp.x);
        veil *= max(vec3(1.0) + amt * (heap - 0.25 * illFlocLitDim.y) * mix(vec3(1.0), vec3(0.8, 0.97, 1.3), min(cool, 1.0)), vec3(0.0));
      }
      // S110 (B2): the lumps - brightest in their ring, the outer share beyond, white inside and blue-white outward
      // (with the star clouds' blue and the fall-off's progress).
      if (lump > 0.0) {
        float rw = smoothstep(0.5 * illFlocLumpC.x, max(illFlocLumpC.x, 0.01), rp.x) * mix(1.0, illFlocLumpC.z, smoothstep(illFlocLumpC.y, 1.8 * illFlocLumpC.y, rp.x));        float t = clamp(illFlocScB.x * (illFlocFall.x > 0.0 ? illFlocFallT(rp.x) : 0.0), 0.0, 1.0);
        // The tints take the disc's tan (red over green about 1.15, blue 0.88) to a neutral white at a lift near 1.5.
        vec3 tint = mix(vec3(1.0), mix(vec3(0.8, 1.0, 1.28), vec3(0.76, 0.98, 1.36), t), illFlocLumpB.w);
        veil *= vec3(1.0) + illFlocLumpA.x * rw * lump * tint;
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
      if (illFlocWarmY > 0.0) veil *= mix(vec3(1.0 + 0.2 * w, 1.0 + 0.03 * w, 1.0 - 0.32 * w), vec3(1.0 + 0.1 * w, 1.0 + 0.07 * w, 1.0 - 0.3 * w), illFlocWarmY);
      else veil *= vec3(1.0 + 0.2 * w, 1.0 + 0.03 * w, 1.0 - 0.32 * w);
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
      veil *= 1.0 - illFlocNucPt.z * (illFlocGlow.x == 2.0 ? exp(-q * q) : exp(-pow(q, illFlocGlow.x)));
    }
    // S109 (B3): a broad soft glow lifted over the nucleus, toward a pale yellow-cream.
    if (illFlocGlow.y > 0.0) {
      float e = exp(-rp.x / illFlocGlow.z);
      veil *= vec3(1.0) + illFlocGlow.y * e * mix(vec3(1.0), vec3(1.12, 1.0, 0.72), illFlocGlow.w);
    }
    // S109 (B4): the white-hot core - a small gaussian lift with more blue and green than red, so the cream glow's
    // peak goes to white a few pixels across and the glow falls from it.
    if (illFlocHot.x > 0.0) {
      float q = rp.x / max(illFlocHot.y, 1e-3);
      veil *= vec3(1.0) + illFlocHot.x * exp(-q * q) * vec3(1.0, 1.3, 1.9);
    }
    if (illFlocLitDim.w > 0.0) {
      float q = rp.x / max(illFlocNucPt.x, 1e-3);
      veil *= vec3(1.0) + illFlocLitDim.w * exp(-q * q) * mix(vec3(1.0), vec3(0.85, 0.97, 1.25), illFlocNucPt.y);
    }
    // S110 (B2): the disc's yellow - red taken off outside the nucleus and green given (blue a little: blue
    // over green falls a little, as the photograph's): the hue turns from salmon toward yellow-tan without the light dimming.
    if (illFlocTan.x > 0.0) {
      float k = illFlocTan.x * smoothstep(0.5 * illFlocTan.y, max(illFlocTan.y, 0.01), rp.x);
      veil *= vec3(1.0 - k, 1.0 + 0.5 * k, 1.0 + 0.1 * k);
    }
    // S109 (B): the disc's fall-off, and the outer disc's blue-grey growing with it.
    if (illFlocFall.x > 0.0) veil *= illFlocFallAt(rp.x);
    if (illFlocFallB.y > 0.0) veil *= mix(vec3(1.0), vec3(0.8, 0.94, 1.3), illFlocFallB.y * illFlocFallT(rp.x));
    return veil;
  }
`,
  hooks: { dustAv: "illFlocAv", youngGain: "illFlocYoung", veil: "illFlocVeil", points: "illFlocPts" },
  // S109 (B): the points' fall-off fades toward edge-on with the veil's, so field and points stay in step.
  graze: { points: "fade" },
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
      illFlocWarmY: p.warmYellow ?? DEFAULTS.warmYellow,
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
      ...fallBandUniforms(p),
    };
  },
};
