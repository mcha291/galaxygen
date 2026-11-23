// The flocculent network drawn in the disc's plane (S106, builder C): the network's second style (floc.ts `style` 1,
// NGC 4414's default). ILLUSTRATIVE, display-only structure of the viewer's own (the lead's ruling 12): HST's NGC 4414
// shows brown dust in soft, feathered filaments and irregular patches a few hundred parsecs across that string together
// into many short spiral arcs, and the starlight between them clumped into cream "cauliflower" clouds; no published
// field draws either. S105's style (flocMap.ts: strands and a lace on spiral lattices) read as brushed dashes - every
// cell of its noise was stretched along the azimuth - so this style takes its small-scale structure from noise
// evaluated in CARTESIAN kiloparsecs (x = R cos phi, y = R sin phi), isotropic in the small: a domain-warped cloud fBm
// and a ridged multi-octave net, each octave turned by its own angle so no axis shows. Only the large scale is spiral:
// a mask of short arcs on the drawn pitch (flocMap.ts Ladder, cells `arcWidth` across and `arcStretch` times as long),
// so the feathered pieces line up into arcs. What is the model's: the pitch (pitch_angle times the `pitch` slider) and
// the gas's radial profile (the radial fall); the rest is a seeded drawing, fixed in the galaxy's frame.
//
// Written into the floc channel in flocMap.ts's encoding (dust above 128, the light's level below): the dust where the
// drawn depth passes the margin, the light (the clouds' level and their brightest knots) everywhere else inside the
// light's reach, going to the patches' mean toward a dust margin and toward the reach.

import { FLOC_MAP, Ladder, type FlocGeometry, type FlocShape, flocKey, noise2 } from "./flocMap";

const TAU = 2 * Math.PI;
const DEG = Math.PI / 180;
const clamp01 = (v: number) => Math.min(1, Math.max(0, v));
const smoothstep = (e0: number, e1: number, v: number) => {
  const t = clamp01((v - e0) / (e1 - e0));
  return t * t * (3 - 2 * t);
};

/** Each octave's turn (cos, sin) and offset: no two octaves share an axis. */
const OCT = Array.from({ length: 6 }, (_, o) => ({ c: Math.cos(0.9 + 1.37 * o), s: Math.sin(0.9 + 1.37 * o), dx: 17.3 * o + 3.1, dy: 9.7 * o + 5.3 }));

/** fBm of value noise in [0, 1] (mean about a half), `oct` octaves, the first at unit cells. */
export function fbm(x: number, y: number, key: number, oct: number): number {
  let sum = 0;
  let norm = 0;
  let amp = 1;
  let f = 1;
  for (let o = 0; o < oct; o += 1) {
    const q = OCT[o];
    sum += amp * noise2(f * (q.c * x - q.s * y) + q.dx, f * (q.s * x + q.c * y) + q.dy, key + o);
    norm += amp;
    amp *= 0.5;
    f *= 2.03;
  }
  return sum / norm;
}

/** A ridged multifractal in [0, 1]: thin bright ridges where the noise crosses its middle, each octave weighted by the last. */
export function ridged(x: number, y: number, key: number, oct: number, sharp: number): number {
  let sum = 0;
  let norm = 0;
  let amp = 1;
  let f = 1;
  let w = 1;
  for (let o = 0; o < oct; o += 1) {
    const q = OCT[o];
    const n = noise2(f * (q.c * x - q.s * y) + q.dx, f * (q.s * x + q.c * y) + q.dy, key + 31 * o);
    let r = 1 - Math.abs(2 * n - 1);
    r = r ** sharp * w;
    w = clamp01(r * 1.8);
    sum += amp * r;
    norm += amp;
    amp *= 0.55;
    f *= 2.07;
  }
  return sum / norm;
}

/** A billowed fBm in [0, 1]: rounded puffs, each octave's tops round, the "cauliflower" of the clouds. */
export function billow(x: number, y: number, key: number, oct: number): number {
  let sum = 0;
  let norm = 0;
  let amp = 1;
  let f = 1;
  for (let o = 0; o < oct; o += 1) {
    const q = OCT[o];
    const n = 2 * noise2(f * (q.c * x - q.s * y) + q.dx, f * (q.s * x + q.c * y) + q.dy, key + 57 * o) - 1;
    sum += amp * (1 - n * n);
    norm += amp;
    amp *= 0.5;
    f *= 2.11;
  }
  return sum / norm;
}

/** The network's fields at one place: everything the map and the clouds' points read. */
export interface NetSampler {
  /** The dust's drawn depth at (x, y) kpc: 1 a full filament's centre. */
  dust(x: number, y: number): number;
  /** The clouds' level at (x, y) in [0, 1] (about a half on average): the light between the dust. */
  light(x: number, y: number): number;
  /** The brightest knots' level at (x, y) in [0, 1], `p` the light's level there. */
  knot(x: number, y: number, p: number): number;
  /** The radius the dust reaches, kpc. */
  outer: number;
  /** The radius the light reaches, kpc. */
  reach: number;
}

