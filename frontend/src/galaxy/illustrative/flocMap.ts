// The flocculent network's map (S109, BUILD_VIII row 109, D275): one polar raster built on the client for a
// flocculent disc as HST's NGC 4414 shows one - a network of short dust filaments winding at the spiral's pitch, and
// the light broken into patches with white-blue clumps outside. Pure functions of an /api/arrays frame and the shaping
// parameters: no React, no three, no clock. Everything here is ILLUSTRATIVE: which filament runs where is the viewer's
// own seeded drawing, tuned to the goal picture, and no number of the model.
//
// What is the model's: the pitch (the scalar pitch_angle; a filament's heading is that pitch times a slider, plus its
// own spread), the gas's radial profile (gas_surface_density: more filaments where there is more gas), the gas
// contrast (gas_density_contrast: more filaments on the flocculent pieces) and the stars' contrast
// (pattern_density_contrast: the young clumps gather on the pieces).
//
// The dust is two drawings summed. The LACE (drawLace) carries most of it: a smooth noise whose cells are pieces of
// the drawn spiral, ridged, so its threads close into cells, fork and join as the photograph's do, thick and run
// together into blotches where the dust gathers (bundles of the viewer's own, the published gas) and gone elsewhere.
// The FILAMENTS (flocStrands) are the few long ones: a filament is a short walk in the plane whose heading, measured
// from the direction of growing azimuth toward the direction of growing radius, is the pitch - so it is a piece of the
// log spiral ln R = tan(pitch) phi + c, the arm pieces' own convention (arm_pieces.py; lanesMap.ts) - wandering by a
// few degrees as it goes. Trunks carry branches that leave at an angle and turn back to the spiral, and those carry
// twigs; short wide "bands" (none at the defaults) are thick strands. They are drawn as lines of round Gaussian spots,
// as the lanes are. The light is soft blobs: patches in threes along the spiral, each a cloud of grains, and strings
// of young clumps.
//
// The map: ONE byte a texel on the lanes' grid (lanesMap.ts LANE_MAP: 2000 rings over 0-rHi by 3600 sectors) - the
// feature's channel of the look's shared map, the march's fragment having no sampler to spare for a second one - so
// the dust and the light share it, signed about 128:
//     byte > 128   dust: sqrt(shape / shapeMax) = (byte - 128) / 127, shape the drawn depth less the margin (0.3): a
//                  full filament's centre holds 0.7, a crossing more;
//     byte < 128   light: level = (128 - byte) / 127 - from the floor (0.08) to 0.5 the patches (the disc's light
//                  swelled and thinned in soft blobs: the floor the darkest gap, 0.5 the brightest patch, their mean
//                  over the disc half way, 0.29), above 0.5 a young clump (0.5 its edge, 1 its centre). Toward a
//                  filament's margin and toward the light's reach the level goes to that mean, which changes
//                  nothing; beyond the reach every byte is the mean;
//     byte 0       never written: "no map".
// So a filament's edge is one texel where the GPU's linear filter passes from the mean level through 128 (a level
// under the floor counts for less and less) into the dust: plain disc beside a filament, never a bright or dark rim.
// The feature's GLSL (floc.ts) decodes it; every depth and gain is a uniform there.

import type { IllFrame } from "./feature";
import { LANE_MAP } from "./lanesMap";

const TAU = 2 * Math.PI;
const DEG = Math.PI / 180;

/**
 * The map's size (the lanes' grid: the shared map's), the shape drawn at byte 255, the size of the coarser rasters the
 * light is drawn on before it is laid into the map (over 0 to the light's reach), the light's floor (the patches' darkest gap), and the dust's margin (the depth under which a filament is not drawn: the light's there).
 */
export const FLOC_MAP = { rings: LANE_MAP.rings, sectors: LANE_MAP.sectors, shapeMax: 4, lightRings: 600, lightSectors: 1800, lightFloor: 0.08, margin: 0.3 } as const;

/** The light reaches this far past the dust's outer radius (the clumps and patches lie beyond the dust), within the grid. */
export const FLOC_REACH = 1.3;

/** The /api/arrays names the network reads. */
export const FLOC_ARRAYS = ["gas_density_contrast", "pattern_density_contrast", "gas_surface_density", "pitch_angle"] as const;

/** The network's shaping parameters: floc.ts's controls by their keys (units as each control states). */
export interface FlocShape {
  /** trunks per kpc2 where every weight is 1. */
  density: number;
  /** kpc: a trunk's typical length (each between 0.45 and 1.75 of it). */
  length: number;
  /** pc: a filament's typical full width at half depth. */
  width: number;
  /** x the published pitch. */
  pitch: number;
  /** degrees: the spread of the trunks' own pitches about it. */
  pitchSpread: number;
  /** degrees: how far a filament's heading wanders along its length. */
  wiggle: number;
  /** branches per trunk of typical length (and half as many twigs per branch). */
  branches: number;
  /** degrees: the angle a branch leaves at. */
  branchAngle: number;
  /** wide bands per trunk. */
  bands: number;
  /** pc: a band's full width at half depth. */
  bandWidth: number;
  /** 0-1: how much a filament swells into knots and thins to threads along its length. */
  swell: number;
  /** 0-1: the depth swelled and thinned over the plane. */
  mottle: number;
  /** pc: the mottle's patches. */
  grain: number;
  /** 0-1: how far the filaments gather into bundles of the viewer's own. */
  gather: number;
  /** pc: the bundles' width across the spiral. */
  bundle: number;
  /** 0-1: how far their number follows the published gas contrast. */
  followGas: number;
  /** a power on the gas's radial profile. */
  radial: number;
  /** kpc */
  innerRadius: number;
  /** kpc */
  outerRadius: number;
  /** pc: a light patch's size. */
  patchSize: number;
  /** strings of young clumps per kpc2 where every weight is 1. */
  clumpDensity: number;
  /** pc: a clump's size. */
  clumpSize: number;
  /** kpc: the clumps come in over this radius. */
  clumpInner: number;
  /** 0-1: how far the clumps keep to the published stars' contrast. */
  clumpFollow: number;
  /** x a filament's depth: the lace - the fine network of threads between the filaments; 0 none. */
  lace: number;
  /** pc: the lace's cells, across the spiral. */
  cell: number;
  /** 0-1: how thick the lace's threads are, as a share of a cell. */
  thread: number;
  /** how many times longer along the spiral than across a cell of the lace is. */
  stretch: number;
  /** 0-1: how far the lace's threads run together into blotches where the dust gathers. */
  blotch: number;
  seed: number;
  /** S106: 0 the strands and the lace (this file), 1 the network drawn in the disc's plane (flocNet.ts). */
  style: number;
  /** S106 plane style: pc, the clouds of dust's size. */
  netScale: number;
  /** how far the plane is pushed about, as a share of netScale. */
  netWarp: number;
  /** 0-1: the level under which the network has gaps (more is less dust). */
  netGaps: number;
  /** the softness of the gaps' edges. */
  netSoft: number;
  /** 0-1: how far the dust is broken into feathered ridges. */
  netFeather: number;
  /** 0-1: how far the dust keeps to short arcs on the spiral. */
  netArc: number;
  /** pc: an arc's width. */
  arcWidth: number;
  /** an arc's length over its width. */
  arcStretch: number;
  /** the drawn depth's scale (1 a full filament). */
  netDepth: number;
  /** pc: the light's clouds' size. */
  litScale: number;
  /** x the outer radius: the light's reach. */
  litReach: number;
  /** S106 second pass, the plane style's filaments: pc, the spacing of the filaments across the spiral. */
  filSpacing: number;
  /** how many times longer along the spiral than its spacing a filament's run is. */
  filRun: number;
  /** 0-1: the finer wisps between the filaments, as a share of a filament's depth. */
  wisps: number;
  /** the smooth haze the threads lie in, as a share of a full thread's depth where the threads' amount is full. */
  haze: number;
  /** x the outer radius: where the dust's ring comes in to full (it is `core` of it inside half of this). */
  ringIn: number;
  /** x the outer radius: where the dust's ring starts to thin (to `rim` of it by 0.95 of the outer radius). */
  ringOut: number;
  /** 0-1: the dust's amount in the nuclear region, as a share of the ring's. */
  core: number;
  /** 0-1: the dust's amount in the outer disc, as a share of the ring's. */
  rim: number;
  /** 0-1: how much more dust lies toward `nearAz` (the near side as the template's stand sees it). */
  nearBias: number;
  /** degrees: the galactocentric azimuth of the most dust. */
  nearAz: number;
  /** the star clouds, as floc.ts's cloud* controls (the map paints a soft glow under each group). */
  cloudCount: number;
  cloudGroup: number;
  cloudMembers: number;
  cloudReach: number;
  cloudStart: number;
  cloudSlope: number;
  cloudRange: number;
  /** 0-1: how far the clouds keep to the rich sectors about `cloudAz`. */
  cloudRich: number;
  /** degrees: the galactocentric azimuth of the richest clouds. */
  cloudAz: number;
  /** 0-1: the glow drawn under a group (in the clump glow's tint and gain). */
  cloudGlow: number;
  /** S106 third pass (C4), the plane style's mesh: the broad soft lanes' depth, in full threads (0 none). */
  laneDepth: number;
  /** pc: a broad lane's full width at half depth. */
  laneWidth: number;
  /** pc: the broad lanes' spacing across the spiral. */
  laneSpacing: number;
  /** how many times longer along the spiral than their spacing the lanes' noise cells are. */
  laneRun: number;
  /** 0-1: how far the threads and wisps keep to the broad lanes' sides (the feathers a lane carries). */
  feathers: number;
  /** the spurs' depth, as a share of a thread's (0 none): short threads leaving the lanes and threads at an angle. */
  spurs: number;
  /** degrees: the spurs' angle to the spiral. */
  spurAngle: number;
  /** x the thread spacing: how far the plane is pushed about before the threads are drawn, exactly (they diverge and merge). */
  tangle: number;
  /** x the thread width: the wisps' width. */
  wispWidth: number;
  /** x the thread run: the wisps' run. */
  wispRun: number;
  /** 0-1: how far a thread thins toward its piece's ends. */
  taper: number;
}

