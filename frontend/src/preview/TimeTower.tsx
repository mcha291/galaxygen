import { useThree } from "@react-three/fiber";
import { useEffect, useMemo } from "react";
import { BufferAttribute, DoubleSide, LatheGeometry, MeshBasicMaterial, Plane, Vector2, Vector3 } from "three";

const SEGMENTS = 96;

interface Props {
  /** One lathe profile per ring level: (radius, height) pairs from wallProfile. */
  walls: Float64Array[];
  /** Linear RGB per t cell, the colour of every wall at that height. */
  colours: Float32Array;
  /** Height of the playback moment: walls below it are history, above it still to come. */
  now: number;
}

/**
 * Checkpoint 2's history tower: each fixed-Σ ring swept up through cosmic time
 * as a wall, stepping outward where a merger lands, coloured by the σ_z matter
 * forming at that time carries today. What has happened by the playback moment
 * is drawn solid; what is still to come, faint, so every merger's effect is
 * visible at once and the slice climbing the tower is the present.
 */
export function TimeTower({ walls, colours, now }: Props) {
  const gl = useThree((s) => s.gl);
  useEffect(() => {
    gl.localClippingEnabled = true;
  }, [gl]);

  const below = useMemo(() => new Plane(new Vector3(0, -1, 0), 0), []);
  const above = useMemo(() => new Plane(new Vector3(0, 1, 0), 0), []);
  below.constant = now;
  above.constant = -now;

  const materials = useMemo(
    () => ({
      past: new MeshBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.4, side: DoubleSide, depthWrite: false, clippingPlanes: [below] }),
      future: new MeshBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.08, side: DoubleSide, depthWrite: false, clippingPlanes: [above] }),
    }),
    [below, above],
  );
  useEffect(() => () => {
    materials.past.dispose();
    materials.future.dispose();
  }, [materials]);

  const geometries = useMemo(
    () =>
      walls.map((profile) => {
        const points: Vector2[] = [];
        for (let k = 0; k < profile.length; k += 2) points.push(new Vector2(profile[k], profile[k + 1]));
        const g = new LatheGeometry(points, SEGMENTS);
        // Lathe vertices run segment by segment, each through the whole profile;
        // two profile points per t cell, so point p takes cell p >> 1's colour.
        const count = (SEGMENTS + 1) * points.length;
        const rgb = new Float32Array(count * 3);
        for (let v = 0; v < count; v += 1) {
          const cell = (v % points.length) >> 1;
          rgb.set(colours.subarray(cell * 3, cell * 3 + 3), v * 3);
        }
        g.setAttribute("color", new BufferAttribute(rgb, 3));
        return g;
      }),
    [walls, colours],
  );
  useEffect(() => () => geometries.forEach((g) => g.dispose()), [geometries]);

  return (
    <group>
      {geometries.map((g, i) => (
        <group key={i}>
          <mesh geometry={g} material={materials.past} renderOrder={1} />
          <mesh geometry={g} material={materials.future} renderOrder={1} />
        </group>
      ))}
    </group>
  );
}
