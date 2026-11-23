// The illustrative look's registry (S105, BUILD_VIII row 105, D275). Under the look "physical" nothing here runs: the
// march's fragment is fieldFragment() as pinned, the points' vertex shader FluxPoints' own, no grade pass, the stands
// and the sample's opacity the template's. Under "illustrative" the features below draw display-only structure and
// colour of the viewer's own, tuned to the goal pictures.
//
// THE CONTRACT A FEATURE FILE KEEPS (read feature.ts for the types). A feature is one file in this directory exporting an
// IllFeature, listed once in FEATURES below. Adding a control, a uniform, a GLSL body or an array to a feature needs no
// edit anywhere else: the Tuning panel's "Illustrative" group, the stored and pasted combinations (Tuning.ill, keys
// `${id}.${key}`, clamped to each control's range, diffed against the template's illustrative defaults), the shaders
// and the one /api/arrays request all read this registry.
//
//   controls   sliders; `default`, or `perTemplate[template]` - the illustrative preset's value on that template.
//   glsl       global-scope GLSL put into BOTH the march's fragment (FieldVolume) and the points' vertex shader
//              (FluxPoints, every point and knot): uniforms and functions. Available there: `rHi` (float, kpc: the grid's
//              outer radius; every published texture reads zero beyond it), `cloudExt` (vec3: each channel's optical depth
//              per magnitude of A_V, the dust grains' reddening through the filter set) and `vec4 illMap(vec2 rp)` (the
//              shared map below, read at rp: u = R / rHi, v = phi / 2 pi). Name everything with the feature's prefix
//              (illLanes..., uniform illLanesWidth). NO SAMPLER: the pinned march declares 15 of WebGL's 16 fragment
//              texture units, and the shared map takes the last; a feature's GLSL that declares a sampler fails the
//              march's program and the whole field goes undrawn (S105: 17 units, a black disc). illustrative.test.ts
//              counts them.
//   map        the shared illustrative map (feature.ts IllMapBuilder, ILL_MAP): ONE RGBA8 texture over the disc on the
//              lanes' grid (2000 x 3600, row = phi, clamped in R, wrapped in phi, linear), owned by this registry and
//              declared once as `uniform sampler2D illMapTex`, read through illMap(rp). Channels: R the lanes, G the
//              flocculent network, B and A the arms (feature.ts ILL_MAP_CHANNELS). A feature names its channels and a
//              builder of one byte plane per channel (null: zero), cached by the feature (memoOn); the registry
//              composes the planes and re-uploads only when a plane's object changes. The same texture is handed to the
//              points' vertex shader. A feature's own layer material (`layer`) may still bind samplers of its own.
//              S107 (the sliders' stall): the planes are built OFF the main thread, by the map worker (illMapClient.ts,
//              illMapJob.ts; stepRuntime below): it runs the builders themselves and hands back each NAMED memo's build
//              (memoOn(build, "<feature>.<what>")), which the main thread puts in the same cache - so a plane's memo
//              must be named, and a builder must be a pure function of its params and context (no DOM, no WebGL, no
//              module state but its memos: it runs in a worker too). An unnamed plane memo still works, built on the
//              main thread when drawn (a stall over ~0.1 s on its slider is a defect). Until the planes arrive the view
//              draws the previous map; the look capture waits for them (window.__galaxygenIllPending).
//   hooks      which of its GLSL functions take part in the march (rp = vec2(R kpc, phi rad), phi = atan(-z, x) in
//              [0, 2 pi), the model's galactocentric azimuth; R cylindrical):
//     dustAv    float f(vec2 rp): extra face-on A_V, magnitudes, at the midplane point rp. All features' are summed into
//               illDustAv(rp). The march adds illDustAv(rp) * cloudExt * dustDepth to each sub-step's diffuse optical
//               depth, so it lies in the dust's own sech2 layer, reddens per channel exactly as the clouds do and follows
//               the extinction strength; the points' dustTo adds the same along each point's segment to the camera, so a
//               lane dims the stars and knots behind it as it dims the field.
//     youngGain float f(vec2 rp): a multiplier on the young starlight - the clustered march's young and kept middle
//               shares (FieldVolume's clumpedLight; drawn while the randomness layer and "young light clustered in the
//               march" are on, the default). Multiplied over features into illYoungGain(rp). With the layer off there is
//               no separate young light and the hook reads nothing.
//     edge      float f(float r): a multiplier on all emission (stars, bulge, dust's own light, HII, diffuse gas) and on
//               the depths, at cylindrical radius r. Multiplied over features into illEdge(r).
//     veil      vec3 f(vec2 rp) (S107): a per-channel multiplier on a ray's WHOLE light, read once per ray where it
//               crosses the midplane (the march's thin screen, screenRP). Multiplied over features into illVeil(rp).
//               A drawing laid over the picture - a lane inked in front of all the starlight, which a depth in the
//               dust's thin layer cannot do (half the stars stand in front of it) - and so the march's alone: the
//               points are not veiled.
//     light     vec3 f(vec2 rp): a per-channel multiplier on all the disc's starlight at the midplane point rp (the
//               plane's light and the clustered young light; not the bulge, the dust's, the HII's or the gas's).
//               Multiplied over features into illLight(rp) (S108, the arms).
//     gas       float f(vec2 xy, float g) (S106, the base): the randomness layer's gas fluctuation map g read at the
//               face-on point xy (kpc; the include's frame, x = scene x, y = -scene z) made the value the dust's
//               placement is multiplied by. Chained over features into illGas(xy, g) (each feature's f applied to the
//               last one's value). The march's screenGas and FluxPoints' gasAt, so the points' dust follows the field's;
//               read only while the map is drawn ("gas fluctuation in the march" on, the layer on). Its function is
//               defined in the feature's `noiseGlsl`.
//     points    float f(vec2 rp) (S108, the points' edge): a multiplier on every point's light FluxPoints draws (the
//               star-first mode's stars and clusters, the region's stars, the knots) at the point's own midplane place
//               rp. Multiplied over features into illPoints(rp); read in FluxPoints' vertex shader only (the march's
//               light is the edge hook's), so the points fade with the field's taper.
//     depth     vec3 f(vec3 d, vec2 rp) (S106, the base's mend and core): the ring texture's published face-on diffuse
//               depth per channel d (row 0 of `rings`, as read at rp, before the placement, the clouds' share and the
//               extinction strength multiply it) made the depth the dust's layer carries. Chained over features into
//               illDepth(d, rp). The march's tau (its own patch, on the tau line; the layer's dustAv is added after it)
//               and FluxPoints' face (on the dustAv patch's anchor), so the points' dust takes the same. Defined in the
//               feature's `noiseGlsl`: it may read `rings`, `rLo` and `cloudExt`, which only those two shaders declare.
//     graze     (S108, the grazing handover; GRAZE_DEFAULT below) not a hook: every shader the layer's GLSL is in
//               carries `float illGraze`, 1 from face-on to base.grazeFrom off the disc's axis, 0 from base.grazeTo
//               (per ray in the march, per point's sight line in FluxPoints and the regions). The composition fades a
//               hook's value to its identity by it where the feature's `graze` (or the kind's default) says "fade"
//               (the veil and the light by default); a feature's GLSL may read illGraze for its own removals of the
//               model's physics (base: the dust's placement, the grain, the core; edge: the bulge's dimming; lanes and
//               floc: the ink handed to the dust's own layer). Exactly the S107 values while illGraze is 1.
//   noiseGlsl  (S106) global-scope GLSL put only where the randomness layer's include (noise.glsl.ts) is - the march's
//              fragment and FluxPoints' vertex shader, after every feature's `glsl` - so it may call layerGasMap,
//              layerGasSum and the rest and read their uniforms. Other layers' shaders (runtime.glsl: the knots' layer)
//              get illGlsl() without it.
//   uniforms   (params, context) => values for its uniforms (numbers and vectors; never a texture for the march - see
//              `map`). Called at every change of a parameter or of the context (the template; the arrays' frame); handed
//              to the march and every point's material through the same uniform object, so neither FieldVolume nor
//              FluxPoints is edited for it. A change re-marches the field.
//   context    (S106, B4) what map builders, uniforms and layers receive besides their own params: the template, the
//              arrays' frame, and `paramsOf(featureId)` - every feature's CURRENT (drawn) parameters, read-only, bound
//              here (illContextFor) around every call and by GalaxyTab for the layers. A feature may read another's live
//              sliders through it (the lanes read the arms' skel* sliders: armsSkeleton.ts currentSkeleton); a value read
//              so that shapes a plane goes into that plane's memoOn keys, so the plane rebuilds - debounced like the
//              owner's own map-shaping sliders (illEffective holds a cross-read change until the sliders settle).
//   arrays     /api/arrays names (e.g. the arm pieces' columns); all features' are asked in one request.
//   layer      a React component drawn in the Galaxy view's canvas (IllLayerProps: the knots, their gain, the dust).
//   replacesKnots  true where its layer draws in place of the field mode's default knots.
//
// The grade (grade.ts) is not a march hook: GalaxyView's composer runs it as a pass after the bloom. The speckle and the
// framing are read by GalaxyTab (speckle.ts sampleOpacity, framing.ts standScale).

