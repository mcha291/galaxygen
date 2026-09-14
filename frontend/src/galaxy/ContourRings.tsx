import { Billboard, Text } from "@react-three/drei";
import { useEffect, useMemo } from "react";
import { BufferAttribute, BufferGeometry, LineBasicMaterial, LineLoop } from "three";

const SEGMENTS = 128;

export interface Ring {
  level: number;
  /** Where the level sits now, kpc; null when the profile no longer reaches it. */
  radius: number | null;
  /** Where it sat on the unmoved disc, drawn faint so a move shows. */
  before: number | null;
}

interface Props {
  rings: Ring[];
  lift: number;
  colour: string;
  unit: string;
  fontSize: number;
}

/** Each ring's label at its own angle, so the inner rings' labels do not pile up on one line. */
function labelAt(radius: number, k: number, lift: number): [number, number, number] {
  const phi = 0.35 + 0.4 * k;
  return [radius * Math.cos(phi), lift, -radius * Math.sin(phi)];
}

/** A circle of radius 1 in the galaxy's plane, scaled per ring. */
function unitCircle(): BufferGeometry {
  const points = new Float32Array(SEGMENTS * 3);
  for (let j = 0; j < SEGMENTS; j += 1) {
    const phi = (j / SEGMENTS) * Math.PI * 2;
    points[j * 3] = Math.cos(phi);
    points[j * 3 + 2] = -Math.sin(phi);
  }
  const g = new BufferGeometry();
  g.setAttribute("position", new BufferAttribute(points, 3));
  return g;
}

/**
 * Contour rings of a surface density at fixed levels over the disc: solid where
 * the level sits now, faint where it sat before anything moved it, labelled
 * with the level. The disc is axisymmetric at these checkpoints, so a ring is a
 * circle and all the information is in its radius.
 */
export function ContourRings({ rings, lift, colour, unit, fontSize }: Props) {
  const circle = useMemo(unitCircle, []);
  const now = useMemo(() => new LineBasicMaterial({ color: colour, transparent: true, opacity: 0.75, depthWrite: false }), [colour]);
  const was = useMemo(() => new LineBasicMaterial({ color: colour, transparent: true, opacity: 0.22, depthWrite: false }), [colour]);
  useEffect(() => () => circle.dispose(), [circle]);
  useEffect(() => () => {
    now.dispose();
    was.dispose();
  }, [now, was]);

  // Rebuilt only when a ring moves, which during playback is once per merger.
  const lines = useMemo(() => {
    const loop = (radius: number | null, material: LineBasicMaterial) => {
      if (radius === null) return null;
      const line = new LineLoop(circle, material);
      line.scale.setScalar(radius);
      line.position.y = lift;
      line.renderOrder = 1;
      return line;
    };
    return rings.map((ring) => ({ ...ring, now: loop(ring.radius, now), was: loop(ring.before, was) }));
  }, [rings, circle, now, was, lift]);

  return (
    <group>
      {lines.map(({ level, radius, now: current, was: previous }, k) => (
        <group key={level}>
          {previous && <primitive object={previous} />}
          {current && radius !== null && (
            <>
              <primitive object={current} />
              <Billboard position={labelAt(radius, k, lift)}>
                <Text fontSize={fontSize} color={colour} anchorX="left" anchorY="bottom" outlineWidth={fontSize * 0.03} outlineColor="#05060a">
                  {`${level} ${unit}`}
                </Text>
              </Billboard>
            </>
          )}
        </group>
      ))}
    </group>
  );
}
