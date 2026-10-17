import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo, useRef } from "react";
import {
  AdditiveBlending,
  BackSide,
  BoxGeometry,
  ClampToEdgeWrapping,
  DataTexture,
  FloatType,
  HalfFloatType,
  LinearFilter,
  Matrix4,
  NearestFilter,
  Mesh,
  PlaneGeometry,
  RGBAFormat,
  RedFormat,
  RGFormat,
  DataUtils,
  RepeatWrapping,
  Scene,
  ShaderMaterial,
  Vector2,
  Vector3,
  Vector4,
  WebGLRenderTarget,
} from "three";

import { ALL_AGES, FIELD_SCALARS, ageParts, agedLight, clumpedLight, keptParts } from "@interface/ages.js";

import { type Census, type FieldsPayload, type Frame, type Query, type RenderFrame, loadArrays, loadRender } from "../api";
import { type CloudColumns, type CloudRaster, CLOUD_RASTER, cloudDepthScale, cloudRaster, finestRaster } from "./cloudOpacity";
import type { CellLayout } from "./brightTiles";
import { evenLayout } from "./knots";
import { useLoad } from "../useLoad";
import { type FilterSetName, bulgeLight, curvesOf, whiteOf } from "./filters";
import { DUST_CUTS, marchHalfHeight, planeTexture, RING_ROWS, SLAB_PIECES, starTexels, SUB_SAMPLES_MAX, summed, type RegionWindow } from "./regimes";
import { type DustPaintShown, FIELD_LAYERS, type MarchLayers, WHERE_STOPS, dustLevels, dustRamp, ringDepths, whereLevel } from "./components";
import { DUST_TOP_HEIGHTS, tallestLayer } from "./flux";
import type { PointDust } from "./FluxPoints";
import { gpuTimer } from "./gpuTimer";
import { renderRings } from "./ringProfile";
import { STEPS, type Tuning, TUNING_DEFAULTS } from "./tuning";
import { NOISE_GLSL, NOISE_UNIFORMS } from "./noise.glsl";
import {
  type ClusteringTables,
  type GasTables,
  type SpurTables,
  clusterMeanTexels,
  gasRingTexels,
  gasWeightTexels,
  noiseScalars,
  prepareClustering,
  prepareGas,
  prepareSpurs,
  spurTexels,
} from "./noise";

/**
 * How bright 1 L☉/pc² of white light draws at zero exposure stops, against a star point's 1 per
 * 100 L☉. A display balance between the layers, not a physical constant: a point is one star and
 * the field is a disc of them. Since S38 the field's channels are the model's filter responses over
 * the white point (filters.ts), so a ring of white light draws its surface brightness in each channel.
 */
export const LIGHT_PER_LSUN_PC2 = 1 / 400;

// The march's sampling (STEPS, PIXEL_BUDGET, MAX_RESOLUTION) is a display choice and lives in tuning.ts (D199).
/** The points of the scattered light's phase table the shader holds (spectra.PHASE_POINTS). */
const PHASE_POINTS = 21;

// A screen-covering triangle pair that lays the marched image over the view, added as light.
const COMPOSITE_VERTEX = /* glsl */ `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = vec4(position.xy, 0.0, 1.0);
  }
`;
const COMPOSITE_FRAGMENT = /* glsl */ `
  uniform sampler2D field;
  varying vec2 vUv;
  void main() {
    gl_FragColor = vec4(texture2D(field, vUv).rgb, 1.0);
  }
`;

// The bulge's scale radius comes from the arrays; every component, its layer and its colour from /api/render.
const SCALARS: string[] = [...FIELD_SCALARS];

/** Each age part's switch (S63, D223): its light's multiplier in the stellar layer, 0 off and 1 on. */
export interface AgeGains {
  young: number;
  middle: number;
  old: number;
}

/** One age part as the render carries it (interface/ages.js ageParts): its name, switch, label and placing field. */
export interface AgePart {
  name: string;
  key: keyof AgeGains;
  label: string;
  unit: string | null;
  placedBy: string | null;
  weight: string | null;
}

/** What the stellar layer's texture is refilled from when an age switch moves: the parts and the render's arrays. */
interface AgedStars {
  parts: AgePart[];
  arrays: Record<string, ArrayLike<number>>;
  n: { R: number; phi: number; filter: number };
  white: number[];
  /**
   * The middle part's kept arrays (S66, V7, D226 R5b; interface/ages.js keptParts) where the young light can be
   * clustered in the march - the render carries them, the clustering field and the gas field's cells (the layer on), and
   * the middle part is placed by a weight - else null.
   */
  kept: { arrays: Record<number, string> } | null;
  /** The switches the texture was last filled with, and whether it was filled split for the clustered march. */
  shown: string;
}

/**
 * Fill the stellar layer's textures for the age switches `gains` (S63) and, where `clumped`, split for the clustered
 * march (S66): `plane` the rest and the clump textures the young and kept shares (interface/ages.js clumpedLight). Not
 * clumped, `plane` is agedLight's sum exactly as S63 drew it and the clump textures are not read.
 */
function fillStars(aged: AgedStars, gains: AgeGains, clumped: boolean, plane: DataTexture, clumps: DataTexture[]) {
  const { n, white } = aged;
  if (clumped && aged.kept) {
    const split = clumpedLight(aged.arrays, aged.parts, aged.kept, gains, n);
    (plane.image.data as Float32Array).set(starTexels(n.R, n.phi, split.rest, white));
    split.clumps.forEach((c, k) => {
      (clumps[k].image.data as Float32Array).set(starTexels(n.R, n.phi, c, white));
      clumps[k].needsUpdate = true;
    });
  } else {
    (plane.image.data as Float32Array).set(starTexels(n.R, n.phi, agedLight(aged.arrays, aged.parts, gains, n), white));
  }
  plane.needsUpdate = true;
}

/** The layer's tables as the march holds them (S66, V7): each null with the layer off or where the render has none. */
interface LayerTables {
  gas: GasTables | null;
  clustering: ClusteringTables | null;
  spurs: SpurTables | null;
  /** Whether the render names the placement without the spurs and their ring mean: what the per-sub-step spurs read. */
  unspurred: boolean;
}

/** A float texture read at its own texels (nearest, clamped): the layer's tables, never blended with a neighbour's. */
function tableTexture(data: Float32Array, width: number, height: number, red = false): DataTexture {
  const t = new DataTexture(data, width, height, red ? RedFormat : RGBAFormat, FloatType);
  t.minFilter = NearestFilter;
  t.magFilter = NearestFilter;
  t.wrapS = ClampToEdgeWrapping;
  t.wrapT = ClampToEdgeWrapping;
  t.generateMipmaps = false;
  t.needsUpdate = true;
  return t;
}

/** A 1 x 1 zero table: what the march samples where the render carries no table (the layer off). */
const noTable = (red = false) => tableTexture(new Float32Array(red ? 1 : 4), 1, 1, red);

/** The names of the textures the march's mesh owns and disposes with it. */
const OWN_TEXTURES = ["plane", "scatter", "hii", "rings", "clump3", "clump2", "clump1", "clusterMeans", "uGasRing", "uGasWeights", "uGasCells", "uSpurs"];

const agesKey = (g: AgeGains) => `${g.young},${g.middle},${g.old}`;

const VERTEX = /* glsl */ `
  varying vec3 vWorld;
  void main() {
    vec4 world = modelMatrix * vec4(position, 1.0);
    vWorld = world.xyz;
    gl_Position = projectionMatrix * viewMatrix * world;
  }
`;