export const SHAPE_KEYS: readonly (keyof FlocShape)[] = [
  "density", "length", "width", "pitch", "pitchSpread", "wiggle", "branches", "branchAngle", "bands", "bandWidth", "swell", "mottle", "grain", "gather", "bundle",
  "followGas", "radial", "innerRadius", "outerRadius", "patchSize", "clumpDensity", "clumpSize", "clumpInner", "clumpFollow", "lace", "cell", "thread", "stretch", "blotch", "seed",
  "style", "netScale", "netWarp", "netGaps", "netSoft", "netFeather", "netArc", "arcWidth", "arcStretch", "netDepth", "litScale", "litReach",
  "filSpacing", "filRun", "wisps", "haze", "ringIn", "ringOut", "core", "rim", "nearBias", "nearAz",
  "cloudCount", "cloudGroup", "cloudMembers", "cloudReach", "cloudStart", "cloudSlope", "cloudRange", "cloudRich", "cloudAz", "cloudGlow",
  "laneDepth", "laneWidth", "laneSpacing", "laneRun", "feathers", "spurs", "spurAngle", "tangle", "wispWidth", "wispRun", "taper",
];

/** A field over the disc on the model's polar grid. */
export interface PolarField {
  values: ArrayLike<number>;
  rings: number;
  sectors: number;
}

/** What the maps are drawn from. */
export interface FlocGeometry {
  /** kpc: the grid's outer radius. */
  rHi: number;
  /** degrees: the published pitch (pitch_angle). */
  pitchDeg: number;
  gas: PolarField | null;
  pattern: PolarField | null;
  /** The gas's surface density by ring over 0-rHi, or null. */
  gasProfile: ArrayLike<number> | null;
}

const numbers = (a: unknown): ArrayLike<number> | null => (a && typeof a === "object" && "length" in a && !(a instanceof BigInt64Array) ? (a as ArrayLike<number>) : null);
const finite = (v: unknown): number => (typeof v === "number" && Number.isFinite(v) ? v : NaN);

/** The pitch drawn where none is published (a galaxy with no pattern still has its shear), degrees. */
export const FALLBACK_PITCH = 20;

/** The geometry an /api/arrays frame holds (FLOC_ARRAYS asked). */
export function geometryOf(frame: IllFrame | null): FlocGeometry {
  const axes = ((frame?.header as { grid?: { axes?: Record<string, { n?: number; hi?: number }> } } | undefined)?.grid?.axes ?? {}) as Record<string, { n?: number; hi?: number }>;
  const rings = finite(axes.R?.n) || 400;
  const sectors = finite(axes.phi?.n) || 360;
  const rHi = finite(axes.R?.hi) || 30;
  const field = (name: string): PolarField | null => {
    const a = frame ? numbers(frame.arrays[name]) : null;
    return a && a.length === rings * sectors ? { values: a, rings, sectors } : null;
  };
  const profile = frame ? numbers(frame.arrays.gas_surface_density) : null;
  const pitch = Math.abs(finite(frame?.header.scalars?.pitch_angle));
  return {
    rHi,
    pitchDeg: pitch > 0 ? pitch : FALLBACK_PITCH,
    gas: field("gas_density_contrast"),
    pattern: field("pattern_density_contrast"),
    gasProfile: profile && profile.length === rings ? profile : null,
  };
}

/** A field read at a point of the plane, bilinear between its cell centres, the azimuth wrapped. */
export function readField(f: PolarField, rHi: number, x: number, y: number): number {
  const r = Math.hypot(x, y);
  let phi = Math.atan2(y, x);
  if (phi < 0) phi += TAU;
  const u = Math.min(f.rings - 1, Math.max(0, (r / rHi) * f.rings - 0.5));
  const v = (phi / TAU) * f.sectors - 0.5;
  const i0 = Math.min(f.rings - 2, Math.floor(u));
  const j0 = Math.floor(v);
  const a = u - i0;
  const b = v - j0;
  const at = (i: number, j: number) => Number(f.values[i * f.sectors + (((j % f.sectors) + f.sectors) % f.sectors)]);
  return (1 - a) * ((1 - b) * at(i0, j0) + b * at(i0, j0 + 1)) + a * ((1 - b) * at(i0 + 1, j0) + b * at(i0 + 1, j0 + 1));
}

// --- the seeded drawing: integers only, then smooth interpolation (a seed of the viewer's own; never a clock) ------

/** lowbias32. */
function mix(h: number): number {
  h = (h ^ (h >>> 16)) >>> 0;
  h = Math.imul(h, 0x7feb352d) >>> 0;
  h = (h ^ (h >>> 15)) >>> 0;
  h = Math.imul(h, 0x846ca68b) >>> 0;
  return (h ^ (h >>> 16)) >>> 0;
}

