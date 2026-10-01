import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo, useRef } from "react";
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
  NearestFilter,
  Mesh,
  PlaneGeometry,
  RGBAFormat,
  RepeatWrapping,
  Scene,
  ShaderMaterial,
  Vector2,
  Vector3,
  Vector4,
  WebGLRenderTarget,
} from "three";

import { type FieldsPayload, type Frame, type Query, type RenderFrame, loadArrays, loadRender } from "../api";
import { useLoad } from "../useLoad";
import { type FilterSetName, bulgeLight, curvesOf, whiteOf } from "./filters";
import { marchHalfHeight, planeTexture, RING_ROWS, SUB_SAMPLES_MAX, summed, type RegionWindow } from "./regimes";
import { STEPS, type Tuning, TUNING_DEFAULTS } from "./tuning";

/**
 * How bright 1 L☉/pc² of white light draws at zero exposure stops, against a star point's 1 per
 * 100 L☉. A display balance between the layers, not a physical constant: a point is one star and
 * the field is a disc of them. Since S38 the field's channels are the model's filter responses over
 * the white point (filters.ts), so a ring of white light draws its surface brightness in each channel.
 */
export const LIGHT_PER_LSUN_PC2 = 1 / 400;

// The march's sampling (STEPS, PIXEL_BUDGET, MAX_RESOLUTION) is a display choice and lives in tuning.ts (D199).
/** The points of the scattered light's phase table the shader holds (spectra.PHASE_POINTS). */
const PHASE_POINTS = 21;

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

// The bulge's scale radius comes from the arrays; every component, its layer and its colour from /api/render.
const SCALARS = ["bulge_scale_radius"];

const VERTEX = /* glsl */ `
  varying vec3 vWorld;
  void main() {
    vec4 world = modelMatrix * vec4(position, 1.0);
    vWorld = world.xyz;
    gl_Position = projectionMatrix * viewMatrix * world;
  }
`;

