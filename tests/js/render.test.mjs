// What the viewer draws, checked against the declarations it draws from.
//
// The declarations are real — dumped from /api/fields by tests/test_viewer.py —
// and the values are synthetic, which is the split that makes the assertions
// exact without letting the contract drift. A ramp is checked by comparing the
// colour it produces against the published stops, never against a colour written
// here: this file may not contain one (rule A9, asserted in test_viewer.py).

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import { cellAt, discOf, discScale, imageOf2D, polylineOf } from "../../galaxy/api/client/field.js";
import { legendStops, makePalette, makeRamp, rgbOf, statistics } from "../../galaxy/api/client/ramp.js";
import { census, describe, format, identify, nearest, project } from "../../galaxy/api/client/stars.js";
import * as view from "../../galaxy/api/client/view.js";

const fixture = JSON.parse(readFileSync(process.env.GALAXY_FIXTURE, "utf-8"));
const { cmaps, fields } = fixture.fields;
const byName = Object.fromEntries(fields.map((f) => [f.name, f]));
const declOf = (name) => {
  const decl = byName[name];
  assert.ok(decl, `${name} is not published; this test is out of date with the model`);
  return decl;
};

test("a pinned bound is the declaration speaking, and it wins", () => {
  const decl = declOf("star_metallicity"); // RdBu, lo -2, hi 0.5, meaningful zero
  const ramp = makeRamp(decl, cmaps, [-9, 9]);
  assert.equal(ramp.lo, decl.ramp.lo);
  assert.equal(ramp.hi, decl.ramp.hi);
  const stops = cmaps[decl.ramp.cmap].stops;
  assert.deepEqual(ramp.color(decl.ramp.lo).slice(0, 3), rgbOf(stops[0]));
  assert.deepEqual(ramp.color(decl.ramp.hi).slice(0, 3), rgbOf(stops.at(-1)));
  assert.deepEqual(ramp.color(-99).slice(0, 3), rgbOf(stops[0]), "out of range clamps, it does not wrap");
});

test("an open bound is taken from the data, at percentiles", () => {
  const decl = declOf("stellar_surface_density");
  assert.equal(decl.ramp.lo, null, "this test needs a field whose ramp leaves its bounds open");
  const values = [...Array(100).keys()]; // 0..99, plus one outlier
  values.push(1e9);
  const ramp = makeRamp(decl, cmaps, values);
  assert.ok(ramp.hi < 1e9, "one hot cell must not flatten the rest to a single colour");
  assert.equal(ramp.stats.max, 1e9, "though the outlier is still reported");
  assert.equal(ramp.stats.min, 0);
  assert.ok(ramp.lo >= 0 && ramp.lo < 5, "the low bound is a percentile, near the minimum but not it");
});

test("a value that is not a number is drawn as nothing", () => {
  const ramp = makeRamp(declOf("stellar_surface_density"), cmaps, [1, 2, 3]);
  assert.deepEqual(ramp.color(NaN), [0, 0, 0, 0]);
  assert.deepEqual(ramp.color(null), [0, 0, 0, 0], "Number(null) is 0; a published null is not one");
  assert.equal(ramp.position(Infinity), null);
  assert.notEqual(ramp.color(0)[3], 0, "zero is a measurement and is drawn");
});

test("a meaningful zero through a diverging map lands on the neutral stop", () => {
  const base = declOf("star_metallicity");
  const open = { ...base, ramp: { ...base.ramp, lo: null, hi: null } }; // the same map, bounds released
  const ramp = makeRamp(open, cmaps, [-1, 0, 4]);
  assert.equal(ramp.lo, -ramp.hi, "bounds are symmetric about zero");
  const table = cmaps[base.ramp.cmap];
  assert.ok(table.diverging && table.midpoint);
  assert.deepEqual(ramp.color(0).slice(0, 3), rgbOf(table.midpoint));
});

test("a log ramp needs positive values and says so when it does not have them", () => {
  const decl = declOf("star_mass");
  assert.equal(decl.ramp.scale, "log", "this test needs a log-scaled field");
  const good = makeRamp(decl, cmaps, [0.1, 1, 10]);
  assert.equal(good.scale, "log");
  assert.ok(good.position(1) > 0 && good.position(1) < 1);
  const bad = makeRamp(decl, cmaps, [0, 0, 0]);
  assert.equal(bad.scale, "linear");
  assert.match(bad.note, /log needs positive values/);
});

test("a categorical column is drawn in its declared colours", () => {
  const decl = declOf("star_population");
  const palette = makePalette(decl);
  assert.deepEqual(palette.categories, decl.categories);
  decl.ramp.colors.forEach((hex, i) => assert.deepEqual(palette.color(i).slice(0, 3), rgbOf(hex)));
  assert.equal(palette.label(0), decl.categories[0]);
  assert.equal(palette.color(99)[3], 0, "a code with no category is drawn as nothing");
  assert.equal(palette.label(1n), decl.categories[1], "the wire hands over BigInt codes");
});

