import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo } from "react";
import { AdditiveBlending, BufferAttribute, BufferGeometry, type PerspectiveCamera, Points, ShaderMaterial, type Texture, Vector2, Vector3 } from "three";

import { DUST_SEGMENT_STEPS } from "./flux";
import { DISC_LOOP_HALF, PLUMMER_HALF_MASS, PLUMMER_REACH, PROFILE_MAX_HALF } from "./plummer";
import { type PhysicalPsf, type SpritePsf, psfMean, psfTexture } from "./psf";
import { RING_ROWS } from "./regimes";

// The star-first mode's points (S50, D208): each a published flux on the field's own scale. A point's sprite
// deposits, summed over its pixels, its light over the area of sky one pixel covers at the point (flux.ts
// pixelArea and spriteLight, line for line), times the field's gain; and the dust between the point and the
// camera dims it per channel (flux.ts dustToPoint, line for line), read from the textures the march reads.
// Additive: light adds. Not pickable here: the view's Picker works on positions.
//
// Since S64 (V6; RULING_S64 R6, R7) a point with an extent (pc) and a profile is drawn with its own extent once its
// diameter fills a pixel (plummer.ts, line for line): a cluster as a Plummer sphere of its half-mass radius, a knot as
// a disc of its Stromgren radius, in a box of whole pixels round it, each pixel taking the profile's light over its
// own area over the box's - its light summed over the box, dimmed as the point is. Below the switch, or without a
// profile, the point is drawn exactly as before (the same statements: the frame is the same bytes).

/** The march's dust, as the points read it: the ring texture, the scattered light's (whose spare channel is the
 * dust's placement), the radial extent they span, and the slab the segment is cut by, kpc. Since S64 (V6) the clouds'
 * raster (null: no clouds drawn) and its slab texture (each texel's clouds' mean height and half-thickness, kpc), and
 * each channel's depth per magnitude of A_V. Since S66 (V7, D226 R7) the march multiplies the diffuse dust's placement
 * per sub-step by the gas fluctuation map and draws the spurs from their table; the points do not: a point's dust is
 * the ring's placed column as the textures hold it (the cell means, spurs included), unmodulated below the cell - a
 * debt (the mend: the GLSL include shared into this shader, its pin moved). */
export interface PointDust {
  rings: Texture;
  scatter: Texture;
  rLo: number;
  rHi: number;
  top: number;
  clouds?: Texture | null;
  slab?: Texture | null;
  cloudExt?: readonly [number, number, number];
}

// plummer.ts plummerCorner and plummerRect, line for line: the Plummer's share of its light over a rectangle.
const PROFILE_GLSL = /* glsl */ `
  float plummerCorner(float x, float y, float a) {
    float sx = sqrt(a * a + x * x);
    float sy = sqrt(a * a + y * y);
    return ((x / sx) * atan(y / sx) + (y / sy) * atan(x / sy)) / 6.28318531;
  }
  float plummerRect(vec2 lo, vec2 hi, float a) {
    return plummerCorner(hi.x, hi.y, a) - plummerCorner(lo.x, hi.y, a) - plummerCorner(hi.x, lo.y, a) + plummerCorner(lo.x, lo.y, a);
  }
`;