// Emission and absorption along the line of sight, front to back (S39, V2). At each step every
// component's light in the step is added, dimmed by all the dust between it and the camera and by the
// step's own dust mixed through it, and the step's dust dims everything behind it. Units: the textures
// are L☉/pc² through a face-on column, and each component is spread through its own layer — a
// sech²(y / 2h) / 4h profile at the scale height the model names (the render header's layers), which
// integrates to 1 over height — so a step takes each layer's exact column over its own height range, a
// difference of tanh, whatever the step's size; the bulge is L☉ times a Hernquist density per kpc³, times
// the step, per 10⁶ pc² per kpc².
//
// Volumetric, not a surface (RENDER_PHYSICS §4): a tilted ray crosses more of a thick layer than a
// face-on one, so the diffuse Hα's 1.4 kpc layer brightens toward the disc's limb by itself.
//
// Every colour here is the model's filter integral over the white point (regimes.ts, filters.ts); the
// dust is each channel's own optical depth from the grain model's curve. The shader only sums and dims,
// and reads the scattered light's phase factor from the model's table by the view's |cos i|.
//
// Sub-samples along each step (S46, D197 (3)): a step is split into n equal sub-steps, n its in-plane
// length over the plane texture's radial cell (regimes.ts subSamples, at most SUB_SAMPLES_MAX), and each
// sub-step reads the layers once, at its midplane crossing or else at the pixel's fixed fraction along it,
// and takes its own exact column, its own dust mixed through its light and its own dimming of what lies
// behind. Read once per step, a grazing step spans many cells, and neighbouring pixels quantised R at the
// same step boundaries: the disc drew as concentric terraces. The columns are exact per sub-step and add
// to the step's, so the sub-samples change where the layers are read, not how much light there is.
//
// The dust in its own layer (S50, D206): the model publishes the gas's scale height ring by ring and the
// render names it the dust's — tens of parsecs in the inner disc against the stars' few hundred. A sub-step
// that spans such a layer cannot treat light and dust as mixed (that is exact only when they share a
// profile), so it is cut at fixed multiples of the dust's height (regimes.ts DUST_CUTS) and its pieces are
// composed front to back, each with its exact columns: the stars in front of the dust are not dimmed by it,
// and an inclined view shows the dark lane inside the stellar disc.
//
// The dust round each ring (S50, D207): the render's placement — the gas's own contrast since D210, the dust's column at
// a cell over its ring's mean — multiplies the ring's depth, thermal light and diagnostic where the sub-step
// reads them. The march is unchanged: a multiplication of what it already read.
//
// The clouds as extinction (S64, BUILD_III V6; RULING_S64 R2-R4): the diffuse dust's depth is the ring's times its
// placement times the ring's diffuse share (dust_diffuse_share, the ring texture's share row) - what the ring's realised
// clouds do not hold - and the clouds' own dust is a third layer of opacity: the viewer's raster of /api/clouds'
// cloud_dust_extinction_v (cloudOpacity.ts, face-on A_V conserved per texel) times each channel's depth per
// magnitude (the header's extinction_ratio over 1.0857, as the diffuse dust's), at the clouds' own published heights:
// each texel's clouds a uniform slab from their A_V-weighted mean height and spread (the lead's ruling on R3), composed
// with the diffuse dust in the same pieces (regimes.ts composeStep). The switch "clouds as extinction" (cloudsOn) drops the clouds' layer and leaves the diffuse
// dust reduced: the share is the model's, the switch is display. Inside the region regime's window the clouds' layer
// fades as its own cloud interiors fade in, as the field's HII does (no double counting).
//
// The steps are compiled in (a GLSL loop needs a constant bound): a new count is a new shader (D199).
export const fieldFragment = (steps: number = STEPS): string => /* glsl */ `
  uniform sampler2D plane;
  uniform sampler2D scatter;
  uniform sampler2D hii;
  uniform sampler2D rings;
  uniform float phase[${PHASE_POINTS}];
  uniform float rLo;
  uniform float rHi;
  // One texel's radial width, kpc (regimes.ts PlaneTexture.cell): the sub-steps' in-plane length.
  uniform float planeCell;
  // The most sub-samples a step reads (the Tuning panel's cap, D199), at most the loop's ${SUB_SAMPLES_MAX}.
  uniform float subMax;
  // 1 offsets each step by the pixel's fixed fraction; 0 reads each sub-step at its middle (D199).
  uniform float dither;
  uniform float halfHeight;
  // The layers' scale heights, kpc (the render header's layers). The dust's is per ring since D206 and rides in
  // the ring texture (readHeight).
  uniform float starsHeight;
  uniform float hiiHeight;
  uniform float digHeight;
  uniform float bulgeScale;
  uniform vec3 bulgeLight;
  uniform float gain;
  // The region regime's window (r_min, r_max, phi_min, phi_max) and how far its resolved HII spheres have
  // faded in: inside it the field's HII steps back by the same weight (S40, no double counting).
  uniform vec4 regionWindow;
  uniform float hiiFade;
  // The component layers (D205, S50): each emitting layer's multiplier, the dust's depth switch and the
  // "where it is" diagnostic's light per unit of the dust's column share and its declared ramp. The field's are
  // 1, 1, 1, 1 and 0 (components.ts FIELD_LAYERS): every term below is multiplied by one or has zero added, so
  // the field draws as before, to the bit.
  uniform float starsGain;
  uniform float gasGain;
  uniform float dustGain;
  uniform float dustDepth;
  uniform float dustWhere;
  uniform vec3 whereStops[${WHERE_STOPS}];
  // The clouds' raster (S64, V6): face-on A_V per texel over the plane's polar extent, and beside it each texel's slab
  // (its clouds' mean height and half-thickness, kpc: cloudOpacity.ts); each channel's depth per magnitude
  // (cloudOpacity.ts cloudDepthScale); 1 to draw them, 0 not.
  uniform sampler2D cloudTex;
  uniform sampler2D cloudSlab;
  uniform vec3 cloudExt;
  uniform float cloudsOn;
  // The knots' undrawn share (S64, V6, R5): per level-0 cell, 1 - D_c / K_c (knots.ts undrawnShare), a sectors x rings
  // texture; the cells' radial edges and counts (lo, hi, rings, sectors: the clusters header's knots.layout); 1 to read
  // it, 0 to leave the field's HII whole.
  uniform sampler2D hiiShare;
  uniform vec4 shareCells;
  uniform float shareOn;
  // The randomness layer in the march (S66, BUILD_III V7; D226 R3-R5), each 1 only where the render header carries its
  // field (its seed non-null: the layer on) and its switch is on, else 0 - and then nothing below reads it, so under
  // "physics only" every map is exactly 1 and the march is the S64 one (R9c). gasFluct: the gas fluctuation map times
  // the dust's placement. spursOn: the spurs from their table (spurCount rows) in place of their cell means. youngClump:
  // the young and the middle part's kept light (clump3, clump2, clump1: the textures of k = 3, 2, 1 octaves, placed by
  // their weights) times the k-octave map over its level-0 cell's k-octave mean (clusterMeans: rgb = k 3, 2, 1).
  uniform float gasFluct;
  uniform float spursOn;
  uniform int spurCount;
  uniform float youngClump;
  uniform sampler2D clump3;
  uniform sampler2D clump2;
  uniform sampler2D clump1;
  uniform highp sampler2D clusterMeans;
${NOISE_UNIFORMS}
  varying vec3 vWorld;

  // The column of a sech²(y / 2h) / 4h layer, which integrates to 1 over height, along the ray
  // from height y0 to y1 over a path ds: its share of height, over the ray's slope. A ray
  // running level through the layer takes the density at its height times the path.
  // tanh clamped: some drivers build it from exp, which overflows to NaN far outside the layer.
  float sech2(float x) { float c = cosh(clamp(x, -30.0, 30.0)); return 1.0 / (c * c); }
  float safeTanh(float x) { return tanh(clamp(x, -10.0, 10.0)); }
  float column(float y0, float y1, float h, float ds) {
    if (h <= 0.0) return 0.0;
    float dy = y1 - y0;
    if (abs(dy) < 1e-4 * h) return sech2(0.5 * (y0 + y1) / (2.0 * h)) / (4.0 * h) * ds;
    return abs(safeTanh(y1 / (2.0 * h)) - safeTanh(y0 / (2.0 * h))) * 0.5 * ds / abs(dy);
  }

  // Where to read the layers over a sub-step from p0 to p1: where it crosses the midplane, or else the
  // pixel's fixed fraction 'at' along it (the screen-space dither, never frame-seeded: RENDER_PHYSICS §8).
  vec3 readPoint(vec3 p0, vec3 p1, float at) {
    if (p0.y * p1.y < 0.0) return mix(p0, p1, p0.y / (p0.y - p1.y));
    return mix(p0, p1, at);
  }

  // Radius and azimuth in the stars' frame: x = r cos φ, z = −r sin φ.
  vec2 polarOf(vec3 p) {
    float phi = atan(-p.z, p.x);
    if (phi < 0.0) phi += 6.28318531;
    return vec2(length(p.xz), phi);
  }

  // An explicit level: implicit derivatives inside a loop and a branch are undefined, and some
  // drivers' compilers expand them into shaders that take seconds to build.
  vec4 readPolar(sampler2D tex, vec2 rp) {
    return textureLod(tex, vec2((rp.x - rLo) / (rHi - rLo), rp.y / 6.28318531), 0.0);
  }
  vec3 readRing(float r, float row) {
    return textureLod(rings, vec2((r - rLo) / (rHi - rLo), (row + 0.5) / ${RING_ROWS.count}.0), 0.0).rgb;
  }

  float inRegion(vec2 rp) {
    return (rp.x >= regionWindow.x && rp.x <= regionWindow.y && rp.y >= regionWindow.z && rp.y <= regionWindow.w) ? 1.0 : 0.0;
  }

  // The share of the field's HII light the drawn knots leave in the level-0 cell at rp (knots.ts cellAt, line for
  // line); 1 outside the cells or with none drawn.
  float knotShare(vec2 rp) {
    if (shareOn < 0.5 || rp.x < shareCells.x || rp.x >= shareCells.y) return 1.0;
    float ring = min(shareCells.z - 1.0, floor((rp.x - shareCells.x) / (shareCells.y - shareCells.x) * shareCells.z));
    float sector = min(shareCells.w - 1.0, floor(rp.y / 6.28318531 * shareCells.w));
    return textureLod(hiiShare, vec2((sector + 0.5) / shareCells.w, (ring + 0.5) / shareCells.z), 0.0).r;
  }

  // regimes.ts's phaseAt, line for line: the table read linearly at |cos i|.
  float phaseAt(float cosView) {
    float x = clamp(abs(cosView), 0.0, 1.0) * float(${PHASE_POINTS - 1});
    int k = min(int(floor(x)), ${PHASE_POINTS - 2});
    float lo = phase[0];
    float hi = phase[1];
    for (int n = 0; n < ${PHASE_POINTS - 1}; n++) {
      if (n == k) { lo = phase[n]; hi = phase[n + 1]; }
    }
    return lo + (hi - lo) * (x - float(k));
  }

  // The dust diagnostic's ramp (D205), components.ts whereTint line for line: its stops read linearly at t.
  vec3 whereTint(float t) {
    float x = clamp(t, 0.0, 1.0) * float(${WHERE_STOPS - 1});
    int k = min(int(floor(x)), ${WHERE_STOPS - 2});
    vec3 lo = whereStops[0];
    vec3 hi = whereStops[1];
    for (int n = 0; n < ${WHERE_STOPS - 1}; n++) {
      if (n == k) { lo = whereStops[n]; hi = whereStops[n + 1]; }
    }
    return lo + (hi - lo) * (x - float(k));
  }
  // Each ring's level on the dust's declared ramp (components.ts dustLevels), held in the depth row's spare channel.
  float readLevel(float r) {
    return textureLod(rings, vec2((r - rLo) / (rHi - rLo), (${RING_ROWS.depth}.0 + 0.5) / ${RING_ROWS.count}.0), 0.0).a;
  }
  // The dust layer's scale height at a ring, kpc (D206): the thermal row's spare channel (regimes.ts planeTexture).
  float readHeight(float r) {
    return textureLod(rings, vec2((r - rLo) / (rHi - rLo), (${RING_ROWS.thermal}.0 + 0.5) / ${RING_ROWS.count}.0), 0.0).a;
  }
  // The column of a uniform slab of face-on depth 1 between heights lo and hi (regimes.ts slabColumn, line for line).
  float slabColumn(float y0, float y1, float lo, float hi, float ds) {
    float thick = hi - lo;
    if (thick <= 0.0) return 0.0;
    float dy = y1 - y0;
    if (abs(dy) < 1e-4 * thick) {
      float mid = 0.5 * (y0 + y1);
      return (mid >= lo && mid <= hi) ? ds / thick : 0.0;
    }
    float overlap = max(0.0, min(max(y0, y1), hi) - max(min(y0, y1), lo));
    return overlap / thick * ds / abs(dy);
  }
  // The spurs' mean round the ring at r (S66, D226 R4): the diffuse gas row's spare channel (regimes.ts planeTexture).
  float readSpurShare(float r) {
    return textureLod(rings, vec2((r - rLo) / (rHi - rLo), (${RING_ROWS.dig}.0 + 0.5) / ${RING_ROWS.count}.0), 0.0).a;
  }

  // The randomness layer's functions (noise.glsl.ts, the include the twin and the GPU probe hold to the model's vectors).
${NOISE_GLSL}

  // The young light clustered (S66, D226 R5a-b): each k-octave map over the map's mean in its level-0 cell (the gas
  // field's cells: ring by its edges, sector by azimuth), so a cell's light is kept on the model's lattice - k = 3, 2, 1
  // in x, y, z, at the screen point xy. A mean that is not a positive number leaves its share unmodulated.
  vec3 clusterRatios(vec2 xy) {
    vec3 maps = layerClusterMaps(xy);
    vec3 mean = texelFetch(clusterMeans, ivec2(layerGasSector(xy), layerGasRing(length(xy))), 0).rgb;
    return vec3(mean.x > 0.0 ? maps.z / mean.x : 1.0, mean.y > 0.0 ? maps.y / mean.y : 1.0, mean.z > 0.0 ? maps.x / mean.z : 1.0);
  }
  // Each kept share at the sub-step's read point times its ratio (clusterRatios, read once per ray).
  vec3 clumpedLight(vec3 ratio, vec2 rp) {
    return readPolar(clump3, rp).rgb * ratio.x + readPolar(clump2, rp).rgb * ratio.y + readPolar(clump1, rp).rgb * ratio.z;
  }

  // Where a sub-step is cut as it crosses the dust's layer, in the dust's scale heights (regimes.ts DUST_CUTS).
  float dustCut(int k) {
    ${DUST_CUTS.map((c, k) => (k < DUST_CUTS.length - 1 ? `if (k == ${k}) return ${c.toFixed(2)};` : `return ${c.toFixed(2)};`)).join("\n    ")}
  }

  void main() {
    vec3 origin = cameraPosition;
    vec3 dir = normalize(vWorld - cameraPosition);
    vec3 lo = vec3(-rHi, -halfHeight, -rHi);
    vec3 inv = 1.0 / dir;
    vec3 t0 = (lo - origin) * inv;
    vec3 t1 = (-lo - origin) * inv;
    vec3 tNear3 = min(t0, t1);
    vec3 tFar3 = max(t0, t1);
    float tNear = max(max(tNear3.x, tNear3.y), max(tNear3.z, 0.0));
    float tFar = min(min(tFar3.x, tFar3.y), tFar3.z);
    if (tFar <= tNear) discard;

    // The scattered light this view receives: the disc's axis is y.
    float scattering = phaseAt(dir.y);
    // Steps spaced geometrically from the camera: fine where the galaxy is close and large on
    // screen, coarse where it is far and small. Even steps along a 60 kpc ray pass straight
    // over a disc 0.3 kpc thick a few hundred parsecs away.
    float tStart = max(tNear, 0.01);
    float ratio = pow(max(tFar, tStart * 1.0001) / tStart, 1.0 / float(${steps}));
    // A per-pixel offset turns banding into fine noise: into each step for the bulge's point sample, and
    // into each sub-step for the layers' reads. Fixed by the pixel, never by the frame.
    float jitter = dither > 0.5 ? fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453) : 0.5;
    vec3 light = vec3(0.0);
    vec3 transmitted = vec3(1.0);
    // The layer's maps as a thin screen (S66, D226 R3/R5 as amended): the gas fluctuation map, the spurs' sum and the
    // clustering maps are face-on column maps, read once per ray where it crosses the midplane (y = 0) - or, for a ray
    // that does not cross it inside the march (|dir.y| under 1e-6, or the crossing outside [tStart, tFar]), at its start
    // point's projection - and each value multiplies every sub-step's placement as below. The alternative, the map read
    // at each sub-step's own point: a column map drawn through the layer makes each feature a pillar of the layer's
    // height, smeared by h tan i along the view (the streaks of the first capture); a thin screen at the midplane
    // displaces nothing - a declared approximation. With the layer off none of them is read (each uniform 0).
    float tCross = abs(dir.y) > 1e-6 ? -origin.y / dir.y : -1.0;
    vec3 screen = (tCross >= tStart && tCross <= tFar) ? origin + dir * tCross : origin + dir * tStart;
    vec2 screenXY = vec2(screen.x, -screen.z);
    vec2 screenRP = polarOf(screen);
    float screenGas = gasFluct > 0.5 ? layerGasMap(screenXY) : 1.0;
    float screenSpurs = spursOn > 0.5 ? layerSpurSum(screenRP.x, screenRP.y, spurCount) : 0.0;
    vec3 screenClumps = youngClump > 0.5 ? clusterRatios(screenXY) : vec3(1.0);
    for (int k = 0; k < ${steps}; k++) {
      float a = tStart * pow(ratio, float(k));
      float ds = a * (ratio - 1.0);
      vec3 p = origin + dir * (a + jitter * ds);
      float s = max(length(p), 0.02);
      vec3 bulge = bulgeLight * bulgeScale / (6.28318531 * s * pow(s + bulgeScale, 3.0)) * 1.0e-6 * ds;

      // The disc's layers over the whole step, [a, a + ds], in n sub-steps of at most about one plane
      // cell in the plane each (regimes.ts subSamples). The bulge's light is spread evenly over them, so
      // it sits in the same dust as before; with n = 1 this is the single read per step of S39.
      vec3 p0 = origin + dir * a;
      vec3 p1 = p0 + dir * ds;
      int n = int(clamp(ceil(length(p1.xz - p0.xz) / planeCell), 1.0, subMax));
      float sub = ds / float(n);
      for (int j = 0; j < ${SUB_SAMPLES_MAX}; j++) {
        if (j >= n) break;
        vec3 q0 = p0 + dir * (float(j) * sub);
        vec3 q1 = p0 + dir * (float(j + 1) * sub);
        vec3 bulgeSub = bulge * starsGain / float(n);
        vec2 rp = polarOf(readPoint(q0, q1, jitter));
        // What the sub-step reads, once: each layer's light per unit of its own column, the dust's depth per
        // unit of the dust's, and the dust layer's height at this ring (D206). Beyond rHi every texture is
        // zero: the box's side faces clip nothing but zeros.
        vec3 starsLight = vec3(0.0);
        vec3 dustLight = vec3(0.0);
        vec3 hiiLight = vec3(0.0);
        vec3 digLight = vec3(0.0);
        vec3 tau = vec3(0.0);
        vec3 tauC = vec3(0.0);
        vec2 slab = vec2(0.0);
        float hDust = 0.0;
        if (rp.x < rHi) {
          starsLight = readPolar(plane, rp).rgb * starsGain;
          // The young light clustered (S66, V7): its shares here times the screen's ratios.
          if (youngClump > 0.5) starsLight += clumpedLight(screenClumps, rp) * starsGain;
          // Where it is (D205): a diagnostic, the ring's level on the declared ramp in its declared scale, in the
          // ramp's colour at that level, spread through the dust's layer by its column; it dims nothing.
          float level = readLevel(rp.x);
          // The dust's column here over its ring's mean (D207): the model's placement, in the scattered
          // light's spare channel. It multiplies the depth, the thermal light and the diagnostic — everything that
          // is the dust's own column — and not the scattered light, already a share of the placed starlight.
          vec4 scattered = readPolar(scatter, rp);
          float place = scattered.a;
          // The spurs (S66, V7, D226 R4; D221 item 7): g' = (1 - <S>(R)) g + S, g the placement without them (the HII
          // texture's spare channel) read here and S their sum on the screen (over the rows its radius reads).
          if (spursOn > 0.5) place = (1.0 - readSpurShare(rp.x)) * readPolar(hii, rp).a + screenSpurs;
          // The gas fluctuation (S66, V7, D226 R3): the screen's map times the placement, in one statement, so that
          // whatever reads place below is the S64 march's.
          if (gasFluct > 0.5) place *= screenGas;
          dustLight = (scattered.rgb * scattering + readRing(rp.x, ${RING_ROWS.thermal}.0) * place) * dustGain + dustWhere * level * whereTint(level) * place;
          hiiLight = readPolar(hii, rp).rgb * (1.0 - hiiFade * inRegion(rp)) * gasGain * knotShare(rp);
          digLight = readRing(rp.x, ${RING_ROWS.dig}.0) * gasGain;
          // The diffuse dust (S64): the ring's depth times its placement times the share the realised clouds leave.
          tau = readRing(rp.x, ${RING_ROWS.depth}.0) * place * readRing(rp.x, ${RING_ROWS.share}.0).r * dustDepth;
          hDust = readHeight(rp.x);
          // The clouds' own dust (S64): the raster's face-on A_V here times each channel's depth per magnitude.
          tauC = readPolar(cloudTex, rp).r * cloudExt * cloudsOn * dustDepth * (1.0 - hiiFade * inRegion(rp));
          slab = readPolar(cloudSlab, rp).rg;
        }
        // Composed in order (D206; regimes.ts composeStep, line for line). The dust's layer is far thinner than
        // the stars' in the inner disc, so a sub-step that spans it is cut at fixed multiples of the dust's
        // height and its pieces taken front to back: the stars in front of the layer are not dimmed by it. The
        // layers are symmetric about the midplane, so heights run upward along the ray in u (the clouds' slab, which is
        // not, mirrored with them). With the slab (S64) the pieces are cut at the dust's cuts and at the slab's
        // SLAB_PIECES equal parts, merged in order of height.
        float sgn = q1.y >= q0.y ? 1.0 : -1.0;
        float u0 = sgn * q0.y;
        float u1 = sgn * q1.y;
        float du = u1 - u0;
        bool clouds = max(tauC.r, max(tauC.g, tauC.b)) > 0.0 && slab.y > 0.0;
        bool dusty = hDust > 0.0;
        float lo = sgn * slab.x - slab.y;
        float hi = sgn * slab.x + slab.y;
        float hMin = (dusty && clouds) ? min(hDust, slab.y) : (dusty ? hDust : (clouds ? slab.y : 0.0));
        bool whole = hMin <= 0.0 || du <= 1e-6 * hMin;
        int pd = 0;
        int ps = 0;
        float a = u0;
        for (int m = 0; m <= ${DUST_CUTS.length + SLAB_PIECES + 1}; m++) {
          float b = u1;
          float share = 1.0;
          if (whole) {
            if (m > 0) break;
          } else {
            float nd = (dusty && pd < ${DUST_CUTS.length}) ? dustCut(pd) * hDust : 1.0e9;
            float ns = (clouds && ps <= ${SLAB_PIECES}) ? lo + (hi - lo) * float(ps) / ${SLAB_PIECES}.0 : 1.0e9;
            b = min(u1, min(nd, ns));
            if (nd <= ns) pd++; else ps++;
            if (b <= a) continue;
            share = (b - a) / du;
          }
          float piece = sub * share;
          float cDust = column(a, b, hDust, piece);
          vec3 emitted = bulgeSub * share + starsLight * column(a, b, starsHeight, piece) + dustLight * cDust
            + hiiLight * column(a, b, hiiHeight, piece) + digLight * column(a, b, digHeight, piece);
          vec3 depth = tau * cDust + (clouds ? tauC * slabColumn(a, b, lo, hi, piece) : vec3(0.0));
          // Light mixed through its own dust leaves (1 − e^−τ)/τ of itself; each piece's dust dims only what
          // lies behind it, so light and dust keep their order inside a long step.
          vec3 own = mix(vec3(1.0) - 0.5 * depth, (vec3(1.0) - exp(-depth)) / max(depth, vec3(1e-6)), step(vec3(1e-3), depth));
          light += transmitted * emitted * own;
          transmitted *= exp(-depth);
          a = b;
          if (a >= u1) break;
        }
      }
    }
    gl_FragColor = vec4(light * gain, 1.0);
  }
`;

