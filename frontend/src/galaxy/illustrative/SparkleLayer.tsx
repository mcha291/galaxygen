// The arms' sparkle's drawing (BUILD_VIII row 108): armsSparkle.ts's points through FluxPoints, on the knots' gain (the
// field's scale and exposure), dimmed by the march's dust as the knots are. The buffers are built once per (arm map,
// shaping values, template), never per frame. Loaded lazily by arms.ts.

import { useMemo } from "react";
import { FluxPoints, type PointDust } from "../FluxPoints";
import { toScene } from "../positions";
import { armMapFor } from "./arms";
import { buildSparkle, hashString } from "./armsSparkle";
import type { IllLayerProps } from "./feature";

/** The sparkle's blue-white at full share (over the white point). */
const SPARKLE_BLUE: readonly [number, number, number] = [0.62, 0.84, 1.25];
/** The seed of the viewer's own (and the template's name): fixed, never the time or the frame. */
const SPARKLE_SEED = 0x5108a2b5;

export default function ArmsSparkle({ params, runtime, context, knotsGain, dust }: IllLayerProps) {
  const built = armMapFor(params, context.frame);
  const count = params.sparkle ?? 0;
  const rMax = (params.extend ?? 0) + 18;
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
    return { positions: toScene(s.radius, s.azimuth, s.height), weight: s.weight };
  }, [built, shape, context.template]);
  const blue = params.sparkleblue ?? 0.7;
  const base = params.sparklegain ?? 2e4;
  const flux = useMemo(() => {
    if (!points) return null;
    const c = SPARKLE_BLUE.map((v) => 1 + (v - 1) * blue);
    const out = new Float32Array(points.weight.length * 3);
    for (let i = 0; i < points.weight.length; i++) for (let k = 0; k < 3; k++) out[3 * i + k] = points.weight[i] * base * c[k];
    return out;
  }, [points, blue, base]);
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
