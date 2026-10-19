import { afterEach, describe, expect, it } from "vitest";

import { beginSwap, endSwap, heldLoads, loads, pendingLoads, swapState } from "./useLoad";

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
