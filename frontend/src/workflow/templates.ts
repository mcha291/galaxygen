// The templates (S54, D213; rule D1 as amended at D212): a named galaxy is an input set, a camera, a lens and a
// filter set, published by `/api/templates`. The viewer holds none of it (rule D5): this file reads what the
// route answers, lays a template's inputs on the workflow's own state through interface/flow.js, and says what
// the switcher shows. Pure: no React, no network (the route is asked for through api.ts and the one transport).
import * as flow from "@interface/flow.js";

import { type LensCamera, isLens } from "../galaxy/capture";
import { FILTER_SET_NAMES, type FilterSetName } from "../galaxy/filters";
import { type FlowState, type MergerEvent, formatNumber } from "./logic";

/**
 * A template's pin (S58, D217 item 2): a measured fact of the named galaxy's structure, stated in place of the
 * model's derivation or draw - `name` is the pin's input, which is the published field it decides where there is
 * one of that name; `value` the observed class, true or false, or - since S59 (D218 items 5-6) - a measured number
 * in the pin's own unit; `source` where it was read. `label` and `unit` are the pin input's own, as the model's
 * registry states them (S59's follow-up: "Angle of the bar to the Sun-centre line (a template's pin)", "deg"; a
 * class has no unit); null from an API that does not serve them. **A pin is no input of the viewer's**:
 * `/api/inputs` does not list it, the API refuses it as a query parameter, and it reaches a run only through
 * `template=<name>` (templateQuery below).
 *
 * Since S60 (D219) a value has two more shapes, as the route serves them: a **named class** - a string, one of
 * the pin's own `classes` (NGC 4414's `arm_class` is "flocculent" of grand_design, multi_armed, flocculent) -
 * and a **table** of measured rows (PinTable: the Milky Way's `arm_pieces`, six arms of a published table).
 */
export interface Pin {
  name: string;
  label: string | null;
  unit: string | null;
  value: boolean | number | string | PinTable;
  /** A named class's own list of classes, as served beside it; null on every other pin. */
  classes: string[] | null;
  source: string;
}

/**
 * A pin that is a table (S60, D219): the columns' names and units as served, and the rows, each as long as the
 * columns - a text, a number, or null for a number not read (rule B9). The viewer reads none of the numbers: it
 * says how many rows are pinned and lists their first column (pinWords).
 */
export interface PinTable {
  columns: { name: string; unit: string | null }[];
  rows: (string | number | null)[][];
}

/** One template, as `/api/templates` publishes it. `inputs` is fully resolved: every control, every seed, the event list. */
export interface Template {
  name: string;
  label: string;
  about: string;
  model: string;
  inputs: { controls: Record<string, number>; seeds: Record<string, number>; mergers: MergerEvent[] };
  /** Where the Galaxy view stands and through which lens (D213 ruling 5). */
  camera: LensCamera;
  /** The filter set the galaxy is first seen through: one of the viewer's own (filters.ts). */
  filters: FilterSetName;
  /** What the template states of the instrument; a number not read is null (rule B9). */
  instrument: { distance_mpc: number | null; pixel_scale_arcsec: number | null };
  /** What the template states of the galaxy's structure in place of a derivation (S58, D217); none before S58. */
  pins: Pin[];
  /** Carried as published and not read here: the fit and the checks are the model's records. */
  fit: unknown;
  checks: unknown[];
}

export interface Templates {
  /** The template the viewer lands on (rule D1). */
  default: string;
  templates: Template[];
}

/** A template's name is a path segment of its thumbnail and a button's key: lower-case letters, digits, underscores. */
const NAME = /^[a-z0-9]+(_[a-z0-9]+)*$/;
/** The event list's input, as `/api/inputs` names it. */
export const EVENTS_INPUT = "mergers";

const isRecord = (v: unknown): v is Record<string, unknown> => typeof v === "object" && v !== null && !Array.isArray(v);
const isNumber = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);

function numbers(value: unknown, what: string): Record<string, number> {
  if (!isRecord(value)) throw new Error(`${what} is not an object of numbers`);
  for (const [key, v] of Object.entries(value)) if (!isNumber(v)) throw new Error(`${what}.${key} is not a number: ${String(v)}`);
  return value as Record<string, number>;
}

const numberOrNull = (v: unknown): number | null => (isNumber(v) ? v : null);

