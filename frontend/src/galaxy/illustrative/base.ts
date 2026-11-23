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
//   - mend (S106, builder E; the hook `depth`): the published diffuse dust arrives as a face-on transmission per channel
//     in float32; at NGC 4414's centre the depths are about 97 / 122 / 159 nepers (R, V, B), past float32's smallest
//     number, so G and B read a transmission of 0 inside ~0.3 kpc, B alone out to ~0.53 kpc, and all three in the ring
//     at 0.11 kpc, and regimes.ts depthOf reads 0 as no dust: a blue-white nucleus and a bright ring. The model's depths
//     are exactly in the reddening ratio (cloudExt; checked to 1e-5 on both templates), so a lost channel is rebuilt
//     from the deepest one, and an all-lost texel from its two deep neighbours. Only reads touching a lost texel change:
//     the Milky Way (never underflows) and every healthy ring come back bit for bit. The physical look keeps the leak
//     (the physical fix is the owner's to rule).
//   - core and coreRadius: once mended, the true column (A_V ~ 130 mag face-on at NGC 4414's centre) hides the nucleus
//     the goal photograph shows bright; the diffuse dust is thinned by core decades at the centre, a smoothstep in
//     radius to none at coreRadius, all channels alike (the reddening kept).
// Display-only (D275, ruling 4): nothing published moves; the points' dust takes the same map (FluxPoints' gasAt) and
// the same depth (FluxPoints' face).

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
      key: "depth", label: "dust under it", min: 0, max: 2, step: 0.01, unit: "×", default: 1, perTemplate: { milky_way: 0.1, ngc_4414: 1 },
      about: "A multiplier on the diffuse dust's placement while the gas map is drawn: below 1 a clearer, brighter disc. Illustrative.",
    },
    {
      key: "lift", label: "disc lift", min: 0, max: 3, step: 0.05, unit: "stops", default: 0, perTemplate: { milky_way: 2.5, ngc_4414: 0 },
      about: "The disc's starlight lifted by this many stops toward the lift radius (smoothly from none at the centre): a flatter, airbrushed disc. Illustrative.",
    },
    {
      key: "radius", label: "lift radius", min: 1, max: 30, step: 0.5, unit: "kpc", default: 12, perTemplate: { milky_way: 15},
      about: "Where the disc's lift is full, kpc; beyond it the lift holds. Illustrative.",
    },
    {
      key: "mend", label: "mend lost depth", min: 0, max: 1, step: 0.01, unit: "", default: 1,
      about: "Where the published dust's depth underflowed to nothing in a channel (NGC 4414's centre: blue-white, a ring at 0.11 kpc), rebuilt from the deepest channel through the reddening ratio: 1 mended, 0 as read. A no-op where no channel is lost. Illustrative.",
    },
    {
      key: "core", label: "core clearing", min: 0, max: 4, step: 0.05, unit: "dex", default: 0, perTemplate: { milky_way: 0, ngc_4414: 2 },
      about: "The diffuse dust thinned toward the centre by this many decades at the centre, smoothly to none at the core radius: the nucleus shines through. Illustrative.",
    },
    {
      key: "coreRadius", label: "core radius", min: 0.1, max: 5, step: 0.05, log: true, unit: "kpc", default: 1,
      about: "Where the core clearing ends, kpc (a smoothstep from the centre). Illustrative.",
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
  // The mend (base.ts twin baseMended): the ring texture's depth row read texel by texel (row 0 of rings), each texel's
  // column as an A_V (each channel's depth over its depth per magnitude, the deepest channel's), and a texel "lost" where
  // that column is deep (over 10 mag: float32 underflows only past ~87 nepers) and a channel reads under 0.99 of it, or
  // where all three read nothing between deep neighbours. Only where one of the two texels a read interpolates is lost
  // is the depth rebuilt (the columns interpolated, times cloudExt); elsewhere d comes back untouched, bit for bit.
  uniform float illBaseMend;
  uniform float illBaseCore;
  uniform float illBaseCoreRadius;
  float illBaseAvOf(vec3 d) {
    return max(cloudExt.r > 0.0 ? d.r / cloudExt.r : 0.0, max(cloudExt.g > 0.0 ? d.g / cloudExt.g : 0.0, cloudExt.b > 0.0 ? d.b / cloudExt.b : 0.0));
  }
  float illBaseLeastOf(vec3 d) {
    return min(cloudExt.r > 0.0 ? d.r / cloudExt.r : 1e30, min(cloudExt.g > 0.0 ? d.g / cloudExt.g : 1e30, cloudExt.b > 0.0 ? d.b / cloudExt.b : 1e30));
  }
  vec3 illBaseRingDepth(int i) {
    return texelFetch(rings, ivec2(i, 0), 0).rgb;
  }
  // x: the texel's column (mag), y: 1 where it was lost.
  vec2 illBaseTexelAv(int i, int n) {
    vec3 d = illBaseRingDepth(i);
    float a = illBaseAvOf(d);
    if (a > 0.0) return vec2(a, (a > 10.0 && illBaseLeastOf(d) < 0.99 * a) ? 1.0 : 0.0);
    float lo = i > 0 ? illBaseAvOf(illBaseRingDepth(i - 1)) : 0.0;
    float hi = i < n - 1 ? illBaseAvOf(illBaseRingDepth(i + 1)) : 0.0;
    if (hi > 10.0 && i == 0) return vec2(hi, 1.0);
    if (hi > 10.0 && lo > 10.0) return vec2(0.5 * (lo + hi), 1.0);
    return vec2(0.0);
  }
  vec3 illBaseMended(vec3 d, float r) {
    int n = textureSize(rings, 0).x;
    float u = clamp((r - rLo) / (rHi - rLo), 0.0, 1.0) * float(n) - 0.5;
    float fl = floor(u);
    float f = u - fl;
    int i0 = int(fl);
    if (i0 < 0) { i0 = 0; f = 0.0; }
    if (i0 > n - 2) { i0 = n - 2; f = 1.0; }
    vec2 t0 = illBaseTexelAv(i0, n);
    vec2 t1 = illBaseTexelAv(i0 + 1, n);
    if (t0.y + t1.y <= 0.0) return d;
    return mix(d, max(d, mix(t0.x, t1.x, f) * cloudExt), illBaseMend);
  }
  vec3 illBaseDepthOf(vec3 d, vec2 rp) {
    if (illBaseMend > 0.0 && rp.x < rHi) d = illBaseMended(d, rp.x);
    if (illBaseCore > 0.0 && rp.x < illBaseCoreRadius) d *= exp2(-3.32192809 * illBaseCore * (1.0 - smoothstep(0.0, illBaseCoreRadius, rp.x)));
    return d;
  }
`,
  hooks: { gas: "illBaseGas", light: "illBaseLight", depth: "illBaseDepthOf" },
  uniforms: (p) => ({
    illBaseMend: p.mend ?? 1,
    illBaseCore: p.core ?? 0,
    illBaseCoreRadius: p.coreRadius ?? 1,
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

type Rgb = readonly [number, number, number];

const avOf = (d: Rgb, ext: Rgb): number => Math.max(...[0, 1, 2].map((k) => (ext[k] > 0 ? d[k] / ext[k] : 0)));
const leastOf = (d: Rgb, ext: Rgb): number => Math.min(...[0, 1, 2].map((k) => (ext[k] > 0 ? d[k] / ext[k] : 1e30)));

/** A depth texel's column (mag) and whether it was lost (the GLSL's illBaseTexelAv). */
export function baseTexelAv(texels: readonly Rgb[], i: number, ext: Rgb): { av: number; lost: boolean } {
  const a = avOf(texels[i], ext);
  if (a > 0) return { av: a, lost: a > 10 && leastOf(texels[i], ext) < 0.99 * a };
  const lo = i > 0 ? avOf(texels[i - 1], ext) : 0;
  const hi = i < texels.length - 1 ? avOf(texels[i + 1], ext) : 0;
  if (hi > 10 && i === 0) return { av: hi, lost: true };
  if (hi > 10 && lo > 10) return { av: 0.5 * (lo + hi), lost: true };
  return { av: 0, lost: false };
}

/**
 * The mend (the GLSL's illBaseMended): d the depth read at radius r (kpc) from the depth row `texels` over [rLo, rHi],
 * rebuilt in the reddening ratio `ext` where a texel the read interpolates is lost; d itself (the same object) elsewhere.
 */
export function baseMended(d: Rgb, r: number, texels: readonly Rgb[], ext: Rgb, rLo: number, rHi: number, mend = 1): Rgb {
  const n = texels.length;
  const u = Math.min(1, Math.max(0, (r - rLo) / (rHi - rLo))) * n - 0.5;
  let i0 = Math.floor(u);
  let f = u - i0;
  if (i0 < 0) [i0, f] = [0, 0];
  if (i0 > n - 2) [i0, f] = [n - 2, 1];
  const t0 = baseTexelAv(texels, i0, ext);
  const t1 = baseTexelAv(texels, i0 + 1, ext);
  if (!t0.lost && !t1.lost) return d;
  const a = t0.av + (t1.av - t0.av) * f;
  return [0, 1, 2].map((k) => d[k] + (Math.max(d[k], a * ext[k]) - d[k]) * mend) as unknown as Rgb;
}

/** The core clearing's multiplier on the depth at radius r (the GLSL's twin): 10^-core at the centre, 1 from radius out. */
export function baseCore(r: number, core: number, radius: number): number {
  if (core <= 0 || r >= radius) return 1;
  const t = Math.min(1, Math.max(0, r / radius));
  return 10 ** (-core * (1 - t * t * (3 - 2 * t)));
}

/** The gas map's value after the base, for a map value g already read the model's way (grain and depth only). */
export const baseGas = (g: number, grain: number, depth: number): number => (1 + (g - 1) * grain) * depth;