interface Props {
  meta: FieldsPayload;
  query: Query;
  /** Exposure in stops. */
  stops: number;
  /** The regime weight, 0 to 1: how much of the field is drawn at this zoom. */
  weight?: number;
  /** The filter set the field is seen through (filters.json): the model integrates it, per component. */
  filterSet?: FilterSetName;
  /** The region regime's window and weight (S40): the field's HII fades there as the resolved spheres fade in. */
  regionWindow?: RegionWindow | null;
  hiiFade?: number;
  /**
   * The Tuning panel's display choices (D199): the march's sampling, the field's gain multiplier and the
   * white point. The defaults are the values the view drew with before the panel.
   */
  tuning?: Pick<Tuning, "resolution" | "pixelBudget" | "steps" | "subMax" | "dither" | "filtering" | "fieldGain" | "whiteKelvin"> &
    Partial<Pick<Tuning, "cloudRaster" | "gasInMarch" | "spursInMarch" | "clumpsInMarch">>;
  /** Filled in at each re-march: the target's size and the CPU-side time of the march's render call. */
  stats?: MarchStats;
  /**
   * Which layers emit and how strongly, whether the dust dims, and the dust's "where it is" tint (D205):
   * the brightest mode's component switches. The field's default draws every layer as before.
   */
  layers?: MarchLayers;
  /** Told how the dust diagnostic is painted when the render arrives (field, scale, the range mapped): its caption. */
  onDepth?: (paint: DustPaintShown | null) => void;
  /**
   * The star-first mode's threshold (D208): with a luminosity the stellar layer is the render's remainder,
   * `stars_unresolved` — the light no point above it carries, nor the clusters — and without one the whole.
   */
  lMin?: number | null;
  /** Handed the march's dust textures for the segment to each point (T20, D208); null when the volume goes. */
  onDust?: (dust: PointDust | null) => void;
  /**
   * Handed the stars' layer scale height, kpc - the render header's `layers.stars` - whenever a render carries one
   * (S65, V6b): what the star-first view weighs its zoomed budget by (brightTiles.ts frustumWeights).
   */
  onStarsLayer?: (h: number) => void;
  /**
   * The starlight by age (S63, D223): each part's multiplier. Where the render carries the three parts the stellar
   * layer is their sum at these switches; all on (the default) is the whole of the stars' light.
   */
  ages?: AgeGains;
  /** Told which age parts the render carries and what places each (null: none, the layer is `stars`): the rail's switches. */
  onAges?: (parts: AgePart[] | null) => void;
  /**
   * The whole disc's cloud census (/api/clouds, f4; S64 V6), rasterised into the clouds' opacity layer; null draws no
   * clouds' layer (the diffuse dust is still the render's reduced one).
   */
  clouds?: Census | null;
  /** The "clouds as extinction" switch (S64): the clouds' layer drawn, or not. The diffuse share applies either way. */
  cloudsOn?: boolean;
  /**
   * The knots' undrawn share (S64, V6, R5): per level-0 cell of `layout` (the clusters header's knots.layout), the
   * share of the field's HII layers (halpha_hii and lines_hii) left drawn, 1 - D_c / K_c (knots.ts undrawnShare). Null
   * leaves them whole.
   */
  hiiShare?: { share: Float32Array; layout: CellLayout } | null;
}