/** A served text that may be absent: a string as it came, null where the key is missing or null; anything else is no text. */
const textOrNull = (v: unknown): string | null | undefined => (v === undefined || v === null ? null : typeof v === "string" ? v : undefined);

/** A pin as it came, for an error's message: cut short, since a table is long. */
const quoted = (pin: unknown): string => {
  const text = JSON.stringify(pin) ?? String(pin);
  return text.length > 240 ? `${text.slice(0, 240)}...` : text;
};

/** A non-empty list of non-empty texts (a named class's `classes`), or null where it is anything else. */
const textsOrNull = (v: unknown): string[] | null =>
  Array.isArray(v) && v.length > 0 && v.every((c) => typeof c === "string" && c) ? (v as string[]) : null;

/**
 * A table pin's value as served: `{columns: [{name, unit}], rows: [[...]]}`, every row as long as the columns and
 * every cell a text, a finite number or null. Null where it is anything else.
 */
function tableOrNull(v: unknown): PinTable | null {
  if (!isRecord(v) || !Array.isArray(v.columns) || !Array.isArray(v.rows)) return null;
  const columns: PinTable["columns"] = [];
  for (const column of v.columns as unknown[]) {
    const unit = isRecord(column) ? textOrNull(column.unit) : undefined;
    if (!isRecord(column) || typeof column.name !== "string" || !column.name || unit === undefined) return null;
    columns.push({ name: column.name, unit });
  }
  const cell = (c: unknown) => c === null || typeof c === "string" || isNumber(c);
  const whole = (v.rows as unknown[]).every((row) => Array.isArray(row) && row.length === columns.length && row.every(cell));
  return whole ? { columns, rows: (v.rows as (string | number | null)[][]).map((row) => [...row]) } : null;
}

/**
 * A template's pins as published: `[{name, label, unit, value, source}]`. The value is one of four shapes, and
 * the parser is built from what the route serves:
 * - the observed class, true or false (S58: `bar_present`);
 * - a measured number (S59: the Milky Way's bar angle, NGC 4414's pitch);
 * - a named class, a text that is one of the pin's own `classes`, a key the entry then carries (S60, D219:
 *   `arm_class`) - a text with no such list, or one that is not in it, is no class the viewer can stand behind;
 * - a table, `{columns, rows}` (S60: `arm_pieces`; tableOrNull above).
 * `label` and `unit` are the pin input's own, served since S59's follow-up, and an API from before it has neither
 * key - both are then null. **A pin the viewer cannot read is refused, not dropped**: it would be shown as nothing
 * while the API applies it. That refusal has stopped the viewer landing each time the wire grew (S59's numbers,
 * S60's two shapes): templates.test.ts holds this parser to the route's pins as they are served today
 * (pins.live.json), so the next growth fails there.
 */
function parsePins(raw: unknown, at: string): Pin[] {
  if (raw === undefined || raw === null) return []; // an API from before the pins (S54-S57)
  if (!Array.isArray(raw)) throw new Error(`${at}: pins is not a list`);
  return raw.map((pin: unknown) => {
    const shape = `${at}: a pin is {name, value: true or false, a number, one of its classes or a table of columns and rows, source}`;
    if (!isRecord(pin) || typeof pin.name !== "string" || !pin.name) throw new Error(`${shape}, got ${quoted(pin)}`);
    const classes = textsOrNull(pin.classes);
    let value: Pin["value"];
    if (typeof pin.value === "boolean" || isNumber(pin.value)) value = pin.value;
    else if (typeof pin.value === "string") {
      if (!classes || !classes.includes(pin.value)) throw new Error(`${at}: pin ${pin.name} names the class ${JSON.stringify(pin.value)}, which is not one of its classes ${JSON.stringify(pin.classes ?? null)}`);
      value = pin.value;
    } else {
      const table = tableOrNull(pin.value);
      if (!table) throw new Error(`${shape}, got ${quoted(pin)}`);
      value = table;
    }
    const label = textOrNull(pin.label);
    const unit = textOrNull(pin.unit);
    if (label === undefined || unit === undefined) throw new Error(`${at}: pin ${pin.name}'s label and unit are texts or absent, got ${quoted(pin)}`);
    return { name: pin.name, label, unit, value, classes: typeof value === "string" ? classes : null, source: typeof pin.source === "string" ? pin.source : "" };
  });
}

