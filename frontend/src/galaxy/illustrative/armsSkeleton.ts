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
  };
}

/** Whether the arms' marks read the skeleton (the `skeleton` switch). */
export const skeletonOn = (p: IllParams): boolean => (p.skeleton ?? 0) >= 0.5;

/** A cached skeleton builder (one per reader, so two readers at different parameters do not evict each other). */
export function skeletonMemo(): (frame: IllFrame | null, p: IllParams) => Skeleton | null {
  const build = memoOn((frame: unknown, json: unknown) => {
    const f = frame as IllFrame | null;
    if (!f) return null;
    const g = geometryOf(f);
    if (g.pieces.length === 0 && !g.bar) return null;
    return buildSkeleton({ pieces: g.pieces, bar: g.bar }, JSON.parse(json as string) as SkeletonParams);
  });
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
  const band = skeletonBand(sk, width, height, rHi, wing);
  const ringMean = new Float64Array(width);
  for (let r = 0; r < height; r++) {
    const row = r * width;
    for (let c = 0; c < width; c++) ringMean[c] += band[row + c];
  }
  let meanMax = 0;
  for (let c = 0; c < width; c++) {
    ringMean[c] /= height;
    meanMax = Math.max(meanMax, ringMean[c]);
  }
  const share = new Uint8Array(width * height);
  for (let i = 0; i < band.length; i++) share[i] = Math.round(255 * Math.sqrt(Math.min(1, band[i])));
  const samples: number[] = [];
  for (let k = 0; k < SKEL_MEAN_SAMPLES; k++) {
    const c = Math.min(width - 1, Math.max(0, Math.round(((k + 0.5) / SKEL_MEAN_SAMPLES) * width - 0.5)));
    samples.push(ringMean[c]);
  }
  const mean = new Uint8Array(width * height);
  if (contrast) {
    const { n, nR, nPhi: P } = contrast;
    const i0s = new Int32Array(width);
    const i1s = new Int32Array(width);
    const fxs = new Float64Array(width);
    for (let c = 0; c < width; c++) {
      const x = ((c + 0.5) / width) * nR - 0.5;
      const i0 = Math.floor(x);
      fxs[c] = x - i0;
      i0s[c] = Math.min(nR - 1, Math.max(0, i0));
      i1s[c] = Math.min(nR - 1, Math.max(0, i0 + 1));
    }
    for (let r = 0; r < height; r++) {
      const y = ((r + 0.5) / height) * P - 0.5;
      const jf = Math.floor(y);
      const fy = y - jf;
      const j0 = ((jf % P) + P) % P;
      const j1 = (j0 + 1) % P;
      const row = r * width;
      for (let c = 0; c < width; c++) {
        const a = i0s[c] * P;
        const b = i1s[c] * P;
        const fx = fxs[c];
        const v0 = n[a + j0] * (1 - fx) + n[b + j0] * fx;
        const v1 = n[a + j1] * (1 - fx) + n[b + j1] * fx;
        mean[row + c] = Math.round(255 * Math.min(1, Math.max(0, (v0 * (1 - fy) + v1 * fy) / SKEL_CONTRAST_MAX)));
      }
    }
  } else mean.fill(Math.round(255 / SKEL_CONTRAST_MAX));
  skeletonBuild.ms = (typeof performance !== "undefined" ? performance.now() : 0) - t0;
  return { share, mean, meanMax, flags: new Array<number>(flagFloats).fill(65535), ringMean: samples };
}
