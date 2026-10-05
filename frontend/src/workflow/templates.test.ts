import * as flow from "@interface/flow.js";
import { ApiError } from "@interface/transport.js";
import { describe, expect, it } from "vitest";

import { type FlowState, type InputDecl, reopen, runHash } from "./logic";
import fixture from "./templates.fixture.json";
import {
  EVENTS_INPUT,
  TEMPLATE_KEY,
  applyTemplate,
  isEdited,
  parseTemplates,
  pinWords,
  readTemplates,
  switcherItems,
  templateLabel,
  templateOf,
  templateQuery,
  thumbnailOf,
} from "./templates";
import { generateDefault, isGenerated, landOn, queryOf } from "./useWorkflow";

const PAYLOAD: unknown = fixture.payload;
const copy = () => JSON.parse(JSON.stringify(PAYLOAD)) as { default: string; templates: Record<string, unknown>[] };

// A flow over the API's own input names, built by flow.js itself: the defaults are the fixture's `milky_way`.
const RANGES: Record<string, [number, number, number]> = {
  halo_mass: [1e11, 1e13, 1],
  disc_spin: [0.005, 0.05, 1],
  halo_assembly_z: [0.5, 5, 1],
  baryon_retention: [0.05, 0.5, 1],
  infall_timescale: [1, 14, 4],
  inside_out_index: [0, 3, 4],
  migration_efficiency: [0, 8, 4],
};
// The seeds and their checkpoints, as /api/inputs declares them: five since S55 (D214), the layer's own at the pattern's.
const SEEDS: Record<string, number> = { world_seed: 1, pattern_seed: 3, systems_seed: 5, planets_seed: 6, texture_seed: 3 };

function fresh(model = "azimuthal"): FlowState {
  const milkyWay = parseTemplates(PAYLOAD).templates[0];
  const cps = [1, 2, 3, 4, 5, 6].map((n) => ({ n, name: `cp${n}`, stages: [`s${n}`] }));
  const stages = { model, order: cps.map((c) => c.stages[0]), checkpoints: cps };
  const controls: InputDecl[] = Object.entries(RANGES).map(([name, [lo, hi, checkpoint]]) => ({
    name, label: "", kind: "control", about: "", checkpoint, default: milkyWay.inputs.controls[name], lo, hi,
  }));
  const seeds: InputDecl[] = Object.entries(SEEDS).map(([name, checkpoint]) => ({ name, label: "", kind: "seed", about: "", checkpoint, default: 0 }));
  const events: InputDecl[] = [{ name: EVENTS_INPUT, label: "", kind: "events", about: "", checkpoint: 2, default: milkyWay.inputs.mergers }];
  return flow.initial(flow.catalogue(stages, { controls, seeds, events })) as FlowState;
}

