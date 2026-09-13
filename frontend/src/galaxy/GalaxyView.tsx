import { OrbitControls } from "@react-three/drei";
import { Canvas, type ThreeEvent } from "@react-three/fiber";
import { useMemo } from "react";

import { extent } from "./positions";
import styles from "./GalaxyView.module.css";

export type Preset = "face-on" | "edge-on" | "oblique";

interface Props {
  positions: Float32Array;
  colors: Float32Array;
  preset: Preset;
  onPick?: (row: number) => void;
}

/**
 * The sampled galaxy as a rotatable point cloud: drag to orbit, wheel to zoom
 * towards the cursor, right-drag to pan. A prototype of the 3D view: it draws
 * the materialised sample only; the smooth far field and per-cell stars at close
 * range are the two zoom regimes still to come.
 *
 * The canvas is transparent so the ground is the design system's --bg-deep from
 * CSS, not a colour written here.
 */
export function GalaxyView({ positions, colors, preset, onPick }: Props) {
  const reach = useMemo(() => extent(positions) || 20, [positions]);

  return (
    <div className={styles.view}>
      <Canvas
        key={preset} // a preset is a fresh camera; orbiting from there is the user's
        camera={{ position: cameraFor(preset, reach), fov: 45, near: reach / 1000, far: reach * 20 }}
        dpr={[1, 2]}
        gl={{ alpha: true, antialias: true }}
        raycaster={{ params: { Points: { threshold: reach / 400 } } as never }}
      >
        <Stars positions={positions} colors={colors} reach={reach} onPick={onPick} />
        <OrbitControls
          makeDefault
          enableDamping
          dampingFactor={0.12}
          zoomToCursor
          minDistance={reach / 200}
          maxDistance={reach * 8}
        />
      </Canvas>
    </div>
  );
}

function Stars({ positions, colors, reach, onPick }: Omit<Props, "preset"> & { reach: number }) {
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
        // paint a colour the field declaration never gave (design brief §3). A
        // glow belongs to the far-field regime, drawn from the density field.
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
