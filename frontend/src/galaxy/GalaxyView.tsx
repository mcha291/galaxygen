import { OrbitControls } from "@react-three/drei";
import { Canvas, type ThreeEvent, useThree } from "@react-three/fiber";
import { useEffect, useMemo, useRef } from "react";
import type { PerspectiveCamera } from "three";
import type { OrbitControls as OrbitControlsImpl } from "three-stdlib";

import { extent } from "./positions";
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
  positions: Float32Array;
  colors: Float32Array;
  preset: Preset;
  onPick?: (row: number) => void;
  /** Set to move the camera to this zoom; the view reports every change through onView. */
  zoom?: number;
  onView?: (view: ViewState) => void;
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
export function GalaxyView({ positions, colors, preset, onPick, zoom, onView }: Props) {
  const reach = useMemo(() => extent(positions) || 20, [positions]);
  const range = useMemo<ZoomRange>(() => ({ min: reach / 200, max: reach * 8 }), [reach]);

  return (
    <div className={styles.view}>
      <Canvas
        key={preset} // a preset is a fresh camera; orbiting from there is the user's
        camera={{ position: cameraFor(preset, reach), fov: FOV, near: reach / 1000, far: reach * 20 }}
        dpr={[1, 2]}
        gl={{ alpha: true, antialias: true }}
        raycaster={{ params: { Points: { threshold: reach / 400 } } as never }}
      >
        <Stars positions={positions} colors={colors} reach={reach} onPick={onPick} />
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

function Stars({ positions, colors, reach, onPick }: Pick<Props, "positions" | "colors" | "onPick"> & { reach: number }) {
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
        size={reach / 150} // about 1.5 px at the preset distance; grows as the camera closes in
        sizeAttenuation
        // Normal blending, not additive: overlapping stars adding up to white would
        // paint a colour the field declaration never gave (design brief §3).
        transparent
        opacity={0.9}
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
