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
import { echoedLayer } from "./layer";
import { type LineWeights, MAX_OBJECTS, OBJECT_FLOATS, cloudInterior, packObjects, regionFragment, sortedFrom } from "./region";
import type { RegionWindow } from "./regimes";

/** The most pixels the region is marched at (as FieldVolume's budget): the loop over objects runs per pixel. */
const PIXEL_BUDGET = 400_000;
const MAX_RESOLUTION = 0.5;

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

// The march's fragment shader is region.ts's `regionFragment`: built for the census it draws, with the cloud
// interior's noise as that census's header publishes it (S55, D214 §5), or smooth where there is none to draw.

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
  /**
   * Told why the clouds' interiors are drawn smooth where that is not the layer's switch (S55): the model publishes
   * no noise, or one the viewer's normaliser was not measured for. Null while they are drawn as published, while
   * the layer is off, and when the volume goes.
   */
  onInterior?: (note: string | null) => void;
}

/**
 * The region regime (BUILD_II V3): a window's clouds, HII regions and bubble shells drawn from the published
 * vectors (RENDER_PHYSICS §5), marched per pixel front to back. Emission is added to the frame; the clouds'
 * transmission multiplies what lies behind them in a second pass — the field and the stars alike, a star in front
 * of a cloud included (an approximation of the composite, stated in HANDOFF_S40). The line's per-filter weight and
 * the dust's extinction ratios are the model's (`/api/render` at the region's level), the white point the viewer's.
 */
export function RegionVolume({ query, window, level, clusters, stops, weight, filterSet = "rgb", whiteKelvin = WHITE_KELVIN, onInterior }: Props) {
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
    // The clouds' interiors (S55): the noise this census's own header publishes, or smooth - the physics alone
    // where the header says the layer is off, and where there is no noise the viewer can evaluate (said in `note`).
    const interior = cloudInterior(echoedLayer(clouds.header) === "off", clouds.header);
    const fragment = regionFragment(interior.noise);
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
        fragmentShader: fragment,
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
    return { table, texture, meshes, sorted: new Float32Array(MAX_OBJECTS * OBJECT_FLOATS), note: interior.note };
  }, [clouds, clusters, remnants, rendered]);

  // Why the interiors are smooth, where it is not the switch: said on the page by the tab, unsaid when this goes.
  const note = built?.note ?? null;
  useEffect(() => {
    onInterior?.(note);
    return () => onInterior?.(null);
  }, [note]); // eslint-disable-line react-hooks/exhaustive-deps -- the tab's setter; the note is what changes

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
