import { paintOf } from "@interface/ramp.js";
import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo } from "react";
import {
  AdditiveBlending,
  BackSide,
  BoxGeometry,
  ClampToEdgeWrapping,
  DataTexture,
  FloatType,
  HalfFloatType,
  LinearFilter,
  Matrix4,
  Mesh,
  PlaneGeometry,
  RGBAFormat,
  RepeatWrapping,
  Scene,
  ShaderMaterial,
  Vector2,
  Vector3,
  WebGLRenderTarget,
} from "three";

import { type FieldsPayload, type Frame, type Query, loadArrays } from "../api";
import { useLoad } from "../useLoad";
import { srgbToLinear } from "./colors";
import { CLUMPS, HII_RGB, LATTICE_LIFT, YOUNG_KELVIN, planeTexture } from "./regimes";

/**
 * How bright 1 L☉/pc² draws at zero exposure stops, against a star point's 1 per 100 L☉.
 * A display balance between the layers, not a physical constant: a point is one star and
 * the field is a disc of them.
 */
export const LIGHT_PER_LSUN_PC2 = 1 / 400;

/**
 * Extinction in the red, green and blue channels per magnitude of A_V: the R, V and B bands
 * of Cardelli, Clayton & Mathis at R_V = 3.1 standing in for the three channels
 * `[recall: CCM 1989, A_R/A_V = 0.748, A_B/A_V = 1.324]`. Dust dims blue more than red, so a
 * dusty region reddens as it darkens: occlusion, never an added colour (R4).
 */
export const CHANNEL_EXTINCTION = [0.748, 1.0, 1.324] as const;

/**
 * The young light's and the dust's scale heights, as shares of the thin disc's. The same share:
 * light mixed through thick dust glows at their ratio, so a young layer thinner than its dust
 * draws a bright line down the middle of an edge-on dust lane.
 */
export const YOUNG_HEIGHT = 1 / 3;
export const DUST_HEIGHT = 1 / 3;

/** Ray-march steps through the galaxy's bounding box. */
const STEPS = 96;
/**
 * The most pixels the field is marched at, whatever the screen: the image is stretched onto the
 * canvas, and the field is smooth, so this loses nothing to see. The work per frame has to be
 * bounded by a number, not by the display. Marching every pixel of a 4K screen the galaxy fills,
 * at a device pixel ratio of 2, is a billion shader iterations a frame; that outlasts Windows'
 * two-second GPU watchdog, the driver resets, and the browser does not come back.
 */
const PIXEL_BUDGET = 400_000;
/** And never more than half the drawing buffer's resolution on a side. */
const MAX_RESOLUTION = 0.5;

// A screen-covering triangle pair that lays the marched image over the view, added as light.
const COMPOSITE_VERTEX = /* glsl */ `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = vec4(position.xy, 0.0, 1.0);
  }
`;
const COMPOSITE_FRAGMENT = /* glsl */ `
  uniform sampler2D field;
  varying vec2 vUv;
  void main() {
    gl_FragColor = vec4(texture2D(field, vUv).rgb, 1.0);
  }
`;

const FIELDS = ["disc_surface_brightness", "disc_light_temperature", "pattern_density_contrast", "dust_extinction_v", "halpha_surface_brightness"];
const SCALARS = ["thin_disc_scale_height", "bulge_luminosity", "bulge_light_temperature", "bulge_scale_radius", "pitch_angle", "arm_multiplicity"];

const VERTEX = /* glsl */ `
  varying vec3 vWorld;
  void main() {
    vec4 world = modelMatrix * vec4(position, 1.0);
    vWorld = world.xyz;
    gl_Position = projectionMatrix * viewMatrix * world;
  }
`;

