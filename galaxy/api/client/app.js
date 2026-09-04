// The shell: the only file here that touches the DOM.
//
// Everything with a rule attached to it lives somewhere else — the checkpoint
// state machine in flow.js (D1), value-to-colour in ramp.js (A9), the one fetch
// in transport.js (D2) — so this file is wiring, and a bug here is a wiring bug
// rather than a broken rule. That split is the reason the viewer can be checked
// without a browser.
//
// Two things here are worth reading rather than skimming.
//
// **Stale responses.** Every load carries a token and a response is dropped
// unless its token is still the current one. A viewer that awaits two requests
// and paints whichever lands second will, sooner or later, show one galaxy's
// field with another galaxy's stars, and it will do it intermittently.
//
// **What the picture does not have.** The face-on disc is a radial profile
// revolved, because no published field varies with φ — and the viewer says so,
// underneath the picture, by looking at the declarations rather than by carrying
// a sentence somebody typed. When a stage publishes a non-axisymmetric density
// the note goes away on its own (debt #23).

import { discOf, discScale, imageOf2D, polylineOf } from "./field.js";
import * as flow from "./flow.js";
import { legendStops, makePalette, makeRamp } from "./ramp.js";
import * as catalogue from "./stars.js";
import * as view from "./view.js";
import { arrays, fields as fetchFields, inputs as fetchInputs, region, stages as fetchStages, version } from "./transport.js";

const GALAXY_SIZE = 480;
const PREVIEW = { width: 520, height: 260 };
const STAR_SAMPLE = 20000; // the published clickable sample; the LOD ladder raises it
const STAR_RADIUS = 1.6;

const el = {
  rail: document.getElementById("rail"),
  view: document.getElementById("view"),
  model: document.getElementById("model"),
  viewerHash: document.getElementById("viewer-hash"),
  apiHash: document.getElementById("api-hash"),
};

let state = null;
let meta = null; // the /api/fields payload, plus a name index
let picked = { field: null, star: -1 };
let data = { arrays: null, header: null, stars: null, points: null, error: null, busy: false };
let token = 0;

const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

function h(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === null || value === undefined || value === false) continue;
    if (key === "class") node.className = value;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else if (key === "text") node.textContent = value;
    else node.setAttribute(key, value === true ? "" : String(value));
  }
  for (const child of children.flat()) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child.nodeType ? child : document.createTextNode(String(child)));
  }
  return node;
}

// --- loading ------------------------------------------------------------------

async function boot() {
  try {
    const v = await version();
    const stages = await fetchStages();
    const fieldsPayload = await fetchFields();
    const inputsPayload = await fetchInputs();
    el.viewerHash.textContent = v.viewer.hash.slice(0, 12);
    el.apiHash.textContent = v.api.hash.slice(0, 12);
    el.model.textContent = `model ${stages.model}`;

    const byName = Object.fromEntries(fieldsPayload.fields.map((f) => [f.name, f]));
    meta = { ...fieldsPayload, byName };
    state = flow.initial(flow.catalogue(stages, inputsPayload));
    picked.field = view.defaultField(meta.fields, state.current);
    render();
    load();
  } catch (error) {
    el.view.append(h("p", { class: "error", text: `${error.message}` }));
  }
}

async function load() {
  const mine = ++token;
  data = { ...data, busy: true, error: null };
  paint();
  try {
    const names = view.wanted(meta.fields, state.current, picked.field);
    const query = flow.query(state);
    const frame = names.length ? await arrays(names, query) : { header: null, arrays: {} };
    if (mine !== token) return; // a newer request is already in flight

    let stars = null;
    let header = null;
    if (view.hasCatalogue(meta.fields, state.current)) {
      const got = await region({}, { ...query, stars: STAR_SAMPLE });
      if (mine !== token) return;
      stars = got.arrays;
      header = got.header;
    }
    data = { arrays: frame, header, stars, starHeader: header, busy: false, error: null };
    picked.star = -1;
  } catch (error) {
    if (mine !== token) return;
    data = { ...data, busy: false, error: error.message };
  }
  paint();
}

function apply(next) {
  state = next;
  const still = view.drawableAt(meta.fields, state.current).some((f) => f.name === picked.field);
  if (!still) picked.field = view.defaultField(meta.fields, state.current);
  render();
  load();
}

// --- the rail: checkpoints, controls, seeds ----------------------------------

function render() {
  el.rail.replaceChildren(renderSteps(), renderControls());
  paint();
}

