// Rule D1, asserted against the real declarations.
//
// The catalogue comes from a live /api/stages and /api/inputs, dumped by the
// pytest wrapper (tests/test_viewer.py) into the file named by $GALAXY_FIXTURE.
// A fixture written by hand here would drift from the registry silently, which
// is the failure the two-model discipline exists to prevent one level down.
//
//   uv run pytest tests/test_viewer.py      # the way to run this

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
  FlowError, catalogue, confirm, goTo, initial, isEditable, isLocked,
  query, reopen, reroll, seedsAt, setValue, toggleLock, withPreview,
} from "../../galaxy/api/client/flow.js";

const path = process.env.GALAXY_FIXTURE;
assert.ok(path, "GALAXY_FIXTURE is unset; run this through tests/test_viewer.py");
const fixture = JSON.parse(readFileSync(path, "utf-8"));
const cat = catalogue(fixture.stages, fixture.inputs);

test("a page load lands on stage one, with the published defaults", () => {
  const state = initial(cat);
  assert.equal(state.current, 1);
  assert.equal(state.confirmed, 0);
  assert.equal(state.values.halo_mass, fixture.inputs.controls.find((c) => c.name === "halo_mass").default);
  assert.deepEqual(state.previews, {});
  // Six checkpoints, and the empty one is kept: "nothing here yet" is true and worth saying.
  assert.equal(cat.checkpoints.length, 6);
  const planets = cat.checkpoints.at(-1);
  assert.equal(planets.stages.length, 0);
  assert.ok(cat.checkpoints.every((cp) => cp.name));
});

test("every input lands in exactly one checkpoint, and none is lost", () => {
  const placed = cat.checkpoints.flatMap((cp) => cp.inputs);
  assert.equal(placed.length, new Set(placed).size);
  assert.deepEqual(new Set(placed), new Set(cat.inputs.keys()));
});

test("a confirmed control is disabled, not hidden", () => {
  let state = confirm(initial(cat));
  assert.equal(state.confirmed, 1);
  assert.equal(state.current, 2);
  // Still listed at its checkpoint — the viewer can render it, greyed.
  assert.ok(cat.checkpoints[0].inputs.includes("halo_mass"));
  assert.equal(isEditable(state, "halo_mass"), false);
  assert.throws(() => setValue(state, "halo_mass", 1.2e12), FlowError);
  // ... and a later one is untouched.
  assert.equal(isEditable(state, "migration_efficiency"), true);
});

test("a control is held to the range the API publishes", () => {
  const state = initial(cat);
  const halo = fixture.inputs.controls.find((c) => c.name === "halo_mass");
  assert.throws(() => setValue(state, "halo_mass", halo.hi * 10), FlowError);
  assert.throws(() => setValue(state, "halo_mass", "not a number"), FlowError);
  assert.equal(setValue(state, "halo_mass", halo.lo).values.halo_mass, halo.lo);
  assert.throws(() => setValue(state, "not_an_input", 1), FlowError);
});

test("reopening a stage discards every later one", () => {
  let state = initial(cat);
  for (let n = 1; n <= 4; n += 1) state = withPreview(confirm(state), n, { drawn: n });
  assert.equal(state.confirmed, 4);
  assert.deepEqual(Object.keys(state.previews), ["1", "2", "3", "4"]);

  state = reopen(state, 2);
  assert.equal(state.current, 2);
  assert.equal(state.confirmed, 1, "checkpoint 2 is open again");
  assert.deepEqual(Object.keys(state.previews), ["1"], "later previews are discarded, not kept as stale");
  assert.equal(isEditable(state, "infall_timescale"), true);
  assert.throws(() => reopen(state, 0), FlowError);
  assert.throws(() => reopen(state, 99), FlowError);
});

test("you cannot look past the checkpoint you have confirmed", () => {
  const state = confirm(initial(cat));
  assert.equal(goTo(state, 2).current, 2);
  assert.throws(() => goTo(state, 3), FlowError);
  assert.equal(goTo(state, 1).confirmed, 0, "going back is reopening; it discards");
});

test("a lock stops a re-roll and nothing else", () => {
  let state = initial(cat);
  const draw = () => 4242;
  const seeds = cat.checkpoints.flatMap((cp) => seedsAt(state, cp.n));
  assert.ok(seeds.includes("pattern_seed"));

  state = toggleLock(state, "pattern_seed");
  assert.ok(isLocked(state, "pattern_seed"));
  const rolled = reroll(state, seeds, draw);
  assert.equal(rolled.values.pattern_seed, state.values.pattern_seed, "a locked seed is not re-rolled");
  assert.equal(rolled.values.world_seed, 4242, "an unlocked one is");

  // The other half of D1: a lock is not a freeze. Confirm through the pattern,
  // then reopen checkpoint 1 and change the halo mass. The seed keeps its value;
  // the pattern's result does not survive.
  let held = rolled;
  for (let n = 1; n <= 4; n += 1) held = withPreview(confirm(held), n, { drawn: n });
  held = reopen(held, 1);
  held = setValue(held, "halo_mass", 9e11);
  assert.equal(held.values.pattern_seed, state.values.pattern_seed, "the locked value survived");
  assert.equal(held.previews[4], undefined, "the locked seed's *result* did not");
  assert.equal(held.confirmed, 0);
  assert.ok(isLocked(held, "pattern_seed"), "and the lock itself is still set");

  assert.throws(() => toggleLock(state, "halo_mass"), FlowError, "only seeds are locked");
});

test("a re-roll skips seeds whose checkpoint is confirmed", () => {
  const state = confirm(initial(cat)); // checkpoint 1 confirmed: world_seed is fixed
  const rolled = reroll(state, ["world_seed", "systems_seed"], () => 7);
  assert.equal(rolled.values.world_seed, state.values.world_seed);
  assert.equal(rolled.values.systems_seed, 7);
});

test("the input vector goes out the way the API takes it", () => {
  const out = query(initial(cat));
  assert.equal(typeof out.halo_mass, "number");
  assert.equal(typeof out.mergers, "string", "an event list travels as JSON");
  assert.deepEqual(JSON.parse(out.mergers), fixture.inputs.events[0].default);
});