describe("/api/templates, as the viewer reads it (S54, D213)", () => {
  it("parses the contract's shape: the default, each template's inputs, camera, lens and filter set", () => {
    const got = parseTemplates(PAYLOAD);
    expect(got.default).toBe("milky_way");
    expect(got.templates.map((t) => t.name)).toEqual(["milky_way", "ngc_4414"]);
    const [milkyWay, ngc] = got.templates;
    // D213 ruling 5: the Milky Way face-on through the 45° lens and rgb; NGC 4414 at 55° through a 5° lens and wfc3.
    expect(milkyWay.camera).toEqual({ inclination_deg: 0, azimuth_deg: 270, radius_kpc: 20, fov_deg: 45 });
    expect(milkyWay.filters).toBe("rgb");
    expect(ngc.camera).toEqual({ inclination_deg: 55, azimuth_deg: 0, radius_kpc: 20, fov_deg: 5 });
    expect(ngc.filters).toBe("wfc3");
    expect(ngc.instrument).toEqual({ distance_mpc: 17.7, pixel_scale_arcsec: null });
    expect(milkyWay.instrument).toEqual({ distance_mpc: null, pixel_scale_arcsec: null });
    expect(ngc.inputs.seeds).toEqual({ world_seed: 4414, pattern_seed: 4414, systems_seed: 4414, planets_seed: 4414, texture_seed: 4414 });
    expect(ngc.inputs.mergers).toEqual([]);
    expect(milkyWay.inputs.mergers).toHaveLength(2);
    expect(templateOf(got, "ngc_4414")).toBe(ngc);
    expect(templateOf(got, "andromeda")).toBeNull();
    expect(templateOf(null, "milky_way")).toBeNull();
  });

  it("refuses a payload it would have to guess at, naming what is wrong", () => {
    const broken = (change: (p: ReturnType<typeof copy>) => void) => {
      const p = copy();
      change(p);
      return () => parseTemplates(p);
    };
    expect(() => parseTemplates({})).toThrow(/lists no templates/);
    expect(() => parseTemplates({ default: "milky_way", templates: [] })).toThrow(/lists no templates/);
    expect(broken((p) => (p.default = "andromeda"))).toThrow(/default "andromeda" is not one of milky_way, ngc_4414/);
    expect(broken((p) => (p.templates[1].name = "milky_way"))).toThrow(/repeats a name/);
    expect(broken((p) => (p.templates[1].name = "../secret"))).toThrow(/usable name/);
    expect(broken((p) => (p.templates[1].filters = "sdss"))).toThrow(/ngc_4414 names the filter set "sdss"; the viewer holds rgb/);
    expect(broken((p) => ((p.templates[1].camera as Record<string, unknown>).fov_deg = 0))).toThrow(/field of view of 0 degrees is not a lens/);
    expect(broken((p) => delete (p.templates[1].camera as Record<string, unknown>).fov_deg)).toThrow(/not a lens/);
    expect(broken((p) => ((p.templates[1].camera as Record<string, unknown>).radius_kpc = -1))).toThrow(/camera inclination 55, azimuth 0, radius -1/);
    expect(broken((p) => ((p.templates[0].inputs as Record<string, unknown>).controls = { halo_mass: "heavy" }))).toThrow(/inputs.controls.halo_mass is not a number/);
    expect(broken((p) => delete (p.templates[0].inputs as Record<string, unknown>).mergers)).toThrow(/inputs.mergers is not a list/);
  });

  it("carries what it does not read, and takes a missing instrument as numbers not read", () => {
    const p = copy();
    delete p.templates[0].instrument;
    delete p.templates[0].about;
    const [milkyWay, ngc] = parseTemplates(p).templates;
    expect(milkyWay.instrument).toEqual({ distance_mpc: null, pixel_scale_arcsec: null });
    expect(milkyWay.about).toBe("");
    expect(ngc.fit).toEqual({ targets: [], controls: [] });
    expect(ngc.checks).toEqual([]);
  });
});

