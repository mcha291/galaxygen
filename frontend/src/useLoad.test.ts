import { afterEach, describe, expect, it } from "vitest";

import {
  HANDOVER_MS,
  InputClock,
  ViewMark,
  beginLanding,
  beginSwap,
  endSwap,
  handOver,
  handed,
  heldLoads,
  loads,
  pendingLoads,
  swapPart,
  swapState,
  takeHanded,
} from "./useLoad";

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

  it("asks a loader's first key at once and settles every later one (S78), without an input", () => {
    const clock = new InputClock();
    clock.see(undefined, 0);
    expect(clock.wait(SETTLE, 0, "galaxy a")).toBe(0);
    // StrictMode's cleanup and re-run before the timer fires: the same first key, still at once
    expect(clock.wait(SETTLE, 1, "galaxy a")).toBe(0);
    clock.fired();
    clock.see(undefined, 500);
    expect(clock.wait(SETTLE, 500, "galaxy b")).toBe(SETTLE);
    // the first key again, after its request went out: a move like any other
    expect(clock.wait(SETTLE, 900, "galaxy a")).toBe(SETTLE);
  });

  it("asks the first key at once with an input too, and every later key by the input's clock (S78; F3 unchanged)", () => {
    const clock = new InputClock();
    clock.see("view a", 0);
    expect(clock.wait(SETTLE, 0, "tiles 1")).toBe(0);
    clock.fired();
    // the counts answer and the tiles' key moves, the input standing: the rest of the settle since the mount
    clock.see("view a", 120);
    expect(clock.wait(SETTLE, 120, "tiles 2")).toBe(130);
    // the user moves: the whole settle
    clock.see("view b", 400);
    expect(clock.wait(SETTLE, 400, "tiles 3")).toBe(SETTLE);
  });

  it("settles a second key asked before the first one's request went out", () => {
    const clock = new InputClock();
    clock.see(undefined, 0);
    expect(clock.wait(SETTLE, 0, "galaxy a")).toBe(0);
    expect(clock.wait(SETTLE, 10, "galaxy b")).toBe(SETTLE); // the key moved before the timer fired
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
    expect(swapState()).toEqual({ swapping: false, failure: null, landing: false });
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
    expect(swapState()).toEqual({ swapping: false, failure: "HTTP 400: mass_ratio out of range", landing: false });
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
    expect(swapState()).toEqual({ swapping: false, failure: null, landing: false });
    loads.drop(field);
  });
});

