import { OrbitControls } from "@react-three/drei";
import { Canvas, type ThreeEvent, useFrame, useThree } from "@react-three/fiber";
import { type ReactNode, useEffect, useMemo, useRef } from "react";
import { ACESFilmicToneMapping, AdditiveBlending, Color, NormalBlending, type PerspectiveCamera } from "three";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
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
}

interface Props {
  /** The star sample; omitted where a checkpoint has no stars yet. */
  positions?: Float32Array | null;
  colors?: Float32Array | null;
  /** Framing radius in kpc when there are no stars to frame on. */
  reach?: number;
  /** Extra layers drawn in the galaxy's frame (a disc image, for instance). */
  children?: ReactNode;
  preset: Preset;
  onPick?: (row: number) => void;
  /** Set to move the camera to this zoom; the view reports every change through onView. */
  zoom?: number;
  onView?: (view: ViewState) => void;
  /** Photometric mode: colours are radiance, summed additively and tone-mapped once (RENDER_PLAN R1). */
  photometric?: boolean;
}

const FOV = 45;

/**
 * The sampled galaxy as a rotatable point cloud: drag to orbit, wheel to zoom
 * towards the cursor, right-drag to pan. It draws the materialised sample only;
 * the smooth far field and per-cell stars at close range are still to come.
 *
 * The canvas is transparent so the ground is the design system's --bg-deep from
 * CSS, not a colour written here.
 */
export function GalaxyView({ positions, colors, reach: framing, children, preset, onPick, zoom, onView, photometric = false }: Props) {
  const reach = useMemo(() => (positions ? extent(positions) : 0) || framing || 20, [positions, framing]);
  const range = useMemo<ZoomRange>(() => ({ min: reach / 200, max: reach * 8 }), [reach]);

  return (
    <div className={styles.view}>
      <Canvas
        key={`${preset}:${photometric}`} // a preset is a fresh camera; orbiting from there is the user's
        camera={{ position: cameraFor(preset, reach), fov: FOV, near: reach / 1000, far: reach * 20 }}
        dpr={[1, 2]}
        gl={{ alpha: true, antialias: true }}
        raycaster={{ params: { Points: { threshold: reach / 400 } } as never }}
      >
        {children}
        {positions && colors && <Stars positions={positions} colors={colors} reach={reach} onPick={onPick} additive={photometric} />}
        {photometric && <HdrOutput />}
        <OrbitControls makeDefault enableDamping dampingFactor={0.12} zoomToCursor minDistance={range.min} maxDistance={range.max} />
        <ZoomBridge range={range} zoom={zoom} onView={onView} />
      </Canvas>
    </div>
  );
}

/** Keeps the camera distance and an outside zoom slider in step, in both directions. */
function ZoomBridge({ range, zoom, onView }: { range: ZoomRange; zoom?: number; onView?: (v: ViewState) => void }) {
  const camera = useThree((s) => s.camera) as PerspectiveCamera;
  const controls = useThree((s) => s.controls) as OrbitControlsImpl | null;
  const size = useThree((s) => s.size);
  const reported = useRef<number | null>(null);

  useEffect(() => {
    if (!controls) return;
    const report = () => {
      const d = camera.position.distanceTo(controls.target);
      const z = zoomOf(d, range);
      const across = acrossOf(d, FOV, size.width / Math.max(size.height, 1));
      if (reported.current !== null && Math.abs(reported.current - z) < 1e-3) return;
      reported.current = z;
      onView?.({ zoom: z, across, pxPerKpc: size.width / across });
    };
    reported.current = null;
    report();
    controls.addEventListener("change", report);
    return () => controls.removeEventListener("change", report);
  }, [camera, controls, range, size, onView]);

  useEffect(() => {
    if (!controls || zoom === undefined) return;
    if (reported.current !== null && Math.abs(reported.current - zoom) < 1e-3) return;
    const direction = camera.position.clone().sub(controls.target).normalize();
    camera.position.copy(controls.target).addScaledVector(direction, distanceOf(zoom, range));
    controls.update();
  }, [zoom, camera, controls, range]);

  return null;
}

/**
 * Light is additive, so in photometric mode the stars are summed into a half-float
 * target, where a core of a thousand giants is a thousand times one giant, and
 * tone-mapped once on the way to the screen (ACES filmic). Tone-mapping each star
 * as it is drawn would clip it to white before the sum, which is the failure the
 * normal-blending choice below was a workaround for.
 */
function HdrOutput() {
  const gl = useThree((s) => s.gl);
  const scene = useThree((s) => s.scene);
  const camera = useThree((s) => s.camera);
  const size = useThree((s) => s.size);
  const composer = useMemo(() => {
    const c = new EffectComposer(gl); // half-float render targets by default
    c.addPass(new RenderPass(scene, camera));
    c.addPass(new OutputPass()); // tone mapping and the sRGB encode, once
    return c;
  }, [gl, scene, camera]);
  useEffect(() => {
    const before = { toneMapping: gl.toneMapping, clear: gl.getClearColor(new Color()), alpha: gl.getClearAlpha() };
    gl.toneMapping = ACESFilmicToneMapping;
    // The sum needs an opaque ground: additive light over a transparent canvas leaves the
    // alpha of the brightest star, and the page would show through the galaxy. The ground
    // is the design system's deep background, read from its token.
    const ground = getComputedStyle(document.documentElement).getPropertyValue("--bg-deep").trim();
    gl.setClearColor(new Color(ground || "#05060a"), 1);
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

function Stars({ positions, colors, reach, onPick, additive = false }: {
  positions: Float32Array; colors: Float32Array; reach: number; onPick?: (row: number) => void; additive?: boolean;
}) {
  const pick = (event: ThreeEvent<MouseEvent>) => {
    if (event.index === undefined) return;
    event.stopPropagation(); // the nearest star only, not every star behind it
    onPick?.(event.index);
  };
  return (
    <points onClick={pick}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
        <bufferAttribute attach="attributes-color" args={[colors, 3]} />
      </bufferGeometry>
      <pointsMaterial
        vertexColors
        map={psfTexture()} // RENDER_PLAN R2: a point spread function, not a square
        alphaTest={0.01}
        size={reach / 70} // the PSF's wings need room: its bright core stays about 2 px at the preset distance
        sizeAttenuation
        // Scientific mode blends normally: overlapping stars adding up to white would paint a
        // colour the field declaration never gave (design brief §3). Photometric mode adds,
        // because light does, and the sum is tone-mapped by HdrOutput rather than clipped.
        blending={additive ? AdditiveBlending : NormalBlending}
        transparent
        opacity={1}
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