describe("a template's pins (S58, D217 item 2)", () => {
  // What /api/fields declares of the field the pin decides, as far as the words need it.
  const FIELDS = [
    { name: "bar_present", label: "Barred", categories: ["no", "yes"], unit: "dimensionless", unit_display: "" },
    { name: "stellar_mass_total", label: "Stellar mass", categories: [], unit: "Msun", unit_display: "M☉" },
    { name: "pitch_angle", label: "Spiral arm pitch angle", categories: [], unit: "deg", unit_display: "°" },
    { name: "sun_azimuth", label: "Azimuth of the Sun", categories: [], unit: "rad", unit_display: "rad" },
    { name: "arm_segment_pitch_scatter", label: "Spread of a segment's pitch", categories: [], unit: "dimensionless", unit_display: "" },
  ];

  it("reads each pin as published: the field it decides, the observed class or the measured number, and where it was read", () => {
    const [milkyWay, ngc] = parseTemplates(PAYLOAD).templates;
    expect(milkyWay.pins).toEqual([
      { name: "bar_present", value: true, source: "[illustrative] the Milky Way is barred" },
      { name: "sun_bar_angle", value: 30, source: "[illustrative] the bar's angle to the Sun-centre line" },
    ]);
    expect(ngc.pins).toEqual([
      { name: "bar_present", value: false, source: "[illustrative] no source finds a bar in NGC 4414" },
      { name: "pitch_angle", value: 28.9, source: "[illustrative] the measured mean pitch of its arm segments" },
    ]);
  });

  it("reads /api/templates as S59 answers it: a numeric pin does not stop the viewer from landing (D218 items 5-6)", () => {
    // Until S59 a pin's value was a class and anything else was refused; a template with a measured number among
    // its pins then failed to parse, and the viewer showed "Loading the model failed" in place of the galaxy.
    const p = copy();
    p.templates[1].pins = [{ name: "pitch_angle", value: 28.9, source: "[verified: ...]" }, { name: "sun_bar_angle", value: 0, source: "" }];
    expect(parseTemplates(p).templates[1].pins.map((pin) => pin.value)).toEqual([28.9, 0]);
  });

  it("takes a template without pins as pinned nothing: an API from before S58", () => {
    const p = copy();
    delete p.templates[0].pins;
    p.templates[1].pins = [];
    expect(parseTemplates(p).templates.map((t) => t.pins)).toEqual([[], []]);
  });

  it("refuses a pin it cannot read rather than dropping what the API would still apply", () => {
    const broken = (pins: unknown) => {
      const p = copy();
      p.templates[1].pins = pins;
      return () => parseTemplates(p);
    };
    expect(broken("bar_present")).toThrow(/template ngc_4414: pins is not a list/);
    expect(broken([{ name: "bar_present", value: "no", source: "" }])).toThrow(/template ngc_4414: a pin is \{name, value: true or false or a number, source\}/);
    expect(broken([{ value: false }])).toThrow(/a pin is/);
    // a number that is none (JSON's null for a NaN, a string of digits) is no measured value
    expect(broken([{ name: "pitch_angle", value: null, source: "" }])).toThrow(/a pin is/);
    expect(broken([{ name: "pitch_angle", value: "28.9", source: "" }])).toThrow(/a pin is/);
    // a pin without a source is still a pin: the words stand, the tooltip is empty
    expect(broken([{ name: "bar_present", value: false }])()).toMatchObject({ templates: [{}, { pins: [{ name: "bar_present", value: false, source: "" }] }] });
  });

  it("says a pin in the field declaration's own words, with none of the viewer's", () => {
    const [milkyWay, ngc] = parseTemplates(PAYLOAD).templates;
    expect(pinWords(ngc.pins[0], FIELDS)).toBe("Barred: no (as observed)");
    expect(pinWords(milkyWay.pins[0], FIELDS)).toBe("Barred: yes (as observed)");
    // No declaration (the fields not loaded yet, a model without the field): the pin's own name, yes or no.
    expect(pinWords(ngc.pins[0])).toBe("bar_present: no (as observed)");
    expect(pinWords(milkyWay.pins[0], [])).toBe("bar_present: yes (as observed)");
    // A field that is not a two-class one does not lend its categories to a true-or-false pin.
    expect(pinWords({ name: "stellar_mass_total", value: true, source: "" }, FIELDS)).toBe("Stellar mass: yes (as observed)");
  });

  it("says a measured number with the declaration's label and unit, and with neither where no field has the pin's name", () => {
    const [milkyWay, ngc] = parseTemplates(PAYLOAD).templates;
    // NGC 4414's pitch: the pin decides the published field of its own name, whose label and unit these are.
    expect(pinWords(ngc.pins[1], FIELDS)).toBe("Spiral arm pitch angle: 28.9° (as observed)");
    // The Milky Way's bar angle publishes sun_azimuth: no field is named sun_bar_angle, and /api/templates gives a
    // pin no label and no unit, so the viewer states the pin's name and the bare number (rule B9: no unit guessed).
    expect(pinWords(milkyWay.pins[1], FIELDS)).toBe("sun_bar_angle: 30 (as observed)");
    expect(pinWords(ngc.pins[1])).toBe("pitch_angle: 28.9 (as observed)");
    // A unit that is a word stands after a space; a dimensionless number has none.
    expect(pinWords({ name: "sun_azimuth", value: 1.1497328186297713, source: "" }, FIELDS)).toBe("Azimuth of the Sun: 1.15 rad (as observed)");
    expect(pinWords({ name: "stellar_mass_total", value: 4.75e10, source: "" }, FIELDS)).toBe("Stellar mass: 4.750 × 10¹⁰ M☉ (as observed)");
    expect(pinWords({ name: "arm_segment_pitch_scatter", value: 0.56, source: "" }, FIELDS)).toBe("Spread of a segment's pitch: 0.56 (as observed)");
    // Zero is a number, not a "no".
    expect(pinWords({ name: "pitch_angle", value: 0, source: "" }, FIELDS)).toBe("Spiral arm pitch angle: 0° (as observed)");
  });
});

