import { afterEach, describe, expect, it } from "vitest";

import { beginSwap, carriedFor, carry, endSwap } from "./useLoad";

// S106 (docs/BRIEF.md "Known defects" (i)): a canvas made afresh inside a swap - the look switched while a generation
// is pending moves the stand - starts its loaders from what the unmounted ones showed, not from nothing until the swap
// publishes. The browser's side is e2e/switch/lookswitch.probe.ts.
describe("what a loader showed in a swap, for a loader of its key made afresh in it (S106)", () => {
  afterEach(() => endSwap());

  it("keeps a value only while a swap is under way, and forgets it when the swap ends or another begins", () => {
    carry("k", 1);
    expect(carriedFor("k")).toBeUndefined(); // no swap: nothing is kept
    beginSwap();
    carry("k", 2);
    expect(carriedFor<number>("k")).toBe(2);
    expect(carriedFor("other")).toBeUndefined();
    beginSwap(); // a Generate over a Generate: what the last one showed is asked again by its loaders' effects
    expect(carriedFor("k")).toBeUndefined();
    carry("k", 3);
    endSwap();
    expect(carriedFor("k")).toBeUndefined();
  });
});
