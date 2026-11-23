// The flocculent network drawn in the disc's plane (S106, builder C; the second pass C3): the network's second style
// (floc.ts `style` 1, NGC 4414's default). ILLUSTRATIVE, display-only structure of the viewer's own (the lead's ruling
// 12): HST's NGC 4414 shows its dust as MANY THIN FILAMENTS - dark brown threads a few tens of parsecs wide and a few
// hundred long, feathered and branching, strung end to end into dozens of narrow spiral arcs from the nucleus to the
// edge, densest in a broad ring and on the near side - and the starlight between them clumped into cream puffs; no
// published field draws either.
//
// The dust: the ridge lines of two families of spiral value noise (flocMap.ts Ladder: cells `filSpacing` across the
// spiral and `filRun` times as long along it, one size in parsecs at every radius) - where a family's noise crosses its
// middle a thread runs, so the threads follow the drawn pitch, fork and join where the noise's contours do, and swell
// into knots where they flatten or cross. The finer family (`wisps`) is half the spacing. Each family is cut into pieces
// a few hundred parsecs long by an isotropic noise in CARTESIAN kiloparsecs (`netScale`, `netGaps`, `netSoft`), its
// thickness feathered by a finer one (`netFeather`), the plane pushed about only a little first (`netWarp`: a wiggle, no
// curls). The amount: a coarse mask of arcs on the spiral (`netArc`, `arcWidth`, `arcStretch`), the gas's radial
// profile to a power (`radial`), a ring (`ringIn`, `ringOut`, `core`, `rim`), a near-side bias (`nearBias`, `nearAz`).
// What is the model's: the pitch (pitch_angle times the `pitch` slider) and the gas's radial profile; the rest is a
// seeded drawing, fixed in the galaxy's frame.
//
// The light between: a cloud fBm in Cartesian kiloparsecs (`litScale`), and a soft glow under each star cloud's group
// (flocClouds.ts; `cloudGlow`). The finest grain of the light (puffs of tens of parsecs) is floc.ts's GLSL, not the map.
//
// Written into the floc channel: the dust above 128 in flocMap.ts's encoding, the light below 128 in the plane style's
// own (floc.ts illFlocRead, illFlocStyle 1): q = 0.6 p for the clouds' level p (0.3 neutral), over 0.6 a group's glow
// (the clump level); toward the light's reach it goes to neutral, toward a dust margin to 0 (a soft shade, never a rim).

// S106 third pass (C4): the threads' mesh controls (broad mottled lanes, feathers along them, spurs at an angle, an
// exact tangle of the threads' plane, tapered ends, the wisps' width and run); with netDepth 0 (NGC 4414's default:
// its dust is floc.ts's mesh, drawn in the march) no dust grid is built. The groups' glow is summed on a grid four
// times coarser and laid on bilinearly (paintGlow): a slider's rebuild in the browser 0.15-0.19 s.

import { buildClouds } from "./flocClouds";
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

/** The dust's amounts at a place: each family's (in full threads) and the threads' width there (x the width asked). */
export interface Amount {
  a1: number;
  a2: number;
  fe: number;
  /** S106 third pass: the broad lanes' amount, the spurs', and the threads' and wisps' piece levels (their taper). */
  aL: number;
  aS: number;
  p1: number;
  p2: number;
}

/** An Amount's fields in the order the coarse grid keeps them. */
const AMOUNT_KEYS = ["a1", "a2", "fe", "aL", "aS", "p1", "p2"] as const;

