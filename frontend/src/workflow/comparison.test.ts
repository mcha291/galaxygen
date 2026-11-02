import * as flow from "@interface/flow.js";
import { describe, expect, it } from "vitest";

import type { Query } from "../api";
import { FILTER_SET_NAMES } from "../galaxy/filters";
import { defaultSource, paneExposure, paneGalaxy, sourceItems, sourceSet, templateQueryOf, trackShown } from "./comparison";
import type { FlowState, InputDecl } from "./logic";
import live from "./pins.live.json";
import fixture from "./templates.fixture.json";
import { EVENTS_INPUT, TEMPLATE_KEY, parseTemplates } from "./templates";
import { landOn, queryOf } from "./useWorkflow";

// The fixture's two templates with the route's own pins (as templates.test.ts reads them), over a flow built by flow.js.
const LIVE = live.pins as unknown as Record<string, Record<string, unknown>[]>;
const { templates } = parseTemplates({ ...fixture.payload, templates: fixture.payload.templates.map((t) => ({ ...t, pins: LIVE[t.name] })) });
const [milkyWay, ngc] = templates;
const RANGES: Record<string, [number, number, number]> = {
  halo_mass: [1e11, 1e13, 1],
  disc_spin: [0.005, 0.05, 1],
  halo_assembly_z: [0.5, 5, 1],
  baryon_retention: [0.05, 0.5, 1],
  infall_timescale: [1, 14, 4],
  inside_out_index: [0, 3, 4],
  migration_efficiency: [0, 8, 4],
};
const SEEDS: Record<string, number> = { world_seed: 1, pattern_seed: 3, systems_seed: 5, planets_seed: 6, texture_seed: 3 };

function catalogue(model = "azimuthal"): FlowState["cat"] {
  const cps = [1, 2, 3, 4, 5, 6].map((n) => ({ n, name: `cp${n}`, stages: [`s${n}`] }));
  const stages = { model, order: cps.map((c) => c.stages[0]), checkpoints: cps };
  const controls: InputDecl[] = Object.entries(RANGES).map(([name, [lo, hi, checkpoint]]) => ({
    name, label: "", kind: "control", about: "", checkpoint, default: milkyWay.inputs.controls[name], lo, hi,
  }));
  const seeds: InputDecl[] = Object.entries(SEEDS).map(([name, checkpoint]) => ({ name, label: "", kind: "seed", about: "", checkpoint, default: 0 }));
  const events: InputDecl[] = [{ name: EVENTS_INPUT, label: "", kind: "events", about: "", checkpoint: 2, default: milkyWay.inputs.mergers }];
  return (flow.initial(flow.catalogue(stages, { controls, seeds, events })) as FlowState).cat;
}
const cat = catalogue();
const landed = (t: typeof ngc) => queryOf(landOn(flow.initial(cat) as FlowState, t), t.model, t);
const mwQuery = landed(milkyWay);