function parseTemplate(raw: unknown): Template {
  if (!isRecord(raw) || typeof raw.name !== "string" || !NAME.test(raw.name)) {
    throw new Error(`a template without a usable name: ${JSON.stringify(isRecord(raw) ? raw.name : raw)}`);
  }
  const at = `template ${raw.name}`;
  if (typeof raw.label !== "string" || !raw.label.trim()) throw new Error(`${at} has no label`);
  if (typeof raw.model !== "string" || !raw.model) throw new Error(`${at} names no model`);
  if (!isRecord(raw.inputs)) throw new Error(`${at} has no inputs`);
  if (!Array.isArray(raw.inputs.mergers)) throw new Error(`${at}: inputs.mergers is not a list`);
  const camera = raw.camera;
  if (!isRecord(camera)) throw new Error(`${at} has no camera`);
  const { inclination_deg, azimuth_deg, radius_kpc, fov_deg } = camera;
  if (!isNumber(inclination_deg) || inclination_deg < 0 || inclination_deg > 180 || !isNumber(azimuth_deg) || !isNumber(radius_kpc) || radius_kpc <= 0) {
    throw new Error(`${at}: camera inclination ${String(inclination_deg)}, azimuth ${String(azimuth_deg)}, radius ${String(radius_kpc)}`);
  }
  if (!isNumber(fov_deg) || !isLens(fov_deg)) throw new Error(`${at}: a field of view of ${String(fov_deg)} degrees is not a lens`);
  // A set the viewer does not hold is refused, not replaced: the template says what it is seen through.
  if (typeof raw.filters !== "string" || !(FILTER_SET_NAMES as string[]).includes(raw.filters)) {
    throw new Error(`${at} names the filter set ${JSON.stringify(raw.filters)}; the viewer holds ${FILTER_SET_NAMES.join(", ")}`);
  }
  const instrument = isRecord(raw.instrument) ? raw.instrument : {};
  return {
    name: raw.name,
    label: raw.label,
    about: typeof raw.about === "string" ? raw.about : "",
    model: raw.model,
    inputs: {
      controls: numbers(raw.inputs.controls, `${at}: inputs.controls`),
      seeds: numbers(raw.inputs.seeds, `${at}: inputs.seeds`),
      mergers: raw.inputs.mergers as MergerEvent[],
    },
    camera: { inclination_deg, azimuth_deg, radius_kpc, fov_deg },
    filters: raw.filters as FilterSetName,
    instrument: { distance_mpc: numberOrNull(instrument.distance_mpc), pixel_scale_arcsec: numberOrNull(instrument.pixel_scale_arcsec) },
    pins: parsePins(raw.pins, at),
    fit: raw.fit ?? null,
    checks: Array.isArray(raw.checks) ? raw.checks : [],
  };
}

/**
 * `/api/templates`' answer, checked where the viewer leans on it: each template's name, label, model, inputs,
 * camera with its lens and filter set, and the default being one of them. Anything else is carried as it came.
 * A payload that fails is an error the viewer shows, never a template half applied.
 */
export function parseTemplates(payload: unknown): Templates {
  if (!isRecord(payload) || !Array.isArray(payload.templates) || payload.templates.length === 0) {
    throw new Error("/api/templates lists no templates");
  }
  const templates = payload.templates.map(parseTemplate);
  const names = templates.map((t) => t.name);
  if (new Set(names).size !== names.length) throw new Error(`/api/templates repeats a name: ${names.join(", ")}`);
  if (typeof payload.default !== "string" || !names.includes(payload.default)) {
    throw new Error(`/api/templates' default ${JSON.stringify(payload.default)} is not one of ${names.join(", ")}`);
  }
  return { default: payload.default, templates };
}

/**
 * Ask for the templates through `ask` (api.ts hands in the transport's `get`). **An API from before S54 has no
 * such route and answers 404: that is null here, not an error**, and the viewer then lands as it did before
 * the templates - the default galaxy at the published defaults, no switcher. A viewer pointed at an older API
 * must still land. Every other failure (the API down, a payload that does not parse) is thrown.
 */
export async function readTemplates(ask: () => Promise<unknown>): Promise<Templates | null> {
  let payload: unknown;
  try {
    payload = await ask();
  } catch (error) {
    if ((error as { status?: unknown }).status === 404) return null;
    throw error;
  }
  return parseTemplates(payload);
}