test("statistics ignore what is not a number, and report how much of that there was", () => {
  const stats = statistics([1, NaN, 3, Infinity, 5]);
  assert.equal(stats.finite, 3);
  assert.equal(stats.count, 5);
  assert.equal(stats.min, 1);
  assert.equal(stats.max, 5);
  assert.deepEqual(statistics([NaN, NaN]), { min: null, max: null, lo: null, hi: null, finite: 0, count: 2 });
});

test("a legend is the ramp, not a copy of it", () => {
  const ramp = makeRamp(declOf("stellar_surface_density"), cmaps, [0, 1]);
  const strip = legendStops(ramp, 5);
  assert.equal(strip.length, 5);
  assert.deepEqual(strip[0], ramp.at(0));
  assert.deepEqual(strip.at(-1), ramp.at(1));
});

test("a grid cell is found by coordinate, and off the axis is not a cell", () => {
  const axis = { lo: 0, hi: 30, n: 3 };
  assert.equal(cellAt(0, axis), 0);
  assert.equal(cellAt(9.9, axis), 0);
  assert.equal(cellAt(10.1, axis), 1);
  assert.equal(cellAt(30, axis), 2, "the outer edge belongs to the last cell");
  assert.equal(cellAt(30.1, axis), -1);
  assert.equal(cellAt(-1, axis), -1);
  assert.equal(cellAt(NaN, axis), -1);
});

test("a 2-D field is sampled, never averaged, and the first axis points up", () => {
  const ramp = { color: (v) => [Number(v), 0, 0, 255] };
  const image = imageOf2D([10, 20, 30, 40, 50, 60], 2, 3, ramp, { maxWidth: 3, maxHeight: 2 });
  assert.equal(image.width, 3);
  assert.equal(image.height, 2);
  const red = (x, y) => image.data[(y * image.width + x) * 4];
  assert.equal(red(0, 0), 40, "row 1 of the array is the top of the picture");
  assert.equal(red(2, 1), 30);
  const values = new Set([...Array(6).keys()].map((i) => red(i % 3, Math.floor(i / 3))));
  assert.ok([...values].every((v) => [10, 20, 30, 40, 50, 60].includes(v)), "no value was invented between cells");
});

test("a disc is a profile revolved, and off the grid is transparent", () => {
  const axis = { lo: 0, hi: 10, n: 5 };
  const ramp = { color: (v) => [Number(v), 0, 0, 255] };
  const size = 40;
  const disc = discOf([1, 2, 3, 4, 5], axis, ramp, { size });
  const at = (x, y) => disc.data.slice((y * size + x) * 4, (y * size + x) * 4 + 4);
  assert.equal(at(0, 0)[3], 0, "the corner is outside the outer radius");
  assert.equal(at(size / 2, size / 2)[0], 1, "the centre reads the innermost ring");
  assert.equal(at(size - 1, size / 2)[0], 5, "the rim reads the outermost");
  // Axisymmetric by construction: the same radius is the same colour everywhere.
  assert.deepEqual(at(size / 2, 2), at(size / 2, size - 3));
  assert.deepEqual(at(2, size / 2), at(size - 3, size / 2));
});

test("a line breaks where the numbers stop", () => {
  const box = { x: 0, y: 0, width: 100, height: 50 };
  const line = polylineOf([1, 2, NaN, 4], box);
  assert.equal(line.segments.length, 2, "a gap is not drawn across");
  assert.equal(line.lo, 1);
  assert.equal(line.hi, 4);
  assert.equal(line.segments[0][0][1], box.height, "the smallest value sits at the bottom");
  assert.deepEqual(polylineOf([NaN], box).segments, []);
});

test("stars land where their own radius and azimuth put them, and can be picked", () => {
  const size = 200;
  const scale = discScale(size, 10);
  const columns = {
    star_radius: new Float64Array([0, 10, 5]),
    star_azimuth: new Float64Array([0, 0, Math.PI / 2]),
  };
  const points = project(columns, scale, size);
  assert.deepEqual(Array.from(points.sx), [100, 200, 100]);
  assert.deepEqual(Array.from(points.sy), [100, 100, 50]);
  assert.equal(nearest(199, 101, points), 1);
  assert.equal(nearest(0, 0, points), -1, "a click on nothing selects nothing");
  assert.equal(nearest(0, 0, points, 1000), 2, "with a wide enough reach, the nearest one is found");
});

test("a star reads back in the units its columns were declared with", () => {
  const columns = {
    star_radius: new Float64Array([8.2]),
    star_mass: new Float64Array([0.5]),
    star_population: new BigInt64Array([1n]),
  };
  const rows = describe(0, columns, byName);
  const radius = rows.find((r) => r.name === "star_radius");
  assert.equal(radius.label, byName.star_radius.label);
  assert.equal(radius.unit, byName.star_radius.unit_display);
  assert.equal(radius.value, "8.2");
  const population = rows.find((r) => r.name === "star_population");
  assert.equal(population.value, byName.star_population.categories[1]);
  assert.deepEqual(describe(9, columns, byName), [], "no such star, no rows invented");
});

