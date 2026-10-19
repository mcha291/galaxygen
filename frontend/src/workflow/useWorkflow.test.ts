import * as flow from "@interface/flow.js";
import { describe, expect, it } from "vitest";

import { type FlowState, type InputDecl, fromSlider, runHash, toSlider } from "./logic";
import { parseTemplates } from "./templates";
import fixture from "./templates.fixture.json";
import { DEFAULT_MODEL, carry, dirtyGroupsOf, generated, isDirty, isLoading, landOn, queryOf, resetDraft } from "./useWorkflow";
import { valueAt } from "./Workflow";

describe("the viewer's starting model", () => {
  it("is the azimuthal model, the API's and the tests' default since S46 (D197)", () => {
    expect(DEFAULT_MODEL).toBe("azimuthal");
  });
});

// A fresh draft over a small catalogue with the API's input names, built by flow.js itself (as templates.test.ts
// does): halo_mass in the first group, a seed in every group, two in the pattern's (S55).
const { templates } = parseTemplates({ ...fixture.payload, templates: fixture.payload.templates.map((t) => ({ ...t, pins: [] })) });
const [milkyWay, ngc] = templates;
const milky = milkyWay.inputs.controls;

function fresh(model = "azimuthal"): FlowState {
  const cps = [1, 2, 3, 4, 5, 6].map((n) => ({ n, name: `cp${n}`, stages: [`s${n}`] }));
  const stages = { model, order: cps.map((c) => c.stages[0]), checkpoints: cps };
  const control = (name: string, checkpoint: number, lo: number, hi: number): InputDecl => ({
    name, label: "", kind: "control", about: "", checkpoint, default: milky[name], lo, hi,
  });
  const controls = [
    control("halo_mass", 1, 1e11, 1e13), control("disc_spin", 1, 0.005, 0.05), control("halo_assembly_z", 1, 0.5, 5),
    control("baryon_retention", 1, 0.05, 0.5), control("infall_timescale", 4, 1, 14), control("inside_out_index", 4, 0, 3),
    control("migration_efficiency", 4, 0, 8),
  ];
  const seed = (name: string, checkpoint: number): InputDecl => ({ name, label: "", kind: "seed", about: "", checkpoint, default: 0 });
  const seeds = [seed("world_seed", 1), seed("pattern_seed", 3), seed("texture_seed", 3), seed("systems_seed", 5), seed("planets_seed", 6)];
  const events: InputDecl[] = [{ name: "mergers", label: "", kind: "events", about: "", checkpoint: 2, default: milkyWay.inputs.mergers }];
  return flow.initial(flow.catalogue(stages, { controls, seeds, events })) as FlowState;
}

/** The viewer as the hook holds it: a draft and its model, the galaxy shown, the template chosen. */
function session(template = ngc) {
  const landed = landOn(fresh(template.model), template);
  return { draft: landed, model: template.model, shown: generated(landed, template.model), template };
}
type Session = ReturnType<typeof session>;
const draftQuery = (s: Session) => queryOf(s.draft, s.model, s.template);
const shownQuery = (s: Session) => queryOf(s.shown.state, s.shown.model, s.template);
const dirty = (s: Session) => isDirty(draftQuery(s), shownQuery(s));
const groups = (s: Session) => [...dirtyGroupsOf(s.draft, s.shown.state)];
const edit = (s: Session, fn: (d: FlowState) => FlowState): Session => ({ ...s, draft: fn(s.draft) });
const generate = (s: Session): Session => (dirty(s) ? { ...s, shown: generated(s.draft, s.model) } : s);
const reset = (s: Session): Session => ({ ...s, draft: resetDraft(s.draft.cat, s.template), model: s.template.model });

describe("a template landing (rule D1 as amended, D232)", () => {
  it("is clean: the draft is the galaxy shown, every group unmarked", () => {
    for (const t of templates) {
      const s = session(t);
      expect(dirty(s)).toBe(false);
      expect(groups(s)).toEqual([]);
    }
  });

  it("is asked for exactly as the landing always was: milky_way's query, pinned to the letter and to its hash", () => {
    const s = session(milkyWay);
    // The fixture's milky_way (templates.fixture.json, whose Sagittarius is an older one than the route serves):
    // the query the landing builds from it, to the letter, and its run hash. The live template's landing read
    // e673d8 in the header at S68's walk; the picture test holds the frames, this the code that builds the query.
    expect(shownQuery(s)).toEqual({
      halo_mass: 1.1e12, disc_spin: 0.0173, halo_assembly_z: 1.66, baryon_retention: 0.35,
      infall_timescale: 7, inside_out_index: 1, migration_efficiency: 3.6,
      world_seed: 0, pattern_seed: 0, texture_seed: 0, systems_seed: 0, planets_seed: 0,
      mergers: JSON.stringify(milkyWay.inputs.mergers),
      model: "azimuthal", template: "milky_way",
    });
    expect(runHash(shownQuery(s))).toBe("7c6a54");
  });
});

