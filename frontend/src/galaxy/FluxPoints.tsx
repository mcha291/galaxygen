import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo } from "react";
import {
  AddEquation,
  AdditiveBlending,
  BufferAttribute,
  BufferGeometry,
  type Camera,
  CustomBlending,
  FloatType,
  HalfFloatType,
  Mesh,
  NearestFilter,
  OneFactor,
  type PerspectiveCamera,
  PlaneGeometry,
  Points,
  Scene,
  ShaderMaterial,
  type Texture,
  Vector2,
  Vector3,
  WebGLRenderTarget,
  ZeroFactor,
} from "three";

import { useContextGeneration } from "./contextLoss";
import { type IllRuntime, illustrativePointsVertex } from "./illustrative";
import { DUST_SEGMENT_STEPS } from "./flux";
import { NOISE_GLSL, NOISE_UNIFORMS } from "./noise.glsl";
import { WING_BLOCK, WING_MAX_HALF, psfClamped } from "./hstPsf";
import { DISC_LOOP_HALF, PLUMMER_HALF_MASS, PLUMMER_REACH, PROFILE_MAX_HALF } from "./plummer";
import { type PhysicalPsf, type SpritePsf, psfMean, psfTexture } from "./psf";
import { RING_ROWS } from "./regimes";
import {
  GOLDEN_ANGLE,
  SPHERE_KERNEL_MAX_HALF,
  SPHERE_LATTICE_PX,
  SPHERE_MAX_PAIRS,
  SPHERE_MIN_PX,
  SPHERE_NORM_LOOP_HALF,
} from "./sphere";

/** The largest sprite's half-side the sphere's loops reach, pixels: the Tuning panel's largest sprite, 25 px. */
const SPRITE_LOOP_HALF = 13;

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
//
// Since S102 (#232; sphere.ts) a knot is its HII region's sphere of `hii_radius` in projection (profile 3): from
// SPHERE_MIN_PX of radius its light is the point's, spread over the chord profile and drawn at each sample as the point
// itself is drawn there (the sprite, or the instrument's image), so the knot's light is the point's; below it, the point.

/** The march's dust, as the points read it: the ring texture, the scattered light's (whose spare channel is the
 * dust's placement), the radial extent they span, and the slab the segment is cut by, kpc. Since S64 (V6) the clouds'
 * raster (null: no clouds drawn) and its slab texture (each texel's clouds' mean height and half-thickness, kpc), and
 * each channel's depth per magnitude of A_V. Since S66 (V7, D226 R7) the march multiplies the diffuse dust's placement
 * per sub-step by the gas fluctuation map and draws the spurs from their table. Since S93 (#174) the points' diffuse
 * dust takes the same gas map, the march's include and tables shared into this shader (`noise`), read as the march's
 * thin screen; the spurs stay the ring's placed column as the textures hold them (their cell means). */
export interface PointDust {
  rings: Texture;
  scatter: Texture;
  rLo: number;
  rHi: number;
  top: number;
  clouds?: Texture | null;
  slab?: Texture | null;
  cloudExt?: readonly [number, number, number];
  /** The extinction strength (S67, D228, the owner's ruling): every depth to a point multiplied by it; 1 when absent. */
  depthScale?: number;
  /** The march material's uniforms (S93, #174): its gas fluctuation tables (GAS_TEXTURES, GAS_SCALARS) and its switch
   * gasFluct, read each frame, so the points' diffuse dust takes the map the march multiplies its own by. */
  noise?: Record<string, { value: unknown }> | null;
}

/** The gas fluctuation map's tables and scalars (noise.glsl.ts), as the march's material names them (S93, #174). */
export const GAS_TEXTURES = ["uGasRing", "uGasWeights", "uGasCells"] as const;
export const GAS_SCALARS = ["uGasSeed", "uGasInvScale", "uGasSense", "uGasEdge0"] as const;

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

