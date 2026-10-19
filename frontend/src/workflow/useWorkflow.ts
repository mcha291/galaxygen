import * as flow from "@interface/flow.js";
import { useCallback, useEffect, useRef, useState } from "react";

import { loadDeclarations, loadTemplates, type Query } from "../api";
import { beginSwap, endSwap } from "../useLoad";
import { type FlowState, drawSeed } from "./logic";
import { type Template, type Templates, applyTemplate, isEdited, templateOf, templateQuery } from "./templates";

/** The galaxy on screen: the inputs it was generated from and the model that ran them. */
export interface Shown {
  state: FlowState;
  model: string;
}

export interface Workflow {
  /** The draft's model: the one the panel's inputs are of, and the one the next "Generate" runs. */
  model: string;
  models: string[];
  /** The draft: the inputs the panel shows and edits. Null until the first declarations have arrived. */
  state: FlowState | null;
  /** The galaxy on screen. It changes at a landing and at "Generate", and at nothing else. */
  shown: Shown | null;
  error: string | null;
  /**
   * The shown galaxy's query: what every loader spreads and every cache key serialises, so every view draws the
   * galaxy on screen and none draws the draft (rule D1 as amended: never half one input set and half another).
   */
  query: Query | null;
  /** The draft's query: what "Generate" will make the shown one. */
  draftQuery: Query | null;
  /** The draft differs from the galaxy shown - an input, a seed, the event list or the model. */
  dirty: boolean;
  /** The draft's model's declarations have not arrived yet: the draft is still the other model's, and cannot be generated. */
  loading: boolean;
  /** The groups (checkpoint numbers) whose inputs differ from the galaxy shown, in the catalogue's order. */
  dirtyGroups: ReadonlySet<number>;
  /** Counts the "Generate"s: a view marks the galaxy on screen stale from one until the new answers have arrived. */
  generation: number;
  /** The templates `/api/templates` publishes, in its order; empty where the API has none (one from before S54). */
  templates: Template[];
  /** The template the galaxy is, or was edited from; null where the API has none. */
  template: Template | null;
  /** The galaxy shown is no longer the template: it was generated from changed inputs or another model. */
  edited: boolean;
  /** Counts the landings on a template - the first load and every choice: a view keys its camera on it. */
  selection: number;
  /** Choose a template: the draft and the galaxy shown both land on its inputs. Its camera, lens and filter set are the view's to take. */
  selectTemplate(name: string): void;
  /** Change the draft's model: every input both models share is carried, and the draft is dirty. Nothing is regenerated. */
  setModel(model: string): void;
  setValue(name: string, value: unknown): void;
  /** Reroll one seed by name, or every seed of a group by its number. */
  reroll(which: string | number): void;
  /** The draft becomes the galaxy shown, whole. A no-op while the draft is the galaxy shown. */
  generate(): void;
  /** The draft returns to the template's inputs (the published defaults where there is none), of the template's model. */
  reset(): void;
}

/** The model the viewer starts on: the azimuthal one, the API's and the tests' default since S46 (D197). */
export const DEFAULT_MODEL = "azimuthal";

/**
 * A template landed on (S54, D213; rule D1 as amended): its inputs laid on a fresh draft through flow.setValue
 * (templates.ts applyTemplate). For `milky_way`, whose inputs are the defaults, this is the fresh draft's values.
 * A landing makes this both the draft and the galaxy shown, so a landing is clean.
 */
export function landOn(fresh: FlowState, template: Template): FlowState {
  return applyTemplate(fresh, template);
}

/**
 * What every route is sent: the whole input vector, explicitly (flow.query), the model, and - for a galaxy that
 * is a template or was started from one - `template=<name>` (S58, D217 item 2; templates.ts templateQuery). The
 * template's inputs are still laid out value by value, so an edit is one changed value in the same query and the
 * API lays the query's inputs over the template's; the parameter is what brings the template's **pins**, which
 * are no input a request may set. A galaxy started from no template (`template` null: an API from before S54)
 * is asked exactly as it was. The one source of what is asked of the API: every loader spreads the shown
 * galaxy's query and every cache key serialises it, so two galaxies that differ by a pin alone never share a
 * response.
 */
export function queryOf(state: FlowState, model: string, template: Template | null): Query {
  return templateQuery({ ...(flow.query(state) as Query), model }, template);
}

/** The draft's inputs over another model's fresh draft: every input both share is carried, nothing else. */
export function carry(fresh: FlowState, draft: FlowState): FlowState {
  const values = { ...fresh.values };
  for (const name of fresh.cat.inputs.keys()) if (name in draft.values) values[name] = draft.values[name];
  return { ...fresh, values };
}

