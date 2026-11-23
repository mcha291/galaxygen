// The arm skeleton (skeleton.ts) as the illustrative features read it (S106, builder B3): its controls from the arms'
// parameters (arms.ts's `skel*` sliders), its geometry from an /api/arrays frame (the arm pieces and the bar, as the
// lanes read them: lanesMap.ts geometryOf), and its planes of the shared map. Display-only drawing of the layer's own
// (the lead's ruling 12): see skeleton.ts's header.
//
// For the pink regions' builder: `skeletonMemo()` gives a cached builder; call it with the frame and the arms'
// parameters (live, or the template's defaults as lanes.ts does) and read the result with skeleton.ts ridgeAt
// (distance to the nearest ridge and its strength at (R, phi)) and sampleRidges (points along the ridges).

import type { IllFrame, IllParams } from "./feature";
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

/** The last band build's time, ms (a diagnostic). */
export const skeletonBuild = { ms: 0 };

/**
 * The arms' two planes of the shared map from the skeleton (arms.ts's GLSL reads them as it reads armsField.ts
 * armPlanes'): B round(255 sqrt(s)), s the band (skeleton.ts skeletonBand, its faint wing `wing`), A the band's ring
 * mean over meanMax; the tint flags all set (every ring is a ring of arms).
 */
export function skeletonPlanes(sk: Skeleton, width: number, height: number, rHi: number, wing: number, flagFloats: number): { share: Uint8Array; mean: Uint8Array; meanMax: number; flags: number[] } {
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
  const meanRow = new Uint8Array(width);
  for (let c = 0; c < width; c++) meanRow[c] = meanMax > 0 ? Math.round((255 * ringMean[c]) / meanMax) : 0;
  const mean = new Uint8Array(width * height);
  for (let r = 0; r < height; r++) mean.set(meanRow, r * width);
  skeletonBuild.ms = (typeof performance !== "undefined" ? performance.now() : 0) - t0;
  return { share, mean, meanMax, flags: new Array<number>(flagFloats).fill(65535) };
}