describe("template= on every request of a galaxy started from a template (S58)", () => {
  const { templates } = parseTemplates(PAYLOAD);
  const [milkyWay, ngc] = templates;

  it("a template's galaxy is asked for by its inputs and by its name: the name brings the pins", () => {
    const landed = landOn(fresh(), ngc);
    const q = queryOf(landed, "azimuthal", ngc);
    expect(q[TEMPLATE_KEY]).toBe("ngc_4414");
    // every input is still laid out, value by value, and the model named
    expect(q).toEqual({ ...(flow.query(landed) as Record<string, unknown>), model: "azimuthal", template: "ngc_4414" });
    expect(queryOf(landOn(fresh(), milkyWay), "azimuthal", milkyWay).template).toBe("milky_way");
    // a pin is never an input of the query: the API refuses one, and the template's name is what gives it
    expect(Object.keys(q)).not.toContain("bar_present");
  });

  it("stands through Edit galaxy: a reopened checkpoint, a moved control, a re-rolled seed, another event list, another model", () => {
    const landed = landOn(fresh(), ngc);
    const reopened = reopen(landed, 1).state;
    expect(queryOf(reopened, "azimuthal", ngc).template).toBe("ngc_4414");
    const moved = flow.setValue(reopened, "halo_mass", 2e12) as FlowState;
    const rerolled = flow.reroll(moved, ["world_seed"], () => 7) as FlowState;
    const merged = flow.setValue(rerolled, EVENTS_INPUT, [{ time: 5, mass_ratio: 0.1, gas_fraction: 0.2 }]) as FlowState;
    expect(isEdited(merged, "azimuthal", ngc)).toBe(true);
    const q = queryOf(merged, "azimuthal", ngc);
    // the edits are the query's own inputs, which the API lays over the template's; the template is still named
    expect([q.template, q.halo_mass, q.world_seed, q.mergers]).toEqual(["ngc_4414", 2e12, 7, '[{"time":5,"mass_ratio":0.1,"gas_fraction":0.2}]']);
    expect(queryOf(merged, "basic", ngc)).toMatchObject({ model: "basic", template: "ngc_4414" });
  });

  it("a galaxy started from no template sends none: the query is the one sent before the templates, to the letter", () => {
    const free = generateDefault(fresh());
    const q = queryOf(free, "azimuthal", null);
    expect(TEMPLATE_KEY in q).toBe(false);
    expect(q).toEqual({ ...(flow.query(free) as Record<string, unknown>), model: "azimuthal" });
    const bare = { halo_mass: 1.1e12, model: "azimuthal" };
    expect(templateQuery(bare, null)).toBe(bare); // the very object, untouched
    expect(templateQuery(bare, ngc)).toEqual({ halo_mass: 1.1e12, model: "azimuthal", template: "ngc_4414" });
    expect(bare).toEqual({ halo_mass: 1.1e12, model: "azimuthal" });
  });

  it("is part of every cache key and of the run hash: the same inputs under another template are another galaxy", () => {
    // NGC 4414's inputs reached by editing the Milky Way: one input vector, two pins.
    const state = landOn(fresh(), ngc);
    const [asNgc, asMilkyWay, asNone] = [ngc, milkyWay, null].map((t) => queryOf(state, "azimuthal", t));
    const keys = [asNgc, asMilkyWay, asNone].map((q) => JSON.stringify([["bar_present"], q])); // a loader's key (Published.tsx)
    expect(new Set(keys).size).toBe(3);
    expect(new Set([asNgc, asMilkyWay, asNone].map(runHash)).size).toBe(3);
  });
});

describe("the loader's fallback: an API from before the templates still lands", () => {
  it("answers null for a 404, the transport's own error for a route that is not there", async () => {
    const missing = new ApiError(404, { error: "no such route" }, "/api/templates");
    await expect(readTemplates(() => Promise.reject(missing))).resolves.toBeNull();
  });

  it("parses what the route answers", async () => {
    const got = await readTemplates(() => Promise.resolve(PAYLOAD));
    expect(got?.default).toBe("milky_way");
  });

  it("throws everything else: the API down, a server error, a payload that does not parse", async () => {
    await expect(readTemplates(() => Promise.reject(new ApiError(500, null, "/api/templates")))).rejects.toThrow(/500/);
    await expect(readTemplates(() => Promise.reject(new TypeError("Failed to reach the server")))).rejects.toThrow(/Failed to reach/);
    await expect(readTemplates(() => Promise.resolve({ default: "milky_way", templates: [] }))).rejects.toThrow(/lists no templates/);
  });
});

