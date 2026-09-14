import { useFrame } from "@react-three/fiber";
import { useEffect, useMemo, useRef } from "react";
import { BufferAttribute, BufferGeometry, Color, Points, PointsMaterial } from "three";

import { psfTexture } from "./psf";
import { omegas, tracerPositions } from "./shear";

interface Props {
  /** The grid's radius centres and the published circular velocity on them. */
  R: ArrayLike<number>;
  v: ArrayLike<number>;
  /** The rings the tracers ride, kpc. */
  rings: number[];
  playing: boolean;
  /** Myr of galactic time per second of wall time. */
  speed: number;
  /** Changing this puts every tracer back where it started, at t = 0. */
  resetKey: number;
  onTime?: (tMyr: number) => void;
  perRing?: number;
  lift: number;
}

/** The token's colour, read once: tracers are chrome over data, not data. */
function tokenColour(name: string): Color {
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return new Color(value || "white");
}

/**
 * Tracer points on circular orbits over the disc: a handful per ring, each ring
 * turning at Ω(R) = v_c(R)/R. Not stars — there are none at this checkpoint —
 * only markers that make the rotation curve visible as rings sliding past one
 * another.
 */
export function Tracers({ R, v, rings, playing, speed, resetKey, onTime, perRing = 12, lift }: Props) {
  const omega = useMemo(() => omegas(rings, R, v), [rings, R, v]);

  const object = useMemo(() => {
    const geometry = new BufferGeometry();
    geometry.setAttribute("position", new BufferAttribute(tracerPositions(rings, omega, perRing, 0, lift), 3));
    const material = new PointsMaterial({
      color: tokenColour("--ink-1"),
      map: psfTexture(),
      size: 16, // the PSF's bright core is about a third of the sprite
      sizeAttenuation: false, // markers, so a fixed size on screen at any zoom
      transparent: true,
      alphaTest: 0.01,
      depthWrite: false,
    });
    const points = new Points(geometry, material);
    points.renderOrder = 2;
    return points;
  }, [rings, omega, perRing, lift]);
  useEffect(() => () => {
    object.geometry.dispose();
    (object.material as PointsMaterial).dispose();
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
    tracerPositions(rings, omega, perRing, t.current, lift, attr.array as Float32Array);
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
