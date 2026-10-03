
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
    return textureLod(rings, vec2((r - rLo) / (rHi - rLo), (0.0 + 0.5) / 3.0), 0.0).a;
  }
  // The dust layer's scale height at a ring, kpc (D206): the thermal row's spare channel (regimes.ts planeTexture).
  float readHeight(float r) {
    return textureLod(rings, vec2((r - rLo) / (rHi - rLo), (2.0 + 0.5) / 3.0), 0.0).a;
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
        float hDust = 0.0;
        if (rp.x < rHi) {
          starsLight = readPolar(plane, rp).rgb * starsGain;
          // Where it is (D205): a diagnostic, the ring's level on the declared ramp in its declared scale, in the
          // ramp's colour at that level, spread through the dust's layer by its column; it dims nothing.
          float level = readLevel(rp.x);
          // The dust's column here over its ring's mean (D207): the model's placement, in the scattered
          // light's spare channel. It multiplies the depth, the thermal light and the diagnostic — everything that
          // is the dust's own column — and not the scattered light, already a share of the placed starlight.
          vec4 scattered = readPolar(scatter, rp);
          float place = scattered.a;
          dustLight = (scattered.rgb * scattering + readRing(rp.x, 2.0) * place) * dustGain + dustWhere * level * whereTint(level) * place;
          hiiLight = readPolar(hii, rp).rgb * (1.0 - hiiFade * inRegion(rp)) * gasGain;
          digLight = readRing(rp.x, 1.0) * gasGain;
          tau = readRing(rp.x, 0.0) * place * dustDepth;
          hDust = readHeight(rp.x);
        }
        // Composed in order (D206; regimes.ts composeStep, line for line). The dust's layer is far thinner than
        // the stars' in the inner disc, so a sub-step that spans it is cut at fixed multiples of the dust's
        // height and its pieces taken front to back: the stars in front of the layer are not dimmed by it. The
        // layers are symmetric about the midplane, so heights run upward along the ray in u.
        float sgn = q1.y >= q0.y ? 1.0 : -1.0;
        float u0 = sgn * q0.y;
        float u1 = sgn * q1.y;
        float du = u1 - u0;
        bool whole = hDust <= 0.0 || du <= 1e-6 * hDust;
        for (int m = 0; m <= 14; m++) {
          float a = u0;
          float b = u1;
          float share = 1.0;
          if (whole) {
            if (m > 0) break;
          } else {
            a = max(u0, m == 0 ? -1.0e9 : dustCut(m - 1) * hDust);
            b = min(u1, m == 14 ? 1.0e9 : dustCut(m) * hDust);
            if (b <= a) continue;
            share = (b - a) / du;
          }
          float piece = sub * share;
          float cDust = column(a, b, hDust, piece);
          vec3 emitted = bulgeSub * share + starsLight * column(a, b, starsHeight, piece) + dustLight * cDust
            + hiiLight * column(a, b, hiiHeight, piece) + digLight * column(a, b, digHeight, piece);
          vec3 depth = tau * cDust;
          // Light mixed through its own dust leaves (1 − e^−τ)/τ of itself; each piece's dust dims only what
          // lies behind it, so light and dust keep their order inside a long step.
          vec3 own = mix(vec3(1.0) - 0.5 * depth, (vec3(1.0) - exp(-depth)) / max(depth, vec3(1e-6)), step(vec3(1e-3), depth));
          light += transmitted * emitted * own;
          transmitted *= exp(-depth);
        }
      }
    }
    gl_FragColor = vec4(light * gain, 1.0);
  }
