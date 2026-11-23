// The pink HII regions' drawing (S106, BUILD_VIII row 106; knots.ts is the feature, knotsMath.ts the arithmetic). One
// point per region of the field mode's knots (GalaxyTab's knotPoints: the model's places, their own lines' light, their
// hii_radius), drawn as a soft irregular nebula - up to four Gaussian sub-blobs from the region's index hash and a
// white-blue core - at a radius of its own clamped to a floor and a ceiling, additive into the HDR scene before the
// bloom and the grade. Its light is on the field's scale (the knots' gain, so the exposure and the field's weight move
// it), deposited as a total over the pixel area at the region (as FluxPoints' points are) and dimmed by the march's dust
// along the segment to the camera (FluxPoints' dustTo, line for line but the gas map, with the layer's own A_V). The arm
// weight reads the dust's placement (the scatter texture's alpha: the gas's own contrast, D210) at the region's place.
//
// No JSX and no @react-three/fiber import: the registry is imported by the e2e tools (tuning.ts), so this file keeps to
// react and three. The per-frame uniforms are written in the points' onBeforeRender (the renderer and the camera are
// handed there). Buffers are rebuilt only when the knots or a parameter that shapes them change; nothing per frame.

import { createElement, useEffect, useMemo, useRef } from "react";
import {
  AdditiveBlending,
  AddEquation,
  BufferAttribute,
  BufferGeometry,
  type Camera,
  CustomBlending,
  DataTexture,
  type PerspectiveCamera,
  Points,
  RGBAFormat,
  OneFactor,
  OneMinusSrcAlphaFactor,
  ShaderMaterial,
  type Texture,
  UnsignedByteType,
  Vector2,
  Vector3,
  type WebGLRenderer,
} from "three";

import { DUST_SEGMENT_STEPS } from "../flux";
import { RING_ROWS } from "../regimes";
import { type IllLayerProps, illMeasure, illNow } from "./feature";
import { type Placement, regionAttributes } from "./knotsMath";
import { modelLightRef, placeOnSkeleton, regionsSkeleton, skeletonAttributes } from "./knotsPlace";

const vertexShader = (illGlsl: string) => /* glsl */ `
  attribute vec3 aLight;
  attribute vec3 aCore;
  attribute float aRadius;
  attribute vec4 aB0;
  attribute vec4 aB1;
  attribute vec4 aB2;
  attribute vec4 aB3;
  uniform float pxPerUnit;
  uniform float gain;
  uniform float coreGain;
  uniform float coreSize;
  uniform float dustStrength;
  uniform float maxPoint;
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
  varying vec3 vLight;
  varying vec3 vCore;
  varying float vRpx;
  varying float vHalf;
  varying float vCoreSigma;
  varying vec4 vB0;
  varying vec4 vB1;
  varying vec4 vB2;
  varying vec4 vB3;
${illGlsl}
  float sech2(float x) { float c = cosh(clamp(x, -30.0, 30.0)); return 1.0 / (c * c); }
  float safeTanh(float x) { return tanh(clamp(x, -10.0, 10.0)); }
  float column(float y0, float y1, float h, float ds) {
    if (h <= 0.0) return 0.0;
    float dy = y1 - y0;
    if (abs(dy) < 1e-4 * h) return sech2(0.5 * (y0 + y1) / (2.0 * h)) / (4.0 * h) * ds;
    return abs(safeTanh(y1 / (2.0 * h)) - safeTanh(y0 / (2.0 * h))) * 0.5 * ds / abs(dy);
  }
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
  // FluxPoints' dustTo (flux.ts dustToPoint) without the gas map, with the illustrative layer's A_V (illDustAv).
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
      float share = textureLod(rings, vec2(x, (${RING_ROWS.share}.0 + 0.5) / ${RING_ROWS.count}.0), 0.0).r;
      vec2 slab = cloudsOn > 0.5 ? textureLod(cloudSlab, vec2(x, phi / 6.28318531), 0.0).rg : vec2(0.0);
      float cloudColumn = cloudsOn > 0.5 ? slabColumn(p.y + u.y * s0, p.y + u.y * s1, slab.x - slab.y, slab.x + slab.y, ds) : 0.0;
      vec3 clouds = cloudsOn > 0.5 ? textureLod(cloudTex, vec2(x, phi / 6.28318531), 0.0).r * cloudExt : vec3(0.0);
      tau += face * place * share * column(p.y + u.y * s0, p.y + u.y * s1, h, ds) + clouds * cloudColumn;
      tau += illDustAv(vec2(r, phi)) * cloudExt * column(p.y + u.y * s0, p.y + u.y * s1, h, ds);
    }
    return tau * dustDepthScale;
  }
  float blobReach(vec4 b, float rpx) { return b.w > 0.0 ? length(b.xy) * rpx + 3.0 * max(b.z * rpx, 0.6) : 0.0; }
  void main() {
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    float depth = -mv.z;
    float dist = length(mv.xyz);
    gl_Position = vec4(2.0, 2.0, 2.0, 1.0);
    gl_PointSize = 1.0;
    vLight = vec3(0.0);
    vCore = vec3(0.0);
    if (depth <= 0.0) return;
    // The arm weight and the radial fade are in aLight and aCore already (regionAttributes, on the CPU).
    float side = 1000.0 * depth / pxPerUnit;
    float area = side * side * depth / dist;
    // The field's edge taper (edge.ts, the march's illEdge), so the regions end where the field's light does.
    vec3 ext = (dustOn > 0.5 ? exp(-dustTo(position) * dustStrength) : vec3(1.0)) * illEdge(length(position.xz));
    vLight = aLight * gain / area * ext;
    vCore = aCore * gain * coreGain / area * ext;
    float rpx = aRadius / side;
    vRpx = rpx;
    vCoreSigma = max(coreSize * rpx, 0.6);
    float reach = max(max(blobReach(aB0, rpx), blobReach(aB1, rpx)), max(blobReach(aB2, rpx), blobReach(aB3, rpx)));
    reach = max(reach, 3.0 * vCoreSigma);
    float size = min(2.0 * reach + 1.0, maxPoint);
    vHalf = 0.5 * size;
    vB0 = aB0; vB1 = aB1; vB2 = aB2; vB3 = aB3;
    gl_Position = projectionMatrix * mv;
    gl_PointSize = size;
  }
`;

