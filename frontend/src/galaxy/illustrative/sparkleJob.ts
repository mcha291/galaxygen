// The arms' sparkle's points as a pure job (S107, the sliders' stall): what SparkleLayer.tsx built in its useMemo, moved
// here unchanged so the map worker (illMap.worker.ts) can build it off the main thread and the layer can build it on
// the main thread where there is no worker (vitest, a failed worker) - the same calls in the same order, so the points
// are the same bits either way. No React, no three.js.

import { toScene } from "../positions";
import { armMapFor, armsSkeleton, barOf, shapeOf } from "./arms";
import { skeletonOn, skeletonParamsOf } from "./armsSkeleton";
import { buildSparkle, hashString } from "./armsSparkle";
import { ILL_MAP, type IllFrame, type IllParams } from "./feature";
import { grainDensity, ridgeAt } from "./skeleton";

/** The seed of the viewer's own (and the template's name): fixed, never the time or the frame. */
const SPARKLE_SEED = 0x5108a2b5;

/** The sparkle's shaping values from the arms' parameters (SparkleLayer's own object, key for key). */
export function sparkleShape(params: IllParams) {
  return {
    count: params.sparkle ?? 0,
    clump: params.clump ?? 0.6,
    groupPc: params.groupsize ?? 120,
    members: params.members ?? 10,
    ridge: params.sparkleridge ?? 2,
    slope: params.sparkleslope ?? 1.4,
    range: params.sparklerange ?? 40,
    rMax: params.sparkleedge ?? 16,
    heightPc: 60,
    floor: params.sparklefloor ?? 0,
    lift: params.sparklelift ?? 0,
    avoid: params.sparkleavoid ?? 0,
    bunch: params.sparklebunch ?? 0,
    bunchPc: params.sparklebunchsize ?? 400,
    bunchBright: params.sparklebunchbright ?? 0,
    // S107 (MW2): the places drawn through the density's envelope (armsSparkle.ts envelopePlace).
    direct: (params.sparkledirect ?? 0) >= 0.5,
  };
}

/** Whether the sparkle reads the lanes (the shared map's R) at these parameters: only while it keeps off them. */
export const sparkleReadsLanes = (params: IllParams): boolean => (sparkleShape(params).avoid ?? 0) > 0;

/** The points as the layer draws them: scene positions, each point's weight and its radius (kpc). */
export interface SparklePoints {
  positions: Float32Array;
  weight: Float32Array;
  radius: Float32Array;
}

/**
 * The sparkle's points for the arms' parameters on this frame: `lanes` the shared map's RGBA bytes as the layer reads
 * them (its R the lanes; ILL_MAP's size) or null where the sparkle does not read them or the map is not composed.
 * Null where nothing is drawn.
 */
export function sparklePoints(params: IllParams, frame: IllFrame | null, template: string | null, lanes: ArrayLike<number> | null): SparklePoints | null {
  const built = armMapFor(params, frame);
  const shape = sparkleShape(params);
  // S106: on the skeleton, the grain's density read across its ridges (skeleton.ts grainDensity) in place of the share.
  const skeleton = skeletonOn(params) ? armsSkeleton(frame, params) : null;
  const tail = params.skeltail ?? 0.05;
  const grainFade = params.skelgrainfade ?? 1.5;
  if (!built || shape.count <= 0) return null;
  const plane = lanes ? { data: lanes, width: ILL_MAP.width, height: ILL_MAP.height, rHi: built.grid.rHi } : null;
  const ridgeLevel = skeleton ? (r: number, phi: number) => grainDensity(ridgeAt(skeleton, r, phi), tail, grainFade) : null;
  // S109 (sparklebar): on the skeleton, a grain over the drawn bar too (its ellipse's profile, the bar light's own).
  const onBar = ridgeLevel ? barGrain(params, frame) : null;
  const levelOf = ridgeLevel && onBar ? (r: number, phi: number) => Math.max(ridgeLevel(r, phi), onBar(r, phi)) : ridgeLevel;
  // S108: the stream follows the generated galaxy (the frame's reroll, index.ts illSeeded; 0 for the template's own).
  const s = buildSparkle(built.map, built.grid, shape, (SPARKLE_SEED ^ hashString(template ?? "galaxy") ^ (frame?.header.illReroll ?? 0)) >>> 0, built.raw, plane, levelOf);
  if (s.radius.length === 0) return null;
  return { positions: toScene(s.radius, s.azimuth, s.height), weight: s.weight, radius: s.radius };
}

/**
 * The points a sparkle layer draws (S107, rule D1): those kept for its key, else the last that arrived - only if they
 * were built for the same galaxy (`galaxy`: the frame's token and the template); another galaxy's are never drawn.
 */
export function sparkleShown(
  held: SparklePoints | null | undefined,
  arrived: { galaxy: string; points: SparklePoints | null } | null,
  galaxy: string,
): SparklePoints | null {
  if (held !== undefined) return held;
  return arrived && arrived.galaxy === galaxy ? arrived.points : null;
}

/**
 * A string that moves exactly when sparklePoints' answer can (the layer's cache key): the frame's and the lanes' own
 * tokens (illMapClient.ts objectId), the template, and every parameter the build reads.
 */
export function sparkleKey(params: IllParams, frame: IllFrame | null, frameToken: number, template: string | null, lanesToken: string): string {
  const shape = sparkleShape(params);
  return JSON.stringify([
    frameToken,
    template,
    lanesToken,
    shape,
    // armMapFor's own key (arms.ts: its shape and the strength)
    JSON.stringify(shapeOf(params, frame)),
    params.strength ?? 1,
    skeletonOn(params) ? [JSON.stringify(skeletonParamsOf(params)), params.skeltail ?? 0.05, params.skelgrainfade ?? 1.5] : null,
    // S109: the bar's grain (barGrain's inputs; the bar's own geometry is the frame's)
    (params.sparklebar ?? 0) > 0 ? [params.sparklebar, params.barsize ?? 1, params.barthin ?? 1, params.barsharp ?? 2] : null,
  ]);
}

/**
 * S109: the sparkle's density over the drawn bar - sparklebar times the bar light's profile exp(-1.6 e^barsharp), e the
 * ellipse radius in the drawn bar's units (arms.ts illArmsBarE: the published half-length times barsize, the axis
 * ratio times barthin, the angle the lanes read); null at 0 or without a bar.
 */
export function barGrain(params: IllParams, frame: IllFrame | null): ((r: number, phi: number) => number) | null {
  const share = params.sparklebar ?? 0;
  const bar = barOf(frame);
  if (!(share > 0) || !bar) return null;
  const a = bar.halfLength * (params.barsize ?? 1);
  const b = a * bar.axisRatio * (params.barthin ?? 1);
  const sharp = params.barsharp ?? 2;
  const c = Math.cos(bar.angle);
  const s = Math.sin(bar.angle);
  return (r, phi) => {
    const x = r * Math.cos(phi);
    const y = r * Math.sin(phi);
    const e = Math.hypot((x * c + y * s) / a, (y * c - x * s) / b);
    return share * Math.exp(-1.6 * Math.pow(e, sharp));
  };
}
