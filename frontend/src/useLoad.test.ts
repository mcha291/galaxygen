import { afterEach, describe, expect, it } from "vitest";

import { InputClock, beginSwap, endSwap, heldLoads, loads, pendingLoads, swapState } from "./useLoad";

// The settle's clock (S76, D240 F3; the review's G3), driven as useLoad drives it: `see` on every render with the
// loader's input, `wait` when a new key is asked. The times are the page's clock, ms.
describe("the settle's clock", () => {
  const SETTLE = 250;

  it("restarts the settle on every change of the input: a user still moving waits", () => {
    const clock = new InputClock();
    clock.see("view a", 0);
    expect(clock.wait(SETTLE, 0)).toBe(SETTLE);
    // Each view report moves the input and the key in one render: every key asked waits the whole settle again.
    for (const [at, view] of [[100, "view b"], [200, "view c"], [300, "view d"]] as const) {
      clock.see(view, at);
      expect(clock.wait(SETTLE, at)).toBe(SETTLE);
    }
    // A key moved 100 ms after the last report waits the rest of it.
    clock.see("view d", 400);
    expect(clock.wait(SETTLE, 400)).toBe(150);
  });

  it("asks at once for a key an answer moved after the user has been still, and the rest of the settle before", () => {
    const clock = new InputClock();
    clock.see("view a", 0);
    clock.see("view a", 120); // the counts answer, the tiles' key moves, the input stands
    expect(clock.wait(SETTLE, 120)).toBe(130);
    clock.see("view a", 600); // the render names the stars' layer: the threshold moves, the input stands
    expect(clock.wait(SETTLE, 600)).toBe(0);
  });

  it("without an input every key waits the whole settle, as before F3", () => {
    const clock = new InputClock();
    for (const at of [0, 50, 1000, 5000]) {
      clock.see(undefined, at);
      expect(clock.wait(SETTLE, at)).toBe(SETTLE);
    }
  });

  it("does not count an input's first naming after null as a move: the cells waited on an answer, not on the user", () => {
    const clock = new InputClock();
    clock.see(null, 0); // the bright table not yet answered: no cells to name
    clock.see("cells 1", 900); // its layout arrives, the cells are named
    expect(clock.wait(SETTLE, 900)).toBe(0);
    clock.see("cells 2", 1000); // a move of the user's
    expect(clock.wait(SETTLE, 1000)).toBe(SETTLE);
    clock.see(null, 1100); // the mode left: the cells unnamed again, itself a move
    clock.see("cells 2", 1200);
    expect(clock.wait(SETTLE, 1200)).toBe(150);
  });
});

// The swap (S68, rule D1 as amended: never half one input set and half another), driven through the same three
// moves useLoad makes - wait on a key, answer, drop - with plain tokens and publications in place of React state.
const tick = () => new Promise<void>((resolve) => queueMicrotask(resolve));

afterEach(async () => {
  endSwap();
  await tick();
});

describe("outside a swap", () => {
  it("publishes every answer as it arrives: the landing and every pan are as they were", () => {
    const a = {};
    const published: string[] = [];
    loads.wait(a);
    expect(pendingLoads()).toBe(1);
    loads.answer(a, () => published.push("a"));
    expect(published).toEqual(["a"]);
    expect(pendingLoads()).toBe(0);
    expect(swapState().swapping).toBe(false);
  });
});

describe("a Generate's swap", () => {
  it("holds the first answer until the second arrives, then publishes both together", () => {
    const stars = {};
    const field = {};
    const published: string[] = [];
    beginSwap();
    loads.wait(stars);
    loads.wait(field);
    loads.answer(stars, () => published.push("stars"));
    expect(published).toEqual([]); // held: the old field is not drawn under the new stars
    expect(heldLoads()).toBe(1);
    expect(swapState().swapping).toBe(true);
    loads.answer(field, () => published.push("field"));
    expect(published.sort()).toEqual(["field", "stars"]);
    expect(heldLoads()).toBe(0);
    expect(swapState()).toEqual({ swapping: false, failure: null });
  });

  it("with one loader asking, its answer completes the swap at once", () => {
    const moved = {};
    const published: string[] = [];
    beginSwap();
    loads.wait(moved);
    loads.answer(moved, () => published.push("moved"));
    expect(published).toEqual(["moved"]);
  });

  it("counts a failure as answered, so the others publish, and remembers it as the swap's failure", () => {
    const stars = {};
    const field = {};
    const published: string[] = [];
    beginSwap();
    loads.wait(stars);
    loads.wait(field);
    loads.answer(stars, () => published.push("stars"));
    loads.answer(field, () => published.push("field failed"), "HTTP 400: mass_ratio out of range");
    expect(published.sort()).toEqual(["field failed", "stars"]);
    expect(swapState()).toEqual({ swapping: false, failure: "HTTP 400: mass_ratio out of range" });
  });

  it("drops what a loader held when its key moves again, and does not end the swap inside the commit", async () => {
    const stars = {};
    const field = {};
    const published: string[] = [];
    beginSwap();
    loads.wait(stars);
    loads.wait(field);
    loads.answer(stars, () => published.push("stars, first key"));
    loads.drop(stars); // the key moved: the held answer is for a query no longer asked
    loads.wait(stars); // ... and the same commit asks again
    await tick();
    expect(swapState().swapping).toBe(true);
    loads.answer(field, () => published.push("field"));
    expect(published).toEqual([]);
    loads.answer(stars, () => published.push("stars"));
    expect(published.sort()).toEqual(["field", "stars"]);
  });

  it("ends at a landing: what is held is published and the failure forgotten", () => {
    const stars = {};
    const field = {};
    const published: string[] = [];
    beginSwap();
    loads.wait(stars);
    loads.wait(field);
    loads.answer(stars, () => published.push("stars"), "failed");
    endSwap();
    expect(published).toEqual(["stars"]);
    expect(swapState()).toEqual({ swapping: false, failure: null });
    loads.drop(field);
  });
});
