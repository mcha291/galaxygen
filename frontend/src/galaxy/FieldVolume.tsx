import { paintOf } from "@interface/ramp.js";
import { useFrame } from "@react-three/fiber";
import { useEffect, useMemo } from "react";
import {
  AdditiveBlending,
  BackSide,
  BoxGeometry,
  ClampToEdgeWrapping,
  DataTexture,
  FloatType,
  LinearFilter,
  Mesh,
  RGBAFormat,
  RepeatWrapping,
  ShaderMaterial,
  Vector3,
} from "three";

import { type FieldsPayload, type Frame, type Query, loadArrays } from "../api";
import { useLoad } from "../useLoad";
import { srgbToLinear } from "./colors";
import { planeTexture } from "./regimes";

/**
 * How bright 1 L☉/pc² draws at zero exposure stops, against a star point's 1 per 100 L☉.
 * A display balance between the layers, not a physical constant: a point is one star and
 * the field is a disc of them.
 */
export const LIGHT_PER_LSUN_PC2 = 1 / 400;

/**
 * Extinction in the red, green and blue channels per magnitude of A_V: the R, V and B bands
 * of Cardelli, Clayton & Mathis at R_V = 3.1 standing in for the three channels
 * `[recall: CCM 1989, A_R/A_V = 0.748, A_B/A_V = 1.324]`. Dust dims blue more than red, so a
 * dusty region reddens as it darkens: occlusion, never an added colour (R4).
 */
export const CHANNEL_EXTINCTION = [0.748, 1.0, 1.324] as const;

/** Ray-march steps through the galaxy's bounding box. */
const STEPS = 128;

const FIELDS = ["disc_surface_brightness", "disc_light_temperature", "pattern_density_contrast", "dust_extinction_v", "halpha_surface_brightness"];
const SCALARS = ["thin_disc_scale_height", "bulge_luminosity", "bulge_light_temperature", "bulge_scale_radius"];

const VERTEX = /* glsl */ `
  varying vec3 vWorld;
  void main() {
    vec4 world = modelMatrix * vec4(position, 1.0);
    vWorld = world.xyz;
    gl_Position = projectionMatrix * viewMatrix * world;
  }
`;

// Emission and absorption along the line of sight, front to back. At each step the light
// emitted there is added, dimmed by all the dust between it and the camera, and the dust in
// that step dims everything behind it. Units: the plane texture is L☉/pc² through a face-on
// column and the sech² profiles integrate to 1 per kpc of height, so their product times the
// step in kpc is L☉/pc²; the bulge is L☉ times a Hernquist density per kpc³, times the step,
// per 10⁶ pc² per kpc².
const FRAGMENT = /* glsl */ `
  uniform sampler2D plane;
  uniform float rLo;
  uniform float rHi;
  uniform float halfHeight;
  uniform float discHeight;
  uniform float dustHeight;
  uniform float bulgeLuminosity;
  uniform float bulgeScale;
  uniform vec3 bulgeColour;
  uniform vec3 extinction;
  uniform float gain;
  varying vec3 vWorld;

  float sech2(float x) { float c = cosh(clamp(x, -30.0, 30.0)); return 1.0 / (c * c); }

  void main() {
    vec3 origin = cameraPosition;
    vec3 dir = normalize(vWorld - cameraPosition);
    vec3 lo = vec3(-rHi, -halfHeight, -rHi);
    vec3 inv = 1.0 / dir;
    vec3 t0 = (lo - origin) * inv;
    vec3 t1 = (-lo - origin) * inv;
    vec3 tNear3 = min(t0, t1);
    vec3 tFar3 = max(t0, t1);
    float tNear = max(max(tNear3.x, tNear3.y), max(tNear3.z, 0.0));
    float tFar = min(min(tFar3.x, tFar3.y), tFar3.z);
    if (tFar <= tNear) discard;

    // Steps spaced geometrically from the camera: fine where the galaxy is close and large on
    // screen, coarse where it is far and small. Even steps along a 60 kpc ray pass straight
    // over a disc 0.3 kpc thick a few hundred parsecs away.
    float tStart = max(tNear, 0.01);
    float ratio = pow(max(tFar, tStart * 1.0001) / tStart, 1.0 / float(${STEPS}));
    // A per-pixel offset into the first step turns banding into fine noise.
    float jitter = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453);
    vec3 light = vec3(0.0);
    vec3 transmitted = vec3(1.0);
    for (int k = 0; k < ${STEPS}; k++) {
      float a = tStart * pow(ratio, float(k));
      float ds = a * (ratio - 1.0);
      vec3 p = origin + dir * (a + jitter * ds);
      float r = length(p.xz);
      vec3 emitted = vec3(0.0);
      float tau = 0.0;
      if (r < rHi) {
        // Azimuth in the stars' frame: x = r cos φ, z = −r sin φ.
        float phi = atan(-p.z, p.x);
        if (phi < 0.0) phi += 6.28318531;
        vec4 column = texture2D(plane, vec2((r - rLo) / (rHi - rLo), phi / 6.28318531));
        emitted += column.rgb * sech2(p.y / (2.0 * discHeight)) / (4.0 * discHeight);
        tau = column.a * sech2(p.y / (2.0 * dustHeight)) / (4.0 * dustHeight);
      }
      float s = max(length(p), 0.02);
      emitted += bulgeColour * bulgeLuminosity * bulgeScale / (6.28318531 * s * pow(s + bulgeScale, 3.0)) * 1.0e-6;
      light += transmitted * emitted * ds;
      transmitted *= exp(-tau * ds * extinction);
    }
    gl_FragColor = vec4(light * gain, 1.0);
  }
`;