/** The network's fields at one place: everything the map and the clouds' points read. */
export interface NetSampler {
  /** The dust's drawn depth at (x, y) kpc: 1 a full filament's centre. */
  dust(x: number, y: number): number;
  /** The clouds' level at (x, y) in [0, 1] (about a half on average): the light between the dust. */
  light(x: number, y: number): number;
  /** The dust's amounts (each family's) and feathering at a place (r its radius, phi its azimuth in [0, 2 pi)). */
  amount(x: number, y: number, r: number, phi: number, out: Amount): void;
  /** The dust's threads at a place given the amounts there: dust(x, y) is threads at amount's values. */
  threads(x: number, y: number, r: number, phi: number, am: Amount): number;
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
  // The amount by radius: the inner cut, the ring (core inside, rim outside), to nothing at the outer radius.
  const ringIn = Math.max(0.01, shape.ringIn) * outer;
  const ringOut = Math.max(0.02, shape.ringOut) * outer;
  const ring = (r: number) =>
    (inner > 0 ? smoothstep(0.5 * inner, 1.5 * inner, r) : 1) *
    (shape.core + (1 - shape.core) * smoothstep(0.4 * ringIn, ringIn, r)) *
    (1 - (1 - shape.rim) * smoothstep(ringOut, Math.max(ringOut + 0.01, 0.95 * outer), r)) *
    (1 - smoothstep(0.88 * outer, outer, r));
  const s = Math.max(shape.netScale * 1e-3, 0.01);
  const A = Math.max(shape.filSpacing * 1e-3, 0.02);
  const run = Math.max(shape.filRun, 0.5);
  const fam1 = new Ladder(pitch, A, run, flocKey(shape.seed, 9, 1, 1));
  const fam2 = new Ladder(Math.min(80 * DEG, pitch * 1.35), 0.5 * A, Math.max(0.1, shape.wispRun) * run, flocKey(shape.seed, 9, 1, 2));
  const arcs = new Ladder(pitch, Math.max(shape.arcWidth * 1e-3, 0.05), Math.max(shape.arcStretch, 0.5), flocKey(shape.seed, 9, 0, 1));
  const kw = flocKey(shape.seed, 9, 0, 2);
  const kp = flocKey(shape.seed, 9, 0, 3);
  const kf = flocKey(shape.seed, 9, 0, 4);
  const kl = flocKey(shape.seed, 9, 0, 5);
  const warp = shape.netWarp * A;
  const lo = shape.netGaps - shape.netSoft;
  const hi = shape.netGaps + shape.netSoft;
  // A thread's half width at half depth, kpc (the finer family's a little thinner): a thread is drawn on its family's
  // middle crossing at the distance |n - 1/2| / |grad n| from it, so it keeps one width, and where the noise lies flat
  // (no crossing near) nothing is drawn - no blob.
  const half = Math.max(shape.width * 1e-3, 0.005) / 2;
  const nearAz = shape.nearAz * DEG;
  const LN2 = Math.LN2;
  const probe = { v: 0, g: 0 };
  // A family's distance from its nearest thread, kpc (the noise's middle crossing over its slope).
  const dist = (fam: Ladder, lnR: number, phi: number, place: number, r: number) => {
    fam.atSlope(lnR, phi, place, r, probe);
    return Math.abs(probe.v - 0.5) / Math.max(probe.g, 1e-6);
  };
  const profile1 = (d: number, h: number) => {
    const e = (LN2 * d * d) / (h * h);
    return e > 6 ? 0 : Math.exp(-e);
  };
  const thread = (fam: Ladder, lnR: number, phi: number, place: number, r: number, h: number) => profile1(dist(fam, lnR, phi, place, r), h);
  // S106 third pass (C4): the mesh. The broad soft lanes (a coarse family, short flocculent arcs), the feathers they
  // carry (the threads and wisps gathered along their sides), the spurs (a family at an angle to the spiral, drawn
  // near the lanes and the threads), the tangle (the threads' plane pushed about exactly over a few spacings, so they
  // diverge, cross and merge), the taper (a thread thins toward its piece's ends).
  const famL = new Ladder(pitch, Math.max(shape.laneSpacing * 1e-3, 0.1), Math.max(shape.laneRun, 0.5), flocKey(shape.seed, 9, 1, 3));
  const halfL = Math.max(shape.laneWidth * 1e-3, 0.01) / 2;
  const famS = new Ladder(Math.min(85 * DEG, pitch + Math.max(0, shape.spurAngle) * DEG), 0.8 * A, 1.5, flocKey(shape.seed, 9, 1, 4));
  const kt = flocKey(shape.seed, 9, 0, 6);
  const tw = Math.max(0, shape.tangle) * A;
  const ts = 4 * A;
  const needLane = shape.laneDepth > 0 || shape.feathers > 0;
  const amount = (x: number, y: number, r: number, phi: number, out: Amount): void => {
    out.a1 = 0;
    out.a2 = 0;
    out.fe = 1;
    out.aL = 0;
    out.aS = 0;
    out.p1 = 1;
    out.p2 = 1;
    const f = ring(r);
    if (f <= 0 || shape.netDepth <= 0) return;
    // The pieces: an isotropic noise cuts each family's threads into runs of a few hundred parsecs (the lanes' into
    // runs two and a half times as long, the spurs' into short barbs).
    const p1 = smoothstep(lo, hi, fbm(x / s, y / s, kp, 2));
    const p2 = shape.wisps > 0 ? smoothstep(lo, hi, fbm(x / (0.6 * s) + 11.3, y / (0.6 * s) + 4.1, kp + 17, 2)) : 0;
    const pL = shape.laneDepth > 0 ? smoothstep(lo, hi, fbm(x / (2.5 * s) + 3.7, y / (2.5 * s) + 19.1, kp + 31, 2)) : 0;
    const pS = shape.spurs > 0 ? smoothstep(lo + 0.08, hi + 0.08, fbm(x / (0.45 * s) + 27.1, y / (0.45 * s) + 1.3, kp + 43, 2)) : 0;
    if (p1 <= 0 && p2 <= 0 && pL <= 0 && pS <= 0) return;
    let a = shape.netDepth * f * radial(r);
    if (shape.netArc > 0) a *= 1 - shape.netArc + shape.netArc * 2.2 * smoothstep(0.38, 0.72, arcs.at(Math.log(Math.max(r, 1e-3)), phi, Ladder.place(r)));
    if (shape.nearBias > 0) a *= 1 + shape.nearBias * Math.cos(phi - nearAz);
    if (a <= 0) return;
    out.a1 = a * p1;
    out.a2 = a * shape.wisps * p2;
    out.aL = a * shape.laneDepth * pL;
    out.aS = a * shape.spurs * pS;
    out.p1 = p1;
    out.p2 = p2;
    // The feathers: each thread's width swells and thins along it (thin threads, knots where it swells).
    if (shape.netFeather > 0) out.fe = Math.max(0.2, 1 - shape.netFeather + shape.netFeather * 1.7 * fbm(x / (0.9 * A) + 7.7, y / (0.9 * A) + 2.2, kf, 2));
  };
  // The threads at a place, given the amounts there.
  const threads = (x: number, y: number, r: number, phi: number, am: Amount): number => {
    const { a1, a2, fe, aL, aS } = am;
    if (a1 <= 0 && a2 <= 0 && aL <= 0 && aS <= 0) return 0;
    let lnR = Math.log(Math.max(r, 1e-3));
    const place = Ladder.place(r);
    let v = 0;
    // The broad lanes, in the unpushed plane, and how near one is (the feathers keep to their sides).
    let prox = 1;
    if (needLane) {
      const dL = dist(famL, lnR, phi, place, r);
      // Mottled: a lane is smoke broken into blotches and holes, not a painted band.
      if (aL > 0) v += aL * profile1(dL, halfL * (0.6 + 0.4 * fe)) * Math.max(0, 1.9 * fbm(x / (1.2 * halfL) + 2.9, y / (1.2 * halfL) + 6.1, kt + 11, 2) - 0.45);
      if (shape.feathers > 0) {
        const q = dL / (3 * halfL);
        prox = 1 - shape.feathers + shape.feathers * 2 * Math.exp(-q * q);
      }
    }
    // The tangle: the threads' plane pushed about exactly by up to `tangle` spacings over four.
    let tr = r;
    let tPlace = place;
    if (tw > 0) {
      const X = x + tw * (2 * fbm(x / ts, y / ts, kt, 2) - 1);
      const Y = y + tw * (2 * fbm(x / ts + 31.7, y / ts + 8.3, kt + 5, 2) - 1);
      tr = Math.max(Math.hypot(X, Y), 1e-3);
      lnR = Math.log(tr);
      phi = Math.atan2(Y, X);
      if (phi < 0) phi += TAU;
      x = X;
      y = Y;
      tPlace = Ladder.place(tr);
    }
    // The wiggle: the place pushed about by a fraction of a spacing, so a thread wanders without curling.
    if (warp > 0) {
      const wx = warp * (2 * noise2(x / (3 * A), y / (3 * A), kw) - 1);
      const wy = warp * (2 * noise2(x / (3 * A) + 41.2, y / (3 * A) + 13.7, kw) - 1);
      // To first order in the push (it is a fraction of a spacing, far under the radius).
      lnR += (x * wx + y * wy) / (tr * tr);
      phi += (x * wy - y * wx) / (tr * tr);
    }
    const taper = Math.max(0, Math.min(1, shape.taper));
    let t1 = 0;
    let d1 = 1e9;
    if (a1 > 0 || aS > 0) {
      d1 = dist(fam1, lnR, phi, tPlace, tr);
      if (a1 > 0) {
        t1 = profile1(d1, half * fe * (1 - taper * (1 - am.p1)));
        v += prox * a1 * t1;
      }
    }
    if (a2 > 0) v += prox * a2 * thread(fam2, lnR, phi, tPlace, tr, shape.wispWidth * half * fe * (1 - taper * (1 - am.p2))) * (1 + 0.8 * t1);
    // The spurs: barbs at an angle, drawn only within a few widths of a thread or a lane's side.
    if (aS > 0) {
      const near = Math.max(Math.exp(-((d1 / (6 * half)) ** 2)), needLane ? (prox - (1 - shape.feathers)) / Math.max(2 * shape.feathers, 1e-6) : 0);
      if (near > 0.02) v += aS * near * thread(famS, lnR, phi, tPlace, tr, 0.8 * half * fe) * (1 + 0.8 * t1);
    }
    // The haze: a share of the amount drawn smooth, the smoky brown the threads lie in.
    return v + shape.haze * a1;
  };
  const probeA: Amount = { a1: 0, a2: 0, fe: 1, aL: 0, aS: 0, p1: 1, p2: 1 };
  const dust = (x: number, y: number): number => {
    const r = Math.hypot(x, y);
    let phi = Math.atan2(y, x);
    if (phi < 0) phi += TAU;
    amount(x, y, r, phi, probeA);
    return threads(x, y, r, phi, probeA);
  };
  const ls = Math.max(shape.litScale * 1e-3, 0.01);
  const light = (x: number, y: number): number => {
    const wx = x + 0.5 * ls * (2 * fbm(x / (2 * ls), y / (2 * ls), kw + 7, 2) - 1);
    const wy = y + 0.5 * ls * (2 * fbm(x / (2 * ls) + 23.1, y / (2 * ls) + 7.9, kw + 7, 2) - 1);
    // Bright rounded puffs over a middling ground with a few darker gaps, so the clouds read as cream clumps.
    const n = 0.7 * fbm(wx / ls, wy / ls, kl, 3) + 0.3 * billow(wx / (0.5 * ls), wy / (0.5 * ls), kl + 3, 2);
    return clamp01(0.42 + 0.58 * smoothstep(0.55, 0.8, n) - 0.3 * smoothstep(0.5, 0.3, n));
  };
  return { dust, amount, threads, light, outer, reach };
}