// Emission and absorption along the line of sight, front to back. At each step the light
// emitted there is added, dimmed by all the dust between it and the camera and by the step's
// own dust mixed through it, and the step's dust dims everything behind it. Units: the plane
// textures are L☉/pc² through a face-on column and the sech² profiles integrate to 1 per kpc of
// height, so their product times the step in kpc is L☉/pc²; the bulge is L☉ times a Hernquist
// density per kpc³, times the step, per 10⁶ pc² per kpc².
//
// Two layers. The old disc fills the thin disc's height and is smooth, so a point per step
// serves. The young light, its line and the dust sit in layers a few times thinner, where the
// clumps are: sampling those at a point per step both misses them (a step is wider than the
// layer) and, through a tilted disc, smears each clump across every position the ray passes
// over while inside the thicker height. So each step takes the layer's exact column over its
// own height range, a difference of tanh, and reads the layer where the ray is nearest the
// midplane.
//
// The clumps are drawn here, per sample, not baked into the layer texture: a clump near the
// centre is smaller than a texel, and an HII knot is a texel at most anywhere. The noise is
// regimes.ts's clumpNoise and clumpFactors line for line (the hash in uint arithmetic, where
// Math.imul wraps the same), and `norms` gives each ring back its published mean.
const FRAGMENT = /* glsl */ `
  uniform sampler2D plane;
  uniform sampler2D layer;
  uniform sampler2D norms;
  uniform vec3 youngColour;
  uniform vec3 lineColour;
  uniform float clumped;
  uniform float latCot;
  uniform float latTan;
  uniform int latN;
  uniform int latM;
  uniform int seedStars;
  uniform int seedDust;
  uniform vec2 statsStars;
  uniform vec2 statsDust;
  uniform float knotMean;
  uniform float knotThreshold;
  uniform float knotCap;
  uniform float sigmaYoung;
  uniform float sigmaDust;
  uniform float fade;
  uniform float rLo;
  uniform float rHi;
  uniform float halfHeight;
  uniform float discHeight;
  uniform float youngHeight;
  uniform float dustHeight;
  uniform float bulgeLuminosity;
  uniform float bulgeScale;
  uniform vec3 bulgeColour;
  uniform vec3 extinction;
  uniform float gain;
  varying vec3 vWorld;

  float sech2(float x) { float c = cosh(clamp(x, -30.0, 30.0)); return 1.0 / (c * c); }

  // The column of a sech²(y / 2h) / 4h layer, which integrates to 1 over height, along the ray
  // from height y0 to y1 over a path ds: its share of height, over the ray's slope. A ray
  // running level through the layer takes the density at its height times the path.
  // tanh clamped: some drivers build it from exp, which overflows to NaN far outside the layer.
  float safeTanh(float x) { return tanh(clamp(x, -10.0, 10.0)); }
  float column(float y0, float y1, float h, float ds) {
    float dy = y1 - y0;
    if (abs(dy) < 1e-4 * h) return sech2(0.5 * (y0 + y1) / (2.0 * h)) / (4.0 * h) * ds;
    return abs(safeTanh(y1 / (2.0 * h)) - safeTanh(y0 / (2.0 * h))) * 0.5 * ds / abs(dy);
  }

  // Where to read a layer over a step from p0 to p1: where it crosses the midplane, or else the
  // step's middle, since a step that stays on one side holds little of a thin layer unless it
  // runs level through it.
  vec3 nearestMidplane(vec3 p0, vec3 p1) {
    if (p0.y * p1.y < 0.0) return mix(p0, p1, p0.y / (p0.y - p1.y));
    return 0.5 * (p0 + p1);
  }

  // Radius and azimuth in the stars' frame: x = r cos φ, z = −r sin φ.
  vec2 polarOf(vec3 p) {
    float phi = atan(-p.z, p.x);
    if (phi < 0.0) phi += 6.28318531;
    return vec2(length(p.xz), phi);
  }

  // An explicit level: implicit derivatives inside a loop and a branch are undefined, and some
  // drivers' compilers expand them into shaders that take seconds to build.
  vec4 readPolar(sampler2D tex, vec2 rp) {
    return textureLod(tex, vec2((rp.x - rLo) / (rHi - rLo), rp.y / 6.28318531), 0.0);
  }

  vec4 readPlane(sampler2D tex, vec3 p) { return readPolar(tex, polarOf(p)); }

  float lattice(int x, int y, int seed) {
    uint h = uint(x) * 0x27d4eb2du ^ uint(y) * 0x165667b1u ^ uint(seed) * 0x9e3779b1u;
    h = (h ^ (h >> 15u)) * 0x85ebca6bu;
    h = (h ^ (h >> 13u)) * 0xc2b2ae35u;
    h ^= h >> 16u;
    return float(h) / 2147483647.0 - 1.0;
  }

  float cellValue(int cx, int cy, int n, int m, int seed) {
    int turns = int(floor(float(cx) / float(n)));
    return lattice(cx - turns * n, cy - turns * m + ${LATTICE_LIFT}, seed);
  }

  float valueNoise(vec2 v, int n, int m, int seed) {
    vec2 c = floor(v);
    vec2 f = v - c;
    vec2 s = f * f * (3.0 - 2.0 * f);
    int x0 = int(c.x);
    int y0 = int(c.y);
    float a = cellValue(x0, y0, n, m, seed);
    float b = cellValue(x0 + 1, y0, n, m, seed);
    float cc = cellValue(x0, y0 + 1, n, m, seed);
    float d = cellValue(x0 + 1, y0 + 1, n, m, seed);
    return a + (b - a) * s.x + (cc - a) * s.y + (a - b - cc + d) * s.x * s.y;
  }

  float clumpNoise(float lnR, float angle, int seed, vec2 stats) {
    float x = (angle - latCot * lnR) * float(latN) / 6.28318531;
    float y = (lnR * latTan + angle) * float(latM) / 6.28318531;
    float v = 0.7 * valueNoise(vec2(x, y), latN, latM, seed) + 0.3 * valueNoise(vec2(2.0 * x, 2.0 * y), 2 * latN, 2 * latM, seed + 1);
    return (v - stats.x) / stats.y;
  }

  void main() {
    vec3 origin = cameraPosition;
    vec3 dir = normalize(vWorld - cameraPosition);
    vec3 lo = vec3(-rHi, -halfHeight, -rHi);
    vec3 inv = 1.0 / dir;
    vec3 t0 = (lo - origin) * inv;
    vec3 t1 = (-lo - origin) * inv;
    vec3 tNear3 = min(t0, t1);
    vec3 tFar3 = max(t0, t1);
    float tNear = max(max(tNear3.x, tNear3.y), max(tNear3.z, 0.0));
    float tFar = min(min(tFar3.x, tFar3.y), tFar3.z);
    if (tFar <= tNear) discard;

    // Steps spaced geometrically from the camera: fine where the galaxy is close and large on
    // screen, coarse where it is far and small. Even steps along a 60 kpc ray pass straight
    // over a disc 0.3 kpc thick a few hundred parsecs away.
    float tStart = max(tNear, 0.01);
    float ratio = pow(max(tFar, tStart * 1.0001) / tStart, 1.0 / float(${STEPS}));
    // A per-pixel offset into the first step turns banding into fine noise.
    float jitter = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453);
    vec3 light = vec3(0.0);
    vec3 transmitted = vec3(1.0);
    for (int k = 0; k < ${STEPS}; k++) {
      float a = tStart * pow(ratio, float(k));
      float ds = a * (ratio - 1.0);
      // The old disc and the bulge at a jittered point in the step, times the step.
      vec3 p = origin + dir * (a + jitter * ds);
      vec3 emitted = vec3(0.0);
      if (length(p.xz) < rHi) emitted += readPlane(plane, p).rgb * sech2(p.y / (2.0 * discHeight)) / (4.0 * discHeight);
      float s = max(length(p), 0.02);
      emitted += bulgeColour * bulgeLuminosity * bulgeScale / (6.28318531 * s * pow(s + bulgeScale, 3.0)) * 1.0e-6;
      emitted *= ds;

      // The midplane layer over the whole step, [a, a + ds].
      // Most steps are far above or below it and skip it: beyond 20 scale heights, sech²(y / 2h)
      // is under 10⁻⁸.
      vec3 p0 = origin + dir * a;
      vec3 p1 = p0 + dir * ds;
      vec3 depth = vec3(0.0);
      if (p0.y * p1.y <= 0.0 || min(abs(p0.y), abs(p1.y)) < 20.0 * max(youngHeight, dustHeight)) {
        float young = column(p0.y, p1.y, youngHeight, ds);
        float dust = column(p0.y, p1.y, dustHeight, ds);
        vec2 rp = polarOf(nearestMidplane(p0, p1));
        if (rp.x < rHi) {
          vec4 thin = readPolar(layer, rp);
          // The clump factors, each times its ring's norm (clumpFactors in regimes.ts).
          float fy = 1.0;
          float fl = 1.0;
          float fd = 1.0;
          if (clumped > 0.5) {
            vec4 k = textureLod(norms, vec2((rp.x - rLo) / (rHi - rLo), 0.5), 0.0);
            float lnR = log(max(rp.x, 1e-3));
            float s = 1.0 - exp(-(rp.x / fade) * (rp.x / fade));
            float n = clumpNoise(lnR, rp.y, seedStars, statsStars);
            float nd = clumpNoise(lnR, rp.y, seedDust, statsDust);
            float excess = min(max(0.0, n - knotThreshold), knotCap);
            fy = exp(sigmaYoung * s * n) * k.r;
            fl = mix(1.0, (1.0 - s + s * excess / knotMean) * k.g, k.a);
            fd = exp(sigmaDust * s * nd) * k.b;
          }
          emitted += (youngColour * thin.r * fy + lineColour * thin.g * fl) * young;
          depth = thin.b * fd * dust * extinction;
        }
      }
      // Light mixed through its own dust leaves (1 − e^−τ)/τ of itself.
      vec3 own = mix(vec3(1.0) - 0.5 * depth, (vec3(1.0) - exp(-depth)) / max(depth, vec3(1e-6)), step(vec3(1e-3), depth));
      light += transmitted * emitted * own;
      transmitted *= exp(-depth);
    }
    gl_FragColor = vec4(light * gain, 1.0);
  }
`;