/**
 * The groups of the draft whose inputs differ from the galaxy shown (flow.changedGroups over the two input
 * vectors as the API takes them). A model switch alone dirties no group: it is said by `dirty` and the panel's
 * model line, and the groups say which inputs moved.
 */
export function dirtyGroupsOf(draft: FlowState, shown: FlowState): Set<number> {
  return new Set(flow.changedGroups(draft, flow.query(draft), flow.query(shown)) as number[]);
}

/** The draft is still another model's than the one chosen: its declarations are on their way, and nothing is generated. */
export function isLoading(draft: FlowState | null, model: string): boolean {
  return !!draft && draft.cat.model !== model;
}

/** Whether "Generate" has anything to do: the two queries differ in any input, the model or the template. */
export function isDirty(draftQuery: Query | null, shownQuery: Query | null): boolean {
  return !!draftQuery && !!shownQuery && JSON.stringify(draftQuery) !== JSON.stringify(shownQuery);
}

/** "Generate": the draft, of its model, becomes the galaxy shown - whole, in one step. */
export function generated(draft: FlowState, model: string): Shown {
  return { state: draft, model };
}

/** "Reset to template": a fresh draft over `cat` at the template's inputs, or at the published defaults without one. */
export function resetDraft(cat: FlowState["cat"], template: Template | null): FlowState {
  const fresh = flow.initial(cat) as FlowState;
  return template ? landOn(fresh, template) : fresh;
}

export type View = "science" | "galaxy";

/** What arrives with a model's declarations: land on a template, reset the draft to one, or carry the draft. */
type Pending = { template: Template; mode: "land" | "reset" } | null;

/**
 * React state around interface/flow.js: two input sets, the **draft** the panel edits and the **shown** one whose
 * galaxy is on screen (rule D1 as amended at D232). flow.js decides what an edit may be (it throws on a value out
 * of range); this hook holds the two, loads each model's declarations, and moves the shown one at a landing and
 * at "Generate" only. Every loader takes `query`, the shown one's, so an edit moves nothing on screen until it is
 * generated, and then the whole galaxy moves at once.
 *
 * The galaxy it opens on is the default template's (S54, D213): `/api/templates` is asked first, the
 * declarations of the template's model second, and both sets land on the template's inputs (landOn). Choosing
 * another template is the same landing again. Where the API has no templates (a 404: one from before S54) the
 * hook lands on the published defaults, and `templates` is empty.
 */