/** A key from the seed and up to three labels. */
export const flocKey = (seed: number, a = 0, b = 0, c = 0): number => mix((mix((mix((mix((seed ^ 0x51ed270b) >>> 0) ^ (a >>> 0)) >>> 0) ^ (b >>> 0)) >>> 0) ^ (c >>> 0)) >>> 0);

/** A number in [0, 1) from a key and an index. */
export const flocRandom = (key: number, i: number): number => mix((key ^ mix(i >>> 0)) >>> 0) / 4294967296;

/** Smooth value noise in [-1, 1] along a line, its lattice at the integers. */
function noise1(x: number, key: number): number {
  const i = Math.floor(x);
  const f = x - i;
  const u = f * f * f * (f * (f * 6 - 15) + 10);
  const a = flocRandom(key, i) * 2 - 1;
  const b = flocRandom(key, i + 1) * 2 - 1;
  return a + (b - a) * u;
}

/** 65 536 numbers in [0, 1), fixed (lowbias32 of their indices): the lattices' values, looked up by a hash of the cell. */
const TABLE = (() => {
  const t = new Float32Array(65536);
  for (let i = 0; i < t.length; i += 1) t[i] = mix((i + 0x1f123bb5) >>> 0) / 4294967296;
  return t;
})();
const lattice = (ix: number, iy: number, key: number): number => TABLE[Math.imul(Math.imul(ix, 0x9e3779b1) ^ Math.imul(iy, 0x85ebca77) ^ key, 0x2c1b3c6d) >>> 16];

/** Smooth value noise in [0, 1] over the plane, its lattice at the integers. */
export function noise2(x: number, y: number, key: number): number {
  const ix = Math.floor(x);
  const iy = Math.floor(y);
  const fx = x - ix;
  const fy = y - iy;
  const ux = fx * fx * (3 - 2 * fx);
  const uy = fy * fy * (3 - 2 * fy);
  const a = lattice(ix, iy, key);
  const b = lattice(ix + 1, iy, key);
  const c = lattice(ix, iy + 1, key);
  const d = lattice(ix + 1, iy + 1, key);
  return a + (b - a) * ux + (c - a) * uy + (a - b - c + d) * ux * uy;
}

/**
 * Smooth value noise in [0, 1] over the disc whose cells are pieces of log spirals: `arms` of them cross any circle,
 * each `1 / cells` of a turn long. In X = cells phi / 2 pi (along) and Y = arms (ln R / tan(pitch) - phi) / 2 pi
 * (across: constant on a spiral of that pitch) a turn of azimuth is X + cells, Y - arms, so the lattice point
 * (X, Y) and (X + cells, Y - arms) are one point and the noise has no seam.
 */
export function spiralNoise(lnR: number, phi: number, invTan: number, arms: number, cells: number, key: number): number {
  const X = (phi / TAU) * cells;
  const Y = (arms * (lnR * invTan - phi)) / TAU;
  const ix = Math.floor(X);
  const iy = Math.floor(Y);
  const fx = X - ix;
  const fy = Y - iy;
  const ux = fx * fx * (3 - 2 * fx);
  const uy = fy * fy * (3 - 2 * fy);
  const at = (cx: number, cy: number) => {
    const k = Math.floor(cx / cells);
    return lattice(cx - k * cells, cy + k * arms, key);
  };
  const a = at(ix, iy);
  const b = at(ix + 1, iy);
  const c = at(ix, iy + 1);
  const d = at(ix + 1, iy + 1);
  return a + (b - a) * ux + (c - a) * uy + (a - b - c + d) * ux * uy;
}

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));
const smoothstep = (e0: number, e1: number, v: number) => {
  const t = clamp01((v - e0) / (e1 - e0));
  return t * t * (3 - 2 * t);
};

/** A polar raster of sums: row = sector, column = ring, over 0-reach. */
class Raster {
  readonly acc: Float32Array;
  readonly dR: number;
  readonly dPhi: number;
  private readonly kr = new Float64Array(8192);
  constructor(readonly rings: number, readonly sectors: number, readonly reach: number) {
    this.acc = new Float32Array(rings * sectors);
    this.dR = reach / rings;
    this.dPhi = TAU / sectors;
  }

  /** A round Gaussian spot of standard deviation `sigma` kpc at (x, y), its centre's height `weight` (as lanesMap.ts's). */
  spot(x: number, y: number, sigma: number, weight: number): void {
    const { acc, rings, sectors, dR, dPhi, kr } = this;
    const r = Math.hypot(x, y);
    const reach = 3.2 * sigma;
    if (!(weight > 0) || r - reach >= this.reach) return;
    let phi = Math.atan2(y, x);
    if (phi < 0) phi += TAU;
    const inv = 1 / (2 * sigma * sigma);
    const iLo = Math.max(0, Math.ceil((r - reach) / dR - 0.5));
    const iHi = Math.min(rings - 1, Math.floor((r + reach) / dR - 0.5));
    if (iHi < iLo) return;
    if (r >= 10 * sigma) {
      for (let i = iLo; i <= iHi; i += 1) {
        const d = (i + 0.5) * dR - r;
        kr[i - iLo] = Math.exp(-d * d * inv);
      }
      const half = reach / r;
      const jLo = Math.ceil((phi - half) / dPhi - 0.5);
      const jHi = Math.floor((phi + half) / dPhi - 0.5);
      for (let j = jLo; j <= jHi; j += 1) {
        const d = r * ((j + 0.5) * dPhi - phi);
        const w = weight * Math.exp(-d * d * inv);
        const row = (((j % sectors) + sectors) % sectors) * rings;
        for (let i = iLo; i <= iHi; i += 1) acc[row + i] += w * kr[i - iLo];
      }
      return;
    }
    const half = r <= reach ? Math.PI : Math.min(Math.PI, 1.05 * Math.asin(reach / r) + dPhi);
    const jLo = Math.ceil((phi - half) / dPhi - 0.5);
    const jHi = Math.min(jLo + sectors - 1, Math.floor((phi + half) / dPhi - 0.5));
    const reach2 = reach * reach;
    for (let j = jLo; j <= jHi; j += 1) {
      const c = Math.cos((j + 0.5) * dPhi - phi);
      const row = (((j % sectors) + sectors) % sectors) * rings;
      for (let i = iLo; i <= iHi; i += 1) {
        const ri = (i + 0.5) * dR;
        const d2 = ri * ri + r * r - 2 * ri * r * c;
        if (d2 < reach2) acc[row + i] += weight * Math.exp(-d2 * inv);
      }
    }
  }
}

const SQRT_TAU = Math.sqrt(TAU);
/** The dust's margin, and the light's level at the patches' mean. */
const MARGIN = FLOC_MAP.margin;
const MEAN = FLOC_MAP.lightFloor + 0.25 * (1 - 2 * FLOC_MAP.lightFloor);
const sigmaOf = (fwhmKpc: number) => fwhmKpc / 2.3548;

/** One drawn filament: its points in the plane (kpc), each point's heading, standard deviation (kpc) and depth. */
export interface Strand {
  /** 0 a trunk, 1 a branch, 2 a twig, 3 a wide band. */
  kind: 0 | 1 | 2 | 3;
  n: number;
  x: Float64Array;
  y: Float64Array;
  /** rad, from the direction of growing azimuth toward that of growing radius: the pitch, for a filament on the spiral. */
  heading: Float64Array;
  sigma: Float64Array;
  depth: Float64Array;
  /** kpc */
  length: number;
}