const FRAGMENT = /* glsl */ `
  varying vec3 vLight;
  varying vec3 vCore;
  varying float vRpx;
  varying float vHalf;
  varying float vCoreSigma;
  varying vec4 vB0;
  varying vec4 vB1;
  varying vec4 vB2;
  varying vec4 vB3;
  // A unit Gaussian's value at offset o px (sigma s px): its light over the pixels sums to about 1.
  float gauss(vec2 o, float s) { return exp(-dot(o, o) / (2.0 * s * s)) / (6.28318531 * s * s); }
  float blob(vec2 p, vec4 b) { return b.w > 0.0 ? b.w * gauss(p - b.xy * vRpx, max(b.z * vRpx, 0.6)) : 0.0; }
  void main() {
    vec2 p = (gl_PointCoord - 0.5) * (2.0 * vHalf);
    float s = blob(p, vB0) + blob(p, vB1) + blob(p, vB2) + blob(p, vB3);
    vec3 light = vLight * s + vCore * gauss(p, vCoreSigma);
    gl_FragColor = vec4(light, 1.0);
  }
`;

/**
 * The skeleton regions' vertex shader (knots.ts `place` = 1; knotsPlace.ts): the knots' own preamble (attributes,
 * uniforms, dustTo) and a main of its own. The lobes are laid in the arm's frame - along the arm's tangent (aDir, scene)
 * and across it, both projected to the screen at the region (so they lie in the disc's plane, foreshortened as it is)
 * - and each lobe carries a hue share (aTint) between the redder colour (aLight) and the more magenta (aLight2).
 * The legacy shader above is left as it is, byte for byte (the model's places, ngc_4414).
 */
