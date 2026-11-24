// The star clouds' drawing (S106, builder C): flocClouds.ts's points through FluxPoints, on the knots' gain (the
// field's scale and exposure), dimmed by the march's dust as the knots are. Built once per (frame, shaping values),
// never per frame. Loaded lazily by floc.ts (FluxPoints imports the registry).

import { useMemo } from "react";
import { FluxPoints, type PointDust } from "../FluxPoints";
import { toScene } from "../positions";
import { cloudShapeOf, cloudThin, shapeOf } from "./floc";
import { buildClouds, buildSparks, cloudFlux } from "./flocClouds";
import { geometryOf } from "./flocMap";
import { type IllLayerProps, illMeasure, illNow } from "./feature";

export default function CloudsLayer({ params, runtime, context, knotsGain, dust }: IllLayerProps) {
  const shape = shapeOf(params);
  const cloud = cloudShapeOf(params);
  // S109 (B2): the clouds thinned by the disc's fall-off (floc.ts cloudThin), its values in the key.
  const thinned = cloudThin(params);
  const shapeKey = JSON.stringify([shape, cloud, thinned.key]);
  const frame = context.frame;
  const points = useMemo(() => {
    if (!frame || cloud.count <= 0 || shape.style < 0.5) return null;
    const started = illNow();
    const c = buildClouds(geometryOf(frame), shape, cloud, thinned.thin);
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
  // S108 (the grazing handover; pointsPlace.ts): the clouds lie in the midplane; toward edge-on FluxPoints lifts them
  // by the base's point-layer height through a uniform of this material's own (illPointsLift) beside the shared ones,
  // so they are a thin lit layer, not a line. The runtime handed on is made once per runtime (its uniforms shared).
  const lifted = useMemo(() => {
    const r = runtime as unknown as { glsl: string; uniforms: Record<string, { value: unknown }>; version: number };
    return { ...r, uniforms: { ...r.uniforms, illPointsLift: { value: 0 } } };
  }, [runtime]);
  lifted.uniforms.illPointsLift.value = context.paramsOf?.("base").pointHeight ?? 0;
  // S110 (B2): the sparks (flocClouds.ts buildSparks), single sharp points, built once per their shaping values.
  const spark = {
    count: params.sparkCount ?? 0, from: params.sparkFrom ?? 5, to: params.sparkTo ?? 12, inner: params.sparkInner ?? 0.15,
    slope: params.sparkSlope ?? 1.2, range: params.sparkRange ?? 30, seed: params.seed ?? 11,
  };
  const sparkKey = JSON.stringify(spark);
  const sparks = useMemo(() => {
    if (spark.count <= 0 || shape.style < 0.5) return null;
    const s = buildSparks(spark);
    const n = s.weight.length;
    const radius = new Float32Array(n);
    const azimuth = new Float32Array(n);
    for (let i = 0; i < n; i += 1) {
      radius[i] = Math.hypot(s.x[i], s.y[i]);
      const phi = Math.atan2(s.y[i], s.x[i]);
      azimuth[i] = phi < 0 ? phi + 2 * Math.PI : phi;
    }
    return { s, positions: toScene(radius, azimuth, new Float32Array(n)) };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sparkKey, shape.style]);
  const sparkGain = params.sparkGain ?? 30000;
  const sparkFlux = useMemo(() => (sparks ? cloudFlux({ ...sparks.s, groups: [] }, sparkGain, blue, warmR) : null), [sparks, sparkGain, blue, warmR]);
  if ((!points || !flux) && !(sparks && sparkFlux)) return null;
  return (
    <>
      {points && flux && (
        <FluxPoints
          positions={points.positions}
          flux={flux}
          gain={knotsGain}
          psf={null}
          spriteSize={params.cloudSize ?? 1.5}
          dust={(dust as PointDust | null) ?? null}
          ill={lifted as never}
          illCap={params.cloudCap ?? 0}
        />
      )}
      {sparks && sparkFlux && (
        <FluxPoints
          positions={sparks.positions}
          flux={sparkFlux}
          gain={knotsGain}
          psf={null}
          spriteSize={params.sparkSize ?? 0.8}
          dust={(dust as PointDust | null) ?? null}
          ill={lifted as never}
          illCap={params.sparkCap ?? 0}
        />
      )}
    </>
  );
}
