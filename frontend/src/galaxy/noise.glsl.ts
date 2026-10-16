/**
 * The randomness layer's noise as one GLSL ES 3.00 include (S66, BUILD_III Phase V7; D226 R1, R9a): the functions the
 * march evaluates once per ray at the midplane (a thin screen, D226 as amended) - the gas fluctuation map, the clustering field's three truncated maps, the gas spurs'
 * point function - and the primitives they are made of. three r186 compiles a ShaderMaterial as `#version 300 es`
 * with `precision highp float; precision highp int;`, so `uint` arithmetic wraps modulo 2^32 and `>>` on a uint is a
 * logical shift, as the model's numpy uint32 is.
 *
 * Its twin is `noise.ts` (Math.fround / Math.imul), function for function and operation for operation, held to the
 * model's vectors (`noise.test.ts`); this text is pinned by sha in `noise.test.ts` and measured on the GPU by
 * `window.__galaxygenNoiseProbe` (`frontend/e2e/noise.spec.ts`). Names carry a `layer` prefix (a desktop GLSL's
 * deprecated built-ins are named noise1..noise4); the Python each function twins is named beside it.
 *
 * The tables (uploaded by the march from `noise.ts`' preparation, every number the model's):
 * - `uGasRing` RGBA32F 32 x 2: texel (r, 0) = (inner edge kpc, sigma, strain, twist mod 2 pi), (r, 1) = (break index,
 *   norm, outer edge, 0) - gas_fluctuation's table `ring`;
 * - `uGasWeights` RGBA32F 7 x 2: texel (b, 0) = weights 0-3, (b, 1) = weights 4-5 - GasFluctuationField.amplitudes;
 * - `uGasCells` R32F 32 x 32: the cell normalisers, column a sector, row a ring;
 * - the uniforms `uGasSeed` (uint), `uGasInvScale`, `uGasSense`, `uGasEdge0`;
 * - the clustering field's `uClusterSeed` (uint), `uClusterInvScale`, `uClusterGain`, `uClusterTop`, `uClusterNorm`,
 *   `uClusterSigma`;
 * - `uSpurs` RGBA32F (3 count) x 1: spur j's texels 3j..3j+2 = (ln R_f, phi_f, A, F), (sin p, cos p, T, lambda),
 *   (sigma, T sin p, 0, 0); `uSpurTurn`, `uSpurReach`.
 * A material that includes this text declares those it reads (`NOISE_UNIFORMS` lists them all).
 */

/** The declarations of every table and uniform the include's field functions read. */
export const NOISE_UNIFORMS = /* glsl */ `
uniform highp sampler2D uGasRing;
uniform highp sampler2D uGasWeights;
uniform highp sampler2D uGasCells;
uniform uint uGasSeed;
uniform float uGasInvScale;
uniform float uGasSense;
uniform float uGasEdge0;
uniform uint uClusterSeed;
uniform float uClusterInvScale;
uniform float uClusterGain;
uniform float uClusterTop;
uniform float uClusterNorm;
uniform float uClusterSigma;
uniform highp sampler2D uSpurs;
uniform float uSpurTurn;
uniform float uSpurReach;
`;

