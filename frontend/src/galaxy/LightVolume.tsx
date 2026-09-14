import { paintOf } from "@interface/ramp.js";
import { useFrame } from "@react-three/fiber";
import { useEffect, useMemo } from "react";
import {
  AdditiveBlending,
  BufferAttribute,
  BufferGeometry,
  Points,
  ShaderMaterial,
  Vector2,
  Vector3,
} from "three";

import { type FieldsPayload, type Frame, type Query, loadArrays } from "../api";
import { useLoad } from "../useLoad";
import { srgbToLinear } from "./colors";
import { HII_RGB, type Particles, discLuminosity, sampleBulge, sampleDisc, seeded } from "./volume";

/**
 * How bright 1 L☉/pc² draws against a star point at zero exposure stops. A display
 * balance between the layers, not a physical constant: a point is one star and the
 * volume is a disc of them. At this value the inner disc's few hundred L☉/pc² sits
 * near unit intensity, as a 100 L☉ giant does.
 */
export const LIGHT_PER_LSUN_PC2 = 1 / 400;

/**
 * Extinction in the red, green and blue channels per magnitude of A_V: the R, V and B
 * bands of Cardelli, Clayton & Mathis at R_V = 3.1 standing in for the three channels
 * `[recall: CCM 1989, A_R/A_V = 0.748, A_B/A_V = 1.324]`. Dust dims blue more than red,
 * so a dusty region reddens as it darkens: occlusion, never an added colour (R4).
 */
export const CHANNEL_EXTINCTION = [0.748, 1.0, 1.324] as const;

// Particle budget. A display choice: enough disc particles that their smoothing overlaps
// into a surface, few enough emission knots that each is bright enough to see.
const DISC_PARTICLES = 600_000;
const HII_PARTICLES = 800;
const HII_CLUMP = 3;
/** An HII region is a few hundred parsecs across whatever the spacing between them. */
const HII_SIZE_PC = 120;
/**
 * The line's weight against the starlight in the viewer's channels. Starlight is drawn at its
 * bolometric luminosity, of which a population puts roughly a fifth into the red channel; the
 * line puts all of its light there. A display correction of the bolometric-to-channel mismatch,
 * not a measured ratio, and the reason the published Hα, a thousandth of the starlight, shows.
 */
const LINE_CHANNEL_WEIGHT = 5;
const BULGE_PARTICLES = 40_000;

const DRAWING = new Vector2();

const SCALARS = ["thin_disc_scale_height", "bulge_luminosity", "bulge_light_temperature", "bulge_scale_radius"];
const FIELDS = ["disc_surface_brightness", "disc_light_temperature", "pattern_density_contrast", "dust_extinction_v", "halpha_surface_brightness"];

interface Props {
  meta: FieldsPayload;
  query: Query;
  /** Exposure in stops, shared with the star points so the layers keep their balance. */
  stops: number;
}

const PARTICLE_VERTEX = /* glsl */ `
  attribute float size;
  attribute float tau;
  uniform float pxPerUnit;
  uniform float minPx;
  uniform float dustHeight;
  uniform vec3 extinction;
  varying vec3 vLight;
  void main() {
    vec4 world = modelMatrix * vec4(position, 1.0);
    // R4, per particle: the share of the dust column between this particle and the camera,
    // for dust in a tanh-profiled layer about the midplane, times the path's airmass. Seen
    // face-on it is half the column for a star in the midplane and none for one above the
    // dust; seen edge-on the airmass is long and the midplane goes dark: the lane.
    vec3 toCamera = normalize(cameraPosition - world.xyz);
    float side = toCamera.y >= 0.0 ? 1.0 : -1.0;
    float between = 0.5 * (1.0 - tanh(side * world.y / dustHeight));
    float airmass = 1.0 / max(abs(toCamera.y), 0.03);
    vec3 transmitted = exp(-tau * between * airmass * extinction);
    vec4 mv = viewMatrix * world;
    gl_Position = projectionMatrix * mv;
    // Never under a few pixels, or the kernel aliases into single-pixel grain; never so wide
    // the driver clamps it. Whatever size is drawn, its area is what the light is divided by.
    float pcPerPx = 1000.0 * -mv.z / pxPerUnit;
    float px = clamp(size / pcPerPx, minPx, 512.0);
    gl_PointSize = px;
    float drawn = px * pcPerPx;
    // L☉ per particle times the gain is spread over its smoothing area in pc², so the sum of
    // many reads as a surface brightness at any distance, as a texture would.
    vLight = transmitted * color / (drawn * drawn);
  }
`;

// A Gaussian kernel over the point, normalised so it integrates to one smoothing area.
const PARTICLE_FRAGMENT = /* glsl */ `
  varying vec3 vLight;
  void main() {
    vec2 d = gl_PointCoord - 0.5;
    // sigma a quarter of the point, normalised over the square it is cut to:
    // (sigma sqrt(2 pi) erf(1 / (2 sigma sqrt 2)))^2 = 0.3578.
    float kernel = exp(-dot(d, d) / (2.0 * 0.25 * 0.25)) / 0.3578;
    gl_FragColor = vec4(vLight * kernel, 1.0);
  }
`;