import { ClampToEdgeWrapping, DataTexture, LinearFilter, RGBAFormat, RepeatWrapping, UnsignedByteType } from "three";

import { arms } from "./arms";
import { base } from "./base";
import { edge } from "./edge";
import { ILL_MAP, type IllContext, type IllControl, type IllFeature, type IllFrame, type IllParams, illMeasure, illNow, releaseMemos, wouldBuild } from "./feature";
import { floc } from "./floc";
import { illMapAnswered, illMapFailed, illMapKey, releaseIllJobs, startIllMap } from "./illMapClient";
import { framing } from "./framing";
import { POINTS_PLACE_GLSL } from "./pointsPlace";
import { grade } from "./grade";
import { knots } from "./knots";
import { lanes } from "./lanes";
import { points } from "./points";
import { sky } from "./sky";
import { speckle } from "./speckle";

export type { IllContext, IllControl, IllFeature, IllLayerProps, IllMapBuilder, IllParams } from "./feature";
export { ILL_MAP, ILL_MAP_CHANNELS } from "./feature";

/** The two looks (D275). Physical: the viewer as it stood at S104. Illustrative: this directory's layer over it. */
export type Look = "physical" | "illustrative";
export const LOOKS: readonly Look[] = ["physical", "illustrative"];

/** The registered features, in order. Edited only to add a new file. */
const FEATURES: IllFeature[] = [grade, edge, speckle, framing, knots, lanes, arms, floc, base, sky, points];

/** The features registered now. */
export const features = (): readonly IllFeature[] => FEATURES;

/** A feature added at run time (the registry's test; a feature file is listed in FEATURES instead). */
export function registerFeature(f: IllFeature): () => void {
  if (FEATURES.some((g) => g.id === f.id)) throw new Error(`illustrative feature ${f.id} registered twice`);
  FEATURES.push(f);
  return () => {
    const i = FEATURES.indexOf(f);
    if (i >= 0) FEATURES.splice(i, 1);
  };
}

/** A control's stored key. */
export const illKey = (f: IllFeature, c: IllControl): string => `${f.id}.${c.key}`;

/** Every illustrative control, with its stored key and its feature. */
export function illControls(): { key: string; feature: IllFeature; control: IllControl }[] {
  return FEATURES.flatMap((feature) => feature.controls.map((control) => ({ key: illKey(feature, control), feature, control })));
}

