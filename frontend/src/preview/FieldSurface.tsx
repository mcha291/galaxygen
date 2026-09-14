import { paintOf } from "@interface/ramp.js";
import { Billboard, Grid, Text } from "@react-three/drei";
import { useMemo } from "react";
import { BufferAttribute, BufferGeometry, Color, DoubleSide } from "three";

import type { FieldDecl, FieldsPayload } from "../api";
import { interp } from "../galaxy/shear";
import { type Axis, centres, linearTicks } from "./axes";
import { contourLevels, contourRings, heightAxisLabel, heightOf, heightScaleOf, polarSurface } from "./surface";

/** How tall the surface stands, in the scene's kpc. A display choice, made once. */
const RELIEF = 9;
const RING_COLOUR = "#cfd6e4";
const AXIS_COLOUR = "#7c8798";

/**
 * The surface's height in the scene at radius r, for anything laid on it (the
 * shearing spokes). Linear between cell centres, as the mesh is; null when the
 * profile has no scale and no surface is drawn.
 */
export function surfaceHeightAt(profile: ArrayLike<number>, R: Axis, clearance = 0.05): ((r: number) => number) | null {
  const scale = heightScaleOf(profile);
  if (!scale) return null;
  const radii = centres(R);
  return (r) => heightOf(interp(r, radii, profile), scale) * RELIEF + clearance;
}

interface Props {
  decl: FieldDecl;
  profile: ArrayLike<number>;
  R: Axis;
  cmaps: FieldsPayload["cmaps"];
  /** Contour rings per decade of the value. Two gives a ring every half decade. */
  perDecade?: number;
}

/**
 * A radial profile as a surface plot: height for the value, contour rings, a grid
 * plane and labelled axes.
 *
 * **Why this and not the face-on disc.** Checkpoints 1 and 2 publish Σ(R) and
 * nothing more — a 1D function. Swept into a disc it becomes a 2D image whose
 * second axis carries no information, and the resemblance to a galaxy does the
 * talking. The galaxy view at checkpoints 5 and 6 shows objects at real
 * positions; this shows a constructed function. They should not look alike, and
 * the axes, the grid and the rings are what say so.
 *
 * **Why height is allowed here.** In a scene, z means kiloparsecs above the
 * midplane — the disc has a real scale height and the star sample is positioned
 * at a real z, so displacing a surface by density would put two meanings on one
 * channel. In a chart, the vertical axis means whatever it is labelled. That is
 * the whole of the difference, and it is why this component carries axis labels
 * rather than treating them as decoration.
 *
 * The height is log for anything spanning more than a decade, which an
 * exponential disc always does. So the relief is **not** proportional to the
 * quantity, and the axis label says `log₁₀` when that is the case.
 */
