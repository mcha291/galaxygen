// The sky's drawing (S106, builder D; sky.ts says what and why): the field stars as one Points draw at infinity, the
// floor as a screen quad and the halo as a sprite in the disc's plane, all additive into the frame before the bloom and
// the grade, none read by the dust. The buffers are built once per (shape, lens, aspect), never per frame; the uniforms
// are set in place. Loaded lazily by sky.ts, and mounted only while something of it is drawn.

import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  AdditiveBlending,
  BufferAttribute,
  BufferGeometry,
  DoubleSide,
  Mesh,
  type PerspectiveCamera,
  PlaneGeometry,
  Points,
  ShaderMaterial,
  Vector2,
  Vector3,
} from "three";

import type { IllLayerProps } from "./feature";
import { FLOOR_BLUE, HALO_BLUE, buildSkyStars, grazePair, skyTint, sphereCount } from "./sky";

/** The frame side the sizes are given at, px. */
const SIZE_AT = 1024;
/** The halo's sprite reaches this many of its gaussian radii (its light there e^-6 of the centre's). */
const HALO_REACH = 3.5;
const BUFFER = new Vector2();

const STARS_VERTEX = /* glsl */ `
  attribute vec3 skyColour;
  attribute float skyWeight;
  uniform float skyBright;
  uniform float skySize;
  uniform float skyGlow;
  uniform float skyLogRange;
  uniform float skyPx;
  varying vec3 vSkyColour;
  varying float vSkySigma;
  varying float vSkyGlowSigma;
  varying float vSkyShare;
  varying float vSkyHalf;
  void main() {
    // A direction on the sky, drawn at infinity: only the view's rotation, no translation, so no parallax.
    vec3 v = mat3(viewMatrix) * position;
    if (v.z > -1e-4) {
      gl_Position = vec4(2.0, 2.0, 2.0, 1.0);
      gl_PointSize = 0.0;
      return;
    }
    vec4 c = projectionMatrix * vec4(v, 0.0);
    c.z = 0.0;
    gl_Position = c;
    float t = skyLogRange > 0.0 ? clamp(log(max(skyWeight, 1.0)) / skyLogRange, 0.0, 1.0) : 0.0;
    vSkySigma = max(skySize * skyPx * (1.0 + 0.6 * t), 0.05);
    vSkyShare = skyGlow * smoothstep(0.35, 1.0, t);
    vSkyGlowSigma = 4.0 * vSkySigma;
    float reach = 3.0 * (vSkyShare > 0.001 ? vSkyGlowSigma : vSkySigma);
    gl_PointSize = 2.0 * ceil(reach) + 1.0;
    vSkyHalf = 0.5 * gl_PointSize;
    vSkyColour = skyColour * skyBright;
  }
`;

const STARS_FRAGMENT = /* glsl */ `
  varying vec3 vSkyColour;
  varying float vSkySigma;
  varying float vSkyGlowSigma;
  varying float vSkyShare;
  varying float vSkyHalf;
  void main() {
    vec2 d = (gl_PointCoord - 0.5) * 2.0 * vSkyHalf;
    float r2 = dot(d, d);
    float s2 = vSkySigma * vSkySigma;
    float g2 = vSkyGlowSigma * vSkyGlowSigma;
    float core = exp(-0.5 * r2 / s2) / (6.2831853 * s2);
    float glow = exp(-0.5 * r2 / g2) / (6.2831853 * g2);
    gl_FragColor = vec4(vSkyColour * ((1.0 - vSkyShare) * core + vSkyShare * glow), 1.0);
  }
`;

const FLOOR_VERTEX = /* glsl */ `
  void main() { gl_Position = vec4(position.xy, 0.0, 1.0); }
`;
const FLOOR_FRAGMENT = /* glsl */ `
  uniform vec3 skyFloor;
  void main() { gl_FragColor = vec4(skyFloor, 1.0); }
`;

const HALO_VERTEX = /* glsl */ `
  uniform float skyHaloExtent;
  varying vec2 vSkyR;
  void main() {
    // The sprite lies in the disc's plane (scene y = 0), centred on the galaxy.
    vSkyR = position.xy * skyHaloExtent;
    gl_Position = projectionMatrix * viewMatrix * vec4(vSkyR.x, 0.0, vSkyR.y, 1.0);
  }
`;
// S110 (B2): the halo takes the grazing handover (index.ts illGraze, the registry's illGrazeAt: from, to radians off
// the disc's axis): its light times the weight of the sight line to the fragment's point in the disc's plane, so seen
// edge-on the face-on haze is gone with the veils it sits under and draws no band to the frame's corners. Exactly the
// S109 light while the weight is 1 (every stand from face-on to base.grazeFrom).
const HALO_FRAGMENT = /* glsl */ `
  uniform vec3 skyHalo;
  uniform float skyHaloRadius;
  uniform vec2 skyGrazeAt;
  varying vec2 vSkyR;
  float skyGrazeOf(vec3 d) {
    float c = clamp(abs(d.y) / max(length(d), 1e-20), 0.0, 1.0);
    float a = acos(c);
    if (skyGrazeAt.y <= 0.0 || a <= skyGrazeAt.x) return 1.0;
    if (skyGrazeAt.y <= skyGrazeAt.x) return 0.0;
    return 1.0 - smoothstep(skyGrazeAt.x, skyGrazeAt.y, a);
  }
  void main() {
    float q = dot(vSkyR, vSkyR) / (skyHaloRadius * skyHaloRadius);
    vec3 c = skyHalo * exp(-0.5 * q);
    float g = skyGrazeOf(vec3(vSkyR.x, 0.0, vSkyR.y) - cameraPosition);
    if (g < 1.0) c *= g;
    gl_FragColor = vec4(c, 1.0);
  }
`;