/** The star clouds' glow is summed on a grid this many times coarser each way than the map's (paintGlow). */
const GLOW_K = 4;

/** The dust margin (flocMap.ts). */
const MARGIN = FLOC_MAP.margin;

/** Fields sampled on a coarse polar grid over 0-rMax (row = sector); buildNetChannel reads them back bilinearly. */
class Coarse {
  /** One array a field. */
  readonly f: Float32Array[];
  readonly dR: number;
  readonly dPhi: number;
  /**
   * `fn` writes the fields at a place into its last argument. `cell` kpc: a ring's azimuthal samples are taken every
   * `stride` sectors where that keeps them under it (by default half the radial cell).
   */
  constructor(
    readonly rings: number,
    readonly sectors: number,
    readonly rMax: number,
    fields: number,
    fn: (x: number, y: number, r: number, phi: number, out: Float32Array) => void,
    cell = 0,
  ) {
    this.f = Array.from({ length: fields }, () => new Float32Array(rings * sectors));
    this.dR = rMax / rings;
    this.dPhi = TAU / sectors;
    const cos = new Float64Array(sectors);
    const sin = new Float64Array(sectors);
    for (let j = 0; j < sectors; j += 1) {
      cos[j] = Math.cos((j + 0.5) * this.dPhi);
      sin[j] = Math.sin((j + 0.5) * this.dPhi);
    }
    const most = cell > 0 ? cell : 0.5 * this.dR;
    const tmp = new Float32Array(fields);
    for (let i = 0; i < rings; i += 1) {
      const r = (i + 0.5) * this.dR;
      // A ring whose azimuthal cell is well under the one asked is sampled every `stride` sectors (a power of two that
      // divides the sectors, or 1) and filled linearly between: the inner disc costs no more than the outer.
      let stride = 1;
      while (stride < 64 && sectors % (2 * stride) === 0 && r * this.dPhi * 2 * stride <= most) stride *= 2;
      for (let j = 0; j < sectors; j += stride) {
        fn(r * cos[j], r * sin[j], r, (j + 0.5) * this.dPhi, tmp);
        for (let k = 0; k < fields; k += 1) this.f[k][j * rings + i] = tmp[k];
      }
      if (stride === 1) continue;
      for (const v of this.f) {
        for (let j = 0; j < sectors; j += stride) {
          const a = v[j * rings + i];
          const b = v[((j + stride) % sectors) * rings + i];
          for (let k = 1; k < stride; k += 1) v[(j + k) * rings + i] = a + ((b - a) * k) / stride;
        }
      }
    }
  }

