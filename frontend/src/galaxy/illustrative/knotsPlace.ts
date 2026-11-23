// The pink HII regions placed on the arm skeleton (S106, builder K; knots.ts's `place` = 1). DISPLAY-ONLY DRAWING OF
// THE LAYER'S OWN (the lead's ruling 12, COMMON.md): the model's HII regions lie at the model's own places, which are
// not on the drawn skeleton (skeleton.ts), so under `place` the regions are laid by the viewer itself, with a fixed seed,
// along the skeleton's ridges as the goal picture has them: in bunches strung along each ridge (a few close together,
// then a gap), biased to the ridge's inner edge (the dust lane's side), denser where the ridge is strong, with a steep
// size spread (many small, a few large complexes) and a bright complex at each bar end (the two major arms' starts).
// Each region is a small nebula of several overlapping lobes of slightly different pink-red hues, spread along the arm,
// with a small white-hot core and a few blue-white points beside it. Only the light's scale is the model's (the 90th
// percentile of its regions' own light, so the gain and the exposure move them as they move the knots); no published
// number, readout, tracer or preview changes. No three.js here: pure arithmetic, tested (knots.test.ts).

import { currentSkeleton, skeletonKey } from "./armsSkeleton";
import type { IllContext, IllParams } from "./feature";
import { CORE_COLOUR, MAX_BLOBS, hash01, quantile, radialWeight, regionColour } from "./knotsMath";
import { type Skeleton, armAt, patchAt, radiusAtTurn, sampleRidges } from "./skeleton";

const TAU = 2 * Math.PI;

/**
 * THE ONE READ OF THE SKELETON for the regions: the arm skeleton at the arms' LIVE parameters (armsSkeleton.ts
 * currentSkeleton, cached there) and the key that moves exactly when it does (the layer's memo key).
 */
export function regionsSkeleton(context: IllContext): { skeleton: Skeleton | null; key: string } {
  return { skeleton: currentSkeleton(context), key: skeletonKey(context) };
}

