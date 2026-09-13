import * as flow from "@interface/flow.js";
import { describe, expect, it } from "vitest";

import {
  type FlowState,
  type InputDecl,
  drawSeed,
  firstDifference,
  formatNumber,
  formatPower,
  fromSlider,
  isLog,
  reopen,
  rerollCost,
  runHash,
  statusOf,
  toSlider,
} from "./logic";

const halo: InputDecl = { name: "halo_mass", label: "", kind: "control", about: "", checkpoint: 1, default: 1.1e12, lo: 1e11, hi: 1e13 };
const spin: InputDecl = { name: "disc_spin", label: "", kind: "control", about: "", checkpoint: 1, default: 0.0173, lo: 0.005, hi: 0.05 };

function session(): FlowState {
  const cps = [1, 2, 3, 4, 5, 6].map((n) => ({ n, name: `cp${n}`, stages: [`s${n}`] }));
  const stages = { model: "simple", order: cps.map((c) => c.stages[0]), checkpoints: cps };
  const seed = (n: number) => ({ name: `seed_${n}`, label: "", kind: "seed", about: "", checkpoint: n, default: 0 });
  const inputs = { controls: [halo, spin], seeds: [1, 2, 3, 4, 5, 6].map(seed), events: [] };
  return flow.initial(flow.catalogue(stages, inputs)) as FlowState;
}

describe("statusOf", () => {
  it("walks locked, editing, next and blocked", () => {
    let s = session();
    s = flow.confirm(flow.confirm(s)) as FlowState; // 1 and 2 confirmed, editing 3
    expect([1, 2, 3, 4, 5].map((n) => statusOf(s, n))).toEqual(["locked", "locked", "editing", "blocked", "blocked"]);
    s = { ...s, current: 1 };
    expect(statusOf(s, 3)).toBe("next");
  });
});

describe("reopen", () => {
  it("names every later confirmation it throws away", () => {
    const s = flow.confirm(flow.confirm(flow.confirm(session()))) as FlowState;
    const { state, discarded } = reopen(s, 1);
    expect(discarded).toEqual([2, 3]);
    expect(state.confirmed).toBe(0);
    expect(state.current).toBe(1);
  });

  it("discards nothing when it is the last confirmed one", () => {
    const s = flow.confirm(flow.confirm(session())) as FlowState;
    expect(reopen(s, 2).discarded).toEqual([]);
  });
});

describe("rerollCost", () => {
  it("is every later checkpoint", () => {
    expect(rerollCost(session(), 4)).toEqual([5, 6]);
    expect(rerollCost(session(), 6)).toEqual([]);
  });
});

describe("drawSeed", () => {
  it("is a non-negative integer", () => {
    expect(drawSeed(() => 0)).toBe(0);
    const s = drawSeed(() => 0.999999);
    expect(Number.isInteger(s) && s >= 0 && s < 2 ** 31).toBe(true);
  });
});

describe("firstDifference", () => {
  it("is where the stage lists part", () => {
    const a = [{ n: 1, name: "", stages: ["halo"], inputs: [] }, { n: 2, name: "", stages: ["sfh", "chemistry"], inputs: [] }];
    const b = [{ n: 1, name: "", stages: ["halo"], inputs: [] }, { n: 2, name: "", stages: ["sfh", "chemistry_dtd"], inputs: [] }];
    expect(firstDifference(a, b)).toBe(2);
    expect(firstDifference(a, a)).toBeNull();
  });
});

describe("sliders", () => {
  it("drags two decades in log space and one in linear", () => {
    expect(isLog(halo)).toBe(true);
    expect(isLog(spin)).toBe(false);
    expect(fromSlider(halo, 500)).toBeCloseTo(1e12, -8);
    expect(fromSlider(spin, 500)).toBeCloseTo(0.0275, 6);
  });

  it("round-trips the default and pins the ends to the published bounds", () => {
    expect(fromSlider(halo, toSlider(halo, 1.1e12)) / 1.1e12).toBeCloseTo(1, 2);
    expect(fromSlider(halo, 0)).toBe(1e11);
    expect(fromSlider(halo, 1000)).toBe(1e13);
  });
});

describe("runHash", () => {
  it("is six hex digits, independent of key order, and moves with any input", () => {
    const a = runHash({ model: "simple", halo_mass: 1.1e12, world_seed: 0 });
    expect(a).toMatch(/^[0-9a-f]{6}$/);
    expect(runHash({ world_seed: 0, halo_mass: 1.1e12, model: "simple" })).toBe(a);
    expect(runHash({ model: "simple", halo_mass: 1.1e12, world_seed: 1 })).not.toBe(a);
  });
});

describe("formatPower", () => {
  it("writes decades as bare powers, and small ones plainly", () => {
    expect(formatPower(1e12)).toBe("10¹²");
    expect(formatPower(1e-5)).toBe("10⁻⁵");
    expect(formatPower(100)).toBe("100");
  });
});

describe("formatNumber", () => {
  it("writes large and small magnitudes as powers of ten", () => {
    expect(formatNumber(1.1e12)).toBe("1.10 × 10¹²");
    expect(formatNumber(2.5e-4)).toBe("2.50 × 10⁻⁴");
  });

  it("uses a real minus sign", () => {
    expect(formatNumber(-0.04861)).toBe("−0.0486");
  });

  it("leaves ordinary numbers plain", () => {
    expect(formatNumber(0.0173)).toBe("0.0173");
    expect(formatNumber(7)).toBe("7");
  });
});
