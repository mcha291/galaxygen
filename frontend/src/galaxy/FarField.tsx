import { paintOf } from "@interface/ramp.js";
import { useEffect, useMemo } from "react";
import { AdditiveBlending, DataTexture, DoubleSide, FloatType, LinearFilter, RGBAFormat } from "three";

import { type FieldsPayload, type Frame, type Query, loadArrays } from "../api";
import { useLoad } from "../useLoad";
import { srgbToLinear } from "./colors";
import { FAR_FIELD_PER_LSUN_PC2, farFieldImage } from "./unresolved";

const SIZE = 768;

interface Props {
  meta: FieldsPayload;
  query: Query;
  /** Exposure in stops, shared with the star points so the two layers keep their balance. */
  stops: number;
}

/**
 * The disc's unresolved light under the star sample (RENDER_PLAN R3): the published
 * surface brightness, in the published colour of that light, times the bar and arm
 * contrast when the model publishes one, attenuated by the published face-on dust
 * extinction as a mixed slab (R4). A plane in the galaxy's midplane, added
 * into the same half-float target as the stars and tone-mapped with them.
 *
 * It has no thickness, so edge-on it is a line: the vertical structure of the light
 * is not drawn yet.
 */
export function FarField({ meta, query, stops }: Props) {
  const declared = (name: string) => meta.fields.find((f) => f.name === name);
  const brightnessDecl = declared("disc_surface_brightness");
  const colourDecl = declared("disc_light_temperature");
  const contrastDecl = declared("pattern_density_contrast");
  const dustDecl = declared("dust_extinction_v");
  const names = [brightnessDecl, colourDecl, contrastDecl, dustDecl].filter((d) => !!d).map((d) => d!.name);
  const key = brightnessDecl && colourDecl ? JSON.stringify([names, query]) : null;
  const loaded = useLoad<Frame>(key, (signal) => loadArrays(names, query, signal));
  const frame = loaded.value && names.every((n) => n in loaded.value!.arrays) ? loaded.value : null;
  const R = frame?.header.grid.axes.R;

  const texture = useMemo(() => {
    if (!frame || !R || !brightnessDecl || !colourDecl) return null;
    const temperature = frame.arrays[colourDecl.name] as Float64Array;
    const paint = paintOf(colourDecl, meta.cmaps, temperature);
    const colour = new Float64Array(R.n * 3);
    for (let i = 0; i < R.n; i += 1) {
      const [r, g, b, a] = paint.color(temperature[i]);
      if (a === 0) colour.fill(Number.NaN, 3 * i, 3 * i + 3);
      else colour.set([srgbToLinear(r / 255), srgbToLinear(g / 255), srgbToLinear(b / 255)], 3 * i);
    }
    const contrast = contrastDecl && frame.header.grid.axes.phi
      ? { values: frame.arrays[contrastDecl.name] as Float64Array, phi: frame.header.grid.axes.phi }
      : undefined;
    const data = farFieldImage(frame.arrays[brightnessDecl.name] as Float64Array, colour, R, FAR_FIELD_PER_LSUN_PC2 * 2 ** stops, SIZE, contrast,
      dustDecl ? (frame.arrays[dustDecl.name] as Float64Array) : undefined);
    const t = new DataTexture(data, SIZE, SIZE, RGBAFormat, FloatType);
    t.minFilter = LinearFilter;
    t.magFilter = LinearFilter;
    t.needsUpdate = true;
    return t;
  }, [frame, R, brightnessDecl, colourDecl, contrastDecl, dustDecl, meta.cmaps, stops]);
  useEffect(() => () => texture?.dispose(), [texture]);

  if (!texture || !R) return null;
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} renderOrder={-1}>
      <planeGeometry args={[2 * R.hi, 2 * R.hi]} />
      <meshBasicMaterial map={texture} blending={AdditiveBlending} transparent depthWrite={false} side={DoubleSide} />
    </mesh>
  );
}