// hstPsf.ts psfCorner and psfRect, line for line (S67, D227 R1): the instrument's PSF table's light between the centre and
// u (cells from the centre, each axis), clamped to the table and bilinear between its nodes, per channel; a rectangle's
// light is four corners.
const PSF_GLSL = /* glsl */ `
  uniform sampler2D psfTable;
  uniform float psfCells;
  vec3 psfCorner(vec2 u) {
    vec2 g = clamp(u + 0.5 * psfCells, 0.0, psfCells);
    vec2 i = min(floor(g), psfCells - 1.0);
    vec2 f = g - i;
    ivec2 a = ivec2(i);
    vec3 c00 = texelFetch(psfTable, a, 0).rgb;
    vec3 c10 = texelFetch(psfTable, a + ivec2(1, 0), 0).rgb;
    vec3 c01 = texelFetch(psfTable, a + ivec2(0, 1), 0).rgb;
    vec3 c11 = texelFetch(psfTable, a + ivec2(1, 1), 0).rgb;
    return (c00 * (1.0 - f.x) + c10 * f.x) * (1.0 - f.y) + (c01 * (1.0 - f.x) + c11 * f.x) * f.y;
  }
  vec3 psfRect(vec2 lo, vec2 hi) {
    return psfCorner(hi) - psfCorner(vec2(lo.x, hi.y)) - psfCorner(vec2(hi.x, lo.y)) + psfCorner(lo);
  }
`;

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
  uniform sampler2D cloudTex;
  uniform sampler2D cloudSlab;
  uniform vec3 cloudExt;
  uniform float cloudsOn;
  // The profile (S64): 0 none, 1 a Plummer sphere of half-mass radius extent, 2 a disc of radius extent (pc); the
  // drawing buffer's size, px.
  attribute float extent;
  uniform float profile;
  uniform vec2 bufferPx;
  varying vec3 vLight;
  varying float vMode;
  varying vec4 vBox;
  varying vec2 vCentre;
  varying float vNorm;
  ${PROFILE_GLSL}
  // The instrument's image of a point (S67, D227 R1): on where the template's optics apply; the table's pc per cell; each
  // channel's normaliser, one over the table's light over the box.
  uniform float physOn;
  uniform float psfCellPc;
  varying vec3 vNorm3;
  ${PSF_GLSL}
  // plummer.ts discNorm: the disc's coverage summed over its box, or its area past the loop's bound.
  float discNorm(vec2 c, vec2 k0, float n, float r) {
    if (n > ${2 * DISC_LOOP_HALF + 1}.0) return 3.14159265 * r * r;
    float s = 0.0;
    for (int i = 0; i < ${2 * DISC_LOOP_HALF + 1}; i++) {
      if (float(i) >= n) break;
      for (int j = 0; j < ${2 * DISC_LOOP_HALF + 1}; j++) {
        if (float(j) >= n) break;
        s += clamp(r - length(k0 + vec2(float(i), float(j)) + 0.5 - c) + 0.5, 0.0, 1.0);
      }
    }
    return s;
  }

  // The march's own (FieldVolume): a sech²(y / 2h) / 4h layer's column from height y0 to y1 over a path ds.
  float sech2(float x) { float c = cosh(clamp(x, -30.0, 30.0)); return 1.0 / (c * c); }
  float safeTanh(float x) { return tanh(clamp(x, -10.0, 10.0)); }
  float column(float y0, float y1, float h, float ds) {
    if (h <= 0.0) return 0.0;
    float dy = y1 - y0;
    if (abs(dy) < 1e-4 * h) return sech2(0.5 * (y0 + y1) / (2.0 * h)) / (4.0 * h) * ds;
    return abs(safeTanh(y1 / (2.0 * h)) - safeTanh(y0 / (2.0 * h))) * 0.5 * ds / abs(dy);
  }

  // The column of a uniform slab of face-on depth 1 between heights lo and hi (regimes.ts slabColumn, line for line).
  float slabColumn(float y0, float y1, float lo, float hi, float ds) {
    float thick = hi - lo;
    if (thick <= 0.0) return 0.0;
    float dy = y1 - y0;
    if (abs(dy) < 1e-4 * thick) {
      float mid = 0.5 * (y0 + y1);
      return (mid >= lo && mid <= hi) ? ds / thick : 0.0;
    }
    float overlap = max(0.0, min(max(y0, y1), hi) - max(min(y0, y1), lo));
    return overlap / thick * ds / abs(dy);
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
      // The diffuse share the ring's realised clouds leave (S64), and the clouds' own layer from the march's raster.
      float share = textureLod(rings, vec2(x, (${RING_ROWS.share}.0 + 0.5) / ${RING_ROWS.count}.0), 0.0).r;
      vec2 slab = cloudsOn > 0.5 ? textureLod(cloudSlab, vec2(x, phi / 6.28318531), 0.0).rg : vec2(0.0);
      float cloudColumn = cloudsOn > 0.5 ? slabColumn(p.y + u.y * s0, p.y + u.y * s1, slab.x - slab.y, slab.x + slab.y, ds) : 0.0;
      vec3 clouds = cloudsOn > 0.5 ? textureLod(cloudTex, vec2(x, phi / 6.28318531), 0.0).r * cloudExt : vec3(0.0);
      tau += face * place * share * column(p.y + u.y * s0, p.y + u.y * s1, h, ds) + clouds * cloudColumn;
    }
    return tau;
  }

  void main() {
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    float depth = -mv.z;
    float dist = length(mv.xyz);
    vec3 light = vec3(0.0);
    float mode = 0.0;
    float side = 0.0;
    if (depth > 0.0) {
      // The area of sky one pixel covers at the point, pc² (flux.ts pixelArea), and the sprite's unit sum.
      side = 1000.0 * depth / pxPerUnit;
      float area = side * side * depth / dist;
      light = flux * gain / (area * spritePx * spritePx * spriteMean);
      if (dustOn > 0.5) light *= exp(-dustTo(position));
      // With its extent (S64, plummer.ts resolvedAt): its whole light, dimmed alike, spread by its own profile.
      if (profile > 0.5 && extent > 0.0 && 2.0 * extent >= side) {
        mode = profile;
        light = flux * gain / area;
        if (dustOn > 0.5) light *= exp(-dustTo(position));
      }
      // As the instrument's image of a point (S67, D227 R1; hstPsf.ts): its whole light, dimmed alike, spread by the PSF.
      if (mode < 0.5 && physOn > 0.5) {
        mode = 3.0;
        light = flux * gain / area;
        if (dustOn > 0.5) light *= exp(-dustTo(position));
      }
    }
    vLight = light;
    vMode = mode;
    gl_PointSize = spritePx;
    gl_Position = projectionMatrix * mv;
    if (mode > 2.5) {
      // The box of whole pixels round the point (plummer.ts profileBox at hstPsf.ts psfHalf), the table's cells per
      // pixel, and each channel's light over the box, by which each pixel's share is divided (hstPsf.ts psfWeights).
      vec2 c = (gl_Position.xy / gl_Position.w * 0.5 + 0.5) * bufferPx;
      float scale = side / psfCellPc;
      float h = clamp(ceil(0.5 * psfCells * psfCellPc / side), 1.0, ${PROFILE_MAX_HALF.toFixed(1)});
      vec2 k0 = floor(c) - h;
      float n = 2.0 * h + 1.0;
      vBox = vec4(k0, n, scale);
      vCentre = c;
      vNorm3 = 1.0 / psfRect((k0 - c) * scale, (k0 + n - c) * scale);
      gl_PointSize = n + 4.0;
    } else if (mode > 0.5) {
      // The box of whole pixels round the point (plummer.ts profileBox), the profile's scale in pixels, and the light
      // over the box, by which each pixel's share is divided (plummer.ts profileWeights).
      vec2 c = (gl_Position.xy / gl_Position.w * 0.5 + 0.5) * bufferPx;
      float scale = mode < 1.5 ? extent / ${PLUMMER_HALF_MASS} / side : extent / side;
      float h = clamp(ceil(mode < 1.5 ? ${PLUMMER_REACH.toFixed(1)} * scale : scale + 1.0), 1.0, ${PROFILE_MAX_HALF.toFixed(1)});
      vec2 k0 = floor(c) - h;
      float n = 2.0 * h + 1.0;
      vBox = vec4(k0, n, scale);
      vCentre = c;
      vNorm = 1.0 / (mode < 1.5 ? plummerRect(k0 - c, k0 + n - c, scale) : discNorm(c, k0, n, scale));
      gl_PointSize = n + 4.0;
    }
  }