// sphere.ts chord, chordCell and tapOffset, line for line (S102, #232): the chord through a uniform sphere, its mean over
// a pixel, and the taps at the profile's radial quantiles in antipodal pairs; and what a point deposits at offset o px
// from it - the sprite over its square as gl_PointCoord reads it (mode 0), or the instrument's image over the pixel,
// cut at the kernel's box of half-side reach + 0.5 px (the box's light is the normaliser, vNorm3).
const SPHERE_GLSL = /* glsl */ `
  float chord(float rho) {
    return sqrt(max(0.0, 1.0 - rho * rho));
  }
  float chordCell(vec2 d, float r) {
    return 0.25 * (chord(length(d + vec2(-0.25, -0.25)) / r) + chord(length(d + vec2(-0.25, 0.25)) / r) +
      chord(length(d + vec2(0.25, -0.25)) / r) + chord(length(d + vec2(0.25, 0.25)) / r));
  }
  vec2 tapOffset(float t, float n) {
    float p = floor(t / 2.0);
    float f = (p + 0.5) / n;
    float rho = sqrt(1.0 - pow(1.0 - f, 2.0 / 3.0));
    float turn = p * ${GOLDEN_ANGLE.toFixed(9)} + mod(t, 2.0) * 3.14159265;
    return rho * vec2(cos(turn), sin(turn));
  }
  vec3 spriteAt(vec2 o) {
    if (abs(o.x) >= 0.5 * spritePx || abs(o.y) >= 0.5 * spritePx) return vec3(0.0);
    vec4 t = textureLod(sprite, vec2(o.x / spritePx + 0.5, 0.5 - o.y / spritePx), 0.0);
    return t.rgb * t.a;
  }
  vec3 imageAt(vec2 o, float reach, float scale) {
    vec2 lo = max(o - 0.5, vec2(-reach - 0.5));
    vec2 hi = min(o + 0.5, vec2(reach + 0.5));
    if (lo.x >= hi.x || lo.y >= hi.y) return vec3(0.0);
    return psfRect(lo * scale, hi * scale);
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
  uniform float dustDepthScale;
  uniform sampler2D cloudTex;
  uniform sampler2D cloudSlab;
  uniform vec3 cloudExt;
  uniform float cloudsOn;
  // The gas fluctuation map on the points' diffuse dust (S93, #174): the march's noise include and its tables, shared
  // from the march's material (PointDust.noise); gasOn is the march's own gasFluct, so the map is read exactly where the
  // march reads it and is 1 (never read) with the layer off.
  uniform float gasOn;
  ${NOISE_UNIFORMS}
  ${NOISE_GLSL}
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
  // The knot as its HII region's sphere (S102, #232; sphere.ts): profile 3, its radius in pixels, its tap pairs, the
  // kernel's reach and nothing; the sprite read here for the closure's scale (sphere.ts knotScale).
  uniform sampler2D sprite;
  varying vec4 vSphere;
  ${SPHERE_GLSL}
  // sphere.ts kernelSum through the sprite: what a point at p deposits over the pixels round it, per channel.
  vec3 spriteSum(vec2 p) {
    float reach = floor(0.5 * spritePx) + 1.0;
    vec3 s = vec3(0.0);
    for (int i = 0; i < ${2 * SPRITE_LOOP_HALF + 1}; i++) {
      if (float(i) > 2.0 * reach) break;
      for (int j = 0; j < ${2 * SPRITE_LOOP_HALF + 1}; j++) {
        if (float(j) > 2.0 * reach) break;
        s += spriteAt(floor(p) + vec2(float(i), float(j)) - reach + 0.5 - p);
      }
    }
    return s;
  }
  // sphere.ts sphereNorm: the chord cells summed over the knot's box, or the profile's integral past the loop's bound.
  float sphereNorm(vec2 c, float r) {
    float h = ceil(r) + 1.0;
    if (h > ${SPHERE_NORM_LOOP_HALF.toFixed(1)}) return 2.0 * 3.14159265 * r * r / 3.0;
    float s = 0.0;
    for (int i = 0; i < ${2 * SPHERE_NORM_LOOP_HALF + 1}; i++) {
      if (float(i) > 2.0 * h) break;
      for (int j = 0; j < ${2 * SPHERE_NORM_LOOP_HALF + 1}; j++) {
        if (float(j) > 2.0 * h) break;
        s += chordCell(floor(c) + vec2(float(i), float(j)) - h + 0.5 - c, r);
      }
    }
    return s;
  }
  // The wings past a clamped box (S82, #178; hstPsf.ts psfWingWeights): wingsOn while any point may be clamped, the wings'
  // pass drawing (wingPass) into the coarse target of wingPx blocks of wingBlock pixels; vWing the wings' box in blocks.
  uniform float wingsOn;
  uniform float wingPass;
  uniform float wingBlock;
  uniform vec2 wingPx;
  varying vec4 vWing;
  // hstPsf.ts wingBox, line for line: the table's half-width in blocks and one more, at most WING_MAX_HALF.
  vec4 wingBox(vec2 c, float side) {
    float hw = clamp(ceil(0.5 * psfCells * psfCellPc / side / wingBlock) + 1.0, 1.0, ${WING_MAX_HALF.toFixed(1)});
    return vec4(floor(c / wingBlock) - hw, 2.0 * hw + 1.0, wingBlock);
  }
  // The wings' pass draws only a point the instrument's image draws whose box is clamped (hstPsf.ts psfClamped).
  bool wingDrawn() {
    float depth = -(modelViewMatrix * vec4(position, 1.0)).z;
    if (depth <= 0.0 || physOn < 0.5) return false;
    float side = 1000.0 * depth / pxPerUnit;
    if (profile > 0.5 && profile < 2.5 && extent > 0.0 && 2.0 * extent >= side) return false;
    if (profile > 2.5 && extent >= ${SPHERE_MIN_PX} * side) return false;
    return ceil(0.5 * psfCells * psfCellPc / side) > ${PROFILE_MAX_HALF.toFixed(1)};
  }
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
    // The gas map as the march's thin screen (S93, #174; FieldVolume's screenGas): read once where the segment crosses
    // the midplane (y = 0) inside [0, sMax], else at the point's own projection, and multiplying the diffuse dust only.
    float gasAt = 1.0;
    if (gasOn > 0.5) {
      float tCross = abs(u.y) > 1e-6 ? -p.y / u.y : -1.0;
      vec3 screen = (tCross >= 0.0 && tCross <= sMax) ? p + u * tCross : p;
      gasAt = layerGasMap(vec2(screen.x, -screen.z));
    }
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
      tau += face * place * gasAt * share * column(p.y + u.y * s0, p.y + u.y * s1, h, ds) + clouds * cloudColumn;
    }
    return tau * dustDepthScale;
  }

  void main() {
    if (wingPass > 0.5 && !wingDrawn()) {
      gl_Position = vec4(2.0, 2.0, 2.0, 1.0);
      gl_PointSize = 1.0;
      return;
    }
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
      if (profile > 0.5 && profile < 2.5 && extent > 0.0 && 2.0 * extent >= side) {
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
      // As its HII region's sphere (S102, #232; sphere.ts): from SPHERE_MIN_PX of radius, the light the point's own path
      // gave it (the sprite's, or the instrument's image's), spread over the chord profile - mode 5 through the sprite,
      // 6 through the image; dimmed by its centre's column, as the point is.
      if (profile > 2.5 && extent >= ${SPHERE_MIN_PX} * side) mode = mode > 2.5 ? 6.0 : 5.0;
    }
    vLight = light;
    vMode = mode;
    gl_PointSize = spritePx;
    gl_Position = projectionMatrix * mv;
    if (mode > 4.5) {
      // The box of whole pixels round the knot: its radius, the kernel's reach and the edge's slack (sphere.ts). The
      // taps' pairs, or the lattice's normaliser; through the image, its box's light per channel (vNorm3); through the
      // sprite, the point's own sum at the centre over the samples' (knotScale), so the knot's light is the point's.
      vec2 c = (gl_Position.xy / gl_Position.w * 0.5 + 0.5) * bufferPx;
      float r = extent / side;
      float scale = side / psfCellPc;
      float reach = mode > 5.5 ? min(ceil(0.5 * psfCells * psfCellPc / side), ${SPHERE_KERNEL_MAX_HALF.toFixed(1)}) : ceil(0.5 * spritePx) - 1.0;
      float pairs = min(${SPHERE_MAX_PAIRS.toFixed(1)}, max(1.0, ceil(2.0 * r * r)));
      float h = min(ceil(r) + reach + 2.0, ${PROFILE_MAX_HALF.toFixed(1)});
      vec2 k0 = floor(c) - h;
      float n = 2.0 * h + 1.0;
      vBox = vec4(k0, n, scale);
      vCentre = c;
      vSphere = vec4(r, pairs, reach, 0.0);
      vNorm = r < ${SPHERE_LATTICE_PX.toFixed(1)} ? 1.0 : 1.0 / sphereNorm(c, r);
      if (mode > 5.5) {
        vNorm3 = 1.0 / psfRect(vec2(-reach - 0.5) * scale, vec2(reach + 0.5) * scale);
      } else {
        vec3 point = spriteSum(c);
        vec3 samples = vec3(0.0);
        if (r < ${SPHERE_LATTICE_PX.toFixed(1)}) {
          for (int t = 0; t < ${2 * SPHERE_MAX_PAIRS}; t++) {
            if (float(t) >= 2.0 * pairs) break;
            samples += spriteSum(c + r * tapOffset(float(t), pairs));
          }
          samples /= 2.0 * pairs;
        } else {
          samples = spriteSum(vec2(0.5));
        }
        vLight *= vec3(samples.r > 0.0 ? point.r / samples.r : 1.0, samples.g > 0.0 ? point.g / samples.g : 1.0, samples.b > 0.0 ? point.b / samples.b : 1.0);
      }
      gl_PointSize = n + 4.0;
    } else if (mode > 2.5) {
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
      // Clamped (S82, #178): the light past the box is the wings' to draw, so each channel is over the wings' box's light
      // (one where it covers the table), not the box's; in the wings' pass the point is that box in the coarse target.
      if (wingsOn > 0.5 && ceil(0.5 * psfCells * psfCellPc / side) > ${PROFILE_MAX_HALF.toFixed(1)}) {
        vWing = wingBox(c, side);
        vNorm3 = 1.0 / psfRect((vWing.xy * vWing.w - c) * scale, ((vWing.xy + vWing.z) * vWing.w - c) * scale);
        if (wingPass > 0.5) {
          vMode = 4.0;
          gl_Position = vec4((vWing.xy + 0.5 * vWing.z) / wingPx * 2.0 - 1.0, 0.0, 1.0);
          gl_PointSize = vWing.z + 2.0;
        }
      }
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
  varying vec4 vWing;
  ${PROFILE_GLSL}
  ${PSF_GLSL}
  // The knot as its HII region's sphere (S102, #232; sphere.ts knotDeposit): the sprite's size, and the sphere's numbers.
  uniform float spritePx;
  varying vec4 vSphere;
  ${SPHERE_GLSL}
  void main() {
    if (vMode > 4.5) {
      // This pixel's light: the point's own deposit at each sample of the chord profile - taps under
      // SPHERE_LATTICE_PX of radius, else the pixel lattice's chord cells over their sum (vNorm) - through the sprite
      // (mode 5) or the instrument's image cut at its box, over the box's light (mode 6, vNorm3).
      vec2 k = floor(gl_FragCoord.xy);
      if (k.x < vBox.x || k.y < vBox.y || k.x >= vBox.x + vBox.z || k.y >= vBox.y + vBox.z) discard;
      bool image = vMode > 5.5;
      float r = vSphere.x;
      float reach = vSphere.z;
      vec3 s = vec3(0.0);
      if (r < ${SPHERE_LATTICE_PX.toFixed(1)}) {
        float m = 2.0 * vSphere.y;
        for (int t = 0; t < ${2 * SPHERE_MAX_PAIRS}; t++) {
          if (float(t) >= m) break;
          vec2 o = k + 0.5 - vCentre - r * tapOffset(float(t), vSphere.y);
          s += image ? imageAt(o, reach, vBox.w) : spriteAt(o);
        }
        s /= m;
      } else {
        for (int i = 0; i < ${2 * SPRITE_LOOP_HALF + 1}; i++) {
          if (float(i) > 2.0 * reach) break;
          for (int j = 0; j < ${2 * SPRITE_LOOP_HALF + 1}; j++) {
            if (float(j) > 2.0 * reach) break;
            vec2 u = vec2(float(i), float(j)) - reach;
            float w = chordCell(k - u + 0.5 - vCentre, r);
            if (w > 0.0) s += w * (image ? imageAt(u, reach, vBox.w) : spriteAt(u));
          }
        }
        s *= vNorm;
      }
      gl_FragColor = vec4(vLight * s * (image ? vNorm3 : vec3(1.0)), 1.0);
      return;
    }
    if (vMode > 3.5) {
      // The wings (S82, #178; hstPsf.ts psfWingWeights): this block's light less its part inside the box, over the wings'
      // box's light; the composite spreads it over the block's pixels.
      vec2 q = floor(gl_FragCoord.xy);
      if (q.x < vWing.x || q.y < vWing.y || q.x >= vWing.x + vWing.z || q.y >= vWing.y + vWing.z) discard;
      vec2 lo = q * vWing.w;
      vec2 hi = lo + vWing.w;
      vec2 a = max(lo, vBox.xy);
      vec2 b = min(hi, vBox.xy + vBox.z);
      vec3 inner = a.x < b.x && a.y < b.y ? psfRect((a - vCentre) * vBox.w, (b - vCentre) * vBox.w) : vec3(0.0);
      gl_FragColor = vec4(vLight * (psfRect((lo - vCentre) * vBox.w, (hi - vCentre) * vBox.w) - inner) * vNorm3, 1.0);
      return;
    }
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

// The wings' composite (S82, #178): a quad over the frame, each pixel its block's light in the coarse target over the
// block's pixels, added to the frame's light (its alpha left as it is) - each block's light spread evenly over it.
const COMPOSITE_VERTEX = /* glsl */ `
  void main() {
    gl_Position = vec4(position.xy, 0.0, 1.0);
  }
