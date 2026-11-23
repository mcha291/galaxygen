// The dust lanes (BUILD_VIII row 107, S107, D275): narrow, translucent, reddening lanes along the arms' ridges and the
// bar's leading edges, with feathers. ILLUSTRATIVE: the model's gas ridge is 1-2 kpc wide and its clouds are isolated
// ellipses, so no published field draws a lane 100 pc wide; this feature draws them itself, placed by published
// geometry - the arm pieces' loci, the bar's half-length and axis ratio, the bar's angle read off
// pattern_density_contrast, the gas contrast along each ridge - and shaped by a seeded drawing of the viewer's own.
//
// What it hands the march: a polar map of the lanes' shape (lanesMap.ts: 2000 x 3600 bytes over 0-30 kpc, 15 pc by
// 0.1 degree, built once per arrays frame and per shaping value, about a tenth of a second), read two ways:
//   dustAv  the share of the depth that is NOT ink, as extra face-on A_V in the dust's own layer: the march reddens
//           through it per channel as it does through the clouds, and the points behind it are dimmed the same.
//   veil    the ink: the rest of the depth as a screen over the ray's whole light. A depth in the dust's layer dims
//           only what lies behind it - half the old stars and most of a bar stand in front, so a lane there is a
//           faint grey-blue mark however deep - and the goal pictures' lanes are dark red-brown lines drawn over the
//           arms; the veil's law is the grains' own reddening, steepened by the redness slider.
// The depth, the ink, the redness, the edge and the mottle are uniforms: no rebuild.

import { ClampToEdgeWrapping, DataTexture, LinearFilter, RedFormat, RepeatWrapping, UnsignedByteType } from "three";

import { type IllControl, type IllFeature, type IllFrame, type IllParams, memoOn } from "./feature";
import { LANE_ARRAYS, LANE_MAP, type LaneShape, SHAPE_KEYS, buildLaneMap, geometryOf } from "./lanesMap";

