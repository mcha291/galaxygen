// The arm skeleton (skeleton.ts) as the illustrative features read it (S106, builder B3): its controls from the arms'
// parameters (arms.ts's `skel*` sliders), its geometry from an /api/arrays frame (the arm pieces and the bar, as the
// lanes read them: lanesMap.ts geometryOf), and its planes of the shared map. Display-only drawing of the layer's own
// (the lead's ruling 12): see skeleton.ts's header.
//
// For the pink regions' builder: `skeletonMemo()` gives a cached builder; call it with the frame and the arms'
// parameters (live, or the template's defaults as lanes.ts does) and read the result with skeleton.ts ridgeAt
// (distance to the nearest ridge and its strength at (R, phi)) and sampleRidges (points along the ridges).

import type { IllContext, IllFrame, IllParams } from "./feature";
import { memoOn } from "./feature";
import { geometryOf } from "./lanesMap";
import { SKELETON_DEFAULTS, type Skeleton, type SkeletonParams, buildSkeleton, skeletonBand } from "./skeleton";

/** The skeleton's controls from the arms' parameters (skeleton.ts SKELETON_DEFAULTS where one is absent). */
export function skeletonParamsOf(p: IllParams): SkeletonParams {
  const d = SKELETON_DEFAULTS;
  return {
    lesser: p.skellesser ?? d.lesser,
    spurs: p.skelspurs ?? d.spurs,
    pitchScale: p.skelpitch ?? d.pitchScale,
    drift: p.skeldrift ?? d.drift,
    kink: p.skelkink ?? d.kink,
    width: p.skelwidth ?? d.width,
    outer: p.skelouter ?? d.outer,
    fade: p.skelfade ?? d.fade,
    start: p.skelstart ?? d.start,
    lesserStart: p.skellesserstart ?? d.lesserStart,
    lesserLevel: p.skellevel ?? d.lesserLevel,
    seed: p.skelseed ?? d.seed,
    // S107 (the Milky Way's spiral and its patchy arms)
    pitchGrow: p.skelpitchgrow ?? d.pitchGrow,
    open: p.skelopen ?? d.open,
    lesserWidth: p.skellesserwidth ?? d.lesserWidth,
    lesserReach: p.skellesserreach ?? d.lesserReach,
    patch: p.skelpatch ?? d.patch,
    patchScale: p.skelpatchsize ?? d.patchScale,
    ragged: p.skelragged ?? d.ragged,
    // S107, MW2 (the even winding)
    nudge: p.skelnudge ?? d.nudge,
    even: p.skeleven ?? d.even,
    // S108 (J2): the pitch floor for a rerolled galaxy's near-circular pieces, as a slider.
    pitchMin: p.skelpitchmin ?? d.pitchMin,
  };
}

/** Whether the arms' marks read the skeleton (the `skeleton` switch). */
export const skeletonOn = (p: IllParams): boolean => (p.skeleton ?? 0) >= 0.5;

/**
 * A cached skeleton builder (one per reader, so two readers at different parameters do not evict each other); `name`
 * (S107) lets the map worker build it (feature.ts memoOn).
 */
export function skeletonMemo(name?: string): (frame: IllFrame | null, p: IllParams) => Skeleton | null {
  const build = memoOn((frame: unknown, json: unknown) => {
    const f = frame as IllFrame | null;
    if (!f) return null;
    const g = geometryOf(f);
    if (g.pieces.length === 0 && !g.bar) return null;
    return buildSkeleton({ pieces: g.pieces, bar: g.bar }, JSON.parse(json as string) as SkeletonParams);
  }, name);
  return (frame, p) => build(frame, JSON.stringify(skeletonParamsOf(p)));
}

const currentMemo = skeletonMemo();

/**
 * The arm skeleton as the arms draw it NOW (S106, B4): built from the frame and the arms' CURRENT parameters
 * (context.paramsOf("arms"), their live skel* sliders; skeleton.ts SKELETON_DEFAULTS where the context carries no
 * accessor), cached; null until the arrays have arrived or for a galaxy with no arm pieces and no bar. Built whatever
 * the arms' own `skeleton` switch says (read skeletonOn(context.paramsOf("arms")) for that). For any feature that places
 * things on the arms (the lanes, the pink regions): a value it shapes a plane from belongs in that plane's memo keys -
 * skeletonKey(context) gives one string that moves exactly when this skeleton does.
 */
