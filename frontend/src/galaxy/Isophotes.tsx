import { useEffect, useMemo } from "react";
import { BufferAttribute, BufferGeometry, Color, LineBasicMaterial, LineLoop } from "three";

const SEGMENTS = 160;

interface Props {
  /** Ring radii in kpc, one per level. */
  rings: number[];
  lift: number;
}

/**
 * Isophotes of an axisymmetric disc: unlabelled circles where the surface
 * density crosses fixed levels. On an exponential disc they fall evenly spaced,
 * one scale length times ln 10 per decade, so the spacing reads as the scale
 * length without a colour bar.
 */
export function Isophotes({ rings, lift }: Props) {
  const circle = useMemo(() => {
    const points = new Float32Array(SEGMENTS * 3);
    for (let j = 0; j < SEGMENTS; j += 1) {
      const phi = (j / SEGMENTS) * Math.PI * 2;
      points[j * 3] = Math.cos(phi);
      points[j * 3 + 2] = -Math.sin(phi);
    }
    const g = new BufferGeometry();
    g.setAttribute("position", new BufferAttribute(points, 3));
    return g;
  }, []);
  const material = useMemo(() => {
    const value = getComputedStyle(document.documentElement).getPropertyValue("--ink-1").trim();
    return new LineBasicMaterial({ color: new Color(value || "white"), transparent: true, opacity: 0.45, depthWrite: false });
  }, []);
  useEffect(() => () => {
    circle.dispose();
    material.dispose();
  }, [circle, material]);

  const loops = useMemo(
    () =>
      rings.map((radius) => {
        const line = new LineLoop(circle, material);
        line.scale.setScalar(radius);
        line.position.y = lift;
        line.renderOrder = 1;
        return line;
      }),
    [rings, circle, material, lift],
  );

  return (
    <group>
      {loops.map((line, i) => (
        <primitive key={i} object={line} />
      ))}
    </group>
  );
}