const skeletonVertexShader = (illGlsl: string) => {
  const legacy = vertexShader(illGlsl);
  const preamble = legacy.slice(0, legacy.indexOf("  float blobReach("));
  return `${preamble}
  attribute vec3 aLight2;
  attribute vec3 aDir;
  attribute vec4 aTint;
  uniform vec2 viewPx;
  varying vec3 vLight2;
  varying vec4 vTint;
  varying vec2 vSeed;
  vec2 toPx(vec4 clip) { return clip.xy / clip.w * 0.5 * viewPx; }
  vec4 lobe(vec4 b, vec2 pT, vec2 pN, float rpx) { return vec4(b.x * pT + b.y * pN, max(b.z * rpx, 0.6), b.w); }
  float lobeReach(vec4 c) { return c.w > 0.0 ? length(c.xy) + 3.0 * c.z : 0.0; }
  void main() {
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    float depth = -mv.z;
    float dist = length(mv.xyz);
    gl_Position = vec4(2.0, 2.0, 2.0, 1.0);
    gl_PointSize = 1.0;
    vLight = vec3(0.0);
    vLight2 = vec3(0.0);
    vCore = vec3(0.0);
    if (depth <= 0.0) return;
    float side = 1000.0 * depth / pxPerUnit;
    float area = side * side * depth / dist;
    vec3 ext = (dustOn > 0.5 ? exp(-dustTo(position) * dustStrength) : vec3(1.0)) * illEdge(length(position.xz));
    vLight = aLight * gain / area * ext;
    vLight2 = aLight2 * gain / area * ext;
    vCore = aCore * gain * coreGain / area * ext;
    float rpx = aRadius / side;
    vRpx = rpx;
    vCoreSigma = max(coreSize * rpx, 0.6);
    // The arm's frame on the screen: one region radius along the tangent and across it, in px.
    vec4 clip = projectionMatrix * mv;
    vec2 c0 = toPx(clip);
    vec3 nrm = vec3(-aDir.z, 0.0, aDir.x);
    float kpc = aRadius / 1000.0;
    vec2 pT = toPx(projectionMatrix * (modelViewMatrix * vec4(position + aDir * kpc, 1.0))) - c0;
    vec2 pN = toPx(projectionMatrix * (modelViewMatrix * vec4(position + nrm * kpc, 1.0))) - c0;
    vB0 = lobe(aB0, pT, pN, rpx); vB1 = lobe(aB1, pT, pN, rpx); vB2 = lobe(aB2, pT, pN, rpx); vB3 = lobe(aB3, pT, pN, rpx);
    vTint = aTint;
    vSeed = vec2(fract(position.x * 7.31 + position.z * 3.17), fract(position.z * 5.83 - position.x * 2.29)) * 97.0;
    float reach = max(max(lobeReach(vB0), lobeReach(vB1)), max(lobeReach(vB2), lobeReach(vB3)));
    reach = max(reach, 3.0 * vCoreSigma);
    float size = min(2.0 * reach + 1.0, maxPoint);
    vHalf = 0.5 * size;
    gl_Position = clip;
    gl_PointSize = size;
  }
`;
};