function renderSteps() {
  return h(
    "ol",
    {},
    state.cat.checkpoints.map((cp) => {
      const reachable = cp.n <= state.confirmed + 1;
      const classes = ["step", cp.n === state.current ? "current" : "", cp.n <= state.confirmed ? "confirmed" : ""];
      return h(
        "li",
        {},
        h(
          "button",
          {
            class: classes.filter(Boolean).join(" "),
            disabled: !reachable,
            title: reachable ? "" : `confirm checkpoint ${cp.n - 1} first`,
            onclick: () => apply(flow.goTo(state, cp.n)),
          },
          h("span", { class: "n", text: `${cp.n}` }),
          h(
            "span",
            {},
            cp.name,
            h("span", { class: "stages", text: cp.stages.join(", ") || "nothing is built here yet" }),
          ),
        ),
      );
    }),
  );
}

function renderControls() {
  const cp = state.cat.checkpoints.find((c) => c.n === state.current);
  const panel = h("div", { class: "panel" }, h("h2", { text: `${cp.name} — inputs` }));
  const inputs = cp.inputs.map((name) => state.cat.inputs.get(name));
  if (!inputs.length) panel.append(h("p", { class: "empty", text: "no input belongs to this checkpoint" }));

  for (const input of inputs.filter((i) => i.kind === "control")) panel.append(renderControl(input));
  const seeds = inputs.filter((i) => i.kind === "seed");
  if (seeds.length) {
    panel.append(h("h2", { text: "seeds" }));
    for (const seed of seeds) panel.append(renderSeed(seed));
    panel.append(
      h("button", {
        text: "re-roll",
        disabled: seeds.every((s) => flow.isLocked(state, s.name)) || !flow.isEditable(state, seeds[0].name),
        onclick: () => apply(flow.reroll(state, seeds.map((s) => s.name), () => Math.floor(Math.random() * 2 ** 31))),
      }),
    );
  }
  for (const events of inputs.filter((i) => i.kind === "events")) {
    panel.append(
      h("h2", { text: events.label }),
      h("p", { class: "caption", text: `${state.values[events.name].length} event(s); editing them is not built yet` }),
    );
  }

  const confirmed = state.current <= state.confirmed;
  panel.append(
    h("div", { class: "panel", style: "padding:10px 0 0;background:none;border:0" },
      confirmed
        ? h("button", { class: "primary", text: `reopen checkpoint ${state.current}`, onclick: () => apply(flow.reopen(state, state.current)) })
        : h("button", { class: "primary", text: "confirm", onclick: () => apply(flow.confirm(state)) }),
      confirmed ? h("p", { class: "caption", text: "reopening discards every later checkpoint" }) : null,
    ),
  );
  return panel;
}

function renderControl(input) {
  const editable = flow.isEditable(state, input.name);
  const value = state.values[input.name];
  const readout = h("span", { class: "value", text: catalogue.format(value) });
  const step = (input.hi - input.lo) / 200;
  return h(
    "div",
    { class: "control", "data-disabled": String(!editable) },
    h("label", {}, h("span", { text: input.label }), readout),
    h("input", {
      type: "range",
      min: input.lo,
      max: input.hi,
      step,
      value,
      disabled: !editable, // rule D1: disabled, never hidden
      oninput: (e) => {
        readout.textContent = catalogue.format(Number(e.target.value));
      },
      onchange: (e) => apply(flow.setValue(state, input.name, Number(e.target.value))),
    }),
    h("div", { class: "range" }, h("span", { text: `${catalogue.format(input.lo)}` }), h("span", { text: `${input.unit_display || input.unit}` }), h("span", { text: `${catalogue.format(input.hi)}` })),
  );
}

function renderSeed(seed) {
  const editable = flow.isEditable(state, seed.name);
  const locked = flow.isLocked(state, seed.name);
  return h(
    "div",
    { class: "seed" },
    h("span", { class: "name", text: seed.label }),
    h("input", {
      type: "number",
      value: state.values[seed.name],
      disabled: !editable,
      onchange: (e) => apply(flow.setValue(state, seed.name, Number(e.target.value))),
    }),
    h("button", {
      text: locked ? "locked" : "lock",
      "aria-pressed": String(locked),
      title: "a lock stops a re-roll; it never freezes this against an earlier change",
      onclick: () => apply(flow.toggleLock(state, seed.name)),
    }),
  );
}

// --- the view: galaxy, preview, scalars, star --------------------------------

