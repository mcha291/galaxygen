import { describe, expect, it } from "vitest";

import { fieldFragment } from "./FieldVolume";
import pinned from "./fieldFragment.d207.glsl?raw";
import { WHITE_KELVIN } from "./filters";
import { CLOSE_FIELD_FLOOR, DUST_CUTS, REGIME_KPC, SUB_SAMPLES_MAX, regimeWeights } from "./regimes";
import {
  BLOOM,
  MAX_RESOLUTION,
  PIXEL_BUDGET,
  STAR_SPRITE_PX,
  STEPS,
  TUNING_CONTROLS,
  TUNING_DEFAULTS,
  TUNING_STORAGE_KEY,
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
      cloudIntensity: 1,
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
    // to the march is a change to this file, made knowingly. The panel's values are uniforms, not source.
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
    expect(now).toContain(`for (int m = 0; m <= ${DUST_CUTS.length}; m++)`);
    DUST_CUTS.forEach((c) => expect(now).toContain(`return ${c.toFixed(2)};`));
    // D207: the dust's placement multiplies its depth, its thermal light and the diagnostic, not the scattered light.
    expect(now).toContain("float place = scattered.a;");
    expect(now).toMatch(/tau = readRing\(rp\.x, \d\.0\) \* place \* dustDepth;/);
    expect(now).toMatch(/\(scattered\.rgb \* scattering \+ readRing\(rp\.x, \d\.0\) \* place\) \* dustGain \+ dustWhere \* level \* whereTint\(level\) \* place;/);
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
    expect(group.filter((c) => c.switch).map((c) => c.key).sort()).toEqual(["compCells", "compClouds", "compDust", "compGas", "compPoints", "compStars", "dustReading"]);
    for (const c of group.filter((c) => !c.switch)) expect(c).toMatchObject({ kind: "range", min: 0.25, max: 4, log: true });
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