/** A strand's pitch from its two ends, degrees: atan(d ln R / d phi), the azimuth followed round the turn. */
export function strandPitch(s: Strand): number {
  let turned = 0;
  for (let i = 1; i < s.n; i += 1) {
    const d = Math.atan2(s.y[i], s.x[i]) - Math.atan2(s.y[i - 1], s.x[i - 1]);
    turned += Math.atan2(Math.sin(d), Math.cos(d));
  }
  const grown = Math.log(Math.hypot(s.x[s.n - 1], s.y[s.n - 1]) / Math.hypot(s.x[0], s.y[0]));
  return Math.atan2(grown, turned) / DEG;
}

/** The weights a place is drawn by: how many filaments start there, and how deep one is there. */
interface Weights {
  /** The number weight of a filament's start at (x, y). */
  start(x: number, y: number): number;
  /** An upper bound of `start`. */
  bound: number;
  /** The fade of everything at radius r: nothing inside the inner radius or beyond the outer. */
  fade(r: number): number;
}

/** A ladder's levels: level k's cells are sized for the radius LADDER_R0 2^(k / 2) kpc. */
const LADDER_R0 = 0.35;
const LADDER_LEVELS = 16;

/**
 * Spiral noise whose cells keep one size in parsecs at every radius. A lattice that turns with the azimuth
 * (spiralNoise) has cells in proportion to the radius, so the noise is taken on a ladder of lattices, one every half
 * octave of radius, each with the whole numbers of cells that give the size asked at its own radius, and blended
 * between neighbours: one smooth field, its cells within a fifth of the size asked (smaller inside LADDER_R0).
 */
export class Ladder {
  private readonly arms = new Int32Array(LADDER_LEVELS + 4);
  private readonly cells = new Int32Array(LADDER_LEVELS + 4);
  private readonly invTan: number;
  private readonly invSin: number;
  /** `pitch` rad; `across` kpc, a cell's size across the spiral; `stretch`, its length along over that. */
  constructor(pitch: number, across: number, stretch: number, private readonly key: number) {
    this.invTan = 1 / Math.tan(pitch);
    this.invSin = 1 / Math.sin(pitch);
    for (let k = 0; k < this.arms.length; k += 1) {
      const rk = LADDER_R0 * 2 ** (k / 2);
      this.arms[k] = Math.max(2, Math.round((TAU * rk * Math.sin(pitch)) / across));
      this.cells[k] = Math.max(3, Math.round((TAU * rk) / (Math.cos(pitch) * across * stretch)));
    }
  }

  /** The level (a whole number) and the blend to the next at radius r, as level + blend. */
  static place(r: number): number {
    const l = Math.min(LADDER_LEVELS - 1.001, Math.max(0, 2 * Math.log2(Math.max(r, 1e-6) / LADDER_R0)));
    const k = Math.floor(l);
    return k + smoothstep(0.25, 0.75, l - k);
  }

  /**
   * S106 (C3): the noise at (ln R, phi) for a place, and its slope's size, per kpc, at radius r (each level's own, blended
   * as the values are): what a thread drawn on the noise's middle crossing needs to keep one width in parsecs.
   */
  atSlope(lnR: number, phi: number, place: number, r: number, out: { v: number; g: number }): void {
    const k0 = Math.floor(place);
    const w = place - k0;
    let v = 0;
    let g = 0;
    for (let side = 0; side < 2; side += 1) {
      const wt = side === 0 ? 1 - w : w;
      if (wt <= 0) continue;
      const k = k0 + side;
      const arms = this.arms[k];
      const cells = this.cells[k];
      const X = (phi / TAU) * cells;
      const Y = (arms * (lnR * this.invTan - phi)) / TAU;
      const ix = Math.floor(X);
      const iy = Math.floor(Y);
      const fx = X - ix;
      const fy = Y - iy;
      const ux = fx * fx * (3 - 2 * fx);
      const uy = fy * fy * (3 - 2 * fy);
      const key = this.key ^ Math.imul(k + 1, 0x61c88647);
      // The lattice's corners, the azimuth wrapped as spiralNoise's (inlined: this is the plane style's hot loop).
      const q0 = Math.floor(ix / cells);
      const q1 = Math.floor((ix + 1) / cells);
      const x0 = ix - q0 * cells;
      const x1 = ix + 1 - q1 * cells;
      const a = lattice(x0, iy + q0 * arms, key);
      const b = lattice(x1, iy + q1 * arms, key);
      const c = lattice(x0, iy + 1 + q0 * arms, key);
      const d = lattice(x1, iy + 1 + q1 * arms, key);
      const e = a - b - c + d;
      const n = a + (b - a) * ux + (c - a) * uy + e * ux * uy;
      const nX = 6 * fx * (1 - fx) * (b - a + e * uy);
      const nY = 6 * fy * (1 - fy) * (c - a + e * ux);
      // |grad X| = cells / (2 pi r); |grad Y| = arms / (2 pi r sin(pitch)) (Y is constant along the spiral).
      const gX = (nX * cells) / (TAU * r);
      const gY = (nY * arms * this.invSin) / (TAU * r);
      v += wt * n;
      g += wt * Math.sqrt(gX * gX + gY * gY);
    }
    out.v = v;
    out.g = g;
  }

  /** The noise in [0, 1] at (ln R, phi) for a place (Ladder.place of the radius), `shift` levels finer (or coarser, below 0). */
  at(lnR: number, phi: number, place: number, shift = 0): number {
    const k0 = Math.floor(place);
    const w = place - k0;
    const k = Math.max(0, k0 + shift);
    const lo = w < 1 ? spiralNoise(lnR, phi, this.invTan, this.arms[k], this.cells[k], this.key ^ Math.imul(k + 1, 0x61c88647)) : 0;
    const hi = w > 0 ? spiralNoise(lnR, phi, this.invTan, this.arms[k + 1], this.cells[k + 1], this.key ^ Math.imul(k + 2, 0x61c88647)) : 0;
    return lo + (hi - lo) * w;
  }
}

function weightsOf(g: FlocGeometry, shape: FlocShape, pitch: number): Weights {
  const inner = Math.max(0, shape.innerRadius);
  const outer = Math.max(inner + 0.1, Math.min(shape.outerRadius, g.rHi));
  const fade = (r: number) => (inner > 0 ? smoothstep(0.5 * inner, 1.5 * inner, r) : 1) * (1 - smoothstep(0.7 * outer, outer, r));
  // The gas's profile over its value at half the outer radius, to the power: 1 where none is published.
  const profile = g.gasProfile;
  const rings = profile ? profile.length : 0;
  const at = (r: number) => (profile ? Number(profile[Math.min(rings - 1, Math.max(0, Math.floor((r / g.rHi) * rings)))]) : 1);
  const ref = Math.max(at(0.5 * outer), 1e-12);
  const radial = (r: number) => (profile && shape.radial > 0 ? Math.min(2.5, Math.max(0, at(r) / ref) ** shape.radial) : 1);
  // The bundles: spiral pieces of the viewer's own, `bundle` parsecs across and six times as long, and a finer set.
  const across = Math.max(shape.bundle * 1e-3, 0.05);
  const wide = new Ladder(pitch, across, 6, flocKey(shape.seed, 0, 0, 11));
  const fine = new Ladder(pitch, 0.45 * across, 3, flocKey(shape.seed, 0, 0, 12));
  const start = (x: number, y: number) => {
    const r = Math.hypot(x, y);
    const f = fade(r);
    if (f <= 0) return 0;
    let w = f * radial(r);
    if (g.gas && shape.followGas > 0) w *= 1 - shape.followGas + shape.followGas * 2 * clamp01((readField(g.gas, g.rHi, x, y) - 0.5) / 1.5);
    if (shape.gather > 0) {
      let phi = Math.atan2(y, x);
      if (phi < 0) phi += TAU;
      const lnR = Math.log(Math.max(r, 1e-3));
      const place = Ladder.place(r);
      const n = 0.65 * wide.at(lnR, phi, place) + 0.35 * fine.at(lnR, phi, place);
      w *= 1 - shape.gather + shape.gather * 2 * smoothstep(0.38, 0.62, n);
    }
    return w;
  };
  return { start, bound: 2.5 * 2 * 2, fade };
}