describe("landing on a template (rule D1 as amended)", () => {
  const { templates } = parseTemplates(PAYLOAD);
  const [milkyWay, ngc] = templates;

  it("milky_way is the default galaxy exactly: the state the defaults confirmed through reach, and the same query", () => {
    const landed = landOn(fresh(), milkyWay);
    const defaults = generateDefault(fresh());
    expect(flow.query(landed)).toEqual(flow.query(defaults));
    expect(landed.confirmed).toBe(6);
    expect(landed.current).toBe(6);
    expect(isGenerated(landed)).toBe(true);
  });

  it("another template lands generated on its own controls, seeds and event list", () => {
    const landed = landOn(fresh(), ngc);
    expect(isGenerated(landed)).toBe(true);
    expect(landed.values.disc_spin).toBe(0.0117);
    expect(landed.values.halo_mass).toBe(9.0e11);
    expect(landed.values.world_seed).toBe(4414);
    expect(landed.values.planets_seed).toBe(4414);
    expect(landed.values[EVENTS_INPUT]).toEqual([]);
    // The query is the whole input vector, the events as JSON: what every route is sent.
    const q = flow.query(landed) as Record<string, unknown>;
    expect(q.mergers).toBe("[]");
    expect(q.disc_spin).toBe(0.0117);
    expect(Object.keys(q).sort()).toEqual([...Object.keys(RANGES), ...Object.keys(SEEDS), EVENTS_INPUT].sort());
  });

  it("sets each input through flow.setValue, so a value outside its published range is refused and not sent", () => {
    const wide = { ...ngc, inputs: { ...ngc.inputs, controls: { ...ngc.inputs.controls, disc_spin: 0.5 } } };
    expect(() => applyTemplate(fresh(), wide)).toThrow(/disc_spin = 0.5 is outside its published range/);
    const unknown = { ...ngc, inputs: { ...ngc.inputs, controls: { ...ngc.inputs.controls, bar_strength: 1 } } };
    expect(() => applyTemplate(fresh(), unknown)).toThrow(/bar_strength is not an input/);
  });

  it("the event list set is a copy: editing the galaxy's events never reaches the template", () => {
    const landed = applyTemplate(fresh(), milkyWay);
    (landed.values[EVENTS_INPUT] as { time: number }[])[0].time = 1;
    expect(milkyWay.inputs.mergers[0].time).toBe(3.8);
  });

  it("Edit galaxy starts from the template's inputs with the confirmations kept; reopening discards the later ones", () => {
    const landed = landOn(fresh(), ngc);
    expect(landed.confirmed).toBe(6); // "Edit galaxy" is a tab switch: nothing is touched
    const { state, discarded } = reopen(landed, 4);
    expect(discarded).toEqual([5, 6]);
    expect(state.values.disc_spin).toBe(0.0117); // the controls open at the template's values
    expect(state.values.world_seed).toBe(4414);
    expect(isEdited(state, "azimuthal", ngc)).toBe(false); // reopened, nothing changed: still the template's inputs
  });
});

