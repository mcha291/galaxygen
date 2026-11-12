// S97 (lane V, build 1): the knots' intensity - a display balance on the HII knots' drawn light and nothing else. At 1
// every frame draws as before (the knots' gain is today's product to the bit), so the closure (ii) of
// tests/test_v6_knots.py holds; at k the knots' light is k times it. Not a key that changes what is loaded.
import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import { LIGHT_PER_LSUN_PC2 } from "./FieldVolume";
import { knotsGain } from "./knots";
import { LOAD_TUNING_KEYS, TUNING_CONTROLS, TUNING_DEFAULTS, type RangeControl, changed, defaultsFor, drawnTuning, sanitize } from "./tuning";

const source = readFileSync(new URL("./GalaxyTab.tsx", import.meta.url), "utf-8");
const control = TUNING_CONTROLS.find((c) => c.key === "knotsIntensity") as RangeControl;

describe("knotsIntensity, the control (S97)", () => {
  it("defaults to 1 on every template, so untouched nothing drawn moves", () => {
    expect(TUNING_DEFAULTS.knotsIntensity).toBe(1);
    for (const t of [null, "milky_way", "ngc_4414"]) expect(defaultsFor(t).knotsIntensity).toBe(1);
  });

  it("is a log range from 0.05 to 4 in the panel's Components group, labelled, its about stating the closure", () => {
    expect(control).toMatchObject({ kind: "range", min: 0.05, max: 4, log: true, group: "Components", label: "HII knots intensity" });
    expect(control.switch).toBeFalsy();
    expect(control.about).toMatch(/display balance/);
    expect(control.about).toMatch(/At 1 the screen carries the census's Halpha exactly/);
    expect(control.about).toMatch(/by exactly this factor/);
    expect(control.about).toMatch(/not the region regime's HII regions/);
    expect(control.about).toMatch(/ionized gas intensity does not reach the knots/);
  });

  it("is clamped to its range and kept when valid", () => {
    expect(sanitize({ knotsIntensity: 0.001 }).knotsIntensity).toBe(0.05);
    expect(sanitize({ knotsIntensity: 9 }).knotsIntensity).toBe(4);
    expect(sanitize({ knotsIntensity: 0.3 }).knotsIntensity).toBe(0.3);
    expect(sanitize({ knotsIntensity: "0.3" }).knotsIntensity).toBe(1);
  });

  it("is reported in the copy box's diff when moved, and not at the default", () => {
    expect(changed({ ...TUNING_DEFAULTS })).toEqual({});
    expect(changed({ ...TUNING_DEFAULTS, knotsIntensity: 0.2 })).toEqual({ knotsIntensity: 0.2 });
    const mw = defaultsFor("milky_way");
    expect(changed({ ...mw, knotsIntensity: 0.2 }, mw)).toEqual({ knotsIntensity: 0.2 });
  });

  it("is not a load key: a landing's hold draws it from the held template, like every drawing choice", () => {
    expect(LOAD_TUNING_KEYS as readonly string[]).not.toContain("knotsIntensity");
    const live = { ...TUNING_DEFAULTS, knotsIntensity: 2 };
    const held = { ...TUNING_DEFAULTS, knotsIntensity: 0.5 };
    expect(drawnTuning(live, held).knotsIntensity).toBe(0.5);
  });
});

describe("the knots' gain as drawn (S97)", () => {
  const cases: [number, number, number][] = [
    [1, 0, 1],
    [1.65, 0, 1],
    [1.2, -2.5, 0.37],
    [0.25, 8, 0.001],
    [4, -6, 0.999],
  ];

  it("at intensity 1 is today's expression to the bit", () => {
    for (const [g, e, w] of cases) {
      const today = LIGHT_PER_LSUN_PC2 * g * 2 ** e * w;
      expect(Object.is(knotsGain(LIGHT_PER_LSUN_PC2, g, e, w, 1), today)).toBe(true);
    }
  });

  it("at intensity k is k times it", () => {
    for (const [g, e, w] of cases) {
      const today = LIGHT_PER_LSUN_PC2 * g * 2 ** e * w;
      for (const k of [0.05, 0.3, 2, 4]) expect(knotsGain(LIGHT_PER_LSUN_PC2, g, e, w, k)).toBeCloseTo(k * today, 15);
    }
  });

  it("is what GalaxyTab hands the knots' one FluxPoints, with the drawn tuning's intensity", () => {
    expect(source).toMatch(/const\s+knotsGain\s*=\s*knotsGainOf\(\s*LIGHT_PER_LSUN_PC2\s*,\s*look\.fieldGain\s*,\s*exposure\s*,\s*weights\.field\s*,\s*look\.knotsIntensity\s*\)/);
    // One drawer of the knots: the FluxPoints with the disc profile; its gain uniform is shared with the wings' pass.
    expect(source.match(/gain=\{knotsGain\}/g)).toHaveLength(1);
    expect(source).toMatch(/<FluxPoints[^>]*gain=\{knotsGain\}[^>]*profile=\{2\}/);
    // The old inline product is gone.
    expect(source).not.toMatch(/knotsGain\s*=\s*LIGHT_PER_LSUN_PC2\s*\*/);
  });

  it("leaves the points' and the star-first field's gains (the page's hooks) as they were", () => {
    expect(source).toMatch(/const\s+pointsGain\s*=\s*LIGHT_PER_LSUN_PC2\s*\*\s*look\.fieldGain\s*\*\s*2\s*\*\*\s*exposure\s*\*\s*pointGain\s*\*/);
    expect(source).toMatch(/const\s+starFieldGain\s*=\s*LIGHT_PER_LSUN_PC2\s*\*\s*look\.fieldGain\s*\*\s*2\s*\*\*\s*exposure;/);
  });
});