export function templateOf(templates: Templates | null, name: string | null): Template | null {
  return templates?.templates.find((t) => t.name === name) ?? null;
}

/**
 * A template's inputs laid on a fresh flow: each control, each seed and the event list set through
 * `flow.setValue`, the step a user's own edit takes - so a value outside its published range, or an input the
 * model does not have, is refused there (a FlowError) rather than sent. Nothing is confirmed here.
 */
export function applyTemplate(fresh: FlowState, template: Template): FlowState {
  let state = fresh;
  for (const [name, value] of Object.entries({ ...template.inputs.controls, ...template.inputs.seeds })) {
    state = flow.setValue(state, name, value) as FlowState;
  }
  if (state.cat.inputs.has(EVENTS_INPUT) || template.inputs.mergers.length > 0) {
    state = flow.setValue(state, EVENTS_INPUT, template.inputs.mergers.map((event) => ({ ...event }))) as FlowState;
  }
  return state;
}

/**
 * Whether the galaxy asked for is no longer the template: another model, or an input vector that differs from
 * the template's in what the API is sent (`flow.query`: every value, the events as JSON). A reopened checkpoint
 * whose values still stand is not an edit; a moved control, a re-rolled seed or a changed event list is.
 */
export function isEdited(state: FlowState, model: string, template: Template): boolean {
  if (model !== template.model) return true;
  let base: Record<string, unknown>;
  try {
    base = flow.query(applyTemplate(flow.initial(state.cat) as FlowState, template)) as Record<string, unknown>;
  } catch {
    return true; // the template does not fit this model's inputs, so this galaxy is not it
  }
  const now = flow.query(state) as Record<string, unknown>;
  return Object.keys(base).some((name) => base[name] !== now[name]);
}

/** The query parameter that names the template a request starts from (`template=<name>`, S54; the pins since S58). */
export const TEMPLATE_KEY = "template";

/**
 * The query every route is asked with for a galaxy that is a template or was started from one: the input vector
 * as it stands and `template=<name>` beside it (S58, D217 item 2). The API lays the request's own inputs over the
 * template's, so every control, seed and event list is still the query's - an edit is one changed value, as
 * before - and **the template's pins are applied, which no input of the query can give or remove**. Without the
 * parameter a template's galaxy is asked for unpinned and the model derives what the template states as observed
 * (NGC 4414 was drawn barred that way until S58).
 *
 * **The one place the parameter is added** (useWorkflow's `query`, which every loader spreads and every cache key
 * serialises), so a loader added later carries it without knowing of it (rule B13). A galaxy started from no
 * template - an API from before S54 - gets its own object back untouched: nothing is sent that was not before.
 */
export function templateQuery<Q extends Record<string, unknown>>(query: Q, template: Pick<Template, "name"> | null): Q {
  return template ? { ...query, [TEMPLATE_KEY]: template.name } : query;
}

/** What `/api/fields` declares of a field, as far as a pin's words need it: its label, its categories and its unit. */
type Declared = { name: string; label: string; categories?: string[]; unit?: string; unit_display?: unknown };

/**
 * A pin in plain words: "<the field's label>: <what it pins> (as observed)" - "Barred: no (as observed)",
 * "Spiral arm pitch angle: 28.9° (as observed)". The label, the category and the unit are the declaration's of
 * the published field of the pin's name (rule A9: the viewer holds no name of its own for what the model
 * publishes). A pinned class is the declaration's second category when true and its first when false, as the
 * model publishes it; a pinned number is written with the declaration's unit (a unit that is a word after a
 * space, a sign such as ° against the number).
 *
 * **Without a declaration of that name** - the fields not loaded yet, or a pin that decides a field of another
 * name (S59's `sun_bar_angle` publishes `sun_azimuth`) - the pin's own label and unit, as `/api/templates` serves
 * them since S59's follow-up: "Angle of the bar to the Sun-centre line (a template's pin): 30° (as observed)". The
 * label is written as served, nothing stripped from it (rule A9), and the unit is shown as the field declarations
 * show it - the `unit_display` of any declared field of that unit ("deg" is "°" there), else the unit as served.
 * From an API that serves neither, the pin's name, and yes or no or the bare number: no unit is guessed (rule B9).
 *
 * **A named class** (S60, D219) is written as served - "Arm class: flocculent (as observed)" - under the label of
 * the published field of the pin's name where there is one (`arm_class`, whose categories are the same texts),
 * else under the pin's own. **A table** is one line, never its numbers: how many rows it pins, and their first
 * column under that column's own name - "Measured arm pieces (a template's pin): 6 rows by arm: Norma, Sct-Cen,
 * Sgr-Car, Local, Perseus, Outer (as observed)". Past TABLE_LISTED rows the rest are counted, not listed.
 */
