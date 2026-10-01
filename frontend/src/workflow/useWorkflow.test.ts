import * as flow from "@interface/flow.js";
import { describe, expect, it } from "vitest";

import { type FlowState, type InputDecl, reopen, statusOf } from "./logic";
import { DEFAULT_MODEL, EDIT_VIEW, generateDefault, isGenerated, settleView } from "./useWorkflow";

describe("the viewer's starting model", () => {
  it("is the azimuthal model, the API's and the tests' default since S46 (D197)", () => {
    expect(DEFAULT_MODEL).toBe("azimuthal");
  });
});

// A fresh flow over a small fake catalogue, built by flow.js itself (as logic.test.ts does).
const halo: InputDecl = { name: "halo_mass", label: "", kind: "control", about: "", checkpoint: 1, default: 1.1e12, lo: 1e11, hi: 1e13 };

function fresh(): FlowState {
  const cps = [1, 2, 3, 4, 5, 6].map((n) => ({ n, name: `cp${n}`, stages: [`s${n}`] }));
  const stages = { model: "azimuthal", order: cps.map((c) => c.stages[0]), checkpoints: cps };
  const seed = (n: number) => ({ name: `seed_${n}`, label: "", kind: "seed", about: "", checkpoint: n, default: 0 });
  const inputs = { controls: [halo], seeds: [1, 2, 3, 4, 5, 6].map(seed), events: [] };
  return flow.initial(flow.catalogue(stages, inputs)) as FlowState;
}

describe("the first load lands on the default galaxy (D198)", () => {
  it("confirms every checkpoint through flow.confirm: confirmed = last, current = last", () => {
    const s = generateDefault(fresh());
    expect(s.confirmed).toBe(6);
    expect(s.current).toBe(6);
    expect(isGenerated(s)).toBe(true);
    expect([1, 2, 3, 4, 5, 6].map((n) => statusOf(s, n))).toEqual(Array(6).fill("locked"));
  });

  it("is exactly the state six clicks of Confirm & lock reach, at the published defaults", () => {
    let clicked = fresh();
    for (let k = 0; k < 6; k += 1) clicked = flow.confirm(clicked) as FlowState;
    const s = generateDefault(fresh());
    expect(s.confirmed).toBe(clicked.confirmed);
    expect(s.current).toBe(clicked.current);
    expect(s.values).toEqual(fresh().values);
    expect(flow.query(s)).toEqual(flow.query(clicked));
  });

  it("a fresh flow is not generated", () => {
    expect(isGenerated(fresh())).toBe(false);
    expect(isGenerated(null)).toBe(false);
  });
});

describe("Edit galaxy", () => {
  it("switches to the Preview and leaves every confirmation in place", () => {
    const s = generateDefault(fresh());
    const view = settleView(EDIT_VIEW, isGenerated(s));
    expect(view).toBe("preview"); // no longer sent straight back to the Galaxy tab
    expect(s.confirmed).toBe(6);
    expect(isGenerated(s)).toBe(true);
  });

  it("reopening a checkpoint still discards every later one, and closes the Galaxy tab", () => {
    const s = generateDefault(fresh());
    const { state, discarded } = reopen(s, 3);
    expect(discarded).toEqual([4, 5, 6]);
    expect(state.confirmed).toBe(2);
    expect(state.current).toBe(3);
    expect(settleView("galaxy", isGenerated(state))).toBe("preview");
    expect(settleView("science", isGenerated(state))).toBe("science");
  });
});