`;

const FRAGMENT = /* glsl */ `
  uniform sampler2D sprite;
  varying vec3 vLight;
  varying float vMode;
  varying vec4 vBox;
  varying vec2 vCentre;
  varying float vNorm;
  varying vec3 vNorm3;
  ${PROFILE_GLSL}
  ${PSF_GLSL}
  void main() {
    if (vMode < 0.5) {
      // The instrument's pattern per channel: the sprite's colour times its alpha (psf.ts), unit sum over the sprite.
      vec4 t = texture2D(sprite, gl_PointCoord);
      gl_FragColor = vec4(vLight * t.rgb * t.a, 1.0);
      return;
    }
    if (vMode > 2.5) {
      // The instrument's image (S67): this pixel's share of each channel's light over the box (hstPsf.ts psfWeights).
      vec2 q = floor(gl_FragCoord.xy);
      if (q.x < vBox.x || q.y < vBox.y || q.x >= vBox.x + vBox.z || q.y >= vBox.y + vBox.z) discard;
      gl_FragColor = vec4(vLight * psfRect((q - vCentre) * vBox.w, (q + 1.0 - vCentre) * vBox.w) * vNorm3, 1.0);
      return;
    }
    // The profile (S64): this pixel's share of the light over the box (plummer.ts profileWeights); none outside it.
    vec2 k = floor(gl_FragCoord.xy);
    if (k.x < vBox.x || k.y < vBox.y || k.x >= vBox.x + vBox.z || k.y >= vBox.y + vBox.z) discard;
    float w = vMode < 1.5 ? plummerRect(k - vCentre, k + 1.0 - vCentre, vBox.w) : clamp(vBox.w - length(k + 0.5 - vCentre) + 0.5, 0.0, 1.0);
    gl_FragColor = vec4(vLight * (w * vNorm), 1.0);
  }
