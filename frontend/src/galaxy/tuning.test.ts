import { describe, expect, it } from "vitest";

import { fieldFragment } from "./FieldVolume";
import { NOISE_GLSL } from "./noise.glsl";
import pinned from "./fieldFragment.s66.glsl?raw";
import { WHITE_KELVIN } from "./filters";
import { CLOSE_FIELD_FLOOR, DUST_CUTS, REGIME_KPC, SLAB_PIECES, SUB_SAMPLES_MAX, regimeWeights } from "./regimes";
import {
  BLOOM,
  MAX_RESOLUTION,
  PIXEL_BUDGET,
  STAR_SPRITE_PX,
  STEPS,
  TUNING_CONTROLS,
  TUNING_DEFAULTS,
  TEMPLATE_EXPOSURE,
  TEMPLATE_TUNING,
  TUNING_STORAGE_KEY,
  type Tuning,
  defaultsFor,
  exposureFor,
  storageKeyFor,
  changed,
  loadTuning,
  positionOf,
  sanitize,
  saveTuning,
  valueAt,
  type RangeControl,
} from "./tuning";

function memory() {
  const store = new Map<string, string>();
  return {
    store,
    getItem: (k: string) => store.get(k) ?? null,
    setItem: (k: string, v: string) => void store.set(k, v),
    removeItem: (k: string) => void store.delete(k),
  };
}

