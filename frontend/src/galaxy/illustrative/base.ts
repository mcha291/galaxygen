// The base (S106, BUILD_VIII section 6 item 2): the disc under the arms, smoothed the way the goal pictures' are.
//
// WHAT DREW THE STREAKS (traced by capture, S106 builder A: each physical-side switch and each feature's strength set off
// one at a time, frames beside the defaults). The fine hair-like streaks under both pictures are the randomness layer's
// GAS FLUCTUATION map (the march's screenGas, noise.glsl.ts layerGasMap; the switch "gas fluctuation in the march"): a
// lognormal multiplier on the dust's placement, read once per ray at the midplane, so it shapes the diffuse dust's depth
// and the dust's own light. Its noise is read through a log-spiral shear (layerGasRead: the read point turned by
// theta = sense (twist + strain log(R / R_r)), which grows with log R), and a turn that grows with radius stretches an
// isotropic noise into long threads along the flow - the brushed grain. With the map off the Milky Way's slate zone and
// lavender disc go smooth and NGC 4414's grey outer disc goes cloudy; the clustered young light, the spurs, the arms,
// the lanes and the knots draw none of it (NGC 4414's network is brushed by its own pieces, floc.ts, not by this).
//
// WHAT THIS FEATURE DOES, under the illustrative look only (the hook `gas`, index.ts; the physical look reads the map as
// the model gives it):
//   - grain: the map taken toward its unit mean, mix(1, g, grain): 0 the dust smooth, 1 the model's map.
//   - unshear: the map read again with its turn scaled by (1 - unshear): 1 the same noise without the shear, an
//     isotropic cloudy mottle (NGC 4414's photograph), 0 the model's threads. size scales the noise's grain (> 1 coarser).
//   - depth: a multiplier on the dust's placement while the map is drawn (with less contrast in the map the disc's mean
//     transmission falls - the mean of exp(-tau g) is above exp(-tau) - and this gives it back).
//   - lift and radius: the disc's starlight lifted by lift stops toward radius (smoothstep from the centre), so the
//     Milky Way's disc stays nearly as bright to its soft edge as the goal's airbrushed haze (the hook `light`).
// Display-only (D275, ruling 4): nothing published moves; the points' dust takes the same map (FluxPoints' gasAt).

import type { IllFeature } from "./feature";

export const base: IllFeature = {
  id: "base",
  label: "base",
  about: "The disc under the arms: the gas fluctuation map's brushed threads smoothed or made cloudy, and the disc's light lifted toward its edge.",
  controls: [
    {
      key: "grain", label: "gas grain", min: 0, max: 1, step: 0.01, unit: "", default: 1, perTemplate: { milky_way: 0, ngc_4414: 1 },
      about: "The gas fluctuation map on the dust taken toward its mean: 0 the dust smooth (no streaks), 1 the model's map. Illustrative.",
    },
    {
      key: "unshear", label: "unbrush", min: 0, max: 1, step: 0.01, unit: "", default: 0, perTemplate: { milky_way: 1, ngc_4414: 1 },
      about: "The map's log-spiral shear taken away: 0 the model's threads along the flow, 1 the same noise isotropic, a cloudy mottle. Illustrative.",
    },
    {
      key: "size", label: "mottle size", min: 0.25, max: 4, step: 0.01, log: true, unit: "×", default: 1, perTemplate: { ngc_4414: 1.6 },
      about: "The map's noise read coarser (above 1) or finer, while unbrushed or resized. Illustrative.",
    },
    {
      key: "depth", label: "dust under it", min: 0, max: 2, step: 0.01, unit: "×", default: 1, perTemplate: { milky_way: 0.6, ngc_4414: 1 },
      about: "A multiplier on the diffuse dust's placement while the gas map is drawn: below 1 a clearer, brighter disc. Illustrative.",
    },
    {
      key: "lift", label: "disc lift", min: 0, max: 3, step: 0.05, unit: "stops", default: 0, perTemplate: { milky_way: 1.25, ngc_4414: 0 },
      about: "The disc's starlight lifted by this many stops toward the lift radius (smoothly from none at the centre): a flatter, airbrushed disc. Illustrative.",
    },
    {
      key: "radius", label: "lift radius", min: 1, max: 30, step: 0.5, unit: "kpc", default: 12, perTemplate: { milky_way: 15 },
      about: "Where the disc's lift is full, kpc; beyond it the lift holds. Illustrative.",
    },
  ],
  glsl: /* glsl */ `
  uniform float illBaseLift;
  uniform float illBaseRadius;
  vec3 illBaseLight(vec2 rp) {
    if (illBaseLift <= 0.0) return vec3(1.0);
    return vec3(exp2(illBaseLift * smoothstep(0.0, illBaseRadius, rp.x)));
  }
`,
  noiseGlsl: /* glsl */ `
  uniform float illBaseGrain;
  uniform float illBaseUnshear;
  uniform float illBaseSize;
  uniform float illBaseDepth;
  // layerGasMap (noise.glsl.ts) with the read's turn scaled by (1 - unshear) and the noise's frequency over size.
  float illBaseGasMap(vec2 xy) {
    int ring = layerGasRing(length(xy));
    vec4 row = texelFetch(uGasRing, ivec2(ring, 0), 0);
    float R = length(xy);
    float theta = (1.0 - illBaseUnshear) * uGasSense * (row.w + row.z * log(max(R, uGasEdge0) / row.x));
    float c = cos(theta);
    float s = sin(theta);
    vec2 q = vec2(xy.x * c + xy.y * s, xy.y * c - xy.x * s) / illBaseSize;
    float g = layerGasSum(q, ring);
    float normaliser = texelFetch(uGasCells, ivec2(layerGasSector(xy), ring), 0).x;
    return layerLognormal(g, row.y, normaliser);
  }
  float illBaseGas(vec2 xy, float g) {
    float m = (illBaseGrain > 0.0 && (illBaseUnshear > 0.0 || illBaseSize != 1.0)) ? illBaseGasMap(xy) : g;
    return mix(1.0, m, illBaseGrain) * illBaseDepth;
  }
`,
  hooks: { gas: "illBaseGas", light: "illBaseLight" },
  uniforms: (p) => ({
    illBaseGrain: p.grain ?? 1,
    illBaseUnshear: p.unshear ?? 0,
    illBaseSize: p.size ?? 1,
    illBaseDepth: p.depth ?? 1,
    illBaseLift: p.lift ?? 0,
    illBaseRadius: p.radius ?? 12,
  }),
};

/** The lift's multiplier at radius r, kpc (the GLSL's twin). */
export function baseLift(r: number, lift: number, radius: number): number {
  if (lift <= 0) return 1;
  const t = Math.min(1, Math.max(0, r / radius));
  return 2 ** (lift * t * t * (3 - 2 * t));
}

/** The gas map's value after the base, for a map value g already read the model's way (grain and depth only). */
export const baseGas = (g: number, grain: number, depth: number): number => (1 + (g - 1) * grain) * depth;