interface Props {
  meta: FieldsPayload;
  query: Query;
  /** Exposure in stops. */
  stops: number;
  /** The regime weight, 0 to 1: how much of the field is drawn at this zoom. */
  weight?: number;
}

/**
 * The field regime: the whole galaxy's light as a volume, ray-marched per pixel through
 * the published fields (RENDER_PLAN R3, R4, M4). No particles and no sample: at the scale
 * of a galaxy the light is unresolved, and a smooth integral is what it is.
 */
export function FieldVolume({ meta, query, stops, weight = 1 }: Props) {
  const declared = (name: string) => meta.fields.find((f) => f.name === name);
  const fields = FIELDS.filter((n) => declared(n));
  const names = [...fields, ...SCALARS.filter((n) => declared(n))];
  const key = declared("disc_surface_brightness") && declared("disc_light_temperature") ? JSON.stringify([names, query]) : null;
  const loaded = useLoad<Frame>(key, (signal) => loadArrays(names, query, signal));
  const frame = loaded.value && fields.every((n) => n in loaded.value!.arrays) ? loaded.value : null;

  const mesh = useMemo(() => {
    const R = frame?.header.grid.axes.R;
    const tempDecl = declared("disc_light_temperature");
    if (!frame || !R || !tempDecl) return null;
    const paint = paintOf(tempDecl, meta.cmaps, frame.arrays.disc_light_temperature as Float64Array);
    const linear = (kelvin: number): number[] => {
      const [r, g, b, a] = paint.color(kelvin);
      return a === 0 ? [Number.NaN, Number.NaN, Number.NaN] : [srgbToLinear(r / 255), srgbToLinear(g / 255), srgbToLinear(b / 255)];
    };
    const temperature = frame.arrays.disc_light_temperature;
    const colour = new Float64Array(R.n * 3);
    for (let i = 0; i < R.n; i += 1) colour.set(linear(Number(temperature[i])), 3 * i);
    const phi = frame.header.grid.axes.phi;
    const contrastValues = frame.arrays.pattern_density_contrast;
    const { data, width, height } = planeTexture({
      R,
      brightness: frame.arrays.disc_surface_brightness as Float64Array,
      colour,
      halpha: frame.arrays.halpha_surface_brightness as Float64Array | undefined,
      extinction: frame.arrays.dust_extinction_v as Float64Array | undefined,
      contrast: contrastValues && phi ? { values: contrastValues as Float64Array, phi } : undefined,
    });
    const plane = new DataTexture(data, width, height, RGBAFormat, FloatType);
    plane.minFilter = LinearFilter;
    plane.magFilter = LinearFilter;
    plane.wrapS = ClampToEdgeWrapping;
    plane.wrapT = RepeatWrapping;
    plane.needsUpdate = true;

    const scalars = frame.header.scalars;
    const discHeight = (scalars.thin_disc_scale_height ?? 300) / 1000;
    const bulgeScale = scalars.bulge_scale_radius ?? 0;
    const bulgeColour = scalars.bulge_light_temperature ? linear(scalars.bulge_light_temperature) : [0, 0, 0];
    // Tall enough for the disc's light to have fallen away and the bulge to have faded.
    const halfHeight = Math.max(10 * discHeight, 12 * bulgeScale, 2);

    const material = new ShaderMaterial({
      uniforms: {
        plane: { value: plane },
        rLo: { value: R.lo },
        rHi: { value: R.hi },
        halfHeight: { value: halfHeight },
        discHeight: { value: discHeight },
        // The dust lies in a layer thinner than the stars: half the thin disc's scale height, about
        // the cold gas's share of the stellar disc [recall]; a stated display choice.
        dustHeight: { value: discHeight / 2 },
        bulgeLuminosity: { value: scalars.bulge_luminosity ?? 0 },
        bulgeScale: { value: Math.max(bulgeScale, 1e-3) },
        bulgeColour: { value: new Vector3(...bulgeColour.map((c) => (Number.isFinite(c) ? c : 0))) },
        extinction: { value: new Vector3(...CHANNEL_EXTINCTION) },
        gain: { value: 0 },
      },
      vertexShader: VERTEX,
      fragmentShader: FRAGMENT,
      side: BackSide, // the far faces, so it draws with the camera outside the box or inside it
      blending: AdditiveBlending,
      transparent: true,
      depthTest: false,
      depthWrite: false,
    });
    const box = new Mesh(new BoxGeometry(2 * R.hi, 2 * halfHeight, 2 * R.hi), material);
    box.renderOrder = -1;
    box.frustumCulled = false;    return box;
  }, [frame, meta.cmaps]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(
    () => () => {
      if (!mesh) return;
      const material = mesh.material as ShaderMaterial;
      (material.uniforms.plane.value as DataTexture).dispose();
      material.dispose();
      mesh.geometry.dispose();
    },
    [mesh],
  );

  useFrame(() => {
    if (mesh) (mesh.material as ShaderMaterial).uniforms.gain.value = LIGHT_PER_LSUN_PC2 * 2 ** stops * weight;
  });

  return mesh ? <primitive object={mesh} /> : null;
}