export function useWorkflow(initialModel = DEFAULT_MODEL): Workflow {
  const [model, setModelName] = useState(initialModel);
  const [models, setModels] = useState<string[]>([initialModel]);
  const [state, setState] = useState<FlowState | null>(null);
  const [shown, setShown] = useState<Shown | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [generation, setGeneration] = useState(0);
  // The draft as it stands, for the declarations' handler (which carries it into another model).
  const draft = useRef<FlowState | null>(null);
  draft.current = state;
  // The templates: null until the route has answered, and still null where the API has none.
  const [templates, setTemplates] = useState<Templates | null>(null);
  const [asked, setAsked] = useState(false);
  const [chosen, setChosen] = useState<string | null>(null);
  const [selection, setSelection] = useState(0);
  // A template waiting for its model's declarations: landed on, or reset to, when they arrive.
  const pending = useRef<Pending>(null);

  // What a landing sets, wherever it happens: the draft and the galaxy shown, both at the template's inputs.
  const land = useCallback((fresh: FlowState, template: Template) => {
    const landed = landOn(fresh, template);
    endSwap(); // a landing makes a Generate under way moot: what it held is published, its failure forgotten
    setState(landed);
    setShown({ state: landed, model: template.model });
    setChosen(template.name);
    setSelection((n) => n + 1);
  }, []);

  useEffect(() => {
    const abort = new AbortController();
    loadTemplates(abort.signal)
      .then((found) => {
        const first = templateOf(found, found?.default ?? null);
        if (found && first) {
          setTemplates(found);
          pending.current = { template: first, mode: "land" };
          setModelName(first.model);
        }
        setAsked(true);
      })
      .catch((e: Error) => {
        if (!abort.signal.aborted) setError(e.message);
      });
    return () => abort.abort();
  }, []);

  useEffect(() => {
    if (!asked) return; // the template's model is not known until /api/templates has answered
    const abort = new AbortController();
    loadDeclarations(model, abort.signal)
      .then(({ stages, inputs }) => {
        const cat = flow.catalogue(stages, inputs);
        const fresh = flow.initial(cat) as FlowState;
        const before = draft.current;
        setModels(stages.models);
        const wanted = pending.current;
        if (wanted && wanted.template.model === stages.model) {
          pending.current = null;
          if (wanted.mode === "land") {
            // The first load, or a template of another model chosen: land on it (rule D1 as amended).
            land(fresh, wanted.template);
          } else {
            setState(landOn(fresh, wanted.template)); // reset to a template of another model: the draft only
          }
          return;
        }
        if (!before) {
          // No templates (an API from before S54): the first load lands on the published defaults, shown.
          setState(fresh);
          setShown({ state: fresh, model: stages.model });
          return;
        }
        // A model switch: the draft's shared inputs carried over, the galaxy shown untouched until "Generate".
        setState(carry(fresh, before));
      })
      .catch((e: Error) => {
        if (!abort.signal.aborted) setError(e.message);
      });
    return () => abort.abort();
  }, [model, asked, land]);

  // Every edit runs through flow.js; a FlowError is a bug in the panel, so it is surfaced rather than swallowed.
  const act = useCallback((fn: (s: FlowState) => FlowState) => {
    setState((s) => {
      if (!s) return s;
      try {
        setError(null);
        return fn(s);
      } catch (e) {
        setError((e as Error).message);
        return s;
      }
    });
  }, []);

  const setValue = useCallback((name: string, value: unknown) => act((s) => flow.setValue(s, name, value) as FlowState), [act]);

  const reroll = useCallback(
    (which: string | number) =>
      act((s) => flow.reroll(s, typeof which === "number" ? flow.seedsAt(s, which) : [which], () => drawSeed()) as FlowState),
    [act],
  );

  // The template the galaxy is or was started from: set at every landing (the first load, the switcher) and by
  // nothing else, so it stands through edits, generates and resets until another template is landed on. Null
  // only where the API has none.
  const template = templateOf(templates, chosen);
  const query = shown ? queryOf(shown.state, shown.model, template) : null;
  const draftQuery = state ? queryOf(state, model, template) : null;
  const dirty = isDirty(draftQuery, query);
  const loading = isLoading(state, model);
  const dirtyGroups = state && shown ? dirtyGroupsOf(state, shown.state) : new Set<number>();
  const edited = !!shown && !!template && isEdited(shown.state, shown.model, template);

  // Refused while the draft is another model's than the one chosen (its declarations still loading): the draft's
  // catalogue would be generated under the wrong model's name. The swap begins before the query moves, so every
  // answer to the new query is held until all of them have arrived (useLoad.ts, rule D1 as amended).
  const generate = useCallback(() => {
    if (!state || !dirty || isLoading(state, model)) return;
    beginSwap();
    setShown(generated(state, model));
    setGeneration((n) => n + 1);
  }, [state, model, dirty]);

  // "Reset to template": the draft at the template's inputs, of the template's model; the galaxy shown stays
  // until "Generate". A template of another model waits for that model's declarations.
  const reset = useCallback(() => {
    const now = draft.current;
    if (!now) return;
    setError(null);
    if (!template || template.model === model) {
      try {
        setState(resetDraft(now.cat, template));
      } catch (e) {
        setError((e as Error).message);
      }
      return;
    }
    pending.current = { template, mode: "reset" };
    setModelName(template.model);
  }, [template, model]);

  // Choosing a template goes through the flow's own state: a fresh draft over the same catalogue with the
  // template's inputs set, made the galaxy shown in the same update. A template of another model waits for that
  // model's declarations. The query (queryOf) stays the one source of what is asked of the API.
  const selectTemplate = useCallback(
    (name: string) => {
      const chosenTemplate = templateOf(templates, name);
      if (!chosenTemplate) return;
      const now = draft.current;
      if (now && chosenTemplate.model === model) {
        try {
          setError(null);
          pending.current = null;
          land(flow.initial(now.cat) as FlowState, chosenTemplate);
        } catch (e) {
          setError((e as Error).message);
        }
        return;
      }
      pending.current = { template: chosenTemplate, mode: "land" };
      setModelName(chosenTemplate.model);
    },
    [templates, model, land],
  );

  return {
    model,
    models,
    state,
    shown,
    error,
    query,
    draftQuery,
    dirty,
    loading,
    dirtyGroups,
    generation,
    templates: templates?.templates ?? [],
    template,
    edited,
    selection,
    selectTemplate,
    setModel: setModelName,
    setValue,
    reroll,
    generate,
    reset,
  };
}