`;

/** The points' two shader texts, as the material is built with them: exported for the pin (fluxPoints.test.ts). */
export const FLUX_POINTS_SHADER = { vertex: VERTEX, fragment: FRAGMENT } as const;

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
  /**
   * Each point's extent, pc (S64): a cluster's half-mass radius or a knot's Stromgren radius; with `profile` the point
   * is drawn with it once its diameter fills a pixel (plummer.ts). Without, every point is the sprite.
   */
  extent?: Float32Array | null;
  /** 1 a Plummer sphere (the clusters), 2 a disc (the knots); 0 or absent, the sprite always. */
  profile?: 0 | 1 | 2;
  /**
   * The instrument's image of a point at its physical size (S67, D227 R1; psf.ts physicalPsf): where a template's optics
   * apply, every point the profile does not draw is drawn with it, in place of the sprite. Null: the sprite (R2).
   */
  physical?: PhysicalPsf | null;
}

const BUFFER = new Vector2();

export function FluxPoints({ positions, flux, gain, psf, spriteSize, dust, extent = null, profile = 0, physical = null }: Props) {
  const gl = useThree((s) => s.gl);
  const points = useMemo(() => {
    const geometry = new BufferGeometry();
    geometry.setAttribute("position", new BufferAttribute(positions, 3));
    geometry.setAttribute("flux", new BufferAttribute(flux, 3));
    // No extent: zero for every point, which never switches (the sprite always).
    const extents = extent && extent.length * 3 === flux.length ? extent : new Float32Array(flux.length / 3);
    geometry.setAttribute("extent", new BufferAttribute(extents, 1));
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
        cloudTex: { value: sprite },
        cloudSlab: { value: sprite },
        cloudExt: { value: new Vector3(0, 0, 0) },
        cloudsOn: { value: 0 },
        profile: { value: 0 },
        bufferPx: { value: new Vector2(1, 1) },
        // Bound to the sprite until a table arrives: never read while physOn is 0.
        physOn: { value: 0 },
        psfTable: { value: sprite },
        psfCells: { value: 1 },
        psfCellPc: { value: 1 },
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
  }, [positions, flux, extent]);
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
    uniforms.profile.value = profile;
    (uniforms.bufferPx.value as Vector2).set(buffer.x, buffer.y);
    uniforms.physOn.value = physical ? 1 : 0;
    if (physical) {
      uniforms.psfTable.value = physical.texture;
      uniforms.psfCells.value = physical.cells;
      uniforms.psfCellPc.value = physical.cellPc;
    }
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
    // The clouds' layer (S64): read only with a raster in hand.
    const clouds = dust?.clouds ?? null;
    const slab = dust?.slab ?? null;
    uniforms.cloudsOn.value = clouds && slab ? 1 : 0;
    if (clouds && slab) {
      uniforms.cloudTex.value = clouds;
      uniforms.cloudSlab.value = slab;
      (uniforms.cloudExt.value as Vector3).set(...(dust!.cloudExt ?? [0, 0, 0]));
    }
  });
  return <primitive object={points} />;
}

const DEFAULT_MEAN: [number, number, number] = (() => {
  const m = psfMean();
  return [m, m, m];
})();
