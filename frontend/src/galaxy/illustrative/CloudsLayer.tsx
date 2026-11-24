// The star clouds' drawing (S106, builder C): flocClouds.ts's points through FluxPoints, on the knots' gain (the
// field's scale and exposure), dimmed by the march's dust as the knots are. Built once per (frame, shaping values),
// never per frame. Loaded lazily by floc.ts (FluxPoints imports the registry).

import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo, useRef } from "react";
import { AdditiveBlending, BufferAttribute, BufferGeometry, Points, ShaderMaterial, Vector2 } from "three";
import { FluxPoints, type PointDust } from "../FluxPoints";
import { toScene } from "../positions";
import { cloudShapeOf, cloudThin, shapeOf, sparkFallOf } from "./floc";
import { buildClouds, buildSparks, cloudFlux } from "./flocClouds";
import { geometryOf } from "./flocMap";
import { type IllLayerProps, illMeasure, illNow } from "./feature";
import { grazePair } from "./sky";

/** The frame side the sharp sparks' sizes are given at, px (as the sky's stars). */
const SPARK_SIZE_AT = 1024;
const SPARK_BUFFER = new Vector2();

// S111 (B): the sharp sparks - each a tight gaussian core a pixel or so across at a given PEAK brightness in the frame's
// linear light (not a sprite of unit sum, whose peak the bloom then spreads into a soft disc), a faint halo of its own
// and, at will, a faint four-ray cross along the frame's axes. The peak is set near the bloom's threshold, so the
// bloom adds little and the point stays sharp; the halo and the cross are drawn here, not by the bloom. Lying in the
// disc's plane; they fade with the grazing handover (index.ts illGraze) as the disc's light does.
const SPARK_VERTEX = /* glsl */ `
  attribute vec3 sparkColour;
  uniform float sparkPeak;
  uniform float sparkCore;
  uniform float sparkHalo;
  uniform float sparkCross;
  uniform float sparkPx;
  uniform vec2 sparkGrazeAt;
  varying vec3 vSparkColour;
  varying float vSparkSigma;
  varying float vSparkHalf;
  float sparkGrazeOf(vec3 d) {
    float c = clamp(abs(d.y) / max(length(d), 1e-20), 0.0, 1.0);
    float a = acos(c);
    if (sparkGrazeAt.y <= 0.0 || a <= sparkGrazeAt.x) return 1.0;
    if (sparkGrazeAt.y <= sparkGrazeAt.x) return 0.0;
    return 1.0 - smoothstep(sparkGrazeAt.x, sparkGrazeAt.y, a);
  }
  void main() {
    vec4 w = modelMatrix * vec4(position, 1.0);
    float g = sparkGrazeOf(w.xyz - cameraPosition);
    gl_Position = projectionMatrix * viewMatrix * w;
    vSparkSigma = max(sparkCore * sparkPx, 0.2);
    float reach = (sparkHalo > 0.0 || sparkCross > 0.0) ? 6.0 * vSparkSigma + 2.0 * sparkPx : 3.0 * vSparkSigma;
    gl_PointSize = g > 0.0 ? 2.0 * ceil(reach) + 1.0 : 0.0;
    vSparkHalf = 0.5 * gl_PointSize;
    vSparkColour = sparkColour * sparkPeak * g;
  }
`;
const SPARK_FRAGMENT = /* glsl */ `
  uniform float sparkHalo;
  uniform float sparkCross;
  varying vec3 vSparkColour;
  varying float vSparkSigma;
  varying float vSparkHalf;
  void main() {
    vec2 d = (gl_PointCoord - 0.5) * 2.0 * vSparkHalf;
    float s2 = vSparkSigma * vSparkSigma;
    float r2 = dot(d, d);
    float core = exp(-0.5 * r2 / s2);
    float halo = sparkHalo * 0.08 * exp(-0.5 * r2 / (9.0 * s2));
    float edge = 1.0 - smoothstep(0.6 * vSparkHalf, vSparkHalf, sqrt(r2));
    float cross = sparkCross * 0.25 * (exp(-0.5 * d.y * d.y / (0.25 * s2)) * exp(-abs(d.x) / (2.0 * vSparkSigma)) + exp(-0.5 * d.x * d.x / (0.25 * s2)) * exp(-abs(d.y) / (2.0 * vSparkSigma))) * edge;
    gl_FragColor = vec4(vSparkColour * (core + (halo + cross) * edge), 1.0);
  }
`;

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
  // S111 (B): sparkSharp 1 draws the sparks as sharp cores of a given peak (SPARK_VERTEX), not through FluxPoints.
  const sharp = (params.sparkSharp ?? 0) >= 0.5;
  const sparkFlux = useMemo(() => (sparks && !sharp ? cloudFlux({ ...sparks.s, groups: [] }, sparkGain, blue, warmR) : null), [sparks, sharp, sparkGain, blue, warmR]);
  // The sharp sparks' colours: the clouds' cream to blue-white law at unit base, times the disc's fall-off (the points'
  // share), so a spark on the dim outskirts is as dim as its disc.
  const fallKey = JSON.stringify(sparkFallOf(params).key);
  const sharpPoints = useMemo(() => {
    if (!sparks || !sharp) return null;
    const fall = sparkFallOf(params).at;
    const colour = cloudFlux({ ...sparks.s, groups: [] }, 1, blue, warmR);
    for (let i = 0; i < sparks.s.weight.length; i += 1) {
      const f = fall(Math.hypot(sparks.s.x[i], sparks.s.y[i]));
      for (let ch = 0; ch < 3; ch += 1) colour[3 * i + ch] *= f;
    }
    const geometry = new BufferGeometry();
    geometry.setAttribute("position", new BufferAttribute(sparks.positions, 3));
    geometry.setAttribute("sparkColour", new BufferAttribute(colour, 3));
    const material = new ShaderMaterial({
      uniforms: {
        sparkPeak: { value: 1 }, sparkCore: { value: 0.6 }, sparkHalo: { value: 0 }, sparkCross: { value: 0 }, sparkPx: { value: 1 },
        sparkGrazeAt: { value: new Vector2() },
      },
      vertexShader: SPARK_VERTEX,
      fragmentShader: SPARK_FRAGMENT,
      transparent: true, blending: AdditiveBlending, depthTest: false, depthWrite: false,
    });
    const object = new Points(geometry, material);
    object.frustumCulled = false;
    return object;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sparks, sharp, blue, warmR, fallKey]);
  useEffect(() => () => {
    if (!sharpPoints) return;
    sharpPoints.geometry.dispose();
    (sharpPoints.material as ShaderMaterial).dispose();
  }, [sharpPoints]);
  const gl = useThree((s) => s.gl);
  const latest = useRef(params);
  latest.current = params;
  useFrame(() => {
    if (!sharpPoints) return;
    const p = latest.current;
    const u = (sharpPoints.material as ShaderMaterial).uniforms;
    u.sparkPx.value = gl.getDrawingBufferSize(SPARK_BUFFER).y / SPARK_SIZE_AT;
    u.sparkPeak.value = p.sparkPeak ?? 1;
    u.sparkCore.value = p.sparkCore ?? 0.6;
    u.sparkHalo.value = p.sparkHalo ?? 0;
    u.sparkCross.value = p.sparkCross ?? 0;
    const [gFrom, gTo] = grazePair((runtime as unknown as { uniforms?: Record<string, { value: unknown }> })?.uniforms?.illGrazeAt?.value);
    (u.sparkGrazeAt.value as Vector2).set(gFrom, gTo);
  });
  if ((!points || !flux) && !(sparks && sparkFlux) && !sharpPoints) return null;
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
      {sharpPoints && <primitive object={sharpPoints} />}
    </>
  );
}
