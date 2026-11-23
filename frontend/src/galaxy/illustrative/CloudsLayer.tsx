// The star clouds' drawing (S106, builder C): flocClouds.ts's points through FluxPoints, on the knots' gain (the
// field's scale and exposure), dimmed by the march's dust as the knots are. Built once per (frame, shaping values),
// never per frame. Loaded lazily by floc.ts (FluxPoints imports the registry).

import { useMemo } from "react";
import { FluxPoints, type PointDust } from "../FluxPoints";
import { toScene } from "../positions";
import { cloudShapeOf, shapeOf } from "./floc";
import { buildClouds, cloudFlux } from "./flocClouds";
import { geometryOf } from "./flocMap";
import { type IllLayerProps, illMeasure, illNow } from "./feature";

export default function CloudsLayer({ params, runtime, context, knotsGain, dust }: IllLayerProps) {
  const shape = shapeOf(params);
  const cloud = cloudShapeOf(params);
  const shapeKey = JSON.stringify([shape, cloud]);
  const frame = context.frame;
  const points = useMemo(() => {
    if (!frame || cloud.count <= 0 || shape.style < 0.5) return null;
    const started = illNow();
    const c = buildClouds(geometryOf(frame), shape, cloud);
    illMeasure("clouds", started);
    if (c.weight.length === 0) return null;
    const n = c.weight.length;
    const radius = new Float32Array(n);
    const azimuth = new Float32Array(n);
    const height = new Float32Array(n);
    for (let i = 0; i < n; i += 1) {
      radius[i] = Math.hypot(c.x[i], c.y[i]);
      const phi = Math.atan2(c.y[i], c.x[i]);
      azimuth[i] = phi < 0 ? phi + 2 * Math.PI : phi;
      height[i] = 0;
    }
    return { clouds: c, positions: toScene(radius, azimuth, height) };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [frame, shapeKey]);
  const base = params.cloudGain ?? 3000;
  const blue = params.cloudBlue ?? 1;
  const warmR = params.cloudWarmR ?? 5;
  const flux = useMemo(() => (points ? cloudFlux(points.clouds, base, blue, warmR) : null), [points, base, blue, warmR]);
  if (!points || !flux) return null;
  return (
    <FluxPoints
      positions={points.positions}
      flux={flux}
      gain={knotsGain}
      psf={null}
      spriteSize={params.cloudSize ?? 1.5}
      dust={(dust as PointDust | null) ?? null}
      ill={runtime as never}
    />
  );
}