export function pinWords(pin: Pin, fields: readonly Declared[] = []): string {
  const decl = fields.find((f) => f.name === pin.name);
  const value = pin.value;
  let stated: string;
  if (typeof value === "number") {
    const served = pin.unit ?? "";
    const unit = decl ? shown(decl) : served === "dimensionless" ? "" : shown(fields.find((f) => f.unit === served)) || served;
    stated = `${formatNumber(value, 4)}${/^[A-Za-zµμ]/.test(unit) ? " " : ""}${unit}`;
  } else if (typeof value === "boolean") {
    stated = decl?.categories?.length === 2 ? decl.categories[value ? 1 : 0] : value ? "yes" : "no";
  } else if (typeof value === "string") {
    stated = value;
  } else {
    stated = tableWords(value);
  }
  return `${decl?.label || pin.label || pin.name}: ${stated} (as observed)`;
}

/** How many of a table pin's rows are listed by their first column before the rest are only counted. */
export const TABLE_LISTED = 8;

/** A table pin's value in words: its rows counted, and their first column listed under the column's served name. */
function tableWords(table: PinTable): string {
  const n = table.rows.length;
  const count = `${n} ${n === 1 ? "row" : "rows"}`;
  const first = table.columns[0];
  if (!first || n === 0) return count;
  const cell = (c: string | number | null) => (c === null ? "—" : typeof c === "number" ? formatNumber(c, 4) : c);
  const listed = table.rows.slice(0, TABLE_LISTED).map((row) => cell(row[0]));
  const rest = n > TABLE_LISTED ? ` and ${n - TABLE_LISTED} more` : "";
  return `${count} by ${first.name}: ${listed.join(", ")}${rest}`;
}

/** A declared field's unit as the viewer writes it beside a number: its `unit_display`, none for a dimensionless one. */
function shown(decl: Declared | undefined): string {
  return decl && decl.unit !== "dimensionless" ? String(decl.unit_display ?? decl.unit ?? "") : "";
}

/** The template's name as the viewer writes it: its label, with "edited" once the galaxy is no longer it. */
export function templateLabel(template: Template, edited: boolean): string {
  return edited ? `${template.label} · edited` : template.label;
}

/**
 * Where the app serves a template's thumbnail from: `public/templates/<name>.png`, a capture of the picture
 * test's own (D213 ruling 7; e2e/captures.json), so choosing a template costs no model run for the others.
 */
export function thumbnailOf(name: string, base = "/"): string {
  return `${base}templates/${name}.png`;
}

export interface SwitcherItem {
  name: string;
  /** The button's text: the label, or "<label> · edited" on the template the galaxy was edited from. */
  caption: string;
  /** Pressed only while the galaxy shown is this template, unedited. */
  pressed: boolean;
  /** The galaxy shown started from this template and has been changed since. */
  edited: boolean;
  thumbnail: string;
  title: string;
}

/**
 * What the switcher shows (D213 ruling 7). The chosen template is pressed while the galaxy is the template. Once
 * a control, a seed, the event list or the model has been changed, **the galaxy is no longer the template**: its
 * button is released and reads "<label> · edited", and choosing it again restores the template - its inputs,
 * its camera, its lens and its filter set. The thumbnail stays the template's own, never the edited galaxy's.
 */
export function switcherItems(templates: Template[], chosen: string | null, edited: boolean, base = "/"): SwitcherItem[] {
  return templates.map((t) => {
    const from = t.name === chosen;
    const changed = from && edited;
    return {
      name: t.name,
      caption: templateLabel(t, changed),
      pressed: from && !edited,
      edited: changed,
      thumbnail: thumbnailOf(t.name, base),
      title: changed ? `${t.about} Edited since: choose it again to restore the template.`.trim() : t.about,
    };
  });
}
