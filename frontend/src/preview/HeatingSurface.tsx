import { paintOf } from "@interface/ramp.js";
import { Billboard, Grid, Text } from "@react-three/drei";
import { useEffect, useMemo } from "react";
import { BufferAttribute, BufferGeometry, Color, DoubleSide, Line, LineBasicMaterial } from "three";

import type { FieldDecl, FieldsPayload } from "../api";
import type { MergerEvent } from "../workflow/logic";
import { type Axis, centres, linearTicks } from "./axes";
import { type HeightScale, footprintOf, gridSurface, heightAxisLabel, heightOf } from "./surface";

const AXIS_COLOUR = "#7c8798";
const PLANE_COLOUR = "#cfd6e4";
const NAN_COLOUR = new Color(0.08, 0.09, 0.12);

interface Props {
  spreadDecl: FieldDecl;
  /** disc_radial_spread, (R, t) row-major. */
  spread: ArrayLike<number>;
  heatingDecl?: FieldDecl;
  /** disc_heating, one value per t cell. */
  heating?: ArrayLike<number>;
  R: Axis;
  t: Axis;
  mergers: MergerEvent[];
  cmaps: FieldsPayload["cmaps"];
}

/** A linear scale from a meaningful zero to the data's maximum; flat data still gets a scale. */
function zeroScale(values: ArrayLike<number>): HeightScale {
  let hi = 0;
  for (let i = 0; i < values.length; i += 1) if (Number.isFinite(values[i]) && values[i] > hi) hi = values[i];
  return { lo: 0, hi: hi > 0 ? hi : 1, log: false };
}

/** Subscript digits have no glyphs in the 3D text font. */
function plain(text: string): string {
  return text.replace(/[₀-₉]/g, (d) => String(d.charCodeAt(0) - 0x2080));
}

function linearColour(rgba: number[], out: Color): Color {
  // Nothing drawn for a non-number (rule B9): the base colour, never a value of zero.
  return rgba[3] === 0 ? out.copy(NAN_COLOUR) : out.setRGB(rgba[0] / 255, rgba[1] / 255, rgba[2] / 255).convertSRGBToLinear();
}

/**
 * Checkpoint 2 as a chart over (R, t): the radial spread a star born at (R, t)
 * carries today as the height, σ_z(t) as a curve along the R = 0 edge, and each
 * merger as a plane at its time. A chart, not a scene: t runs along the depth
 * axis, so every length here is in axis units and the labels say which.
 */