export function FieldSurface({ decl, profile, R, cmaps, perDecade = 2 }: Props) {
  const radii = useMemo(() => {
    const out = new Float64Array(profile.length);
    for (let i = 0; i < out.length; i += 1) out[i] = R.lo + (i + 0.5) * R.width;
    return out;
  }, [profile.length, R.lo, R.width]);

  const scale = useMemo(() => heightScaleOf(profile), [profile]);

  const geometry = useMemo(() => {
    if (!scale) return null;
    const mesh = polarSurface(profile, radii, scale, 128);
    const g = new BufferGeometry();
    // z arrives normalised so the exaggeration lives in one place.
    const pos = mesh.positions;
    for (let i = 2; i < pos.length; i += 3) pos[i] *= RELIEF;
    g.setAttribute("position", new BufferAttribute(pos, 3));
    g.setIndex(new BufferAttribute(mesh.indices, 1));

    // Painted by the field's own declared ramp, never a table held here (rule A9).
    const ramp = paintOf(decl, cmaps, profile);  // .color(v) -> [r, g, b, a], 0-255
    const colours = new Float32Array((pos.length / 3) * 3);
    const c = new Color();
    for (let i = 0; i < mesh.rings; i += 1) {
      const [r, gg, b, a] = ramp.color(profile[i]);
      // Nothing drawn for a non-number (rule B9): the surface keeps the base colour
      // rather than reading as a value of zero.
      if (a === 0) c.setRGB(0.08, 0.09, 0.12);
      else c.setRGB(r / 255, gg / 255, b / 255).convertSRGBToLinear();
      for (let j = 0; j < mesh.spokes; j += 1) {
        const k = (i * mesh.spokes + j) * 3;
        colours[k] = c.r;
        colours[k + 1] = c.g;
        colours[k + 2] = c.b;
      }
    }
    g.setAttribute("color", new BufferAttribute(colours, 3));
    g.computeVertexNormals();
    return g;
  }, [profile, radii, scale, decl, cmaps]);

  const rings = useMemo(() => {
    if (!scale) return [];
    return contourRings(profile, radii, contourLevels(scale, perDecade)).map(({ level, radius }) => {
      const points = new Float32Array(129 * 3);
      const z = heightOf(level, scale) * RELIEF + 0.02; // just clear of the surface
      for (let j = 0; j <= 128; j += 1) {
        const phi = (j / 128) * Math.PI * 2;
        points[j * 3] = radius * Math.cos(phi);
        points[j * 3 + 1] = radius * Math.sin(phi);
        points[j * 3 + 2] = z;
      }
      const g = new BufferGeometry();
      g.setAttribute("position", new BufferAttribute(points, 3));
      return { level, radius, geometry: g };
    });
  }, [profile, radii, scale, perDecade]);

  if (!scale || !geometry) return null;

  const rTicks = linearTicks(0, R.hi, 4).filter((t) => t > 0);
  // The 3D text font has no subscript digits; they would draw as boxes.
  const label = heightAxisLabel(decl.label, String(decl.unit_display ?? decl.unit ?? ""), scale).replace(/[₀-₉]/g, (d) =>
    String(d.charCodeAt(0) - 0x2080),
  );

  return (
    // Built z-up; the scene is y-up with φ running x → −z, as the stars are.
    // Rotating −π/2 about x takes (r cos φ, r sin φ, h) to (r cos φ, h, −r sin φ).
    <group rotation={[-Math.PI / 2, 0, 0]}>
      {/* A grid plane under the surface: charts have them, galaxies do not. */}
      <Grid
        args={[R.hi * 2, R.hi * 2]}
        cellSize={R.hi / 10}
        sectionSize={R.hi / 2}
        cellColor="#243044"
        sectionColor="#33425c"
        fadeDistance={R.hi * 4}
        rotation={[Math.PI / 2, 0, 0]}
        position={[0, 0, 0]}
      />

      <mesh geometry={geometry}>
        <meshStandardMaterial vertexColors side={DoubleSide} roughness={0.85} metalness={0} />
      </mesh>
      <ambientLight intensity={1.1} />
      <directionalLight position={[R.hi, R.hi, R.hi * 2]} intensity={1.4} />

      {rings.map(({ level, geometry: g }) => (
        <lineLoop key={level} geometry={g}>
          <lineBasicMaterial color={RING_COLOUR} transparent opacity={0.45} />
        </lineLoop>
      ))}

      {/* Radial ticks, in kpc, on the grid plane. */}
      {rTicks.map((t) => (
        <Billboard key={t} position={[t, 0, 0.4]}>
          <Text fontSize={R.hi / 22} color={AXIS_COLOUR} anchorX="center" anchorY="middle">
            {t}
          </Text>
        </Billboard>
      ))}
      <Billboard position={[R.hi * 0.72, 0, -R.hi / 12]}>
        <Text fontSize={R.hi / 20} color={AXIS_COLOUR} anchorX="center" anchorY="middle">
          R (kpc)
        </Text>
      </Billboard>

      {/* The vertical axis, with its scale said in full: a log height is not
          proportional to the quantity, and a surface that does not say so is
          exactly the misleading thing this construction exists to avoid. */}
      <Billboard position={[0, -R.hi * 0.9, RELIEF * 0.55]}>
        <Text fontSize={R.hi / 20} color={AXIS_COLOUR} anchorX="center" anchorY="middle">
          {label}
        </Text>
      </Billboard>
      {rings.length > 0 && (
        <Billboard position={[0, -R.hi * 0.9, RELIEF * 0.35]}>
          <Text fontSize={R.hi / 26} color={AXIS_COLOUR} anchorX="center" anchorY="middle">
            {`rings every ${(1 / perDecade).toFixed(1)} dex`}
          </Text>
        </Billboard>
      )}
    </group>
  );
}
