import { describe, expect, it } from "vitest";

import { fieldFragment } from "./FieldVolume";
import { NOISE_GLSL } from "./noise.glsl";
import pinned from "./fieldFragment.s78.glsl?raw";
import { beginLanding, endSwap, loads, swapState } from "../useLoad";
import { WHITE_KELVIN } from "./filters";
import { CLOSE_FIELD_FLOOR, DUST_CUTS, REGIME_KPC, SLAB_PIECES, SUB_SAMPLES_MAX, regimeWeights } from "./regimes";
import {
  BLOOM,
  MAX_RESOLUTION,
  MOVING_SETTLE_MS,
  PIXEL_BUDGET,
  STAR_SPRITE_PX,
  STEPS,
  SUB_SAMPLES_MOVING,
  TUNING_CONTROLS,
  TUNING_DEFAULTS,
  TEMPLATE_EXPOSURE,
  TEMPLATE_TUNING,
  TUNING_STORAGE_KEY,
  LOAD_TUNING_KEYS,
  drawnTuning,
  heldTemplate,
  type Tuning,
  defaultsFor,
  exposureFor,
  storageKeyFor,
  changed,
  loadTuning,
  marchSubSamples,
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
      // S81 (T14): the cut while the camera moves - at rest the full cap, so the defaults draw every still frame as before.
      subMoving: SUB_SAMPLES_MOVING,
      settleMs: MOVING_SETTLE_MS,
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
      knotsIntensity: 1, // S97: the knots' drawn light at the closure's
      clusterRadius: true,
      regionStars: "catalogue", // S82 (#172, the owner's ruling): the region regime draws the catalogue's points
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
    // under "physics only", so that the S64 statements run unchanged there. S78 (T29, the program's compile time)
    // re-pinned it on purpose (fieldFragment.s78.glsl; S66's is in git): the loop bounds made dynamic so that Direct3D's
    // compiler does not unroll them (ANGLE marks no loop [loop]; the 96-step program took 6.8 s to build, 1 s since) - the
    // step loop runs to the uniform steps and the sub-samples' loop to n itself - and the steps' exponent the uniform
    // invSteps, 1 / steps as a float, the value the constant 1.0 / float(96) was folded to: the arithmetic unchanged, the
    // same operations in the same order, and one program for every step count.
    const now = fieldFragment();
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
    expect(now.indexOf("layerGasMap(screenXY)")).toBeLessThan(now.indexOf("for (int k = 0; k < steps; k++)"));
    // S78 (T29): the steps are uniforms, and no loop of the march is bounded by a constant it then breaks out of.
    for (const name of ["int steps", "float invSteps"]) expect(now).toContain(`uniform ${name};`);
    expect(now).toContain("float ratio = pow(max(tFar, tStart * 1.0001) / tStart, invSteps);");
    expect(now).toContain("for (int j = 0; j < n; j++) {");
    expect(now).not.toContain("if (j >= n) break;");
    expect(now).not.toContain(`k < ${STEPS}; k++`);
    // The reciprocal three uploads (a float) is the float the constant 1.0 / float(steps) was folded to, at the counts the
    // templates open on: 0.010416667 at 96, 0.020833334 at 48 (ANGLE's literals in the translated shader).
    expect(Math.fround(1 / 96)).toBe(Math.fround(0.010416667));
    expect(Math.fround(1 / 48)).toBe(Math.fround(0.020833334));
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
    // the owner: "Put the Milky Way back to 96 steps"; S71 (F-4-1, the owner's word of 2026-10-27): was cloudsExtinction
    // false (the paste's) - the Milky Way draws its clouds as extinction, so the 0.492 of its dust the clouds hold is drawn.
    expect(defaultsFor("milky_way")).toEqual({ ...owner, steps: 96, cloudsExtinction: true });
    expect(defaultsFor("milky_way").cloudsExtinction).toBe(true);
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
    expect(group.filter((c) => c.switch).map((c) => c.key).sort()).toEqual(["ageMiddle", "ageOld", "ageYoung", "cloudsExtinction", "clusterRadius", "compCells", "compClouds", "compDust", "compGas", "compPoints", "compStars", "dustReading", "knots", "regionStars"]);
    // ...and, since S67 (D228, the owner's ruling), the extinction strength: linear from 0 to 2, at 1 the model's.
    // S97: the knots' intensity reaches lower (0.05) to judge the knots under the owner's bloom.
    for (const c of group.filter((c) => !c.switch && c.key !== "extinctionStrength" && c.key !== "knotsIntensity")) expect(c).toMatchObject({ kind: "range", min: 0.25, max: 4, log: true });
    expect(group.find((c) => c.key === "knotsIntensity")).toMatchObject({ kind: "range", min: 0.05, max: 4, log: true });
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

describe("the march's cut while the camera moves (S81, T14)", () => {
  it("is the full cap at rest, whatever the moving choices: a still frame is the frame without the cut", () => {
    for (const subMax of [1, 3, 8, 8.4, 0, 99]) {
      const full = Math.min(SUB_SAMPLES_MAX, Math.max(1, Math.round(subMax))); // the uniform as the frame loop set it before S81
      for (const subMoving of [1, 2, 8]) {
        for (const settleMs of [0, 200, 1000]) {
          expect(marchSubSamples(subMax, subMoving, settleMs, settleMs)).toEqual({ sub: full, full, moving: false });
          expect(marchSubSamples(subMax, subMoving, settleMs, Infinity)).toEqual({ sub: full, full, moving: false });
        }
      }
    }
  });

  it("lowers the cap to the moving count within the settle, never above the full cap, and never with a settle of 0", () => {
    expect(marchSubSamples(8, 2, 200, 0)).toEqual({ sub: 2, full: 8, moving: true });
    expect(marchSubSamples(8, 2, 200, 199.9)).toEqual({ sub: 2, full: 8, moving: true });
    expect(marchSubSamples(8, 2, 200, 200)).toEqual({ sub: 8, full: 8, moving: false });
    expect(marchSubSamples(3, 6, 200, 10).sub).toBe(3);
    expect(marchSubSamples(8, 0, 200, 10).sub).toBe(1);
    expect(marchSubSamples(8, 2, 0, 0)).toEqual({ sub: 8, full: 8, moving: false });
  });

  it("is two panel controls in the March group, stored as the panel's other values are", () => {
    const moving = TUNING_CONTROLS.find((c) => c.key === "subMoving") as RangeControl;
    const settle = TUNING_CONTROLS.find((c) => c.key === "settleMs") as RangeControl;
    expect([moving.group, moving.min, moving.max, moving.integer]).toEqual(["March", 1, SUB_SAMPLES_MAX, true]);
    expect([settle.group, settle.min, settle.max, settle.unit]).toEqual(["March", 0, 1000, "ms"]);
    expect(sanitize({ subMoving: 12, settleMs: -5 })).toMatchObject({ subMoving: SUB_SAMPLES_MAX, settleMs: 0 });
    const kept = new Map<string, string>();
    const storage = { getItem: (k: string) => kept.get(k) ?? null, setItem: (k: string, v: string) => void kept.set(k, v), removeItem: (k: string) => void kept.delete(k) };
    saveTuning({ ...defaultsFor("milky_way"), subMoving: 4, settleMs: 350 }, storage, "milky_way");
    expect(loadTuning(storage, "milky_way")).toMatchObject({ subMoving: 4, settleMs: 350 });
    expect(JSON.parse(kept.get(storageKeyFor("milky_way"))!)).toEqual({ subMoving: 4, settleMs: 350 });
  });
});

// S82 (#188's follow-up): during a landing's hold the previous picture is drawn with its own template's display tuning,
// while every value that keys a load is the new template's, so the landing's loads go out as without the hold; after the
// swap's publish both are the new template's. Driven as GalaxyTab drives it: App's drawn camera stays the previous
// landing's while the store's swap is a landing's (heldTemplate), and the picture is drawn with drawnTuning.
describe("the tuning a landing's hold draws with (S82, #188)", () => {
  // The Milky Way on screen, NGC 4414 landed on; each template's stored choices differ in a load key too.
  const milkyWay = { ...defaultsFor("milky_way"), whiteKelvin: 5800, knots: false };
  const ngc = { ...defaultsFor("ngc_4414"), whiteKelvin: 7200, knots: true };
  const DISPLAY = Object.keys(TUNING_DEFAULTS).filter((k) => !(LOAD_TUNING_KEYS as readonly string[]).includes(k)) as (keyof Tuning)[];

  it("keeps the drawn template's look and the new template's load keys until the swap publishes", () => {
    // The two templates' display defaults differ where the owner set them (TEMPLATE_TUNING): the hold must show it.
    for (const k of ["fieldGain", "bloomStrength", "steps", "spikes", "cloudRaster"] as const) expect(milkyWay[k]).not.toEqual(ngc[k]);
    const stars = {};
    beginLanding(true); // NGC 4414 chosen over the Milky Way on screen
    loads.wait(stars);
    expect(swapState().landing).toBe(true);
    // App's drawn camera: the previous landing's (selection 1, the Milky Way) while the landing's swap is on.
    const drawn = swapState().landing ? { selection: 1, name: "milky_way" } : { selection: 2, name: "ngc_4414" };
    const held = heldTemplate(drawn, { selection: 2, name: "ngc_4414" });
    expect(held).toBe("milky_way");
    const look = drawnTuning(ngc, held === "milky_way" ? milkyWay : null);
    for (const k of DISPLAY) expect(look[k], `${k}: the drawn template's`).toEqual(milkyWay[k]);
    for (const k of LOAD_TUNING_KEYS) expect(look[k], `${k}: the new template's`).toEqual(ngc[k]);
    expect(look.whiteKelvin).toBe(7200); // the render, the blackbody, the clusters and the tiles asked at NGC 4414's white
    // The swap publishes: the camera is the landing's own, nothing is held, everything is the new template's.
    loads.answer(stars, () => undefined);
    expect(swapState().swapping).toBe(false);
    const after = swapState().landing ? { selection: 1, name: "milky_way" } : { selection: 2, name: "ngc_4414" };
    expect(heldTemplate(after, { selection: 2, name: "ngc_4414" })).toBeNull();
    expect(drawnTuning(ngc, null)).toBe(ngc); // the live tuning itself
    endSwap();
  });

  it("holds nothing outside a landing or for the same template chosen again", () => {
    expect(heldTemplate({ selection: 3, name: "milky_way" }, { selection: 3, name: "milky_way" })).toBeNull();
    expect(heldTemplate({ selection: 3, name: "milky_way" }, { selection: 4, name: "milky_way" })).toBeNull();
  });

  it("names as load keys exactly the values a request's key or a loader's mounting reads", () => {
    expect([...LOAD_TUNING_KEYS].sort()).toEqual(
      ["cloudsExtinction", "compClouds", "compDust", "compGas", "compPoints", "compStars", "fieldFloor", "knots", "regionStars", "whiteKelvin"],
    );
    for (const k of LOAD_TUNING_KEYS) expect(k in TUNING_DEFAULTS).toBe(true);
  });
});
