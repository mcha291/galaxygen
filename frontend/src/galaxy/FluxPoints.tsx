import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo } from "react";
import { AdditiveBlending, BufferAttribute, BufferGeometry, type PerspectiveCamera, Points, ShaderMaterial, type Texture, Vector2, Vector3 } from "three";

import { DUST_SEGMENT_STEPS } from "./flux";
import { type SpritePsf, psfMean, psfTexture } from "./psf";
import { RING_ROWS } from "./regimes";

// The star-first mode's points (S50, D208): each a published flux on the field's own scale. A point's sprite
// deposits, summed over its pixels, its light over the area of sky one pixel covers at the point (flux.ts
// pixelArea and spriteLight, line for line), times the field's gain; and the dust between the point and the
// camera dims it per channel (flux.ts dustToPoint, line for line), read from the textures the march reads.
// Additive: light adds. Not pickable here: the view's Picker works on positions.

/** The march's dust, as the points read it: the ring texture, the scattered light's (whose spare channel is the
 * dust's placement), the radial extent they span, and the slab the segment is cut by, kpc. */
export interface PointDust {
  rings: Texture;
  scatter: Texture;
  rLo: number;
  rHi: number;
  top: number;
}

const VERTEX = /* glsl */ `
  attribute vec3 flux;
  uniform float pxPerUnit;
  uniform float spritePx;
  uniform float gain;
  uniform vec3 spriteMean;
  uniform sampler2D rings;
  uniform sampler2D scatter;
  uniform float rLo;
  uniform float rHi;
  uniform float dustTop;
  uniform float dustOn;
  varying vec3 vLight;

  // The march's own (FieldVolume): a sech²(y / 2h) / 4h layer's column from height y0 to y1 over a path ds.
  float sech2(float x) { float c = cosh(clamp(x, -30.0, 30.0)); return 1.0 / (c * c); }
  float safeTanh(float x) { return tanh(clamp(x, -10.0, 10.0)); }
  float column(float y0, float y1, float h, float ds) {
    if (h <= 0.0) return 0.0;
    float dy = y1 - y0;
    if (abs(dy) < 1e-4 * h) return sech2(0.5 * (y0 + y1) / (2.0 * h)) / (4.0 * h) * ds;
    return abs(safeTanh(y1 / (2.0 * h)) - safeTanh(y0 / (2.0 * h))) * 0.5 * ds / abs(dy);
  }

  // The dust's optical depth per channel from the point to the camera (flux.ts dustToPoint, line for line).
  vec3 dustTo(vec3 p) {
    vec3 d = cameraPosition - p;
    float len = length(d);
    vec3 tau = vec3(0.0);
    if (len <= 0.0) return tau;
    vec3 u = d / len;
    float sMax = len;
    if (abs(u.y) > 1e-6) sMax = min(sMax, max(0.0, ((u.y > 0.0 ? dustTop : -dustTop) - p.y) / u.y));
    float a = dot(u.xz, u.xz);
    if (a > 1e-12) {
      float b = dot(p.xz, u.xz);
      float c = dot(p.xz, p.xz) - rHi * rHi;
      float disc = b * b - a * c;
      sMax = disc > 0.0 ? min(sMax, max(0.0, (-b + sqrt(disc)) / a)) : 0.0;
    }
    if (sMax <= 0.0) return tau;
    float ds = sMax / float(${DUST_SEGMENT_STEPS});
    for (int j = 0; j < ${DUST_SEGMENT_STEPS}; j++) {
      float s0 = float(j) * ds;
      float s1 = s0 + ds;
      vec3 q = p + u * (0.5 * (s0 + s1));
      float r = length(q.xz);
      if (r >= rHi) continue;
      float phi = atan(-q.z, q.x);
      if (phi < 0.0) phi += 6.28318531;
      float x = (r - rLo) / (rHi - rLo);
      vec3 face = textureLod(rings, vec2(x, (${RING_ROWS.depth}.0 + 0.5) / ${RING_ROWS.count}.0), 0.0).rgb;
      float h = textureLod(rings, vec2(x, (${RING_ROWS.thermal}.0 + 0.5) / ${RING_ROWS.count}.0), 0.0).a;
      float place = textureLod(scatter, vec2(x, phi / 6.28318531), 0.0).a;
      tau += face * place * column(p.y + u.y * s0, p.y + u.y * s1, h, ds);
    }
    return tau;
  }

  void main() {
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    float depth = -mv.z;
    float dist = length(mv.xyz);
    vec3 light = vec3(0.0);
    if (depth > 0.0) {
      // The area of sky one pixel covers at the point, pc² (flux.ts pixelArea), and the sprite's unit sum.
      float side = 1000.0 * depth / pxPerUnit;
      float area = side * side * depth / dist;
      light = flux * gain / (area * spritePx * spritePx * spriteMean);
      if (dustOn > 0.5) light *= exp(-dustTo(position));
    }
    vLight = light;
    gl_PointSize = spritePx;
    gl_Position = projectionMatrix * mv;
  }
`;

