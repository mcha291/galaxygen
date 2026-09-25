import { OrbitControls } from "@react-three/drei";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { type ReactNode, useEffect, useMemo, useRef } from "react";
import { AdditiveBlending, AgXToneMapping, Color, Matrix4, NormalBlending, type PerspectiveCamera, Vector2 } from "three";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";
import type { OrbitControls as OrbitControlsImpl } from "three-stdlib";

import { extent } from "./positions";
import { psfTexture } from "./psf";
import { type ZoomRange, acrossOf, distanceOf, zoomOf } from "./zoom";
import styles from "./GalaxyView.module.css";

export type Preset = "face-on" | "edge-on" | "oblique";

export interface ViewState {
  /** Slider position in [0, 1], 1 closest. */
  zoom: number;
  /** Width of the view at the orbit target, kpc. */
  across: number;
  /** Screen pixels per kpc at the orbit target, for a scale bar. */
  pxPerKpc: number;
  /** The orbit target in the scene, kpc: where a close view is looking. */
  target: [number, number, number];
}

/** A set of star points: positions and colours, how strongly drawn, and what a click on one does. */
export interface StarLayer {
  positions: Float32Array;
  colors: Float32Array;
  opacity?: number;
  onPick?: (row: number) => void;
}

interface Props {
  /** The star layers: the whole-galaxy sample and, close up, a region's own stars. */
  layers?: StarLayer[];
  /** Framing radius in kpc when there are no stars to frame on. */
  reach?: number;
  /** Extra layers drawn in the galaxy's frame (the field, a disc image). */
  children?: ReactNode;
  preset: Preset;
  /** Set to move the camera to this zoom; the view reports every change through onView. */
  zoom?: number;
  onView?: (view: ViewState) => void;
  /** Render into a half-float target and tone-map once: needed wherever light is drawn (RENDER_PLAN R1). */
  hdr?: boolean;
  /** The stars' colours are radiance, so they add rather than blend. */
  additive?: boolean;
}

const FOV = 45;
const BLOOM = { strength: 0.35, radius: 0.45, threshold: 1.0 };
const STAR_SPRITE_PX = 9;

/**
 * The galaxy in 3D: drag to orbit, wheel to zoom towards the cursor, right-drag to pan.
 * It composites whatever it is given: the field as a child, star layers on top.
 */
export function GalaxyView({ layers = [], reach: framing, children, preset, zoom, onView, hdr = false, additive = false }: Props) {
  const first = layers[0]?.positions;
  const reach = useMemo(() => (first ? extent(first) : 0) || framing || 20, [first, framing]);
  const range = useMemo<ZoomRange>(() => ({ min: reach / 200, max: reach * 8 }), [reach]);

  return (
    <div className={styles.view}>
      <Canvas
        key={`${preset}:${hdr}`} // a preset is a fresh camera; orbiting from there is the user's
        camera={{ position: cameraFor(preset, reach), fov: FOV, near: reach / 1000, far: reach * 20 }}
        dpr={[1, 2]}
        gl={{ alpha: true, antialias: true }}
      >
        {children}
        {layers.map((layer, i) => (
          <Stars key={i} layer={layer} additive={additive} />
        ))}
        {hdr && <HdrOutput />}
        <Picker layers={layers} />
        <OrbitControls makeDefault enableDamping dampingFactor={0.12} zoomToCursor minDistance={range.min} maxDistance={range.max} />
        <ZoomBridge range={range} zoom={zoom} onView={onView} />
      </Canvas>
    </div>
  );
}