const SKELETON_FRAGMENT = /* glsl */ `
  varying vec3 vLight;
  varying vec3 vLight2;
  varying vec3 vCore;
  varying float vRpx;
  varying float vHalf;
  varying float vCoreSigma;
  varying vec4 vB0;
  varying vec4 vB1;
  varying vec4 vB2;
  varying vec4 vB3;
  varying vec4 vTint;
  varying vec2 vSeed;
  uniform float knRag;
  uniform float knVeil;
  float gauss(vec2 o, float s) { return exp(-dot(o, o) / (2.0 * s * s)) / (6.28318531 * s * s); }
  // A lobe already in px (centre xy, sigma z, weight w), y up.
  float lobe(vec2 p, vec4 b) { return b.w > 0.0 ? b.w * gauss(p - b.xy, b.z) : 0.0; }
  // S107 (MW2): a fixed value noise in the region's own radii, for the lobes' ragged outlines and wisps (knots.ragged).
  float knHash(vec2 c) { return fract(sin(dot(c, vec2(127.1, 311.7))) * 43758.5453); }
  float knNoise(vec2 x) {
    vec2 i = floor(x);
    vec2 f = fract(x);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(knHash(i), knHash(i + vec2(1.0, 0.0)), f.x), mix(knHash(i + vec2(0.0, 1.0)), knHash(i + vec2(1.0, 1.0)), f.x), f.y);
  }
  void main() {
    vec2 p = (gl_PointCoord - 0.5) * (2.0 * vHalf);
    p.y = -p.y;
    // S107 (MW2, knots.ragged): the lobes read at a point displaced by a fixed noise (ragged, lobed outlines; up to
    // half a region radius at 1) and their light broken by a finer one (wisps and holes).
    vec2 pw = p;
    float mottle = 1.0;
    if (knRag > 0.0) {
      vec2 q = p / max(vRpx, 0.5);
      vec2 warp = vec2(knNoise(q * 1.8 + vSeed), knNoise(q * 1.8 + vSeed.yx + 31.7)) - 0.5;
      warp += 0.5 * (vec2(knNoise(q * 4.1 + vSeed * 1.3), knNoise(q * 4.1 + vSeed.yx * 1.3 + 7.1)) - 0.5);
      pw = p + warp * knRag * vRpx;
      float n = 0.6 * knNoise(q * 6.0 + vSeed.yx) + 0.4 * knNoise(q * 13.0 + vSeed * 1.7);
      mottle = max(0.0, 1.0 + min(1.0, knRag) * (2.2 * n - 1.1));
    }
    vec4 s = vec4(lobe(pw, vB0), lobe(pw, vB1), lobe(pw, vB2), lobe(pw, vB3)) * mottle;
    float all4 = s.x + s.y + s.z + s.w;
    float tinted = dot(s, vTint);
    vec3 light = vLight * (all4 - tinted) + vLight2 * tinted + vCore * gauss(p, vCoreSigma);
    // S107 (MW3, knots.veil): the region's own cloud hides this share of the light behind it (premultiplied: the
    // blending is ONE, ONE_MINUS_SRC_ALPHA), each lobe's unnormalised Gaussian at its weight's share of the largest,
    // ragged as the light is - so the pink stands on a dimmed ground and keeps a deep red-magenta through the grade
    // instead of a pastel pink over the arms' blue-white. 0: the plain additive light.
    float cover = 0.0;
    if (knVeil > 0.0) {
      vec4 w = vec4(vB0.w, vB1.w, vB2.w, vB3.w);
      float wMax = max(max(w.x, w.y), max(w.z, w.w));
      vec4 bz = max(vec4(vB0.z, vB1.z, vB2.z, vB3.z), vec4(1e-3));
      vec4 d2 = vec4(dot(pw - vB0.xy, pw - vB0.xy), dot(pw - vB1.xy, pw - vB1.xy), dot(pw - vB2.xy, pw - vB2.xy), dot(pw - vB3.xy, pw - vB3.xy));
      vec4 e = exp(-d2 / (2.0 * bz * bz)) * w / max(wMax, 1e-6);
      cover = clamp(knVeil * max(max(e.x, e.y), max(e.z, e.w)) * min(mottle, 1.0), 0.0, 1.0);
    }
    gl_FragColor = vec4(light, cover);
  }
`;

/** FluxPoints' PointDust as this layer reads it (restated: FluxPoints is a .tsx the e2e tools cannot compile). */
interface PointDust {
  rings: Texture;
  scatter: Texture;
  rLo: number;
  rHi: number;
  top: number;
  clouds?: Texture | null;
  slab?: Texture | null;
  cloudExt?: readonly [number, number, number];
  depthScale?: number;
}

const BUFFER = new Vector2();
let maxPointSize = 0;

/** The material's stand-in texture before the march's own arrive: one RGBA texel of zero bytes (S105 fix R2). */
export function knotsBlank(): DataTexture {
  const blank = new DataTexture(new Uint8Array(4), 1, 1, RGBAFormat, UnsignedByteType);
  blank.needsUpdate = true;
  return blank;
}

/** The material and its stand-in texture released together (S105 fix R2). */
export function disposeKnotsMaterial(material: ShaderMaterial): void {
  (material.userData.blank as DataTexture | undefined)?.dispose();
  material.dispose();
}

