// The star clouds (S106, builder C; second pass C3): tight groups of bright points over the flocculent disc's outer part,
// blue-white outside and cream inside, each a few to a few dozen points of mixed brightness about a brilliant centre,
// with a soft glow under the group (the map's clump level, flocNet.ts buildNetChannel paints it). Gathered where the
// network's light is bright and the dust thin (flocNet.ts's fields), richest in the sectors about `cloudAz`, confined
// inside the disc's edge (the reach, a little ragged). HST's NGC 4414 shows its outer disc as such patches.
// ILLUSTRATIVE, display-only, of the viewer's own (the lead's ruling 12): no published field places a star cloud. Pure
// and deterministic: the same geometry, shape and seed give the same points.

import { type FlocGeometry, type FlocShape, flocKey, flocRandom, noise2 } from "./flocMap";
import { netSampler } from "./flocNet";

/** The clouds' own shaping values (floc.ts's cloud* controls, read from the shape). */
export interface CloudShape {
  /** points in all. */
  count: number;
  /** pc: a group's typical gaussian radius (each between a third and three times it). */
  groupPc: number;
  /** members per group, mean. */
  members: number;
  /** x the network's outer radius: the clouds' reach (a little ragged); none beyond it. */
  reach: number;
  /** x the outer radius: where the clouds come in (half-way). */
  start: number;
  /** the brightness law's index (L ~ u^(-1/slope)). */
  slope: number;
  /** the brightest over the faintest. */
  range: number;
  /** 0-1: how far the clouds keep to the rich sectors. */
  rich: number;
  /** degrees: the galactocentric azimuth of the richest sector. */
  az: number;
  /** S106 third pass (C4): the share of groups that are large complexes (four times the members, two and a half times the size). */
  complex: number;
}

/** The clouds' shaping values in a network's shape. */
export const cloudsOf = (s: FlocShape): CloudShape => ({
  count: s.cloudCount,
  groupPc: s.cloudGroup,
  members: s.cloudMembers,
  reach: s.cloudReach,
  start: s.cloudStart,
  slope: s.cloudSlope,
  range: s.cloudRange,
  rich: s.cloudRich,
  az: s.cloudAz,
  complex: s.cloudComplex,
});

/** A group: its centre (kpc), its gaussian radius (kpc) and its brightest member's weight. */
export interface CloudGroup {
  x: number;
  y: number;
  size: number;
  lead: number;
}

export interface Clouds {
  x: Float32Array;
  y: Float32Array;
  /** Each point's brightness in units of the faintest. */
  weight: Float32Array;
  groups: CloudGroup[];
}

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));
const smoothstep = (e0: number, e1: number, v: number) => {
  const t = clamp01((v - e0) / (e1 - e0));
  return t * t * (3 - 2 * t);
};
const DEG = Math.PI / 180;

/** The clouds' density at (x, y), in [0, 1]: bright light, thin dust, the outer disc, the rich sectors, inside the edge. */
export function cloudDensity(g: FlocGeometry, shape: FlocShape, c: CloudShape): (x: number, y: number) => number {
  const net = netSampler(g, shape);
  const outer = net.outer;
  const reach = Math.min(g.rHi, Math.max(0.1, c.reach) * outer);
  const start = Math.max(0, c.start) * outer;
  const kEdge = flocKey(shape.seed, 13, 0, 1);
  const kSect = flocKey(shape.seed, 13, 0, 2);
  const az = c.az * DEG;
  return (x: number, y: number) => {
    const r = Math.hypot(x, y);
    // The edge: the reach pushed in and out a little by a noise at a kiloparsec and a half; nothing past it.
    const rim = reach * (1 + 0.08 * (2 * noise2(x / 1.5 + 5.1, y / 1.5 + 2.7, kEdge) - 1));
    const radial = (0.15 + 0.85 * smoothstep(0.4 * start, start, r)) * (1 - smoothstep(0.82 * rim, rim, r));
    if (radial <= 0) return 0;
    // The rich sectors: a broad lobe about `az`, broken by a noise in azimuth (two or three rich stretches).
    const phi = Math.atan2(y, x);
    const lobe = 0.5 + 0.5 * Math.cos(phi - az);
    const broken = noise2(2.2 * Math.cos(phi) + 9.1, 2.2 * Math.sin(phi) + 4.3, kSect);
    const sector = 1 - c.rich + c.rich * clamp01(1.6 * lobe * lobe * (0.4 + 1.2 * broken));
    const light = smoothstep(0.4, 0.75, net.light(x, y));
    if (light <= 0) return 0;
    const dust = r < outer ? clamp01(net.dust(x, y) / 0.8) : 0;
    return radial * sector * light * (1 - 0.8 * dust);
  };
}

/** The brightness law: 1 to `range`, many faint, few bright. */
const brightness = (u: number, slope: number, range: number) => Math.min(range, (1 - u) ** (-1 / Math.max(0.1, slope)));

/** The points: groups placed against the density, members in a gaussian about each, brightest at the centre. */
export function buildClouds(g: FlocGeometry, shape: FlocShape, c: CloudShape = cloudsOf(shape), thin?: (r: number) => number): Clouds {
  const total = Math.max(0, Math.floor(c.count));
  const x = new Float32Array(total);
  const y = new Float32Array(total);
  const weight = new Float32Array(total);
  const groups: CloudGroup[] = [];
  if (total === 0) return { x, y, weight, groups };
  const density = cloudDensity(g, shape, c);
  const reach = Math.min(g.rHi, 1.1 * Math.max(0.1, c.reach) * Math.max(0.1, Math.min(shape.outerRadius, g.rHi)));
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
    // S109 (B2): `thin` (in [0, 1] by radius) takes clouds away where the disc's own light is dimmed: no clump left
    // floating alone on the dark outskirts. Absent, the clouds as drawn (the same draws, the same points).
    if (u() >= density(cx, cy) * (thin ? thin(r) : 1)) continue;
    // Members: a few to a few dozen (a log-uniform spread about the mean); the group's size spread several-fold.
    // S106 (C4): a share of the groups are large complexes - many more members over a wider glow.
    const big = c.complex > 0 && u() < c.complex ? 1 : 0;
    const m = Math.max(2, Math.round(c.members * Math.exp(1.6 * (2 * u() - 1)) * (big ? 4 : 1)));
    const lead = brightness(u(), c.slope, c.range);
    const size = sigma * Math.exp(1.1 * (2 * u() - 1)) * Math.sqrt(m / Math.max(1, c.members)) * (big ? 1.25 : 1);
    groups.push({ x: cx, y: cy, size, lead });
    for (let q = 0; q < m && k < total; q += 1, k += 1) {
      const a = Math.sqrt(-2 * Math.log(Math.max(1e-12, u())));
      const b = 2 * Math.PI * u();
      x[k] = cx + (q === 0 ? 0 : a * Math.cos(b) * size);
      y[k] = cy + (q === 0 ? 0 : a * Math.sin(b) * size);
      weight[k] = q === 0 ? lead : Math.min(lead, brightness(u(), c.slope, c.range));
    }
  }
  return { x: x.subarray(0, k), y: y.subarray(0, k), weight: weight.subarray(0, k), groups };
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