export function currentSkeleton(context: IllContext): Skeleton | null {
  return currentMemo(context.frame, context.paramsOf?.("arms") ?? {});
}

/** A string that changes exactly when currentSkeleton(context)'s parameters do (a memo key; the frame is the other). */
export const skeletonKey = (context: IllContext): string => JSON.stringify(skeletonParamsOf(context.paramsOf?.("arms") ?? {}));

/** The last band build's time, ms (a diagnostic). */
export const skeletonBuild = { ms: 0 };

/** The skeleton's ring means are handed to the GLSL as this many samples over [0, rHi] (illArmsSkelMean). */
export const SKEL_MEAN_SAMPLES = 64;
/** The model's contrast is carried in A as byte round(255 min(1, n / SKEL_CONTRAST_MAX)). */
export const SKEL_CONTRAST_MAX = 2.5;

/** The dither's tile, texels (a fixed hash over a DITHER x DITHER tile, repeated). */
const DITHER = 64;

/** A fixed dither in [-0.5, 0.5) for the byte at column c, row r (an integer hash: the same on every machine). */
export function ditherAt(c: number, r: number): number {
  let h = (Math.imul(c | 0, 0x27d4eb2d) ^ Math.imul(r | 0, 0x165667b1) ^ 0x2f1d) >>> 0;
  h = Math.imul(h ^ (h >>> 15), 0x2c1b3c6d) >>> 0;
  h = (h ^ (h >>> 13)) >>> 0;
  return h / 4294967296 - 0.5;
}

/**
 * The arms' two planes of the shared map from the skeleton (S106, B3; arms.ts's GLSL reads them under illArmsSkel):
 *   B  round(255 sqrt(s)), s the band (skeleton.ts skeletonBand, its faint wing `wing`), as armPlanes' B;
 *   A  the model's own star contrast n (pattern_density_contrast over its ring mean, `contrast` on the arms' grid,
 *      bilinear, clamped in R, wrapped in phi) as round(255 min(1, n / SKEL_CONTRAST_MAX)) - so the GLSL can divide
 *      the model's own arm light out (arms.skelflat) and the skeleton's arms are the only ones drawn;
 * the band's ring means as SKEL_MEAN_SAMPLES samples (the ring's light kept, as armPlanes' A does), their largest,
 * and the tint flags all set (every ring is a ring of arms).
 */
export function skeletonPlanes(
  sk: Skeleton,
  width: number,
  height: number,
  rHi: number,
  wing: number,
  flagFloats: number,
  contrast: { n: Float64Array; nR: number; nPhi: number } | null = null,
): { share: Uint8Array; mean: Uint8Array; meanMax: number; flags: number[]; ringMean: number[] } {
  const t0 = typeof performance !== "undefined" ? performance.now() : 0;
  // S107: with clumped arms the ring means are the unclumped band's (skeletonBand's `plainMean`).
  const plain = sk.arms.some((a) => a.patch) ? new Float64Array(width) : null;
  const band = skeletonBand(sk, width, height, rHi, wing, plain);
  let ringMean: Float64Array;
  if (plain) ringMean = plain;
  else {
    ringMean = new Float64Array(width);
    for (let r = 0; r < height; r++) {
      const row = r * width;
      for (let c = 0; c < width; c++) ringMean[c] += band[row + c];
    }
    for (let c = 0; c < width; c++) ringMean[c] /= height;
  }
  let meanMax = 0;
  for (let c = 0; c < width; c++) meanMax = Math.max(meanMax, ringMean[c]);
  const share = new Uint8Array(width * height);
  for (let i = 0; i < band.length; i++) share[i] = Math.round(255 * Math.sqrt(Math.min(1, band[i])));
  const samples: number[] = [];
  for (let k = 0; k < SKEL_MEAN_SAMPLES; k++) {
    const c = Math.min(width - 1, Math.max(0, Math.round(((k + 0.5) / SKEL_MEAN_SAMPLES) * width - 0.5)));
    samples.push(ringMean[c]);
  }
  const mean = contrast ? contrastPlane(contrast, width, height) : new Uint8Array(width * height).fill(Math.round(255 / SKEL_CONTRAST_MAX));

  skeletonBuild.ms = (typeof performance !== "undefined" ? performance.now() : 0) - t0;
  return { share, mean, meanMax, flags: new Array<number>(flagFloats).fill(65535), ringMean: samples };
}

