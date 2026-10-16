
  uniform sampler2D plane;
  uniform sampler2D scatter;
  uniform sampler2D hii;
  uniform sampler2D rings;
  uniform float phase[21];
  uniform float rLo;
  uniform float rHi;
  // One texel's radial width, kpc (regimes.ts PlaneTexture.cell): the sub-steps' in-plane length.
  uniform float planeCell;
  // The most sub-samples a step reads (the Tuning panel's cap, D199), at most the loop's 8.
  uniform float subMax;
  // 1 offsets each step by the pixel's fixed fraction; 0 reads each sub-step at its middle (D199).
  uniform float dither;
  uniform float halfHeight;
  // The layers' scale heights, kpc (the render header's layers). The dust's is per ring since D206 and rides in
  // the ring texture (readHeight).
  uniform float starsHeight;
  uniform float hiiHeight;
  uniform float digHeight;
  uniform float bulgeScale;
  uniform vec3 bulgeLight;
  uniform float gain;
  // The region regime's window (r_min, r_max, phi_min, phi_max) and how far its resolved HII spheres have
  // faded in: inside it the field's HII steps back by the same weight (S40, no double counting).
  uniform vec4 regionWindow;
  uniform float hiiFade;
  // The component layers (D205, S50): each emitting layer's multiplier, the dust's depth switch and the
  // "where it is" diagnostic's light per unit of the dust's column share and its declared ramp. The field's are
  // 1, 1, 1, 1 and 0 (components.ts FIELD_LAYERS): every term below is multiplied by one or has zero added, so
  // the field draws as before, to the bit.
  uniform float starsGain;
  uniform float gasGain;
  uniform float dustGain;
  uniform float dustDepth;
  uniform float dustWhere;
  uniform vec3 whereStops[8];
  // The clouds' raster (S64, V6): face-on A_V per texel over the plane's polar extent, and beside it each texel's slab
  // (its clouds' mean height and half-thickness, kpc: cloudOpacity.ts); each channel's depth per magnitude
  // (cloudOpacity.ts cloudDepthScale); 1 to draw them, 0 not.
  uniform sampler2D cloudTex;
  uniform sampler2D cloudSlab;
  uniform vec3 cloudExt;
  uniform float cloudsOn;
  // The knots' undrawn share (S64, V6, R5): per level-0 cell, 1 - D_c / K_c (knots.ts undrawnShare), a sectors x rings
  // texture; the cells' radial edges and counts (lo, hi, rings, sectors: the clusters header's knots.layout); 1 to read
  // it, 0 to leave the field's HII whole.
  uniform sampler2D hiiShare;
  uniform vec4 shareCells;
  uniform float shareOn;
  // The randomness layer in the march (S66, BUILD_III V7; D226 R3-R5), each 1 only where the render header carries its
  // field (its seed non-null: the layer on) and its switch is on, else 0 - and then nothing below reads it, so under
  // "physics only" every map is exactly 1 and the march is the S64 one (R9c). gasFluct: the gas fluctuation map times
  // the dust's placement. spursOn: the spurs from their table (spurCount rows) in place of their cell means. youngClump:
  // the young and the middle part's kept light (clump3, clump2, clump1: the textures of k = 3, 2, 1 octaves, placed by
  // their weights) times the k-octave map over its level-0 cell's k-octave mean (clusterMeans: rgb = k 3, 2, 1).
  uniform float gasFluct;
  uniform float spursOn;
  uniform int spurCount;
  uniform float youngClump;
  uniform sampler2D clump3;
  uniform sampler2D clump2;
  uniform sampler2D clump1;
  uniform highp sampler2D clusterMeans;

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

  varying vec3 vWorld;

  // The column of a sech²(y / 2h) / 4h layer, which integrates to 1 over height, along the ray
  // from height y0 to y1 over a path ds: its share of height, over the ray's slope. A ray
  // running level through the layer takes the density at its height times the path.
  // tanh clamped: some drivers build it from exp, which overflows to NaN far outside the layer.
  float sech2(float x) { float c = cosh(clamp(x, -30.0, 30.0)); return 1.0 / (c * c); }
  float safeTanh(float x) { return tanh(clamp(x, -10.0, 10.0)); }
  float column(float y0, float y1, float h, float ds) {
    if (h <= 0.0) return 0.0;
    float dy = y1 - y0;
    if (abs(dy) < 1e-4 * h) return sech2(0.5 * (y0 + y1) / (2.0 * h)) / (4.0 * h) * ds;
    return abs(safeTanh(y1 / (2.0 * h)) - safeTanh(y0 / (2.0 * h))) * 0.5 * ds / abs(dy);
  }

  // Where to read the layers over a sub-step from p0 to p1: where it crosses the midplane, or else the
  // pixel's fixed fraction 'at' along it (the screen-space dither, never frame-seeded: RENDER_PHYSICS §8).
  vec3 readPoint(vec3 p0, vec3 p1, float at) {
    if (p0.y * p1.y < 0.0) return mix(p0, p1, p0.y / (p0.y - p1.y));
    return mix(p0, p1, at);
  }

  // Radius and azimuth in the stars' frame: x = r cos φ, z = −r sin φ.
  vec2 polarOf(vec3 p) {
    float phi = atan(-p.z, p.x);
    if (phi < 0.0) phi += 6.28318531;
    return vec2(length(p.xz), phi);
  }

  // An explicit level: implicit derivatives inside a loop and a branch are undefined, and some
  // drivers' compilers expand them into shaders that take seconds to build.
  vec4 readPolar(sampler2D tex, vec2 rp) {
    return textureLod(tex, vec2((rp.x - rLo) / (rHi - rLo), rp.y / 6.28318531), 0.0);
  }
  vec3 readRing(float r, float row) {
    return textureLod(rings, vec2((r - rLo) / (rHi - rLo), (row + 0.5) / 4.0), 0.0).rgb;
  }

  float inRegion(vec2 rp) {
    return (rp.x >= regionWindow.x && rp.x <= regionWindow.y && rp.y >= regionWindow.z && rp.y <= regionWindow.w) ? 1.0 : 0.0;
  }

  // The share of the field's HII light the drawn knots leave in the level-0 cell at rp (knots.ts cellAt, line for
  // line); 1 outside the cells or with none drawn.
  float knotShare(vec2 rp) {
    if (shareOn < 0.5 || rp.x < shareCells.x || rp.x >= shareCells.y) return 1.0;
    float ring = min(shareCells.z - 1.0, floor((rp.x - shareCells.x) / (shareCells.y - shareCells.x) * shareCells.z));
    float sector = min(shareCells.w - 1.0, floor(rp.y / 6.28318531 * shareCells.w));
    return textureLod(hiiShare, vec2((sector + 0.5) / shareCells.w, (ring + 0.5) / shareCells.z), 0.0).r;
  }

  // regimes.ts's phaseAt, line for line: the table read linearly at |cos i|.
  float phaseAt(float cosView) {
    float x = clamp(abs(cosView), 0.0, 1.0) * float(20);
    int k = min(int(floor(x)), 19);
    float lo = phase[0];
    float hi = phase[1];
    for (int n = 0; n < 20; n++) {
      if (n == k) { lo = phase[n]; hi = phase[n + 1]; }
    }
    return lo + (hi - lo) * (x - float(k));
  }

  // The dust diagnostic's ramp (D205), components.ts whereTint line for line: its stops read linearly at t.
  vec3 whereTint(float t) {
    float x = clamp(t, 0.0, 1.0) * float(7);
    int k = min(int(floor(x)), 6);
    vec3 lo = whereStops[0];
    vec3 hi = whereStops[1];
    for (int n = 0; n < 7; n++) {
      if (n == k) { lo = whereStops[n]; hi = whereStops[n + 1]; }
    }
    return lo + (hi - lo) * (x - float(k));
  }
  // Each ring's level on the dust's declared ramp (components.ts dustLevels), held in the depth row's spare channel.
  float readLevel(float r) {
    return textureLod(rings, vec2((r - rLo) / (rHi - rLo), (0.0 + 0.5) / 4.0), 0.0).a;
  }
  // The dust layer's scale height at a ring, kpc (D206): the thermal row's spare channel (regimes.ts planeTexture).
  float readHeight(float r) {
    return textureLod(rings, vec2((r - rLo) / (rHi - rLo), (2.0 + 0.5) / 4.0), 0.0).a;
  }
  // The column of a uniform slab of face-on depth 1 between heights lo and hi (regimes.ts slabColumn, line for line).
  float slabColumn(float y0, float y1, float lo, float hi, float ds) {
    float thick = hi - lo;
    if (thick <= 0.0) return 0.0;
    float dy = y1 - y0;
    if (abs(dy) < 1e-4 * thick) {
      float mid = 0.5 * (y0 + y1);
      return (mid >= lo && mid <= hi) ? ds / thick : 0.0;
    }
    float overlap = max(0.0, min(max(y0, y1), hi) - max(min(y0, y1), lo));
    return overlap / thick * ds / abs(dy);
  }
  // The spurs' mean round the ring at r (S66, D226 R4): the diffuse gas row's spare channel (regimes.ts planeTexture).
  float readSpurShare(float r) {
    return textureLod(rings, vec2((r - rLo) / (rHi - rLo), (1.0 + 0.5) / 4.0), 0.0).a;
  }

  // The randomness layer's functions (noise.glsl.ts, the include the twin and the GPU probe hold to the model's vectors).

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


  // The young light clustered (S66, D226 R5a-b): each k-octave map over the map's mean in its level-0 cell (the gas
  // field's cells: ring by its edges, sector by azimuth), so a cell's light is kept on the model's lattice - k = 3, 2, 1
  // in x, y, z, at the screen point xy. A mean that is not a positive number leaves its share unmodulated.
  vec3 clusterRatios(vec2 xy) {
    vec3 maps = layerClusterMaps(xy);
    vec3 mean = texelFetch(clusterMeans, ivec2(layerGasSector(xy), layerGasRing(length(xy))), 0).rgb;
    return vec3(mean.x > 0.0 ? maps.z / mean.x : 1.0, mean.y > 0.0 ? maps.y / mean.y : 1.0, mean.z > 0.0 ? maps.x / mean.z : 1.0);
  }
  // Each kept share at the sub-step's read point times its ratio (clusterRatios, read once per ray).
  vec3 clumpedLight(vec3 ratio, vec2 rp) {
    return readPolar(clump3, rp).rgb * ratio.x + readPolar(clump2, rp).rgb * ratio.y + readPolar(clump1, rp).rgb * ratio.z;
  }

  // Where a sub-step is cut as it crosses the dust's layer, in the dust's scale heights (regimes.ts DUST_CUTS).
  float dustCut(int k) {
    if (k == 0) return -11.00;
    if (k == 1) return -8.00;
    if (k == 2) return -6.00;
    if (k == 3) return -4.50;
    if (k == 4) return -3.00;
    if (k == 5) return -2.00;
    if (k == 6) return -1.00;
    if (k == 7) return 1.00;
    if (k == 8) return 2.00;
    if (k == 9) return 3.00;
    if (k == 10) return 4.50;
    if (k == 11) return 6.00;
    if (k == 12) return 8.00;
    return 11.00;
  }

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

    // The scattered light this view receives: the disc's axis is y.
    float scattering = phaseAt(dir.y);
    // Steps spaced geometrically from the camera: fine where the galaxy is close and large on
    // screen, coarse where it is far and small. Even steps along a 60 kpc ray pass straight
    // over a disc 0.3 kpc thick a few hundred parsecs away.
    float tStart = max(tNear, 0.01);
    float ratio = pow(max(tFar, tStart * 1.0001) / tStart, 1.0 / float(96));
    // A per-pixel offset turns banding into fine noise: into each step for the bulge's point sample, and
    // into each sub-step for the layers' reads. Fixed by the pixel, never by the frame.
    float jitter = dither > 0.5 ? fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453) : 0.5;
    vec3 light = vec3(0.0);
    vec3 transmitted = vec3(1.0);
    // The layer's maps as a thin screen (S66, D226 R3/R5 as amended): the gas fluctuation map, the spurs' sum and the
    // clustering maps are face-on column maps, read once per ray where it crosses the midplane (y = 0) - or, for a ray
    // that does not cross it inside the march (|dir.y| under 1e-6, or the crossing outside [tStart, tFar]), at its start
    // point's projection - and each value multiplies every sub-step's placement as below. The alternative, the map read
    // at each sub-step's own point: a column map drawn through the layer makes each feature a pillar of the layer's
    // height, smeared by h tan i along the view (the streaks of the first capture); a thin screen at the midplane
    // displaces nothing - a declared approximation. With the layer off none of them is read (each uniform 0).
    float tCross = abs(dir.y) > 1e-6 ? -origin.y / dir.y : -1.0;
    vec3 screen = (tCross >= tStart && tCross <= tFar) ? origin + dir * tCross : origin + dir * tStart;
    vec2 screenXY = vec2(screen.x, -screen.z);
    vec2 screenRP = polarOf(screen);
    float screenGas = gasFluct > 0.5 ? layerGasMap(screenXY) : 1.0;
    float screenSpurs = spursOn > 0.5 ? layerSpurSum(screenRP.x, screenRP.y, spurCount) : 0.0;
    vec3 screenClumps = youngClump > 0.5 ? clusterRatios(screenXY) : vec3(1.0);
    for (int k = 0; k < 96; k++) {
      float a = tStart * pow(ratio, float(k));
      float ds = a * (ratio - 1.0);
      vec3 p = origin + dir * (a + jitter * ds);
      float s = max(length(p), 0.02);
      vec3 bulge = bulgeLight * bulgeScale / (6.28318531 * s * pow(s + bulgeScale, 3.0)) * 1.0e-6 * ds;

      // The disc's layers over the whole step, [a, a + ds], in n sub-steps of at most about one plane
      // cell in the plane each (regimes.ts subSamples). The bulge's light is spread evenly over them, so
      // it sits in the same dust as before; with n = 1 this is the single read per step of S39.
      vec3 p0 = origin + dir * a;
      vec3 p1 = p0 + dir * ds;
      int n = int(clamp(ceil(length(p1.xz - p0.xz) / planeCell), 1.0, subMax));
      float sub = ds / float(n);
      for (int j = 0; j < 8; j++) {
        if (j >= n) break;
        vec3 q0 = p0 + dir * (float(j) * sub);
        vec3 q1 = p0 + dir * (float(j + 1) * sub);
        vec3 bulgeSub = bulge * starsGain / float(n);
        vec2 rp = polarOf(readPoint(q0, q1, jitter));
        // What the sub-step reads, once: each layer's light per unit of its own column, the dust's depth per
        // unit of the dust's, and the dust layer's height at this ring (D206). Beyond rHi every texture is
        // zero: the box's side faces clip nothing but zeros.
        vec3 starsLight = vec3(0.0);
        vec3 dustLight = vec3(0.0);
        vec3 hiiLight = vec3(0.0);
        vec3 digLight = vec3(0.0);
        vec3 tau = vec3(0.0);
        vec3 tauC = vec3(0.0);
        vec2 slab = vec2(0.0);
        float hDust = 0.0;
        if (rp.x < rHi) {
          starsLight = readPolar(plane, rp).rgb * starsGain;
          // The young light clustered (S66, V7): its shares here times the screen's ratios.
          if (youngClump > 0.5) starsLight += clumpedLight(screenClumps, rp) * starsGain;
          // Where it is (D205): a diagnostic, the ring's level on the declared ramp in its declared scale, in the
          // ramp's colour at that level, spread through the dust's layer by its column; it dims nothing.
          float level = readLevel(rp.x);
          // The dust's column here over its ring's mean (D207): the model's placement, in the scattered
          // light's spare channel. It multiplies the depth, the thermal light and the diagnostic — everything that
          // is the dust's own column — and not the scattered light, already a share of the placed starlight.
          vec4 scattered = readPolar(scatter, rp);
          float place = scattered.a;
          // The spurs (S66, V7, D226 R4; D221 item 7): g' = (1 - <S>(R)) g + S, g the placement without them (the HII
          // texture's spare channel) read here and S their sum on the screen (over the rows its radius reads).
          if (spursOn > 0.5) place = (1.0 - readSpurShare(rp.x)) * readPolar(hii, rp).a + screenSpurs;
          // The gas fluctuation (S66, V7, D226 R3): the screen's map times the placement, in one statement, so that
          // whatever reads place below is the S64 march's.
          if (gasFluct > 0.5) place *= screenGas;
          dustLight = (scattered.rgb * scattering + readRing(rp.x, 2.0) * place) * dustGain + dustWhere * level * whereTint(level) * place;
          hiiLight = readPolar(hii, rp).rgb * (1.0 - hiiFade * inRegion(rp)) * gasGain * knotShare(rp);
          digLight = readRing(rp.x, 1.0) * gasGain;
          // The diffuse dust (S64): the ring's depth times its placement times the share the realised clouds leave.
          tau = readRing(rp.x, 0.0) * place * readRing(rp.x, 3.0).r * dustDepth;
          hDust = readHeight(rp.x);
          // The clouds' own dust (S64): the raster's face-on A_V here times each channel's depth per magnitude.
          tauC = readPolar(cloudTex, rp).r * cloudExt * cloudsOn * dustDepth * (1.0 - hiiFade * inRegion(rp));
          slab = readPolar(cloudSlab, rp).rg;
        }
        // Composed in order (D206; regimes.ts composeStep, line for line). The dust's layer is far thinner than
        // the stars' in the inner disc, so a sub-step that spans it is cut at fixed multiples of the dust's
        // height and its pieces taken front to back: the stars in front of the layer are not dimmed by it. The
        // layers are symmetric about the midplane, so heights run upward along the ray in u (the clouds' slab, which is
        // not, mirrored with them). With the slab (S64) the pieces are cut at the dust's cuts and at the slab's
        // SLAB_PIECES equal parts, merged in order of height.
        float sgn = q1.y >= q0.y ? 1.0 : -1.0;
        float u0 = sgn * q0.y;
        float u1 = sgn * q1.y;
        float du = u1 - u0;
        bool clouds = max(tauC.r, max(tauC.g, tauC.b)) > 0.0 && slab.y > 0.0;
        bool dusty = hDust > 0.0;
        float lo = sgn * slab.x - slab.y;
        float hi = sgn * slab.x + slab.y;
        float hMin = (dusty && clouds) ? min(hDust, slab.y) : (dusty ? hDust : (clouds ? slab.y : 0.0));
        bool whole = hMin <= 0.0 || du <= 1e-6 * hMin;
        int pd = 0;
        int ps = 0;
        float a = u0;
        for (int m = 0; m <= 19; m++) {
          float b = u1;
          float share = 1.0;
          if (whole) {
            if (m > 0) break;
          } else {
            float nd = (dusty && pd < 14) ? dustCut(pd) * hDust : 1.0e9;
            float ns = (clouds && ps <= 4) ? lo + (hi - lo) * float(ps) / 4.0 : 1.0e9;
            b = min(u1, min(nd, ns));
            if (nd <= ns) pd++; else ps++;
            if (b <= a) continue;
            share = (b - a) / du;
          }
          float piece = sub * share;
          float cDust = column(a, b, hDust, piece);
          vec3 emitted = bulgeSub * share + starsLight * column(a, b, starsHeight, piece) + dustLight * cDust
            + hiiLight * column(a, b, hiiHeight, piece) + digLight * column(a, b, digHeight, piece);
          vec3 depth = tau * cDust + (clouds ? tauC * slabColumn(a, b, lo, hi, piece) : vec3(0.0));
          // Light mixed through its own dust leaves (1 − e^−τ)/τ of itself; each piece's dust dims only what
          // lies behind it, so light and dust keep their order inside a long step.
          vec3 own = mix(vec3(1.0) - 0.5 * depth, (vec3(1.0) - exp(-depth)) / max(depth, vec3(1e-6)), step(vec3(1e-3), depth));
          light += transmitted * emitted * own;
          transmitted *= exp(-depth);
          a = b;
          if (a >= u1) break;
        }
      }
    }
    gl_FragColor = vec4(light * gain, 1.0);
  }