/** The illustrative parameters' defaults on a template: each control's perTemplate value there, else its default. */
export function illDefaults(template: string | null | undefined): Record<string, number> {
  const out: Record<string, number> = {};
  for (const { key, control } of illControls()) out[key] = (template ? control.perTemplate?.[template] : undefined) ?? control.default;
  return out;
}

/** A value made valid for a control: a finite number clamped to its range; null if unusable. */
export function clampIll(control: IllControl, value: unknown): number | null {
  if (typeof value !== "number" || !Number.isFinite(value)) return null;
  return Math.min(control.max, Math.max(control.min, value));
}

/** Any object read as illustrative parameters over `base`: unknown keys dropped, bad values `base`'s, numbers clamped. */
export function sanitizeIll(raw: unknown, base: Readonly<Record<string, number>> = illDefaults(null)): Record<string, number> {
  const out: Record<string, number> = {};
  for (const { key, control } of illControls()) out[key] = clampIll(control, base[key]) ?? control.default;
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return out;
  for (const [key, value] of Object.entries(raw as Record<string, unknown>)) {
    const entry = illControls().find((c) => c.key === key);
    if (!entry) continue;
    const v = clampIll(entry.control, value);
    if (v !== null) out[key] = v;
  }
  return out;
}

/** What a pasted `ill` object holds that is not usable: unknown keys and unusable values, each as "ill.<key>". */
export function illProblems(raw: unknown): { ignored: string[]; rejected: string[] } {
  const ignored: string[] = [];
  const rejected: string[] = [];
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return { ignored, rejected: raw === undefined ? [] : ["ill"] };
  for (const [key, value] of Object.entries(raw as Record<string, unknown>)) {
    const entry = illControls().find((c) => c.key === key);
    if (!entry) ignored.push(`ill.${key}`);
    else if (clampIll(entry.control, value) === null) rejected.push(`ill.${key}`);
  }
  return { ignored, rejected };
}

/** The entries of `ill` that differ from `defaults`. */
export function illChanged(ill: Readonly<Record<string, number>>, defaults: Readonly<Record<string, number>>): Record<string, number> {
  const out: Record<string, number> = {};
  for (const { key } of illControls()) if (ill[key] !== undefined && ill[key] !== defaults[key]) out[key] = ill[key];
  return out;
}

/** A feature's own parameters, by its local keys. */
export function paramsOf(f: IllFeature, ill: Readonly<Record<string, number>>): IllParams {
  const out: Record<string, number> = {};
  for (const c of f.controls) out[c.key] = ill[illKey(f, c)] ?? c.default;
  return out;
}

/**
 * The context with `paramsOf` bound to these parameters (S106, B4; feature.ts IllContext.paramsOf): every feature's
 * current values by id, so a feature reads another's live sliders. Every call below binds it; GalaxyTab binds the
 * layers' context to the drawn parameters the same way.
 */
export function illContextFor(context: IllContext, ill: Readonly<Record<string, number>>): IllContext {
  const cache = new Map<string, IllParams>();
  return {
    ...context,
    paramsOf: (id: string) => {
      let p = cache.get(id);
      if (!p) {
        const f = FEATURES.find((g) => g.id === id);
        p = f ? paramsOf(f, ill) : {};
        cache.set(id, p);
      }
      return p;
    },
  };
}

// --- S108: the layer's seeds follow the generated galaxy ---------------------------------------------------------------
// The layer's drawings (floc's network, dust and clouds; the arms' skeleton; the regions' placement; the lanes' wander;
// the sparkle's stream) were drawn from fixed seeds of the layer's own, so a galaxy generated with other pattern and
// texture seeds kept the template's drawing. Now each such seed's effective value is its slider's value shifted by the
// galaxy's reroll (the frame's illReroll): the identity for the template's own seeds - the default galaxy's frames are
// today's byte for byte - and another drawing for each generated galaxy. The sliders still pick among drawings.

/** The seed sliders that follow the galaxy (S108). The sky's field stars do not: the sky is the viewer's. */
export const GALAXY_SEEDED: readonly string[] = ["floc.seed", "arms.skelseed", "knots.seed", "lanes.seed"];

/** A 32-bit integer mix (lowbias32). */
const mix32 = (x: number): number => {
  let h = x >>> 0;
  h ^= h >>> 16;
  h = Math.imul(h, 0x7feb352d);
  h ^= h >>> 15;
  h = Math.imul(h, 0x846ca68b);
  h ^= h >>> 16;
  return h >>> 0;
};
const stringHash = (s: string): number => {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 0x01000193);
  return h >>> 0;
};

/**
 * The galaxy's reroll (S108): 0 where its published pattern_seed and texture_seed (`inputs`, the frame header's) are the
 * template's own (`own`, the template's inputs.seeds; null: no template, 0), else a non-zero hash of the two.
 */
export function illReroll(inputs: unknown, own: Readonly<Record<string, number>> | null | undefined): number {
  if (!own || !inputs || typeof inputs !== "object") return 0;
  const got = inputs as Record<string, unknown>;
  const seed = (name: string): number | null => (typeof got[name] === "number" && Number.isFinite(got[name]) ? Math.round(got[name] as number) : null);
  const pattern = seed("pattern_seed");
  const texture = seed("texture_seed");
  if (pattern === null || texture === null) return 0;
  if (pattern === Math.round(own.pattern_seed ?? Number.NaN) && texture === Math.round(own.texture_seed ?? Number.NaN)) return 0;
  return mix32(mix32(pattern ^ 0x2545f491) ^ texture) || 1;
}

/** The frame with its reroll stamped on its header (a new object; the arrays shared). */
export function withIllReroll<F extends IllFrame>(frame: F, own: Readonly<Record<string, number>> | null | undefined): F {
  return { ...frame, header: { ...frame.header, illReroll: illReroll(frame.header.inputs, own) } };
}

