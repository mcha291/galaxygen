import { OrbitControls } from "@react-three/drei";
import { Canvas, type ThreeEvent, useFrame, useThree } from "@react-three/fiber";
import { type ReactNode, useEffect, useMemo, useRef } from "react";
import { ACESFilmicToneMapping, AdditiveBlending, Color, NormalBlending, type PerspectiveCamera, Vector2 } from "three";
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
        raycaster={{ params: { Points: { threshold: reach / 400 } } as never }}
      >
        {children}
        {layers.map((layer, i) => (
          <Stars key={i} layer={layer} reach={reach} additive={additive} />
        ))}
        {hdr && <HdrOutput />}
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
  const reported = useRef<{ zoom: number; x: number; z: number } | null>(null);

  useEffect(() => {
    if (!controls) return;
    const report = () => {
      const d = camera.position.distanceTo(controls.target);
      const z = zoomOf(d, range);
      const across = acrossOf(d, FOV, size.width / Math.max(size.height, 1));
      const { x, y, z: tz } = controls.target;
      const last = reported.current;
      // A pan matters as well as a zoom now: close up, where the view looks decides which stars load.
      if (last && Math.abs(last.zoom - z) < 1e-3 && Math.hypot(last.x - x, last.z - tz) < across / 20) return;
      reported.current = { zoom: z, x, z: tz };
      onView?.({ zoom: z, across, pxPerKpc: size.width / across, target: [x, y, tz] });
    };
    reported.current = null;
    report();
    controls.addEventListener("change", report);
    return () => controls.removeEventListener("change", report);
  }, [camera, controls, range, size, onView]);

  useEffect(() => {
    if (!controls || zoom === undefined) return;
    if (reported.current !== null && Math.abs(reported.current.zoom - zoom) < 1e-3) return;
    const direction = camera.position.clone().sub(controls.target).normalize();
    camera.position.copy(controls.target).addScaledVector(direction, distanceOf(zoom, range));
    controls.update();
  }, [zoom, camera, controls, range]);

  return null;
}

/**
 * Light is additive, so it is summed into a half-float target, where a core of a thousand
 * giants is a thousand times one giant, and tone-mapped once on the way to the screen (ACES
 * filmic). Tone-mapping each star as it is drawn would clip it to white before the sum.
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
    gl.toneMapping = ACESFilmicToneMapping;
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

function Stars({ layer, reach, additive }: { layer: StarLayer; reach: number; additive: boolean }) {
  const opacity = layer.opacity ?? 1;
  const pick = (event: ThreeEvent<MouseEvent>) => {
    if (event.index === undefined || !layer.onPick || opacity < 0.05) return;
    event.stopPropagation(); // the nearest star only, not every star behind it
    layer.onPick(event.index);
  };
  return (
    <points onClick={pick} visible={opacity > 0.01}>
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
