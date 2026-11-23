import { describe, expect, it } from "vitest";

import { fieldFragment } from "../FieldVolume";
import { FLUX_POINTS_SHADER } from "../FluxPoints";
import pinned from "../fieldFragment.s78.glsl?raw";
import {
  LOOK_STORAGE_KEY,
  TUNING_DEFAULTS,
  TUNING_STORAGE_KEY,
  changed,
  copyBoxText,
  defaultsFor,
  illustrativeDefaultsFor,
  loadLook,
  loadTuning,
  lookDefaultsFor,
  parseCombination,
  sanitize,
  saveLook,
  saveTuning,
  storageKeyFor,
} from "../tuning";
import {
  ILL_MAP,
  MARCH_PATCHES,
  POINTS_PATCHES,
  createRuntime,
  features,
  illArrays,
  illControls,
  illDefaults,
  illGlsl,
  illMapPlanes,
  illUniformValues,
  illustrativeFragment,
  illustrativePointsVertex,
  occurrences,
  registerFeature,
  updateRuntime,
} from "./index";
import type { IllFeature } from "./feature";
import { ILLUSTRATIVE_BASE } from "./preset";

function memory() {
  const store = new Map<string, string>();
  return {
    store,
    getItem: (k: string) => store.get(k) ?? null,
    setItem: (k: string, v: string) => void store.set(k, v),
    removeItem: (k: string) => void store.delete(k),
  };
}

describe("the look's storage (S105, D275)", () => {
  it("keeps the look per browser, physical by default and as the absence of the key", () => {
    const m = memory();
    expect(loadLook(m)).toBe("physical");
    saveLook("illustrative", m);
    expect(m.store.get(LOOK_STORAGE_KEY)).toBe("illustrative");
    expect(loadLook(m)).toBe("illustrative");
    saveLook("physical", m);
    expect(m.store.has(LOOK_STORAGE_KEY)).toBe(false);
    m.store.set(LOOK_STORAGE_KEY, "nonsense");
    expect(loadLook(m)).toBe("physical");
    expect(loadLook(null)).toBe("physical");
  });

  it("keeps the physical look's tuning under the key of before, the illustrative look's under its own", () => {
    expect(storageKeyFor("milky_way")).toBe(`${TUNING_STORAGE_KEY}.milky_way`);
    expect(storageKeyFor("milky_way", "physical")).toBe(`${TUNING_STORAGE_KEY}.milky_way`);
    expect(storageKeyFor("milky_way", "illustrative")).toBe(`${TUNING_STORAGE_KEY}.milky_way.illustrative`);
    const m = memory();
    const phys = { ...defaultsFor("milky_way"), fieldGain: 2 };
    saveTuning(phys, m, "milky_way");
    const ill = { ...illustrativeDefaultsFor("milky_way"), fieldGain: 3, ill: { ...illustrativeDefaultsFor("milky_way").ill, "grade.saturation": 2.5 } };
    saveTuning(ill, m, "milky_way", "illustrative");
    expect(JSON.parse(m.store.get(`${TUNING_STORAGE_KEY}.milky_way`)!)).toEqual({ fieldGain: 2 });
    expect(JSON.parse(m.store.get(`${TUNING_STORAGE_KEY}.milky_way.illustrative`)!)).toEqual({ fieldGain: 3, ill: { "grade.saturation": 2.5 } });
    expect(loadTuning(m, "milky_way").fieldGain).toBe(2);
    expect(loadTuning(m, "milky_way", "illustrative")).toEqual(ill);
    // The illustrative look never falls back to the one key of before S67.
    const old = memory();
    old.store.set(TUNING_STORAGE_KEY, JSON.stringify({ fieldGain: 0.5 }));
    expect(loadTuning(old, "milky_way").fieldGain).toBe(0.5);
    expect(loadTuning(old, "milky_way", "illustrative")).toEqual(illustrativeDefaultsFor("milky_way"));
  });

  it("lays the illustrative overlay and the preset over the template's physical defaults; the physical look's are defaultsFor's", () => {
    expect(lookDefaultsFor("milky_way", "physical")).toEqual(defaultsFor("milky_way"));
    const ill = illustrativeDefaultsFor("milky_way");
    for (const [k, v] of Object.entries(ILLUSTRATIVE_BASE.milky_way)) expect((ill as unknown as Record<string, unknown>)[k]).toBe(v);
    expect(ill.ill).toEqual(illDefaults("milky_way"));
    expect(ill.toneMapping).toBe(defaultsFor("milky_way").toneMapping);
    // the physical defaults carry the registry's plain defaults, which no physical frame reads
    expect(defaultsFor("milky_way").ill).toEqual(illDefaults(null));
  });

  it("round-trips the look and the illustrative parameters through the copy box and the paste box", () => {
    const defaults = illustrativeDefaultsFor("ngc_4414");
    const t = sanitize({ fieldGain: 1.5, ill: { "grade.saturation": 2.2, "edge.width": 3 } }, defaults);
    const box = copyBoxText(t, defaults, "ngc_4414", "rgb", 1, "illustrative");
    const parsed = JSON.parse(box);
    expect(parsed.look).toBe("illustrative");
    expect(parsed.ill).toEqual({ "grade.saturation": 2.2, "edge.width": 3 });
    const of = (look: "physical" | "illustrative") => lookDefaultsFor("ngc_4414", look);
    const back = parseCombination(box, defaultsFor("ngc_4414"), of);
    expect(back.look).toBe("illustrative");
    expect(back.tuning).toEqual(t);
    expect(back.ignored).toEqual([]);
    expect(back.rejected).toEqual([]);
    // the physical look's box is the text of before: no look, no ill
    const physical = copyBoxText(defaultsFor("ngc_4414"), defaultsFor("ngc_4414"), "ngc_4414", "rgb", 0);
    expect(physical).toBe(JSON.stringify({ template: "ngc_4414", filters: "rgb", exposure: 0 }));
    const p = parseCombination(physical, defaults, of);
    expect(p.look).toBeNull();
    expect(p.tuning).toEqual(defaultsFor("ngc_4414"));
  });

  it("clamps each illustrative value to its control and reports the unusable ones", () => {
    const t = sanitize({ ill: { "grade.saturation": 99, "edge.width": -4, "nope.x": 1, "grade.gain": "loud" } });
    expect(t.ill["grade.saturation"]).toBe(3);
    expect(t.ill["edge.width"]).toBe(0);
    expect(t.ill["grade.gain"]).toBe(TUNING_DEFAULTS.ill["grade.gain"]);
    expect("nope.x" in t.ill).toBe(false);
    const c = parseCombination(JSON.stringify({ look: "dreamy", ill: { "nope.x": 1, "grade.gain": "loud" } }));
    expect(c.look).toBeNull();
    expect(c.rejected).toEqual(["look", "ill.grade.gain"]);
    expect(c.ignored).toEqual(["ill.nope.x"]);
    expect(changed(TUNING_DEFAULTS)).toEqual({});
  });
});