/** The filaments for a geometry and a shape, in the order they are drawn. The same inputs give the same strands. */
export function flocStrands(g: FlocGeometry, shape: FlocShape): Strand[] {
  const out: Strand[] = [];
  const pitch = Math.min(80, Math.max(1, g.pitchDeg * shape.pitch)) * DEG;
  const weights = weightsOf(g, shape, pitch);
  const inner = Math.max(0, shape.innerRadius);
  const outer = Math.max(inner + 0.1, Math.min(shape.outerRadius, g.rHi));
  const area = Math.PI * (outer * outer - 0.25 * inner * inner);
  const wiggle = shape.wiggle * DEG;
  const sigmaFloor = (1.2 * g.rHi) / FLOC_MAP.rings;

  // A walk of n points from (x, y), `ds` apart, the heading at point k given.
  const walk = (x: number, y: number, n: number, ds: number, theta: (k: number) => number) => {
    const xs = new Float64Array(n);
    const ys = new Float64Array(n);
    const hs = new Float64Array(n);
    for (let k = 0; k < n; k += 1) {
      xs[k] = x;
      ys[k] = y;
      const th = theta(k);
      hs[k] = th;
      const c = Math.cos(th);
      const s = Math.sin(th);
      // The step's direction taken at its middle (a midpoint step): the heading is kept against the turning radius
      // vector, so a constant heading is a log spiral of that pitch to the step's second order.
      const r = Math.hypot(x, y) || 1e-9;
      const mx = x + ((-y * c + x * s) / r) * 0.5 * ds;
      const my = y + ((x * c + y * s) / r) * 0.5 * ds;
      const mr = Math.hypot(mx, my) || 1e-9;
      x += ((-my * c + mx * s) / mr) * ds;
      y += ((mx * c + my * s) / mr) * ds;
    }
    return { xs, ys, hs };
  };

  // A strand from its walk: the width and depth along it - a swell over half a kiloparsec and a finer one, the ends
  // tapered (both for a trunk and a band; a branch is whole at its root and thins to its tip), the disc's fade.
  const strand = (kind: Strand["kind"], path: ReturnType<typeof walk>, ds: number, sigma0: number, depth0: number, key: number): Strand => {
    const n = path.xs.length;
    const sigma = new Float64Array(n);
    const depth = new Float64Array(n);
    const rooted = kind === 1 || kind === 2;
    for (let k = 0; k < n; k += 1) {
      const t = n > 1 ? k / (n - 1) : 0;
      const s = k * ds;
      const w = 0.65 * noise1(s / 0.5 + 3.1, key) + 0.55 * noise1(s / 0.13 + 7.7, key ^ 0x3c6ef372);
      const taper = rooted ? smoothstep(0, 0.06, t) * (1 - t) ** 1.1 : smoothstep(0, 0.22, t) * smoothstep(0, 0.22, 1 - t);
      sigma[k] = Math.max(sigmaFloor, sigma0 * Math.exp(0.6 * shape.swell * w) * (rooted ? 1 - 0.45 * t : 1));
      depth[k] = depth0 * taper * Math.max(0, 1 + shape.swell * (0.8 * w - 0.2)) * weights.fade(Math.hypot(path.xs[k], path.ys[k]));
    }
    return { kind, n, x: path.xs, y: path.ys, heading: path.hs, sigma, depth, length: (n - 1) * ds };
  };

  // Branches off a strand: each leaves at the branch angle (between half and one and a half of it), to either side,
  // most running on the way the strand runs, and turns back toward the spiral along its length.
  const branchesOf = (parent: Strand, sigma0: number, depth0: number, mean: number, kind: 1 | 2, key: number) => {
    const count = Math.floor(mean * (parent.length / shape.length) + flocRandom(key, 0));
    for (let b = 0; b < count; b += 1) {
      const u = (i: number) => flocRandom(key, 8 * b + i + 1);
      const at = Math.min(parent.n - 1, Math.floor((0.12 + 0.76 * u(0)) * parent.n));
      if (parent.depth[at] < 0.15 * depth0) continue;
      const back = u(1) < 0.3;
      const side = u(2) < 0.6 ? 1 : -1;
      const angle = shape.branchAngle * DEG * (0.5 + u(3));
      const length = parent.length * (0.25 + 0.5 * u(4));
      const s0 = Math.max(sigmaFloor, sigma0 * 0.72);
      const ds = Math.min(0.06, Math.max(0.006, 0.6 * s0));
      const n = Math.max(4, Math.ceil(length / ds) + 1);
      const base = parent.heading[at] + (back ? Math.PI : 0);
      const bKey = flocKey(key, b, kind, 5);
      const path = walk(parent.x[at], parent.y[at], n, ds, (k) => base + side * angle * (1 - (0.7 * k) / (n - 1)) + 0.8 * wiggle * noise1((k * ds) / 0.35, bKey));
      const child = strand(kind, path, ds, s0, depth0 * 0.85, bKey);
      out.push(child);
      if (kind === 1) branchesOf(child, s0, depth0 * 0.85, 0.5 * mean, 2, flocKey(bKey, 0, 0, 6));
    }
  };

  // Trunks, then bands: candidates even over the disc's area, each kept with its place's weight.
  const draw = (kind: 0 | 3, perKpc2: number, salt: number) => {
    const candidates = Math.round(perKpc2 * area * weights.bound);
    const key = flocKey(shape.seed, salt, 0, 1);
    for (let c = 0; c < candidates; c += 1) {
      const u = (i: number) => flocRandom(key, 12 * c + i);
      const r = Math.sqrt(0.25 * inner * inner + u(0) * (outer * outer - 0.25 * inner * inner));
      const phi = TAU * u(1);
      const x = r * Math.cos(phi);
      const y = r * Math.sin(phi);
      if (u(2) * weights.bound >= weights.start(x, y)) continue;
      const band = kind === 3;
      // Near the centre a filament is shorter and finer in proportion (full size from 2.5 kpc out).
      const near = Math.min(1, 0.25 + (0.75 * r) / 2.5);
      const length = shape.length * (band ? 0.35 + 0.6 * u(3) : 0.45 + 1.3 * u(3)) * near;
      const sigma0 = Math.max(sigmaFloor, sigmaOf((band ? shape.bandWidth * (0.6 + 0.8 * u(4)) : shape.width * (0.6 + 1.6 * u(4) * u(4))) * 1e-3) * Math.max(0.4, near));
      const depth0 = band ? 0.45 + 0.5 * u(5) : 0.55 + 0.75 * u(5);
      // The trunk's own pitch: the drawn pitch and its spread (three uniforms summed: nearly a Gaussian of that deviation).
      const own = pitch + shape.pitchSpread * DEG * (u(6) + u(7) + u(8) - 1.5) * 2 * (band ? 1.5 : 1);
      const ds = Math.min(0.06, Math.max(0.006, 0.6 * sigma0));
      const n = Math.max(4, Math.ceil(length / ds) + 1);
      const sKey = flocKey(key, c, 0, 2);
      // Back along its own spiral by half its length to where it begins, then forward, wandering.
      const back = walk(x, y, Math.ceil(n / 2), ds, () => own + Math.PI);
      const path = walk(back.xs[back.xs.length - 1], back.ys[back.ys.length - 1], n, ds, (k) => own + wiggle * noise1((k * ds) / 0.45, sKey));
      const s = strand(kind, path, ds, sigma0, depth0, sKey);
      out.push(s);
      if (!band && shape.branches > 0) branchesOf(s, sigma0, depth0, shape.branches, 1, flocKey(sKey, 0, 0, 3));
    }
  };
  if (shape.density > 0) {
    draw(0, shape.density, 1);
    if (shape.bands > 0) draw(3, shape.density * shape.bands, 2);
  }
  return out;
}