describe("tuning defaults (D199)", () => {
  it("are the values the view drew with before the panel", () => {
    expect(STEPS).toBe(96);
    expect(PIXEL_BUDGET).toBe(400_000);
    expect(MAX_RESOLUTION).toBe(0.5);
    expect(BLOOM).toEqual({ strength: 0.35, radius: 0.45, threshold: 1.0 });
    expect(STAR_SPRITE_PX).toBe(9);
    expect(CLOSE_FIELD_FLOOR).toBe(0.03);
    expect(TUNING_DEFAULTS).toEqual({
      resolution: MAX_RESOLUTION,
      pixelBudget: PIXEL_BUDGET,
      steps: STEPS,
      subMax: SUB_SAMPLES_MAX,
      dither: true,
      filtering: "linear",
      fieldGain: 1,
      fieldFloor: CLOSE_FIELD_FLOOR,
      whiteKelvin: WHITE_KELVIN,
      bloomStrength: BLOOM.strength,
      bloomRadius: BLOOM.radius,
      bloomThreshold: BLOOM.threshold,
      toneMapping: "agx",
      spriteSize: STAR_SPRITE_PX,
      pointGain: 1,
      // S67 (D227 R3): the owner's spike switch, off until their tuning sets it (off: the obscured Airy).
      spikes: false,
      compPoints: true,
      compStars: true,
      compGas: true,
      compDust: true,
      dustReading: "acts",
      compClouds: false,
      compCells: false,
      starsIntensity: 1,
      gasIntensity: 1,
      dustIntensity: 1,
      extinctionStrength: 1, // S67, D228: the model's extinction, the owner's ruling's default
      cloudIntensity: 1,
      ageYoung: true,
      ageMiddle: true,
      ageOld: true,
      // S64 (V6): the clouds as extinction, on; the raster at the finest 16 MiB holds on the render grid.
      cloudsExtinction: true,
      cloudRaster: 5,
      cloudElongation: 1, // S67, D230: the gas field's own shear (R2, the owner's choice)
      // S64 (V6): the HII regions as knots and the clusters with their radius, both on.
      knots: true,
      clusterRadius: true,
      // S66 (V7, D226 R3-R5): the randomness layer in the march, each on (drawn only with the layer on).
      gasInMarch: true,
      spursInMarch: true,
      clumpsInMarch: true,
    });
    expect(WHITE_KELVIN).toBe(6500);
  });

  it("has one control per value, each default inside its range", () => {
    expect(TUNING_CONTROLS.map((c) => c.key).sort()).toEqual(Object.keys(TUNING_DEFAULTS).sort());
    for (const c of TUNING_CONTROLS) {
      expect(c.about).toMatch(/display/);
      if (c.kind === "range") {
        const v = TUNING_DEFAULTS[c.key] as number;
        expect(v).toBeGreaterThanOrEqual(c.min);
        expect(v).toBeLessThanOrEqual(c.max);
      }
    }
  });

  it("leave the march's fragment shader the one D206 and D207 ruled, with the default steps", () => {
    // The snapshot is FieldVolume's fragment as D206 and D207 (S50) left it (D207 added the dust's placement). Until then this test undid S47's and
    // S50's declared uniforms one replacement at a time and compared the rest with session-46's source, which
    // proved those two rows changed no picture. D206 changes the march on purpose (the dust in its own layer,
    // each sub-step composed in order), so the comparison ends there and the source is pinned whole: a change
    // to the march is a change to this file, made knowingly. The panel's values are uniforms, not source. S64 (V6)
    // re-pinned it on purpose: the diffuse depth times the ring's diffuse share, each raster texel's clouds a slab at
    // their own heights in the step, the pieces cut at the dust's cuts and the slab's parts (fieldFragment.s64.glsl; D207's snapshot is in git);
    // and again for the knots' undrawn share (S64, R5): the HII light times each level-0 cell's 1 - D_c / K_c. S66 (V7,
    // D226 R3-R5, R9) re-pinned it on purpose (fieldFragment.s66.glsl; S64's is in git): the randomness layer's include
    // (noise.glsl.ts), each map read once per ray as a thin screen at the ray's midplane crossing (D226 as amended)
    // and its value multiplying each sub-step - the gas map times the placement, the spurs from their
    // table, the young and kept light times the clustering maps over their cell means - each behind a uniform that is 0
    // under "physics only", so that the S64 statements run unchanged there.
    const now = fieldFragment();
    expect(fieldFragment(STEPS)).toBe(now);
    expect(now.replace(/\r\n/g, "\n")).toBe(pinned.replace(/\r\n/g, "\n"));
    // What the tuning panel and the component switches reach are uniforms, and at the field's defaults each is
    // the identity: the sub-samples' cap, the dither, the layers' multipliers and the dust's depth switch.
    for (const name of ["subMax", "dither", "starsGain", "gasGain", "dustGain", "dustDepth", "dustWhere"]) {
      expect(now).toContain(`uniform float ${name};`);
    }
    expect(now).toContain(`1.0, subMax));`);
    expect(SUB_SAMPLES_MAX).toBe(8);
    // D206: the dust's height is read per ring, never a uniform, and the cuts are regimes.ts's.
    expect(now).not.toContain("uniform float dustHeight");
    expect(now).toContain(`for (int m = 0; m <= ${DUST_CUTS.length + SLAB_PIECES + 1}; m++)`);
    DUST_CUTS.forEach((c) => expect(now).toContain(`return ${c.toFixed(2)};`));
    // D207: the dust's placement multiplies its depth, its thermal light and the diagnostic, not the scattered light.
    expect(now).toContain("float place = scattered.a;");
    expect(now).toMatch(/tau = readRing\(rp\.x, \d\.0\) \* place \* readRing\(rp\.x, \d\.0\)\.r \* dustDepth;/);
    // S64: the clouds' layer, its uniforms and its own column in each piece.
    for (const name of ["cloudsOn"]) expect(now).toContain(`uniform float ${name};`);
    expect(now).toContain("vec3 depth = tau * cDust + (clouds ? tauC * slabColumn(a, b, lo, hi, piece) : vec3(0.0));");
    expect(now).toContain("uniform sampler2D cloudSlab;");
    // S64 (V6, R5): the knots' undrawn share multiplies the field's HII light, cell by cell, and nothing else.
    expect(now).toContain("hiiLight = readPolar(hii, rp).rgb * (1.0 - hiiFade * inRegion(rp)) * gasGain * knotShare(rp);");
    expect(now.match(/knotShare\(rp\)/g)).toHaveLength(1);
    expect(now).toContain("if (shareOn < 0.5 || rp.x < shareCells.x || rp.x >= shareCells.y) return 1.0;");
    expect(now).toMatch(/\(scattered\.rgb \* scattering \+ readRing\(rp\.x, \d\.0\) \* place\) \* dustGain \+ dustWhere \* level \* whereTint\(level\) \* place;/);
    // S66 (V7): the include is in the march; each modulation is one statement behind its uniform, at the read point.
    expect(now).toContain(NOISE_GLSL);
    for (const name of ["gasFluct", "spursOn", "youngClump"]) expect(now).toContain(`uniform float ${name};`);
    // As amended on builder B's capture: the maps are a thin screen at the ray's midplane crossing, read once per ray.
    expect(now).toContain("vec2 rp = polarOf(readPoint(q0, q1, jitter));");
    expect(now).toContain("float tCross = abs(dir.y) > 1e-6 ? -origin.y / dir.y : -1.0;");
    expect(now).toContain("float screenGas = gasFluct > 0.5 ? layerGasMap(screenXY) : 1.0;");
    expect(now).toContain("if (gasFluct > 0.5) place *= screenGas;");
    expect(now).toContain("if (spursOn > 0.5) place = (1.0 - readSpurShare(rp.x)) * readPolar(hii, rp).a + screenSpurs;");
    expect(now).toContain("if (youngClump > 0.5) starsLight += clumpedLight(screenClumps, rp) * starsGain;");
    expect(now.match(/layerGasMap\(/g)).toHaveLength(2); // its definition and the one call, before the step loop
    expect(now.indexOf("layerGasMap(screenXY)")).toBeLessThan(now.indexOf(`for (int k = 0; k < ${STEPS}; k++)`));
    expect(fieldFragment(128)).toContain("k < 128; k++");
    expect(fieldFragment(128)).toContain("1.0 / float(128)");
  });

  it("leave the field's weight at every zoom bit for bit the S40 formula", () => {
    const ramp = (x: number, from: number, to: number) => Math.min(1, Math.max(0, (Math.log(from) - Math.log(x)) / (Math.log(from) - Math.log(to))));
    for (const across of [100, 40, 25, 12, 4, 3, 2, 1, 0.5]) {
      const stars = ramp(across, REGIME_KPC.stars, REGIME_KPC.stars / 2);
      const old = 1 - 0.7 * ramp(across, REGIME_KPC.field, REGIME_KPC.stars) - 0.27 * stars;
      expect(regimeWeights(across).field).toBe(old);
      expect(regimeWeights(across, TUNING_DEFAULTS.fieldFloor).field).toBe(old);
    }
    expect(regimeWeights(0.5, 0.2).field).toBeCloseTo(0.2, 12);
    expect(regimeWeights(0.5, 0).field).toBeCloseTo(0, 12);
    expect(regimeWeights(100, 0.2).field).toBe(1);
  });
});

describe("tuning storage", () => {
  it("round-trips, storing only what changed", () => {
    const s = memory();
    const t = { ...TUNING_DEFAULTS, steps: 128, dither: false, toneMapping: "aces" as const, fieldGain: 2 };
    saveTuning(t, s);
    expect(JSON.parse(s.store.get(TUNING_STORAGE_KEY)!)).toEqual({ steps: 128, dither: false, fieldGain: 2, toneMapping: "aces" });
    expect(loadTuning(s)).toEqual(t);
    saveTuning({ ...TUNING_DEFAULTS }, s);
    expect(s.store.has(TUNING_STORAGE_KEY)).toBe(false);
  });

  it("clamps numbers, drops unknown keys and bad values", () => {
    const t = sanitize({ steps: 1000, subMax: 0, resolution: "x", fieldGain: -3, toneMapping: "sepia", dither: "yes", whiteKelvin: 6512.4, bogus: 1 });
    expect(t.steps).toBe(256);
    expect(t.subMax).toBe(1);
    expect(t.resolution).toBe(TUNING_DEFAULTS.resolution);
    expect(t.fieldGain).toBe(0.25);
    expect(t.toneMapping).toBe("agx");
    expect(t.dither).toBe(true);
    expect(t.whiteKelvin).toBe(6512);
    expect("bogus" in t).toBe(false);
  });

  it("works without storage, and with broken storage", () => {
    expect(loadTuning(null)).toEqual(TUNING_DEFAULTS);
    const broken = {
      getItem: () => {
        throw new Error("blocked");
      },
      setItem: () => {
        throw new Error("blocked");
      },
      removeItem: () => {
        throw new Error("blocked");
      },
    };
    expect(loadTuning(broken)).toEqual(TUNING_DEFAULTS);
    expect(() => saveTuning({ ...TUNING_DEFAULTS, steps: 64 }, broken)).not.toThrow();
    expect(loadTuning({ getItem: () => "{not json" })).toEqual(TUNING_DEFAULTS);
  });

  it("changed is empty at the defaults", () => {
    expect(changed({ ...TUNING_DEFAULTS })).toEqual({});
    expect(changed({ ...TUNING_DEFAULTS, bloomStrength: 0.5 })).toEqual({ bloomStrength: 0.5 });
  });
});

describe("the display defaults per template (S67, D227 R4; T1)", () => {
  // A map as the owner's paste would fill it: the Milky Way's bloom and points, NGC 4414's spikes and steps.
  const MAP = { milky_way: { bloomStrength: 0.5, pointGain: 2 }, ngc_4414: { spikes: true, steps: 1000, bogus: 1 } as Partial<Tuning> };
  const EXPOSURE = { ngc_4414: 1.5 };

  // The third paste (2026-10-19): was one set for both - NGC 4414 gains its own values, and both march 48 steps (was 96).
  it("carry the owner's pastes for both templates (2026-10-18, 2026-10-19 copied to NGC 4414, then the third: NGC 4414's own, steps 48)", () => {
    expect(Object.keys(TEMPLATE_TUNING)).toEqual(["milky_way", "ngc_4414"]);
    expect(TEMPLATE_EXPOSURE).toEqual({});
    const owner = {
      ...TUNING_DEFAULTS, resolution: 1, pixelBudget: 2_000_000, steps: 48, fieldGain: 1.65, fieldFloor: 0.1, bloomStrength: 2.25,
      bloomRadius: 0.35, bloomThreshold: 0.45, toneMapping: "aces", spriteSize: 3, pointGain: 4, compCells: true,
      starsIntensity: 0.55, gasIntensity: 1, dustIntensity: 1, extinctionStrength: 1.25, cloudsExtinction: false,
    };
    expect(defaultsFor("milky_way")).toEqual({ ...owner, steps: 96 }); // the owner: "Put the Milky Way back to 96 steps"
    expect(defaultsFor("ngc_4414")).toEqual({
      ...owner, fieldGain: 1.2, bloomStrength: 2, spikes: true, cloudsExtinction: true, cloudRaster: 3,
    });
    // Against the plain defaults the paste's five values are among what differs (the copy box's own reading).
    expect(changed(defaultsFor("ngc_4414"))).toMatchObject({ fieldGain: 1.2, bloomStrength: 2, spikes: true, cloudRaster: 3, steps: 48 });
    expect(defaultsFor(null)).toEqual(TUNING_DEFAULTS);
    for (const name of ["milky_way", "ngc_4414", null]) expect(exposureFor(name)).toBe(0);
  });

  it("lay a template's own over TUNING_DEFAULTS, made valid; another template and none keep the plain ones", () => {
    expect(defaultsFor("milky_way", MAP)).toEqual({ ...TUNING_DEFAULTS, bloomStrength: 0.5, pointGain: 2 });
    // Clamped and cleaned as stored choices are: steps to its range, an unknown key dropped.
    expect(defaultsFor("ngc_4414", MAP)).toEqual({ ...TUNING_DEFAULTS, spikes: true, steps: 256 });
    expect(defaultsFor("andromeda", MAP)).toEqual(TUNING_DEFAULTS);
    expect(defaultsFor(null, MAP)).toEqual(TUNING_DEFAULTS);
    expect(exposureFor("ngc_4414", EXPOSURE)).toBe(1.5);
    expect(exposureFor("milky_way", EXPOSURE)).toBe(0);
    expect(exposureFor("ngc_4414", { ngc_4414: Number.NaN })).toBe(0);
  });

  it("compare and reset against the template's defaults: changed() is what differs from them", () => {
    const own = defaultsFor("milky_way", MAP);
    expect(changed(own, own)).toEqual({});
    expect(changed({ ...own, bloomStrength: 0.35 }, own)).toEqual({ bloomStrength: 0.35 }); // back at today's is a change here
    expect(changed(own)).toEqual({ bloomStrength: 0.5, pointGain: 2 }); // against the plain defaults: the template's own
  });

  it("keep each template's choices under its own key, and the one key of before for no template", () => {
    expect(storageKeyFor("m31")).toBe(`${TUNING_STORAGE_KEY}.m31`);
    expect(storageKeyFor(null)).toBe(TUNING_STORAGE_KEY);
    const s = memory();
    saveTuning({ ...TUNING_DEFAULTS, steps: 128 }, s, "m31");
    saveTuning({ ...TUNING_DEFAULTS, dither: false }, s, "m33");
    expect(JSON.parse(s.store.get(`${TUNING_STORAGE_KEY}.m31`)!)).toEqual({ steps: 128 });
    expect(JSON.parse(s.store.get(`${TUNING_STORAGE_KEY}.m33`)!)).toEqual({ dither: false });
    expect(s.store.has(TUNING_STORAGE_KEY)).toBe(false);
    expect(loadTuning(s, "m31")).toEqual({ ...TUNING_DEFAULTS, steps: 128 });
    expect(loadTuning(s, "m33")).toEqual({ ...TUNING_DEFAULTS, dither: false });
    expect(loadTuning(s, "andromeda")).toEqual(TUNING_DEFAULTS);
    // At the defaults a template's key is kept, empty, so the old key is not read for it again (the fallback below).
    saveTuning({ ...TUNING_DEFAULTS }, s, "m31");
    expect(s.store.get(`${TUNING_STORAGE_KEY}.m31`)).toBe("{}");
  });

  it("falls back to the old key for a template with no key of its own, read and never written back (the lead's second pass)", () => {
    const s = memory();
    // The owner's live tuning, stored before S67 under the one key.
    s.store.set(TUNING_STORAGE_KEY, JSON.stringify({ bloomStrength: 0.6, spikes: true }));
    expect(loadTuning(s, "m31")).toEqual({ ...TUNING_DEFAULTS, bloomStrength: 0.6, spikes: true });
    expect(loadTuning(s, "m33")).toEqual({ ...TUNING_DEFAULTS, bloomStrength: 0.6, spikes: true });
    // A save writes the template's own key; the old key is untouched, and from then on the template's own wins.
    saveTuning({ ...TUNING_DEFAULTS, bloomStrength: 0.7 }, s, "m31");
    expect(JSON.parse(s.store.get(TUNING_STORAGE_KEY)!)).toEqual({ bloomStrength: 0.6, spikes: true });
    expect(loadTuning(s, "m31")).toEqual({ ...TUNING_DEFAULTS, bloomStrength: 0.7 });
    // Saved back at the defaults, the template's key stays (empty) and the old key's values do not return.
    saveTuning({ ...TUNING_DEFAULTS }, s, "m31");
    expect(loadTuning(s, "m31")).toEqual(TUNING_DEFAULTS);
    expect(loadTuning(s, "m33")).toEqual({ ...TUNING_DEFAULTS, bloomStrength: 0.6, spikes: true });
    // Over a template's own defaults, the old key's values are laid as any stored choices are.
    expect(loadTuning(s, null)).toEqual({ ...TUNING_DEFAULTS, bloomStrength: 0.6, spikes: true });
  });

  it("has the star-first picture's four on by default and the diagnostics off, nothing stored, and keeps a switched one (D205, D208)", () => {
    // The picture is the points over the field's remainder, its gas and its dust (D208); until then every layer
    // was off (D205). The cloud markers and the cell outlines are diagnostics and stay off.
    for (const key of ["compPoints", "compStars", "compGas", "compDust"] as const) expect(TUNING_DEFAULTS[key]).toBe(true);
    for (const key of ["compClouds", "compCells"] as const) expect(TUNING_DEFAULTS[key]).toBe(false);
    expect(changed({ ...TUNING_DEFAULTS, compPoints: false })).toEqual({ compPoints: false });
    expect(sanitize({ compPoints: false }).compPoints).toBe(false);
    expect(sanitize({ compPoints: "no" }).compPoints).toBe(true);
    expect(TUNING_DEFAULTS.dustReading).toBe("acts");
    for (const key of ["starsIntensity", "gasIntensity", "dustIntensity", "cloudIntensity"] as const) expect(TUNING_DEFAULTS[key]).toBe(1);
    const s = memory();
    saveTuning({ ...TUNING_DEFAULTS }, s);
    expect(s.store.has(TUNING_STORAGE_KEY)).toBe(false);
    const t = { ...TUNING_DEFAULTS, compDust: false, dustReading: "where" as const, cloudIntensity: 2 };
    expect(changed(t)).toEqual({ compDust: false, dustReading: "where", cloudIntensity: 2 });
    saveTuning(t, s);
    expect(loadTuning(s)).toEqual(t);
    expect(sanitize({ dustReading: "glow", compClouds: 1, gasIntensity: 9 })).toMatchObject({ dustReading: "acts", compClouds: false, gasIntensity: 4 });
    // The switches live in the brightest mode's Components section; the panel's Components group shows the intensities.
    const group = TUNING_CONTROLS.filter((c) => c.group === "Components");
    expect(group.filter((c) => c.switch).map((c) => c.key).sort()).toEqual(["ageMiddle", "ageOld", "ageYoung", "cloudsExtinction", "clusterRadius", "compCells", "compClouds", "compDust", "compGas", "compPoints", "compStars", "dustReading", "knots"]);
    // ...and, since S67 (D228, the owner's ruling), the extinction strength: linear from 0 to 2, at 1 the model's.
    for (const c of group.filter((c) => !c.switch && c.key !== "extinctionStrength")) expect(c).toMatchObject({ kind: "range", min: 0.25, max: 4, log: true });
    const strength = group.find((c) => c.key === "extinctionStrength")!;
    expect(strength).toMatchObject({ kind: "range", min: 0, max: 2, step: 0.01 });
    expect((strength as { log?: boolean }).log).toBeFalsy();
    expect(strength.about).toContain("by the owner's ruling of 2026-10-18");
  });
});

describe("log sliders", () => {
  it("land on the default at its position and stay inside the range", () => {
    for (const c of TUNING_CONTROLS.filter((c): c is RangeControl => c.kind === "range" && Boolean(c.log))) {
      const v = TUNING_DEFAULTS[c.key] as number;
      expect(valueAt(c, positionOf(c, v)) / v).toBeCloseTo(1, 2);
      expect(valueAt(c, 0)).toBe(c.min);
      expect(valueAt(c, 1000)).toBe(c.max);
    }
  });
});