/** A seed slider's value shifted by a non-zero reroll: another integer in the control's range, never its own value. */
export function rerolledSeed(control: IllControl, key: string, value: number, reroll: number): number {
  if (!reroll) return value;
  const lo = Math.ceil(control.min);
  const span = Math.floor(control.max) - lo + 1;
  if (span < 2) return value;
  const offset = 1 + (mix32(reroll ^ stringHash(key)) % (span - 1));
  return lo + ((((Math.round(value) - lo + offset) % span) + span) % span);
}

/**
 * The parameters the layer draws with for this galaxy (S108): `ill` itself (the same object) for the template's own
 * seeds or where no frame has come; else a copy with each GALAXY_SEEDED slider rerolled. GalaxyTab draws with it -
 * the map builders (main thread and worker), the uniforms, the layers and the cross-reads alike - while the panel
 * shows the sliders' own values.
 */
export function illSeeded(ill: Readonly<Record<string, number>>, context: IllContext): Readonly<Record<string, number>> {
  const reroll = context.frame?.header.illReroll ?? 0;
  if (!reroll) return ill;
  const out: Record<string, number> = { ...ill };
  for (const { key, control } of illControls()) {
    if (GALAXY_SEEDED.includes(key) && out[key] !== undefined) out[key] = rerolledSeed(control, key, out[key], reroll);
  }
  return out;
}

/** The /api/arrays names any feature asks for, sorted, once each. */
export function illArrays(): string[] {
  return [...new Set(FEATURES.flatMap((f) => f.arrays ?? []))].sort();
}

/**
 * THE GRAZING HANDOVER (S108). The layer is a face-on drawing: its thin-screen drawings (the veil, read once per ray at
 * the midplane) are smeared along the sight line as the ray turns into the plane, and its removals of the model's own
 * physics (the Milky Way's diffuse dust at a tenth, the bulge dimmed round the bar, NGC 4414's core cleared) take the
 * edge-on galaxy's dust lane and bulge away. So every shader the layer's GLSL is in carries `illGraze`, a weight per
 * ray (the march: its direction) or per point (the points: the sight line from the camera), 1 from face-on to the
 * handover's start angle off the disc's axis (`base.grazeFrom`), falling smoothly (a smoothstep in the angle) to 0 at
 * its end (`base.grazeTo`); exactly 1 up to the start, where every composed value below is the S107 value bit for bit.
 * The composition takes each feature's hook value toward the hook's identity by it where the feature's `graze` (or the
 * kind's default here) says "fade"; a feature's own removals of the model's physics read illGraze themselves (base,
 * edge). A shader that never sets illGraze (one the layer's GLSL reaches without a ray or a point) keeps 1.
 */
export const GRAZE_DEFAULT: Readonly<Record<keyof NonNullable<IllFeature["hooks"]>, "fade" | "keep">> = Object.freeze({
  // The thin screen's drawing and the disc's light tints (a face-on pattern: an edge-on slab in the layer's tints).
  veil: "fade",
  light: "fade",
  // Read at each sub-step's own point, in the layers' heights: real 3-D structure, kept.
  dustAv: "keep",
  youngGain: "keep",
  edge: "keep",
  // Chained values whose features handle the handover inside (base: the dust's placement and the grain).
  gas: "keep",
  depth: "keep",
  // The star-first points' own taper (S108, points.ts): a point's light by its radius, kept.
  points: "keep",
});

const grazeOf = (f: IllFeature, kind: keyof typeof GRAZE_DEFAULT): "fade" | "keep" => f.graze?.[kind] ?? GRAZE_DEFAULT[kind];

const hookCall = (kind: "dustAv" | "youngGain" | "edge" | "veil" | "light" | "points", arg: string, op: string, unit: string) => {
  const wrap = kind === "dustAv" ? "illGrazeAdd" : kind === "veil" || kind === "light" ? "illGrazeMul3" : "illGrazeMul";
  const calls = FEATURES.filter((f) => f.hooks?.[kind]).map((f) => {
    const call = `${f.hooks![kind]}(${arg})`;
    return grazeOf(f, kind) === "fade" ? `${wrap}(${call})` : call;
  });
  return calls.length ? calls.join(` ${op} `) : unit;
};

/** The registry's own GLSL of the handover: the weight, its uniform (base.ts's controls) and the fades. */
const GRAZE_GLSL = /* glsl */ `
  // The grazing handover (S108; index.ts GRAZE_DEFAULT): (from, to) radians off the disc's axis; to <= 0 off.
  uniform vec2 illGrazeAt;
  float illGraze = 1.0;
  float illGrazeOf(vec3 d) {
    float c = clamp(abs(d.y) / max(length(d), 1e-20), 0.0, 1.0);
    float a = acos(c);
    if (illGrazeAt.y <= 0.0 || a <= illGrazeAt.x) return 1.0;
    if (illGrazeAt.y <= illGrazeAt.x) return 0.0;
    return 1.0 - smoothstep(illGrazeAt.x, illGrazeAt.y, a);
  }
  float illGrazeAdd(float v) { return illGraze >= 1.0 ? v : v * illGraze; }
  float illGrazeMul(float v) { return illGraze >= 1.0 ? v : mix(1.0, v, illGraze); }
  vec3 illGrazeMul3(vec3 v) { return illGraze >= 1.0 ? v : mix(vec3(1.0), v, illGraze); }
  float illGrazeTo(float a, float b) { return illGraze >= 1.0 ? b : mix(a, b, illGraze); }
  vec3 illGrazeTo3(vec3 a, vec3 b) { return illGraze >= 1.0 ? b : mix(a, b, illGraze); }
  // A point layer's lift (S108): a point of the layer drawn in the midplane (the star clouds, the regions) raised by a
  // fixed normal deviate of its own (hashed from its face-on place) times h kpc times (1 - illGraze): a thin lit layer
  // seen edge-on, not a line; exactly the point itself while illGraze is 1 (every stand the look was tuned at).
  vec3 illLiftOf(vec3 p, float h) {
    if (h <= 0.0 || illGraze >= 1.0) return p;
    vec2 u = fract(sin(vec2(dot(p.xz, vec2(12.9898, 78.233)), dot(p.xz, vec2(39.3468, 11.1351)))) * 43758.5453);
    float n = sqrt(-2.0 * log(max(u.x, 1e-4))) * cos(6.28318531 * u.y);
    return vec3(p.x, p.y + h * (1.0 - illGraze) * n, p.z);
  }`;


