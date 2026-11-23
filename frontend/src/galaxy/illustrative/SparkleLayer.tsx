// The arms' sparkle's drawing (BUILD_VIII row 108): armsSparkle.ts's points through FluxPoints, on the knots' gain (the
// field's scale and exposure), dimmed by the march's dust as the knots are. The buffers are built once per (arm map,
// shaping values, template), never per frame. Loaded lazily by arms.ts.
//
// S106 (the Milky Way's grain): the points are drawn in two tiers - the fine grain on the small sprite and the
// brightest share (`sparklebig`) on a larger one (`sparklebigsize`) - so the arms' grain has sizes, not one dot.
// A share of 0 draws every point on the small sprite, as S105 did.

import { useMemo } from "react";
import { FluxPoints, type PointDust } from "../FluxPoints";
import { toScene } from "../positions";
import { armMapFor, armsSkeleton, shapeOf } from "./arms";
import { skeletonOn } from "./armsSkeleton";
import { grainDensity, ridgeAt } from "./skeleton";
import { buildSparkle, hashString, sparkleFlux, sparkleTiers, tierIndices } from "./armsSparkle";
import { ILL_MAP, type IllLayerProps } from "./feature";

/** The sparkle's blue-white at full share (over the white point). */
const SPARKLE_BLUE: readonly [number, number, number] = [0.72, 0.98, 1.2];
/** The seed of the viewer's own (and the template's name): fixed, never the time or the frame. */
const SPARKLE_SEED = 0x5108a2b5;

/** The members `idx` of a flat buffer of `width` values per point. */
function pick(values: Float32Array, idx: Uint32Array, width: number): Float32Array {
  const out = new Float32Array(idx.length * width);
  for (let k = 0; k < idx.length; k++) for (let c = 0; c < width; c++) out[k * width + c] = values[idx[k] * width + c];
  return out;
}

export default function ArmsSparkle({ params, runtime, context, knotsGain, dust }: IllLayerProps) {
  const built = armMapFor(params, context.frame);
  // S106: on the skeleton, the grain's density read across its ridges (skeleton.ts grainDensity) in place of the share.
  const skeleton = skeletonOn(params) ? armsSkeleton(context.frame, params) : null;
  const tail = params.skeltail ?? 0.05;
  const grainFade = params.skelgrainfade ?? 1.5;
  const count = params.sparkle ?? 0;
  const rMax = params.sparkleedge ?? 16;
  const shape = useMemo(
    () => ({
      count,
      clump: params.clump ?? 0.6,
      groupPc: params.groupsize ?? 120,
      members: params.members ?? 10,
      ridge: params.sparkleridge ?? 2,
      slope: params.sparkleslope ?? 1.4,
      range: params.sparklerange ?? 40,
      rMax,
      heightPc: 60,
      floor: params.sparklefloor ?? 0,
      lift: params.sparklelift ?? 0,
      avoid: params.sparkleavoid ?? 0,
      bunch: params.sparklebunch ?? 0,
      bunchPc: params.sparklebunchsize ?? 400,
      bunchBright: params.sparklebunchbright ?? 0,
    }),
    [count, params.clump, params.groupsize, params.members, params.sparkleridge, params.sparkleslope, params.sparklerange, rMax, params.sparklefloor, params.sparklelift, params.sparkleavoid, params.sparklebunch, params.sparklebunchsize, params.sparklebunchbright],
  );
  // S106: the shared map (its R the lanes), read only while the sparkle keeps off the lanes.
  const mapTex = (shape.avoid ?? 0) > 0 ? ((runtime as { uniforms?: Record<string, { value: unknown }> }).uniforms?.illMapTex?.value as { image?: { data?: ArrayLike<number>; width?: number; height?: number } } | undefined) : undefined;
  const points = useMemo(() => {
    if (!built || shape.count <= 0) return null;
    const img = mapTex?.image;
    const lanes =
      img?.data && img.width === ILL_MAP.width && img.height === ILL_MAP.height ? { data: img.data, width: img.width, height: img.height, rHi: built.grid.rHi } : null;
    const levelOf = skeleton ? (r: number, phi: number) => grainDensity(ridgeAt(skeleton, r, phi), tail, grainFade) : null;
    const s = buildSparkle(built.map, built.grid, shape, (SPARKLE_SEED ^ hashString(context.template ?? "galaxy")) >>> 0, built.raw, lanes, levelOf);
    if (s.radius.length === 0) return null;
    return { positions: toScene(s.radius, s.azimuth, s.height), weight: s.weight, radius: s.radius };
  }, [built, shape, context.template, mapTex, skeleton, tail, grainFade]);
  const blue = params.sparkleblue ?? 0.7;
  const base = params.sparklegain ?? 2e4;
  const start = shapeOf(params, context.frame).start;
  const h = context.frame?.header.scalars.thin_disc_scale_length;
  const scale = (typeof h === "number" && h > 0 ? h : 2.5) * (params.sparklefall ?? 1);
  const flux = useMemo(() => {
    if (!points) return null;
    const c = SPARKLE_BLUE.map((v) => 1 + (v - 1) * blue) as [number, number, number];
    return sparkleFlux(points.weight, points.radius, base, c, start, scale);
  }, [points, blue, base, start, scale]);
  const bigShare = params.sparklebig ?? 0;
  const tiers = useMemo(() => {
    if (!points || !flux) return null;
    const t = sparkleTiers(points.weight, bigShare);
    return [0, 1].map((tier) => {
      const idx = tierIndices(t, tier);
      return idx.length === 0 ? null : { positions: pick(points.positions, idx, 3), flux: pick(flux, idx, 3) };
    });
  }, [points, flux, bigShare]);
  if (!tiers) return null;
  const sizes = [params.sparklesize ?? 1.5, params.sparklebigsize ?? 3];
  return (
    <>
      {tiers.map((t, i) =>
        t ? (
          <FluxPoints
            key={i}
            positions={t.positions}
            flux={t.flux}
            gain={knotsGain}
            psf={null}
            spriteSize={sizes[i]}
            dust={(dust as PointDust | null) ?? null}
            ill={runtime as never}
          />
        ) : null,
      )}
    </>
  );
}
