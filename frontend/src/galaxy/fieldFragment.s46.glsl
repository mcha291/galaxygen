
  uniform sampler2D plane;
  uniform sampler2D scatter;
  uniform sampler2D hii;
  uniform sampler2D rings;
  uniform float phase[21];
  uniform float rLo;
  uniform float rHi;
  // One texel's radial width, kpc (regimes.ts PlaneTexture.cell): the sub-steps' in-plane length.
  uniform float planeCell;
  uniform float halfHeight;
  uniform float starsHeight;
  uniform float dustHeight;
  uniform float hiiHeight;
  uniform float digHeight;
  uniform float bulgeScale;
  uniform vec3 bulgeLight;
  uniform float gain;
  // The region regime's window (r_min, r_max, phi_min, phi_max) and how far its resolved HII spheres have
  // faded in: inside it the field's HII steps back by the same weight (S40, no double counting).
  uniform vec4 regionWindow;
  uniform float hiiFade;
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
    return textureLod(rings, vec2((r - rLo) / (rHi - rLo), (row + 0.5) / 3.0), 0.0).rgb;
  }

  float inRegion(vec2 rp) {
    return (rp.x >= regionWindow.x && rp.x <= regionWindow.y && rp.y >= regionWindow.z && rp.y <= regionWindow.w) ? 1.0 : 0.0;
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
    float jitter = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453);
    vec3 light = vec3(0.0);
    vec3 transmitted = vec3(1.0);
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
      int n = int(clamp(ceil(length(p1.xz - p0.xz) / planeCell), 1.0, 8.0));
      float sub = ds / float(n);
      for (int j = 0; j < 8; j++) {
        if (j >= n) break;
        vec3 q0 = p0 + dir * (float(j) * sub);
        vec3 q1 = p0 + dir * (float(j + 1) * sub);
        vec3 emitted = bulge / float(n);
        vec3 depth = vec3(0.0);
        vec2 rp = polarOf(readPoint(q0, q1, jitter));
        // Beyond rHi every texture is zero: the box's side faces clip nothing but zeros.
        if (rp.x < rHi) {
          float cStars = column(q0.y, q1.y, starsHeight, sub);
          float cDust = column(q0.y, q1.y, dustHeight, sub);
          float cHii = column(q0.y, q1.y, hiiHeight, sub);
          float cDig = column(q0.y, q1.y, digHeight, sub);
          emitted += readPolar(plane, rp).rgb * cStars;
          emitted += (readPolar(scatter, rp).rgb * scattering + readRing(rp.x, 2.0)) * cDust;
          emitted += readPolar(hii, rp).rgb * cHii * (1.0 - hiiFade * inRegion(rp)) + readRing(rp.x, 1.0) * cDig;
          depth = readRing(rp.x, 0.0) * cDust;
        }
        // Light mixed through its own dust leaves (1 − e^−τ)/τ of itself; each sub-step's dust dims
        // only what lies behind it, so light and dust keep their order inside a long step.
        vec3 own = mix(vec3(1.0) - 0.5 * depth, (vec3(1.0) - exp(-depth)) / max(depth, vec3(1e-6)), step(vec3(1e-3), depth));
        light += transmitted * emitted * own;
        transmitted *= exp(-depth);
      }
    }
    gl_FragColor = vec4(light * gain, 1.0);
  }