  /** The first `n` fields read bilinearly at (r, phi), phi in [0, 2 pi), into `out`. */
  read(r: number, phi: number, out: Float32Array, n = this.f.length): void {
    const a = Math.min(this.rings - 1.0001, Math.max(0, r / this.dR - 0.5));
    const i = Math.floor(a);
    const w = a - i;
    const u = phi / this.dPhi - 0.5;
    const j = Math.floor(u);
    const b = u - j;
    const j0 = ((j % this.sectors) + this.sectors) % this.sectors;
    const j1 = (j0 + 1) % this.sectors;
    const r0 = j0 * this.rings + i;
    const r1 = j1 * this.rings + i;
    const w00 = (1 - b) * (1 - w);
    const w01 = (1 - b) * w;
    const w10 = b * (1 - w);
    const w11 = b * w;
    for (let k = 0; k < n; k += 1) {
      const v = this.f[k];
      out[k] = w00 * v[r0] + w01 * v[r0 + 1] + w10 * v[r1] + w11 * v[r1 + 1];
    }
  }
}

/**
 * The coarse grids' cells over the map's, (radial, azimuthal): the dust's (full radial resolution - a thread runs
 * mostly along the azimuth, so it is thin across the rings and long across the sectors) and the light's.
 */
export const NET_GRID = { dustR: 1, dustPhi: 4, amount: 6, light: 4 } as const;