`;
const COMPOSITE_FRAGMENT = /* glsl */ `
  uniform sampler2D wingTex;
  uniform float wingBlock;
  void main() {
    ivec2 q = ivec2(floor(gl_FragCoord.xy / wingBlock));
    gl_FragColor = vec4(texelFetch(wingTex, q, 0).rgb / (wingBlock * wingBlock), 0.0);
  }
`;

/** The wings' composite's two shader texts: exported for the pin (fluxPoints.test.ts). */
export const WING_COMPOSITE_SHADER = { vertex: COMPOSITE_VERTEX, fragment: COMPOSITE_FRAGMENT } as const;

const SPHERE_CENTRE = new Vector3();
const EYE = new Vector3();
const FORWARD = new Vector3();

/**
 * Whether any point may be drawn clamped (S82, #178): the nearest the points' bounding sphere comes along the view, at
 * that depth's pixel side (flux.ts pixelArea's), the table's box clamped (hstPsf.ts psfClamped) - a bound, so a frame
 * whose points are all far (every capture but the zoom stands) draws no wings and adds nothing.
 */
export function mayClamp(points: Points, camera: Camera, pxPerUnit: number, physical: Pick<PhysicalPsf, "cells" | "cellPc">): boolean {
  const sphere = points.geometry.boundingSphere;
  if (!sphere || !Number.isFinite(sphere.radius)) return true;
  const centre = SPHERE_CENTRE.copy(sphere.center).applyMatrix4(points.matrixWorld);
  const radius = sphere.radius * points.matrixWorld.getMaxScaleOnAxis();
  camera.getWorldPosition(EYE);
  camera.getWorldDirection(FORWARD);
  const nearest = FORWARD.dot(centre.sub(EYE)) - radius;
  if (!(nearest > 0)) return true;
  return psfClamped(physical, (1000 * nearest) / pxPerUnit);
}

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
   * Each point's extent, pc (S64): a cluster's half-mass radius or a knot's region's radius (`hii_radius` since S102;
   * the Stromgren radius before); with `profile` the point is drawn with it once it reaches its share of a pixel
   * (plummer.ts, sphere.ts). Without, every point is the sprite.
   */
  extent?: Float32Array | null;
  /**
   * 1 a Plummer sphere (the clusters), 2 a disc; 3 an HII region's sphere in projection (the knots since S102, #232;
   * sphere.ts: its chord profile convolved with the point's own sprite or image, from SPHERE_MIN_PX of radius, the
   * extent its `hii_radius`); 0 or absent, the sprite always.
   */
  profile?: 0 | 1 | 2 | 3;
  /**
   * The instrument's image of a point at its physical size (S67, D227 R1; psf.ts physicalPsf): where a template's optics
   * apply, every point the profile does not draw is drawn with it, in place of the sprite. Null: the sprite (R2).
   */
  physical?: PhysicalPsf | null;
  /**
   * The illustrative look (S105, D275; illustrative/index.ts): the vertex shader patched so each point's dust to the camera
   * takes the layer's A_V (illDustAv) as the march does, the layer's uniforms shared in. Null or absent (the physical
   * look): VERTEX as it is, nothing of the layer.
   */
  ill?: IllRuntime | null;
  /**
   * (S108, illustrative/points.ts) Whether these points take the field's edge taper (the layer's points hook): the
   * star-first mode's stars and clusters. Elsewhere (the knots) the hook's share is held at 0 for this material, so they
   * are drawn as before. Read only under the illustrative look.
   */
  illEdged?: boolean;
  /**
   * (S108 J4, illustrative/points.ts illPointsCapped) The brightest this material's points may be (their largest channel,
   * the frame's linear units): the arm grain's (SparkleLayer). Absent or 0, none - every other material's. Read only under
   * the illustrative look.
   */
  illCap?: number;
}

const BUFFER = new Vector2();

export function FluxPoints({ positions, flux, gain, psf, spriteSize, dust, extent = null, profile = 0, physical = null, ill = null, illEdged = false, illCap = 0 }: Props) {
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
        dustDepthScale: { value: 1 },
        cloudTex: { value: sprite },
        cloudSlab: { value: sprite },
        cloudExt: { value: new Vector3(0, 0, 0) },
        cloudsOn: { value: 0 },
        // The gas map (S93, #174): bound to the sprite and 0 until the march's tables arrive; never read while gasOn is 0.
        gasOn: { value: 0 },
        ...Object.fromEntries(GAS_TEXTURES.map((name) => [name, { value: sprite }])),
        ...Object.fromEntries(GAS_SCALARS.map((name) => [name, { value: 0 }])),
        profile: { value: 0 },
        bufferPx: { value: new Vector2(1, 1) },
        // Bound to the sprite until a table arrives: never read while physOn is 0.
        physOn: { value: 0 },
        psfTable: { value: sprite },
        psfCells: { value: 1 },
        psfCellPc: { value: 1 },
        // The wings (S82, #178): off until a frame may clamp a point.
        wingsOn: { value: 0 },
        wingPass: { value: 0 },
        wingBlock: { value: WING_BLOCK },
        wingPx: { value: new Vector2(1, 1) },
        // The illustrative look's (S105): its uniform objects themselves, shared with the march; none under the physical look.
        ...(ill ? ill.uniforms : {}),
        // S108: the points' edge only where these points take it (illEdged); this material's own 0 elsewhere.
        ...(ill && !illEdged ? { illPointsEdge: { value: 0 } } : {}),
        // S108 (J4): the cap this material's own (0 unless the sparkle's), set each frame below.
        ...(ill ? { illPointsCap: { value: 0 } } : {}),
      },
      vertexShader: ill ? illustrativePointsVertex(VERTEX) : VERTEX,
      fragmentShader: FRAGMENT,
      transparent: true,
      blending: AdditiveBlending,
      depthTest: false,
      depthWrite: false,
    });
    const object = new Points(geometry, material);
    object.frustumCulled = false;
    geometry.computeBoundingSphere();
    return object;
  }, [positions, flux, extent, ill, illEdged]);
  useEffect(
    () => () => {
      points.geometry.dispose();
      (points.material as ShaderMaterial).dispose();
    },
    [points],
  );
  // Whether the wings' target can be a blended float32 target: EXT_float_blend, which the viewer enables itself and so must
  // enable again after a lost context is restored (T13, S83) - three re-enables only the extensions it asks for. The
  // target itself is made again by three when next bound, and drawn every frame the wings are on.
  const generation = useContextGeneration(gl.domElement);
  const floatBlend = useMemo(() => gl.extensions.has("EXT_float_blend"), [gl, generation]); // eslint-disable-line react-hooks/exhaustive-deps -- asked again per context
  // The wings' pass (S82, #178): the same points and shader, the uniforms shared but wingPass, drawn into a coarse target
  // of WING_BLOCK-pixel blocks before the frame, and the composite that adds the target to the frame.
  const wings = useMemo(() => {
    const main = points.material as ShaderMaterial;
    const material = new ShaderMaterial({
      uniforms: { ...main.uniforms, wingPass: { value: 1 } },
      vertexShader: ill ? illustrativePointsVertex(VERTEX) : VERTEX,
      fragmentShader: FRAGMENT,
      transparent: true,
      blending: AdditiveBlending,
      depthTest: false,
      depthWrite: false,
    });
    const object = new Points(points.geometry, material);
    object.frustumCulled = false;
    object.matrixAutoUpdate = false;
    const scene = new Scene();
    scene.add(object);
    const type = floatBlend ? FloatType : HalfFloatType;
    const target = new WebGLRenderTarget(1, 1, { type, depthBuffer: false, minFilter: NearestFilter, magFilter: NearestFilter });
    const composite = new Mesh(
      new PlaneGeometry(2, 2),
      new ShaderMaterial({
        uniforms: { wingTex: { value: target.texture }, wingBlock: { value: WING_BLOCK } },
        vertexShader: COMPOSITE_VERTEX,
        fragmentShader: COMPOSITE_FRAGMENT,
        transparent: true,
        depthTest: false,
        depthWrite: false,
        blending: CustomBlending,
        blendEquation: AddEquation,
        blendSrc: OneFactor,
        blendDst: OneFactor,
        blendSrcAlpha: ZeroFactor,
        blendDstAlpha: OneFactor,
      }),
    );
    composite.frustumCulled = false;
    composite.visible = false;
    return { material, object, scene, target, composite };
  }, [points, floatBlend]); // eslint-disable-line react-hooks/exhaustive-deps -- the runtime is the points' (a new one makes new points)
  useEffect(
    () => () => {
      wings.material.dispose();
      wings.target.dispose();
      wings.composite.geometry.dispose();
      (wings.composite.material as ShaderMaterial).dispose();
    },
    [wings],
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
    if (uniforms.illPointsCap) uniforms.illPointsCap.value = illCap;
    const mean = psf?.mean ?? DEFAULT_MEAN;
    (uniforms.spriteMean.value as Vector3).set(mean[0], mean[1], mean[2]);
    uniforms.sprite.value = psf?.texture ?? psfTexture();
    uniforms.dustOn.value = dust ? 1 : 0;
    uniforms.dustDepthScale.value = dust?.depthScale ?? 1;
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
    // The gas map (S93, #174): the march's own tables and switch, copied each frame from its material's uniforms.
    const noise = dust?.noise ?? null;
    uniforms.gasOn.value = noise ? Number(noise.gasFluct?.value ?? 0) : 0;
    if (noise) for (const name of [...GAS_TEXTURES, ...GAS_SCALARS]) if (noise[name]) uniforms[name].value = noise[name].value;
    if (clouds && slab) {
      uniforms.cloudTex.value = clouds;
      uniforms.cloudSlab.value = slab;
      (uniforms.cloudExt.value as Vector3).set(...(dust!.cloudExt ?? [0, 0, 0]));
    } else if (ill && dust) {
      // The illustrative look's A_V reddens through the same depths per magnitude with no clouds' raster in hand (S105).
      (uniforms.cloudExt.value as Vector3).set(...(dust.cloudExt ?? [0, 0, 0]));
    }
    // The wings (S82, #178): only while a point may be clamped; else the frame is drawn as before, nothing added.
    const drawWings = physical !== null && mayClamp(points, camera, uniforms.pxPerUnit.value as number, physical);
    uniforms.wingsOn.value = drawWings ? 1 : 0;
    wings.composite.visible = drawWings;
    if (drawWings) {
      const w = Math.ceil(buffer.x / WING_BLOCK);
      const h = Math.ceil(buffer.y / WING_BLOCK);
      if (wings.target.width !== w || wings.target.height !== h) wings.target.setSize(w, h);
      (uniforms.wingPx.value as Vector2).set(w, h);
      wings.object.matrix.copy(points.matrixWorld);
      wings.object.matrixWorldNeedsUpdate = true;
      const before = gl.getRenderTarget();
      gl.setRenderTarget(wings.target);
      gl.clear(true, false, false);
      gl.render(wings.scene, camera);
      gl.setRenderTarget(before);
    }
  });
  return (
    <>
      <primitive object={points} />
      <primitive object={wings.composite} />
    </>
  );
}

const DEFAULT_MEAN: [number, number, number] = (() => {
  const m = psfMean();
  return [m, m, m];
})();
