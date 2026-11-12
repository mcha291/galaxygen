// S97 (lane V, build 2): "load a combination" - the Tuning panel's copy box read back. The round trip is the test that
// matters: parseCombination(copyBoxText(T, e), defaults) gives back T and e.
import { readFileSync } from "node:fs";
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { describe, expect, it } from "vitest";

import { combinationNotice, TuningPanel } from "./TuningPanel";
import {
  EXPOSURE_RANGE,
  TUNING_CONTROLS,
  TUNING_DEFAULTS,
  type Tuning,
  clampExposure,
  copyBoxText,
  defaultsFor,
  parseCombination,
} from "./tuning";

const STATS = { width: 0, height: 0, ms: 0, gpuMs: null, gpuAvailable: false } as never;

/** A tuning with every range at an in-range value off its default, every toggle flipped, every select at another option. */
function moved(base: Tuning, at: number): Tuning {
  const out: Record<string, unknown> = { ...base };
  for (const c of TUNING_CONTROLS) {
    if (c.kind === "toggle") out[c.key] = !base[c.key];
    else if (c.kind === "select") out[c.key] = c.options[(c.options.findIndex((o) => o.value === base[c.key]) + 1) % c.options.length].value;
    else {
      const v = c.min + at * (c.max - c.min);
      out[c.key] = c.integer ? Math.round(v) : v;
    }
  }
  return out as unknown as Tuning;
}

