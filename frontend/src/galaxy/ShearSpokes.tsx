import { useFrame } from "@react-three/fiber";
import { useEffect, useMemo, useRef } from "react";
import { BufferAttribute, BufferGeometry, Color, LineBasicMaterial, LineSegments } from "three";

import { omegas, spokeSegments } from "./shear";

interface Props {
  /** The grid's radius centres and the published circular velocity on them. */
  R: ArrayLike<number>;
  v: ArrayLike<number>;
  rMax: number;
  playing: boolean;
  /** Myr of galactic time per second of wall time. */
  speed: number;
  /** Changing this puts the spokes back to straight lines at t = 0. */
  resetKey: number;
  onTime?: (tMyr: number) => void;
  spokes?: number;
  /** Scene height at radius r, to lie on a surface; flat just above the disc otherwise. */
  heightAt?: (r: number) => number;
}

const POINTS = 160;

/** The token's colour, read once: the spokes are chrome over data, not data. */
function tokenColour(name: string): Color {
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return new Color(value || "white");
}

/**
 * Straight radial spokes over the disc that shear with the rotation curve: each
 * point orbits at Ω(R) = v_c(R)/R, so the spokes wind into trailing spirals and
 * the rate they wind is the curve's shape made visible.
 */
export function ShearSpokes({ R, v, rMax, playing, speed, resetKey, onTime, spokes = 8, heightAt }: Props) {
  const radii = useMemo(() => {
    const lo = Math.max(R[0], rMax / 200);
    return Float64Array.from({ length: POINTS }, (_, i) => lo + ((rMax - lo) * i) / (POINTS - 1));
  }, [R, rMax]);
  const omega = useMemo(() => omegas(radii, R, v), [radii, R, v]);
  const lift = useMemo(() => (heightAt ? Float64Array.from(radii, heightAt) : rMax / 400), [radii, heightAt, rMax]);

  const object = useMemo(() => {
    const geometry = new BufferGeometry();
    geometry.setAttribute("position", new BufferAttribute(spokeSegments(radii, omega, spokes, 0, lift), 3));
    const material = new LineBasicMaterial({ color: tokenColour("--ink-1"), transparent: true, opacity: 0.55, depthWrite: false });
    const lines = new LineSegments(geometry, material);
    lines.renderOrder = 1;
    return lines;
  }, [radii, omega, spokes, lift]);
  useEffect(() => () => {
    object.geometry.dispose();
    (object.material as LineBasicMaterial).dispose();
  }, [object]);

  const t = useRef(0);
  const reported = useRef(-1);
  useEffect(() => {
    t.current = 0;
    onTime?.(0);
  }, [resetKey]); // eslint-disable-line react-hooks/exhaustive-deps

  useFrame((_, delta) => {
    if (playing) t.current += Math.min(delta, 0.1) * speed;
    const attr = object.geometry.getAttribute("position") as BufferAttribute;
    spokeSegments(radii, omega, spokes, t.current, lift, attr.array as Float32Array);
    attr.needsUpdate = true;
    // The label only needs whole Myr.
    const whole = Math.floor(t.current);
    if (whole !== reported.current) {
      reported.current = whole;
      onTime?.(t.current);
    }
  });

  return <primitive object={object} />;
}