/**
 * The noise-side GLSL (S106): every feature's noiseGlsl and the gas hook chained, for a shader that carries the
 * randomness layer's include (the march, FluxPoints).
 */
function noiseSide(): string[] {
  const step = (kind: "gas" | "depth", v: string, call: (n: string) => string) =>
    FEATURES.filter((f) => f.hooks?.[kind])
      .map((f) => (grazeOf(f, kind) === "fade" ? ` ${v} = ${kind === "gas" ? "illGrazeTo" : "illGrazeTo3"}(${v}, ${call(f.hooks![kind]!)});` : ` ${v} = ${call(f.hooks![kind]!)};`))
      .join("");
  return [
    ...FEATURES.map((f) => f.noiseGlsl ?? "").filter((g) => g.trim() !== ""),
    `  float illGas(vec2 xy, float g) {${step("gas", "g", (n) => `${n}(xy, g)`)} return g; }`,
    `  vec3 illDepth(vec3 d, vec2 rp) {${step("depth", "d", (n) => `${n}(d, rp)`)} return d; }`,
  ];
}

/**
 * The layer's GLSL: the helper, every feature's own GLSL, and the hooks composed over the features; with `noise` (the
 * march and FluxPoints, which carry noise.glsl.ts) also every feature's noiseGlsl and the gas hook.
 */
export function illGlsl(noise = false): string {
  return [
    "  // The illustrative look's GLSL (S105; illustrative/index.ts): display-only, absent under the physical look.",
    "  // The shared map, the layer's one sampler (R lanes, G floc, B and A arms): no feature declares another.",
    "  uniform sampler2D illMapTex;",
    "  vec4 illMap(vec2 rp) {",
    "    return textureLod(illMapTex, vec2(rp.x / rHi, rp.y / 6.28318531), 0.0);",
    "  }",
    GRAZE_GLSL,
    ...FEATURES.map((f) => f.glsl ?? "").filter((g) => g.trim() !== ""),
    `  float illDustAv(vec2 rp) { return ${hookCall("dustAv", "rp", "+", "0.0")}; }`,
    `  float illYoungGain(vec2 rp) { return ${hookCall("youngGain", "rp", "*", "1.0")}; }`,
    `  float illEdge(float r) { return ${hookCall("edge", "r", "*", "1.0")}; }`,
    `  vec3 illVeil(vec2 rp) { return ${hookCall("veil", "rp", "*", "vec3(1.0)")}; }`,
    `  vec3 illLight(vec2 rp) { return ${hookCall("light", "rp", "*", "vec3(1.0)")}; }`,
    `  float illPoints(vec2 rp) { return ${hookCall("points", "rp", "*", "1.0")}; }`,
    ...(noise ? noiseSide() : []),
    "",
  ].join("\n");
}

/** A patch: an exact existing line of a pinned shader and what it becomes. */
export interface Patch {
  anchor: string;
  apply(anchor: string, glsl: string): string;
}

/** The march's patches (FieldVolume's fieldFragment, frag lines ~495-590): each anchor must occur exactly once. */
export const MARCH_PATCHES: readonly Patch[] = [
  { anchor: "  void main() {", apply: (a, glsl) => `${glsl}\n${a}` },
  // S108: the ray's grazing weight, once per ray, before anything of the layer is read.
  { anchor: "    vec3 dir = normalize(vWorld - cameraPosition);", apply: (a) => `${a}\n    illGraze = illGrazeOf(dir);` },
  {
    anchor: "          if (youngClump > 0.5) starsLight += clumpedLight(screenClumps, rp) * starsGain;",
    apply: (a) => a.replace("* starsGain;", "* starsGain * illYoungGain(rp);"),
  },
  { anchor: "          hDust = readHeight(rp.x);", apply: (a) => `${a}\n          tau += illDustAv(rp) * cloudExt * dustDepth;` },
  { anchor: "          float level = readLevel(rp.x);", apply: (a) => `          starsLight *= illLight(rp);\n${a}` },
  {
    anchor: "        // Composed in order (D206; regimes.ts composeStep, line for line). The dust's layer is far thinner than",
    apply: (a) =>
      "        float illE = illEdge(rp.x);\n" +
      "        bulgeSub *= illE; starsLight *= illE; dustLight *= illE; hiiLight *= illE; digLight *= illE; tau *= illE; tauC *= illE;\n" +
      a,
  },
  // S107: the veil, over the ray's whole light at the thin screen's point.
  { anchor: "    gl_FragColor = vec4(light * gain, 1.0);", apply: (a) => a.replace("light * gain", "light * illVeil(screenRP) * gain") },
  // S108: the young light's clustering ratios, a face-on map read on the thin screen like the veil (smeared along a
  // grazing ray: the streaks of the edge-on frames), taken to 1 (the young light unclustered) toward edge-on.
  {
    anchor: "    vec3 screenClumps = youngClump > 0.5 ? clusterRatios(screenXY) : vec3(1.0);",
    apply: (a) => `${a}\n    screenClumps = illGrazeMul3(screenClumps);`,
  },
  // S106: the gas hook, on the screen's gas fluctuation map.
  {
    anchor: "    float screenGas = gasFluct > 0.5 ? layerGasMap(screenXY) : 1.0;",
    apply: (a) => a.replace("layerGasMap(screenXY)", "illGas(screenXY, layerGasMap(screenXY))"),
  },
  // S106: the depth hook, on the ring's published diffuse depth before anything multiplies it (and so before the layer's
  // own dustAv, added two lines below).
  {
    anchor: "          tau = readRing(rp.x, 0.0) * place * readRing(rp.x, 3.0).r * dustDepth;",
    apply: (a) => a.replace("tau = readRing(rp.x, 0.0) *", "tau = illDepth(readRing(rp.x, 0.0), rp) *"),
  },
];

