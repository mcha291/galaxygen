import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo } from "react";
import {
  BufferAttribute,
  BufferGeometry,
  LineBasicMaterial,
  LineSegments,
  NormalBlending,
  type PerspectiveCamera,
  Points,
  ShaderMaterial,
  Vector2,
} from "three";

import { CLOUD_MIN_PX, cellOutlines } from "./components";

// The brightest mode's two diagnostic layers (D205, S50): the cloud census as markers and the level-0
// cells' edges. Neither is light and neither is pickable; the mode's card labels them as diagnostics.

/** The outlines' grey and opacity: a guide under the picture, not a colour of it. A display choice. */
const OUTLINE_GREY = 0.22;
const OUTLINE_OPACITY = 0.55;
/** Drawn first: under the field's volume (−1), the clouds (−0.5) and the stars (0). */
const OUTLINE_ORDER = -2;
const CLOUD_ORDER = -0.5;

/** The level-0 cells' edges (32 rings × 32 sectors over the model's R extent) as one LineSegments in the disc plane. */
export function CellOutlines({ lo, hi }: { lo: number; hi: number }) {
  const lines = useMemo(() => {
    const geometry = new BufferGeometry();
    geometry.setAttribute("position", new BufferAttribute(cellOutlines(lo, hi).positions, 3));
    const material = new LineBasicMaterial({ transparent: true, opacity: OUTLINE_OPACITY, depthTest: false, depthWrite: false });
    material.color.setRGB(OUTLINE_GREY, OUTLINE_GREY, OUTLINE_GREY);
    const object = new LineSegments(geometry, material);
    object.renderOrder = OUTLINE_ORDER;
    object.frustumCulled = false;
    return object;
  }, [lo, hi]);
  useEffect(
    () => () => {
      lines.geometry.dispose();
      (lines.material as LineBasicMaterial).dispose();
    },
    [lines],
  );
  return <primitive object={lines} />;
}

// A marker per cloud, its size the cloud's published diameter at its depth (components.ts cloudMarkerPx,
// line for line), never under CLOUD_MIN_PX; a disc, painted by cloud_mass's declared ramp.
const CLOUD_VERTEX = /* glsl */ `
  attribute float sizePc;
  attribute vec4 paint;
  uniform float pxPerUnit;
  uniform float minPx;
  varying vec4 vPaint;
  void main() {
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    float depth = -mv.z;
    float px = depth > 0.0 ? (2.0 * sizePc / 1000.0) * pxPerUnit / depth : 0.0;
    gl_PointSize = max(minPx, px);
    vPaint = paint;
    gl_Position = projectionMatrix * mv;
  }
`;
const CLOUD_FRAGMENT = /* glsl */ `
  varying vec4 vPaint;
  void main() {
    vec2 d = gl_PointCoord * 2.0 - 1.0;
    if (dot(d, d) > 1.0 || vPaint.a <= 0.0) discard;
    gl_FragColor = vec4(vPaint.rgb, 0.85 * vPaint.a);
  }
`;

interface CloudProps {
  /** Scene positions, three per cloud (positions.ts toScene). */
  positions: Float32Array;
  /** Each cloud's radius, pc (`cloud_size`). */
  sizes: Float32Array;
  /** Linear RGBA per cloud (components.ts cloudColors). */
  colors: Float32Array;
}

/** The cloud census as sized markers: a Points of its own with a per-point size attribute. Not pickable. */
export function CloudMarkers({ positions, sizes, colors }: CloudProps) {
  const gl = useThree((s) => s.gl);
  const points = useMemo(() => {
    const geometry = new BufferGeometry();
    geometry.setAttribute("position", new BufferAttribute(positions, 3));
    geometry.setAttribute("sizePc", new BufferAttribute(sizes, 1));
    geometry.setAttribute("paint", new BufferAttribute(colors, 4));
    const material = new ShaderMaterial({
      uniforms: { pxPerUnit: { value: 1 }, minPx: { value: CLOUD_MIN_PX } },
      vertexShader: CLOUD_VERTEX,
      fragmentShader: CLOUD_FRAGMENT,
      transparent: true,
      blending: NormalBlending, // markers, not light: a crowd of them must not add up to a colour the ramp never gave
      depthTest: false,
      depthWrite: false,
    });
    const object = new Points(geometry, material);
    object.renderOrder = CLOUD_ORDER;
    object.frustumCulled = false;
    return object;
  }, [positions, sizes, colors]);
  useEffect(
    () => () => {
      points.geometry.dispose();
      (points.material as ShaderMaterial).dispose();
    },
    [points],
  );
  // The projection's pixels per kpc at unit depth, in drawing-buffer pixels, and the floor at the device's ratio.
  useFrame(({ camera }) => {
    const buffer = gl.getDrawingBufferSize(BUFFER);
    const fov = (camera as PerspectiveCamera).fov ?? 45;
    const uniforms = (points.material as ShaderMaterial).uniforms;
    uniforms.pxPerUnit.value = buffer.y / (2 * Math.tan((fov * Math.PI) / 360));
    uniforms.minPx.value = CLOUD_MIN_PX * gl.getPixelRatio();
  });
  return <primitive object={points} />;
}

const BUFFER = new Vector2();