export function HeatingSurface({ spreadDecl, spread, heatingDecl, heating, R, t, mergers, cmaps }: Props) {
  const size = R.hi - R.lo; // the footprint is square, R's extent on both sides
  const relief = size * 0.3;
  const xOf = (r: number) => footprintOf(r, R.lo, R.hi, size);
  // Today nearest the default camera, the oldest stars at the back.
  const zOf = (time: number) => footprintOf(time, t.lo, t.hi, size);

  const scale = useMemo(() => zeroScale(spread), [spread]);

  const surface = useMemo(() => {
    const xs = Float64Array.from(centres(R), xOf);
    const zs = Float64Array.from(centres(t), zOf);
    const mesh = gridSurface(spread, xs, zs, scale);
    for (let i = 1; i < mesh.positions.length; i += 3) mesh.positions[i] *= relief;
    const g = new BufferGeometry();
    g.setAttribute("position", new BufferAttribute(mesh.positions, 3));
    g.setIndex(new BufferAttribute(mesh.indices, 1));
    // Painted by the field's own declared ramp (rule A9).
    const ramp = paintOf(spreadDecl, cmaps, spread);
    const colours = new Float32Array(mesh.positions.length);
    const c = new Color();
    for (let k = 0; k < spread.length; k += 1) {
      linearColour(ramp.color(spread[k]), c);
      colours.set([c.r, c.g, c.b], k * 3);
    }
    g.setAttribute("color", new BufferAttribute(colours, 3));
    g.computeVertexNormals();
    return g;
  }, [spread, spreadDecl, cmaps, R, t, scale, relief]); // eslint-disable-line react-hooks/exhaustive-deps

  const curve = useMemo(() => {
    if (!heatingDecl || !heating) return null;
    const sigma = zeroScale(heating);
    const zs = centres(t);
    const ramp = paintOf(heatingDecl, cmaps, heating);
    const positions = new Float32Array(zs.length * 3);
    const colours = new Float32Array(zs.length * 3);
    const c = new Color();
    for (let j = 0; j < zs.length; j += 1) {
      positions.set([xOf(R.lo) - size * 0.02, heightOf(heating[j], sigma) * relief, zOf(zs[j])], j * 3);
      linearColour(ramp.color(heating[j]), c);
      colours.set([c.r, c.g, c.b], j * 3);
    }
    const g = new BufferGeometry();
    g.setAttribute("position", new BufferAttribute(positions, 3));
    g.setAttribute("color", new BufferAttribute(colours, 3));
    return { line: new Line(g, new LineBasicMaterial({ vertexColors: true })), hi: sigma.hi };
  }, [heating, heatingDecl, cmaps, R, t, relief, size]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => () => surface.dispose(), [surface]);
  useEffect(
    () => () => {
      curve?.line.geometry.dispose();
      (curve?.line.material as LineBasicMaterial | undefined)?.dispose();
    },
    [curve],
  );

  const rTicks = linearTicks(R.lo, R.hi, 4);
  const tTicks = linearTicks(t.lo, t.hi, 5);
  const front = size / 2 + size * 0.06;
  const font = size / 36;
  const inRange = mergers.filter((m) => m.time >= t.lo && m.time <= t.hi);

  return (
    <group>
      <ambientLight intensity={1.1} />
      <directionalLight position={[size, size, size]} intensity={1.4} />
      {/* A grid plane under the surface: charts have them, galaxies do not. */}
      <Grid args={[size, size]} cellSize={size / 10} sectionSize={size / 2} cellColor="#243044" sectionColor="#33425c" fadeDistance={size * 4} />

      <mesh geometry={surface}>
        <meshStandardMaterial vertexColors side={DoubleSide} roughness={0.85} metalness={0} />
      </mesh>

      {curve && <primitive object={curve.line} />}

      {inRange.map((m, i) => (
        <group key={i} position={[0, 0, zOf(m.time)]}>
          <mesh position={[0, relief * 0.6, 0]} renderOrder={2}>
            <planeGeometry args={[size, relief * 1.2]} />
            <meshBasicMaterial color={PLANE_COLOUR} transparent opacity={0.1} side={DoubleSide} depthWrite={false} />
          </mesh>
          <Billboard position={[size / 2 + size * 0.04, relief * 1.25, 0]}>
            <Text fontSize={font * 0.85} color={AXIS_COLOUR} anchorX="left" anchorY="middle">
              {`merger 1:${Math.round(1 / m.mass_ratio)} · ${m.time} Gyr`}
            </Text>
          </Billboard>
        </group>
      ))}

      {rTicks.map((r) => (
        <Billboard key={`R${r}`} position={[xOf(r), 0, front]}>
          <Text fontSize={font} color={AXIS_COLOUR} anchorX="center" anchorY="middle">
            {r}
          </Text>
        </Billboard>
      ))}
      <Billboard position={[0, -size * 0.05, front + size * 0.06]}>
        <Text fontSize={font} color={AXIS_COLOUR} anchorX="center" anchorY="middle">
          {`R (${R.unit_display ?? "kpc"})`}
        </Text>
      </Billboard>

      {tTicks.map((time) => (
        <Billboard key={`t${time}`} position={[front, 0, zOf(time)]}>
          <Text fontSize={font} color={AXIS_COLOUR} anchorX="center" anchorY="middle">
            {time}
          </Text>
        </Billboard>
      ))}
      <Billboard position={[front + size * 0.16, 0, 0]}>
        <Text fontSize={font} color={AXIS_COLOUR} anchorX="center" anchorY="middle">
          {`t (${t.unit_display ?? "Gyr"}), birth time`}
        </Text>
      </Billboard>

      <Billboard position={[xOf(R.lo), relief * 1.35, -size / 2]}>
        <Text fontSize={font} color={AXIS_COLOUR} anchorX="center" anchorY="bottom">
          {`${plain(heightAxisLabel("height: radial spread", String(spreadDecl.unit_display ?? spreadDecl.unit ?? ""), scale))} · top ${scale.hi.toPrecision(3)}`}
        </Text>
      </Billboard>
      {curve && heatingDecl && (
        <Billboard position={[xOf(R.lo), relief * 1.15, size / 2]}>
          <Text fontSize={font} color={AXIS_COLOUR} anchorX="center" anchorY="bottom">
            {plain(`curve: σ_z(t), top ${curve.hi.toPrecision(3)} ${String(heatingDecl.unit_display ?? heatingDecl.unit ?? "")}`)}
          </Text>
        </Billboard>
      )}
    </group>
  );
}