const additive = { transparent: true, blending: AdditiveBlending, depthTest: false, depthWrite: false } as const;

export default function SkyLayer({ params, runtime }: IllLayerProps) {
  const camera = useThree((s) => s.camera) as PerspectiveCamera;
  const size = useThree((s) => s.size);
  const gl = useThree((s) => s.gl);
  // The lens the count is made for: the camera's, followed if it changes without a render (a template's own lens).
  const [fov, setFov] = useState(() => camera.fov ?? 45);
  const aspect = size.width / Math.max(size.height, 1);

  const perFrame = params.stars ?? 0;
  const seed = Math.round(params.seed ?? 1);
  const slope = params.slope ?? 0.8;
  const range = params.range ?? 200;
  const warm = params.warm ?? 0.15;
  const blue = params.blue ?? 0.7;
  const count = sphereCount(perFrame, fov, aspect);

  const stars = useMemo(() => {
    if (count <= 0) return null;
    const s = buildSkyStars({ count, seed: (0x5ca1ab1e ^ Math.imul(seed, 0x9e3779b1)) >>> 0, slope, range, warm, blue });
    const geometry = new BufferGeometry();
    geometry.setAttribute("position", new BufferAttribute(s.direction, 3));
    geometry.setAttribute("skyColour", new BufferAttribute(s.colour, 3));
    geometry.setAttribute("skyWeight", new BufferAttribute(s.weight, 1));
    const material = new ShaderMaterial({
      uniforms: {
        skyBright: { value: 0 },
        skySize: { value: 0.55 },
        skyGlow: { value: 0 },
        skyLogRange: { value: Math.log(Math.max(1, range)) },
        skyPx: { value: 1 },
      },
      vertexShader: STARS_VERTEX,
      fragmentShader: STARS_FRAGMENT,
      ...additive,
    });
    const object = new Points(geometry, material);
    object.frustumCulled = false;
    return object;
  }, [count, seed, slope, range, warm, blue]);
  useEffect(
    () => () => {
      if (!stars) return;
      stars.geometry.dispose();
      (stars.material as ShaderMaterial).dispose();
    },
    [stars],
  );

  const floor = useMemo(() => {
    const object = new Mesh(
      new PlaneGeometry(2, 2),
      new ShaderMaterial({ uniforms: { skyFloor: { value: new Vector3() } }, vertexShader: FLOOR_VERTEX, fragmentShader: FLOOR_FRAGMENT, ...additive }),
    );
    object.frustumCulled = false;
    return object;
  }, []);
  const halo = useMemo(() => {
    const object = new Mesh(
      new PlaneGeometry(2, 2),
      new ShaderMaterial({
        uniforms: { skyHalo: { value: new Vector3() }, skyHaloRadius: { value: 16 }, skyHaloExtent: { value: 16 * HALO_REACH }, skyGrazeAt: { value: new Vector2() } },
        vertexShader: HALO_VERTEX,
        fragmentShader: HALO_FRAGMENT,
        side: DoubleSide,
        ...additive,
      }),
    );
    object.frustumCulled = false;
    return object;
  }, []);
  useEffect(
    () => () => {
      for (const m of [floor, halo]) {
        m.geometry.dispose();
        (m.material as ShaderMaterial).dispose();
      }
    },
    [floor, halo],
  );

  const floorOn = (params.floor ?? 0) > 0;
  const haloOn = (params.halo ?? 0) > 0;
  const floorColour = useMemo(() => skyTint(FLOOR_BLUE, params.floorblue ?? 1), [params.floorblue]);
  const haloColour = useMemo(() => skyTint(HALO_BLUE, params.haloblue ?? 1), [params.haloblue]);

  const latest = useRef(params);
  latest.current = params;
  useFrame(({ camera: cam }) => {
    const p = latest.current;
    const lens = (cam as PerspectiveCamera).fov ?? 45;
    if (lens !== fov) setFov(lens);
    if (stars) {
      const u = (stars.material as ShaderMaterial).uniforms;
      const buffer = gl.getDrawingBufferSize(BUFFER);
      u.skyPx.value = buffer.y / SIZE_AT;
      u.skyBright.value = p.bright ?? 0.018;
      u.skySize.value = p.size ?? 0.55;
      u.skyGlow.value = p.glow ?? 0.25;
    }
    const f = p.floor ?? 0;
    ((floor.material as ShaderMaterial).uniforms.skyFloor.value as Vector3).set(floorColour[0] * f, floorColour[1] * f, floorColour[2] * f);
    const h = p.halo ?? 0;
    const r = Math.max(0.01, p.haloradius ?? 11);
    const hu = (halo.material as ShaderMaterial).uniforms;
    (hu.skyHalo.value as Vector3).set(haloColour[0] * h, haloColour[1] * h, haloColour[2] * h);
    hu.skyHaloRadius.value = r;
    hu.skyHaloExtent.value = r * HALO_REACH;
    const [gFrom, gTo] = grazePair(runtime?.uniforms?.illGrazeAt?.value);
    (hu.skyGrazeAt.value as Vector2).set(gFrom, gTo);
  });

  return (
    <>
      {floorOn && <primitive object={floor} />}
      {haloOn && <primitive object={halo} />}
      {stars && <primitive object={stars} />}
    </>
  );
}