interface Props {
  meta: FieldsPayload;
  query: Query;
  /** Exposure in stops. */
  stops: number;
  /** The regime weight, 0 to 1: how much of the field is drawn at this zoom. */
  weight?: number;
}

/**
 * The field regime: the whole galaxy's light as a volume, ray-marched per pixel through
 * the published fields (RENDER_PLAN R3, R4, M4). No particles and no sample: at the scale
 * of a galaxy the light is unresolved, and a smooth integral is what it is.
 */
export function FieldVolume({ meta, query, stops, weight = 1 }: Props) {
  const declared = (name: string) => meta.fields.find((f) => f.name === name);
  const fields = FIELDS.filter((n) => declared(n));
  const names = [...fields, ...SCALARS.filter((n) => declared(n))];
  const key = declared("disc_surface_brightness") && declared("disc_light_temperature") ? JSON.stringify([names, query]) : null;
  const loaded = useLoad<Frame>(key, (signal) => loadArrays(names, query, signal));
  const frame = loaded.value && fields.every((n) => n in loaded.value!.arrays) ? loaded.value : null;

  const mesh = useMemo(() => {
    const R = frame?.header.grid.axes.R;
    const tempDecl = declared("disc_light_temperature");
    if (!frame || !R || !tempDecl) return null;
    const paint = paintOf(tempDecl, meta.cmaps, frame.arrays.disc_light_temperature as Float64Array);
    const linear = (kelvin: number): number[] => {
      const [r, g, b, a] = paint.color(kelvin);
      return a === 0 ? [Number.NaN, Number.NaN, Number.NaN] : [srgbToLinear(r / 255), srgbToLinear(g / 255), srgbToLinear(b / 255)];
    };
    const temperature = frame.arrays.disc_light_temperature;
    const colour = new Float64Array(R.n * 3);
    for (let i = 0; i < R.n; i += 1) colour.set(linear(Number(temperature[i])), 3 * i);
    const phi = frame.header.grid.axes.phi;
    const contrastValues = frame.arrays.pattern_density_contrast;
    const scalars = frame.header.scalars;
    const young = linear(YOUNG_KELVIN);
    const { data, layer, norms, clumps, width, height } = planeTexture({
      R,
      brightness: frame.arrays.disc_surface_brightness as Float64Array,
      colour,
      halpha: frame.arrays.halpha_surface_brightness as Float64Array | undefined,
      extinction: frame.arrays.dust_extinction_v as Float64Array | undefined,
      contrast: contrastValues && phi ? { values: contrastValues as Float64Array, phi } : undefined,
      young: young.every(Number.isFinite) ? young : undefined,
      arms:
        scalars.pitch_angle !== undefined && scalars.arm_multiplicity !== undefined
          ? { pitchDeg: scalars.pitch_angle, multiplicity: scalars.arm_multiplicity }
          : undefined,
      // The world's seed, so a galaxy keeps its clumps from view to view and a new seed moves them;
      // kept non-negative, since the shader's hash takes it as a uint.
      seed: (Number(query.world_seed ?? 0) | 0) & 0x3fffffff,
    });
    const polar = (values: Float32Array) => {
      const texture = new DataTexture(values, width, height, RGBAFormat, FloatType);
      texture.minFilter = LinearFilter;
      texture.magFilter = LinearFilter;
      texture.wrapS = ClampToEdgeWrapping;
      texture.wrapT = RepeatWrapping;
      texture.needsUpdate = true;
      return texture;
    };
    const plane = polar(data);
    const thin = polar(layer);
    const ringNorms = new DataTexture(norms, width, 1, RGBAFormat, FloatType);
    ringNorms.minFilter = LinearFilter;
    ringNorms.magFilter = LinearFilter;
    ringNorms.needsUpdate = true;
    const finite = (rgb: number[]) => new Vector3(...rgb.map((c) => (Number.isFinite(c) ? c : 0)));

    const discHeight = (scalars.thin_disc_scale_height ?? 300) / 1000;
    const bulgeScale = scalars.bulge_scale_radius ?? 0;
    const bulgeColour = scalars.bulge_light_temperature ? linear(scalars.bulge_light_temperature) : [0, 0, 0];
    // Tall enough for the disc's light to have fallen away and the bulge to have faded.
    const halfHeight = Math.max(10 * discHeight, 12 * bulgeScale, 2);

    const material = new ShaderMaterial({
      uniforms: {
        plane: { value: plane },
        layer: { value: thin },
        norms: { value: ringNorms },
        youngColour: { value: finite(young) },
        lineColour: { value: new Vector3(...HII_RGB) },
        clumped: { value: clumps ? 1 : 0 },
        latCot: { value: clumps?.stars.cot ?? 0 },
        latTan: { value: clumps?.stars.tan ?? 0 },
        latN: { value: clumps?.stars.n ?? 1 },
        latM: { value: clumps?.stars.m ?? 1 },
        seedStars: { value: clumps?.stars.seed ?? 0 },
        seedDust: { value: clumps?.dust.seed ?? 0 },
        statsStars: { value: new Vector2(clumps?.stars.mean ?? 0, clumps?.stars.std ?? 1) },
        statsDust: { value: new Vector2(clumps?.dust.mean ?? 0, clumps?.dust.std ?? 1) },
        knotMean: { value: Math.max(clumps?.knotMean ?? 1, 1e-12) },
        knotThreshold: { value: CLUMPS.knotThreshold },
        knotCap: { value: CLUMPS.knotCap },
        sigmaYoung: { value: CLUMPS.sigma.young },
        sigmaDust: { value: CLUMPS.sigma.dust },
        fade: { value: CLUMPS.fade },
        rLo: { value: R.lo },
        rHi: { value: R.hi },
        halfHeight: { value: halfHeight },
        discHeight: { value: discHeight },
        // The young light and the dust lie in a layer thinner than the old stars: OB stars, HII
        // regions and dust within ~50–100 pc of the midplane against the thin disc's ~300
        // [recall]. Kept as a share of the published thin disc; a stated display choice.
        youngHeight: { value: discHeight * YOUNG_HEIGHT },
        dustHeight: { value: discHeight * DUST_HEIGHT },
        bulgeLuminosity: { value: scalars.bulge_luminosity ?? 0 },
        bulgeScale: { value: Math.max(bulgeScale, 1e-3) },
        bulgeColour: { value: finite(bulgeColour) },
        extinction: { value: new Vector3(...CHANNEL_EXTINCTION) },
        gain: { value: 0 },
      },
      vertexShader: VERTEX,
      fragmentShader: FRAGMENT,
      side: BackSide, // the far faces, so it draws with the camera outside the box or inside it
      depthTest: false,
      depthWrite: false,
    });
    const box = new Mesh(new BoxGeometry(2 * R.hi, 2 * halfHeight, 2 * R.hi), material);
    box.frustumCulled = false;
    return box;
  }, [frame, meta.cmaps, query.world_seed]); // eslint-disable-line react-hooks/exhaustive-deps

  const gl = useThree((state) => state.gl);
  const size = useThree((state) => state.size);

  // The box lives in a scene of its own, marched into a lower-resolution float target.
  const offscreen = useMemo(() => {
    if (!mesh) return null;
    const scene = new Scene();
    scene.add(mesh);
    const target = new WebGLRenderTarget(1, 1, { type: HalfFloatType, depthBuffer: false });
    target.texture.minFilter = LinearFilter;
    target.texture.magFilter = LinearFilter;
    const quad = new Mesh(
      new PlaneGeometry(2, 2),
      new ShaderMaterial({
        uniforms: { field: { value: target.texture } },
        vertexShader: COMPOSITE_VERTEX,
        fragmentShader: COMPOSITE_FRAGMENT,
        blending: AdditiveBlending,
        transparent: true,
        depthTest: false,
        depthWrite: false,
      }),
    );
    quad.frustumCulled = false;
    quad.renderOrder = -1;
    return { scene, target, quad, last: { view: new Matrix4(), projection: new Matrix4(), gain: -1, width: 0, height: 0 } };
  }, [mesh]);

  useEffect(
    () => () => {
      if (!mesh || !offscreen) return;
      const material = mesh.material as ShaderMaterial;
      (material.uniforms.plane.value as DataTexture).dispose();
      (material.uniforms.layer.value as DataTexture).dispose();
      (material.uniforms.norms.value as DataTexture).dispose();
      material.dispose();
      mesh.geometry.dispose();
      offscreen.target.dispose();
      offscreen.quad.geometry.dispose();
      (offscreen.quad.material as ShaderMaterial).dispose();
    },
    [mesh, offscreen],
  );

  // Before the composer (priority 1) draws the frame: march again only if the camera, the
  // drawing size or the gain changed. A still view costs nothing after its first frame.
  useFrame(({ camera }) => {
    if (!mesh || !offscreen) return;
    const gain = LIGHT_PER_LSUN_PC2 * 2 ** stops * weight;
    const buffer = gl.getDrawingBufferSize(DRAWING);
    const scale = Math.min(MAX_RESOLUTION, Math.sqrt(PIXEL_BUDGET / Math.max(1, buffer.x * buffer.y)));
    const width = Math.max(1, Math.round(buffer.x * scale));
    const height = Math.max(1, Math.round(buffer.y * scale));
    const last = offscreen.last;
    camera.updateMatrixWorld();
    const moved =
      !last.view.equals(camera.matrixWorld) || !last.projection.equals(camera.projectionMatrix) || last.gain !== gain ||
      last.width !== width || last.height !== height;
    // React may build the memo above twice (StrictMode), and adding the mesh to the second scene
    // takes it out of the first; whichever scene is kept, the mesh goes back into it here.
    const reattached = mesh.parent !== offscreen.scene;
    if (reattached) offscreen.scene.add(mesh);
    if (!moved && !reattached) return;
    if (last.width !== width || last.height !== height) offscreen.target.setSize(width, height);
    (mesh.material as ShaderMaterial).uniforms.gain.value = gain;
    const before = gl.getRenderTarget();
    gl.setRenderTarget(offscreen.target);
    gl.setClearColor(0x000000, 0);
    gl.clear(true, false, false);
    gl.render(offscreen.scene, camera);
    gl.setRenderTarget(before);
    gl.setClearColor(0x000000, 1);
    last.view.copy(camera.matrixWorld);
    last.projection.copy(camera.projectionMatrix);
    last.gain = gain;
    last.width = width;
    last.height = height;
  }, 0.5);

  void size; // re-render on resize so the target follows the canvas
  return offscreen ? <primitive object={offscreen.quad} /> : null;
}

const DRAWING = new Vector2();
