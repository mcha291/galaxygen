import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo } from "react";
import {
  AddEquation,
  AdditiveBlending,
  BackSide,
  BoxGeometry,
  CustomBlending,
  DataTexture,
  FloatType,
  HalfFloatType,
  LinearFilter,
  Matrix4,
  Mesh,
  NearestFilter,
  PlaneGeometry,
  RGBAFormat,
  Scene,
  ShaderMaterial,
  SrcColorFactor,
  Vector2,
  Vector3,
  WebGLRenderTarget,
  ZeroFactor,
} from "three";

import { type Census, type Query, type RenderFrame, loadClouds, loadRemnants, loadRender } from "../api";
import { useLoad } from "../useLoad";
import { LIGHT_PER_LSUN_PC2 } from "./FieldVolume";
import { type FilterSetName, WHITE_KELVIN, curvesOf, whiteOf } from "./filters";
import { FIELD_SIGMA, type LineWeights, MAX_OBJECTS, OBJECT_FLOATS, OCTAVES, packObjects, sortedFrom } from "./region";
import type { RegionWindow } from "./regimes";

/** The most pixels the region is marched at (as FieldVolume's budget): the loop over objects runs per pixel. */
const PIXEL_BUDGET = 400_000;
const MAX_RESOLUTION = 0.5;
/** Samples of a cloud's density along each chord through it. */
const CLOUD_SAMPLES = 4;

const COMPOSITE_VERTEX = /* glsl */ `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = vec4(position.xy, 0.0, 1.0);
  }
`;
const COMPOSITE_FRAGMENT = /* glsl */ `
  uniform sampler2D image;
  varying vec2 vUv;
  void main() { gl_FragColor = vec4(texture2D(image, vUv).rgb, 1.0); }
`;

const VERTEX = /* glsl */ `
  varying vec3 vWorld;
  void main() {
    vec4 world = modelMatrix * vec4(position, 1.0);
    vWorld = world.xyz;
    gl_Position = projectionMatrix * viewMatrix * world;
  }
`;

