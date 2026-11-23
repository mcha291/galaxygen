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

import { createElement, lazy, Suspense } from "react";
import { ILL_MAP_CHANNELS, type IllControl, type IllFeature, type IllFrame, type IllLayerProps, type IllParams, memoOn } from "./feature";
import type { CloudShape } from "./flocClouds";
import { FLOC_ARRAYS, FLOC_MAP, type FlocShape, SHAPE_KEYS, buildFlocChannel, geometryOf } from "./flocMap";
import { buildNetChannel } from "./flocNet";

const CONTROLS: readonly IllControl[] = [
  {
    key: "depth", label: "network depth", min: 0, max: 10, step: 0.05, unit: "mag", default: 0, perTemplate: { milky_way: 0, ngc_4414: 2 },
    about: "The depth at the centre of one full filament of the dust network, magnitudes of A_V; 0 no network. Illustrative.",
  },
  {
    key: "ink", label: "network ink", min: 0, max: 1, step: 0.01, unit: "", default: 0.75,
    about: "The share of the depth drawn as a veil over all the light on its line of sight (sharp brown threads, the same on both sides of the disc); the rest is dust in the dust's own thin layer, which the march makes darker on the near side. Illustrative.",
  },
  { key: "redness", label: "network redness", min: 0, max: 4, step: 0.05, unit: "×", default: 1.5, perTemplate: { ngc_4414: 2.2 }, about: "The veil's colour: 0 a grey veil, 1 the dust grains' own reddening, higher a redder brown. Colour for appearance." },
  { key: "hardness", label: "filament edge", min: 0, max: 1, step: 0.01, unit: "", default: 0.3, perTemplate: { ngc_4414: 0 }, about: "How crisp a filament's edge is: 0 a soft stroke, 1 an inked one with its faint margins gone. Illustrative." },
  {
    key: "patch", label: "patch contrast", min: 0, max: 2, step: 0.01, unit: "×", default: 0, perTemplate: { milky_way: 0, ngc_4414: 1.5 },
    about: "How far the disc's light swells and thins in soft patches about its mean (a multiplier on all the light at each place); 0 a smooth disc. Illustrative.",
  },
  {
    key: "clump", label: "clump glow", min: 0, max: 8, step: 0.05, unit: "×", default: 0, perTemplate: { milky_way: 0, ngc_4414: 4 },
    about: "How much brighter all the light is at the centre of a young clump (a multiplier of 1 plus this, in the clump tint); 0 none. Illustrative.",
  },
  {
    key: "young", label: "clump young light", min: 0, max: 30, step: 0.1, unit: "×", default: 0, perTemplate: { milky_way: 0, ngc_4414: 2 },
    about: "How much more of the model's own clustered young light a clump holds (1 plus this at its centre): its blue flecks gathered into the clumps. Read only while the young light is clustered in the march. Illustrative.",
  },
  { key: "blue", label: "clump tint", min: 0, max: 1, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 0.1 }, about: "The clump glow's colour: 0 the light's own, 1 a blue-white. Colour for appearance." },
  {
    key: "warmth", label: "inner warmth", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 0.3 },
    about: "A cream tint over the inner disc's light, fading outward: the old disc of the photograph. Colour for appearance.",
  },
  { key: "warmRadius", label: "warmth radius", min: 0.5, max: 15, step: 0.1, unit: "kpc", default: 4.5, perTemplate: { ngc_4414: 6 }, about: "The radius at which the warm tint has fallen to 1/e, kpc. Colour for appearance." },
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
  { key: "outerRadius", label: "outer radius", min: 2, max: 23, step: 0.5, unit: "kpc", default: 9, perTemplate: { ngc_4414: 10 }, about: "The network fades from 0.7 of this radius to nothing at it, kpc; the patches and clumps reach 1.3 of it. Illustrative." },
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
  // S106 (builder C): the network drawn in the disc's plane (flocNet.ts) - isotropic feathered dust on short arcs, cream clouds between.
  {
    key: "style", label: "network style", min: 0, max: 1, step: 1, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 1 },
    about: "0: S105's strands and lace on spiral lattices; 1: S106's network drawn in the disc's plane - feathered dust clouds on short spiral arcs and cream clouds of light between them. Illustrative.",
  },
  { key: "netScale", label: "dust cloud size", min: 60, max: 1500, step: 10, unit: "pc", default: 350, perTemplate: { ngc_4414: 350 }, about: "The plane style's dust clouds' size, parsecs (finer octaves ride on them). Illustrative." },
  { key: "netWarp", label: "dust curl", min: 0, max: 3, step: 0.01, unit: "×", default: 0.8, perTemplate: { ngc_4414: 0.6 }, about: "How far the plane is pushed about before the dust is drawn, as a share of the cloud size: the pieces curl and feather. Illustrative." },
  { key: "netGaps", label: "dust gaps", min: 0, max: 1, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 0.4 }, about: "The level of the plane style's noise under which there is no dust: higher, less dust and wider gaps. Illustrative." },
  { key: "netSoft", label: "dust softness", min: 0.01, max: 0.5, step: 0.01, unit: "", default: 0.12, perTemplate: { ngc_4414: 0.12 }, about: "How softly a dust cloud's edge fades out. Illustrative." },
  { key: "netFeather", label: "dust feathers", min: 0, max: 1, step: 0.01, unit: "", default: 0.7, perTemplate: { ngc_4414: 0.7 }, about: "How far the dust is broken into feathered ridges and holes (a ridged noise); 0 smooth clouds. Illustrative." },
  { key: "netArc", label: "dust on arcs", min: 0, max: 1, step: 0.01, unit: "", default: 0.6, perTemplate: { ngc_4414: 0.9 }, about: "How far the dust keeps to short arcs on the drawn spiral (the flocculent pattern); 0 anywhere. Illustrative." },
  { key: "arcWidth", label: "arc width", min: 100, max: 3000, step: 10, unit: "pc", default: 500, perTemplate: { ngc_4414: 450 }, about: "An arc's width across the spiral, parsecs. Illustrative." },
  { key: "arcStretch", label: "arc length", min: 0.5, max: 10, step: 0.1, unit: "×", default: 3, perTemplate: { ngc_4414: 5 }, about: "An arc's length along the spiral over its width. Illustrative." },
  { key: "netDepth", label: "dust drawn", min: 0, max: 4, step: 0.01, unit: "×", default: 1.6, perTemplate: { ngc_4414: 1.6 }, about: "The plane style's drawn depth, in full filaments (the network depth scales it again, without a rebuild). Illustrative." },
  { key: "litScale", label: "light cloud size", min: 40, max: 1500, step: 10, unit: "pc", default: 220, perTemplate: { ngc_4414: 220 }, about: "The size of the cream clouds of light between the dust, parsecs. Illustrative." },
  { key: "litKnots", label: "bright knots", min: 0, max: 1, step: 0.01, unit: "", default: 0.5, perTemplate: { ngc_4414: 0.5 }, about: "How many small bright knots the clouds of light hold (drawn with the clump glow). Illustrative." },
  { key: "litReach", label: "light reach", min: 1, max: 3, step: 0.05, unit: "× outer", default: 1.7, perTemplate: { ngc_4414: 1.7 }, about: "How far the plane style's clouds of light reach, as a multiple of the network's outer radius. Illustrative." },
  {
    key: "cap", label: "dust ceiling", min: 0.1, max: 20, step: 0.05, unit: "mag", default: 20, perTemplate: { ngc_4414: 1.2 },
    about: "The veil's depth saturates softly toward this many magnitudes: the thickest dust stays a deep red-brown, never black. Colour for appearance.",
  },
  {
    key: "nucleus", label: "nucleus cream", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 1 },
    about: "A cream-yellow tint over the nucleus's light (its march draws a blue-cyan core under the stretch): 0 none, 1 full. Colour for appearance.",
  },
  // S106: the star clouds (flocClouds.ts, FlocClouds.tsx), a points layer of the feature's own, drawn in the plane style.
  {
    key: "cloudCount", label: "star cloud points", min: 0, max: 80000, step: 500, unit: "", default: 0, perTemplate: { milky_way: 0, ngc_4414: 30000 },
    about: "How many points the star clouds hold (in the plane style only): loose groups over the bright light between the dust, densest in the outer disc; 0 none. Illustrative.",
  },
  { key: "cloudGain", label: "star cloud brightness", min: 10, max: 1e7, step: 0.01, log: true, unit: "L☉", default: 3000, perTemplate: { ngc_4414: 3000 }, about: "The faintest star cloud point's light, L☉ over the white point (the field's scale, with the exposure). Illustrative." },
  { key: "cloudRange", label: "star cloud range", min: 1, max: 1000, step: 0.01, log: true, unit: "×", default: 20, about: "The brightest star cloud point over the faintest. Illustrative." },
  { key: "cloudSlope", label: "star cloud slope", min: 0.3, max: 4, step: 0.05, unit: "", default: 1.3, about: "The brightness law's index: smaller, more bright points. Illustrative." },
  { key: "cloudSize", label: "star cloud point size", min: 0.5, max: 4, step: 0.1, unit: "px", default: 1.5, about: "A star cloud point's sprite, pixels. Illustrative." },
  { key: "cloudGroup", label: "star cloud size", min: 10, max: 800, step: 5, unit: "pc", default: 120, about: "A star cloud's gaussian radius, parsecs (each between half and one and a half of it). Illustrative." },
  { key: "cloudMembers", label: "star cloud members", min: 1, max: 60, step: 1, unit: "", default: 8, about: "A star cloud's mean number of points. Illustrative." },
  { key: "cloudStart", label: "star clouds from", min: 0, max: 2, step: 0.01, unit: "× outer", default: 0.7, about: "Where the star clouds come in to their full number, as a multiple of the network's outer radius (a quarter of it inside). Illustrative." },
  { key: "cloudReach", label: "star cloud reach", min: 0.5, max: 3, step: 0.01, unit: "× outer", default: 1.5, about: "How far the star clouds reach, as a multiple of the network's outer radius, the edge pushed in and out by a noise: a ragged rim. Illustrative." },
  { key: "cloudBlue", label: "star cloud blue", min: 0, max: 1.5, step: 0.01, unit: "", default: 1, about: "How far the outer clouds' colour goes from cream to blue-white. Colour for appearance." },
  { key: "cloudWarmR", label: "star cloud cream radius", min: 0.5, max: 20, step: 0.1, unit: "kpc", default: 5, about: "The clouds are cream inside 0.6 of this radius and blue-white outside 1.6 of it, kpc. Colour for appearance." },
  { key: "nucleusRadius", label: "nucleus radius", min: 0.05, max: 5, step: 0.01, unit: "kpc", default: 0.8, about: "The radius at which the nucleus's tint has fallen to 1/e, kpc. Colour for appearance." },
];