describe("the fifth seed, texture_seed (S55, D214): the rail and the templates are data-driven", () => {
  const { templates } = parseTemplates(PAYLOAD);
  const [milkyWay, ngc] = templates;

  it("stands at the checkpoint /api/inputs declares it at, beside the pattern's seed, with no code naming it", () => {
    const state = fresh();
    expect(state.cat.inputs.get("texture_seed")).toMatchObject({ kind: "seed", checkpoint: 3, default: 0 });
    expect(state.cat.checkpoints.find((c) => c.n === 3)?.inputs).toEqual(["pattern_seed", "texture_seed"]);
    // What a reroll at the checkpoint draws: both of its seeds (the rail names each, Workflow.tsx).
    expect(flow.seedsAt(state, 3)).toEqual(["pattern_seed", "texture_seed"]);
    expect(state.values.texture_seed).toBe(0);
  });

  it("takes a template's value and sends it: the query carries the fifth seed", () => {
    const landed = landOn(fresh(), ngc);
    expect(landed.values.texture_seed).toBe(4414);
    expect((flow.query(landed) as Record<string, unknown>).texture_seed).toBe(4414);
    expect((flow.query(landOn(fresh(), milkyWay)) as Record<string, unknown>).texture_seed).toBe(0);
  });

  it("is an input like the others: rerolled, the galaxy is no longer the template", () => {
    const open = reopen(landOn(fresh(), ngc), 3).state;
    const both = flow.reroll(open, flow.seedsAt(open, 3), (name: string) => (name === "texture_seed" ? 7 : 8)) as FlowState;
    expect([both.values.pattern_seed, both.values.texture_seed]).toEqual([8, 7]);
    const alone = flow.reroll(open, ["texture_seed"], () => 7) as FlowState;
    expect([alone.values.pattern_seed, alone.values.texture_seed]).toEqual([4414, 7]);
    expect(isEdited(alone, "azimuthal", ngc)).toBe(true);
  });
});

describe("what the switcher shows", () => {
  const { templates } = parseTemplates(PAYLOAD);
  const [milkyWay, ngc] = templates;

  it("the galaxy is the template until an input or the model changes", () => {
    const landed = landOn(fresh(), ngc);
    expect(isEdited(landed, "azimuthal", ngc)).toBe(false);
    expect(isEdited(landed, "azimuthal", milkyWay)).toBe(true); // it is NGC 4414's inputs, not the Milky Way's
    expect(isEdited(landed, "basic", ngc)).toBe(true); // another model is another galaxy
    const moved = flow.setValue(reopen(landed, 4).state, "infall_timescale", 5) as FlowState;
    expect(isEdited(moved, "azimuthal", ngc)).toBe(true);
    const back = flow.setValue(moved, "infall_timescale", 7) as FlowState;
    expect(isEdited(back, "azimuthal", ngc)).toBe(false); // put back: the template again
    const rerolled = flow.reroll(reopen(landed, 5).state, ["systems_seed"], () => 7) as FlowState;
    expect(isEdited(rerolled, "azimuthal", ngc)).toBe(true); // a re-rolled seed is an edit
    const merged = flow.setValue(reopen(landed, 2).state, EVENTS_INPUT, [{ time: 5, mass_ratio: 0.1, gas_fraction: 0.2 }]) as FlowState;
    expect(isEdited(merged, "azimuthal", ngc)).toBe(true);
  });

  it("presses the template the galaxy is, with its thumbnail", () => {
    const items = switcherItems(templates, "ngc_4414", false);
    expect(items.map((i) => [i.name, i.caption, i.pressed, i.edited])).toEqual([
      ["milky_way", "Milky Way", false, false],
      ["ngc_4414", "NGC 4414", true, false],
    ]);
    expect(items.map((i) => i.thumbnail)).toEqual(["/templates/milky_way.png", "/templates/ngc_4414.png"]);
    expect(items[1].title).toBe(ngc.about);
  });

  it("an edited galaxy is no longer the template: its button is released and says so", () => {
    const items = switcherItems(templates, "ngc_4414", true);
    expect(items.map((i) => [i.name, i.caption, i.pressed, i.edited])).toEqual([
      ["milky_way", "Milky Way", false, false],
      ["ngc_4414", "NGC 4414 · edited", false, true],
    ]);
    expect(items[1].title).toMatch(/choose it again to restore the template/);
    expect(items[1].thumbnail).toBe("/templates/ngc_4414.png"); // the template's own picture, never the edited galaxy's
    expect(templateLabel(ngc, true)).toBe("NGC 4414 · edited");
    expect(templateLabel(milkyWay, false)).toBe("Milky Way");
  });

  it("shows nothing where the API has no templates, and presses nothing before one is chosen", () => {
    expect(switcherItems([], null, false)).toEqual([]);
    expect(switcherItems(templates, null, false).some((i) => i.pressed)).toBe(false);
  });

  it("serves a thumbnail from public/templates/<name>.png under the app's base", () => {
    expect(thumbnailOf("milky_way")).toBe("/templates/milky_way.png");
    expect(thumbnailOf("ngc_4414", "/galaxygen/")).toBe("/galaxygen/templates/ngc_4414.png");
  });
});