// region.ts's hash3 / valueNoise / unitField / densityRatio, line for line in 32-bit unsigned arithmetic, so the
// shader draws the field the vitest measures (the float32 division at the end differs from float64 at 1e-7).
const FRAGMENT = /* glsl */ `
  precision highp float;
  precision highp int;
  uniform sampler2D objects;
  uniform int count;
  uniform vec3 lineWeight;
  uniform vec3 extRatio;
  uniform float gain;
  uniform float weight;
  uniform int mode;
  varying vec3 vWorld;

  float hash01(int x, int y, int z, int seed) {
    uint h = uint(x) * 374761393u + uint(y) * 668265263u + uint(z) * 2147483647u + uint(seed) * 1597334677u;
    h = (h ^ (h >> 13u)) * 1274126177u;
    h = h ^ (h >> 16u);
    return float(h) / 4294967296.0;
  }
  float valueNoise(vec3 p, int seed) {
    vec3 i = floor(p);
    vec3 f = p - i;
    vec3 s = f * f * (3.0 - 2.0 * f);
    int ix = int(i.x), iy = int(i.y), iz = int(i.z);
    float c000 = hash01(ix, iy, iz, seed), c100 = hash01(ix + 1, iy, iz, seed);
    float c010 = hash01(ix, iy + 1, iz, seed), c110 = hash01(ix + 1, iy + 1, iz, seed);
    float c001 = hash01(ix, iy, iz + 1, seed), c101 = hash01(ix + 1, iy, iz + 1, seed);
    float c011 = hash01(ix, iy + 1, iz + 1, seed), c111 = hash01(ix + 1, iy + 1, iz + 1, seed);
    float x00 = c000 + (c100 - c000) * s.x;
    float x10 = c010 + (c110 - c010) * s.x;
    float x01 = c001 + (c101 - c001) * s.x;
    float x11 = c011 + (c111 - c011) * s.x;
    float y0 = x00 + (x10 - x00) * s.y;
    float y1 = x01 + (x11 - x01) * s.y;
    return y0 + (y1 - y0) * s.z;
  }
  float unitField(vec3 p, int seed) {
    float sum = 0.0;
    float f = 1.0;
    float w = 1.0;
    for (int k = 0; k < ${OCTAVES}; k++) {
      vec3 q = p * f + vec3(17.3, 31.7, 47.1) * float(k);
      sum += (valueNoise(q, seed + 1013 * k) - 0.5) * w;
      f *= 2.0;
      w *= 0.5;
    }
    return sum / ${FIELD_SIGMA.toFixed(6)};
  }
  float densityRatio(vec3 p, int seed, float sigmaS, float gradient, float angle) {
    float g = unitField(p, seed);
    float tilt = max(0.05, 1.0 + min(0.95, abs(gradient)) * (p.x * cos(angle) + p.z * sin(angle)));
    return tilt * exp(sigmaS * g - 0.5 * sigmaS * sigmaS);
  }

  vec4 obj(int i, int row) { return texelFetch(objects, ivec2(row, i), 0); }
  bool sphere(vec3 o, vec3 d, vec3 c, float r, out float t0, out float t1) {
    vec3 oc = o - c;
    float b = dot(oc, d);
    float h = b * b - (dot(oc, oc) - r * r);
    if (h < 0.0) { t0 = 0.0; t1 = 0.0; return false; }
    h = sqrt(h);
    t0 = max(-b - h, 0.0);
    t1 = -b + h;
    return t1 > t0;
  }

  void main() {
    vec3 origin = cameraPosition;
    vec3 dir = normalize(vWorld - cameraPosition);
    vec3 light = vec3(0.0);
    vec3 trans = vec3(1.0);
    for (int i = 0; i < ${MAX_OBJECTS}; i++) {
      if (i >= count) break;
      vec4 a = obj(i, 0);
      vec4 b = obj(i, 1);
      vec4 c = obj(i, 2);
      vec4 e = obj(i, 3);
      float t0, t1;
      if (!sphere(origin, dir, a.xyz, a.w, t0, t1)) continue;
      int kind = int(b.x + 0.5);
      if (kind == 1) {
        // An HII region: uniform emissivity (L_sun/pc^3) over the chord in pc - brighter toward the limb for free -
        // in its own colour per unit Halpha, every line it carries through the filters (S42).
        light += trans * c.x * (t1 - t0) * 1000.0 * c.yzw;
      } else if (kind == 2) {
        // A shell: the chord through the sphere less the chord through its hollow.
        float i0, i1;
        float inner = sphere(origin, dir, a.xyz, max(a.w - c.y, 0.0), i0, i1) ? i1 - i0 : 0.0;
        light += trans * c.x * ((t1 - t0) - inner) * 1000.0 * lineWeight;
      } else {
        // A cloud: the published mean column made log-normal by its own seeded field; inside its cluster's cavity
        // only the clumps denser than e^sigma survive - the pillars (HANDOFF_S40 R3).
        int seed = ((int(b.y) & 0xffff) << 15) ^ (int(b.z) & 0x7fff);
        float ds = (t1 - t0) / float(${CLOUD_SAMPLES});
        float tau = 0.0;
        for (int k = 0; k < ${CLOUD_SAMPLES}; k++) {
          vec3 p = origin + dir * (t0 + (float(k) + 0.5) * ds);
          float rho = densityRatio((p - a.xyz) / a.w, seed, b.w, c.x, c.y);
          if (e.w > 0.0 && length(p - e.xyz) < e.w && rho < exp(b.w)) rho = 0.0;
          tau += c.z * rho * ds;
        }
        trans *= exp(-tau * extRatio);
      }
    }
    if (mode == 0) gl_FragColor = vec4(light * gain, 1.0);
    else gl_FragColor = vec4(mix(vec3(1.0), trans, weight), 1.0);
  }
`;

interface Props {
  query: Query;
  window: RegionWindow;
  /** The window's clusters at this level, loaded once by the galaxy tab (it draws them as points too, S41). */
  clusters: Census | null;
  level: number;
  /** Exposure in stops. */
  stops: number;
  /** The stars regime's weight, 0 to 1: the resolved objects fade in as the field's HII fades out. */
  weight: number;
  filterSet?: FilterSetName;
  /** The white point, K (the Tuning panel's, D199): the same one the field is drawn with. */
  whiteKelvin?: number;
}