// Emission and absorption along the line of sight, front to back (S39, V2). At each step every
// component's light in the step is added, dimmed by all the dust between it and the camera and by the
// step's own dust mixed through it, and the step's dust dims everything behind it. Units: the textures
// are L☉/pc² through a face-on column, and each component is spread through its own layer — a
// sech²(y / 2h) / 4h profile at the scale height the model names (the render header's layers), which
// integrates to 1 over height — so a step takes each layer's exact column over its own height range, a
// difference of tanh, whatever the step's size; the bulge is L☉ times a Hernquist density per kpc³, times
// the step, per 10⁶ pc² per kpc².
//
// Volumetric, not a surface (RENDER_PHYSICS §4): a tilted ray crosses more of a thick layer than a
// face-on one, so the diffuse Hα's 1.4 kpc layer brightens toward the disc's limb by itself.
//
// Every colour here is the model's filter integral over the white point (regimes.ts, filters.ts); the
// dust is each channel's own optical depth from the grain model's curve. The shader only sums and dims,
// and reads the scattered light's phase factor from the model's table by the view's |cos i|.
//
// Sub-samples along each step (S46, D197 (3)): a step is split into n equal sub-steps, n its in-plane
// length over the plane texture's radial cell (regimes.ts subSamples, at most SUB_SAMPLES_MAX), and each
// sub-step reads the layers once, at its midplane crossing or else at the pixel's fixed fraction along it,
// and takes its own exact column, its own dust mixed through its light and its own dimming of what lies
// behind. Read once per step, a grazing step spans many cells, and neighbouring pixels quantised R at the
// same step boundaries: the disc drew as concentric terraces. The columns are exact per sub-step and add
// to the step's, so the sub-samples change where the layers are read, not how much light there is.
// The steps are compiled in (a GLSL loop needs a constant bound): a new count is a new shader (D199).
export const fieldFragment = (steps: number = STEPS): string => /* glsl */ `
  uniform sampler2D plane;
  uniform sampler2D scatter;
  uniform sampler2D hii;
  uniform sampler2D rings;
  uniform float phase[${PHASE_POINTS}];
  uniform float rLo;
  uniform float rHi;
  // One texel's radial width, kpc (regimes.ts PlaneTexture.cell): the sub-steps' in-plane length.
  uniform float planeCell;
  // The most sub-samples a step reads (the Tuning panel's cap, D199), at most the loop's ${SUB_SAMPLES_MAX}.
  uniform float subMax;
  // 1 offsets each step by the pixel's fixed fraction; 0 reads each sub-step at its middle (D199).
  uniform float dither;
  uniform float halfHeight;
  uniform float starsHeight;
  uniform float dustHeight;
  uniform float hiiHeight;
  uniform float digHeight;
  uniform float bulgeScale;
  uniform vec3 bulgeLight;
  uniform float gain;
  // The region regime's window (r_min, r_max, phi_min, phi_max) and how far its resolved HII spheres have
  // faded in: inside it the field's HII steps back by the same weight (S40, no double counting).
  uniform vec4 regionWindow;
  uniform float hiiFade;
  varying vec3 vWorld;

  // The column of a sech²(y / 2h) / 4h layer, which integrates to 1 over height, along the ray
  // from height y0 to y1 over a path ds: its share of height, over the ray's slope. A ray
  // running level through the layer takes the density at its height times the path.
  // tanh clamped: some drivers build it from exp, which overflows to NaN far outside the layer.
  float sech2(float x) { float c = cosh(clamp(x, -30.0, 30.0)); return 1.0 / (c * c); }
  float safeTanh(float x) { return tanh(clamp(x, -10.0, 10.0)); }
  float column(float y0, float y1, float h, float ds) {
    if (h <= 0.0) return 0.0;
    float dy = y1 - y0;
    if (abs(dy) < 1e-4 * h) return sech2(0.5 * (y0 + y1) / (2.0 * h)) / (4.0 * h) * ds;
    return abs(safeTanh(y1 / (2.0 * h)) - safeTanh(y0 / (2.0 * h))) * 0.5 * ds / abs(dy);
  }

  // Where to read the layers over a sub-step from p0 to p1: where it crosses the midplane, or else the
  // pixel's fixed fraction 'at' along it (the screen-space dither, never frame-seeded: RENDER_PHYSICS §8).
  vec3 readPoint(vec3 p0, vec3 p1, float at) {
    if (p0.y * p1.y < 0.0) return mix(p0, p1, p0.y / (p0.y - p1.y));
    return mix(p0, p1, at);
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
  vec3 readRing(float r, float row) {
    return textureLod(rings, vec2((r - rLo) / (rHi - rLo), (row + 0.5) / ${RING_ROWS.count}.0), 0.0).rgb;
  }

  float inRegion(vec2 rp) {
    return (rp.x >= regionWindow.x && rp.x <= regionWindow.y && rp.y >= regionWindow.z && rp.y <= regionWindow.w) ? 1.0 : 0.0;
  }

  // regimes.ts's phaseAt, line for line: the table read linearly at |cos i|.
  float phaseAt(float cosView) {
    float x = clamp(abs(cosView), 0.0, 1.0) * float(${PHASE_POINTS - 1});
    int k = min(int(floor(x)), ${PHASE_POINTS - 2});
    float lo = phase[0];
    float hi = phase[1];
    for (int n = 0; n < ${PHASE_POINTS - 1}; n++) {
      if (n == k) { lo = phase[n]; hi = phase[n + 1]; }
    }
    return lo + (hi - lo) * (x - float(k));
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

    // The scattered light this view receives: the disc's axis is y.
    float scattering = phaseAt(dir.y);
    // Steps spaced geometrically from the camera: fine where the galaxy is close and large on
    // screen, coarse where it is far and small. Even steps along a 60 kpc ray pass straight
    // over a disc 0.3 kpc thick a few hundred parsecs away.
    float tStart = max(tNear, 0.01);
    float ratio = pow(max(tFar, tStart * 1.0001) / tStart, 1.0 / float(${steps}));
    // A per-pixel offset turns banding into fine noise: into each step for the bulge's point sample, and
    // into each sub-step for the layers' reads. Fixed by the pixel, never by the frame.
    float jitter = dither > 0.5 ? fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453) : 0.5;
    vec3 light = vec3(0.0);
    vec3 transmitted = vec3(1.0);
    for (int k = 0; k < ${steps}; k++) {
      float a = tStart * pow(ratio, float(k));
      float ds = a * (ratio - 1.0);
      vec3 p = origin + dir * (a + jitter * ds);
      float s = max(length(p), 0.02);
      vec3 bulge = bulgeLight * bulgeScale / (6.28318531 * s * pow(s + bulgeScale, 3.0)) * 1.0e-6 * ds;

      // The disc's layers over the whole step, [a, a + ds], in n sub-steps of at most about one plane
      // cell in the plane each (regimes.ts subSamples). The bulge's light is spread evenly over them, so
      // it sits in the same dust as before; with n = 1 this is the single read per step of S39.
      vec3 p0 = origin + dir * a;
      vec3 p1 = p0 + dir * ds;
      int n = int(clamp(ceil(length(p1.xz - p0.xz) / planeCell), 1.0, subMax));
      float sub = ds / float(n);
      for (int j = 0; j < ${SUB_SAMPLES_MAX}; j++) {
        if (j >= n) break;
        vec3 q0 = p0 + dir * (float(j) * sub);
        vec3 q1 = p0 + dir * (float(j + 1) * sub);
        vec3 emitted = bulge / float(n);
        vec3 depth = vec3(0.0);
        vec2 rp = polarOf(readPoint(q0, q1, jitter));
        // Beyond rHi every texture is zero: the box's side faces clip nothing but zeros.
        if (rp.x < rHi) {
          float cStars = column(q0.y, q1.y, starsHeight, sub);
          float cDust = column(q0.y, q1.y, dustHeight, sub);
          float cHii = column(q0.y, q1.y, hiiHeight, sub);
          float cDig = column(q0.y, q1.y, digHeight, sub);
          emitted += readPolar(plane, rp).rgb * cStars;
          emitted += (readPolar(scatter, rp).rgb * scattering + readRing(rp.x, ${RING_ROWS.thermal}.0)) * cDust;
          emitted += readPolar(hii, rp).rgb * cHii * (1.0 - hiiFade * inRegion(rp)) + readRing(rp.x, ${RING_ROWS.dig}.0) * cDig;
          depth = readRing(rp.x, ${RING_ROWS.depth}.0) * cDust;
        }
        // Light mixed through its own dust leaves (1 − e^−τ)/τ of itself; each sub-step's dust dims
        // only what lies behind it, so light and dust keep their order inside a long step.
        vec3 own = mix(vec3(1.0) - 0.5 * depth, (vec3(1.0) - exp(-depth)) / max(depth, vec3(1e-6)), step(vec3(1e-3), depth));
        light += transmitted * emitted * own;
        transmitted *= exp(-depth);
      }
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
  /** The filter set the field is seen through (filters.json): the model integrates it, per component. */
  filterSet?: FilterSetName;
  /** The region regime's window and weight (S40): the field's HII fades there as the resolved spheres fade in. */
  regionWindow?: RegionWindow | null;
  hiiFade?: number;
  /**
   * The Tuning panel's display choices (D199): the march's sampling, the field's gain multiplier and the
   * white point. The defaults are the values the view drew with before the panel.
   */
  tuning?: Pick<Tuning, "resolution" | "pixelBudget" | "steps" | "subMax" | "dither" | "filtering" | "fieldGain" | "whiteKelvin">;
  /** Filled in at each re-march: the target's size and the CPU-side time of the march's render call. */
  stats?: MarchStats;
}

/** The last re-march: its target in pixels and how long the render call took on the CPU side, ms. */
export interface MarchStats {
  width: number;
  height: number;
  ms: number;
}

/**
 * The field regime: the whole galaxy's light as a volume, ray-marched per pixel through
 * the published components (RENDER_PLAN R3, R4, M4; BUILD_II V1, V2). No particles and no sample:
 * at the scale of a galaxy the light is unresolved, and a smooth integral is what it is. Its colour
 * is the model's filter integral (/api/render): the viewer sends the set's curves and draws the
 * responses over the white point, each component in the layer the model names.
 */
export function FieldVolume({ meta, query, stops, weight = 1, filterSet = "rgb", regionWindow = null, hiiFade = 0, tuning = TUNING_DEFAULTS, stats }: Props) {
  const { resolution, pixelBudget, steps, subMax, dither, filtering, fieldGain, whiteKelvin } = tuning;
  const declared = (name: string) => meta.fields.find((f) => f.name === name);
  const names = SCALARS.filter((n) => declared(n));
  const lit = Boolean(declared("disc_surface_brightness") && declared("disc_light_temperature"));
  const key = lit ? JSON.stringify([names, query]) : null;
  const loaded = useLoad<Frame>(key, (signal) => loadArrays(names, query, signal));
  const frame = loaded.value ?? null;
  const renderKey = lit ? JSON.stringify([filterSet, whiteKelvin, query]) : null;
  const rendered = useLoad<RenderFrame>(renderKey, (signal) => loadRender(curvesOf(filterSet), whiteKelvin, query, signal));
  const light = rendered.value && "stars" in rendered.value.arrays ? rendered.value : null;

  // Read when the material is built, so a mesh made after a steps change compiles once, with them.
  const stepsNow = useRef(steps);
  stepsNow.current = steps;
  const filteringNow = useRef(filtering);
  filteringNow.current = filtering;

  const mesh = useMemo(() => {
    const R = frame?.header.grid.axes.R;
    const phi = frame?.header.grid.axes.phi;
    const white = light ? whiteOf(light.header) : null;
    const layers = light?.header.layers;
    // The render covers the whole grid; a frame from another grid (a model switch in flight) waits, and
    // so does a render without the layers its components are spread through.
    if (!frame || !R || !phi || !light || !white || !layers?.stars || light.header.window.R.n !== R.n || light.header.window.phi.n !== phi.n) {
      return null;
    }
    const a = light.arrays;
    const { data, scatter, hii, rings, width, height, cell } = planeTexture({
      R,
      phi,
      stars: a.stars,
      // Every line in each layer (S42): Halpha plus the others the render carries (lines_hii, lines_dig).
      hii: summed(a.halpha_hii, a.lines_hii),
      dig: summed(a.halpha_dig, a.lines_dig),
      extinction: a.dust_extinction,
      scattered: a.dust_scattered,
      thermal: a.dust_thermal,
      white,
    });
    const filter = filteringNow.current === "nearest" ? NearestFilter : LinearFilter;
    const polar = (values: Float32Array) => {
      const texture = new DataTexture(values, width, height, RGBAFormat, FloatType);
      texture.minFilter = filter;
      texture.magFilter = filter;
      texture.wrapS = ClampToEdgeWrapping;
      texture.wrapT = RepeatWrapping;
      texture.needsUpdate = true;
      return texture;
    };
    const ringTexture = new DataTexture(rings, width, RING_ROWS.count, RGBAFormat, FloatType);
    ringTexture.minFilter = filter;
    ringTexture.magFilter = filter;
    ringTexture.wrapS = ClampToEdgeWrapping;
    ringTexture.wrapT = ClampToEdgeWrapping;
    ringTexture.needsUpdate = true;

    const bulgeScale = frame.header.scalars.bulge_scale_radius ?? 0;
    const halfHeight = marchHalfHeight(layers, bulgeScale);
    // The phase table, or isotropic scattering where the render carries none.
    const table = light.header.components?.dust_scattered?.phase?.factor;
    const phase = table && table.length === PHASE_POINTS ? table.map(Number) : new Array<number>(PHASE_POINTS).fill(1);

    const material = new ShaderMaterial({
      uniforms: {
        plane: { value: polar(data) },
        scatter: { value: polar(scatter) },
        hii: { value: polar(hii) },
        rings: { value: ringTexture },
        phase: { value: phase },
        rLo: { value: R.lo },
        rHi: { value: R.hi },
        planeCell: { value: cell },
        subMax: { value: SUB_SAMPLES_MAX },
        dither: { value: 1 },
        halfHeight: { value: halfHeight },
        // The model's layers (the render header): a missing one is height 0, which draws nothing.
        starsHeight: { value: layers.stars ?? 0 },
        dustHeight: { value: layers.dust ?? 0 },
        hiiHeight: { value: layers.halpha_hii ?? 0 },
        digHeight: { value: layers.halpha_dig ?? 0 },
        bulgeScale: { value: Math.max(bulgeScale, 1e-3) },
        bulgeLight: { value: new Vector3(...bulgeLight(light.header.bulge, white)) },
        gain: { value: 0 },
        regionWindow: { value: new Vector4(0, 0, 0, 0) },
        hiiFade: { value: 0 },
      },
      vertexShader: VERTEX,
      fragmentShader: fieldFragment(stepsNow.current),
      side: BackSide, // the far faces, so it draws with the camera outside the box or inside it
      depthTest: false,
      depthWrite: false,
    });
    const box = new Mesh(new BoxGeometry(2 * R.hi, 2 * halfHeight, 2 * R.hi), material);
    box.frustumCulled = false;
    return box;
  }, [frame, light]);

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
    return { scene, target, quad, last: { view: new Matrix4(), projection: new Matrix4(), gain: -1, width: 0, height: 0, region: "", settings: "" } };
  }, [mesh]);

  useEffect(
    () => () => {
      if (!mesh || !offscreen) return;
      const material = mesh.material as ShaderMaterial;
      for (const name of ["plane", "scatter", "hii", "rings"]) (material.uniforms[name].value as DataTexture).dispose();
      material.dispose();
      mesh.geometry.dispose();
      offscreen.target.dispose();
      offscreen.quad.geometry.dispose();
      (offscreen.quad.material as ShaderMaterial).dispose();
    },
    [mesh, offscreen],
  );

  // A new step count is a new shader (the loop's bound is compiled in); the caller debounces it.
  useEffect(() => {
    if (!mesh) return;
    const material = mesh.material as ShaderMaterial;
    const source = fieldFragment(steps);
    if (material.fragmentShader === source) return;
    material.fragmentShader = source;
    material.needsUpdate = true;
  }, [mesh, steps]);

  // The plane textures' sampling, set in place: no new textures, no new shader.
  useEffect(() => {
    if (!mesh) return;
    const filter = filtering === "nearest" ? NearestFilter : LinearFilter;
    const uniforms = (mesh.material as ShaderMaterial).uniforms;
    for (const name of ["plane", "scatter", "hii", "rings"]) {
      const texture = uniforms[name].value as DataTexture;
      if (texture.minFilter === filter && texture.magFilter === filter) continue;
      texture.minFilter = filter;
      texture.magFilter = filter;
      texture.needsUpdate = true;
    }
  }, [mesh, filtering]);

  // Before the composer (priority 1) draws the frame: march again only if the camera, the
  // drawing size, the gain or a tuning choice changed. A still view costs nothing after its first frame.
  useFrame(({ camera }) => {
    if (!mesh || !offscreen) return;
    const gain = LIGHT_PER_LSUN_PC2 * fieldGain * 2 ** stops * weight;
    const buffer = gl.getDrawingBufferSize(DRAWING);
    const scale = Math.min(resolution, Math.sqrt(pixelBudget / Math.max(1, buffer.x * buffer.y)));
    const width = Math.max(1, Math.round(buffer.x * scale));
    const height = Math.max(1, Math.round(buffer.y * scale));
    const last = offscreen.last;
    camera.updateMatrixWorld();
    const w = regionWindow;
    const region = w && hiiFade > 0 ? `${w.r_min},${w.r_max},${w.phi_min},${w.phi_max},${hiiFade}` : "";
    const settings = `${steps},${subMax},${dither},${filtering}`;
    const moved =
      !last.view.equals(camera.matrixWorld) || !last.projection.equals(camera.projectionMatrix) || last.gain !== gain ||
      last.width !== width || last.height !== height || last.region !== region || last.settings !== settings;
    // React may build the memo above twice (StrictMode), and adding the mesh to the second scene
    // takes it out of the first; whichever scene is kept, the mesh goes back into it here.
    const reattached = mesh.parent !== offscreen.scene;
    if (reattached) offscreen.scene.add(mesh);
    if (!moved && !reattached) return;
    if (last.width !== width || last.height !== height) offscreen.target.setSize(width, height);
    const uniforms = (mesh.material as ShaderMaterial).uniforms;
    uniforms.gain.value = gain;
    (uniforms.regionWindow.value as Vector4).set(w?.r_min ?? 0, w?.r_max ?? 0, w?.phi_min ?? 0, w?.phi_max ?? 0);
    uniforms.hiiFade.value = region ? hiiFade : 0;
    uniforms.subMax.value = Math.min(SUB_SAMPLES_MAX, Math.max(1, Math.round(subMax)));
    uniforms.dither.value = dither ? 1 : 0;
    const before = gl.getRenderTarget();
    gl.setRenderTarget(offscreen.target);
    gl.setClearColor(0x000000, 0);
    gl.clear(true, false, false);
    const started = performance.now();
    gl.render(offscreen.scene, camera);
    const ms = performance.now() - started;
    gl.setRenderTarget(before);
    gl.setClearColor(0x000000, 1);
    last.view.copy(camera.matrixWorld);
    last.projection.copy(camera.projectionMatrix);
    last.gain = gain;
    last.width = width;
    last.height = height;
    last.region = region;
    last.settings = settings;
    if (stats) {
      stats.width = width;
      stats.height = height;
      stats.ms = ms;
    }
  }, 0.5);

  void size; // re-render on resize so the target follows the canvas
  return offscreen ? <primitive object={offscreen.quad} /> : null;
}

const DRAWING = new Vector2();
