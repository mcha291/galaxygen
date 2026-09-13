import { discOf } from "@interface/field.js";
import { paintOf } from "@interface/ramp.js";
import { useEffect, useMemo } from "react";
import { DataTexture, DoubleSide, LinearFilter, RGBAFormat, SRGBColorSpace } from "three";

import type { FieldDecl, FieldsPayload } from "../api";
import type { Axis } from "../preview/axes";
import { polarImage } from "./polar";

interface Props {
  decl: FieldDecl;
  /** One value per R cell. */
  profile: ArrayLike<number>;
  R: Axis;
  cmaps: FieldsPayload["cmaps"];
  /** Paint against these values' range rather than the profile's own, so a scrubbed epoch keeps one scale. */
  rangeValues?: ArrayLike<number>;
  /** A published (R, φ) factor to multiply the profile by: the bar and arms. */
  contrast?: ArrayLike<number>;
  phi?: Axis;
  size?: number;
}

/**
 * A radial profile swept into a face-on disc, laid in the galaxy's plane so it
 * orbits with the camera like the stars do.
 *
 * Scientific mode (RENDER_PLAN §0): the pixels are the field painted by its
 * declared ramp through interface/field.js, nearest cell, transparent off the
 * grid. It is a picture of a field, not a photograph, and says so by its colours.
 */
export function DiscLayer({ decl, profile, R, cmaps, rangeValues, contrast, phi, size = 512 }: Props) {
  const ramp = useMemo(() => paintOf(decl, cmaps, rangeValues ?? profile), [decl, cmaps, rangeValues, profile]);
  const texture = useMemo(() => {
    const { data, width, height } =
      contrast && phi ? polarImage(profile, contrast, R, phi, ramp, size) : discOf(profile, R, ramp, { size, rMax: R.hi });
    const t = new DataTexture(data, width, height, RGBAFormat);
    t.colorSpace = SRGBColorSpace;
    t.minFilter = LinearFilter;
    t.magFilter = LinearFilter;
    t.needsUpdate = true;
    return t;
  }, [profile, R, ramp, size, contrast, phi]);
  useEffect(() => () => texture.dispose(), [texture]);

  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} renderOrder={-1}>
      <planeGeometry args={[2 * R.hi, 2 * R.hi]} />
      <meshBasicMaterial map={texture} transparent depthWrite={false} side={DoubleSide} toneMapped={false} />
    </mesh>
  );
}
