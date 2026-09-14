import { useEffect, useMemo } from "react";
import { type Color, DoubleSide, LatheGeometry, MeshBasicMaterial, Vector2 } from "three";

const SEGMENTS = 128;

interface Props {
  /** Closed (radius, height) lathe profile from envelopeProfile. */
  profile: Float64Array;
  colour: Color;
}

/**
 * The heated disc's envelope: a translucent surface of revolution at ±h(R), the
 * height matter moving up at σ_z reaches in the halo's potential. Real height
 * above the midplane, in the galaxy's frame, so it is read edge-on.
 */
export function Envelope({ profile, colour }: Props) {
  const geometry = useMemo(() => {
    const points: Vector2[] = [];
    for (let k = 0; k < profile.length; k += 2) points.push(new Vector2(profile[k], profile[k + 1]));
    return new LatheGeometry(points, SEGMENTS);
  }, [profile]);
  const material = useMemo(
    () => new MeshBasicMaterial({ color: colour, transparent: true, opacity: 0.22, side: DoubleSide, depthWrite: false }),
    [colour],
  );
  useEffect(() => () => geometry.dispose(), [geometry]);
  useEffect(() => () => material.dispose(), [material]);

  return <mesh geometry={geometry} material={material} renderOrder={1} />;
}