/** What the clouds' raster measured when last built (S64): its texels, bytes, the time to build it and the conservation. */
export interface CloudRasterStats {
  width: number;
  height: number;
  perCell: number;
  bytes: number;
  ms: number;
  census: number;
  held: number;
  outside: number;
  split: number;
}

/** A 1 x 1 raster of no clouds: what the march reads until a census arrives, so the shader never samples nothing. */
function noClouds(): DataTexture {
  const t = new DataTexture(new Float32Array(1), 1, 1, RedFormat, FloatType);
  t.needsUpdate = true;
  return t;
}

/** A 1 x 1 slab of no thickness, beside noClouds. */
function noSlab(): DataTexture {
  const t = new DataTexture(new Uint16Array(2), 1, 1, RGFormat, HalfFloatType);
  t.needsUpdate = true;
  return t;
}

/** A raster's texture at its own texels: each texel's clouds, A_V and slab together, never blended with a neighbour's. */
function rasterTexture(t: DataTexture): DataTexture {
  t.minFilter = NearestFilter;
  t.magFilter = NearestFilter;
  t.wrapS = ClampToEdgeWrapping;
  t.wrapT = RepeatWrapping;
  t.needsUpdate = true;
  return t;
}

/** The last re-march: its target in pixels and how long the render call took on the CPU side, ms. */
export interface MarchStats {
  width: number;
  height: number;
  ms: number;
  /** The GPU's time for the last march, ms, from a timer query (S67, D227 R6); null until one comes back. */
  gpuMs?: number | null;
  /** Whether the browser gives the timer query at all (EXT_disjoint_timer_query_webgl2). */
  gpuAvailable?: boolean;
}