/** The points' patches (FluxPoints' vertex shader): the layer's GLSL before dustTo, and its A_V on each segment. */
export const POINTS_PATCHES: readonly Patch[] = [
  { anchor: "  // The dust's optical depth per channel from the point to the camera (flux.ts dustToPoint, line for line).", apply: (a, glsl) => `${glsl}\n${POINTS_PLACE_GLSL}\n${a}` },
  // S108: the point placed (its grazing weight, and its lift) before anything reads it.
  { anchor: "  void main() {\n    if (wingPass > 0.5 && !wingDrawn()) {", apply: (a) => a.replace("  void main() {", "  void main() {\n    illPointsPlace();") },
  {
    anchor: "      tau += face * place * gasAt * share * column(p.y + u.y * s0, p.y + u.y * s1, h, ds) + clouds * cloudColumn;",
    // S106: the depth hook on the ring's depth (face), as the march's tau; then the layer's A_V on the segment.
    apply: (a) =>
      `${a.replace("tau += face * place", "tau += illDepth(face, vec2(r, phi)) * place")}\n` +
      "      tau += illDustAv(vec2(r, phi)) * cloudExt * column(p.y + u.y * s0, p.y + u.y * s1, h, ds);",
  },
  // S108: the points hook, on the point's light (every mode of it) at the point's own midplane place.
  {
    anchor: "    vLight = light;",
    apply: (a) =>
      "    float illPhi = atan(-position.z, position.x);\n" +
      "    light *= illPoints(vec2(length(position.xz), illPhi < 0.0 ? illPhi + 6.28318531 : illPhi));\n" +
      a,
  },
  // S106: the gas hook, on the segment's gas fluctuation map (the march's screenGas, read the same way).
  {
    anchor: "      gasAt = layerGasMap(vec2(screen.x, -screen.z));",
    apply: (a) => a.replace("layerGasMap(vec2(screen.x, -screen.z))", "illGas(vec2(screen.x, -screen.z), layerGasMap(vec2(screen.x, -screen.z)))"),
  },
];

/** How many times `anchor` occurs in `source` as written. */
export const occurrences = (source: string, anchor: string): number => source.split(anchor).length - 1;

/** A pinned shader with the patches applied; throws where an anchor is not there exactly once. */
export function patched(source: string, patches: readonly Patch[], glsl: string = illGlsl(true)): string {
  let out = source;
  for (const p of patches) {
    const n = occurrences(out, p.anchor);
    if (n !== 1) throw new Error(`illustrative patch anchor found ${n} times: ${p.anchor.trim()}`);
    out = out.replace(p.anchor, () => p.apply(p.anchor, glsl));
  }
  return out;
}

/** The illustrative march fragment: fieldFragment()'s text with the march's patches. */
export const illustrativeFragment = (fieldFragment: string): string => patched(fieldFragment, MARCH_PATCHES);
/** The illustrative points' vertex shader: FluxPoints' with the points' patches. */
export const illustrativePointsVertex = (vertex: string): string => patched(vertex, POINTS_PATCHES);

/**
 * The layer's live state (one per Galaxy view under the illustrative look): the composed GLSL, the uniform objects every
 * material shares (FieldVolume's march, every FluxPoints), and a version that moves when any value does - the march's
 * re-march key reads it.
 */
export interface IllRuntime {
  glsl: string;
  uniforms: Record<string, { value: unknown }>;
  version: number;
  /**
   * (S107, rule D1) The galaxy the values were last written for: its template and its arrays' frame. Another galaxy's
   * map is never drawn: when either moves, stepRuntime draws the empty map until the new galaxy's own planes arrive.
   */
  drawnFor?: { template: string | null; frame: IllContext["frame"] };
}

const sameValue = (a: unknown, b: unknown): boolean => {
  if (Object.is(a, b)) return true;
  if (Array.isArray(a) && Array.isArray(b)) return a.length === b.length && a.every((v, i) => Object.is(v, b[i]));
  return false;
};

const mapTexture = (data: Uint8Array, width: number, height: number): DataTexture => {
  const t = new DataTexture(data, width, height, RGBAFormat, UnsignedByteType);
  t.minFilter = LinearFilter;
  t.magFilter = LinearFilter;
  t.wrapS = ClampToEdgeWrapping;
  t.wrapT = RepeatWrapping;
  t.generateMipmaps = false;
  t.needsUpdate = true;
  return t;
};

/** The shared map before any channel has bytes: one texel of zeros. */
const EMPTY_MAP = mapTexture(new Uint8Array(4), 1, 1);

/** The shared map's composed state: the RGBA buffer, its texture, and the plane each channel was last written from. */
const shared: { buffer: Uint8Array | null; texture: DataTexture; planes: (Uint8Array | null)[] } = {
  buffer: null,
  texture: EMPTY_MAP,
  planes: [null, null, null, null],
};