describe("the registry (S105): a feature file needs no edit elsewhere", () => {
  it("lists the eight features, each control's default inside its range", () => {
    expect(features().map((f) => f.id)).toEqual(["grade", "edge", "speckle", "framing", "knots", "lanes", "arms", "floc"]);
    for (const { control } of illControls()) {
      expect(control.default).toBeGreaterThanOrEqual(control.min);
      expect(control.default).toBeLessThanOrEqual(control.max);
      for (const v of Object.values(control.perTemplate ?? {})) {
        expect(v).toBeGreaterThanOrEqual(control.min);
        expect(v).toBeLessThanOrEqual(control.max);
      }
      expect(control.about).toMatch(/Illustrative|appearance/);
    }
  });

  it("takes a fake feature's control, GLSL, hook, uniforms and arrays everywhere at once", () => {
    const fake: IllFeature = {
      id: "fake",
      label: "fake",
      about: "a test's",
      controls: [{ key: "depth", label: "fake depth", min: 0, max: 5, step: 0.1, default: 1, perTemplate: { milky_way: 2 }, about: "Illustrative." }],
      glsl: "  uniform float illFakeDepth;\n  float illFakeAv(vec2 rp) { return illFakeDepth; }\n",
      hooks: { dustAv: "illFakeAv" },
      uniforms: (p) => ({ illFakeDepth: p.depth }),
      arrays: ["arm_piece_pitch"],
    };
    const asked = illArrays();
    const drop = registerFeature(fake);
    try {
      expect(illControls().some((c) => c.key === "fake.depth")).toBe(true);
      expect(illDefaults("milky_way")["fake.depth"]).toBe(2);
      expect(illustrativeDefaultsFor("milky_way").ill["fake.depth"]).toBe(2);
      expect(sanitize({ ill: { "fake.depth": 50 } }).ill["fake.depth"]).toBe(5);
      const t = sanitize({ ill: { "fake.depth": 3 } }, illustrativeDefaultsFor("milky_way"));
      expect(changed(t, illustrativeDefaultsFor("milky_way"))).toEqual({ ill: { "fake.depth": 3 } });
      const box = copyBoxText(t, illustrativeDefaultsFor("milky_way"), "milky_way", "rgb", 0, "illustrative");
      expect(parseCombination(box, illustrativeDefaultsFor("milky_way")).tuning).toEqual(t);
      expect(illGlsl()).toContain("float illFakeAv(vec2 rp)");
      expect(illGlsl()).toContain("float illDustAv(vec2 rp) { return illLanesAv(rp) + illFlocAv(rp) + illFakeAv(rp); }");
      expect(illustrativeFragment(fieldFragment())).toContain("uniform float illFakeDepth;");
      expect(illustrativePointsVertex(FLUX_POINTS_SHADER.vertex)).toContain("uniform float illFakeDepth;");
      expect(new Set(illArrays())).toEqual(new Set([...asked, "arm_piece_pitch"]));
      const rt = createRuntime(illDefaults("milky_way"));
      expect(rt.uniforms.illFakeDepth.value).toBe(2);
      const shared = rt.uniforms.illFakeDepth;
      updateRuntime(rt, { ...illDefaults("milky_way"), "fake.depth": 4 }, { template: "milky_way", frame: null });
      expect(rt.uniforms.illFakeDepth).toBe(shared); // the same object, so every material that holds it sees the value
      expect(shared.value).toBe(4);
      expect(rt.version).toBe(1);
      updateRuntime(rt, { ...illDefaults("milky_way"), "fake.depth": 4 }, { template: "milky_way", frame: null });
      expect(rt.version).toBe(1);
    } finally {
      drop();
    }
    expect(illControls().some((c) => c.key === "fake.depth")).toBe(false);
    expect(illArrays()).toEqual(asked);
  });
});