test("numbers are formatted, and a missing one is not formatted as zero", () => {
  assert.equal(format(0), "0");
  assert.equal(format(8.2), "8.2");
  assert.equal(format(5.276e10), "5.276e+10");
  assert.equal(format(NaN), "—");
  assert.equal(format(null), "—");
  assert.notEqual(format(NaN), format(0));
});

test("the census is what the region query said it did", () => {
  const header = { stars: { materialised: 290, requested: 20000, seed: 0 }, cells: { count: 9, of: 1024 } };
  assert.deepEqual(census(header), { materialised: 290, requested: 20000, cells: 9, of: 1024, seed: 0 });
});

test("a constant field is drawn down the middle, not on the floor", () => {
  const box = { x: 0, y: 0, width: 100, height: 50 };
  const line = polylineOf([2, 2, 2], box);
  assert.equal(line.constant, true);
  assert.deepEqual(line.segments[0].map(([, y]) => y), [25, 25, 25]);
  assert.equal(line.lo, 2);
  assert.equal(polylineOf([1, 2], box).constant, false);
});

// --- what a checkpoint shows ------------------------------------------------

test("a checkpoint shows what it published, and asks for nothing else", () => {
  const all = fixture.fields.fields;
  const drawable = view.drawableAt(all, 1);
  assert.ok(drawable.length > 0);
  assert.ok(drawable.every((f) => f.checkpoint === 1 && f.domain === "grid"));
  assert.equal(view.defaultField(all, 1), drawable.at(-1).name, "the latest field, not the first");
  assert.notEqual(view.defaultField(all, 1), "canary", "and so not the model-boundary probe");
  const names = view.wanted(all, 1, view.defaultField(all, 1));
  assert.ok(names.every((n) => all.find((f) => f.name === n).checkpoint <= 1));
});

test("the viewer never asks for a scalar that would build the catalogue", () => {
  const all = fixture.fields.fields;
  const materialisers = view.catalogueStages(all);
  assert.ok(materialisers.size >= 1, "some stage publishes object columns");
  const counted = all.filter((f) => f.domain === "galaxy" && materialisers.has(f.stage));
  assert.ok(counted.length > 0, "one of them publishes a scalar too; this would be vacuous otherwise");
  for (const scalar of counted) {
    const asked = view.scalarsAt(all, scalar.checkpoint).map((f) => f.name);
    assert.ok(!asked.includes(scalar.name), `${scalar.name} would materialise a whole sample (rule D4)`);
  }
  // Every other scalar at those checkpoints is still asked for.
  for (const checkpoint of new Set(counted.map((f) => f.checkpoint))) {
    const asked = view.scalarsAt(all, checkpoint).map((f) => f.name);
    const others = all.filter(
      (f) => f.domain === "galaxy" && f.checkpoint === checkpoint && !materialisers.has(f.stage),
    );
    for (const scalar of others) assert.ok(asked.includes(scalar.name), scalar.name);
  }
});

test("the disc is drawn from a radial field, and the picked one wins", () => {
  const all = fixture.fields.fields;
  const radial = view.radialUpTo(all, 3);
  assert.ok(radial.length > 1);
  assert.equal(view.discField(all, 3, null).name, radial.at(-1).name);
  assert.equal(view.discField(all, 3, radial[0].name).name, radial[0].name);
  // A 2-D field cannot be the disc; the latest radial one is used instead.
  const twoD = all.find((f) => f.domain === "grid" && f.axes.length === 2);
  assert.equal(view.discField(all, 3, twoD.name).name, radial.at(-1).name);
});

test("the catalogue appears at the checkpoint that publishes it, and not before", () => {
  const all = fixture.fields.fields;
  const n = all.find((f) => f.domain === "object").checkpoint;
  assert.equal(view.hasCatalogue(all, n - 1), false);
  assert.equal(view.hasCatalogue(all, n), true);
});

test("nothing published varies with phi, and the viewer can tell", () => {
  const all = fixture.fields.fields;
  assert.equal(view.variesWithPhi(all), false, "debt #23: when this changes, the disc note goes away");
  assert.equal(view.variesWithPhi([{ axes: ["R", "phi"] }]), true);
});

test("a row of a region response knows which star it is", () => {
  const header = { cells: { ids: [3, 9, 12], counts: [2, 1, 3] } };
  assert.deepEqual(identify(header, 0), { cell: 3, index: 0 });
  assert.deepEqual(identify(header, 1), { cell: 3, index: 1 });
  assert.deepEqual(identify(header, 2), { cell: 9, index: 0 });
  assert.deepEqual(identify(header, 5), { cell: 12, index: 2 });
  assert.equal(identify(header, 6), null, "past the last star is not a star");
  assert.equal(identify({ cells: { ids: [], counts: [] } }, 0), null);
});