const CONTROLS: readonly IllControl[] = [
  {
    key: "depth", label: "lane depth", min: 0, max: 10, step: 0.05, unit: "mag", default: 0.85, perTemplate: { milky_way: 0.85, ngc_4414: 0.95 },
    about: "The depth at the centre of one full strand of a lane, magnitudes of A_V; 0 no lanes. Illustrative.",
  },
  {
    key: "ink", label: "lane ink", min: 0, max: 1, step: 0.01, unit: "", default: 0.8, perTemplate: { milky_way: 0.8, ngc_4414: 0.75 },
    about: "The share of the depth drawn as a veil over all the light on its line of sight (a lane inked over the picture); the rest is dust in the dust's own thin layer, which dims and reddens only the stars behind it. Illustrative.",
  },
  {
    key: "redness", label: "lane redness", min: 0, max: 4, step: 0.05, unit: "×", default: 1.6, perTemplate: { milky_way: 1.6, ngc_4414: 1.0 },
    about: "The veil's colour: 0 a grey veil, 1 the dust grains' own reddening, higher a redder brown. Colour for appearance.",
  },
  {
    key: "hardness", label: "lane edge", min: 0, max: 1, step: 0.01, unit: "", default: 0.4, perTemplate: { milky_way: 0.4, ngc_4414: 0.45 },
    about: "How crisp a lane's edge is: 0 a soft Gaussian stroke that fades out, 1 an inked stroke with a flat dark core and a sharp edge (its faint margins gone). Illustrative.",
  },
  {
    key: "mottle", label: "mottle", min: 0, max: 1, step: 0.01, unit: "", default: 0.6, perTemplate: { milky_way: 0.6, ngc_4414: 0.6 },
    about: "How much a lane's depth swells and thins from place to place across it: knots, holes and a ragged edge; 0 a smooth stroke. Illustrative.",
  },
  { key: "grain", label: "mottle grain", min: 20, max: 600, step: 5, unit: "pc", default: 150, about: "The size of the mottle's patches, parsecs (a finer set a third of it rides on them). Illustrative." },
  {
    key: "offset", label: "lane offset", min: -400, max: 800, step: 5, unit: "pc", default: 80, perTemplate: { milky_way: 80, ngc_4414: 60 },
    about: "How far to the inner (concave) side of an arm's ridge the lane's centre line lies, parsecs; below 0 the outer side. Illustrative.",
  },
  {
    key: "width", label: "strand width", min: 30, max: 500, step: 5, unit: "pc", default: 110, perTemplate: { milky_way: 110, ngc_4414: 100 },
    about: "One strand's full width at half depth, parsecs (it swells and thins along its length by the clumping). Illustrative.",
  },
  { key: "strands", label: "strands", min: 1, max: 6, step: 1, unit: "", default: 2, perTemplate: { milky_way: 2, ngc_4414: 4 }, about: "How many braided strands make a lane. Illustrative." },
  {
    key: "spread", label: "braid spread", min: 0, max: 1200, step: 10, unit: "pc", default: 260, perTemplate: { milky_way: 260, ngc_4414: 700 },
    about: "The width of the band the strands wander and cross in, parsecs. Illustrative.",
  },
  { key: "braidLength", label: "braid length", min: 0.3, max: 8, step: 0.1, unit: "kpc", default: 2.2, about: "The length along the arm over which the strands cross one another, kpc. Illustrative." },
  {
    key: "wiggle", label: "wiggle", min: 0, max: 600, step: 5, unit: "pc", default: 130, perTemplate: { milky_way: 130, ngc_4414: 160 },
    about: "How far the whole lane meanders about its line, parsecs (each strand a third as far again on its own). Illustrative.",
  },
  { key: "wiggleLength", label: "wiggle length", min: 0.2, max: 6, step: 0.05, unit: "kpc", default: 0.6, about: "The meander's length along the arm, kpc. Illustrative." },
  {
    key: "gaps", label: "gaps", min: 0, max: 0.9, step: 0.01, unit: "", default: 0.35, perTemplate: { milky_way: 0.35, ngc_4414: 0.25 },
    about: "The share of a lane's length that is broken away, so it reads as pieces: 0 unbroken. Illustrative.",
  },
  { key: "gapLength", label: "gap length", min: 0.3, max: 8, step: 0.1, unit: "kpc", default: 0.9, about: "The length of a lane's pieces and of the breaks between them, kpc. Illustrative." },
  { key: "clump", label: "clumping", min: 0, max: 1, step: 0.01, unit: "", default: 0.7, about: "How much a strand swells into dark knots and thins to threads along its length. Illustrative." },
  {
    key: "envelope", label: "envelope", min: 0, max: 1, step: 0.01, unit: "×", default: 0.05, perTemplate: { milky_way: 0.05, ngc_4414: 0.12 },
    about: "A faint band as wide as the braid under the strands, this share of a strand's depth: the lane's translucent margin. Illustrative.",
  },
  {
    key: "followGas", label: "follows the gas", min: 0, max: 1, step: 0.01, unit: "", default: 0.5,
    about: "How far a lane's depth follows the published gas contrast along its ridge: 0 the same depth everywhere, 1 none where the gas is not gathered. Illustrative.",
  },
  { key: "taper", label: "end taper", min: 0, max: 6, step: 0.1, unit: "kpc", default: 1.5, about: "A lane fades over this length at an arm's free ends, kpc (an end that joins another arm does not fade). Illustrative." },
  {
    key: "innerRadius", label: "inner radius", min: 0, max: 8, step: 0.05, unit: "kpc", default: 0.6, perTemplate: { milky_way: 0.6, ngc_4414: 0.5 },
    about: "The arms' lanes fade to nothing inside this radius, kpc. Illustrative.",
  },
  {
    key: "outerRadius", label: "outer radius", min: 2, max: 30, step: 0.5, unit: "kpc", default: 14, perTemplate: { milky_way: 12, ngc_4414: 9 },
    about: "The lanes fade from 0.55 of this radius to nothing at it, kpc: no dark line where the disc's own light has faded. Illustrative.",
  },
  {
    key: "featherSpacing", label: "feather spacing", min: 0, max: 8, step: 0.05, unit: "kpc", default: 0.7, perTemplate: { milky_way: 0.7, ngc_4414: 0.45 },
    about: "The distance along a lane between its feathers - short branches leaving it, most toward the arm's outer side - kpc; 0 none. Illustrative.",
  },
  { key: "featherLength", label: "feather length", min: 0, max: 4, step: 0.05, unit: "kpc", default: 0.8, perTemplate: { milky_way: 0.8, ngc_4414: 1.6 }, about: "A feather's length, kpc (each between half and one and a half of it). Illustrative." },
  { key: "featherPitch", label: "feather pitch", min: 0, max: 85, step: 1, unit: "°", default: 40, about: "How much more open than the arm a feather leaves its lane, degrees (each between half and one and a half of it); it closes back along its length. Illustrative." },
  { key: "featherDepth", label: "feather depth", min: 0, max: 2, step: 0.01, unit: "×", default: 0.8, about: "A feather's depth at its root, as a share of a strand's. Illustrative." },
  { key: "fray", label: "fray", min: 0, max: 2, step: 0.01, unit: "×", default: 1, about: "Short thin wisps leaving the strands at a low angle, their depth as a share of a strand's: a ragged edge; 0 none. Illustrative." },
  {
    key: "barDepth", label: "bar lane depth", min: 0, max: 4, step: 0.01, unit: "×", default: 1,
    about: "The depth of the two lanes along the bar's leading edges, as a share of the lane depth; 0 none. Drawn only where the galaxy has a bar. Illustrative.",
  },
  { key: "barOffset", label: "bar lane offset", min: 0.02, max: 0.95, step: 0.01, unit: "", default: 0.4, about: "How far from the bar's long axis its lanes run, as a share of the bar's half-width. Illustrative." },
  { key: "barWidth", label: "bar lane width", min: 20, max: 400, step: 5, unit: "pc", default: 60, about: "A bar lane's full width at half depth, parsecs. Illustrative." },
  { key: "barCurve", label: "bar lane curve", min: 1, max: 8, step: 0.1, unit: "", default: 2.5, about: "How late a bar lane turns in to the bar's end: 1 a straight line from the end to the centre's side, higher a lane along the axis that turns at the end. Illustrative." },
  { key: "barReach", label: "bar lane reach", min: 0.3, max: 1.3, step: 0.01, unit: "", default: 1, about: "Where a bar lane begins, as a share of the bar's half-length (1 the bar's end). Illustrative." },
  { key: "seed", label: "lane seed", min: 0, max: 999, step: 1, unit: "", default: 7, about: "The seed of the lanes' wander, breaks and feathers: another number, another drawing of the same lanes. Illustrative." },
];

