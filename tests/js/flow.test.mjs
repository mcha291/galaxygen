// Rule D1 as amended (D232), asserted against the real declarations.
//
// The catalogue comes from a live /api/stages and /api/inputs, dumped by the
// pytest wrapper (tests/test_viewer.py) into the file named by $GALAXY_FIXTURE.
// A fixture written by hand here would drift from the registry silently, which
// is the failure the per-model discipline exists to prevent one level down.
//
//   uv run pytest tests/test_viewer.py      # the way to run this

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
  FlowError, catalogue, changedGroups, checkpointOf, initial, query, reroll, seedsAt, setValue,
} from "../../interface/flow.js";
import * as flow from "../../interface/flow.js";

const path = process.env.GALAXY_FIXTURE;
assert.ok(path, "GALAXY_FIXTURE is unset; run this through tests/test_viewer.py");
const fixture = JSON.parse(readFileSync(path, "utf-8"));
const cat = catalogue(fixture.stages, fixture.inputs);

test("a page load lands on the published defaults, and nothing else is in the state", () => {
  const state = initial(cat);
  assert.deepEqual(Object.keys(state).sort(), ["cat", "values"], "no lock, no confirmation, no current stage");
  for (const kind of ["controls", "seeds", "events"]) {
    for (const input of fixture.inputs[kind]) assert.deepEqual(state.values[input.name], input.default, input.name);
  }
  // Six groups, every one of them built. A group with no stages is still kept rather than hidden - the panel
  // must survive one - which is asserted against a catalogue with the stages taken out.
  assert.equal(cat.checkpoints.length, 6);
  assert.ok(cat.checkpoints.every((cp) => cp.name && cp.stages.length > 0));
  const hollow = catalogue(
    { ...fixture.stages, checkpoints: fixture.stages.checkpoints.map((cp) => ({ ...cp, stages: [] })) },
    fixture.inputs,
  );
  assert.deepEqual(query(initial(hollow)), query(initial(cat)));
  assert.ok(hollow.checkpoints.every((cp) => cp.stages.length === 0));
});

test("the staged flow is gone: nothing locks, confirms or reopens", () => {
  for (const gone of ["confirm", "reopen", "goTo", "isEditable", "isLocked", "toggleLock", "withPreview"]) {
    assert.equal(flow[gone], undefined, `flow.${gone} is still exported`);
  }
});

test("every input lands in exactly one group, and none is lost", () => {
  const placed = cat.checkpoints.flatMap((cp) => cp.inputs);
  assert.equal(placed.length, new Set(placed).size);
  assert.deepEqual(new Set(placed), new Set(cat.inputs.keys()));
  const state = initial(cat);
  for (const cp of cat.checkpoints) for (const name of cp.inputs) assert.equal(checkpointOf(state, name), cp.n, name);
});

test("every input is editable at any time, in any order", () => {
  let state = initial(cat);
  // The last group first, then the first: no group waits on another.
  const last = cat.checkpoints.at(-1);
  const seed = seedsAt(state, last.n)[0];
  state = setValue(state, seed, 99);
  state = setValue(state, "halo_mass", 9e11);
  state = setValue(state, "halo_mass", 1.2e12);
  assert.equal(state.values[seed], 99);
  assert.equal(state.values.halo_mass, 1.2e12);
});

test("a control is held to the range the API publishes", () => {
  const state = initial(cat);
  const halo = fixture.inputs.controls.find((c) => c.name === "halo_mass");
  assert.throws(() => setValue(state, "halo_mass", halo.hi * 10), FlowError);
  assert.throws(() => setValue(state, "halo_mass", "not a number"), FlowError);
  assert.equal(setValue(state, "halo_mass", halo.lo).values.halo_mass, halo.lo);
  assert.throws(() => setValue(state, "not_an_input", 1), FlowError);
  assert.throws(() => setValue(state, "world_seed", 1.5), FlowError, "a seed takes an integer");
});

test("a reroll draws the named seeds and nothing else", () => {
  const state = initial(cat);
  const seeds = cat.checkpoints.flatMap((cp) => seedsAt(state, cp.n));
  assert.ok(seeds.includes("pattern_seed") && seeds.includes("world_seed"));
  assert.deepEqual(new Set(seeds), new Set(fixture.inputs.seeds.map((s) => s.name)));

  const rolled = reroll(state, ["pattern_seed", "halo_mass", "not_an_input"], () => 4242);
  assert.equal(rolled.values.pattern_seed, 4242, "the named seed is drawn");
  assert.equal(rolled.values.halo_mass, state.values.halo_mass, "a control is never rerolled");
  for (const name of seeds.filter((n) => n !== "pattern_seed")) {
    assert.equal(rolled.values[name], state.values[name], `${name} was not named and did not move`);
  }
  assert.deepEqual(changedGroups(rolled, query(rolled), query(state)), [checkpointOf(state, "pattern_seed")]);
});

test("the changed groups are where two input vectors differ, and only there", () => {
  const shown = initial(cat);
  assert.deepEqual(changedGroups(shown, query(shown), query(shown)), [], "a fresh draft is the galaxy shown");
  const moved = setValue(shown, "halo_mass", 9e11);
  assert.deepEqual(changedGroups(moved, query(moved), query(shown)), [checkpointOf(shown, "halo_mass")]);
  const events = fixture.inputs.events[0];
  const merged = setValue(moved, events.name, [{ time: 5, mass_ratio: 0.1, gas_fraction: 0.2 }]);
  const both = [checkpointOf(shown, "halo_mass"), checkpointOf(shown, events.name)];
  assert.deepEqual(changedGroups(merged, query(merged), query(shown)), [...new Set(both)].sort((a, b) => a - b));
  const back = setValue(setValue(merged, "halo_mass", shown.values.halo_mass), events.name, events.default);
  assert.deepEqual(changedGroups(back, query(back), query(shown)), [], "an edit undone is clean again");
});

test("the input vector goes out the way the API takes it", () => {
  const out = query(initial(cat));
  assert.equal(typeof out.halo_mass, "number");
  assert.equal(typeof out.mergers, "string", "an event list travels as JSON");
  assert.deepEqual(JSON.parse(out.mergers), fixture.inputs.events[0].default);
  assert.deepEqual(new Set(Object.keys(out)), new Set(cat.inputs.keys()), "every input, and nothing else");
});