function pointsOf(part: Particles, dustHeight: number, minPx = 10): Points {
  const geometry = new BufferGeometry();
  geometry.setAttribute("position", new BufferAttribute(part.positions, 3));
  geometry.setAttribute("color", new BufferAttribute(part.colors, 3));
  geometry.setAttribute("size", new BufferAttribute(part.sizes, 1));
  geometry.setAttribute("tau", new BufferAttribute(part.tau, 1));
  const material = new ShaderMaterial({
    uniforms: {
      pxPerUnit: { value: 1 },
      minPx: { value: minPx },
      dustHeight: { value: dustHeight },
      extinction: { value: new Vector3(...CHANNEL_EXTINCTION) },
    },
    vertexShader: PARTICLE_VERTEX,
    fragmentShader: PARTICLE_FRAGMENT,
    vertexColors: true,
    blending: AdditiveBlending,
    transparent: true,
    depthWrite: false,
    depthTest: false,
  });
  return new Points(geometry, material);
}

/**
 * The galaxy's unresolved light in photometric mode: the disc as a particle volume
 * with the published scale height, its Hα as bright knots crowded into the arms, the
 * bulge as a Hernquist sphere, each particle dimmed and reddened by the published dust
 * between it and the camera (RENDER_PLAN R3, R4, M4).
 */
export function LightVolume({ meta, query, stops }: Props) {
  const declared = (name: string) => meta.fields.find((f) => f.name === name);
  const fields = FIELDS.filter((n) => declared(n));
  const scalars = SCALARS.filter((n) => declared(n));
  const names = [...fields, ...scalars];
  const key = declared("disc_surface_brightness") && declared("disc_light_temperature") ? JSON.stringify([names, query]) : null;
  const loaded = useLoad<Frame>(key, (signal) => loadArrays(names, query, signal));
  const frame = loaded.value && fields.every((n) => n in loaded.value!.arrays) ? loaded.value : null;

  const scene = useMemo(() => {
    const R = frame?.header.grid.axes.R;
    const tempDecl = declared("disc_light_temperature");
    if (!frame || !R || !tempDecl) return null;
    const random = seeded(Number(query.world_seed ?? 0) + 7919);
    const paint = paintOf(tempDecl, meta.cmaps, frame.arrays.disc_light_temperature as Float64Array);
    const linear = (kelvin: number): number[] | null => {
      const [r, g, b, a] = paint.color(kelvin);
      return a === 0 ? null : [srgbToLinear(r / 255), srgbToLinear(g / 255), srgbToLinear(b / 255)];
    };
    const temperature = frame.arrays.disc_light_temperature;
    const brightness = frame.arrays.disc_surface_brightness as Float64Array;
    const contrastValues = frame.arrays.pattern_density_contrast;
    const phi = frame.header.grid.axes.phi;
    const contrast = contrastValues && phi ? { values: contrastValues as Float64Array, phi } : undefined;
    const height = (frame.header.scalars.thin_disc_scale_height ?? 300) / 1000;
    const extinction = frame.arrays.dust_extinction_v as Float64Array | undefined;
    const disc = { R, brightness, contrast, height, extinction };
    // The dust sits in a layer thinner than the stars: half the thin disc's scale height, the
    // usual ratio of the cold gas to the stellar disc [recall], and a stated display choice.
    const dustHeight = height / 2;

    const gain = LIGHT_PER_LSUN_PC2 * 2 ** stops;
    const layers: Points[] = [];
    const light = discLuminosity(R, brightness);
    layers.push(pointsOf(sampleDisc(disc, brightness, light, (ring) => linear(Number(temperature[ring])), DISC_PARTICLES, gain, random), dustHeight));

    const halpha = frame.arrays.halpha_surface_brightness as Float64Array | undefined;
    if (halpha) {
      const knots = sampleDisc(
        { ...disc, height: dustHeight / 2 }, halpha, discLuminosity(R, halpha), () => HII_RGB,
        HII_PARTICLES, gain * LINE_CHANNEL_WEIGHT, random, HII_CLUMP, HII_SIZE_PC,
      );
      layers.push(pointsOf(knots, dustHeight, 2));
    }

    const bulgeL = frame.header.scalars.bulge_luminosity;
    const bulgeT = frame.header.scalars.bulge_light_temperature;
    const bulgeA = frame.header.scalars.bulge_scale_radius;
    const bulgeColour = bulgeT ? linear(bulgeT) : null;
    if (bulgeL && bulgeA && bulgeColour) {
      const tauAt = (r: number) => {
        const i = Math.floor((r - R.lo) / R.width);
        return extinction && i >= 0 && i < R.n && extinction[i] > 0 ? extinction[i] / 1.086 : 0;
      };
      layers.push(pointsOf(sampleBulge(bulgeA, bulgeL, bulgeColour, BULGE_PARTICLES, gain, random, tauAt), dustHeight));
    }
    return { layers };
  }, [frame, meta.cmaps, query.world_seed, stops]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(
    () => () => {
      for (const p of scene?.layers ?? []) {
        p.geometry.dispose();
        (p.material as ShaderMaterial).dispose();
      }
    },
    [scene],
  );

  useFrame(({ camera, gl }) => {
    if (!scene) return;
    // Pixels per scene unit at unit distance: the drawing buffer's height over the view's.
    const fov = "fov" in camera ? (camera as { fov: number }).fov : 45;
    const pxPerUnit = gl.getDrawingBufferSize(DRAWING).y / (2 * Math.tan((fov * Math.PI) / 360));
    for (const p of scene.layers) (p.material as ShaderMaterial).uniforms.pxPerUnit.value = pxPerUnit;
  });

  if (!scene) return null;
  return (
    <group>
      {scene.layers.map((p, i) => (
        <primitive key={i} object={p} />
      ))}
    </group>
  );
}