describe("the comparison's second pane: what it draws (T16, S83)", () => {
  it("another template is asked with its landing's own query - the same request, so the bundles answer it", () => {
    const q = templateQueryOf(cat, ngc)!;
    expect(q).toEqual(landed(ngc));
    expect(q[TEMPLATE_KEY]).toBe("ngc_4414");
    expect(q.world_seed).toBe(4414);
    expect(templateQueryOf(catalogue("other"), ngc)).toBeNull(); // another model's catalogue: not laid on it
  });

  it("offers the galaxy shown, every template it is not, the draft and a picture; NGC 4414 beside the Milky Way first", () => {
    const keys = (edited: boolean, ready = false, previous = false) =>
      sourceItems(templates, milkyWay, edited, { ready, previous }, () => true).map((i) => `${i.key}${i.disabled ? " (off)" : ""}`);
    expect(keys(false)).toEqual(["shown", "template:ngc_4414", "draft (off)", "picture"]);
    expect(keys(true, true)).toEqual(["shown", "template:milky_way", "template:ngc_4414", "draft", "picture"]);
    expect(keys(false, false, true)).toEqual(["shown", "template:ngc_4414", "draft", "picture"]);
    const label = (ready: boolean, previous: boolean) => sourceItems(templates, milkyWay, false, { ready, previous }, () => true).find((i) => i.key === "draft")!.label;
    expect([label(false, false), label(true, false), label(true, true), label(false, true)]).toEqual(["draft", "draft", "draft", "before Generate"]);
    expect(sourceItems(templates, milkyWay, false, { ready: false, previous: false }, (m) => m !== "azimuthal")[1].disabled).toBe(true);
    expect(defaultSource(templates, milkyWay, false)).toEqual({ kind: "template", name: "ngc_4414" });
    expect(defaultSource([milkyWay], milkyWay, false)).toEqual({ kind: "shown" });
  });

  it("a Generate trades the panes: the draft drawn beside goes left, and the pane takes the galaxy it replaced", () => {
    const draft: Query = { ...mwQuery, world_seed: 77 };
    const at = (d: Query | null, previous: Query | null, shown: Query) => ({
      templates, shown: { query: shown, template: milkyWay, edited: shown !== mwQuery }, draft: d, previous, catalogueOf: () => cat,
    });
    // Before: the Milky Way shown, its draft (another world seed) in the pane.
    let track = { generation: 0, selection: 1, query: mwQuery as Query | null, previous: null as Query | null };
    expect(paneGalaxy({ kind: "draft" }, at(draft, track.previous, mwQuery))).toEqual({ query: draft, template: milkyWay, label: "draft of Milky Way" });
    // Generate: the draft is the galaxy shown, the draft is clean, and the pane draws the one it replaced.
    track = trackShown(track, { generation: 1, selection: 1, query: draft });
    expect(trackShown(track, { generation: 1, selection: 1, query: draft })).toBe(track); // a render made twice
    expect(track.previous).toBe(mwQuery);
    expect(paneGalaxy({ kind: "draft" }, at(null, track.previous, draft))).toEqual({ query: mwQuery, template: milkyWay, label: "before the last Generate" });
    // A landing is a new galaxy, not an edit: nothing before it is offered.
    track = trackShown(track, { generation: 1, selection: 2, query: landed(ngc) });
    expect(track.previous).toBeNull();
    expect("none" in paneGalaxy({ kind: "draft" }, at(null, null, mwQuery))).toBe(true);
  });

  it("each pane its own set: a template's own, the galaxy shown through the next set, the draft through the left's", () => {
    expect(sourceSet({ kind: "template", name: "ngc_4414" }, ngc, "hoo", FILTER_SET_NAMES)).toBe(ngc.filters);
    const next = FILTER_SET_NAMES[(FILTER_SET_NAMES.indexOf("rgb") + 1) % FILTER_SET_NAMES.length];
    expect(sourceSet({ kind: "shown" }, milkyWay, "rgb", FILTER_SET_NAMES)).toBe(next);
    expect(next).not.toBe("rgb");
    expect(sourceSet({ kind: "draft" }, milkyWay, "rgb", FILTER_SET_NAMES)).toBe("rgb");
    expect(paneGalaxy({ kind: "shown" }, { templates, shown: { query: mwQuery, template: milkyWay, edited: false }, draft: null, previous: null, catalogueOf: () => cat })).toEqual({
      query: mwQuery, template: milkyWay, label: "Milky Way",
    });
  });

  it("one exposure slider: the right pane at its template's default moved by the stops the left's has moved", () => {
    // Today's map is empty (every template starts at 0 stops): the right pane is drawn at the left's exposure.
    expect(paneExposure(0.75, "milky_way", "ngc_4414")).toBe(0.75);
    // With defaults of their own, the user's move is carried, not the left template's default.
    const map = { milky_way: -0.5, ngc_4414: 1.5 };
    expect(paneExposure(0.25, "milky_way", "ngc_4414", map)).toBe(2.25);
    expect(paneExposure(-0.5, "milky_way", "milky_way", map)).toBe(-0.5);
  });
});