/** Where no light is drawn: the clouds' neutral (q = 0.3, which changes nothing). */
const NONE = 128 - Math.round(127 * 0.3);

/**
 * The floc channel in the plane style: flocMap.ts's encoding, `rings` bytes to a row over 0-rHi and `sectors` rows. The
 * dust is evaluated at every ring and every third sector (at most `dustCell` apart along a ring), the light on a grid
 * four times the map's cells, each read back bilinearly; then the groups' glow is painted.
 */
export function buildNetChannel(g: FlocGeometry, shape: FlocShape, rings: number = FLOC_MAP.rings, sectors: number = FLOC_MAP.sectors): Uint8Array {
  const net = netSampler(g, shape);
  const out = new Uint8Array(rings * sectors).fill(NONE);
  const dR = g.rHi / rings;
  const dPhi = TAU / sectors;
  const lit = Math.min(rings, Math.ceil(net.reach / dR));
  // No threads drawn (netDepth 0): no dust grid at all (the mesh is drawn in the march). Then only the light, its reach
  // and the clouds' glow are read: floc.ts channelShapeOf keys the plane on those alone (S107 fix F2) - a new read of
  // the shape below, outside the dust grid, must be added to its LIGHT_ONLY_KEYS.
  const dusty = shape.netDepth > 0 ? Math.min(lit, Math.ceil(net.outer / dR)) : 0;
  const dSect = Math.max(8, Math.floor(sectors / NET_GRID.dustPhi));
  const lSect = Math.max(8, Math.floor(sectors / NET_GRID.light));
  // Along a ring the dust needs samples about a third of a thread's run across the sectors: a thread at the pitch
  // crosses the sectors over its width / sin(pitch).
  const pitch = Math.min(80, Math.max(1, g.pitchDeg * shape.pitch)) * DEG;
  const dustCell = Math.max(dR, (0.3 * Math.max(shape.width, 10) * 1e-3) / Math.sin(pitch));
  // The dust's amounts and feathering (smooth) on the light's grid, then the threads at every ring.
  const am: Amount = { a1: 0, a2: 0, fe: 1, aL: 0, aS: 0, p1: 1, p2: 1 };
  const nA = AMOUNT_KEYS.length;
  const amounts = new Coarse(Math.max(2, Math.ceil(dusty / NET_GRID.amount)), Math.max(8, Math.floor(sectors / NET_GRID.amount)), Math.max(dusty, 1) * dR, nA, (x, y, r, phi, o) => {
    net.amount(x, y, r, phi, am);
    for (let k = 0; k < nA; k += 1) o[k] = am[AMOUNT_KEYS[k]];
  });
  const amt = new Float32Array(nA);
  const read: Amount = { a1: 0, a2: 0, fe: 1, aL: 0, aS: 0, p1: 1, p2: 1 };
  const dust = new Coarse(Math.max(2, Math.ceil(dusty / NET_GRID.dustR)), dSect, Math.max(dusty, 1) * dR, 1, (x, y, r, phi, o) => {
    amounts.read(r, phi, amt);
    if (amt[0] <= 1e-4 && amt[1] <= 1e-4 && amt[3] <= 1e-4 && amt[4] <= 1e-4) {
      o[0] = 0;
      return;
    }
    for (let k = 0; k < nA; k += 1) read[AMOUNT_KEYS[k]] = amt[k];
    o[0] = net.threads(x, y, r, phi, read);
  }, dustCell);
  const light = new Coarse(Math.max(2, Math.ceil(lit / NET_GRID.light)), lSect, Math.max(lit, 1) * dR, 1, (x, y, _r, _phi, o) => {
    o[0] = net.light(x, y);
  });
  const ringOf = (grid: Coarse, n: number) => {
    const at = new Int32Array(n);
    const w = new Float32Array(n);
    for (let i = 0; i < n; i += 1) {
      const a = Math.min(grid.rings - 1.0001, Math.max(0, ((i + 0.5) * dR) / grid.dR - 0.5));
      at[i] = Math.floor(a);
      w[i] = a - at[i];
    }
    return { at, w };
  };
  const dRing = ringOf(dust, dusty);
  const lRing = ringOf(light, lit);
  const fadeOut = new Float32Array(lit);
  for (let i = 0; i < lit; i += 1) fadeOut[i] = 1 - smoothstep(0.85 * net.reach, net.reach, (i + 0.5) * dR);
  // The dust's byte by its depth, in a table (the square root was the encode's cost).
  const TABLE_N = 4096;
  const dustByte = new Uint8Array(TABLE_N + 1);
  for (let k = 0; k <= TABLE_N; k += 1) dustByte[k] = 128 + Math.round(127 * Math.sqrt(k / TABLE_N));
  const dScale = TABLE_N / FLOC_MAP.shapeMax;
  const dv = dust.f[0];
  const lv = light.f[0];
  const dN = dust.rings;
  const lN = light.rings;
  for (let j = 0; j < sectors; j += 1) {
    const phi = (j + 0.5) * dPhi;
    const ud = (phi / TAU) * dSect - 0.5;
    const ul = (phi / TAU) * lSect - 0.5;
    const dj = Math.floor(ud);
    const lj = Math.floor(ul);
    const db = ud - dj;
    const lb = ul - lj;
    const d0 = (((dj % dSect) + dSect) % dSect) * dN;
    const d1 = ((((dj + 1) % dSect) + dSect) % dSect) * dN;
    const l0 = (((lj % lSect) + lSect) % lSect) * lN;
    const l1 = ((((lj + 1) % lSect) + lSect) % lSect) * lN;
    const row = j * rings;
    for (let i = 0; i < lit; i += 1) {
      let v = 0;
      if (i < dusty) {
        const a = dRing.at[i];
        const w = dRing.w[i];
        v = (1 - db) * ((1 - w) * dv[d0 + a] + w * dv[d0 + a + 1]) + db * ((1 - w) * dv[d1 + a] + w * dv[d1 + a + 1]);
        if (v >= MARGIN) {
          const t = ((v - MARGIN) * dScale + 0.5) | 0;
          out[row + i] = dustByte[t < TABLE_N ? t : TABLE_N];
          continue;
        }
      }
      const edge = fadeOut[i];
      const a = lRing.at[i];
      const w = lRing.w[i];
      const lit0 = (1 - lb) * ((1 - w) * lv[l0 + a] + w * lv[l0 + a + 1]) + lb * ((1 - w) * lv[l1 + a] + w * lv[l1 + a + 1]);
      const q = 0.6 * (0.5 + (lit0 - 0.5) * edge) * (1 - Math.max(0, v) / MARGIN);
      const qb = (127 * q + 0.5) | 0;
      out[row + i] = 128 - (qb > 1 ? qb : 1);
    }
  }
  if (shape.cloudGlow > 0 && shape.cloudCount > 0) paintGlow(out, g, shape, rings, sectors);
  return out;
}