/** The planes every feature's map builder hands over for these parameters and context, by channel (null: zero). */
export function illMapPlanes(ill: Readonly<Record<string, number>>, unbound: IllContext): (Uint8Array | null)[] {
  const context = illContextFor(unbound, ill);
  const planes: (Uint8Array | null)[] = [null, null, null, null];
  const owner: (string | null)[] = [null, null, null, null];
  const size = ILL_MAP.width * ILL_MAP.height;
  for (const f of FEATURES) {
    if (!f.map) continue;
    const started = illNow();
    const built = f.map.build(paramsOf(f, ill), context);
    illMeasure(`map ${f.id}`, started);
    if (built.length !== f.map.channels.length) throw new Error(`illustrative map: ${f.id} built ${built.length} planes for ${f.map.channels.length} channels`);
    f.map.channels.forEach((c, i) => {
      if (!(c >= 0 && c < 4 && Number.isInteger(c))) throw new Error(`illustrative map: ${f.id} names channel ${c}`);
      if (owner[c] !== null) throw new Error(`illustrative map: channel ${c} owned by ${owner[c]} and ${f.id}`);
      owner[c] = f.id;
      const plane = built[i];
      if (plane && plane.length !== size) throw new Error(`illustrative map: ${f.id}'s plane ${i} has ${plane.length} bytes, not ${size}`);
      planes[c] = plane ?? null;
    });
  }
  return planes;
}

/**
 * The shared map for these planes: the same texture while no plane's object changed; else the changed channels
 * written into the one RGBA buffer and a new texture over it (the old one released), so the uniform's value moves and
 * the march re-marches.
 */
export function illMapTexture(planes: readonly (Uint8Array | null)[]): DataTexture {
  const changed = [0, 1, 2, 3].filter((c) => planes[c] !== shared.planes[c]);
  if (changed.length === 0) return shared.texture;
  // S107: no plane at all is the empty map (the first frame's, and another galaxy's until its planes arrive): the
  // buffer let go, so the next planes are composed over zeros.
  if (planes.every((p) => !p) && shared.buffer) {
    if (shared.texture !== EMPTY_MAP) shared.texture.dispose();
    shared.texture = EMPTY_MAP;
    shared.buffer = null;
  }
  if (!shared.buffer) {
    if (planes.every((p) => !p)) {
      shared.planes = [...planes];
      return shared.texture;
    }
    shared.buffer = new Uint8Array(ILL_MAP.width * ILL_MAP.height * 4);
  }
  const started = illNow();
  const buf = shared.buffer;
  const n = ILL_MAP.width * ILL_MAP.height;
  for (const c of changed) {
    const plane = planes[c];
    if (plane) for (let i = 0; i < n; i++) buf[i * 4 + c] = plane[i];
    else for (let i = 0; i < n; i++) buf[i * 4 + c] = 0;
  }
  shared.planes = [...planes];
  if (shared.texture !== EMPTY_MAP) shared.texture.dispose();
  shared.texture = mapTexture(buf, ILL_MAP.width, ILL_MAP.height);
  // S107: the planes it was composed from, by channel (the sparkle names the lanes' plane it reads to the map worker).
  shared.texture.userData.illPlanes = [...planes];
  illMeasure("compose", started);
  return shared.texture;
}

/**
 * (S107) Whether channel `c` of the map `texture` holds the plane its feature builds at the parameters `context` binds
 * (illContextFor) - false while that plane is still being built (a layer that reads the channel waits for it rather
 * than read the previous one). Nothing is built.
 */
export function illChannelCurrent(texture: unknown, c: number, context: IllContext): boolean {
  const f = FEATURES.find((g) => g.map?.channels.includes(c));
  if (!f?.map) return true;
  const at = f.map.channels.indexOf(c);
  let plane: Uint8Array | null = null;
  if (wouldBuild(() => (plane = f.map!.build(context.paramsOf?.(f.id) ?? {}, context)[at] ?? null))) return false;
  const composed = (texture as { userData?: { illPlanes?: (Uint8Array | null)[] } } | null)?.userData?.illPlanes?.[c] ?? null;
  return composed === plane;
}

/** Each feature's uniform values for these parameters and this context, and the shared map (illMapTex). */
export function illUniformValues(ill: Readonly<Record<string, number>>, unbound: IllContext): Record<string, unknown> {
  const context = illContextFor(unbound, ill);
  const out: Record<string, unknown> = {};
  for (const f of FEATURES) {
    if (!f.uniforms) continue;
    const started = illNow();
    Object.assign(out, f.uniforms(paramsOf(f, ill), context));
    illMeasure(`uniforms ${f.id}`, started);
  }
  out.illMapTex = illMapTexture(illMapPlanes(ill, context));
  return out;
}

/** A runtime with every feature's uniforms at these parameters (the template's illustrative defaults without them). */
export function createRuntime(ill: Readonly<Record<string, number>> = illDefaults(null), context: IllContext = { template: null, frame: null }): IllRuntime {
  const values = illUniformValues(ill, context);
  return {
    glsl: illGlsl(),
    uniforms: Object.fromEntries(Object.entries(values).map(([k, v]) => [k, { value: v }])),
    version: 0,
    drawnFor: { template: context.template, frame: context.frame },
  };
}

/** Writes the uniforms' values for these parameters and context into the runtime; the version moves if any changed. */
export function updateRuntime(runtime: IllRuntime, ill: Readonly<Record<string, number>>, context: IllContext): void {
  let moved = false;
  for (const [k, v] of Object.entries(illUniformValues(ill, context))) {
    const u = (runtime.uniforms[k] ??= { value: v });
    if (!sameValue(u.value, v)) {
      u.value = v;
      moved = true;
    }
  }
  if (moved) runtime.version += 1;
  runtime.drawnFor = { template: context.template, frame: context.frame };
}

/**
 * One step of the map contract (S107, the sliders' stall; illMapClient.ts): the runtime brought to these parameters
 * WITHOUT building a plane on this thread where the map worker can build it. Where the runtime would build (illStale)
 * and the worker has not answered for exactly these parameters, the planes are asked of it ("asked": the runtime keeps
 * its previous map and uniforms; call again when illArrivals moves) - or, if it failed for them, nothing changes
 * ("failed"). Otherwise the runtime is updated from the features' caches ("drawn"): every channel at these parameters.
 * Without a worker (vitest, SSR, a failed worker) every step is "drawn", built here as before.
 */
