// The star clouds (S106, builder C): loose groups of small bright points over the flocculent disc, blue-white outside
// and cream inside, gathered where the network's light is bright and the dust is thin (flocNet.ts's fields), densest in
// the outer disc and ragged at its edge - HST's NGC 4414 shows its outer disc as such clouds, its inner disc's light
// clumped the same way. ILLUSTRATIVE, display-only, of the viewer's own (the lead's ruling 12): no published field
// places a star cloud. Pure and deterministic: the same geometry, shape and seed give the same points.

import { type FlocGeometry, type FlocShape, flocKey, flocRandom, noise2 } from "./flocMap";
import { netSampler } from "./flocNet";

/** The clouds' own shaping values (floc.ts's cloud* controls). */
export interface CloudShape {
  /** points in all. */
  count: number;
  /** pc: a group's gaussian radius. */
  groupPc: number;
  /** members per group, mean. */
  members: number;
  /** x the network's outer radius: the clouds' reach (ragged). */
  reach: number;
  /** x the outer radius: where the clouds come in (half-way). */
  start: number;
  /** the brightness law's index (L ~ u^(-1/slope)). */
  slope: number;
  /** the brightest over the faintest. */
  range: number;
}

export interface Clouds {
  x: Float32Array;
  y: Float32Array;
  /** Each point's brightness in units of the faintest. */
  weight: Float32Array;
}

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));
const smoothstep = (e0: number, e1: number, v: number) => {
  const t = clamp01((v - e0) / (e1 - e0));
  return t * t * (3 - 2 * t);
};

/** The clouds' density at (x, y), in [0, 1]: bright light, thin dust, the outer disc, a ragged edge. */
export function cloudDensity(g: FlocGeometry, shape: FlocShape, c: CloudShape): (x: number, y: number) => number {
  const net = netSampler(g, shape);
  const outer = net.outer;
  const reach = Math.min(g.rHi, Math.max(0.1, c.reach) * outer);
  const start = Math.max(0, c.start) * outer;
  const kEdge = flocKey(shape.seed, 13, 0, 1);
  return (x: number, y: number) => {
    const r = Math.hypot(x, y);
    // The edge: the reach pushed in and out by a noise at a kiloparsec and a half, so the disc's rim is ragged.
    const rim = reach * (1 + 0.28 * (2 * noise2(x / 1.5 + 5.1, y / 1.5 + 2.7, kEdge) - 1));
    const radial = (0.25 + 0.75 * smoothstep(0.4 * start, start, r)) * (1 - smoothstep(0.75 * rim, rim, r));
    if (radial <= 0) return 0;
    const light = smoothstep(0.42, 0.8, net.light(x, y));
    if (light <= 0) return 0;
    const dust = r < outer ? clamp01(net.dust(x, y) / 0.8) : 0;
    return radial * light * (1 - dust);
  };
}

/** The brightness law: 1 to `range`, many faint, few bright. */
const brightness = (u: number, slope: number, range: number) => Math.min(range, (1 - u) ** (-1 / Math.max(0.1, slope)));

/** The points: groups placed against the density, members in a gaussian about each, brightest at the centre. */
export function buildClouds(g: FlocGeometry, shape: FlocShape, c: CloudShape): Clouds {
  const total = Math.max(0, Math.floor(c.count));
  const x = new Float32Array(total);
  const y = new Float32Array(total);
  const weight = new Float32Array(total);
  if (total === 0) return { x, y, weight };
  const density = cloudDensity(g, shape, c);
  const reach = Math.min(g.rHi, 1.3 * Math.max(0.1, c.reach) * Math.max(0.1, Math.min(shape.outerRadius, g.rHi)));
  const key = flocKey(shape.seed, 14, 0, 1);
  const sigma = c.groupPc * 1e-3;
  let k = 0;
  let draw = 0;
  const u = () => flocRandom(key, draw++);
  for (let tries = 0; k < total && tries < 40 * total; tries += 1) {
    const r = reach * Math.sqrt(u());
    const phi = 2 * Math.PI * u();
    const cx = r * Math.cos(phi);
    const cy = r * Math.sin(phi);
    if (u() >= density(cx, cy)) continue;
    const m = Math.max(1, Math.round(-Math.log(Math.max(1e-9, u())) * c.members));
    const lead = brightness(u(), c.slope, c.range);
    const size = sigma * (0.5 + u());
    for (let q = 0; q < m && k < total; q += 1, k += 1) {
      const a = Math.sqrt(-2 * Math.log(Math.max(1e-12, u())));
      const b = 2 * Math.PI * u();
      x[k] = cx + (q === 0 ? 0 : a * Math.cos(b) * size);
      y[k] = cy + (q === 0 ? 0 : a * Math.sin(b) * size);
      weight[k] = q === 0 ? lead : Math.min(lead, brightness(u(), c.slope, c.range));
    }
  }
  return { x: x.subarray(0, k), y: y.subarray(0, k), weight: weight.subarray(0, k) };
}

/**
 * Each point's light per channel: its weight times the base, in cream inside `warmR` kpc going to blue-white by
 * twice it (the share `blue` of the way), three floats a point.
 */
export function cloudFlux(c: Clouds, base: number, blue: number, warmR: number): Float32Array {
  const out = new Float32Array(c.weight.length * 3);
  const CREAM = [1.12, 1.0, 0.8];
  const BLUE = [0.78, 0.97, 1.3];
  for (let i = 0; i < c.weight.length; i += 1) {
    const t = smoothstep(0.6 * warmR, 1.6 * warmR, Math.hypot(c.x[i], c.y[i])) * blue;
    for (let ch = 0; ch < 3; ch += 1) out[3 * i + ch] = c.weight[i] * base * (CREAM[ch] + (BLUE[ch] - CREAM[ch]) * t);
  }
  return out;
}