function paint() {
  if (!state || !meta) return;
  const view = h("div", {}, renderGalaxy());
  el.view.replaceChildren(view, renderSide());
}

function renderGalaxy() {
  const decl = view.discField(meta.fields, state.current, picked.field);
  const wrap = h("div", { id: "galaxy-wrap" });
  if (!decl || !data.arrays?.arrays?.[decl.name]) {
    wrap.append(h("p", { class: "empty", text: data.busy ? "drawing…" : "no radial field is published at this checkpoint yet" }));
    return wrap;
  }
  const values = data.arrays.arrays[decl.name];
  const axis = meta.grid.axes.R;
  const ramp = makeRamp(decl, meta.cmaps, values);
  const canvas = h("canvas", { width: GALAXY_SIZE, height: GALAXY_SIZE, title: decl.about });
  const ctx = canvas.getContext("2d");
  const image = discOf(values, axis, ramp, { size: GALAXY_SIZE });
  ctx.putImageData(new ImageData(image.data, image.width, image.height), 0, 0);

  const scale = discScale(GALAXY_SIZE, axis.hi);
  drawSun(ctx, scale);
  if (data.stars) drawStars(ctx, scale);

  canvas.addEventListener("click", (event) => {
    if (!data.points) return;
    const box = canvas.getBoundingClientRect();
    const x = ((event.clientX - box.left) * canvas.width) / box.width;
    const y = ((event.clientY - box.top) * canvas.height) / box.height;
    picked.star = catalogue.nearest(x, y, data.points, 6);
    paint();
  });

  wrap.append(canvas, legend(decl, ramp), h("p", { class: "caption" }, h("strong", { text: decl.label }), ` — ${decl.about}`));
  if (!view.variesWithPhi(meta.fields)) {
    wrap.append(
      h("p", { class: "note", text: "No published field varies with φ, so this disc is a radial profile revolved: the model has no spiral structure to draw (debt #23)." }),
    );
  }
  if (data.starHeader) {
    const c = catalogue.census(data.starHeader);
    wrap.append(h("p", { class: "caption", text: `${c.materialised.toLocaleString()} stars drawn of ${c.requested.toLocaleString()} asked of the galaxy, from ${c.cells} of ${c.of} cells, seed ${c.seed}` }));
  }
  return wrap;
}

function drawSun(ctx, scale) {
  ctx.strokeStyle = css("--line");
  ctx.beginPath();
  ctx.arc(scale.half, scale.half, scale.half, 0, 2 * Math.PI);
  ctx.stroke();
}

function drawStars(ctx, scale) {
  const points = catalogue.project(data.stars, scale, GALAXY_SIZE);
  data.points = points;
  const decl = meta.byName.star_population;
  const palette = decl ? makePalette(decl) : null;
  const codes = data.stars.star_population;
  for (let i = 0; i < points.n; i += 1) {
    const [r, g, b, a] = palette && codes ? palette.color(codes[i]) : [255, 255, 255, 255];
    if (!a) continue;
    ctx.fillStyle = `rgb(${r} ${g} ${b} / 70%)`;
    ctx.fillRect(points.sx[i] - STAR_RADIUS / 2, points.sy[i] - STAR_RADIUS / 2, STAR_RADIUS, STAR_RADIUS);
  }
  if (picked.star >= 0) {
    ctx.strokeStyle = css("--accent");
    ctx.beginPath();
    ctx.arc(points.sx[picked.star], points.sy[picked.star], 5, 0, 2 * Math.PI);
    ctx.stroke();
  }
}

function legend(decl, ramp) {
  const strip = h("canvas", { class: "strip", width: 128, height: 1, style: "height:10px" });
  const ctx = strip.getContext("2d");
  const stops = legendStops(ramp, 128);
  const image = ctx.createImageData(128, 1);
  stops.forEach(([r, g, b], i) => {
    image.data.set([r, g, b, 255], i * 4);
  });
  ctx.putImageData(image, 0, 0);
  return h(
    "div",
    { class: "legend" },
    h("span", { text: catalogue.format(ramp.lo) }),
    strip,
    h("span", { text: `${catalogue.format(ramp.hi)} ${decl.unit_display || ""}` }),
    ramp.note ? h("span", { class: "note", text: ramp.note }) : null,
    h("span", { text: ramp.scale === "linear" ? "" : ramp.scale }),
  );
}

