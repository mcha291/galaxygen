import * as flow from "@interface/flow.js";
import { describe, expect, it } from "vitest";

import type { FlowState, InputDecl } from "./logic";
import { parseTemplates } from "./templates";
import fixture from "./templates.fixture.json";
import { DEFAULT_MODEL, carry, dirtyGroupsOf, generated, isDirty, landOn, queryOf, resetDraft } from "./useWorkflow";

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

  it("is asked for exactly as before V9: the template's inputs, the model and template=", () => {
    const s = session(ngc);
    expect(shownQuery(s)).toEqual({ ...(flow.query(landOn(fresh(), ngc)) as Record<string, unknown>), model: "azimuthal", template: "ngc_4414" });
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
