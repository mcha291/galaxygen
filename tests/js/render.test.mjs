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

import { cellAt, discOf, discScale, imageOf2D, polylineOf } from "../../interface/field.js";
import { legendStops, makePalette, makeRamp, paintOf, rgbOf, statistics } from "../../interface/ramp.js";
import { census, describe, format, identify, nearest, project } from "../../interface/stars.js";
import { domain, layout, markSize, pick } from "../../interface/system.js";
import * as view from "../../interface/view.js";

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

test("a table is not a catalogue: it hides no scalar and promises no sample", () => {
  // S59 (D218), re-read at S60 (D219). A small table the run publishes whole (domain "table":
  // the winding's segments at S59, the arm pieces since S60). While such columns were declared
  // object columns their stage read as a catalogue stage: its scalars were no longer asked for
  // (S59's stage published the five phases beside its table), and checkpoint 3 claimed a
  // sample to draw.
  //
  // The rule is read on the declarations, whatever the stage is called and whatever else it
  // publishes: S60's table stage publishes no scalar of its own, so one is declared beside the
  // table here - a real scalar of that checkpoint, re-declared as that stage's - and a control
  // re-declares the table's columns as object columns, where the same scalar must vanish.
  for (const [name, payload] of Object.entries(fixture.models)) {
    const all = payload.fields;
    const tables = all.filter((f) => f.domain === "table");
    assert.ok(tables.length > 0, `${name}: no table column is published; this test is out of date`);
    const materialisers = view.catalogueStages(all);
    const first = Math.min(...all.filter((f) => f.domain === "object").map((f) => f.checkpoint));
    const asObjects = all.map((f) => (f.domain === "table" ? { ...f, domain: "object" } : f));
    for (const t of tables) {
      assert.ok(!materialisers.has(t.stage), `${name}: ${t.stage} publishes a table and reads as a catalogue stage`);
      assert.ok(t.checkpoint < first, `${name}: the table is published before the first catalogue, or this proves nothing`);
      assert.equal(view.hasCatalogue(all, t.checkpoint), false, `${name}: a table at checkpoint ${t.checkpoint} is taken for a sample`);
      const asked = view.scalarsAt(all, t.checkpoint).map((f) => f.name);
      // Whatever scalars the table's own stage publishes are still asked for,
      for (const scalar of all.filter((f) => f.domain === "galaxy" && f.stage === t.stage)) {
        assert.ok(asked.includes(scalar.name), `${name}: ${scalar.name} is hidden by its stage's table`);
      }
      // and one declared beside the table is, so this holds something whether or not the stage has any:
      const model = all.find((f) => f.domain === "galaxy" && f.checkpoint === t.checkpoint && asked.includes(f.name));
      assert.ok(model, `${name}: no scalar is asked for at checkpoint ${t.checkpoint}; this would be vacuous`);
      const beside = { ...model, name: "a_scalar_beside_the_table", stage: t.stage };
      const shown = (fields) => view.scalarsAt([...fields, beside], t.checkpoint).some((f) => f.name === beside.name);
      assert.ok(shown(all), `${name}: a scalar of ${t.stage} is hidden by the stage's table`);
      // the control: as object columns the same table would hide it and promise a sample.
      assert.ok(!shown(asObjects), `${name}: the control does not bite - a catalogue stage's scalar is asked for`);
      assert.equal(view.hasCatalogue(asObjects, t.checkpoint), true, `${name}: the control does not bite - no sample is promised`);
    }
    // Checkpoint 3 has the tables and no catalogue: every scalar it publishes is asked for, none hidden.
    const at3 = view.scalarsAt(all, 3).map((f) => f.name).sort();
    const published3 = all.filter((f) => f.domain === "galaxy" && f.checkpoint === 3).map((f) => f.name).sort();
    assert.ok(published3.length > 0 && tables.some((t) => t.checkpoint === 3), `${name}: checkpoint 3 no longer holds the tables; this test is out of date`);
    assert.deepEqual(at3, published3, `${name}: a scalar of checkpoint 3 is not asked for`);
    assert.equal(view.hasCatalogue(all, 3), false);
    assert.equal(view.hasCatalogue(all, 4), false);
    assert.equal(view.hasCatalogue(all, 5), true);
  }
});