describe("an edit", () => {
  it("dirties the draft and marks its group alone", () => {
    const s = edit(session(), (d) => flow.setValue(d, "halo_mass", 2e12) as FlowState);
    expect(dirty(s)).toBe(true);
    expect(groups(s)).toEqual([1]);
    const both = edit(s, (d) => flow.setValue(d, "infall_timescale", 5) as FlowState);
    expect(groups(both)).toEqual([1, 4]);
  });

  it("does not move the shown query: every view still draws the galaxy on screen", () => {
    const before = session();
    const s = edit(before, (d) => flow.setValue(d, "mergers", [{ time: 5, mass_ratio: 0.1, gas_fraction: 0.2 }]) as FlowState);
    expect(shownQuery(s)).toEqual(shownQuery(before));
    expect(groups(s)).toEqual([2]);
  });

  it("undone, is clean again", () => {
    const s = edit(edit(session(), (d) => flow.setValue(d, "halo_mass", 2e12) as FlowState), (d) => flow.setValue(d, "halo_mass", ngc.inputs.controls.halo_mass) as FlowState);
    expect(dirty(s)).toBe(false);
  });

  it("a reroll dirties its group only, and only the seed named", () => {
    const s = edit(session(), (d) => flow.reroll(d, ["texture_seed"], () => 7) as FlowState);
    expect(groups(s)).toEqual([3]);
    expect([s.draft.values.texture_seed, s.draft.values.pattern_seed]).toEqual([7, ngc.inputs.seeds.pattern_seed]);
  });
});

describe("Generate", () => {
  it("makes the draft the galaxy shown, whole, and is clean after", () => {
    const edited = edit(session(), (d) => flow.reroll(flow.setValue(d, "halo_mass", 2e12), ["systems_seed"], () => 7) as FlowState);
    const s = generate(edited);
    expect(dirty(s)).toBe(false);
    expect(groups(s)).toEqual([]);
    expect(shownQuery(s)).toEqual(draftQuery(edited));
    expect(shownQuery(s)).toMatchObject({ halo_mass: 2e12, systems_seed: 7, template: "ngc_4414" }); // the pins still ride
  });

  it("does nothing while the draft is the galaxy shown", () => {
    const s = session();
    expect(generate(s)).toBe(s);
  });
});

describe("Reset to template", () => {
  it("returns every input to the template's and is clean, without a generate", () => {
    const edited = edit(session(), (d) => flow.reroll(flow.setValue(d, "disc_spin", 0.03), ["world_seed"], () => 7) as FlowState);
    const s = reset(edited);
    expect(dirty(s)).toBe(false);
    expect(s.draft.values).toEqual(landOn(fresh(), ngc).values);
  });

  it("after a generate, returns the inputs and not the galaxy: dirty until the next generate lands on the template", () => {
    const shown = generate(edit(session(), (d) => flow.setValue(d, "halo_mass", 2e12) as FlowState));
    const s = reset(shown);
    expect(shownQuery(s)).toEqual(shownQuery(shown)); // the galaxy on screen is still the generated one
    expect(groups(s)).toEqual([1]);
    expect(shownQuery(generate(s))).toEqual(shownQuery(session()));
  });

  it("without a template, returns the published defaults", () => {
    expect(resetDraft(fresh().cat, null).values).toEqual(fresh().values);
  });
});

describe("a model switch", () => {
  it("carries every input both models share, and moves nothing on screen", () => {
    const s = edit(session(), (d) => flow.setValue(d, "halo_mass", 2e12) as FlowState);
    const other = fresh("basic");
    const carried = { ...s, draft: carry(other, s.draft), model: "basic" };
    expect(carried.draft.cat).toBe(other.cat);
    expect(carried.draft.values).toEqual(s.draft.values);
    expect(dirty(carried)).toBe(true);
    expect(shownQuery(carried)).toEqual(shownQuery(s));
    expect(generate(carried).shown.model).toBe("basic");
  });
});

describe("a slider moved and put back (F4)", () => {
  const halo: InputDecl = { name: "halo_mass", label: "", kind: "control", about: "", checkpoint: 1, default: 1.1e12, lo: 1e11, hi: 1e13 };

  it("is the exact value of the galaxy on screen again, not its four-figure rounding", () => {
    const shownValue = 1.1e12;
    const at = toSlider(halo, shownValue);
    expect(fromSlider(halo, at)).not.toBe(shownValue); // the trap: the position alone rounds
    expect(valueAt(halo, at, [shownValue, 9e11])).toBe(shownValue);
    const s = edit(edit(session(milkyWay), (d) => flow.setValue(d, "halo_mass", fromSlider(halo, at + 40)) as FlowState),
      (d) => flow.setValue(d, "halo_mass", valueAt(halo, at, [shownValue])) as FlowState);
    expect(dirty(s)).toBe(false);
  });

  it("is the template's exact value at the template's position, and the rounded one elsewhere", () => {
    expect(valueAt(halo, toSlider(halo, 9.0e11), [2e12, 9.0e11])).toBe(9.0e11);
    expect(valueAt(halo, 600, [undefined, null])).toBe(fromSlider(halo, 600));
  });
});

describe("Generate while another model's inputs are loading (F5)", () => {
  it("is refused: the draft is still the other model's", () => {
    const s = session();
    expect(isLoading(s.draft, "basic")).toBe(true);
    expect(isLoading(s.draft, "azimuthal")).toBe(false);
    expect(isLoading(null, "basic")).toBe(false);
  });
});