describe("the copy box's text (S97: lifted into tuning.ts, the panel's output unchanged)", () => {
  it("is the template, the filter set, the exposure and the diff, in that order", () => {
    const mw = defaultsFor("milky_way");
    expect(copyBoxText({ ...mw, knotsIntensity: 0.2 }, mw, "milky_way", "rgb", 1.5)).toBe('{"template":"milky_way","filters":"rgb","exposure":1.5,"knotsIntensity":0.2}');
    expect(copyBoxText({ ...TUNING_DEFAULTS }, TUNING_DEFAULTS, undefined, undefined, undefined)).toBe('{"template":null,"filters":null,"exposure":0}');
  });

  it("is what the panel builds its box from", () => {
    const panel = readFileSync(new URL("./TuningPanel.tsx", import.meta.url), "utf-8");
    expect(panel).toMatch(/value=\{copyBoxText\(tuning,\s*defaults,\s*template,\s*filterSet,\s*exposure\)\}/);
    expect(panel).not.toMatch(/JSON\.stringify\(\{\s*template:/);
  });
});

describe("parseCombination (S97)", () => {
  it("round-trips any tuning and exposure through the copy box, on each template's defaults", () => {
    for (const template of [null, "milky_way", "ngc_4414"]) {
      const d = defaultsFor(template);
      const tunings = [d, moved(d, 0), moved(d, 0.37), moved(d, 1), { ...d, knotsIntensity: 0.05 }, { ...d, toneMapping: "linear" as const }];
      for (const T of tunings) {
        for (const e of [EXPOSURE_RANGE.min, -2.5, 0, 0.5, EXPOSURE_RANGE.max]) {
          const c = parseCombination(copyBoxText(T, d, template, "rgb", e), d);
          expect(c.error).toBeNull();
          expect(c.tuning).toEqual(T);
          expect(c.exposure).toBe(e);
          expect(c.template).toBe(template);
          expect(c.filters).toBe("rgb");
          expect(c.ignored).toEqual([]);
          expect(c.rejected).toEqual([]);
        }
      }
    }
  });

  it("lays the paste over the defaults it is given: keys absent are the defaults'", () => {
    const mw = defaultsFor("milky_way");
    const c = parseCombination('{"bloomStrength":1}', mw);
    expect(c.tuning).toEqual({ ...mw, bloomStrength: 1 });
    expect(c.exposure).toBeNull();
    expect(c.template).toBeNull();
  });

  it("refuses bad JSON and non-objects, applying nothing", () => {
    for (const text of ["", "{", "not json", "[1,2]", "null", "3", '"text"']) {
      const c = parseCombination(text, TUNING_DEFAULTS);
      expect(c.error).not.toBeNull();
      expect(c.tuning).toBeNull();
      expect(c.exposure).toBeNull();
    }
  });

  it("returns unknown keys in ignored, not as an error, and unusable values in rejected", () => {
    const c = parseCombination('{"template":"milky_way","glow":2,"knotz":1,"toneMapping":"sepia","dither":"yes","fieldGain":2}', TUNING_DEFAULTS);
    expect(c.error).toBeNull();
    expect(c.ignored).toEqual(["glow", "knotz"]);
    expect(c.rejected).toEqual(["toneMapping", "dither"]);
    expect(c.tuning).toEqual({ ...TUNING_DEFAULTS, fieldGain: 2 });
  });

  it("clamps out-of-range values as sanitize does", () => {
    const c = parseCombination('{"knotsIntensity":0.001,"bloomStrength":99,"steps":17.2,"resolution":-1}', TUNING_DEFAULTS);
    expect(c.tuning).toMatchObject({ knotsIntensity: 0.05, bloomStrength: 4, steps: 32, resolution: 0.25 });
  });

  it("clamps the exposure to the slider's range and snaps it to its step; anything else is absent", () => {
    expect(EXPOSURE_RANGE).toEqual({ min: -6, max: 8, step: 0.5 });
    expect(parseCombination('{"exposure":12}').exposure).toBe(8);
    expect(parseCombination('{"exposure":-40}').exposure).toBe(-6);
    expect(parseCombination('{"exposure":1.3}').exposure).toBe(1.5);
    expect(parseCombination('{"exposure":-0.2}').exposure).toBe(0);
    expect(parseCombination('{"exposure":"2"}').exposure).toBeNull();
    expect(parseCombination('{"exposure":null}').exposure).toBeNull();
    expect(clampExposure(Number.NaN)).toBeNull();
    expect(clampExposure(Infinity)).toBeNull();
  });

  it("applies a box from another template over this one's defaults, reporting the template and filters it names", () => {
    // The owner's use of 2026-10-19: the Milky Way's box pasted on NGC 4414.
    const mw = defaultsFor("milky_way");
    const ngc = defaultsFor("ngc_4414");
    const box = copyBoxText({ ...mw, bloomStrength: 1.5, knotsIntensity: 0.3 }, mw, "milky_way", "rgb", 0);
    const c = parseCombination(box, ngc);
    expect(c.error).toBeNull();
    expect(c.tuning).toEqual({ ...ngc, bloomStrength: 1.5, knotsIntensity: 0.3 });
    expect(c.template).toBe("milky_way");
    const notice = combinationNotice(c, "ngc_4414", "wfc3", true);
    expect(notice).toMatch(/copied on template milky_way, filters rgb; applied here anyway, nothing switched/);
  });
});

describe("the notice (S97)", () => {
  it("says what was applied and what was not, on one line", () => {
    const ok = parseCombination('{"template":"milky_way","filters":"rgb","exposure":2,"glow":1,"dither":"x"}', TUNING_DEFAULTS);
    const n = combinationNotice(ok, "milky_way", "rgb", true);
    expect(n).toBe("Applied over milky_way defaults; exposure 2 stops; ignored (no such choice): glow; kept the default (value unusable): dither.");
    expect(n).not.toMatch(/\n/);
    expect(combinationNotice(ok, "milky_way", "rgb", false)).toMatch(/exposure not applied here/);
    expect(combinationNotice(parseCombination("{"), "milky_way", "rgb", false)).toMatch(/^Not applied - not JSON/);
  });
});

describe("the panel (S97; static markup, as ErrorBoundary.test.ts draws)", () => {
  it("draws the copy box unchanged and the paste box with its Apply button", () => {
    const mw = defaultsFor("milky_way");
    const t = { ...mw, knotsIntensity: 0.2 };
    const html = renderToStaticMarkup(
      h(TuningPanel, { tuning: t, onChange: () => {}, stats: STATS, template: "milky_way", filterSet: "rgb", exposure: 1, defaults: mw, onExposure: () => {}, initiallyOpen: true }),
    );
    const box = copyBoxText(t, mw, "milky_way", "rgb", 1).replace(/"/g, "&quot;");
    expect(html).toContain(box);
    expect(html).toContain('aria-label="A combination to load, as the copy box&#x27;s JSON"');
    expect(html).toMatch(/<button[^>]*disabled[^>]*>Apply<\/button>|<button[^>]*>Apply<\/button>/);
    expect(html).toContain("HII knots intensity");
  });

  it("is closed by default, as before", () => {
    const html = renderToStaticMarkup(h(TuningPanel, { tuning: { ...TUNING_DEFAULTS }, onChange: () => {}, stats: STATS }));
    expect(html).not.toContain("Apply");
  });
});