export function stepRuntime(runtime: IllRuntime, ill: Readonly<Record<string, number>>, context: IllContext): "asked" | "failed" | "drawn" {
  const key = illMapKey(ill, context);
  if (!illMapAnswered(key) && illStale(ill, context)) {
    // Rule D1: the previous map is kept only on the same galaxy (a slider's move). For another galaxy - another
    // template or another frame of arrays - the empty map (the values without the arrays) is drawn while its own
    // planes are built.
    const moved = runtime.drawnFor?.template !== context.template || runtime.drawnFor?.frame !== context.frame;
    const failed = illMapFailed(key);
    if (failed || startIllMap(key, ill, context)) {
      if (moved) updateRuntime(runtime, ill, { ...context, frame: null });
      return failed ? "failed" : "asked";
    }
  }
  updateRuntime(runtime, ill, context);
  return "drawn";
}

/** How long the sliders must hold still before a plane-shaping change is built (S105 fix R1), ms. */
export const ILL_SETTLE_MS = 250;

/**
 * Whether a feature's map planes or uniforms at these parameters would build anything its memoOn caches do not hold
 * (S105 fix R1): a plane-shaping change. Nothing is built; the uniforms' own values are computed and thrown away.
 * `context` should be bound (illContextFor) to the whole parameter set `params` belongs to.
 */
export function illFeatureWouldBuild(f: IllFeature, params: IllParams, context: IllContext): boolean {
  return wouldBuild(() => {
    f.map?.build(params, context);
    f.uniforms?.(params, context);
  });
}

/**
 * The parameters to draw with now (S105 fix R1, the debounce): `live` (the sliders as they stand) for every feature
 * whose change from `settled` (the same values once they have held still) rebuilds nothing - a change that only sets
 * uniforms is drawn at once - and `settled` for a feature whose change would rebuild a plane: that one is built once,
 * when `settled` catches up. `held` names the features kept back. `live` itself while nothing is held.
 */
export function illEffective(
  live: Readonly<Record<string, number>>,
  settled: Readonly<Record<string, number>>,
  context: IllContext,
): { ill: Readonly<Record<string, number>>; held: string[] } {
  if (live === settled) return { ill: live, held: [] };
  let out: Record<string, number> | null = null;
  const held: string[] = [];
  const moved = (f: IllFeature) => {
    const lp = paramsOf(f, live);
    const sp = paramsOf(f, settled);
    return !f.controls.every((c) => Object.is(lp[c.key], sp[c.key]));
  };
  const liveContext = illContextFor(context, live);
  for (const f of FEATURES) {
    if (!moved(f)) continue;
    if (!illFeatureWouldBuild(f, paramsOf(f, live), liveContext)) continue;
    held.push(f.id);
    out ??= { ...live };
    for (const c of f.controls) out[illKey(f, c)] = paramsOf(f, settled)[c.key];
  }
  // S106 (B4): a feature reads another's live values (IllContext.paramsOf), so one whose own values did not move may
  // still rebuild from another's move that rebuilds nothing of its owner's (the lanes on the arms' skeleton while the
  // arms' own switch is off). Then every moved feature is held: one build once the sliders settle.
  const now = out ?? live;
  const nowContext = illContextFor(context, now);
  const settledContext = illContextFor(context, settled);
  const crossBuilds = FEATURES.some(
    (f) => !held.includes(f.id) && illFeatureWouldBuild(f, paramsOf(f, now), nowContext) && !illFeatureWouldBuild(f, paramsOf(f, now), settledContext),
  );
  if (crossBuilds) {
    out ??= { ...live };
    for (const f of FEATURES) {
      if (held.includes(f.id) || !moved(f)) continue;
      held.push(f.id);
      for (const c of f.controls) out[illKey(f, c)] = paramsOf(f, settled)[c.key];
    }
  }
  return { ill: out ?? live, held };
}

/** Whether the runtime still has to build for these parameters (a plane not yet made for them): the "rebuilding" mark. */
export const illStale = (ill: Readonly<Record<string, number>>, context: IllContext): boolean => {
  const started = illNow();
  const bound = illContextFor(context, ill);
  const stale = FEATURES.some((f) => (f.map || f.uniforms) && illFeatureWouldBuild(f, paramsOf(f, ill), bound));
  illMeasure("stale", started);
  return stale;
};

/**
 * Frees what the layer holds outside a runtime (S105 fix R5): the shared map's 28.8 MB buffer and its texture, and every
 * feature's cached planes and maps (memoOn). Called when the look leaves illustrative; the next runtime builds them again.
 */
export function releaseShared(): void {
  if (shared.texture !== EMPTY_MAP) shared.texture.dispose();
  shared.texture = EMPTY_MAP;
  shared.buffer = null;
  shared.planes = [null, null, null, null];
  releaseMemos();
  // S107: the map worker's caches and every answer not yet in.
  releaseIllJobs();
}

/** What the layer holds outside a runtime now (the release's test): the shared map's buffer bytes. */
export const sharedBytes = (): number => shared.buffer?.byteLength ?? 0;

/** A runtime's release (S105 fix R5): its map uniform back to the empty map, then everything shared freed. */
export function releaseRuntime(runtime: IllRuntime): void {
  if (runtime.uniforms.illMapTex) runtime.uniforms.illMapTex.value = EMPTY_MAP;
  releaseShared();
}

/** Whether a feature's drawing replaces the default knots at these parameters. */
export const knotsReplaced = (ill: Readonly<Record<string, number>>): boolean => FEATURES.some((f) => f.replacesKnots?.(paramsOf(f, ill)) ?? false);