describe("the patched shaders (S105): anchors found once, the physical sources untouched", () => {
  it("finds every march anchor exactly once in the pinned fragment, which stays byte for byte the snapshot", () => {
    const base = fieldFragment();
    expect(base).toBe(pinned);
    for (const p of MARCH_PATCHES) expect(occurrences(base, p.anchor), p.anchor).toBe(1);
    const patched = illustrativeFragment(base);
    expect(fieldFragment()).toBe(pinned); // patching is pure
    expect(patched).not.toBe(base);
    expect(patched).toContain("tau += illDustAv(rp) * cloudExt * dustDepth;");
    expect(patched).toContain("* starsGain * illYoungGain(rp);");
    expect(patched).toContain("float illE = illEdge(rp.x);");
    expect(occurrences(patched, "  void main() {")).toBe(1);
  });

  it("finds every points anchor exactly once, and FluxPoints' own vertex shader carries nothing of the layer", () => {
    const vertex = FLUX_POINTS_SHADER.vertex;
    for (const p of POINTS_PATCHES) expect(occurrences(vertex, p.anchor), p.anchor).toBe(1);
    expect(vertex).not.toMatch(/\bill[A-Z]/);
    const patched = illustrativePointsVertex(vertex);
    expect(patched).toContain("tau += illDustAv(vec2(r, phi)) * cloudExt * column(p.y + u.y * s0, p.y + u.y * s1, h, ds);");
    expect(FLUX_POINTS_SHADER.vertex).toBe(vertex);
  });

  // S105 fix: the pinned march declares 15 samplers and WebGL (ANGLE / D3D11) gives a fragment shader 16 texture units;
  // a 17th fails the march's program and the field goes undrawn under the illustrative look, with no other sign.
  const samplers = (source: string): number => {
    let n = 0;
    for (const m of source.matchAll(/\buniform\s+(?:(?:lowp|mediump|highp)\s+)?[iu]?sampler\w*\s+\w+\s*(?:\[\s*(\d+)\s*\])?\s*;/g)) n += m[1] ? Number(m[1]) : 1;
    return n;
  };

  it("keeps the march's fragment and the points' vertex shader within 16 texture units, the layer taking one", () => {
    expect(samplers(fieldFragment())).toBe(15);
    expect(samplers(illustrativeFragment(fieldFragment()))).toBeLessThanOrEqual(16);
    expect(samplers(illustrativeFragment(fieldFragment()))).toBe(samplers(fieldFragment()) + 1);
    expect(samplers(illustrativePointsVertex(FLUX_POINTS_SHADER.vertex))).toBeLessThanOrEqual(16);
    expect(samplers(illustrativePointsVertex(FLUX_POINTS_SHADER.vertex))).toBe(samplers(FLUX_POINTS_SHADER.vertex) + 1);
    expect(samplers(illGlsl())).toBe(1);
    expect(illGlsl()).toContain("uniform sampler2D illMapTex;");
  });

  it("counts a feature's own sampler in the march (the guard is real)", () => {
    const before = samplers(illustrativeFragment(fieldFragment()));
    const drop = registerFeature({
      id: "fakesampler",
      label: "fake",
      about: "a test's",
      controls: [],
      glsl: "  uniform sampler2D illFakesamplerTex;\n  float illFakesamplerAv(vec2 rp) { return textureLod(illFakesamplerTex, rp, 0.0).r; }\n",
      hooks: { dustAv: "illFakesamplerAv" },
    });
    try {
      expect(samplers(illustrativeFragment(fieldFragment()))).toBe(before + 1);
      expect(samplers(illustrativeFragment(fieldFragment()))).toBeGreaterThan(16);
      expect(samplers(illustrativePointsVertex(FLUX_POINTS_SHADER.vertex))).toBe(samplers(FLUX_POINTS_SHADER.vertex) + 2);
    } finally {
      drop();
    }
    expect(samplers(illustrativeFragment(fieldFragment()))).toBe(before);
  });

  it("composes the shared map from each feature's planes, channel by channel, re-made only when a plane changes", () => {
    const size = ILL_MAP.width * ILL_MAP.height;
    let plane: Uint8Array | null = null;
    const drop = registerFeature({
      id: "fakemap",
      label: "fake",
      about: "a test's",
      controls: [],
      map: { channels: [1], build: () => [plane] },
    });
    try {
      const ctx = { template: null, frame: null };
      const t0 = illUniformValues(illDefaults(null), ctx).illMapTex as { image: { width: number; height: number; data: Uint8Array } };
      expect(illUniformValues(illDefaults(null), ctx).illMapTex === t0).toBe(true);
      plane = new Uint8Array(size);
      plane[5] = 200;
      plane[size - 1] = 7;
      const t1 = illUniformValues(illDefaults(null), ctx).illMapTex as { image: { width: number; height: number; data: Uint8Array } };
      expect(t1 === t0).toBe(false);
      expect([t1.image.width, t1.image.height]).toEqual([ILL_MAP.width, ILL_MAP.height]);
      expect(t1.image.data[5 * 4 + 1]).toBe(200);
      expect(t1.image.data[(size - 1) * 4 + 1]).toBe(7);
      expect(t1.image.data[5 * 4 + 0]).toBe(0);
      expect(illUniformValues(illDefaults(null), ctx).illMapTex === t1).toBe(true);
      plane = null;
      const t2 = illUniformValues(illDefaults(null), ctx).illMapTex as { image: { data: Uint8Array } };
      expect(t2 === t1).toBe(false);
      expect(t2.image.data[5 * 4 + 1]).toBe(0);
      // a channel owned twice, or a plane of the wrong size, is refused
      const dup = registerFeature({ id: "fakedup", label: "fake", about: "a test's", controls: [], map: { channels: [1], build: () => [null] } });
      try {
        expect(() => illMapPlanes(illDefaults(null), ctx)).toThrow(/owned by/);
      } finally {
        dup();
      }
      plane = new Uint8Array(3);
      expect(() => illMapPlanes(illDefaults(null), ctx)).toThrow(/bytes/);
    } finally {
      drop();
    }
  });

  it("composes the neutral stubs: no A_V, a young gain of 1, the edge's taper", () => {
    const g = illGlsl();
    expect(g).toContain("float illDustAv(vec2 rp) { return illLanesAv(rp) + illFlocAv(rp); }");
    expect(g).toContain("float illYoungGain(vec2 rp) { return illEdgeYoung(rp) * illArmsYoung(rp); }");
    expect(g).toContain("float illEdge(float r) { return illEdgeTaper(r); }");
  });
});
