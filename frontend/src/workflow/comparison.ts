import * as flow from "@interface/flow.js";

import type { Query } from "../api";
import type { FilterSetName } from "../galaxy/filters";
import { TEMPLATE_EXPOSURE, exposureFor } from "../galaxy/tuning";
import type { FlowState } from "./logic";
import { type Template, templateLabel } from "./templates";
import { landOn, queryOf } from "./useWorkflow";

// The comparison view's second pane (T16, S83): what it draws beside the galaxy shown - another template, the draft, the
// galaxy shown through another filter set, or a picture the user picks - and the query each galaxy is asked with. Pure,
// so it is tested as it is (comparison.test.ts); galaxy/ComparePane.tsx draws it.

/** What the right pane draws. "shown" is the galaxy on screen (through the pane's own filter set). */
export type CompareSource = { kind: "shown" } | { kind: "template"; name: string } | { kind: "draft" } | { kind: "picture" };

/** A button of the pane's bar. */
export interface SourceItem {
  key: string;
  label: string;
  title: string;
  source: CompareSource;
  disabled: boolean;
}

export const sourceKey = (s: CompareSource): string => (s.kind === "template" ? `template:${s.name}` : s.kind);

/**
 * The query a template's own galaxy is asked with: what a landing on it asks (useWorkflow's land: the template's inputs
 * laid on a fresh draft over its model's catalogue, `template=` beside them) - the same request, so the bundles answer
 * it. Null where the catalogue given is another model's.
 */
export function templateQueryOf(cat: FlowState["cat"], template: Template): Query | null {
  if (cat.model !== template.model) return null;
  return queryOf(landOn(flow.initial(cat) as FlowState, template), template.model, template);
}

/**
 * The bar's choices: the galaxy shown (another set), every template the galaxy shown is not (one that is it, unedited,
 * would be the same galaxy), the draft - while it differs from the galaxy shown, or the galaxy shown before the last
 * Generate once the draft is that Generate's (the panes trade at a Generate) - and a picture.
 */
export function sourceItems(
  templates: Template[],
  shown: Template | null,
  edited: boolean,
  draft: { ready: boolean; previous: boolean },
  catalogued: (model: string) => boolean,
): SourceItem[] {
  const items: SourceItem[] = [
    { key: "shown", label: "this galaxy", title: "The galaxy shown, through the filter set chosen here", source: { kind: "shown" }, disabled: false },
  ];
  for (const t of templates) {
    if (shown && t.name === shown.name && !edited) continue;
    const ok = catalogued(t.model);
    items.push({
      key: `template:${t.name}`,
      label: t.label,
      title: ok ? `${t.label}, as a landing on it draws it: its inputs, its pins, its display tuning` : `${t.label}: its model's declarations are not loaded`,
      source: { kind: "template", name: t.name },
      disabled: !ok,
    });
  }
  items.push({
    key: "draft",
    label: draft.ready || !draft.previous ? "draft" : "before Generate",
    title: draft.ready
      ? "The edit panel's inputs, generated here whole beside the galaxy shown; Generate moves it to the left and this pane takes the galaxy it replaces"
      : draft.previous
        ? "The galaxy shown before the last Generate"
        : "Edit an input in Edit galaxy: the draft is drawn here beside the galaxy shown",
    source: { kind: "draft" },
    disabled: !draft.ready && !draft.previous,
  });
  items.push({ key: "picture", label: "picture", title: "A picture file from this computer at a stated band and scale; it stays in the browser", source: { kind: "picture" }, disabled: false });
  return items;
}

/** The pane's first choice: the first template the galaxy shown is not (NGC 4414 beside the Milky Way), else the galaxy shown. */
export function defaultSource(templates: Template[], shown: Template | null, edited: boolean): CompareSource {
  const other = templates.find((t) => !(shown && t.name === shown.name && !edited));
  return other ? { kind: "template", name: other.name } : { kind: "shown" };
}

/**
 * The galaxy shown before the last Generate (the draft pane's after a Generate: the panes trade). Kept across renders as
 * `track`; a landing forgets it (a landing is a new galaxy, not an edit of the last). Idempotent for a render made twice.
 */
export interface ShownTrack {
  generation: number;
  selection: number;
  query: Query | null;
  previous: Query | null;
}

export function trackShown(track: ShownTrack, now: { generation: number; selection: number; query: Query | null }): ShownTrack {
  if (now.selection !== track.selection) return { ...now, previous: null };
  if (now.generation !== track.generation) return { ...now, previous: track.query };
  return track.query === now.query ? track : { ...track, query: now.query };
}

/** What the pane asks for and names: a galaxy (its query, its template, its label), a picture, or nothing yet. */
export type PaneGalaxy = { query: Query; template: Template | null; label: string } | { picture: true } | { none: string };

/**
 * The right pane's galaxy for a source. `shown` the galaxy on screen's query and template; `draft` the edit panel's
 * query while it differs from the galaxy shown (else null); `previous` the galaxy shown before the last Generate.
 */
export function paneGalaxy(
  source: CompareSource,
  at: {
    templates: Template[];
    shown: { query: Query; template: Template | null; edited: boolean };
    draft: Query | null;
    previous: Query | null;
    catalogueOf(model: string): FlowState["cat"] | null;
  },
): PaneGalaxy {
  const name = (t: Template | null, edited: boolean) => (t ? templateLabel(t, edited) : "the galaxy shown");
  switch (source.kind) {
    case "picture":
      return { picture: true };
    case "shown":
      return { query: at.shown.query, template: at.shown.template, label: name(at.shown.template, at.shown.edited) };
    case "template": {
      const t = at.templates.find((x) => x.name === source.name) ?? null;
      const cat = t ? at.catalogueOf(t.model) : null;
      const query = t && cat ? templateQueryOf(cat, t) : null;
      return t && query ? { query, template: t, label: t.label } : { none: `${source.name}: not available` };
    }
    case "draft":
      if (at.draft) return { query: at.draft, template: at.shown.template, label: `draft of ${name(at.shown.template, false)}` };
      if (at.previous) return { query: at.previous, template: at.shown.template, label: "before the last Generate" };
      return { none: "The draft is the galaxy shown: edit an input in Edit galaxy to draw it here." };
  }
}

/** The set a source opens through: a template's own, the galaxy shown's next one (the same would be the same picture), or the shown one's. */
export function sourceSet(source: CompareSource, template: Template | null, leftSet: FilterSetName, sets: readonly FilterSetName[]): FilterSetName {
  if (source.kind === "template" && template) return template.filters;
  if (source.kind === "shown") return sets[(sets.indexOf(leftSet) + 1) % sets.length] ?? leftSet;
  return leftSet;
}

/**
 * The right pane's exposure, stops: its own template's default and the stops the user has moved the left pane's from
 * its template's default (one exposure slider, the left's, for both: each template keeps its own starting point).
 */
export function paneExposure(
  leftStops: number,
  leftTemplate: string | null,
  rightTemplate: string | null,
  map: Readonly<Record<string, number>> = TEMPLATE_EXPOSURE,
): number {
  return exposureFor(rightTemplate, map) + (leftStops - exposureFor(leftTemplate, map));
}
