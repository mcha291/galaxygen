import * as flow from "@interface/flow.js";
import { ApiError } from "@interface/transport.js";
import { describe, expect, it } from "vitest";

import { type FlowState, type InputDecl, reopen } from "./logic";
import fixture from "./templates.fixture.json";
import { EVENTS_INPUT, applyTemplate, isEdited, parseTemplates, readTemplates, switcherItems, templateLabel, templateOf, thumbnailOf } from "./templates";
import { generateDefault, isGenerated, landOn } from "./useWorkflow";

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
const SEEDS: Record<string, number> = { world_seed: 1, pattern_seed: 3, systems_seed: 5, planets_seed: 6 };

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
    expect(ngc.inputs.seeds).toEqual({ world_seed: 4414, pattern_seed: 4414, systems_seed: 4414, planets_seed: 4414 });
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
    expect(ngc.pins).toEqual([]);
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
