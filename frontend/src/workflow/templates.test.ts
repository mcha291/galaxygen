import * as flow from "@interface/flow.js";
import { ApiError } from "@interface/transport.js";
import { describe, expect, it } from "vitest";

import { type FlowState, type InputDecl, reopen, runHash } from "./logic";
import live from "./pins.live.json";
import fixture from "./templates.fixture.json";
import {
  type Pin,
  type PinTable,
  EVENTS_INPUT,
  TABLE_LISTED,
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

// The route's own pins, by template, as it serves them today: pins.live.json, written from /api/templates and held
// to it by tests/test_viewer.py. The fixture states none; each template's are laid in here, so every test below
// reads what the viewer will be served, and a shape the wire grows is in front of the parser the day it is served.
const LIVE = live.pins as unknown as Record<string, Record<string, unknown>[]>;
const PAYLOAD: unknown = { ...fixture.payload, templates: fixture.payload.templates.map((t) => ({ ...t, pins: LIVE[t.name] })) };
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
  // What /api/fields declares of the fields the pins decide, as far as the words need it (as the route declares them
  // at S60; `stellar_mass_total` and `ring_spacing` stand for a field with a unit that is a word and one with none).
  const FIELDS = [
    { name: "bar_present", label: "Barred", categories: ["no", "yes"], unit: "dimensionless", unit_display: "" },
    { name: "arm_class", label: "Arm class", categories: ["grand_design", "multi_armed", "flocculent"], unit: "dimensionless", unit_display: "" },
    { name: "stellar_mass_total", label: "Stellar mass", categories: [], unit: "Msun", unit_display: "M☉" },
    { name: "pitch_angle", label: "Spiral arm pitch angle", categories: [], unit: "deg", unit_display: "°" },
    { name: "sun_azimuth", label: "Azimuth of the Sun", categories: [], unit: "rad", unit_display: "rad" },
    { name: "ring_spacing", label: "Spacing of the rings", categories: [], unit: "dimensionless", unit_display: "" },
  ];

  // A pin as the tests write one by hand: no label and no unit served unless given (an API from before S59's follow-up).
  const pin = (name: string, value: Pin["value"], served: { label?: string; unit?: string; classes?: string[] } = {}): Pin => ({
    name, value, source: "", label: served.label ?? null, unit: served.unit ?? null, classes: served.classes ?? null,
  });
  // A template's pin by its name, from the route's own (pins.live.json): the order they are served in is not the tests'.
  const pinOf = (template: { name: string; pins: Pin[] }, name: string): Pin => {
    const found = template.pins.find((p) => p.name === name);
    if (!found) throw new Error(`${template.name} serves no pin ${name}: pins.live.json has moved and this test with it`);
    return found;
  };

  it("reads every pin /api/templates serves today, for both templates, and says each in one line", () => {
    // The gate the wire's growth runs into (S60, D219). The pins are the route's, laid in from pins.live.json; a
    // shape the parser does not know throws here, as it would in the browser, where it stops the viewer landing.
    expect(Object.keys(LIVE).sort()).toEqual(fixture.payload.templates.map((t) => t.name).sort());
    const parsed = parseTemplates(PAYLOAD);
    for (const template of parsed.templates) {
      const served = LIVE[template.name];
      expect(served.length).toBeGreaterThan(0);
      expect(template.pins.map((p) => p.name)).toEqual(served.map((p) => p.name));
      for (const [k, read] of template.pins.entries()) {
        // nothing of what was served is lost or changed in the reading
        expect(read.label).toBe(served[k].label);
        expect(read.unit).toBe(served[k].unit);
        expect(read.source).toBe(served[k].source);
        expect(read.value).toEqual(served[k].value);
        expect(read.classes).toEqual(served[k].classes ?? null);
        for (const fields of [FIELDS, []]) {
          const words = pinWords(read, fields);
          expect(words, `${template.name}.${read.name}`).toMatch(/^\S.*: \S.* \(as observed\)$/);
          expect(words).not.toMatch(/\n|\[object|undefined|NaN|null/);
          expect(words.length).toBeLessThan(160); // a line of the panel, never a dump
        }
      }
    }
  });

  it("writes the lines the panel shows for the two templates as they are served today", () => {
    const [milkyWay, ngc] = parseTemplates(PAYLOAD).templates;
    expect(milkyWay.pins.map((p) => pinWords(p, FIELDS))).toEqual([
      "Barred: yes (as observed)",
      "Angle of the bar to the Sun-centre line (a template's pin): 30° (as observed)",
      "Measured arm pieces (a template's pin): 6 rows by arm: Norma, Sct-Cen, Sgr-Car, Local, Perseus, Outer (as observed)",
    ]);
    expect(ngc.pins.map((p) => pinWords(p, FIELDS))).toEqual([
      "Barred: no (as observed)",
      "Spiral arm pitch angle: 28.9° (as observed)",
      "Arm class: flocculent (as observed)",
    ]);
  });

  it("reads each of the four shapes a pin's value has: a class, a number, a named class, a table", () => {
    const [milkyWay, ngc] = parseTemplates(PAYLOAD).templates;
    expect(pinOf(milkyWay, "bar_present")).toMatchObject({ label: "Bar present (a template's pin)", unit: null, value: true, classes: null });
    expect(pinOf(ngc, "bar_present").value).toBe(false);
    expect(pinOf(milkyWay, "sun_bar_angle")).toMatchObject({ label: "Angle of the bar to the Sun-centre line (a template's pin)", unit: "deg", value: 30, classes: null });
    expect(pinOf(ngc, "pitch_angle")).toMatchObject({ label: "Arm pitch angle (a template's pin)", unit: "deg", value: 28.9 });
    // S60 (D219): a named class with its own list of classes,
    expect(pinOf(ngc, "arm_class")).toMatchObject({ label: "Arm class (a template's pin)", unit: null, value: "flocculent", classes: ["grand_design", "multi_armed", "flocculent"] });
    // and a table: the columns with their units, the rows as served.
    const table = pinOf(milkyWay, "arm_pieces").value as PinTable;
    expect(table.columns).toEqual([
      { name: "arm", unit: null },
      { name: "beta_from", unit: "deg" },
      { name: "beta_to", unit: "deg" },
      { name: "beta_kink", unit: "deg" },
      { name: "radius_kink", unit: "kpc" },
      { name: "pitch_below", unit: "deg" },
      { name: "pitch_above", unit: "deg" },
    ]);
    expect(table.rows).toHaveLength(6);
    expect(table.rows[0]).toEqual(["Norma", 5, 54, 18, 4.46, -1, 19.5]);
    expect(table.rows.every((row) => row.length === table.columns.length)).toBe(true);
    for (const p of [...milkyWay.pins, ...ngc.pins]) expect(p.source).toMatch(/^\[verified: /); // the route's own source, not a stand-in
  });

  it("reads /api/templates as S59 answers it: a numeric pin does not stop the viewer from landing (D218 items 5-6)", () => {
    // Until S59 a pin's value was a class and anything else was refused; a template with a measured number among
    // its pins then failed to parse, and the viewer showed "Loading the model failed" in place of the galaxy.
    const p = copy();
    p.templates[1].pins = [{ name: "pitch_angle", value: 28.9, source: "[verified: ...]" }, { name: "sun_bar_angle", value: 0, source: "" }];
    expect(parseTemplates(p).templates[1].pins.map((read) => read.value)).toEqual([28.9, 0]);
  });

  it("takes a pin's label and unit as served, and a pin without them as it was: an API from before they were", () => {
    const p = copy();
    p.templates[1].pins = [
      { name: "bar_present", value: false, source: "" }, // neither key: S58, and S59 before the follow-up
      { name: "pitch_angle", label: null, unit: null, value: 28.9, source: "" },
      { name: "sun_bar_angle", label: "Angle of the bar to the Sun-centre line (a template's pin)", unit: "deg", value: 30, source: "" },
    ];
    expect(parseTemplates(p).templates[1].pins.map(({ label, unit }) => [label, unit])).toEqual([
      [null, null],
      [null, null],
      ["Angle of the bar to the Sun-centre line (a template's pin)", "deg"], // as served: nothing stripped, nothing rewritten
    ]);
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
    const SHAPE = /template ngc_4414: a pin is \{name, value: true or false, a number, one of its classes or a table of columns and rows, source\}/;
    expect(broken("bar_present")).toThrow(/template ngc_4414: pins is not a list/);
    expect(broken([{ value: false }])).toThrow(SHAPE);
    // a number that is none (JSON's null for a NaN) is no measured value, and a list is no value at all
    expect(broken([{ name: "pitch_angle", value: null, source: "" }])).toThrow(SHAPE);
    expect(broken([{ name: "pitch_angle", value: [28.9], source: "" }])).toThrow(SHAPE);
    // a pin without a source is still a pin: the words stand, the tooltip is empty
    expect(broken([{ name: "bar_present", value: false }])()).toMatchObject({ templates: [{}, { pins: [{ name: "bar_present", value: false, source: "" }] }] });
    // a label or a unit that is no text is not guessed at
    expect(broken([{ name: "pitch_angle", label: 7, unit: "deg", value: 28.9, source: "" }])).toThrow(/template ngc_4414: pin pitch_angle's label and unit are texts or absent/);
    expect(broken([{ name: "pitch_angle", label: "Arm pitch angle", unit: { name: "deg" }, value: 28.9, source: "" }])).toThrow(/label and unit are texts or absent/);
  });

  it("refuses a text that is not one of the pin's own classes: a string alone is no class (S60)", () => {
    const broken = (pinned: Record<string, unknown>) => {
      const p = copy();
      p.templates[1].pins = [{ name: "arm_class", label: "Arm class (a template's pin)", unit: null, source: "", ...pinned }];
      return () => parseTemplates(p);
    };
    const CLASSES = ["grand_design", "multi_armed", "flocculent"];
    expect(broken({ value: "flocculent", classes: CLASSES })().templates[1].pins[0]).toMatchObject({ value: "flocculent", classes: CLASSES });
    // no list of classes beside it: a digit string, a "no", any text
    expect(broken({ value: "flocculent" })).toThrow(/pin arm_class names the class "flocculent", which is not one of its classes null/);
    expect(broken({ value: "28.9" })).toThrow(/names the class "28.9"/);
    // a class the list does not hold, and a list that is no list of texts
    expect(broken({ value: "barred", classes: CLASSES })).toThrow(/names the class "barred", which is not one of its classes \["grand_design","multi_armed","flocculent"\]/);
    expect(broken({ value: "flocculent", classes: [] })).toThrow(/not one of its classes/);
    expect(broken({ value: "flocculent", classes: ["flocculent", 3] })).toThrow(/not one of its classes/);
    expect(broken({ value: "flocculent", classes: "flocculent" })).toThrow(/not one of its classes/);
    // a list of classes beside a pin that is none is not the pin's: carried nowhere
    expect(broken({ value: true, classes: CLASSES })().templates[1].pins[0].classes).toBeNull();
  });

  it("refuses a table that is not columns and whole rows (S60)", () => {
    const broken = (value: unknown) => {
      const p = copy();
      p.templates[0].pins = [{ name: "arm_pieces", label: "Measured arm pieces (a template's pin)", unit: null, value, source: "" }];
      return () => parseTemplates(p);
    };
    const columns = [{ name: "arm", unit: null }, { name: "pitch", unit: "deg" }];
    const SHAPE = /template milky_way: a pin is \{name, value: true or false, a number, one of its classes or a table of columns and rows, source\}/;
    expect((broken({ columns, rows: [["Norma", 19.5], ["Local", null]] })().templates[0].pins[0].value as PinTable).rows).toEqual([["Norma", 19.5], ["Local", null]]);
    expect((broken({ columns, rows: [] })().templates[0].pins[0].value as PinTable).rows).toEqual([]); // a table of no rows pins none
    expect(broken({ columns })).toThrow(SHAPE); // no rows
    expect(broken({ rows: [["Norma", 19.5]] })).toThrow(SHAPE); // no columns
    expect(broken({ columns, rows: [["Norma"]] })).toThrow(SHAPE); // a row shorter than the columns
    expect(broken({ columns, rows: [["Norma", 19.5, 3]] })).toThrow(SHAPE); // and one longer
    expect(broken({ columns, rows: [["Norma", [19.5]]] })).toThrow(SHAPE); // a cell that is no text and no number
    expect(broken({ columns, rows: [{ arm: "Norma", pitch: 19.5 }] })).toThrow(SHAPE); // a row that is no list
    expect(broken({ columns: ["arm", "pitch"], rows: [["Norma", 19.5]] })).toThrow(SHAPE); // columns without their units
    expect(broken({ columns: [{ name: "arm", unit: 3 }], rows: [["Norma"]] })).toThrow(SHAPE);
    expect(broken({})).toThrow(SHAPE);
    // the message quotes the pin, cut short: a table is long
    const long = { columns, rows: Array.from({ length: 200 }, (_, k) => [`arm ${k}`, k, k]) };
    expect(() => broken(long)()).toThrow(/got \{"name":"arm_pieces".{0,240}\.\.\.$/);
  });

  it("says a pin in the field declaration's own words, with none of the viewer's", () => {
    const [milkyWay, ngc] = parseTemplates(PAYLOAD).templates;
    // The published field of the pin's name comes first: its label and its categories, not the pin input's label.
    expect(pinWords(pinOf(ngc, "bar_present"), FIELDS)).toBe("Barred: no (as observed)");
    expect(pinWords(pinOf(milkyWay, "bar_present"), FIELDS)).toBe("Barred: yes (as observed)");
    // No declaration of that name (the fields not loaded yet, a model without the field): the pin's own label, as
    // served - nothing stripped from it - and yes or no.
    expect(pinWords(pinOf(ngc, "bar_present"))).toBe("Bar present (a template's pin): no (as observed)");
    expect(pinWords(pinOf(milkyWay, "bar_present"), [])).toBe("Bar present (a template's pin): yes (as observed)");
    // Neither a declaration nor a served label (an API from before S59's follow-up): the pin's name.
    expect(pinWords(pin("bar_present", false))).toBe("bar_present: no (as observed)");
    // A field that is not a two-class one does not lend its categories to a true-or-false pin.
    expect(pinWords(pin("stellar_mass_total", true), FIELDS)).toBe("Stellar mass: yes (as observed)");
  });

  it("says a measured number with the declaration's label and unit where a field has the pin's name", () => {
    const [, ngc] = parseTemplates(PAYLOAD).templates;
    // NGC 4414's pitch: the pin decides the published field of its own name, whose label and unit these are - not
    // the pin input's own "Arm pitch angle (a template's pin)".
    expect(pinWords(pinOf(ngc, "pitch_angle"), FIELDS)).toBe("Spiral arm pitch angle: 28.9° (as observed)");
    // A unit that is a word stands after a space; a dimensionless number has none.
    expect(pinWords(pin("sun_azimuth", 1.1497328186297713), FIELDS)).toBe("Azimuth of the Sun: 1.15 rad (as observed)");
    expect(pinWords(pin("stellar_mass_total", 4.75e10), FIELDS)).toBe("Stellar mass: 4.750 × 10¹⁰ M☉ (as observed)");
    expect(pinWords(pin("ring_spacing", 0.56), FIELDS)).toBe("Spacing of the rings: 0.56 (as observed)");
    // Zero is a number, not a "no".
    expect(pinWords(pin("pitch_angle", 0), FIELDS)).toBe("Spiral arm pitch angle: 0° (as observed)");
    // The declaration's unit wins over a served one that differs from it.
    expect(pinWords(pin("pitch_angle", 28.9, { label: "Arm pitch angle (a template's pin)", unit: "rad" }), FIELDS)).toBe("Spiral arm pitch angle: 28.9° (as observed)");
  });

  it("says a pin that decides a field of another name with its own served label and unit (S59's follow-up)", () => {
    const [milkyWay, ngc] = parseTemplates(PAYLOAD).templates;
    // The Milky Way's bar angle publishes sun_azimuth: no field is named sun_bar_angle. The label is the pin
    // input's as served; the unit "deg" is shown as the field declarations show that unit ("°", from any of them).
    expect(pinWords(pinOf(milkyWay, "sun_bar_angle"), FIELDS)).toBe("Angle of the bar to the Sun-centre line (a template's pin): 30° (as observed)");
    // The fields not loaded yet: the same label, and the unit as served.
    expect(pinWords(pinOf(milkyWay, "sun_bar_angle"))).toBe("Angle of the bar to the Sun-centre line (a template's pin): 30 deg (as observed)");
    expect(pinWords(pinOf(ngc, "pitch_angle"))).toBe("Arm pitch angle (a template's pin): 28.9 deg (as observed)");
    // A unit no declared field has is written as served; a dimensionless number has none.
    expect(pinWords(pin("bar_age", 5, { label: "Age of the bar (a template's pin)", unit: "Gyr" }), FIELDS)).toBe("Age of the bar (a template's pin): 5 Gyr (as observed)");
    expect(pinWords(pin("bar_strength", 0.3, { label: "Bar strength (a template's pin)", unit: "dimensionless" }), FIELDS)).toBe("Bar strength (a template's pin): 0.3 (as observed)");
    // An API from before the follow-up serves neither: the pin's name and the bare number, no unit guessed (rule B9).
    expect(pinWords(pin("sun_bar_angle", 30), FIELDS)).toBe("sun_bar_angle: 30 (as observed)");
    expect(pinWords(pin("pitch_angle", 28.9))).toBe("pitch_angle: 28.9 (as observed)");
  });

  it("says a named class as served, under the published field's label where there is one (S60, D219)", () => {
    const [, ngc] = parseTemplates(PAYLOAD).templates;
    // `arm_class` is a published field too: its label, and the class as the route serves it - the viewer has no
    // word of its own for a class (rule A9), and the declaration's categories are the same texts.
    expect(pinWords(pinOf(ngc, "arm_class"), FIELDS)).toBe("Arm class: flocculent (as observed)");
    // The fields not loaded yet: the pin's own label, as served.
    expect(pinWords(pinOf(ngc, "arm_class"))).toBe("Arm class (a template's pin): flocculent (as observed)");
    // Never rewritten: an underscore stays one.
    expect(pinWords(pin("arm_class", "grand_design", { classes: ["grand_design", "flocculent"] }), FIELDS)).toBe("Arm class: grand_design (as observed)");
  });

  it("says a table in one line: how many rows it pins and their first column, never its numbers (S60, D219)", () => {
    const [milkyWay] = parseTemplates(PAYLOAD).templates;
    const line = pinWords(pinOf(milkyWay, "arm_pieces"), FIELDS);
    expect(line).toBe("Measured arm pieces (a template's pin): 6 rows by arm: Norma, Sct-Cen, Sgr-Car, Local, Perseus, Outer (as observed)");
    expect(line).not.toMatch(/\d\.\d/); // no pitch, no radius, no angle: the rows' numbers are the model's to use
    const columns = [{ name: "arm", unit: null }, { name: "pitch", unit: "deg" }];
    const table = (rows: PinTable["rows"], cols = columns) => pin("arm_pieces", { columns: cols, rows }, { label: "Measured arm pieces" });
    expect(pinWords(table([["Norma", 19.5]]))).toBe("Measured arm pieces: 1 row by arm: Norma (as observed)");
    expect(pinWords(table([]))).toBe("Measured arm pieces: 0 rows (as observed)");
    expect(pinWords(table([[], []], []))).toBe("Measured arm pieces: 2 rows (as observed)"); // no column to list them by
    // A first column of numbers is listed as numbers; one not read as a dash.
    expect(pinWords(table([[3, 19.5], [null, 12.1], [4.4999, 1]], [{ name: "order", unit: null }, { name: "pitch", unit: "deg" }]))).toBe(
      "Measured arm pieces: 3 rows by order: 3, —, 4.5 (as observed)",
    );
    // Past TABLE_LISTED rows the rest are counted, not listed: a line, whatever the table's length.
    const many = Array.from({ length: TABLE_LISTED + 5 }, (_, k) => [`a${k}`, k] as (string | number)[]);
    expect(pinWords(table(many))).toBe(`Measured arm pieces: ${TABLE_LISTED + 5} rows by arm: ${many.slice(0, TABLE_LISTED).map((r) => r[0]).join(", ")} and 5 more (as observed)`);
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