/** The light's reach in the plane style, kpc: the light's own reach (`litReach` times the outer radius), within the grid. */
export const netReach = (g: FlocGeometry, shape: FlocShape): number => Math.min(g.rHi, Math.max(0.1, shape.litReach) * Math.max(0.1, shape.outerRadius));

/** The sampler for a geometry and a shape. */
export function netSampler(g: FlocGeometry, shape: FlocShape): NetSampler {
  const pitch = Math.min(80, Math.max(1, g.pitchDeg * shape.pitch)) * DEG;
  const inner = Math.max(0, shape.innerRadius);
  const outer = Math.max(inner + 0.1, Math.min(shape.outerRadius, g.rHi));
  const reach = netReach(g, shape);
  const profile = g.gasProfile;
  const rings = profile ? profile.length : 0;
  const at = (r: number) => (profile ? Number(profile[Math.min(rings - 1, Math.max(0, Math.floor((r / g.rHi) * rings)))]) : 1);
  const ref = Math.max(at(0.5 * outer), 1e-12);
  const radial = (r: number) => (profile && shape.radial > 0 ? Math.min(2, Math.max(0, at(r) / ref) ** shape.radial) : 1);
  const fade = (r: number) => (inner > 0 ? smoothstep(0.5 * inner, 1.5 * inner, r) : 1) * (1 - smoothstep(0.6 * outer, outer, r));
  const s = Math.max(shape.netScale * 1e-3, 0.01);
  const ls = Math.max(shape.litScale * 1e-3, 0.01);
  const arcs = new Ladder(pitch, Math.max(shape.arcWidth * 1e-3, 0.05), Math.max(shape.arcStretch, 0.5), flocKey(shape.seed, 9, 0, 1));
  const kw = flocKey(shape.seed, 9, 0, 2);
  const kc = flocKey(shape.seed, 9, 0, 3);
  const kn = flocKey(shape.seed, 9, 0, 4);
  const kl = flocKey(shape.seed, 9, 0, 5);
  const kk = flocKey(shape.seed, 9, 0, 6);
  const warp = shape.netWarp * s;
  const lo = shape.netGaps - shape.netSoft;
  const hi = shape.netGaps + shape.netSoft;
  const dust = (x: number, y: number): number => {
    const r = Math.hypot(x, y);
    const f = fade(r);
    if (f <= 0 || shape.netDepth <= 0) return 0;
    // The domain warp: the plane pushed about by a coarse noise, so the pieces curl and feather.
    const wx = x + warp * (2 * noise2(x / (1.7 * s), y / (1.7 * s), kw) - 1);
    const wy = y + warp * (2 * noise2(x / (1.7 * s) + 41.2, y / (1.7 * s) + 13.7, kw) - 1);
    const cloud = fbm(wx / s, wy / s, kc, 3);
    let m = cloud;
    if (shape.netArc > 0) {
      let phi = Math.atan2(y, x);
      if (phi < 0) phi += TAU;
      const arc = arcs.at(Math.log(Math.max(r, 1e-3)), phi, Ladder.place(r));
      m = shape.netArc * (0.6 * arc + 0.4 * cloud) + (1 - shape.netArc) * cloud;
    }
    const cover = smoothstep(lo, hi, m);
    if (cover <= 0) return 0;
    const net = ridged(wx / (0.55 * s), wy / (0.55 * s), kn, 4, 2.2);
    const feather = 1 - shape.netFeather + shape.netFeather * 2.2 * net;
    return shape.netDepth * cover * feather * f * radial(r);
  };
  const light = (x: number, y: number): number => {
    const wx = x + 0.5 * ls * (2 * fbm(x / (2 * ls), y / (2 * ls), kw + 7, 2) - 1);
    const wy = y + 0.5 * ls * (2 * fbm(x / (2 * ls) + 23.1, y / (2 * ls) + 7.9, kw + 7, 2) - 1);
    return clamp01(0.5 + 1.6 * (billow(wx / ls, wy / ls, kl, 4) - 0.62));
  };
  // The knots: the peaks of a fine noise (cells 70 pc) where the clouds are bright (`p`, the light's level there).
  const knot = (x: number, y: number, p: number): number => {
    if (!(shape.litKnots > 0) || p < 0.45) return 0;
    const n = noise2(x / 0.07 + 3.3, y / 0.07 + 1.9, kk);
    return smoothstep(1 - 0.12 * shape.litKnots, 1, n) * smoothstep(0.45, 0.8, p);
  };
  return { dust, light, knot, outer, reach };
}