test("every published field reaches the viewer, in every model", () => {
  // S19's gate. The viewer is written from the declarations, so a field that nothing draws
  // is not a missing view — it is a field the model computes and no one ever looks at. Read
  // per registered model (one, "basic", from D170 to S27; two since; the default "azimuthal"
  // since S46, D197), so a further declaration is gated the day it is added.
  const models = Object.entries(fixture.models);
  assert.ok(models.length >= 1, "no model in the fixture: the gate would be vacuous");
  assert.ok(models.some(([name]) => name === "azimuthal"), "the default model is not in the fixture");
  assert.ok(models.some(([name]) => name === "basic"), "the basic model is not in the fixture");
  for (const [name, payload] of models) {
    const all = payload.fields;
    const materialisers = view.catalogueStages(all);
    let checked = 0;
    for (const f of all) {
      if (f.domain === "grid") {
        const shown = view.drawableAt(all, f.checkpoint).some((d) => d.name === f.name);
        assert.ok(shown, `${name}: ${f.name} is published at checkpoint ${f.checkpoint} and drawn nowhere`);
      } else if (f.domain === "galaxy") {
        // A scalar of a stage that also materialises objects is deliberately not asked
        // for — the region response's own census reports it instead (rule D4).
        if (materialisers.has(f.stage)) continue;
        const shown = view.scalarsAt(all, f.checkpoint).some((d) => d.name === f.name);
        assert.ok(shown, `${name}: scalar ${f.name} is published and never shown`);
      } else if (f.domain === "table") {
        // S59 (D218): a table column is rows the model's own stages read whole (the winding's
        // segments then, the arm pieces since S60). The one kind this gate lets through unshown, and only on its own word: it
        // declares no ramp, says the viewer does not show it, and no rule of the viewer picks
        // it up - not as a picture, not as a number, not as a catalogue's column.
        assert.equal(f.ramp, null, `${name}: table column ${f.name} declares a ramp nothing draws with`);
        assert.match(f.about, /not shown by the viewer/, `${name}: table column ${f.name} does not say it is not shown`);
        assert.ok(!view.drawableAt(all, f.checkpoint).some((d) => d.name === f.name), `${name}: ${f.name} is drawn`);
        assert.ok(!view.scalarsAt(all, f.checkpoint).some((d) => d.name === f.name), `${name}: ${f.name} is printed`);
        assert.ok(!view.wanted(all, f.checkpoint, f.name).includes(f.name), `${name}: ${f.name} is asked for`);
        checked += 1;
        continue;
      } else {
        assert.equal(f.domain, "object", `${name}: ${f.name} has a domain this gate does not know: ${f.domain}`);
      }
      // Anything painted rather than printed must yield its colour from its own
      // declaration: a scalar is a number in a table and declares no ramp at all.
      if (f.domain !== "galaxy") {
        const paint = paintOf(f, payload.cmaps, [0, 1]);
        assert.equal(paint.color(0).length, 4, `${name}: ${f.name} has no colour of its own`);
      }
      checked += 1;
    }
    assert.ok(checked > 100, `${name}: only ${checked} fields checked; the fixture looks empty`);
  }
});

test("a categorical field is drawn from its palette, not from a cmap it does not have", () => {
  const [, payload] = Object.entries(fixture.models)[0];
  const categorical = payload.fields.find((f) => f.ramp && f.ramp.kind === "palette");
  assert.ok(categorical, "no categorical field is published; this test is out of date");
  const paint = paintOf(categorical, payload.cmaps, [0, 1]);
  assert.deepEqual(paint.color(0).slice(0, 3), rgbOf(categorical.ramp.colors[0]));
  assert.deepEqual(paint.color(categorical.categories.length), [0, 0, 0, 0], "no category is no colour");
  assert.equal(paint.label(1), categorical.categories[1]);
  // And a continuous one still goes to the ramp.
  const continuous = payload.fields.find((f) => f.ramp && f.ramp.kind === "ramp");
  assert.equal(paintOf(continuous, payload.cmaps, [0, 1]).scale, continuous.ramp.scale);
});

test("the bar and arms vary with phi, and the viewer can tell", () => {
  const all = fixture.fields.fields;
  assert.equal(view.variesWithPhi(all), true, "pattern_density_contrast is published over (R, phi)");
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

// --- one system, laid out ----------------------------------------------------

test("a system's axis is logarithmic, because three decades on a line is not readable", () => {
  const planets = { planet_semi_major_axis: [0.1, 1, 10], planet_radius: [1, 1, 1] };
  const laid = layout(planets, [], { x: 0, y: 0, width: 300, height: 40 });
  const [a, b, c] = laid.marks.map((m) => m.x);
  assert.ok(Math.abs((b - a) - (c - b)) < 1e-6, "equal ratios are equal distances");
  assert.deepEqual(laid.ticks.map((t) => t.a), [0.1, 1, 10].filter((a) => a >= laid.range.lo && a <= laid.range.hi));
  assert.equal(laid.star.x, 0);
  assert.equal(laid.marks[0].y, laid.axis.y);
});

test("the axis reaches past everything there is, belts included", () => {
  const planets = { planet_semi_major_axis: [1], planet_radius: [1] };
  const belts = [{ kind: "kuiper", inner: 20, outer: 40 }];
  const range = domain(planets, belts);
  assert.ok(range.lo < 1 && range.hi > 40);
  assert.equal(domain({ planet_semi_major_axis: [] }, []), null, "nothing to draw is not a layout");
  assert.equal(layout({ planet_semi_major_axis: [] }, [], { x: 0, y: 0, width: 10, height: 10 }), null);
});

test("a belt is a band, clipped to the axis it is drawn on", () => {
  const planets = { planet_semi_major_axis: [1, 5], planet_radius: [1, 10] };
  const belts = [{ kind: "asteroid", inner: 2.06, outer: 3.28 }];
  const laid = layout(planets, belts, { x: 0, y: 0, width: 400, height: 50 });
  const band = laid.bands[0];
  assert.ok(band.x1 > band.x0);
  assert.ok(band.x0 > laid.marks[0].x && band.x1 < laid.marks[1].x, "between the two planets, as Jupiter's is");
});

test("a marker's area carries the radius, and is clamped at both ends", () => {
  assert.ok(markSize(11) > markSize(1) && markSize(1) > markSize(0.3));
  assert.ok(markSize(1e6) <= 13 && markSize(1e-6) >= 2);
  assert.equal(markSize(NaN), markSize(0), "no radius is drawn at the smallest size, not omitted");
  // Area, not radius: eleven Earth radii is not eleven times the mark.
  assert.ok(markSize(11) < 5 * markSize(1));
});

test("a click picks the planet under it, or nothing", () => {
  const planets = { planet_semi_major_axis: [0.4, 5.2], planet_radius: [1, 11] };
  const laid = layout(planets, [], { x: 0, y: 0, width: 400, height: 40 });
  assert.equal(pick(laid, laid.marks[1].x, laid.axis.y), 1);
  assert.equal(pick(laid, laid.marks[0].x + 1, laid.axis.y), 0);
  assert.equal(pick(laid, laid.axis.x1, laid.axis.y + 100), -1);
});