/** The primitives and the field functions; needs NOISE_UNIFORMS (or the same names) declared before it. */
export const NOISE_GLSL = /* glsl */ `
// --- the hash (noise.py lattice_hash; mix32 = lowbias32, MIX_SHIFTS 16 15 16, MIX_MULTIPLIERS, SEED_SALT) ---------
uint layerMix(uint h) {
  h ^= h >> 16u;
  h *= 0x7feb352du;
  h ^= h >> 15u;
  h *= 0x846ca68bu;
  h ^= h >> 16u;
  return h;
}
uint layerKey(uint seed, uint octave) { return layerMix(layerMix(seed ^ 0x9e3779b9u) ^ octave); }
uint layerHash(uint seed, uint octave, uint ix, uint iy) { return layerMix(layerMix(layerKey(seed, octave) ^ ix) ^ iy); }
uint layerHash(uint seed, uint octave, uint ix, uint iy, uint iz) { return layerMix(layerHash(seed, octave, ix, iy) ^ iz); }
// noise.py lattice_value: (h >> 8) * 2^-23 - 1, exact in float32
float layerValue(uint h) { return float(h >> 8u) * 1.1920928955078125e-7 - 1.0; }

// --- one octave (noise.py _fade, _cell, noise2, noise3) ----------------------------------------------------------
float layerFade(float t) { return t * t * t * (t * (t * 6.0 - 15.0) + 10.0); }
// (uint index, fade weight, variance factor 1 - 2 s (1 - s)); the index is GLSL's uint(int): two's complement. The
// fraction is fract(c), which is c - floor(c) exactly (noise.py: "the fraction is exact"), taken by its own instruction
// so that a driver cannot fuse the coordinate's product into the subtraction (S66: at 4 000 lattice cells a fused
// fraction moved the gas sum by 2e-4 on the RTX 4070).
void layerCell(float c, out uint u, out float s, out float n) {
  float base = floor(c);
  s = layerFade(fract(c));
  n = 1.0 - 2.0 * s * (1.0 - s);
  u = uint(int(base));
}
float layerNoise2(uint seed, float x, float y, uint octave) {
  uint key = layerKey(seed, octave);
  uint ux; float sx; float nx;
  uint uy; float sy; float ny;
  layerCell(x, ux, sx, nx);
  layerCell(y, uy, sy, ny);
  uint h0 = layerMix(key ^ ux);
  uint h1 = layerMix(key ^ (ux + 1u));
  uint uy1 = uy + 1u;
  float v00 = layerValue(layerMix(h0 ^ uy));
  float v10 = layerValue(layerMix(h1 ^ uy));
  float v01 = layerValue(layerMix(h0 ^ uy1));
  float v11 = layerValue(layerMix(h1 ^ uy1));
  float a = v00 + sx * (v10 - v00);
  float b = v01 + sx * (v11 - v01);
  float r = a + sy * (b - a);
  return r * (1.7320508075688772 / sqrt(nx * ny));
}
float layerNoise3(uint seed, float x, float y, float z, uint octave) {
  uint key = layerKey(seed, octave);
  uint ux; float sx; float nx;
  uint uy; float sy; float ny;
  uint uz; float sz; float nz;
  layerCell(x, ux, sx, nx);
  layerCell(y, uy, sy, ny);
  layerCell(z, uz, sz, nz);
  uint uy1 = uy + 1u;
  uint uz1 = uz + 1u;
  uint h0 = layerMix(key ^ ux);
  uint h1 = layerMix(key ^ (ux + 1u));
  uint h00 = layerMix(h0 ^ uy);
  uint h10 = layerMix(h1 ^ uy);
  uint h01 = layerMix(h0 ^ uy1);
  uint h11 = layerMix(h1 ^ uy1);
  float vl = layerValue(layerMix(h00 ^ uz));
  float a00 = vl + sx * (layerValue(layerMix(h10 ^ uz)) - vl);
  vl = layerValue(layerMix(h01 ^ uz));
  float a10 = vl + sx * (layerValue(layerMix(h11 ^ uz)) - vl);
  vl = layerValue(layerMix(h00 ^ uz1));
  float a01 = vl + sx * (layerValue(layerMix(h10 ^ uz1)) - vl);
  vl = layerValue(layerMix(h01 ^ uz1));
  float a11 = vl + sx * (layerValue(layerMix(h11 ^ uz1)) - vl);
  float b0 = a00 + sy * (a10 - a00);
  float b1 = a01 + sy * (a11 - a01);
  float r = b0 + sz * (b1 - b0);
  return r * (1.7320508075688772 / sqrt((nx * ny) * nz));
}

// --- octave sums (noise.py fractal_coarsest), the log-normal map (noise.py lognormal_map) -------------------------
// The truncated sums after 1, 2 and 3 octaves of a 2-D sum (kept 1, 2, 3; an octaves = 3 sum's third is fractal)
vec3 layerFractal2Coarsest(uint seed, vec2 p, int octaves, float baseFrequency, float lacunarity, float gain, float top, float norm) {
  float fr = baseFrequency;
  float a = 1.0;
  float total = 0.0;
  vec3 kept = vec3(0.0);
  for (int j = 0; j < 3; j++) {
    if (j == octaves - 1) a = a * top;
    total = total + a * layerNoise2(seed, p.x * fr, p.y * fr, uint(j));
    fr = fr * lacunarity;
    a = a * gain;
    kept[j] = total * norm;
  }
  return kept;
}
// noise.py fractal for 2-D and 3-D, up to eight octaves (the vectors' sums: six and four)
float layerFractal(uint seed, vec3 p, int ndim, int octaves, float baseFrequency, float lacunarity, float gain, float top, float norm) {
  float fr = baseFrequency;
  float a = 1.0;
  float total = 0.0;
  for (int j = 0; j < 8; j++) {
    if (j >= octaves) break;
    if (j == octaves - 1) a = a * top;
    float n = ndim == 2 ? layerNoise2(seed, p.x * fr, p.y * fr, uint(j)) : layerNoise3(seed, p.x * fr, p.y * fr, p.z * fr, uint(j));
    total = total + a * n;
    fr = fr * lacunarity;
    a = a * gain;
  }
  return total * norm;
}
// normaliser exp(sigma g - sigma^2 / 2) as (sigma g) - ((0.5 sigma) sigma)
float layerLognormal(float g, float sigma, float normaliser) { return normaliser * exp(sigma * g - 0.5 * sigma * sigma); }

// --- the gas fluctuation field (gas_fluctuation.py GasFluctuationField) ------------------------------------------
// ring_of: the last edge not above R, held to rings 0..31 (a binary search of the ring table's inner edges)
int layerGasRing(float R) {
  int lo = 0;
  int hi = 31;
  for (int k = 0; k < 5; k++) {
    int mid = (lo + hi + 1) / 2;
    if (texelFetch(uGasRing, ivec2(mid, 0), 0).x <= R) lo = mid; else hi = mid - 1;
  }
  return lo;
}
// evaluate's sector: floor((atan2(y, x) mod 2 pi) / (2 pi / 32)), held to 0..31
int layerGasSector(vec2 xy) {
  float phi = atan(xy.y, xy.x);
  if (phi < 0.0) phi += 6.283185307179586;
  return clamp(int(floor(phi / 0.19634954084936207)), 0, 31);
}
// read_positions: R = hypot, theta = sense (twist + strain log(max(R, R_0) / R_r)), (R cos, R sin)(atan2(y, x) - theta)
// - here as the same point by rotation, (x cos theta + y sin theta, y cos theta - x sin theta): no atan2 and no second
// cos and sin of a large angle (S66: the polar form's transcendentals put g 5e-2 from float64 at 24 kpc on the GPU)
vec2 layerGasRead(vec2 xy, int ring) {
  vec4 row = texelFetch(uGasRing, ivec2(ring, 0), 0);
  float R = length(xy);
  float theta = uGasSense * (row.w + row.z * log(max(R, uGasEdge0) / row.x));
  float c = cos(theta);
  float s = sin(theta);
  return vec2(xy.x * c + xy.y * s, xy.y * c - xy.x * s);
}
// _sum: sum_j w[b_r][j] noise2(seed, X f_j, Y f_j, j), f stepped by doubling from 1 / scale
float layerGasSum(vec2 q, int ring) {
  int b = int(texelFetch(uGasRing, ivec2(ring, 1), 0).x + 0.5);
  vec4 w0 = texelFetch(uGasWeights, ivec2(b, 0), 0);
  vec4 w1 = texelFetch(uGasWeights, ivec2(b, 1), 0);
  float w[6] = float[6](w0.x, w0.y, w0.z, w0.w, w1.x, w1.y);
  float fr = uGasInvScale;
  float total = 0.0;
  for (int j = 0; j < 6; j++) {
    total = total + w[j] * layerNoise2(uGasSeed, q.x * fr, q.y * fr, uint(j));
    fr = fr * 2.0;
  }
  return total;
}
// evaluate: normaliser_cell exp(sigma_r g - sigma_r^2 / 2) at a face-on position, kpc; unit mean in every cell
float layerGasMap(vec2 xy) {
  int ring = layerGasRing(length(xy));
  float g = layerGasSum(layerGasRead(xy, ring), ring);
  float sigma = texelFetch(uGasRing, ivec2(ring, 0), 0).y;
  float normaliser = texelFetch(uGasCells, ivec2(layerGasSector(xy), ring), 0).x;
  return layerLognormal(g, sigma, normaliser);
}

// --- the clustering field (census_clustering.py ClusteringField.maps, kept 1, 2, 3) -------------------------------
vec3 layerClusterMaps(vec2 xy) {
  vec3 g = layerFractal2Coarsest(uClusterSeed, xy, 3, uClusterInvScale, 2.0, uClusterGain, uClusterTop, uClusterNorm);
  return vec3(layerLognormal(g.x, uClusterSigma, 1.0), layerLognormal(g.y, uClusterSigma, 1.0), layerLognormal(g.z, uClusterSigma, 1.0));
}

// --- the gas spurs (stages/spurs.py Spurs.reads, Spurs.excess) -----------------------------------------------------
bool layerSpurReads(float R, vec4 s0, vec4 s2) {
  float x = log(R);
  float gap = max(max(s0.x - x, x - (s0.x + s2.y)), 0.0);
  return R * gap <= uSpurReach * s2.x;
}
float layerSpurExcess(float R, float phi, vec4 s0, vec4 s1, vec4 s2) {
  float dx = log(R) - s0.x;
  float middle = 0.5 * s1.z * s1.y;
  float u = uSpurTurn * (phi - s0.y) - middle + 3.141592653589793;
  float psi = middle + (u - 6.283185307179586 * floor(u / 6.283185307179586)) - 3.141592653589793;
  float across = dx * s1.y - psi * s1.x;
  float along = dx * s1.x + psi * s1.y;
  float q = R / s2.x;
  float inv2 = 0.5 * (q * q);
  float gap = along < 0.0 ? along : (along > s1.z ? along - s1.z : 0.0);
  float height = along < 0.0 ? 1.0 : (along > s1.z ? 1.0 / s0.w : exp(-s1.w * clamp(along, 0.0, s1.z)));
  return s0.z * height * exp(-(across * across + gap * gap) * inv2);
}
// Spurs.at: every spur the radius reads, in the table's order
float layerSpurSum(float R, float phi, int count) {
  float total = 0.0;
  for (int j = 0; j < 4096; j++) {
    if (j >= count) break;
    vec4 s0 = texelFetch(uSpurs, ivec2(3 * j, 0), 0);
    vec4 s2 = texelFetch(uSpurs, ivec2(3 * j + 2, 0), 0);
    if (layerSpurReads(R, s0, s2)) total = total + layerSpurExcess(R, phi, s0, texelFetch(uSpurs, ivec2(3 * j + 1, 0), 0), s2);
  }
  return total;
}
`;