const FRAGMENT = /* glsl */ `
  uniform sampler2D sprite;
  varying vec3 vLight;
  void main() {
    // The instrument's pattern per channel: the sprite's colour times its alpha (psf.ts), unit sum over the sprite.
    vec4 t = texture2D(sprite, gl_PointCoord);
    gl_FragColor = vec4(vLight * t.rgb * t.a, 1.0);
  }
`;

interface Props {
  /** Scene positions, three per point (positions.ts toScene). */
  positions: Float32Array;
  /** Each point's light per channel, L☉ over the white point (flux.ts fluxOf). */
  flux: Float32Array;
  /** The field's gain: LIGHT_PER_LSUN_PC2 times the field gain, the exposure's stops and the point gain. */
  gain: number;
  /** A named instrument's sprite; the default PSF at `spriteSize` without one. */
  psf: SpritePsf | null;
  spriteSize: number;
  /** The march's dust for the segment to each point; null draws the points undimmed. */
  dust: PointDust | null;
}

const BUFFER = new Vector2();

export function FluxPoints({ positions, flux, gain, psf, spriteSize, dust }: Props) {
  const gl = useThree((s) => s.gl);
  const points = useMemo(() => {
    const geometry = new BufferGeometry();
    geometry.setAttribute("position", new BufferAttribute(positions, 3));
    geometry.setAttribute("flux", new BufferAttribute(flux, 3));
    const sprite = psfTexture();
    const material = new ShaderMaterial({
      uniforms: {
        pxPerUnit: { value: 1 },
        spritePx: { value: 1 },
        gain: { value: 0 },
        spriteMean: { value: new Vector3(1, 1, 1) },
        sprite: { value: sprite },
        // Bound to the sprite until the march's textures arrive: never read while dustOn is 0.
        rings: { value: sprite },
        scatter: { value: sprite },
        rLo: { value: 0 },
        rHi: { value: 1 },
        dustTop: { value: 0 },
        dustOn: { value: 0 },
      },
      vertexShader: VERTEX,
      fragmentShader: FRAGMENT,
      transparent: true,
      blending: AdditiveBlending,
      depthTest: false,
      depthWrite: false,
    });
    const object = new Points(geometry, material);
    object.frustumCulled = false;
    return object;
  }, [positions, flux]);
  useEffect(
    () => () => {
      points.geometry.dispose();
      (points.material as ShaderMaterial).dispose();
    },
    [points],
  );
  useFrame(({ camera }) => {
    const uniforms = (points.material as ShaderMaterial).uniforms;
    const buffer = gl.getDrawingBufferSize(BUFFER);
    const fov = (camera as PerspectiveCamera).fov ?? 45;
    uniforms.pxPerUnit.value = buffer.y / (2 * Math.tan((fov * Math.PI) / 360));
    uniforms.spritePx.value = (psf?.size ?? spriteSize) * gl.getPixelRatio();
    uniforms.gain.value = gain;
    const mean = psf?.mean ?? DEFAULT_MEAN;
    (uniforms.spriteMean.value as Vector3).set(mean[0], mean[1], mean[2]);
    uniforms.sprite.value = psf?.texture ?? psfTexture();
    uniforms.dustOn.value = dust ? 1 : 0;
    if (dust) {
      uniforms.rings.value = dust.rings;
      uniforms.scatter.value = dust.scatter;
      uniforms.rLo.value = dust.rLo;
      uniforms.rHi.value = dust.rHi;
      uniforms.dustTop.value = dust.top;
    }
  });
  return <primitive object={points} />;
}

const DEFAULT_MEAN: [number, number, number] = (() => {
  const m = psfMean();
  return [m, m, m];
})();