/** Keeps the camera distance and an outside zoom slider in step, in both directions, and reports where the view is. */
function ZoomBridge({ range, zoom, onView }: { range: ZoomRange; zoom?: number; onView?: (v: ViewState) => void }) {
  const camera = useThree((s) => s.camera) as PerspectiveCamera;
  const controls = useThree((s) => s.controls) as OrbitControlsImpl | null;
  const size = useThree((s) => s.size);
  const reported = useRef<{ zoom: number; x: number; z: number; width: number; height: number } | null>(null);
  // Read through a ref, not listed as dependencies: the subscription below must not be torn down
  // and re-made on a render. It was, once per render, and each time it reported the view afresh;
  // the report set the parent's state, the parent rendered, the effect ran again, and the page
  // spent two thousand renders a second doing it until one more update locked it for good.
  const latest = useRef({ range, size, onView });
  latest.current = { range, size, onView };

  const report = useRef<(() => void) | null>(null);
  useEffect(() => {
    if (!controls) return;
    report.current = () => {
      const { range: r, size: s, onView: notify } = latest.current;
      const d = camera.position.distanceTo(controls.target);
      const z = zoomOf(d, r);
      const across = acrossOf(d, FOV, s.width / Math.max(s.height, 1));
      const { x, y, z: tz } = controls.target;
      const last = reported.current;
      // A pan matters as well as a zoom now: close up, where the view looks decides which stars load.
      if (
        last && Math.abs(last.zoom - z) < 1e-3 && Math.hypot(last.x - x, last.z - tz) < across / 20 &&
        last.width === s.width && last.height === s.height
      ) return;
      reported.current = { zoom: z, x, z: tz, width: s.width, height: s.height };
      notify?.({ zoom: z, across, pxPerKpc: s.width / across, target: [x, y, tz] });
    };
    const onChange = () => report.current?.();
    onChange();
    controls.addEventListener("change", onChange);
    return () => controls.removeEventListener("change", onChange);
  }, [camera, controls]);
  // A resize or a new zoom range changes what the view is without moving the camera.
  useEffect(() => report.current?.(), [size.width, size.height, range.min, range.max]);

  useEffect(() => {
    if (!controls || zoom === undefined) return;
    if (reported.current !== null && Math.abs(reported.current.zoom - zoom) < 1e-3) return;
    const direction = camera.position.clone().sub(controls.target).normalize();
    camera.position.copy(controls.target).addScaledVector(direction, distanceOf(zoom, latest.current.range));
    controls.update();
  }, [zoom, camera, controls]);

  return null;
}

/**
 * Light is additive, so it is summed into a half-float target, where a core of a thousand
 * giants is a thousand times one giant, and tone-mapped once on the way to the screen. Tone-mapping
 * each star as it is drawn would clip it to white before the sum.
 *
 * AgX, not ACES filmic: the colours here are published temperatures, and a tone curve should
 * change how bright they are, not what colour. ACES adds saturation in the shadows (a dim
 * 5000 K ring came out brown, R/B 1.59 → 1.89; a dim 9000 K one bluer, 0.67 → 0.58), and most
 * of a disc is dim. AgX holds the source's hue to within a few percent below unit intensity and
 * only whitens the brightest light, as film does.
 */
function HdrOutput() {
  const gl = useThree((s) => s.gl);
  const scene = useThree((s) => s.scene);
  const camera = useThree((s) => s.camera);
  const size = useThree((s) => s.size);
  const composer = useMemo(() => {
    const c = new EffectComposer(gl); // half-float render targets by default
    c.addPass(new RenderPass(scene, camera));
    // R5, kept restrained: only light above unit intensity blooms (the core, the brightest
    // giants), and not by much. Bloom is also the fastest way to make an instrument look like
    // a screensaver (RENDER_PLAN R5).
    c.addPass(new UnrealBloomPass(new Vector2(size.width, size.height), BLOOM.strength, BLOOM.radius, BLOOM.threshold));
    c.addPass(new OutputPass()); // tone mapping and the sRGB encode, once
    return c;
  }, [gl, scene, camera]); // eslint-disable-line react-hooks/exhaustive-deps -- resized below, not rebuilt
  useEffect(() => {
    const before = { toneMapping: gl.toneMapping, clear: gl.getClearColor(new Color()), alpha: gl.getClearAlpha() };
    gl.toneMapping = AgXToneMapping;
    // An opaque black ground: additive light over a transparent canvas leaves the alpha of the
    // brightest star, and light added to the design system's navy tints every faint pixel.
    gl.setClearColor(new Color(0, 0, 0), 1);
    return () => {
      gl.toneMapping = before.toneMapping;
      gl.setClearColor(before.clear, before.alpha);
      composer.dispose();
    };
  }, [gl, composer]);
  useEffect(() => composer.setSize(size.width, size.height), [composer, size]);
  // A positive priority takes the render over from react-three-fiber.
  useFrame(() => composer.render(), 1);
  return null;
}