const DEFAULTS: Readonly<Record<string, number>> = Object.fromEntries(CONTROLS.map((c) => [c.key, c.default]));

/** The shaping parameters among the feature's own (the others are uniforms). */
export function shapeOf(p: IllParams): FlocShape {
  return Object.fromEntries(SHAPE_KEYS.map((k) => [k, p[k] ?? DEFAULTS[k]])) as unknown as FlocShape;
}

/** The star clouds' shaping values among the feature's own. */
export function cloudShapeOf(p: IllParams): CloudShape {
  const v = (k: string) => p[k] ?? DEFAULTS[k];
  return {
    count: v("cloudCount"),
    groupPc: v("cloudGroup"),
    members: v("cloudMembers"),
    reach: v("cloudReach"),
    start: v("cloudStart"),
    slope: v("cloudSlope"),
    range: v("cloudRange"),
  };
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
  flocBuild.count += 1;
  return map;
});

/** The feature's channel of the shared map at these parameters, for this frame; null where it draws nothing. */
export function flocChannel(p: IllParams, frame: IllFrame | null): Uint8Array | null {
  const shape = shapeOf(p);
  return channel(frame, flocDrawn(p), ...SHAPE_KEYS.map((k) => shape[k]));
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
  // The feature's byte of the shared map read (flocMap.ts: signed about 128): x the dust, sqrt(shape / ${MAX}); y the
  // patches' level about their mean, in [-0.5, 0.5] (0, which changes nothing, where the light is not known: under a
  // filament, beyond the light's reach, where there is no map - a byte of 0 is never written); z a young clump's
  // level (0 its edge, 1 its centre).
  vec3 illFlocRead(vec2 rp) {
    float b = rp.x < rHi ? illMap(rp).g * 255.0 : 0.0;
    if (b < 0.5) return vec3(0.0);
    float s = (b - 128.0) / 127.0;
    float l = max(-s, 0.0);
    float level = clamp((l - ${FLOOR}) / (0.5 - ${FLOOR}), 0.0, 1.0) - 0.5;
    return vec3(max(s, 0.0), level * smoothstep(0.0, ${FLOOR}, l), clamp((l - 0.5) * 2.0, 0.0, 1.0));
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
    return illFlocDepth * (1.0 - illFlocInk) * illFlocShape(illFlocRead(rp).x);
  }
  float illFlocYoung(vec2 rp) {
    if (illFlocYoungGain <= 0.0) return 1.0;
    return 1.0 + illFlocYoungGain * illFlocRead(rp).z;
  }
  vec3 illFlocVeil(vec2 rp) {
    vec3 veil = vec3(1.0);
    vec3 map = illFlocRead(rp);
    // The ink: the grains' own depth per magnitude in each channel, its spread about the middle channel's times the
    // redness (0 grey, 1 the grains' own).
    float av = illFlocDepth * illFlocInk * illFlocShape(map.x);
    if (av > 0.0) {
      // S106: the ceiling - the depth saturates softly toward illFlocCap magnitudes (a brown, never black).
      av = illFlocCap * (1.0 - exp(-av / illFlocCap));
      vec3 law = max(vec3(cloudExt.g) + illFlocRed * (cloudExt - vec3(cloudExt.g)), vec3(0.02 * cloudExt.g));
      veil *= exp(-av * law);
    }
    // The patches: the light swelled and thinned about the patches' mean level.
    veil *= max(1.0 + illFlocPatch * map.y, 0.0);
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
    return veil;
  }
`,
  hooks: { dustAv: "illFlocAv", youngGain: "illFlocYoung", veil: "illFlocVeil" },
  arrays: FLOC_ARRAYS,
  layer: FlocLayer,
  map: { channels: ILL_MAP_CHANNELS.floc, build: (p, context) => [flocChannel(p, context.frame)] },
  uniforms: (p) => {
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
    };
  },
};