const DEFAULTS: Readonly<Record<string, number>> = Object.fromEntries(CONTROLS.map((c) => [c.key, c.default]));

/** The shaping parameters among a feature's own (everything but the depth, the ink, the redness, the edge and the mottle, which are uniforms). */
export function shapeOf(p: IllParams): LaneShape {
  return Object.fromEntries(SHAPE_KEYS.map((k) => [k, p[k] ?? DEFAULTS[k]])) as unknown as LaneShape;
}

const polar = (t: DataTexture): DataTexture => {
  t.minFilter = LinearFilter;
  t.magFilter = LinearFilter;
  t.wrapS = ClampToEdgeWrapping;
  t.wrapT = RepeatWrapping;
  t.needsUpdate = true;
  return t;
};

/** One texel of no lane: what the shaders read until the arrays have arrived, and for a galaxy with nothing to draw. */
const NONE = polar(new DataTexture(new Uint8Array(1), 1, 1, RedFormat, UnsignedByteType));

/** The last build's time, ms, and how many maps were built (a diagnostic: nothing is drawn from it). */
export const lanesBuild = { ms: 0, count: 0 };

let held: DataTexture | null = null;
const now = () => (typeof performance !== "undefined" ? performance.now() : 0);

/** The map's texture for a frame and a shape: built once per (frame, shaping values), the one before it released. */
const mapTexture = memoOn((frame: unknown, ...values: unknown[]): DataTexture => {
  if (held) held.dispose();
  held = null;
  if (!frame) return NONE;
  const shape = Object.fromEntries(SHAPE_KEYS.map((k, i) => [k, values[i] as number])) as unknown as LaneShape;
  const started = now();
  const map = buildLaneMap(geometryOf(frame as IllFrame), shape);
  lanesBuild.ms = now() - started;
  lanesBuild.count += 1;
  if (!map.drawn) return NONE;
  held = polar(new DataTexture(map.data, map.rings, map.sectors, RedFormat, UnsignedByteType));
  return held;
});

const MAX = LANE_MAP.shapeMax.toFixed(1);