/** How far from the cursor, in CSS pixels, a click still picks a star. */
const PICK_PX = 8;
/** A press that moves further than this is a drag, not a click. */
const DRAG_PX = 4;

/**
 * Clicking a star, in screen space. Every drawn star is projected and the nearest to the cursor
 * within PICK_PX is picked: linear in the stars, allocation-free, and the same at any zoom.
 *
 * Not three.js's raycaster. It tests points against a tolerance in *world* units, and one set
 * for the whole galaxy is half the screen close up, so every star of a dense region became a
 * hit; each hit allocated, the events system sorted and wrapped them all, and a click on a close
 * view of a quarter of a million stars locked the page.
 */
function Picker({ layers }: { layers: StarLayer[] }) {
  const gl = useThree((s) => s.gl);
  const camera = useThree((s) => s.camera);
  const current = useRef(layers);
  current.current = layers;

  useEffect(() => {
    const element = gl.domElement;
    let down: { x: number; y: number } | null = null;
    const onDown = (e: PointerEvent) => {
      down = { x: e.clientX, y: e.clientY };
    };
    const onUp = (e: PointerEvent) => {
      if (!down || Math.hypot(e.clientX - down.x, e.clientY - down.y) > DRAG_PX) return;
      down = null;
      const rect = element.getBoundingClientRect();
      const px = e.clientX - rect.left;
      const py = e.clientY - rect.top;
      camera.updateMatrixWorld();
      const m = new Matrix4().multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse).elements;
      let best: { layer: StarLayer; row: number; d2: number } | null = null;
      for (const layer of current.current) {
        if (!layer.onPick || (layer.opacity ?? 1) < 0.05) continue;
        const pos = layer.positions;
        for (let i = 0, row = 0; i < pos.length; i += 3, row += 1) {
          const x = pos[i];
          const y = pos[i + 1];
          const z = pos[i + 2];
          const w = m[3] * x + m[7] * y + m[11] * z + m[15];
          if (w <= 0) continue; // behind the camera
          const sx = ((m[0] * x + m[4] * y + m[8] * z + m[12]) / w + 1) * 0.5 * rect.width;
          const sy = (1 - (m[1] * x + m[5] * y + m[9] * z + m[13]) / w) * 0.5 * rect.height;
          const d2 = (sx - px) ** 2 + (sy - py) ** 2;
          if (d2 <= PICK_PX * PICK_PX && (!best || d2 < best.d2)) best = { layer, row, d2 };
        }
      }
      if (best) best.layer.onPick!(best.row);
    };
    element.addEventListener("pointerdown", onDown);
    element.addEventListener("pointerup", onUp);
    return () => {
      element.removeEventListener("pointerdown", onDown);
      element.removeEventListener("pointerup", onUp);
    };
  }, [gl, camera]);

  return null;
}

function Stars({ layer, additive }: { layer: StarLayer; additive: boolean }) {
  const opacity = layer.opacity ?? 1;
  return (
    // No pointer handlers: picking is the Picker's, in screen space.
    <points visible={opacity > 0.01}>
      <bufferGeometry key={layer.positions.length}>
        <bufferAttribute attach="attributes-position" args={[layer.positions, 3]} />
        <bufferAttribute attach="attributes-color" args={[layer.colors, 3]} />
      </bufferGeometry>
      <pointsMaterial
        vertexColors
        map={psfTexture()} // RENDER_PLAN R2: a point spread function, not a square
        alphaTest={0.01}
        // A star is a point at any distance, so its sprite keeps one size on screen: the PSF's wings
        // need about this many pixels for its bright core to stay near two.
        size={STAR_SPRITE_PX}
        sizeAttenuation={false}
        // Field colours blend normally: overlapping stars adding up to white would paint a colour
        // the field declaration never gave (design brief §3). Radiance adds, because light does.
        blending={additive ? AdditiveBlending : NormalBlending}
        transparent
        opacity={opacity}
        depthWrite={false}
      />
    </points>
  );
}

function cameraFor(preset: Preset, reach: number): [number, number, number] {
  const d = reach * 2.4;
  if (preset === "face-on") return [0, d, 0.0001]; // looking down -y; the offset keeps "up" defined
  if (preset === "edge-on") return [0, 0, d];
  return [0, d * 0.55, d * 0.85];
}