/**
 * The region regime (BUILD_II V3): a window's clouds, HII regions and bubble shells drawn from the published
 * vectors (RENDER_PHYSICS §5), marched per pixel front to back. Emission is added to the frame; the clouds'
 * transmission multiplies what lies behind them in a second pass — the field and the stars alike, a star in front
 * of a cloud included (an approximation of the composite, stated in HANDOFF_S40). The line's per-filter weight and
 * the dust's extinction ratios are the model's (`/api/render` at the region's level), the white point the viewer's.
 */
export function RegionVolume({ query, window, level, clusters, stops, weight, filterSet = "rgb", whiteKelvin = WHITE_KELVIN }: Props) {
  const place = { ...window, level };
  const key = JSON.stringify([place, query]);
  const clouds = useLoad<Census>(key, (signal) => loadClouds(place, query, signal)).value ?? null;
  const remnants = useLoad<Census>(key, (signal) => loadRemnants(place, query, signal)).value ?? null;
  const renderKey = JSON.stringify([filterSet, whiteKelvin, place, query]);
  const rendered = useLoad<RenderFrame>(renderKey, (signal) => loadRender(curvesOf(filterSet), whiteKelvin, { ...query, ...place }, signal)).value ?? null;

  const built = useMemo(() => {
    if (!clouds || !clusters || !remnants || !rendered) return null;
    const scalars = (clouds.header.scalars ?? {}) as Record<string, number>;
    const white = whiteOf(rendered.header) ?? [1, 1, 1];
    const comps = (rendered.header.components ?? {}) as Record<
      string,
      { transmission?: number[]; extinction_ratio?: number[]; lines?: Record<string, { transmission: number[] }> }
    >;
    const t = comps.halpha_hii?.transmission ?? [0, 0, 0];
    // Each line's weight per channel: the model's transmission at its wavelength over the white point's (S42).
    const weigh = (tr: number[]) => [0, 1, 2].map((k) => (white[k] > 0 ? (tr[k] ?? 0) / white[k] : 0)) as [number, number, number];
    const lines: LineWeights = { halpha: weigh(t) };
    for (const [name, entry] of Object.entries(comps.lines_hii?.lines ?? {})) lines[name] = weigh(entry.transmission);
    const table = packObjects(clouds.columns, clusters.columns, Number(scalars.cloud_extinction_v ?? 0), undefined, remnants.columns, lines);
    if (!table.count) return null;
    const x = comps.dust_extinction?.extinction_ratio ?? [1, 1, 1];
    const line = new Vector3(...[0, 1, 2].map((k) => (white[k] > 0 ? (t[k] ?? 0) / white[k] : 0)));
    const ratio = new Vector3(...[0, 1, 2].map((k) => x[k] ?? 1));
    const texture = new DataTexture(new Float32Array(MAX_OBJECTS * OBJECT_FLOATS), 4, MAX_OBJECTS, RGBAFormat, FloatType);
    texture.minFilter = NearestFilter;
    texture.magFilter = NearestFilter;
    const material = (mode: number) =>
      new ShaderMaterial({
        uniforms: {
          objects: { value: texture },
          count: { value: table.count },
          lineWeight: { value: line },
          extRatio: { value: ratio },
          gain: { value: 0 },
          weight: { value: 0 },
          mode: { value: mode },
        },
        vertexShader: VERTEX,
        fragmentShader: FRAGMENT,
        side: BackSide,
        depthTest: false,
        depthWrite: false,
      });
    const size = table.max.map((v, a) => v - table.min[a] + 0.01);
    const centre = table.max.map((v, a) => 0.5 * (v + table.min[a]));
    const box = new BoxGeometry(size[0], size[1], size[2]);
    const meshes = [0, 1].map((mode) => {
      const m = new Mesh(box, material(mode));
      m.position.set(centre[0], centre[1], centre[2]);
      m.frustumCulled = false;
      return m;
    });
    return { table, texture, meshes, sorted: new Float32Array(MAX_OBJECTS * OBJECT_FLOATS) };
  }, [clouds, clusters, remnants, rendered]);

  const gl = useThree((state) => state.gl);

  const passes = useMemo(() => {
    if (!built) return null;
    return built.meshes.map((mesh, mode) => {
      const scene = new Scene();
      scene.add(mesh);
      const target = new WebGLRenderTarget(1, 1, { type: HalfFloatType, depthBuffer: false });
      target.texture.minFilter = LinearFilter;
      target.texture.magFilter = LinearFilter;
      const quad = new Mesh(
        new PlaneGeometry(2, 2),
        new ShaderMaterial({
          uniforms: { image: { value: target.texture } },
          vertexShader: COMPOSITE_VERTEX,
          fragmentShader: COMPOSITE_FRAGMENT,
          // light adds; transmission multiplies what is already drawn (dst x src)
          ...(mode === 0
            ? { blending: AdditiveBlending }
            : { blending: CustomBlending, blendEquation: AddEquation, blendSrc: ZeroFactor, blendDst: SrcColorFactor }),
          transparent: true,
          depthTest: false,
          depthWrite: false,
        }),
      );
      quad.frustumCulled = false;
      quad.renderOrder = mode === 0 ? 2 : 1;
      return { scene, target, quad, mesh };
    });
  }, [built]);

  useEffect(
    () => () => {
      if (!built || !passes) return;
      built.texture.dispose();
      built.meshes[0].geometry.dispose();
      for (const p of passes) {
        (p.mesh.material as ShaderMaterial).dispose();
        p.target.dispose();
        p.quad.geometry.dispose();
        (p.quad.material as ShaderMaterial).dispose();
      }
    },
    [built, passes],
  );

  const last = useMemo(() => ({ view: new Matrix4(), projection: new Matrix4(), gain: -1, weight: -1, width: 0, height: 0 }), [passes]);
  useFrame(({ camera }) => {
    if (!built || !passes) return;
    const gain = LIGHT_PER_LSUN_PC2 * 2 ** stops * weight;
    const buffer = gl.getDrawingBufferSize(DRAWING);
    const scale = Math.min(MAX_RESOLUTION, Math.sqrt(PIXEL_BUDGET / Math.max(1, buffer.x * buffer.y)));
    const width = Math.max(1, Math.round(buffer.x * scale));
    const height = Math.max(1, Math.round(buffer.y * scale));
    camera.updateMatrixWorld();
    const moved =
      !last.view.equals(camera.matrixWorld) || !last.projection.equals(camera.projectionMatrix) || last.gain !== gain ||
      last.weight !== weight || last.width !== width || last.height !== height;
    const reattached = passes.some((p) => p.mesh.parent !== p.scene);
    for (const p of passes) if (p.mesh.parent !== p.scene) p.scene.add(p.mesh);
    if (!moved && !reattached) return;
    const eye: [number, number, number] = [camera.position.x, camera.position.y, camera.position.z];
    built.texture.image.data = sortedFrom(built.table, eye, built.sorted);
    built.texture.needsUpdate = true;
    const before = gl.getRenderTarget();
    for (const p of passes) {
      if (last.width !== width || last.height !== height) p.target.setSize(width, height);
      const u = (p.mesh.material as ShaderMaterial).uniforms;
      u.gain.value = gain;
      u.weight.value = weight;
      gl.setRenderTarget(p.target);
      // The transmission pass multiplies the frame by its image, so where no ray meets an object it must read 1,
      // not the 0 a black clear leaves (outside the objects' box the frame went black).
      gl.setClearColor(p.mesh === passes[1].mesh ? 0xffffff : 0x000000, 1);
      gl.clear(true, false, false);
      gl.render(p.scene, camera);
    }
    gl.setRenderTarget(before);
    gl.setClearColor(0x000000, 1);
    last.view.copy(camera.matrixWorld);
    last.projection.copy(camera.projectionMatrix);
    last.gain = gain;
    last.weight = weight;
    last.width = width;
    last.height = height;
  }, 0.5);

  return passes ? (
    <>
      <primitive object={passes[1].quad} />
      <primitive object={passes[0].quad} />
    </>
  ) : null;
}

const DRAWING = new Vector2();