/** The pink HII regions, drawn in the Galaxy view's canvas under the illustrative look (knots.ts's `layer`). */
export function KnotsLayer({ params, runtime, knots, knotsGain, dust, context }: IllLayerProps) {
  const drawn = (params.draw ?? 1) >= 0.5 && knots !== null;
  // S106 (K): the regions laid on the arm skeleton (knotsPlace.ts) in place of the model's places; its own shaders.
  const onSkeleton = (params.place ?? 0) >= 0.5;
  // The material: one per runtime (its GLSL and shared uniforms) and placement.
  const material = useMemo(() => {
    // S105 fix R2: one texel of zeros as bytes - a DataTexture's default type is UnsignedByteType, which a Float32Array
    // is not (WebGL refused the upload) - released with the material.
    const blank = knotsBlank();
    return new ShaderMaterial({
      userData: { blank },
      uniforms: {
        pxPerUnit: { value: 1 },
        gain: { value: 0 },
        coreGain: { value: 0 },
        coreSize: { value: 0.1 },
        dustStrength: { value: 1 },
        maxPoint: { value: 64 },
        rings: { value: blank as Texture },
        scatter: { value: blank as Texture },
        rLo: { value: 0 },
        rHi: { value: 1 },
        dustTop: { value: 0 },
        dustOn: { value: 0 },
        dustDepthScale: { value: 1 },
        cloudTex: { value: blank as Texture },
        cloudSlab: { value: blank as Texture },
        cloudExt: { value: new Vector3(0, 0, 0) },
        cloudsOn: { value: 0 },
        viewPx: { value: new Vector2(1, 1) },
        knRag: { value: 0 },
        knVeil: { value: 0 },
        ...runtime.uniforms,
      },
      vertexShader: onSkeleton ? skeletonVertexShader(runtime.glsl) : vertexShader(runtime.glsl),
      fragmentShader: onSkeleton ? SKELETON_FRAGMENT : FRAGMENT,
      transparent: true,
      // S107 (MW3): the skeleton's regions premultiplied (their alpha the veil's cover; 0 adds as AdditiveBlending
      // does); the model's places (ngc_4414) additive as they were.
      ...(onSkeleton
        ? { blending: CustomBlending, blendEquation: AddEquation, blendSrc: OneFactor, blendDst: OneMinusSrcAlphaFactor, blendSrcAlpha: OneFactor, blendDstAlpha: OneMinusSrcAlphaFactor }
        : { blending: AdditiveBlending }),
      depthTest: false,
      depthWrite: false,
    });
  }, [runtime, onSkeleton]);
  useEffect(() => () => disposeKnotsMaterial(material), [material]);

  // The arm weight's grid: the march's placement texture as the CPU holds it (a DataTexture's data), once per texture.
  const scatter = (dust as PointDust | null)?.scatter ?? null;
  const rLo = (dust as PointDust | null)?.rLo ?? 0;
  const rHi = (dust as PointDust | null)?.rHi ?? 0;
  const placement = useMemo((): Placement | null => {
    const image = (scatter as DataTexture | null)?.image as { data?: ArrayLike<number>; width?: number; height?: number } | undefined;
    if (!image?.data || !image.width || !image.height || !(rHi > rLo)) return null;
    return { data: image.data, width: image.width, height: image.height, rLo, rHi };
  }, [scatter, rLo, rHi]);

  // The buffers: rebuilt when the knots, the placement or a parameter that shapes them moves (never per frame).
  const shaping = [
    params.count, params.lumPower, params.pink, params.magenta, params.coreShare, params.size, params.sizeMin, params.sizeMax, params.blobs,
    params.irregular, params.soft, params.armPower, params.armLevel, params.armFlat, params.fadeR, params.fadeWidth, params.innerR,
  ];
  // The skeleton's placement: the regions laid afresh when the skeleton (its key) or a placing parameter moves.
  const skelStarted = illNow();
  const { skeleton, key: skelKey } = onSkeleton ? regionsSkeleton(context) : { skeleton: null, key: "" };
  illMeasure("knots skeleton", skelStarted);
  const placing = [
    params.total, params.bunch, params.gap, params.bunchLen, params.inner, params.across, params.slope, params.lightSize, params.ridgePow,
    params.barEnds, params.sparkle, params.sparkleGain, params.seed, params.elong, params.hue, params.coreBlue,
    params.minStrength, params.patchPow, params.complexes, params.complexGain,
    params.spurCrest, params.complexMembers, params.complexSpread, params.satellites, params.halo, params.haloSize,
  ];
  const geometry = useMemo(() => {
    if (!knots) return null;
    if (onSkeleton) {
      if (!skeleton) return null;
      const started = illNow();
      const a = skeletonAttributes(placeOnSkeleton(skeleton, params), params, modelLightRef(knots.flux));
      illMeasure("knots", started);
      const g = new BufferGeometry();
      g.setAttribute("position", new BufferAttribute(a.positions, 3));
      g.setAttribute("aLight", new BufferAttribute(a.light, 3));
      g.setAttribute("aLight2", new BufferAttribute(a.light2, 3));
      g.setAttribute("aCore", new BufferAttribute(a.core, 3));
      g.setAttribute("aRadius", new BufferAttribute(a.radius, 1));
      g.setAttribute("aDir", new BufferAttribute(a.dir, 3));
      g.setAttribute("aTint", new BufferAttribute(a.tint, 4));
      a.blobs.forEach((b, j) => g.setAttribute(`aB${j}`, new BufferAttribute(b, 4)));
      return g;
    }
    const a = regionAttributes(knots, params, placement);
    const g = new BufferGeometry();
    g.setAttribute("position", new BufferAttribute(a.positions, 3));
    g.setAttribute("aLight", new BufferAttribute(a.light, 3));
    g.setAttribute("aCore", new BufferAttribute(a.core, 3));
    g.setAttribute("aRadius", new BufferAttribute(a.radius, 1));
    a.blobs.forEach((b, j) => g.setAttribute(`aB${j}`, new BufferAttribute(b, 4)));
    return g;
  }, [knots, placement, onSkeleton, skeleton, skelKey, ...shaping, ...(onSkeleton ? placing : [])]); // eslint-disable-line react-hooks/exhaustive-deps -- the shaping parameters, listed
  useEffect(() => () => geometry?.dispose(), [geometry]);

  const points = useMemo(() => {
    if (!geometry) return null;
    const object = new Points(geometry, material);
    object.frustumCulled = false;
    return object;
  }, [geometry, material]);

  // The per-frame values, read by the points' onBeforeRender from the latest props.
  const live = useRef({ params, knotsGain, dust: dust as PointDust | null });
  live.current = { params, knotsGain, dust: dust as PointDust | null };
  useEffect(() => {
    if (!points) return;
    points.onBeforeRender = (renderer: WebGLRenderer, _scene, camera: Camera) => {
      const u = material.uniforms;
      const { params: p, knotsGain: g, dust: d } = live.current;
      const buffer = renderer.getDrawingBufferSize(BUFFER);
      const fov = (camera as PerspectiveCamera).fov ?? 45;
      u.pxPerUnit.value = buffer.y / (2 * Math.tan((fov * Math.PI) / 360));
      (u.viewPx.value as Vector2).set(buffer.x, buffer.y);
      if (maxPointSize === 0) {
        const gl = renderer.getContext();
        const range = gl.getParameter(gl.ALIASED_POINT_SIZE_RANGE) as Float32Array | null;
        maxPointSize = range ? Math.max(1, range[1]) : 64;
      }
      u.maxPoint.value = Math.min(maxPointSize, 1024);
      u.gain.value = g * (p.gain ?? 1);
      u.coreGain.value = p.coreGain ?? 0.5;
      u.coreSize.value = p.coreSize ?? 0.12;
      u.knRag.value = p.ragged ?? 0;
      u.knVeil.value = Math.min(1, Math.max(0, p.veil ?? 0));
      u.dustStrength.value = p.dust ?? 1;
      u.dustOn.value = d && (p.dust ?? 1) > 0 ? 1 : 0;
      u.dustDepthScale.value = d?.depthScale ?? 1;
      if (d) {
        u.rings.value = d.rings;
        u.scatter.value = d.scatter;
        u.rLo.value = d.rLo;
        u.rHi.value = d.rHi;
        u.dustTop.value = d.top;
        const e = d.cloudExt ?? [0, 0, 0];
        (u.cloudExt.value as Vector3).set(e[0], e[1], e[2]);
      }
      const clouds = d?.clouds ?? null;
      const slab = d?.slab ?? null;
      u.cloudsOn.value = clouds && slab ? 1 : 0;
      if (clouds && slab) {
        u.cloudTex.value = clouds;
        u.cloudSlab.value = slab;
      }
    };
  }, [points, material]);

  if (!drawn || !points) return null;
  return createElement("primitive", { object: points });
}