/**
 * A soft glow under each star cloud's group (flocClouds.ts): a gaussian twice the group's radius, its peak `cloudGlow`
 * times the group's brightest member's share of the range, into the light texels only - the clouds' level raised
 * toward its brightest, then into the clump level (floc.ts's clump glow and tint).
 */
function paintGlow(out: Uint8Array, g: FlocGeometry, shape: FlocShape, rings: number, sectors: number): void {
  const { groups } = buildClouds(g, shape);
  const dR = g.rHi / rings;
  const range = Math.log(Math.max(1.0001, shape.cloudRange));
  // S106 (C4): the glows summed (their largest) on a grid GLOW_K times coarser each way, then laid on every light
  // texel read bilinearly - the glow is smooth over a group's size, and painting it texel by texel cost a slider most
  // of its time.
  const K = GLOW_K;
  const cr = Math.ceil(rings / K);
  const cs = Math.max(8, Math.floor(sectors / K));
  const cR = (rings * dR) / cr;
  const cP = TAU / cs;
  const acc = new Float32Array(cr * cs);
  const EXP = new Float32Array(6001);
  for (let k = 0; k <= 6000; k += 1) EXP[k] = Math.exp(-k / 1000);
  const cosR = new Float64Array(cs);
  const sinR = new Float64Array(cs);
  for (let j = 0; j < cs; j += 1) {
    cosR[j] = Math.cos((j + 0.5) * cP);
    sinR[j] = Math.sin((j + 0.5) * cP);
  }
  let top = 0;
  for (const grp of groups) {
    const sig = 1.2 * grp.size + 0.02;
    const peak = shape.cloudGlow * (0.35 + 0.65 * Math.log(Math.max(1, grp.lead)) / range);
    if (peak <= 0.02) continue;
    const r0 = Math.hypot(grp.x, grp.y);
    let p0 = Math.atan2(grp.y, grp.x);
    if (p0 < 0) p0 += TAU;
    const ext = 2.4 * sig + cR;
    const iLo = Math.max(0, Math.floor((r0 - ext) / cR));
    const iHi = Math.min(cr - 1, Math.ceil((r0 + ext) / cR));
    top = Math.max(top, iHi + 1);
    const half = Math.min(cs / 2, Math.ceil(ext / Math.max(r0 - ext, 0.05) / cP));
    const jc = Math.floor(p0 / cP);
    const inv = 1 / (2 * sig * sig);
    for (let dj = -half; dj <= half; dj += 1) {
      const j = (((jc + dj) % cs) + cs) % cs;
      const c = cosR[j];
      const sn = sinR[j];
      const row = j * cr;
      for (let i = iLo; i <= iHi; i += 1) {
        const r = (i + 0.5) * cR;
        const ex = r * c - grp.x;
        const ey = r * sn - grp.y;
        const e = (ex * ex + ey * ey) * inv;
        if (e >= 6) continue;
        const gl = peak * EXP[(e * 1000) | 0];
        if (gl > acc[row + i]) acc[row + i] = gl;
      }
    }
  }
  const last = Math.min(rings, Math.ceil((top * cR) / dR));
  const at = new Int32Array(last);
  const w = new Float32Array(last);
  for (let i = 0; i < last; i += 1) {
    const a = Math.min(cr - 1.0001, Math.max(0, ((i + 0.5) * dR) / cR - 0.5));
    at[i] = Math.floor(a);
    w[i] = a - at[i];
  }
  for (let j = 0; j < sectors; j += 1) {
    const u = ((j + 0.5) / sectors) * cs - 0.5;
    const jj = Math.floor(u);
    const b = u - jj;
    const r0 = (((jj % cs) + cs) % cs) * cr;
    const r1 = ((((jj + 1) % cs) + cs) % cs) * cr;
    const row = j * rings;
    for (let i = 0; i < last; i += 1) {
      const a = at[i];
      const wi = w[i];
      const gl = (1 - b) * ((1 - wi) * acc[r0 + a] + wi * acc[r0 + a + 1]) + b * ((1 - wi) * acc[r1 + a] + wi * acc[r1 + a + 1]);
      if (gl < 0.004) continue;
      const by = out[row + i];
      if (by >= 128) continue;
      const q = (128 - by) / 127;
      let q2: number;
      if (q > 0.6) q2 = Math.max(q, 0.6 + 0.4 * Math.min(1, 2 * gl - 1));
      else if (gl < 0.5) q2 = q + (0.6 - q) * 2 * gl;
      else q2 = 0.6 + 0.4 * Math.min(1, 2 * gl - 1);
      out[row + i] = 128 - Math.max(1, Math.min(127, Math.round(127 * q2)));
    }
  }
}
