import { describe, expect, it } from "vitest";

import { fieldFragment } from "./FieldVolume";
import before from "./fieldFragment.s46.glsl?raw";
import { WHITE_KELVIN } from "./filters";
import { CLOSE_FIELD_FLOOR, REGIME_KPC, SUB_SAMPLES_MAX, regimeWeights } from "./regimes";
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

  it("leave the march's fragment shader as it was but for the two new uniforms", () => {
    // The snapshot is FieldVolume's FRAGMENT taken from session-46's tip before this change. With the
    // defaults the source differs only where the uniforms enter: their declarations, the sub-sample
    // clamp's bound (8.0 then, subMax = 8 now) and the dither's switch (dither = 1 takes the same hash).
    const now = fieldFragment();
    expect(fieldFragment(STEPS)).toBe(now);
    const undone = now
      .replace(/\n {2}\/\/ The most sub-samples[^\n]*\n {2}uniform float subMax;\n {2}\/\/ 1 offsets[^\n]*\n {2}uniform float dither;/, "")
      .replace("1.0, subMax));", `1.0, ${SUB_SAMPLES_MAX}.0));`)
      .replace(/dither > 0\.5 \? (fract\(sin\(dot\(gl_FragCoord\.xy, vec2\(12\.9898, 78\.233\)\)\) \* 43758\.5453\)) : 0\.5;/, "$1;");
    expect(undone).toBe(before);
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