/** A strand drawn: each spot weighed by the length of line it stands for, so the centre holds the depth. */
function drawStrand(raster: Raster, s: Strand): void {
  for (let i = 0; i < s.n; i += 1) {
    const a = Math.max(0, i - 1);
    const b = Math.min(s.n - 1, i + 1);
    const ds = Math.hypot(s.x[b] - s.x[a], s.y[b] - s.y[a]) / (b - a);
    if (s.depth[i] > 1e-4) raster.spot(s.x[i], s.y[i], s.sigma[i], (s.depth[i] * ds) / (s.sigma[i] * SQRT_TAU));
  }
}

/** One soft blob of the light: its place, standard deviation (kpc) and height. */
export interface Blob {
  x: number;
  y: number;
  sigma: number;
  height: number;
}

/** The light patches: soft blobs in threes over the whole disc, each three strung along the spiral's direction. */
export function flocPatches(g: FlocGeometry, shape: FlocShape): Blob[] {
  const out: Blob[] = [];
  const reach = lightReach(g, shape);
  const size = shape.patchSize * 1e-3;
  if (!(size > 0)) return out;
  const pitch = Math.min(80, Math.max(1, g.pitchDeg * shape.pitch)) * DEG;
  const count = Math.round((0.55 / (size * size)) * Math.PI * reach * reach);
  const key = flocKey(shape.seed, 3, 0, 1);
  const floor = (1.2 * reach) / FLOC_MAP.lightRings;
  for (let p = 0; p < count; p += 1) {
    const u = (i: number) => flocRandom(key, 16 * p + i);
    const r = reach * Math.sqrt(u(0));
    const fade = 1 - smoothstep(0.85 * reach, reach, r);
    if (fade <= 0) continue;
    const phi = TAU * u(1);
    const x = r * Math.cos(phi);
    const y = r * Math.sin(phi);
    const near = Math.min(1, 0.3 + (0.7 * r) / 2.5);
    const sigma = Math.max(floor, sigmaOf(size * (0.55 + 0.9 * u(2))) * near);
    const height = (0.35 + 0.65 * u(3) * u(3)) * fade;
    out.push({ x, y, sigma, height });
    // Two more beside it, along the spiral's direction and a little across: a patch is a short irregular fragment.
    for (let k = 0; k < 2; k += 1) {
      const along = (k === 0 ? 1 : -1) * (0.7 + 0.9 * u(4 + 3 * k)) * sigma * 1.6;
      const across = (u(5 + 3 * k) - 0.5) * sigma * 1.4;
      const c = Math.cos(pitch);
      const s = Math.sin(pitch);
      const rr = r || 1e-9;
      // The spiral's direction: cos(pitch) along growing azimuth, sin(pitch) along growing radius.
      const tx = (-y * c + x * s) / rr;
      const ty = (x * c + y * s) / rr;
      out.push({ x: x + tx * along - ty * across, y: y + ty * along + tx * across, sigma: Math.max(floor, sigma * (0.55 + 0.4 * u(6 + 3 * k))), height: height * (0.5 + 0.5 * u(10 + k)) });
    }
  }
  return out;
}

/** The grains: small soft blobs, a third of a patch's size, even over the disc - a patch is a cloud of them. */
export function flocGrains(g: FlocGeometry, shape: FlocShape): Blob[] {
  const out: Blob[] = [];
  const reach = lightReach(g, shape);
  const size = 0.35 * shape.patchSize * 1e-3;
  if (!(size > 0)) return out;
  const count = Math.min(120000, Math.round((0.7 / (size * size)) * Math.PI * reach * reach));
  const key = flocKey(shape.seed, 7, 0, 1);
  const floor = (1.2 * reach) / FLOC_MAP.lightRings;
  for (let p = 0; p < count; p += 1) {
    const u = (i: number) => flocRandom(key, 4 * p + i);
    const r = reach * Math.sqrt(u(0));
    const phi = TAU * u(1);
    out.push({ x: r * Math.cos(phi), y: r * Math.sin(phi), sigma: Math.max(floor, sigmaOf(size * (0.6 + 0.8 * u(2)))), height: 0.4 + 1.2 * u(3) * u(3) });
  }
  return out;
}

/** The young clumps: short strings of bright blobs along the spiral, gathered where the stars' contrast is high. */
export function flocClumps(g: FlocGeometry, shape: FlocShape): Blob[] {
  const out: Blob[] = [];
  const reach = lightReach(g, shape);
  const size = shape.clumpSize * 1e-3;
  if (!(shape.clumpDensity > 0) || !(size > 0)) return out;
  const pitch = Math.min(80, Math.max(1, g.pitchDeg * shape.pitch)) * DEG;
  const bound = 2;
  const candidates = Math.round(shape.clumpDensity * Math.PI * reach * reach * bound);
  const key = flocKey(shape.seed, 4, 0, 1);
  const floor = (1.2 * reach) / FLOC_MAP.lightRings;
  const inner = Math.max(0, shape.clumpInner);
  for (let p = 0; p < candidates; p += 1) {
    const u = (i: number) => flocRandom(key, 8 * p + i);
    const r = reach * Math.sqrt(u(0));
    const phi = TAU * u(1);
    let x = r * Math.cos(phi);
    let y = r * Math.sin(phi);
    let w = (inner > 0 ? smoothstep(0.6 * inner, 1.2 * inner, r) : 1) * (1 - smoothstep(0.8 * reach, 0.97 * reach, r));
    if (g.pattern && shape.clumpFollow > 0) w *= 1 - shape.clumpFollow + shape.clumpFollow * 2 * clamp01((readField(g.pattern, g.rHi, x, y) - 0.95) / 0.4);
    if (u(2) * bound >= w) continue;
    // The string: a short piece of spiral, clumps dropped along it and a little to its sides.
    const sKey = flocKey(key, p, 0, 2);
    const count = 2 + Math.floor(6 * u(3) * u(3));
    const step = size * (0.9 + 1.2 * u(4));
    const own = pitch + (u(5) - 0.5) * 24 * DEG;
    const c = Math.cos(own);
    const s = Math.sin(own);
    for (let k = 0; k < count; k += 1) {
      const v = (i: number) => flocRandom(sKey, 8 * k + i);
      const rr = Math.hypot(x, y) || 1e-9;
      const tx = (-y * c + x * s) / rr;
      const ty = (x * c + y * s) / rr;
      const across = (v(0) - 0.5) * size * 1.2;
      const cx = x - ty * across;
      const cy = y + tx * across;
      const sigma = Math.max(floor, sigmaOf(size * (0.45 + 0.8 * v(1))));
      const height = 0.5 + 1.3 * v(2) * v(2);
      out.push({ x: cx, y: cy, sigma, height });
      // A brighter, tighter core off its centre: a clump is not round.
      if (v(3) < 0.6) out.push({ x: cx + (v(4) - 0.5) * sigma * 1.5, y: cy + (v(5) - 0.5) * sigma * 1.5, sigma: Math.max(floor, 0.5 * sigma), height: 0.8 * height });
      x += tx * step * (0.6 + 0.8 * v(6));
      y += ty * step * (0.6 + 0.8 * v(6));
    }
  }
  return out;
}

