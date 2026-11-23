// The arms' sparkle's drawing (BUILD_VIII row 108): armsSparkle.ts's points through FluxPoints, on the knots' gain (the
// field's scale and exposure), dimmed by the march's dust as the knots are. The buffers are built once per (arm map,
// shaping values, template), never per frame. Loaded lazily by arms.ts.

import { useMemo } from "react";
import { FluxPoints, type PointDust } from "../FluxPoints";
import { toScene } from "../positions";
import { armMapFor, shapeOf } from "./arms";
import { buildSparkle, hashString, sparkleFlux } from "./armsSparkle";
import type { IllLayerProps } from "./feature";

/** The sparkle's blue-white at full share (over the white point). */
const SPARKLE_BLUE: readonly [number, number, number] = [0.72, 0.98, 1.2];
/** The seed of the viewer's own (and the template's name): fixed, never the time or the frame. */
const SPARKLE_SEED = 0x5108a2b5;

export default function ArmsSparkle({ params, runtime, context, knotsGain, dust }: IllLayerProps) {
  const built = armMapFor(params, context.frame);
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
    }),
    [count, params.clump, params.groupsize, params.members, params.sparkleridge, params.sparkleslope, params.sparklerange, rMax],
  );
  const points = useMemo(() => {
    if (!built || shape.count <= 0) return null;
    const s = buildSparkle(built.map, built.grid, shape, (SPARKLE_SEED ^ hashString(context.template ?? "galaxy")) >>> 0);
    if (s.radius.length === 0) return null;
    return { positions: toScene(s.radius, s.azimuth, s.height), weight: s.weight, radius: s.radius };
  }, [built, shape, context.template]);
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
  if (!points || !flux) return null;
  return (
    <FluxPoints
      positions={points.positions}
      flux={flux}
      gain={knotsGain}
      psf={null}
      spriteSize={params.sparklesize ?? 1.5}
      dust={(dust as PointDust | null) ?? null}
      ill={runtime as never}
    />
  );
}