/** The patches' mean level and the margin (flocMap.ts's encoding). */
const MARGIN = FLOC_MAP.margin;
const MEAN = FLOC_MAP.lightFloor + 0.25 * (1 - 2 * FLOC_MAP.lightFloor);


/** A field sampled on a coarse polar grid over 0-rMax (row = sector), read back bilinearly. */
class Coarse {
  readonly v: Float32Array;
  readonly dR: number;
  readonly dPhi: number;
  constructor(readonly rings: number, readonly sectors: number, readonly rMax: number, fn: (x: number, y: number, r: number) => number) {
    this.v = new Float32Array(rings * sectors);
    this.dR = rMax / rings;
    this.dPhi = TAU / sectors;
    for (let j = 0; j < sectors; j += 1) {
      const c = Math.cos((j + 0.5) * this.dPhi);
      const s = Math.sin((j + 0.5) * this.dPhi);
      for (let i = 0; i < rings; i += 1) {
        const r = (i + 0.5) * this.dR;
        this.v[j * rings + i] = fn(r * c, r * s, r);
      }
    }
  }

  /** The value at radius r (kpc) and the sector coordinate `u` (phi / dPhi - 0.5, already wrapped to [0, sectors)). */
  at(r: number, u: number): number {
    const { rings, sectors, v } = this;
    const a = Math.min(rings - 1.0001, Math.max(0, r / this.dR - 0.5));
    const i = Math.floor(a);
    const fa = a - i;
    const j0 = Math.floor(u);
    const fb = u - j0;
    const r0 = ((j0 + sectors) % sectors) * rings;
    const r1 = ((j0 + 1) % sectors) * rings;
    return (1 - fb) * ((1 - fa) * v[r0 + i] + fa * v[r0 + i + 1]) + fb * ((1 - fa) * v[r1 + i] + fa * v[r1 + i + 1]);
  }
}

/** The coarse grids' cells over the map's (radial, azimuthal): the dust's and the light's. */
export const NET_GRID = { dust: 2, light: 4 } as const;

/**
 * The floc channel in the plane style: flocMap.ts's encoding, `rings` bytes to a row over 0-rHi and `sectors` rows. The
 * dust is evaluated on a grid twice the map's cells and the light on one four times them, each read back bilinearly
 * (the fields are smooth at those cells; the finest dust octave is ~45 pc), then encoded texel by texel: a slider's
 * rebuild stays near a quarter of a second.
 */
export function buildNetChannel(g: FlocGeometry, shape: FlocShape, rings: number = FLOC_MAP.rings, sectors: number = FLOC_MAP.sectors): Uint8Array {
  const net = netSampler(g, shape);
  const none = 128 - Math.round(127 * MEAN);
  const out = new Uint8Array(rings * sectors).fill(none);
  const dR = g.rHi / rings;
  const dPhi = TAU / sectors;
  const lit = Math.min(rings, Math.ceil(net.reach / dR));
  const dusty = Math.min(lit, Math.ceil(net.outer / dR));
  const dSect = Math.max(8, Math.floor(sectors / NET_GRID.dust));
  const lSect = Math.max(8, Math.floor(sectors / NET_GRID.light));
  const dust = new Coarse(Math.max(2, Math.ceil(dusty / NET_GRID.dust)), dSect, Math.max(dusty, 1) * dR, (x, y) => net.dust(x, y));
  const light = new Coarse(Math.max(2, Math.ceil(lit / NET_GRID.light)), lSect, Math.max(lit, 1) * dR, (x, y) => net.light(x, y));
  const floor = FLOC_MAP.lightFloor;
  for (let j = 0; j < sectors; j += 1) {
    const phi = (j + 0.5) * dPhi;
    const c = Math.cos(phi);
    const s = Math.sin(phi);
    const ud = (phi / TAU) * dSect - 0.5;
    const ul = (phi / TAU) * lSect - 0.5;
    const udw = ud < 0 ? ud + dSect : ud;
    const ulw = ul < 0 ? ul + lSect : ul;
    const row = j * rings;
    for (let i = 0; i < lit; i += 1) {
      const r = (i + 0.5) * dR;
      const v = i < dusty ? dust.at(r, udw) : 0;
      if (v >= MARGIN) {
        out[row + i] = 128 + Math.round(127 * Math.sqrt(Math.min(1, (v - MARGIN) / FLOC_MAP.shapeMax)));
        continue;
      }
      const p = light.at(r, ulw);
      const k = net.knot(r * c, r * s, p);
      let l = floor + (0.5 - floor) * p;
      if (k > 0) l = 0.5 + 0.5 * k;
      const edge = 1 - smoothstep(0.85 * net.reach, net.reach, r);
      l = MEAN + (l - MEAN) * edge * (1 - Math.max(0, v) / MARGIN);
      out[row + i] = 128 - Math.round(127 * l);
    }
  }
  return out;
}