/**
 * The model's own star contrast n (pattern_density_contrast over its ring mean, on the arms' grid) as a plane of the
 * shared map: round(255 min(1, n / SKEL_CONTRAST_MAX)) per texel, read across rings by a Catmull-Rom cubic and along
 * phi linearly (wrapped), each byte dithered by a fixed hash. S106 (B5, the ring banding): a linear read kinks at every
 * model ring, and a kink in a smooth gradient shows as a thin arc; a rounded smooth field steps by 1/255 along its
 * contours - thin arcs again once the light is divided by it. (Factored out of skeletonPlanes in S107 so the arms'
 * `flat` can divide the model's arm light out without the skeleton; the bytes are the same.)
 */
export function contrastPlane(contrast: { n: ArrayLike<number>; nR: number; nPhi: number }, width: number, height: number): Uint8Array {
  const mean = new Uint8Array(width * height);
  const { n, nR, nPhi: P } = contrast;
  // Each of the contrast's P azimuth rows resampled across rings once (width columns, the cubic), in units of bytes.
  const cols = new Float32Array(P * width);
  for (let c = 0; c < width; c++) {
    const x = ((c + 0.5) / width) * nR - 0.5;
    const i0 = Math.floor(x);
    const t = x - i0;
    const t2 = t * t;
    const t3 = t2 * t;
    const w = [0.5 * (-t3 + 2 * t2 - t), 0.5 * (3 * t3 - 5 * t2 + 2), 0.5 * (-3 * t3 + 4 * t2 + t), 0.5 * (t3 - t2)];
    const a = [0, 1, 2, 3].map((k) => Math.min(nR - 1, Math.max(0, i0 - 1 + k)) * P);
    for (let j = 0; j < P; j++) cols[j * width + c] = (255 / SKEL_CONTRAST_MAX) * (w[0] * n[a[0] + j] + w[1] * n[a[1] + j] + w[2] * n[a[2] + j] + w[3] * n[a[3] + j]);
  }
  const dither = new Float32Array(DITHER * DITHER);
  for (let y = 0; y < DITHER; y++) for (let x = 0; x < DITHER; x++) dither[y * DITHER + x] = ditherAt(x, y);
  for (let r = 0; r < height; r++) {
    const y = ((r + 0.5) / height) * P - 0.5;
    const jf = Math.floor(y);
    const fy = y - jf;
    const j0 = ((jf % P) + P) % P;
    const j1 = (j0 + 1) % P;
    const row = r * width;
    const o0 = j0 * width;
    const o1 = j1 * width;
    const drow = (r % DITHER) * DITHER;
    for (let c = 0; c < width; c++) {
      const v = cols[o0 + c] * (1 - fy) + cols[o1 + c] * fy;
      mean[row + c] = Math.round(Math.min(255, Math.max(0, v)) + dither[drow + (c % DITHER)]);
    }
  }
  return mean;
}

/** A per-ring profile (nR rings over [0, rHi], ring centres) as SKEL_MEAN_SAMPLES samples, linear between centres. */
export function meanSamples(ringMean: ArrayLike<number>, nR: number): number[] {
  const out: number[] = [];
  for (let k = 0; k < SKEL_MEAN_SAMPLES; k++) {
    const x = ((k + 0.5) / SKEL_MEAN_SAMPLES) * nR - 0.5;
    const i0 = Math.floor(x);
    const f = x - i0;
    const a = ringMean[Math.min(nR - 1, Math.max(0, i0))];
    const b = ringMean[Math.min(nR - 1, Math.max(0, i0 + 1))];
    out.push(a * (1 - f) + b * f);
  }
  return out;
}