export const lanes: IllFeature = {
  id: "lanes",
  label: "dust lanes",
  about: "Dust lanes along the arms' ridges and the bar's leading edges, with feathers: placed by the published arm pieces and bar, their wander, breaks and branches the viewer's own drawing.",
  controls: CONTROLS,
  glsl: /* glsl */ `
  uniform sampler2D illLanesMap;
  uniform float illLanesDepth;
  uniform float illLanesInk;
  uniform float illLanesRed;
  uniform float illLanesHard;
  uniform float illLanesMottle;
  uniform float illLanesGrain;
  // A lattice hash (lowbias32 over the two cell numbers) and smooth value noise in [0, 1] over the plane, kpc: the
  // mottle's. Integers only, so it is the same on every GPU; no clock, no frame.
  float illLanesHash(ivec2 p) {
    uint h = (uint(p.x) * 0x9E3779B1u) ^ (uint(p.y) * 0x85EBCA77u + 0x27D4EB2Fu);
    h ^= h >> 16; h *= 0x7feb352du; h ^= h >> 15; h *= 0x846ca68bu; h ^= h >> 16;
    return float(h >> 8) * (1.0 / 16777216.0);
  }
  float illLanesNoise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = p - i;
    vec2 u = f * f * (3.0 - 2.0 * f);
    ivec2 q = ivec2(i);
    return mix(mix(illLanesHash(q), illLanesHash(q + ivec2(1, 0)), u.x), mix(illLanesHash(q + ivec2(0, 1)), illLanesHash(q + ivec2(1, 1)), u.x), u.y);
  }
  // The map holds sqrt(shape / ${MAX}) (lanesMap.ts): shape 1 at the centre of one full strand, more where strands
  // cross (at most 1.6 here: a crossing is a darker knot, never a hole). The edge: between the soft stroke as drawn and
  // an inked one - nothing under a quarter of a strand's depth, the whole of it from 0.6.
  float illLanesShape(vec2 rp) {
    if (illLanesDepth <= 0.0 || rp.x >= rHi) return 0.0;
    float s = illPolar(illLanesMap, rp).r;
    float shape = ${MAX} * s * s;
    if (shape <= 0.0) return 0.0;
    // The mottle: the stroke's depth swelled and thinned over the plane at the grain's length and a third of it, so an
    // inked edge is ragged and a lane has holes and knots at any zoom (the map's texels do not limit it).
    if (illLanesMottle > 0.0) {
      vec2 xy = rp.x * vec2(cos(rp.y), sin(rp.y)) / max(illLanesGrain, 1e-3);
      float m = 0.6 * illLanesNoise(xy) + 0.4 * illLanesNoise(xy * 3.1 + vec2(17.3, 5.9));
      shape *= max(1.0 + illLanesMottle * (2.0 * m - 1.0) * 1.6, 0.0);
    }
    float inked = smoothstep(0.25, 0.6, shape) * (1.0 + 0.5 * max(shape - 1.0, 0.0));
    return min(mix(shape, inked, illLanesHard), 1.6);
  }
  float illLanesAv(vec2 rp) {
    return illLanesDepth * (1.0 - illLanesInk) * illLanesShape(rp);
  }
  // The ink: the grains' own depth per magnitude in each channel, its spread about the middle channel's times the
  // redness (0 grey, 1 the grains' own).
  vec3 illLanesVeil(vec2 rp) {
    float av = illLanesDepth * illLanesInk * illLanesShape(rp);
    if (av <= 0.0) return vec3(1.0);
    vec3 law = max(vec3(cloudExt.g) + illLanesRed * (cloudExt - vec3(cloudExt.g)), vec3(0.02 * cloudExt.g));
    return exp(-av * law);
  }
`,
  hooks: { dustAv: "illLanesAv", veil: "illLanesVeil" },
  arrays: LANE_ARRAYS,
  uniforms: (p, context) => {
    const shape = shapeOf(p);
    return {
      illLanesMap: mapTexture(context.frame, ...SHAPE_KEYS.map((k) => shape[k])),
      illLanesDepth: p.depth ?? DEFAULTS.depth,
      illLanesInk: p.ink ?? DEFAULTS.ink,
      illLanesRed: p.redness ?? DEFAULTS.redness,
      illLanesHard: p.hardness ?? DEFAULTS.hardness,
      illLanesMottle: p.mottle ?? DEFAULTS.mottle,
      illLanesGrain: (p.grain ?? DEFAULTS.grain) * 1e-3,
    };
  },
};