/**
 * A light level read as the GLSL reads it: the patches' level in [0, 1] (0.5 their mean), a clump's in [0, 1], and how
 * far the light is known there (0 under the floor's start, 1 from the floor up: the patches count by this much).
 */
export function flocLight(level: number): { patch: number; clump: number; known: number } {
  const floor = FLOC_MAP.lightFloor;
  return { patch: clamp01((level - floor) / (0.5 - floor)), clump: clamp01((level - 0.5) * 2), known: smoothstep(0, floor, level) };
}

/** What a byte of the map holds (the header's encoding): the dust's shape, or the light's level, or neither. */
export function flocDecode(byte: number): { shape: number; light: number; patch: number; clump: number; known: number } {
  if (byte <= 0) return { shape: 0, light: 0, patch: 0.5, clump: 0, known: 0 };
  const s = (byte - 128) / 127;
  return s > 0 ? { shape: FLOC_MAP.shapeMax * s * s, light: 0, patch: 0.5, clump: 0, known: 0 } : { shape: 0, light: -s, ...flocLight(-s) };
}

/** The radius, kpc, to which the light (the patches and the clumps) is drawn. */
export const lightReach = (g: FlocGeometry, shape: FlocShape): number => Math.min(g.rHi, FLOC_REACH * Math.max(0.1, shape.outerRadius));

/**
 * The lace: the fine network between the filaments, summed into the raster. A smooth noise over the disc whose cells
 * are pieces of the drawn spiral, one size at every radius (Ladder), ridged - a thread wherever the noise crosses its
 * middle value, so the threads close into cells, fork and join - with a second, coarser one on a more open spiral for
 * the cross-links. The ladder's levels are blended BEFORE the ridge: one network at every radius. Where the filaments
 * gather (the bundling, the gas) the threads are thick, and in blotches run together leaving holes - the thick
 * mottled strands; elsewhere they thin to nothing.
 */
function drawLace(raster: Raster, g: FlocGeometry, shape: FlocShape): void {
  if (!(shape.lace > 0) || !(shape.thread > 0)) return;
  const { rings, sectors, dR, dPhi, acc } = raster;
  const pitch = Math.min(80, Math.max(1, g.pitchDeg * shape.pitch)) * DEG;
  const weights = weightsOf(g, shape, pitch);
  const inner = Math.max(0, shape.innerRadius);
  const outer = Math.max(inner + 0.1, Math.min(shape.outerRadius, g.rHi));
  const iLo = Math.max(0, Math.floor((0.5 * inner) / dR));
  const iHi = Math.min(rings - 1, Math.ceil(outer / dR));
  const cell = Math.max(shape.cell * 1e-3, 0.02);
  const stretch = Math.max(shape.stretch, 0.2);
  const threads = new Ladder(pitch, cell, stretch, flocKey(shape.seed, 6, 0, 1));
  const wiggle = new Ladder(pitch, cell, stretch, flocKey(shape.seed, 6, 0, 2));
  const links = new Ladder(Math.min(85 * DEG, pitch + 38 * DEG), 1.7 * cell, stretch, flocKey(shape.seed, 6, 0, 3));
  const blotches = new Ladder(pitch, 2 * cell, stretch, flocKey(shape.seed, 6, 0, 4));
  // Per ring: ln R and its place on the ladder.
  const lnR = new Float64Array(rings);
  const place = new Float64Array(rings);
  for (let i = iLo; i <= iHi; i += 1) {
    const r = (i + 0.5) * dR;
    lnR[i] = Math.log(r);
    place[i] = Ladder.place(r);
  }
  // Where the dust is: the filaments' own number weight, on a coarse grid (every 4th ring, every 8th sector).
  const CR = 4;
  const CS = 8;
  const mRings = Math.floor((iHi - iLo) / CR) + 2;
  const mSectors = Math.floor(sectors / CS);
  const mask = new Float32Array(mRings * mSectors);
  for (let b = 0; b < mSectors; b += 1) {
    const phi = (b + 0.5) * CS * dPhi;
    for (let a = 0; a < mRings; a += 1) {
      const r = (iLo + a * CR + 0.5) * dR;
      mask[b * mRings + a] = smoothstep(0.1, 1.5, weights.start(r * Math.cos(phi), r * Math.sin(phi)));
    }
  }
  for (let j = 0; j < sectors; j += 1) {
    const phi = (j + 0.5) * dPhi;
    const row = j * rings;
    const fb = (j + 0.5) / CS - 0.5;
    const b0 = Math.floor(fb);
    const bw = fb - b0;
    const m0 = (((b0 % mSectors) + mSectors) % mSectors) * mRings;
    const m1 = ((((b0 + 1) % mSectors) + mSectors) % mSectors) * mRings;
    for (let i = iLo; i <= iHi; i += 1) {
      const fa = (i - iLo) / CR;
      const a0 = Math.floor(fa);
      const aw = fa - a0;
      const m = (1 - bw) * ((1 - aw) * mask[m0 + a0] + aw * mask[m0 + a0 + 1]) + bw * ((1 - aw) * mask[m1 + a0] + aw * mask[m1 + a0 + 1]);
      // Under 0.12 the lace has no depth (below).
      if (m <= 0.12) continue;
      const ln = lnR[i];
      const at = place[i];
      // A blotch: where the dust gathers and a coarser noise (cells twice the lace's) is high, the threads thicken
      // until they run together, leaving holes.
      const blotch = shape.blotch > 0 ? smoothstep(0.55, 0.75, 0.45 * m + 0.55 * blotches.at(ln, phi, at)) : 0;
      // A thread's thickness swells and thins along it (a third noise, cells a little finer than the lace's): it breaks
      // into pieces, and a closed ring is rare. A thread thinner than about a twentieth of a cell is a hairline no eye
      // reads as dust: it fades out.
      const t = shape.thread * (0.3 + 0.9 * m + 3.2 * shape.blotch * blotch) * (0.5 + 1.0 * blotches.at(ln, phi, at, 3));
      if (t <= 0.03) continue;
      // The threads: the noise and two finer ones riding on it (the wiggle, the roughness), ridged about the middle.
      const n1 = 0.62 * threads.at(ln, phi, at) + 0.26 * wiggle.at(ln, phi, at, 2) + 0.12 * wiggle.at(ln, phi, at, 4);
      let ridge = 1 - Math.abs(2 * n1 - 1) / t;
      // The cross-links only where the first is not already a thread.
      if (ridge < 0.7) ridge = Math.max(ridge, 0.7 * (1 - Math.abs(2 * links.at(ln, phi, at) - 1) / (0.5 * t)));
      if (ridge <= 0) continue;
      acc[row + i] += shape.lace * smoothstep(0.12, 0.5, m) * smoothstep(0.03, 0.09, t) * (0.75 + 0.5 * blotch) * ridge * ridge * (3 - 2 * ridge);
    }
  }
}