function renderSide() {
  const side = h("div", {});
  if (data.error) side.append(h("p", { class: "error", text: data.error }));
  if (data.busy) side.append(h("p", { class: "busy", text: "running the stages this answer needs…" }));

  const here = view.publishedAt(meta.fields, state.current);
  const drawable = view.drawableAt(meta.fields, state.current);
  if (drawable.length) {
    const picker = h(
      "select",
      { onchange: (e) => { picked.field = e.target.value; load(); } },
      drawable.map((f) => h("option", { value: f.name, selected: f.name === picked.field, text: f.label })),
    );
    side.append(h("div", { class: "panel" }, h("h2", { text: "field published here" }), picker, renderPreview()));
  } else if (!here.length) {
    side.append(h("div", { class: "panel" }, h("p", { class: "empty", text: "This checkpoint has no stages yet — nothing is computed here." })));
  }

  const scalars = view.scalarsAt(meta.fields, state.current);
  if (scalars.length) side.append(renderScalars(scalars));
  if (picked.star >= 0 && data.stars) side.append(renderStar());
  return side;
}

function renderPreview() {
  const decl = meta.byName[picked.field];
  const values = data.arrays?.arrays?.[picked.field];
  if (!decl || !values) return h("p", { class: "empty", text: data.busy ? "…" : "nothing drawn yet" });
  const ramp = makeRamp(decl, meta.cmaps, values);
  const canvas = h("canvas", { width: PREVIEW.width, height: PREVIEW.height });
  const ctx = canvas.getContext("2d");

  if (decl.axes.length === 2) {
    const rows = meta.grid.axes[decl.axes[0]].n;
    const cols = meta.grid.axes[decl.axes[1]].n;
    const image = imageOf2D(values, rows, cols, ramp, { maxWidth: PREVIEW.width, maxHeight: PREVIEW.height });
    ctx.putImageData(new ImageData(image.data, image.width, image.height), 0, 0);
  } else {
    const axis = meta.grid.axes[decl.axes[0]];
    const box = { x: 54, y: 10, width: PREVIEW.width - 64, height: PREVIEW.height - 30 };
    const line = polylineOf(values, box);
    ctx.strokeStyle = css("--line");
    ctx.strokeRect(box.x, box.y, box.width, box.height);
    ctx.strokeStyle = css("--accent");
    ctx.lineWidth = 1.5;
    for (const segment of line.segments) {
      ctx.beginPath();
      segment.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)));
      ctx.stroke();
    }
    ctx.fillStyle = css("--muted");
    ctx.font = "10px ui-monospace, SFMono-Regular, Menlo, monospace";
    ctx.textAlign = "left";
    ctx.fillText(`${decl.axes[0]} ${axis.lo}–${axis.hi} ${axis.unit_display || axis.unit}`, box.x, PREVIEW.height - 6);
    ctx.textAlign = "right";
    ctx.fillText(`${catalogue.format(line.hi)}`, box.x - 4, box.y + 8);
    ctx.fillText(`${catalogue.format(line.lo)}`, box.x - 4, box.y + box.height);
    if (line.constant) ctx.fillText(`${catalogue.format(line.lo)}`, box.x - 4, box.y + box.height / 2 + 4);
  }
  const axes = decl.axes.map((a) => `${a} (${meta.grid.axes[a].n})`).join(" × ");
  return h(
    "div",
    {},
    canvas,
    decl.axes.length === 2 ? legend(decl, ramp) : null,
    h("p", { class: "caption" }, h("strong", { text: `${decl.label} — ${axes}` }), ` ${decl.about}`),
  );
}

function renderScalars(scalars) {
  const rows = scalars.map((f) => {
    const value = data.arrays?.header?.scalars?.[f.name];
    return h(
      "tr",
      { title: f.about },
      h("td", { class: "label", text: f.label }),
      h("td", { class: "value", text: value === undefined ? "…" : catalogue.format(value) }),
      h("td", { class: "unit", text: f.unit_display || "" }),
    );
  });
  return h("div", { class: "panel" }, h("h2", { text: "published here" }), h("table", {}, rows));
}

function renderStar() {
  const rows = catalogue.describe(picked.star, data.stars, meta.byName);
  return h(
    "div",
    { class: "panel" },
    h("h2", { text: "star" }),
    h("table", {}, rows.map((r) => h("tr", {}, h("td", { class: "label", text: r.label }), h("td", { class: "value", text: r.value }), h("td", { class: "unit", text: r.unit })))),
    h("p", { class: "caption", text: "Drawn from the seeded sample; the same seed puts the same star here every time." }),
  );
}

boot();
