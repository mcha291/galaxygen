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

import { type FieldsPayload, type Frame, type Query, type RenderFrame, loadArrays, loadRender } from "../api";
import { useLoad } from "../useLoad";
import { type FilterSetName, WHITE_KELVIN, bulgeLight, curvesOf, whiteOf } from "./filters";
import { RING_ROWS, marchHalfHeight, planeTexture } from "./regimes";

/**
 * How bright 1 L☉/pc² of white light draws at zero exposure stops, against a star point's 1 per
 * 100 L☉. A display balance between the layers, not a physical constant: a point is one star and
 * the field is a disc of them. Since S38 the field's channels are the model's filter responses over
 * the white point (filters.ts), so a ring of white light draws its surface brightness in each channel.
 */
export const LIGHT_PER_LSUN_PC2 = 1 / 400;

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
const FRAGMENT = /* glsl */ `
  uniform sampler2D plane;
  uniform sampler2D scatter;
  uniform sampler2D hii;
  uniform sampler2D rings;
  uniform float phase[${PHASE_POINTS}];
  uniform float rLo;
  uniform float rHi;
  uniform float halfHeight;
  uniform float starsHeight;
  uniform float dustHeight;
  uniform float hiiHeight;
  uniform float digHeight;
  uniform float bulgeScale;
  uniform vec3 bulgeLight;
  uniform float gain;
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

  // Where to read the layers over a step from p0 to p1: where it crosses the midplane, or else the
  // step's middle.
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
  vec3 readRing(float r, float row) {
    return textureLod(rings, vec2((r - rLo) / (rHi - rLo), (row + 0.5) / ${RING_ROWS.count}.0), 0.0).rgb;
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
    float ratio = pow(max(tFar, tStart * 1.0001) / tStart, 1.0 / float(${STEPS}));
    // A per-pixel offset into the first step turns banding into fine noise (the bulge's point sample).
    float jitter = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453);
    vec3 light = vec3(0.0);
    vec3 transmitted = vec3(1.0);
    for (int k = 0; k < ${STEPS}; k++) {
      float a = tStart * pow(ratio, float(k));
      float ds = a * (ratio - 1.0);
      vec3 p = origin + dir * (a + jitter * ds);
      float s = max(length(p), 0.02);
      vec3 emitted = bulgeLight * bulgeScale / (6.28318531 * s * pow(s + bulgeScale, 3.0)) * 1.0e-6 * ds;

      // The disc's layers over the whole step, [a, a + ds], read where the step is nearest the midplane.
      vec3 p0 = origin + dir * a;
      vec3 p1 = p0 + dir * ds;
      vec3 depth = vec3(0.0);
      vec2 rp = polarOf(nearestMidplane(p0, p1));
      if (rp.x < rHi) {
        float cStars = column(p0.y, p1.y, starsHeight, ds);
        float cDust = column(p0.y, p1.y, dustHeight, ds);
        float cHii = column(p0.y, p1.y, hiiHeight, ds);
        float cDig = column(p0.y, p1.y, digHeight, ds);
        emitted += readPolar(plane, rp).rgb * cStars;
        emitted += (readPolar(scatter, rp).rgb * scattering + readRing(rp.x, ${RING_ROWS.thermal}.0)) * cDust;
        emitted += readPolar(hii, rp).rgb * cHii + readRing(rp.x, ${RING_ROWS.dig}.0) * cDig;
        depth = readRing(rp.x, ${RING_ROWS.depth}.0) * cDust;
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
  /** The filter set the field is seen through (filters.json): the model integrates it, per component. */
  filterSet?: FilterSetName;
}

/**
 * The field regime: the whole galaxy's light as a volume, ray-marched per pixel through
 * the published components (RENDER_PLAN R3, R4, M4; BUILD_II V1, V2). No particles and no sample:
 * at the scale of a galaxy the light is unresolved, and a smooth integral is what it is. Its colour
 * is the model's filter integral (/api/render): the viewer sends the set's curves and draws the
 * responses over the white point, each component in the layer the model names.
 */
export function FieldVolume({ meta, query, stops, weight = 1, filterSet = "rgb" }: Props) {
  const declared = (name: string) => meta.fields.find((f) => f.name === name);
  const names = SCALARS.filter((n) => declared(n));
  const lit = Boolean(declared("disc_surface_brightness") && declared("disc_light_temperature"));
  const key = lit ? JSON.stringify([names, query]) : null;
  const loaded = useLoad<Frame>(key, (signal) => loadArrays(names, query, signal));
  const frame = loaded.value ?? null;
  const renderKey = lit ? JSON.stringify([filterSet, WHITE_KELVIN, query]) : null;
  const rendered = useLoad<RenderFrame>(renderKey, (signal) => loadRender(curvesOf(filterSet), WHITE_KELVIN, query, signal));
  const light = rendered.value && "stars" in rendered.value.arrays ? rendered.value : null;

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
    const { data, scatter, hii, rings, width, height } = planeTexture({
      R,
      phi,
      stars: a.stars,
      hii: a.halpha_hii,
      dig: a.halpha_dig,
      extinction: a.dust_extinction,
      scattered: a.dust_scattered,
      thermal: a.dust_thermal,
      white,
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
    const ringTexture = new DataTexture(rings, width, RING_ROWS.count, RGBAFormat, FloatType);
    ringTexture.minFilter = LinearFilter;
    ringTexture.magFilter = LinearFilter;
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
        halfHeight: { value: halfHeight },
        // The model's layers (the render header): a missing one is height 0, which draws nothing.
        starsHeight: { value: layers.stars ?? 0 },
        dustHeight: { value: layers.dust ?? 0 },
        hiiHeight: { value: layers.halpha_hii ?? 0 },
        digHeight: { value: layers.halpha_dig ?? 0 },
        bulgeScale: { value: Math.max(bulgeScale, 1e-3) },
        bulgeLight: { value: new Vector3(...bulgeLight(light.header.bulge, white)) },
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
    return { scene, target, quad, last: { view: new Matrix4(), projection: new Matrix4(), gain: -1, width: 0, height: 0 } };
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