/**
 * The feature's channel of the shared map for a geometry and a shape: `rings` bytes to a row (R, over 0-rHi) and
 * `sectors` rows (phi), in the header's encoding. The same inputs give the same bytes.
 */
export function buildFlocChannel(g: FlocGeometry, shape: FlocShape, rings: number = FLOC_MAP.rings, sectors: number = FLOC_MAP.sectors): Uint8Array {
  const raster = new Raster(rings, sectors, g.rHi);
  drawLace(raster, g, shape);
  for (const s of flocStrands(g, shape)) drawStrand(raster, s);
  const reach = lightReach(g, shape);
  const patches = new Raster(FLOC_MAP.lightRings, FLOC_MAP.lightSectors, reach);
  for (const b of flocPatches(g, shape)) patches.spot(b.x, b.y, b.sigma, b.height);
  const grains = new Raster(FLOC_MAP.lightRings, FLOC_MAP.lightSectors, reach);
  for (const b of flocGrains(g, shape)) grains.spot(b.x, b.y, b.sigma, b.height);
  const clumps = new Raster(FLOC_MAP.lightRings, FLOC_MAP.lightSectors, reach);
  for (const b of flocClumps(g, shape)) clumps.spot(b.x, b.y, b.sigma, b.height);
  // The patches' level is 1 - exp(-sum), grained (a patch is a cloud of small bright grains), scaled so that its mean
  // over the disc's area inside 0.85 of the reach is 0.5 (as the light's level: half way from the floor to 0.5), so
  // the GLSL swells and thins the light about a constant.
  let sum = 0;
  let weight = 0;
  const pAcc = patches.acc;
  for (let k = 0; k < pAcc.length; k += 1) {
    pAcc[k] = (1 - Math.exp(-pAcc[k])) * (0.4 + 0.6 * (1 - Math.exp(-grains.acc[k])));
    const i = k % patches.rings;
    if (i + 0.5 < 0.85 * patches.rings) {
      sum += pAcc[k] * (i + 0.5);
      weight += i + 0.5;
    }
  }
  const scale = sum > 0 ? (0.5 * weight) / sum : 0;
  // The light's level about the patches' mean on the coarse raster: the patches from the floor up to half, a clump
  // over them up to 1; toward the light's reach it goes to the mean (0 here).
  const cAcc = clumps.acc;
  for (let k = 0; k < pAcc.length; k += 1) {
    const base = FLOC_MAP.lightFloor + (0.5 - FLOC_MAP.lightFloor) * Math.min(1, scale * pAcc[k]);
    const r = ((k % patches.rings) + 0.5) * patches.dR;
    pAcc[k] = (base + (1 - base) * (1 - Math.exp(-cAcc[k])) - MEAN) * (1 - smoothstep(0.85 * reach, reach, r));
  }

  // Every byte the patches' mean level (which changes nothing), then the disc inside the reach.
  const none = 128 - Math.round(127 * MEAN);
  const out = new Uint8Array(rings * sectors).fill(none);
  const acc = raster.acc;
  const grain = Math.max(shape.grain * 1e-3, 1e-3);
  const mKey = flocKey(shape.seed, 5, 0, 1);
  const lit = Math.min(rings, Math.ceil(reach / raster.dR));
  const inside = Math.min(rings, Math.max(lit, Math.ceil((Math.min(shape.outerRadius, g.rHi) + 1) / raster.dR)));
  // Each ring's place on the coarse raster (its lower ring and the weight of the next); -1 beyond it.
  const lo = new Int32Array(inside);
  const up = new Float32Array(inside);
  for (let i = 0; i < inside; i += 1) {
    const u = ((i + 0.5) * raster.dR) / patches.dR - 0.5;
    lo[i] = i < lit && u < patches.rings - 1 ? Math.max(0, Math.floor(u)) : -1;
    up[i] = Math.max(0, u - lo[i]);
  }
  for (let j = 0; j < sectors; j += 1) {
    const phi = (j + 0.5) * raster.dPhi;
    const c = Math.cos(phi) / grain;
    const s = Math.sin(phi) / grain;
    const row = j * rings;
    const v0 = phi / patches.dPhi - 0.5;
    const j0 = Math.floor(v0);
    const bw = v0 - j0;
    const r0 = (((j0 % patches.sectors) + patches.sectors) % patches.sectors) * patches.rings;
    const r1 = ((((j0 + 1) % patches.sectors) + patches.sectors) % patches.sectors) * patches.rings;
    for (let i = 0; i < inside; i += 1) {
      let v = acc[row + i];
      if (v > 1e-3 && shape.mottle > 0) {
        // The mottle: the dust's depth swelled and thinned over the plane at the grain's length and a third of it,
        // so a blotch has holes and a thread has knots.
        const r = (i + 0.5) * raster.dR;
        const m = 0.6 * noise2(r * c, r * s, mKey) + 0.4 * noise2(r * c * 3.1 + 17.3, r * s * 3.1 + 5.9, mKey ^ 0x2545f491);
        v *= Math.max(0, 1 + shape.mottle * 1.7 * (2 * m - 1));
      }
      if (v >= MARGIN) out[row + i] = 128 + Math.round(127 * Math.sqrt(Math.min(1, (v - MARGIN) / FLOC_MAP.shapeMax)));
      else if (lo[i] >= 0) {
        // The light, where no filament lies; toward a filament's margin it goes to the mean.
        const a0 = lo[i];
        const aw = up[i];
        const level = (1 - aw) * ((1 - bw) * pAcc[r0 + a0] + bw * pAcc[r1 + a0]) + aw * ((1 - bw) * pAcc[r0 + a0 + 1] + bw * pAcc[r1 + a0 + 1]);
        out[row + i] = 128 - Math.round(127 * (MEAN + level * (1 - Math.max(0, v) / MARGIN)));
      }
    }
  }
  return out;
}

/** The share of the disc's area between two radii (kpc) where the dust's shape is at least `level`. */
export function flocCover(map: Uint8Array, g: FlocGeometry, rIn: number, rOut: number, level = 0.25, rings: number = FLOC_MAP.rings, sectors: number = FLOC_MAP.sectors): number {
  const least = 128 + Math.ceil(127 * Math.sqrt(level / FLOC_MAP.shapeMax));
  let covered = 0;
  let all = 0;
  for (let i = 0; i < rings; i += 1) {
    const r = ((i + 0.5) * g.rHi) / rings;
    if (r < rIn || r > rOut) continue;
    let n = 0;
    for (let j = 0; j < sectors; j += 1) if (map[j * rings + i] >= least) n += 1;
    covered += n * r;
    all += sectors * r;
  }
  return all > 0 ? covered / all : 0;
}