// S82 (#187): the whole swap holds the loaders whose keys follow another loader's answer (the star-first mode's counts
// and tiles after the bright table, the field's remainder after the tiles' threshold), and none of the camera's.
describe("a loader whose key follows another's answer (S82, #187)", () => {
  it("is part of the one publish: registered with the swap before what it follows answers, it asks on the held answer", async () => {
    const table = {};
    const tiles = {};
    const field = {};
    const published: string[] = [];
    const shown: string[] = [];
    beginSwap();
    loads.wait(table);
    loads.wait(field);
    loads.wait(tiles); // `after`: the table has not answered for this swap - it waits on the swap and asks nothing
    loads.answer(field, () => published.push("field"));
    // The table answers: held, and shown at once to the keys that follow it (useLoad's `next`), drawn with nothing.
    loads.answer(table, () => published.push("table"), null, () => shown.push("table"));
    expect(shown).toEqual(["table"]);
    expect(published).toEqual([]); // the tiles still hold the swap: no publish without them
    expect(swapState().swapping).toBe(true);
    // The tiles read the held table and take their own key, in one commit: the swap is not ended by the move.
    loads.drop(tiles);
    loads.wait(tiles);
    await tick();
    expect(swapState().swapping).toBe(true);
    loads.answer(tiles, () => published.push("tiles"));
    expect(published.sort()).toEqual(["field", "table", "tiles"]); // one publish, every dependent answer in
    expect(swapState()).toEqual({ swapping: false, failure: null, landing: false });
  });

  it("before S82 it was a second, partial update: unregistered, the swap published without it", async () => {
    const table = {};
    const field = {};
    const tiles = {};
    const published: string[] = [];
    beginSwap();
    loads.wait(table);
    loads.wait(field);
    loads.answer(field, () => published.push("field"));
    loads.answer(table, () => published.push("table"));
    expect(published.sort()).toEqual(["field", "table"]); // the swap over, the tiles not asked yet
    loads.wait(tiles);
    loads.answer(tiles, () => published.push("tiles"));
    expect(published).toEqual(["field", "table", "tiles"]); // on their own, after it: what `after` removes
  });

  it("the hook's part (swapPart): following an unanswered loader it settles the swap and asks nothing; outside a swap nothing", () => {
    const at = { swapping: true, key: "tiles", moved: false, answered: false };
    // the tiles while the table has not answered: they hold the swap, waiting on it
    expect(swapPart({ ...at, role: { after: true } })).toEqual({ free: false, after: true, settling: true });
    // the table held: they ask their own key, and hold the swap until it answers
    expect(swapPart({ ...at, role: { after: false } })).toEqual({ free: false, after: false, settling: true });
    expect(swapPart({ ...at, role: { after: false }, answered: true })).toEqual({ free: false, after: false, settling: false });
    // a key not yet named because what it follows has not answered still holds the swap (the tiles before the counts);
    // a null key otherwise holds nothing; outside a swap nothing is any of these
    expect(swapPart({ ...at, key: null, role: { after: true } }).settling).toBe(true);
    expect(swapPart({ ...at, key: null, role: { after: false } }).settling).toBe(false);
    expect(swapPart({ ...at, swapping: false, role: { after: true } })).toEqual({ free: false, after: false, settling: false });
  });
});

describe("the camera's loads in a swap (S82, #187)", () => {
  it("a view-keyed loader never holds a swap: moved by the camera, the swap publishes without it", () => {
    const field = {};
    const region = {};
    const published: string[] = [];
    const takenDown: string[] = [];
    beginSwap();
    loads.wait(field);
    loads.wait(region, { takeDown: () => takenDown.push("region") }); // its view moved since the swap began
    expect(pendingLoads()).toBe(1); // the field alone holds it
    loads.answer(field, () => published.push("field"));
    expect(published).toEqual(["field"]);
    expect(swapState().swapping).toBe(false);
    // the previous galaxy's region stars are not left under the new field (rule D1): taken down at the swap's end
    expect(takenDown).toEqual(["region"]);
    loads.answer(region, () => published.push("region"));
    expect(published).toEqual(["field", "region"]); // its own answer, on its own, when it comes
  });

  it("one that answers inside the swap is published with it, and taken down by nothing", () => {
    const field = {};
    const region = {};
    const published: string[] = [];
    const takenDown: string[] = [];
    beginSwap();
    loads.wait(field);
    loads.wait(region, { takeDown: () => takenDown.push("region") });
    loads.answer(region, () => published.push("region"));
    expect(published).toEqual([]); // held: the new galaxy's stars are not drawn over the old field
    loads.answer(field, () => published.push("field"));
    expect(published.sort()).toEqual(["field", "region"]);
    expect(takenDown).toEqual([]);
  });

  it("is free only during a swap: outside one it waits as any loader does", () => {
    const region = {};
    loads.wait(region, { takeDown: () => undefined });
    expect(pendingLoads()).toBe(1);
    loads.drop(region);
  });

  it("holds the swap while the view stands where it stood when the swap began (ViewMark, swapPart)", () => {
    const mark = new ViewMark();
    mark.see("view a", 0); // before any swap
    mark.see("view b", 1); // the swap's first render: the view it began at
    expect(mark.moved("view b")).toBe(false);
    mark.see("view b", 1);
    expect(mark.moved("view c")).toBe(true); // the camera moved during the swap
    mark.see("view c", 2); // the next swap begins where it stands
    expect(mark.moved("view c")).toBe(false);
    const at = { swapping: true, key: "region", answered: false };
    expect(swapPart({ ...at, role: { view: "view b" }, moved: false })).toEqual({ free: false, after: false, settling: true });
    expect(swapPart({ ...at, role: { view: "view c" }, moved: true })).toEqual({ free: true, after: false, settling: false });
    // a loader not keyed on the view is never freed by a move
    expect(swapPart({ ...at, role: {}, moved: true }).free).toBe(false);
  });
});