/**
 * The field regime: the whole galaxy's light as a volume, ray-marched per pixel through
 * the published components (RENDER_PLAN R3, R4, M4; BUILD_II V1, V2). No particles and no sample:
 * at the scale of a galaxy the light is unresolved, and a smooth integral is what it is. Its colour
 * is the model's filter integral (/api/render): the viewer sends the set's curves and draws the
 * responses over the white point, each component in the layer the model names.
 */
export function FieldVolume({
  meta,
  query,
  stops,
  weight = 1,
  filterSet = "rgb",
  regionWindow = null,
  hiiFade = 0,
  tuning = TUNING_DEFAULTS,
  stats,
  layers: shown = FIELD_LAYERS,
  onDepth,
  lMin = null,
  onDust,
  onStarsLayer,
  ages = ALL_AGES,
  onAges,
  clouds = null,
  cloudsOn = true,
  hiiShare = null,
}: Props) {
  const { resolution, pixelBudget, steps, subMax, dither, filtering, fieldGain, whiteKelvin } = tuning;
  // The randomness layer's switches in the march (S66, V7): on unless the tuning says off.
  const gasInMarch = tuning.gasInMarch ?? true;
  const spursInMarch = tuning.spursInMarch ?? true;
  const clumpsInMarch = tuning.clumpsInMarch ?? true;
  const declared = (name: string) => meta.fields.find((f) => f.name === name);
  const names = SCALARS.filter((n) => declared(n));
  const lit = Boolean(declared("disc_surface_brightness") && declared("disc_light_temperature"));
  const key = lit ? JSON.stringify([names, query]) : null;
  const loaded = useLoad<Frame>(key, (signal) => loadArrays(names, query, signal));
  const frame = loaded.value ?? null;
  const unresolved = lMin != null && lMin > 0;
  const renderKey = lit ? JSON.stringify([filterSet, whiteKelvin, query, unresolved ? lMin : null]) : null;
  const rendered = useLoad<RenderFrame>(renderKey, (signal) => loadRender(curvesOf(filterSet), whiteKelvin, query, signal, unresolved ? lMin : null));
  const light = rendered.value && "stars" in rendered.value.arrays ? rendered.value : null;
  // The render's own stars per ring (S67, D227 R5; rule B1: a read-only copy of what the viewer was sent):
  // `window.__galaxygenRenderRings`, the surface-brightness gate's reference beside GalaxyView's ring probe.
  useEffect(() => {
    const R = frame?.header.grid.axes.R;
    const phi = frame?.header.grid.axes.phi;
    const white = light ? whiteOf(light.header) : null;
    if (!R || !phi || !light || !white || light.header.window.R.n !== R.n || light.header.window.phi.n !== phi.n) return;
    const holder = window as unknown as Record<string, unknown>;
    const value = renderRings(R, phi.n, light.arrays.stars as ArrayLike<number>, white, light.header.bulge);
    holder.__galaxygenRenderRings = value;
    return () => {
      if (holder.__galaxygenRenderRings === value) delete holder.__galaxygenRenderRings;
    };
  }, [frame, light]);

  // Read when the material is built, so a mesh made after a steps change compiles once, with them.
  const stepsNow = useRef(steps);
  stepsNow.current = steps;
  const filteringNow = useRef(filtering);
  filteringNow.current = filtering;
  const metaNow = useRef(meta);
  metaNow.current = meta;
  const agesNow = useRef(ages);
  agesNow.current = ages;
  const clumpsNow = useRef(clumpsInMarch);
  clumpsNow.current = clumpsInMarch;

  const mesh = useMemo(() => {
    const R = frame?.header.grid.axes.R;
    const phi = frame?.header.grid.axes.phi;
    const white = light ? whiteOf(light.header) : null;
    const layers = light?.header.layers;
    // The render covers the whole grid; a frame from another grid (a model switch in flight) waits, and
    // so does a render without the layers its components are spread through.
    if (!frame || !R || !phi || !light || !white || !layers?.stars || light.header.window.R.n !== R.n || light.header.window.phi.n !== phi.n) {
      return null;
    }
    const a = light.arrays;
    // The starlight by age (S63, D223): where the render carries the three parts, the stellar layer is their sum at
    // the switches, each part placed round the ring by its own weight. Not under the star-first mode's threshold,
    // whose remainder is its own component - and so not clustered in the march either (S66, D226 R5e): the remainder
    // has no young part (the clusters carry it) and its middle part stays placed by sfr_modulation, unmodulated - a debt
    // (the mend: only=remainder's per-part arrays split by kept octaves as the field's are).
    const parts = unresolved ? null : (ageParts(light.header, a) as AgePart[] | null);
    const n = { R: R.n, phi: phi.n, filter: white.length };
    // The randomness layer's tables (S66, V7; D226 R6): every number the render header's, null with the layer off.
    const tables: LayerTables = {
      gas: prepareGas(light.header.gas_fluctuation),
      clustering: prepareClustering(light.header.census_clustering),
      spurs: prepareSpurs(light.header.spurs),
      unspurred: false,
    };
    const unspurredName = light.header.placement?.dust_unspurred;
    const unspurred = unspurredName && unspurredName in a ? a[unspurredName] : null;
    const spurShare = light.header.spurs?.share ?? null;
    tables.unspurred = Boolean(unspurred && spurShare && spurShare.length === R.n);
    // The young light can be clustered where the render splits the middle part and the layer's cells are there (R5).
    const middle = parts?.find((p) => p.key === "middle");
    const kept = parts && middle?.weight && tables.clustering && tables.gas ? (keptParts(light.header, a) as AgedStars["kept"]) : null;
    const aged: AgedStars | null = parts ? { parts, arrays: a, n, white, kept, shown: "" } : null;
    const { data, scatter, hii, rings, width, height, cell } = planeTexture({
      R,
      phi,
      // The stars' light: the whole component, or under the star-first mode's threshold the remainder no point
      // carries (D208). A frame that predates the threshold has no remainder yet and draws the whole meanwhile.
      // A frame that carries the age parts draws their sum at the switches; one from before them draws `stars`.
      stars: unresolved && a.stars_unresolved ? a.stars_unresolved : aged ? agedLight(a, aged.parts, agesNow.current, n) : a.stars,
      // Every line in each layer (S42): Halpha plus the others the render carries (lines_hii, lines_dig).
      hii: summed(a.halpha_hii, a.lines_hii),
      dig: summed(a.halpha_dig, a.lines_dig),
      extinction: a.dust_extinction,
      scattered: a.dust_scattered,
      thermal: a.dust_thermal,
      // The dust's layer (D206): the render's per-ring heights where the header names them, else its one height.
      dustHeight: typeof layers.dust === "string" ? a[layers.dust] : layers.dust,
      // The dust round each ring (D207): the render's placement where the header names one, else an even ring.
      dustPlacement: light.header.placement?.dust ? a[light.header.placement.dust] : null,
      // The share of each ring's dust left diffuse by its realised clouds (S64, V6): where the header names one.
      diffuseShare: cloudsOf(light) ? a[cloudsOf(light)!.array] : null,
      // The placement without the spurs and their ring mean (S66, V7, R4): where the render names them.
      unspurred: tables.unspurred ? unspurred : null,
      spurShare: tables.unspurred ? spurShare : null,
      white,
    });
    // The dust diagnostic's levels (D205): each ring's place on its declared ramp in its declared scale, kept in
    // the depth row's spare channel, which the field's march never reads.
    let paint: DustPaintShown | null = null;
    try {
      const dust = dustRamp(metaNow.current);
      if (dust) {
        const depthRow = rings.subarray(RING_ROWS.depth * width * 4, (RING_ROWS.depth + 1) * width * 4);
        const { levels, lo, hi } = dustLevels(dust, metaNow.current.cmaps, ringDepths(depthRow, width));
        for (let i = 0; i < width; i += 1) depthRow[i * 4 + 3] = levels[i];
        paint = { field: dust.field, scale: dust.scale, inferred: dust.inferred, coloured: dust.coloured, lo, hi };
      }
    } catch {
      paint = null; // declarations from another model in flight: the diagnostic draws nothing (its levels stay 0)
    }
    const filter = filteringNow.current === "nearest" ? NearestFilter : LinearFilter;
    const polar = (values: Float32Array) => {
      const texture = new DataTexture(values, width, height, RGBAFormat, FloatType);
      texture.minFilter = filter;
      texture.magFilter = filter;
      texture.wrapS = ClampToEdgeWrapping;
      texture.wrapT = RepeatWrapping;
      texture.needsUpdate = true;
      return texture;
    };
    const ringTexture = new DataTexture(rings, width, RING_ROWS.count, RGBAFormat, FloatType);
    ringTexture.minFilter = filter;
    ringTexture.magFilter = filter;
    ringTexture.wrapS = ClampToEdgeWrapping;
    ringTexture.wrapT = ClampToEdgeWrapping;
    ringTexture.needsUpdate = true;

    const bulgeScale = frame.header.scalars.bulge_scale_radius ?? 0;
    const halfHeight = marchHalfHeight(layers, bulgeScale);
    // The phase table, or isotropic scattering where the render carries none.
    const table = light.header.components?.dust_scattered?.phase?.factor;
    const phase = table && table.length === PHASE_POINTS ? table.map(Number) : new Array<number>(PHASE_POINTS).fill(1);

    // The stellar layer and, for the clustered march, the young and kept shares in three more polar textures (S66, R5).
    const planeTex = polar(data);
    const clumpTex = [0, 1, 2].map(() => polar(new Float32Array(width * height * 4)));
    if (aged) {
      const clumped = Boolean(aged.kept) && clumpsNow.current;
      if (clumped) fillStars(aged, agesNow.current, true, planeTex, clumpTex);
      aged.shown = `${agesKey(agesNow.current)},${clumped}`;
    }
    const { gas, clustering, spurs } = tables;
    const scalars: Record<string, number> = {
      uGasSeed: 0, uGasInvScale: 0, uGasSense: 0, uGasEdge0: 0, uClusterSeed: 0, uClusterInvScale: 0, uClusterGain: 0,
      uClusterTop: 0, uClusterNorm: 0, uClusterSigma: 0, uSpurTurn: 0, uSpurReach: 0,
      ...noiseScalars(gas, clustering, spurs),
    };
    const material = new ShaderMaterial({
      uniforms: {
        plane: { value: planeTex },
        scatter: { value: polar(scatter) },
        hii: { value: polar(hii) },
        rings: { value: ringTexture },
        phase: { value: phase },
        rLo: { value: R.lo },
        rHi: { value: R.hi },
        planeCell: { value: cell },
        subMax: { value: SUB_SAMPLES_MAX },
        dither: { value: 1 },
        halfHeight: { value: halfHeight },
        // The model's layers (the render header): a missing one is height 0, which draws nothing. The dust's
        // height is in the ring texture, ring by ring (D206).
        starsHeight: { value: layers.stars ?? 0 },
        hiiHeight: { value: layers.halpha_hii ?? 0 },
        digHeight: { value: layers.halpha_dig ?? 0 },
        bulgeScale: { value: Math.max(bulgeScale, 1e-3) },
        bulgeLight: { value: new Vector3(...bulgeLight(light.header.bulge, white)) },
        gain: { value: 0 },
        regionWindow: { value: new Vector4(0, 0, 0, 0) },
        hiiFade: { value: 0 },
        starsGain: { value: FIELD_LAYERS.stars },
        gasGain: { value: FIELD_LAYERS.gas },
        dustGain: { value: FIELD_LAYERS.dust },
        dustDepth: { value: FIELD_LAYERS.dustDepth },
        dustWhere: { value: FIELD_LAYERS.where },
        whereStops: { value: FIELD_LAYERS.whereStops.map((c) => new Vector3(...c)) },
        // The clouds (S64): no clouds until the census's raster arrives; each channel's depth per magnitude from the
        // dust component's extinction_ratio.
        cloudTex: { value: noClouds() },
        cloudSlab: { value: noSlab() },
        cloudExt: { value: new Vector3(...cloudDepthScale(extinctionRatio(light))) },
        cloudsOn: { value: 0 },
        // The knots' share (S64): none until the view draws knots.
        hiiShare: { value: noClouds() },
        shareCells: { value: new Vector4(0, 1, 1, 1) },
        shareOn: { value: 0 },
        // The randomness layer (S66, V7): the switches' uniforms are set in the frame loop; the tables here, a 1 x 1
        // zero where the render has none (the layer off), so the shader never samples nothing.
        gasFluct: { value: 0 },
        spursOn: { value: 0 },
        spurCount: { value: spurs ? spurs.count : 0 },
        youngClump: { value: 0 },
        clump3: { value: clumpTex[0] },
        clump2: { value: clumpTex[1] },
        clump1: { value: clumpTex[2] },
        clusterMeans: { value: clustering ? tableTexture(clusterMeanTexels(clustering), 32, 32) : noTable() },
        uGasRing: { value: gas ? tableTexture(gasRingTexels(gas), 32, 2) : noTable() },
        uGasWeights: { value: gas ? tableTexture(gasWeightTexels(gas), gas.weights.length / 8, 2) : noTable() },
        uGasCells: { value: gas ? tableTexture(gas.cells, 32, 32, true) : noTable(true) },
        uSpurs: { value: spurs && spurs.count > 0 ? tableTexture(spurTexels(spurs), 3 * spurs.count, 1) : noTable() },
        ...Object.fromEntries(Object.entries(scalars).map(([k, v]) => [k, { value: v }])),
      },
      vertexShader: VERTEX,
      fragmentShader: fieldFragment(stepsNow.current),
      side: BackSide, // the far faces, so it draws with the camera outside the box or inside it
      depthTest: false,
      depthWrite: false,
    });
    const box = new Mesh(new BoxGeometry(2 * R.hi, 2 * halfHeight, 2 * R.hi), material);
    if (paint) box.userData.dustPaint = paint;
    // What the star-first mode's points read for the dust in front of them (T20): the march's own textures.
    const pointDust: PointDust = {
      rings: ringTexture,
      scatter: material.uniforms.scatter.value as DataTexture,
      rLo: R.lo,
      rHi: R.hi,
      top: DUST_TOP_HEIGHTS * tallestLayer(typeof layers.dust === "string" ? a[layers.dust] : layers.dust),
    };
    box.userData.pointDust = pointDust;
    box.userData.cloudExt = cloudDepthScale(extinctionRatio(light));
    box.userData.aged = aged;
    box.userData.tables = tables;
    box.frustumCulled = false;
    return box;
  }, [frame, light, unresolved]);

  // The clouds' raster (S64, V6; RULING_S64 R4): the whole disc's census over the plane's polar extent at the "cloud
  // raster" tuning value's texels per render cell a side (never past the 16 MiB budget for this grid), built once per
  // census and grid. The viewer's own resolution: what each cloud deposits is conserved whatever it is.
  const gridR = frame?.header.grid.axes.R;
  const gridPhi = frame?.header.grid.axes.phi;
  const perCell = gridR && gridPhi ? Math.max(1, Math.min(Math.round(tuning.cloudRaster ?? CLOUD_RASTER), finestRaster(gridR.n, gridPhi.n))) : 0;
  const raster = useMemo((): { texture: DataTexture; slab: DataTexture; top: number; stats: CloudRasterStats } | null => {
    const c = clouds?.columns as Partial<CloudColumns> | undefined;
    if (!gridR || !gridPhi || !perCell || !c?.cloud_dust_extinction_v || !c.cloud_radius || !c.cloud_azimuth || !c.cloud_size || !c.cloud_height) return null;
    const started = performance.now();
    const built: CloudRaster = cloudRaster(c as CloudColumns, gridR.lo, gridR.hi, gridR.n * perCell, gridPhi.n * perCell);
    // The slab beside the A_V (S64, R3 as ruled): half floats, two a texel - each texel's clouds' mean height and
    // half-thickness, kpc - and the highest a slab reaches, which bounds the points' segment.
    const halves = new Uint16Array(built.slab.length);
    let top = 0;
    for (let k = 0; k < built.slab.length; k += 2) {
      halves[k] = DataUtils.toHalfFloat(built.slab[k]);
      halves[k + 1] = DataUtils.toHalfFloat(built.slab[k + 1]);
      if (built.slab[k + 1] > 0) top = Math.max(top, Math.abs(built.slab[k]) + built.slab[k + 1]);
    }
    const ms = performance.now() - started;
    const texture = rasterTexture(new DataTexture(built.av, built.width, built.height, RedFormat, FloatType));
    const slab = rasterTexture(new DataTexture(halves, built.width, built.height, RGFormat, HalfFloatType));
    const stats = {
      width: built.width, height: built.height, perCell, bytes: built.av.byteLength + halves.byteLength, ms,
      census: built.census, held: built.held, outside: built.outside, split: built.split,
    };
    (globalThis as { __galaxygenCloudRaster?: CloudRasterStats }).__galaxygenCloudRaster = stats;
    return { texture, slab, top, stats };
  }, [clouds, gridR?.lo, gridR?.hi, gridR?.n, gridPhi?.n, perCell]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(
    () => () => {
      raster?.texture.dispose();
      raster?.slab.dispose();
    },
    [raster],
  );
  const cloudsShown = Boolean(raster && cloudsOn);
  const cloudsKey = raster ? `${raster.texture.uuid},${cloudsShown}` : "none";
  // The knots' undrawn share (S64, V6, R5): one texel per level-0 cell, sectors across and rings down, read at its own
  // texel. Its radial edges and counts beside it; a layout the march's lookup cannot read (uneven edges) draws no share.
  const share = useMemo(() => {
    if (!hiiShare || !evenLayout(hiiShare.layout) || hiiShare.share.length !== hiiShare.layout.rings * hiiShare.layout.sectors) return null;
    const { layout } = hiiShare;
    const texture = rasterTexture(new DataTexture(hiiShare.share, layout.sectors, layout.rings, RedFormat, FloatType));
    const edges = layout.ring_edges;
    return { texture, cells: [edges[0], edges[edges.length - 1], layout.rings, layout.sectors] as const };
  }, [hiiShare]);
  useEffect(() => () => share?.texture.dispose(), [share]);
  const shareKey = share ? share.texture.uuid : "none";
  // The raster is read at its own texels (nearest: a texel's slab is its own clouds'). Its textures and the switch reach
  // the shader in the frame loop (below), where a change re-marches: set in an effect, a frame marched between React's
  // commit and the effect kept the mesh's placeholder, and nothing in the settings key said to march again.

  const gl = useThree((state) => state.gl);
  const size = useThree((state) => state.size);
  // The GPU's time for the march (S67, D227 R6; gpuTimer.ts): a timer query round its render call, read back frames later.
  const timer = useMemo(() => gpuTimer(gl.getContext() as WebGL2RenderingContext), [gl]);
  useEffect(() => () => timer.dispose(), [timer]);

  // The box lives in a scene of its own, marched into a lower-resolution float target.
  const offscreen = useMemo(() => {
    if (!mesh) return null;
    const scene = new Scene();
    scene.add(mesh);
    const target = new WebGLRenderTarget(1, 1, { type: HalfFloatType, depthBuffer: false });
    target.texture.minFilter = LinearFilter;
    target.texture.magFilter = LinearFilter;
    const quad = new Mesh(
      new PlaneGeometry(2, 2),
      new ShaderMaterial({
        uniforms: { field: { value: target.texture } },
        vertexShader: COMPOSITE_VERTEX,
        fragmentShader: COMPOSITE_FRAGMENT,
        blending: AdditiveBlending,
        transparent: true,
        depthTest: false,
        depthWrite: false,
      }),
    );
    quad.frustumCulled = false;
    quad.renderOrder = -1;
    return { scene, target, quad, last: { view: new Matrix4(), projection: new Matrix4(), gain: -1, width: 0, height: 0, region: "", settings: "" } };
  }, [mesh]);

  useEffect(
    () => () => {
      if (!mesh || !offscreen) return;
      const material = mesh.material as ShaderMaterial;
      for (const name of OWN_TEXTURES) (material.uniforms[name].value as DataTexture).dispose();
      // The placeholder clouds' texture goes with the mesh; the raster's goes with the raster (its own effect).
      for (const name of ["cloudTex", "cloudSlab", "hiiShare"]) {
        const t = material.uniforms[name].value as DataTexture;
        if (t.image.width === 1 && t.image.height === 1) t.dispose();
      }
      material.dispose();
      mesh.geometry.dispose();
      offscreen.target.dispose();
      offscreen.quad.geometry.dispose();
      (offscreen.quad.material as ShaderMaterial).dispose();
    },
    [mesh, offscreen],
  );

  const tellLayer = useRef(onStarsLayer);
  tellLayer.current = onStarsLayer;
  const starsLayer = light?.header.layers?.stars;
  useEffect(() => {
    if (typeof starsLayer === "number" && Number.isFinite(starsLayer) && starsLayer > 0) tellLayer.current?.(starsLayer);
  }, [starsLayer]);

  const tellDust = useRef(onDust);
  tellDust.current = onDust;
  useEffect(() => {
    const base = mesh ? ((mesh.userData.pointDust as PointDust | undefined) ?? null) : null;
    // The points read the clouds from the same raster (S64): its A_V and slab textures and the depth per magnitude.
    const withClouds: PointDust | null = base
      ? {
          ...base,
          clouds: cloudsShown && raster ? raster.texture : null,
          slab: cloudsShown && raster ? raster.slab : null,
          cloudExt: (mesh!.userData.cloudExt as [number, number, number] | undefined) ?? [0, 0, 0],
          top: Math.max(base.top, cloudsShown && raster ? raster.top : 0),
        }
      : null;
    tellDust.current?.(withClouds);
    return () => tellDust.current?.(null);
  }, [mesh, raster, cloudsShown]);

  const tellAges = useRef(onAges);
  tellAges.current = onAges;
  useEffect(() => {
    if (!mesh) return;
    const aged = mesh.userData.aged as AgedStars | null | undefined;
    tellAges.current?.(aged ? aged.parts : null);
  }, [mesh]);

  // An age switch moved (S63, D223): the stellar layer's texture is refilled in place with the parts' sum at the
  // new switches - no new texture, no new shader - and the march's settings key re-marches the frame.
  // Since S66 (V7, R5) also when the young light's clustering is switched: the textures split for the clustered march, or
  // the parts' sum as before.
  const aged = mesh ? ((mesh.userData.aged as AgedStars | null | undefined) ?? null) : null;
  const clumped = Boolean(aged?.kept) && clumpsInMarch;
  const shownAges = `${agesKey(ages)},${clumped}`;
  useEffect(() => {
    if (!mesh || !aged || aged.shown === shownAges) return;
    const uniforms = (mesh.material as ShaderMaterial).uniforms;
    const clumps = ["clump3", "clump2", "clump1"].map((k) => uniforms[k].value as DataTexture);
    fillStars(aged, agesNow.current, clumped, uniforms.plane.value as DataTexture, clumps);
    aged.shown = shownAges;
  }, [mesh, aged, clumped, shownAges]);

  const tellDepth = useRef(onDepth);
  tellDepth.current = onDepth;
  useEffect(() => {
    if (mesh) tellDepth.current?.((mesh.userData.dustPaint as DustPaintShown | undefined) ?? null);
  }, [mesh]);

  // A new step count is a new shader (the loop's bound is compiled in); the caller debounces it.
  useEffect(() => {
    if (!mesh) return;
    const material = mesh.material as ShaderMaterial;
    const source = fieldFragment(steps);
    if (material.fragmentShader === source) return;
    material.fragmentShader = source;
    material.needsUpdate = true;
  }, [mesh, steps]);

  // The plane textures' sampling, set in place: no new textures, no new shader.
  useEffect(() => {
    if (!mesh) return;
    const filter = filtering === "nearest" ? NearestFilter : LinearFilter;
    const uniforms = (mesh.material as ShaderMaterial).uniforms;
    for (const name of ["plane", "scatter", "hii", "rings", "clump3", "clump2", "clump1"]) {
      const texture = uniforms[name].value as DataTexture;
      if (texture.minFilter === filter && texture.magFilter === filter) continue;
      texture.minFilter = filter;
      texture.magFilter = filter;
      texture.needsUpdate = true;
    }
  }, [mesh, filtering]);

  // Before the composer (priority 1) draws the frame: march again only if the camera, the
  // drawing size, the gain or a tuning choice changed. A still view costs nothing after its first frame.
  useFrame(({ camera }) => {
    // The last march's GPU time, once the GPU has it (R6): the readout's and the picture test's (window.__galaxygenMarchGpu).
    const gpuMs = timer.poll();
    if (stats) {
      stats.gpuMs = gpuMs;
      stats.gpuAvailable = timer.available;
    }
    (window as unknown as Record<string, unknown>).__galaxygenMarchGpu = { available: timer.available, ms: gpuMs };
    if (!mesh || !offscreen) return;
    const gain = LIGHT_PER_LSUN_PC2 * fieldGain * 2 ** stops * weight;
    const buffer = gl.getDrawingBufferSize(DRAWING);
    const scale = Math.min(resolution, Math.sqrt(pixelBudget / Math.max(1, buffer.x * buffer.y)));
    const width = Math.max(1, Math.round(buffer.x * scale));
    const height = Math.max(1, Math.round(buffer.y * scale));
    const last = offscreen.last;
    camera.updateMatrixWorld();
    const w = regionWindow;
    const region = w && hiiFade > 0 ? `${w.r_min},${w.r_max},${w.phi_min},${w.phi_max},${hiiFade}` : "";
    // The randomness layer's switches (S66, V7): each 1 only where its tables are there (the layer on) and it is on.
    const tables = mesh.userData.tables as LayerTables;
    const spursDrawn = Boolean(tables.spurs && tables.spurs.count > 0 && tables.unspurred && spursInMarch);
    const layerOn = [tables.gas && gasInMarch ? 1 : 0, spursDrawn ? 1 : 0, clumped ? 1 : 0];
    const settings = `${steps},${subMax},${dither},${filtering},${shown.stars},${shown.gas},${shown.dust},${shown.dustDepth},${shown.where},${shown.whereStops.flat().join(",")},${shownAges},${cloudsKey},${shareKey},${layerOn.join(",")}`;
    const moved =
      !last.view.equals(camera.matrixWorld) || !last.projection.equals(camera.projectionMatrix) || last.gain !== gain ||
      last.width !== width || last.height !== height || last.region !== region || last.settings !== settings;
    // React may build the memo above twice (StrictMode), and adding the mesh to the second scene
    // takes it out of the first; whichever scene is kept, the mesh goes back into it here.
    const reattached = mesh.parent !== offscreen.scene;
    if (reattached) offscreen.scene.add(mesh);
    // The clouds' layer (S64): this mesh's uniforms hold the raster and the switch the view wants, or it marches again.
    const cloudUniforms = (mesh.material as ShaderMaterial).uniforms;
    let cloudsMoved = false;
    if (raster && cloudUniforms.cloudTex.value !== raster.texture) {
      cloudUniforms.cloudTex.value = raster.texture;
      cloudUniforms.cloudSlab.value = raster.slab;
      cloudsMoved = true;
    }
    if (cloudUniforms.cloudsOn.value !== (cloudsShown ? 1 : 0)) {
      cloudUniforms.cloudsOn.value = cloudsShown ? 1 : 0;
      cloudsMoved = true;
    }
    // The knots' share (S64): likewise, in the frame loop, so a new share re-marches.
    if (share && cloudUniforms.hiiShare.value !== share.texture) {
      cloudUniforms.hiiShare.value = share.texture;
      (cloudUniforms.shareCells.value as Vector4).set(...share.cells);
      cloudsMoved = true;
    }
    if (cloudUniforms.shareOn.value !== (share ? 1 : 0)) {
      cloudUniforms.shareOn.value = share ? 1 : 0;
      cloudsMoved = true;
    }
    if (!moved && !reattached && !cloudsMoved) return;
    if (last.width !== width || last.height !== height) offscreen.target.setSize(width, height);
    const uniforms = (mesh.material as ShaderMaterial).uniforms;
    uniforms.gain.value = gain;
    (uniforms.regionWindow.value as Vector4).set(w?.r_min ?? 0, w?.r_max ?? 0, w?.phi_min ?? 0, w?.phi_max ?? 0);
    uniforms.hiiFade.value = region ? hiiFade : 0;
    uniforms.subMax.value = Math.min(SUB_SAMPLES_MAX, Math.max(1, Math.round(subMax)));
    uniforms.dither.value = dither ? 1 : 0;
    uniforms.starsGain.value = shown.stars;
    uniforms.gasGain.value = shown.gas;
    uniforms.dustGain.value = shown.dust;
    uniforms.dustDepth.value = shown.dustDepth;
    uniforms.dustWhere.value = whereLevel(shown.where, LIGHT_PER_LSUN_PC2);
    uniforms.gasFluct.value = layerOn[0];
    uniforms.spursOn.value = layerOn[1];
    uniforms.youngClump.value = layerOn[2];
    (uniforms.whereStops.value as Vector3[]).forEach((v, i) => v.set(...shown.whereStops[i]));
    const before = gl.getRenderTarget();
    gl.setRenderTarget(offscreen.target);
    gl.setClearColor(0x000000, 0);
    gl.clear(true, false, false);
    const started = performance.now();
    timer.begin();
    gl.render(offscreen.scene, camera);
    timer.end();
    const ms = performance.now() - started;
    gl.setRenderTarget(before);
    gl.setClearColor(0x000000, 1);
    last.view.copy(camera.matrixWorld);
    last.projection.copy(camera.projectionMatrix);
    last.gain = gain;
    last.width = width;
    last.height = height;
    last.region = region;
    last.settings = settings;
    if (stats) {
      stats.width = width;
      stats.height = height;
      stats.ms = ms;
    }
  }, 0.5);

  void size; // re-render on resize so the target follows the canvas
  return offscreen ? <primitive object={offscreen.quad} /> : null;
}

const DRAWING = new Vector2();

/** The render's clouds entry (S64, V6): the diffuse share's array and the clouds' layer; null in a render from before it. */
function cloudsOf(light: RenderFrame): { array: string; layers?: { clouds_scale_height?: number | null } } | null {
  const entry = light.header.clouds as { array?: string; layers?: { clouds_scale_height?: number | null } } | null | undefined;
  return entry?.array && entry.array in light.arrays ? { array: entry.array, layers: entry.layers } : null;
}

/** The dust component's A_lambda / A_V per filter (the grain model's, /api/render's dust_extinction about). */
function extinctionRatio(light: RenderFrame): (number | null)[] | null {
  const about = light.header.components?.dust_extinction as { extinction_ratio?: (number | null)[] } | undefined;
  return about?.extinction_ratio ?? null;
}