/** mulberry32: the placement's own fixed-seed stream. */
function stream(seed: number): () => number {
  let s = (seed * 0x9e3779b1) >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const gaussOf = (next: () => number): number => Math.sqrt(-2 * Math.log(Math.max(1e-12, next()))) * Math.cos(TAU * next());

/** One placed region (plane coordinates: x = R cos phi, y = R sin phi, kpc). */
export interface PlacedRegion {
  x: number;
  y: number;
  /** The arm's tangent in the plane (unit), outward along the arm. */
  tx: number;
  ty: number;
  /** Drawn radius, pc. */
  radius: number;
  /** Light relative to the model's reference (1: the 90th percentile of the model's regions). */
  light: number;
  /** 0 a nebula, 1 a blue-white point beside one, 2 (S107, MW2) a complex's soft pink halo (one wide lobe, no core). */
  kind: 0 | 1 | 2;
  /** A stable index for the lobes' hash. */
  id: number;
}

/** The arm's frame at radius R on an arm: the crest point, the tangent and the inner normal (plane, unit). */
function frameAt(sk: Skeleton, a: number, R: number): { x: number; y: number; tx: number; ty: number; nx: number; ny: number; strength: number; width: number } | null {
  const h = armAt(sk.arms[a], R);
  if (!h) return null;
  const c = Math.cos(h.phi);
  const s = Math.sin(h.phi);
  // In (e_R, e_phi): the tangent (tan p, sense), the inner normal (-1, sense tan p) - toward the centre, on the side
  // ridgeAt calls inner (+1).
  const norm = Math.sqrt(1 + h.tanp * h.tanp);
  const tR = h.tanp / norm;
  const tP = sk.sense / norm;
  const nR = -1 / norm;
  const nP = (sk.sense * h.tanp) / norm;
  return {
    x: R * c,
    y: R * s,
    tx: tR * c - tP * s,
    ty: tR * s + tP * c,
    nx: nR * c - nP * s,
    ny: nR * s + nP * c,
    strength: h.strength,
    width: sk.arms[a].width,
  };
}

/** A size from the steep (Pareto) spread: floor u^(-1/slope), clamped to the ceiling. */
export function paretoRadius(u: number, floor: number, ceiling: number, slope: number): number {
  const r = floor * Math.pow(Math.max(1e-9, u), -1 / Math.max(0.1, slope));
  return Math.min(Math.max(floor, ceiling), Math.max(floor, r));
}

/**
 * The regions laid on the skeleton at these parameters (knots.ts's controls): `total` regions in bunches of about
 * `bunch`, the bunches' centres along the crests (sampleRidges, weighted by strength^ridgePow and the radial fade),
 * no two within `gap` kpc; each member spread `bunchLen` kpc along the arm and set `inner` ridge widths to its inner
 * side, scattered `across` widths; sizes from paretoRadius over [sizeMin, sizeMax] at `slope`, light (r / sizeMin)^lightSize;
 * a complex at each major arm's start (the bar's ends) `barEnds` times as bright; `sparkle` blue-white points beside
 * each large region. Deterministic in (skeleton, parameters).
 *
 * S107 (the Milky Way's regions): no bunch where the ridge's strength is under `minStrength` (a faded arm end); a
 * bunch kept with the arm's clumps (skeleton.ts patchAt) to the power `patchPow`, so the regions gather in the arm's
 * bright stretches with long empty ones between; `complexes` large ragged complexes (as the bar ends' are, `complexGain`
 * times a region's light) at strength-weighted places along the two major arms. Each 0 leaves the S106 placement.
 */
export function placeOnSkeleton(sk: Skeleton, p: IllParams): PlacedRegion[] {
  const next = stream(Math.round(p.seed ?? 7));
  const total = Math.max(0, Math.round(p.total ?? 300));
  const bunch = Math.max(1, p.bunch ?? 4);
  const nBunch = Math.max(1, Math.round(total / bunch));
  const gap = Math.max(0, p.gap ?? 0.8);
  const bunchLen = Math.max(0, p.bunchLen ?? 0.3);
  const inner = p.inner ?? 0.35;
  const across = Math.max(0, p.across ?? 0.25);
  const floor = Math.max(1, p.sizeMin ?? 15);
  const ceiling = Math.max(floor, p.sizeMax ?? 200);
  const slope = p.slope ?? 1.4;
  const lightSize = p.lightSize ?? 1.2;
  const ridgePow = Math.max(0, p.ridgePow ?? 1.5);
  const fadeR = p.fadeR ?? 14;
  const fadeWidth = p.fadeWidth ?? 4;
  const innerR = p.innerR ?? 0;
  const minStrength = Math.max(0, p.minStrength ?? 0);
  const patchPow = Math.max(0, p.patchPow ?? 0);
  const out: PlacedRegion[] = [];
  const centres: number[] = [];
  let id = 0;
  const add = (f: NonNullable<ReturnType<typeof frameAt>>, along: number, off: number, radius: number, light: number) => {
    out.push({ x: f.x + along * f.tx + off * f.nx, y: f.y + along * f.ty + off * f.ny, tx: f.tx, ty: f.ty, radius, light, kind: 0, id: id++ });
  };
  // S107 (MW2): on a spur, the regions drawn toward its crest by `spurCrest` (0: the inner-edge bias and the scatter as
  // on an arm); a large complex's members `complexMembers` times as many and spread `complexSpread` times as far along
  // the arm, `satellites` tiny regions about it, and a soft pink halo (`halo` its light against the complex's largest
  // member, `haloSize` times the ceiling its radius). Each at its default leaves the placement as it was.
  const spurCrest = Math.min(1, Math.max(0, p.spurCrest ?? 0));
  const complexMembers = Math.max(0.1, p.complexMembers ?? 1);
  const complexSpread = Math.max(0, p.complexSpread ?? 1);
  const satellites = Math.max(0, Math.round(p.satellites ?? 0));
  const halo = Math.max(0, p.halo ?? 0);
  const haloSize = Math.max(0.5, p.haloSize ?? 3);
  const members = (f: NonNullable<ReturnType<typeof frameAt>>, count: number, scale: number, big: boolean, onCrest = 0) => {
    const spread = big ? complexSpread : 1;
    for (let m = 0; m < count; m++) {
      const along = (m === 0 && big ? 0 : gaussOf(next)) * bunchLen * spread;
      const off = (inner + across * gaussOf(next)) * f.width * (1 - onCrest);
      const u = next();
      const radius = big && m === 0 ? ceiling : paretoRadius(big ? 0.15 + 0.6 * u : u, floor, ceiling, slope);
      add(f, along, off, radius, scale * Math.pow(radius / floor, lightSize));
    }
  };
  /** A large complex: its members, then (MW2) its satellites and its halo. */
  const complex = (f: NonNullable<ReturnType<typeof frameAt>>, scale: number) => {
    members(f, Math.max(3, Math.round(bunch * 1.5 * complexMembers)), scale, true);
    const reach = bunchLen * Math.max(1, complexSpread);
    for (let s = 0; s < satellites; s++) {
      const along = (1.2 + 1.3 * next()) * reach * (next() < 0.5 ? -1 : 1);
      const off = (inner + (0.6 + 0.8 * next()) * (next() < 0.5 ? -1 : 1) * Math.max(0.3, across)) * f.width;
      add(f, along, off, floor * (1 + next()), 0.6 * scale);
    }
    if (halo > 0) {
      out.push({ x: f.x + inner * f.width * f.nx, y: f.y + inner * f.width * f.ny, tx: f.tx, ty: f.ty, radius: haloSize * ceiling, light: halo * scale * Math.pow(ceiling / floor, lightSize), kind: 2, id: id++ });
    }
  };
  // The bar's ends: the two major arms' starts.
  const barEnds = Math.max(0, p.barEnds ?? 3);
  if (barEnds > 0) {
    for (let a = 0; a < sk.arms.length && a < 2; a++) {
      if (sk.arms[a].kind !== "major") continue;
      // (S109: on a hugging major, a sixth of a radian along it - its radius grows too slowly there for r0 * 1.06.)
      const f = frameAt(sk, a, sk.arms[a].ray ? radiusAtTurn(sk.arms[a], sk.sense >= 0 ? 1 : -1, 0.16) : sk.arms[a].r0 * 1.06);
      if (!f) continue;
      complex(f, barEnds);
      centres.push(f.x, f.y);
    }
  }
  // S107: the large complexes along the major arms, each at a strength-weighted place no nearer another (or a bar end)
  // than 3 gaps and five of a complex's reaches (MW3: the satellites reach 2.5 of them either side - so two complexes
  // never run together into one long pink stretch, ordinary regions between them; 2 gaps before).
  const complexes = Math.max(0, Math.round(p.complexes ?? 0));
  if (complexes > 0) {
    const apart = 3 * gap + 5 * bunchLen * Math.max(1, complexSpread);
    const majors = sk.arms.map((a, k) => (a.kind === "major" ? k : -1)).filter((k) => k >= 0);
    let placed = 0;
    for (let t = 0; t < complexes * 60 && placed < complexes && majors.length; t++) {
      const a = majors[Math.floor(next() * majors.length) % majors.length];
      const arm = sk.arms[a];
      const R = Math.exp(arm.lnR0 + next() * (arm.n - 1) * arm.dlnR);
      const f = frameAt(sk, a, R);
      if (!f || f.strength < Math.max(minStrength, 0.3)) continue;
      if (next() > f.strength * patchAt(arm, R) * radialWeight(R, fadeR, fadeWidth, innerR)) continue;
      const g2 = apart * apart;
      let near = false;
      for (let j = 0; j < centres.length && !near; j += 2) near = (centres[j] - f.x) ** 2 + (centres[j + 1] - f.y) ** 2 < g2;
      if (near) continue;
      complex(f, Math.max(0, p.complexGain ?? 3));
      centres.push(f.x, f.y);
      placed++;
    }
  }
  // The bunches along the ridges.
  const cand = sampleRidges(sk, nBunch * 20, Math.round(p.seed ?? 7) * 7919 + 13, 0);
  const start = out.length;
  for (let k = 0; k < cand.radius.length && out.length - start < total; k++) {
    const R = cand.radius[k];
    const f = frameAt(sk, cand.arm[k], R);
    if (!f) continue;
    if (f.strength < minStrength) continue;
    const clumps = patchPow > 0 ? Math.pow(patchAt(sk.arms[cand.arm[k]], R), patchPow) : 1;
    const w = clumps * Math.pow(Math.max(0, f.strength), ridgePow) * radialWeight(R, fadeR, fadeWidth, innerR);
    if (next() > w) continue;
    // Each candidate's own reach (0.4-1.6 gap): the gaps uneven, not a necklace.
    const reach = gap * (0.4 + 1.2 * next());
    const g2 = reach * reach;
    let near = false;
    for (let j = 0; j < centres.length && !near; j += 2) {
      const dx = centres[j] - f.x;
      const dy = centres[j + 1] - f.y;
      near = dx * dx + dy * dy < g2;
    }
    if (near) continue;
    centres.push(f.x, f.y);
    // The bunch's size: 1 + an exponential of mean bunch - 1 (many small bunches and singles, a few large).
    const count = Math.min(Math.round(4 * bunch), 1 + Math.floor(-Math.log(Math.max(1e-9, next())) * (bunch - 1)));
    members(f, count, 1, false, sk.arms[cand.arm[k]].kind === "spur" ? spurCrest : 0);
  }
  // The blue-white points beside the larger regions.
  const sparkle = Math.max(0, Math.round(p.sparkle ?? 0));
  const sparkleGain = Math.max(0, p.sparkleGain ?? 0.2);
  if (sparkle > 0 && sparkleGain > 0) {
    const n = out.length;
    for (let i = 0; i < n; i++) {
      const r = out[i];
      if (r.kind === 2) continue;
      const k = Math.round(sparkle * Math.min(1, r.radius / (3 * floor)));
      for (let j = 0; j < k; j++) {
        const reach = (0.6 + 1.2 * next()) * (r.radius / 1000);
        const a = TAU * next();
        out.push({
          x: r.x + reach * Math.cos(a),
          y: r.y + reach * Math.sin(a),
          tx: r.tx,
          ty: r.ty,
          radius: Math.max(1, 0.12 * floor),
          light: sparkleGain * r.light * (0.4 + 0.6 * next()),
          kind: 1,
          id: id++,
        });
      }
    }
  }
  return out;
}

/**
 * A skeleton region's lobes: `count` Gaussians [along, across, sigma, weight] in units of the drawn radius (weights
 * summing to 1), the along offsets stretched by `elong` against the across ones; and each lobe's hue share in [0, 1]
 * (0 the redder colour, 1 the more magenta). A blue-white point: one round lobe.
 */
export function skeletonLobes(id: number, kind: 0 | 1 | 2, count: number, irregular: number, soft: number, elong: number): { blobs: number[][]; tint: number[] } {
  if (kind === 1) return { blobs: [[0, 0, 0.5, 1], [0, 0, 0.5, 0], [0, 0, 0.5, 0], [0, 0, 0.5, 0]], tint: [0, 0, 0, 0] };
  // MW2: a complex's halo, an envelope along the arm - four soft lobes in a row, the middle two the stronger.
  if (kind === 2) {
    const e = Math.sqrt(Math.max(1, elong));
    const j = (k: number) => 0.08 * (hash01(id, 70 + k) - 0.5);
    return { blobs: [[-0.55 * e, j(0), 0.32, 0.18], [-0.18 * e, j(1), 0.36, 0.32], [0.18 * e, j(2), 0.36, 0.32], [0.55 * e, j(3), 0.32, 0.18]], tint: [0.5, 0.5, 0.5, 0.5] };
  }
  const n = Math.max(1, Math.min(MAX_BLOBS, Math.round(count)));
  const e = Math.max(1, elong);
  const blobs: number[][] = [];
  const tint: number[] = [];
  let total = 0;
  for (let k = 0; k < MAX_BLOBS; k++) {
    if (k >= n) {
      blobs.push([0, 0, 0.5 * soft, 0]);
      tint.push(0);
      continue;
    }
    const a = TAU * hash01(id, 4 * k + 1);
    const reach = (k === 0 ? 0.2 : 0.45 + 0.55 * hash01(id, 4 * k + 2)) * irregular;
    const sigma = (k === 0 ? 0.5 : 0.22 + 0.3 * hash01(id, 4 * k + 3)) * soft;
    const w = k === 0 ? 1 : 0.3 + 0.7 * hash01(id, 4 * k + 4);
    blobs.push([reach * Math.cos(a) * Math.sqrt(e), (reach * Math.sin(a)) / Math.sqrt(e), sigma, w]);
    tint.push(hash01(id, 4 * k + 61));
    total += w;
  }
  for (const b of blobs) b[3] /= total;
  return { blobs, tint };
}

/**
 * The skeleton regions' attribute values (knotsLayer.ts's skeleton shader): scene positions (x, 0, -y), the two lobe
 * colours (light times the redder and the more magenta pink), the core (white to the knots' white-blue by `coreBlue`),
 * the radius (pc), the four lobes, their hues, the arm's scene tangent. `ref` the model's light scale.
 */
export function skeletonAttributes(regions: readonly PlacedRegion[], p: IllParams, ref: number) {
  const m = regions.length;
  const out = {
    positions: new Float32Array(3 * m),
    light: new Float32Array(3 * m),
    light2: new Float32Array(3 * m),
    core: new Float32Array(3 * m),
    radius: new Float32Array(m),
    dir: new Float32Array(3 * m),
    tint: new Float32Array(4 * m),
    blobs: Array.from({ length: MAX_BLOBS }, () => new Float32Array(4 * m)),
  };
  const pink = p.pink ?? 1;
  const magenta = p.magenta ?? 0;
  const hue = p.hue ?? 0.4;
  const white: [number, number, number] = [1, 1, 1];
  const c1 = regionColour(white, pink, magenta - hue / 2);
  const c2 = regionColour(white, pink, magenta + hue / 2);
  const blue = Math.min(1, Math.max(0, p.coreBlue ?? 1));
  const coreC = [0, 1, 2].map((k) => (1 - blue) + blue * CORE_COLOUR[k]);
  const share = p.coreShare ?? 0.9;
  // The sparkle's blue-white is the core's own colour.
  regions.forEach((r, k) => {
    out.positions[3 * k] = r.x;
    out.positions[3 * k + 2] = -r.y;
    out.dir[3 * k] = r.tx;
    out.dir[3 * k + 2] = -r.ty;
    const l = ref * r.light;
    for (let ch = 0; ch < 3; ch++) {
      if (r.kind === 1) {
        out.light[3 * k + ch] = l * CORE_COLOUR[ch];
        out.light2[3 * k + ch] = l * CORE_COLOUR[ch];
      } else {
        out.light[3 * k + ch] = l * c1[ch];
        out.light2[3 * k + ch] = l * c2[ch];
        out.core[3 * k + ch] = r.kind === 0 && hash01(r.id, 97) < share ? l * coreC[ch] : 0;
      }
    }
    out.radius[k] = r.radius;
    const { blobs, tint } = skeletonLobes(r.id, r.kind, p.blobs ?? 4, p.irregular ?? 1, p.soft ?? 1, p.elong ?? 1.8);
    blobs.forEach((b, j) => out.blobs[j].set(b, 4 * k));
    out.tint.set(tint, 4 * k);
  });
  return out;
}

/** The model's light scale: the 90th percentile of its regions' own light (mean over the channels). */
export function modelLightRef(flux: Float32Array): number {
  const n = Math.floor(flux.length / 3);
  const lum = new Float64Array(n);
  for (let i = 0; i < n; i++) lum[i] = (flux[3 * i] + flux[3 * i + 1] + flux[3 * i + 2]) / 3;
  return quantile(lum, 0.9);
}