// S82 (#188): a template landing over a galaxy on screen is a swap of its own - the old picture stays, marked, until
// the template's loaders have answered - and what the old canvas's loaders were published by it is handed over to the
// new canvas's loaders of the same key, so the new canvas neither asks again nor waits blank on the wire.
describe("a template landing (S82, #188)", () => {
  it("is no swap on the app's first landing (nothing on screen), and a swap of its own over a galaxy on screen", () => {
    beginLanding(false);
    expect(swapState()).toEqual({ swapping: false, failure: null, landing: false });
    beginLanding(true);
    expect(swapState()).toEqual({ swapping: true, failure: null, landing: true });
  });

  it("keeps the old galaxy's field drawn until the new one's answers are in, then hands it to the new canvas", () => {
    const field = {}; // the old canvas's field volume, now asking the new template's arrays
    const stars = {}; // the star sample
    const drawn: string[] = ["old field", "old stars"];
    const published: [string, boolean][] = [];
    beginLanding(true);
    loads.wait(field);
    loads.wait(stars);
    // The new field answers first: held - the old field is still what is drawn (the bare stars of #188 are gone).
    loads.answer(field, (landing) => published.push(["new field", landing]));
    expect(published).toEqual([]);
    expect(drawn).toEqual(["old field", "old stars"]);
    expect(swapState()).toMatchObject({ swapping: true, landing: true });
    // The sample answers: the whole swap, told it was a landing's.
    loads.answer(stars, (landing) => published.push(["new stars", landing]));
    expect(published.sort()).toEqual([
      ["new field", true],
      ["new stars", true],
    ]);
    expect(swapState()).toEqual({ swapping: false, failure: null, landing: false });
    // The canvas is made afresh at the template's stand: the old field volume, unmounted, hands its answer over...
    const now = performance.now();
    handOver('["arrays","ngc_4414"]', "new field", now);
    // ... and the new one starts from it, asking nothing, and takes it so no other loader does.
    expect(handed('["arrays","ngc_4414"]', now)).toBe("new field");
    takeHanded('["arrays","ngc_4414"]');
    expect(handed('["arrays","ngc_4414"]', now)).toBeUndefined();
  });

  it("hands over only just after a landing's publish, and nothing past the next swap", () => {
    const stars = {};
    beginLanding(true);
    loads.wait(stars);
    loads.answer(stars, () => undefined);
    const now = performance.now();
    handOver("k", 1, now + HANDOVER_MS + 1); // an unmount long after the landing (a tab left): no part of it
    expect(handed("k", now)).toBeUndefined();
    handOver("k", 2, now);
    expect(handed("k", now + HANDOVER_MS + 1)).toBeUndefined(); // closed
    expect(handed("k", now)).toBe(2);
    beginSwap(); // the next Generate empties it
    expect(handed("k", performance.now())).toBeUndefined();
    endSwap();
  });

  it("stays a landing's through a Generate pressed during it, and makes a Generate under way moot", async () => {
    const field = {};
    const published: string[] = [];
    beginLanding(true);
    beginSwap(); // a Generate while the landing's loaders are out: the landing's camera still waits on it
    expect(swapState().landing).toBe(true);
    endSwap();
    // A Generate under way, then a landing: the landing's own swap, the Generate's failure forgotten.
    const stars = {};
    beginSwap();
    loads.wait(field);
    loads.wait(stars);
    loads.answer(field, () => published.push("generated field, failed"), "HTTP 400");
    expect(swapState().failure).toBe("HTTP 400");
    beginLanding(true);
    expect(swapState()).toEqual({ swapping: true, failure: null, landing: true });
    loads.drop(field); // its key moves to the template's query: what it held for the generated one is dropped
    await tick();
    expect(published).toEqual([]);
    loads.drop(stars);
  });
});
