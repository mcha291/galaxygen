import * as flow from "@interface/flow.js";
import { useCallback, useEffect, useRef, useState } from "react";

import { loadDeclarations, loadTemplates, type Query } from "../api";
import { type Checkpoint, type FlowState, drawSeed, firstDifference, reopen } from "./logic";
import { type Template, type Templates, applyTemplate, isEdited, templateOf } from "./templates";

export interface Workflow {
  model: string;
  models: string[];
  state: FlowState | null;
  /** Checkpoints whose confirmation a reopen or a model switch threw away, until confirmed again. */
  discarded: ReadonlySet<number>;
  error: string | null;
  query: Query | null;
  /** The templates `/api/templates` publishes, in its order; empty where the API has none (one from before S54). */
  templates: Template[];
  /** The template the galaxy is, or was edited from; null where the API has none. */
  template: Template | null;
  /** The galaxy asked for is no longer the template: an input or the model has been changed since it was chosen. */
  edited: boolean;
  /** Counts the landings on a template - the first load and every choice: a view keys its camera on it. */
  selection: number;
  /** Choose a template: regenerate at its inputs, every checkpoint confirmed. Its camera, lens and filter set are the view's to take. */
  selectTemplate(name: string): void;
  setModel(model: string): void;
  setValue(name: string, value: unknown): void;
  confirm(): void;
  open(n: number): void;
  reopenAt(n: number): void;
  reroll(n: number): void;
}

/** The model the viewer starts on: the azimuthal one, the API's and the tests' default since S46 (D197). */
export const DEFAULT_MODEL = "azimuthal";

/**
 * The default galaxy (D198, rule D1 as amended): every checkpoint confirmed at its
 * defaults, by applying flow.confirm once per checkpoint — the same step the
 * "Confirm & lock" button takes, checkpoint by checkpoint, so the result is
 * exactly the state those clicks would have reached (confirmed = last, current =
 * last; flow.confirm does not advance past the last checkpoint). Never a
 * hand-built state: that would drift from flow.js.
 */
export function generateDefault(s: FlowState): FlowState {
  let next = s;
  for (let k = 0; k < s.cat.checkpoints.length; k += 1) next = flow.confirm(next) as FlowState;
  return next;
}

/**
 * A template landed on (S54, D213; rule D1 as amended at D212): its inputs laid on a fresh flow through
 * flow.setValue (templates.ts applyTemplate), then every checkpoint confirmed as above. For `milky_way`, whose
 * inputs are the defaults, this is generateDefault's state exactly.
 */
export function landOn(fresh: FlowState, template: Template): FlowState {
  return generateDefault(applyTemplate(fresh, template));
}

/** Generation is done when every checkpoint is confirmed; the Galaxy tab shows that result only. */
export function isGenerated(s: FlowState | null): boolean {
  const last = s?.cat.checkpoints.length ?? 0;
  return !!s && last > 0 && s.confirmed === last;
}

export type View = "preview" | "science" | "galaxy";

/**
 * The tab the viewer settles on. Reopening a checkpoint un-generates the galaxy,
 * so the Galaxy tab closes to the Preview; nothing else moves the user. Since
 * D198 a generated galaxy no longer sends the Preview tab back to the Galaxy:
 * "Edit galaxy" lands there with the confirmations kept.
 */
export function settleView(view: View, generated: boolean): View {
  return view === "galaxy" && !generated ? "preview" : view;
}

/** "Edit galaxy": open the staged generation. A tab switch only — the flow state is not touched. */
export const EDIT_VIEW: View = "preview";

/**
 * React state around interface/flow.js. flow.js decides what is allowed (it
 * throws on anything D1 forbids); this hook only holds the result, loads each
 * model's declarations, and remembers which confirmations were discarded so the
 * rail can say so. The first declarations to arrive are confirmed through to the
 * last checkpoint (generateDefault), so the viewer opens on a generated galaxy.
 *
 * Since S54 (D213) the galaxy it opens on is the default template's: `/api/templates`
 * is asked first, the declarations of the template's model second, and the flow
 * lands on the template's inputs (landOn). Choosing another template is the same
 * landing again. Where the API has no templates (a 404: one from before S54) the
 * hook lands on the published defaults as it did, and `templates` is empty.
 */
export function useWorkflow(initialModel = DEFAULT_MODEL): Workflow {
  const [model, setModelName] = useState(initialModel);
  const [models, setModels] = useState<string[]>([initialModel]);
  const [state, setState] = useState<FlowState | null>(null);
  const [discarded, setDiscarded] = useState<Set<number>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const previous = useRef<FlowState | null>(null);
  previous.current = state;
  // The templates: null until the route has answered, and still null where the API has none.
  const [templates, setTemplates] = useState<Templates | null>(null);
  const [asked, setAsked] = useState(false);
  const [chosen, setChosen] = useState<string | null>(null);
  const [selection, setSelection] = useState(0);
  // A template waiting for its model's declarations: landed on when they arrive.
  const pending = useRef<Template | null>(null);

  // What a landing sets, wherever it happens: the flow at the template's inputs, nothing discarded.
  const land = useCallback((fresh: FlowState, template: Template) => {
    setState(landOn(fresh, template));
    setDiscarded(new Set());
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
          pending.current = first;
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
        const before = previous.current;
        setModels(stages.models);
        const template = pending.current;
        if (template && template.model === stages.model) {
          // The first load, or a template of another model chosen: land on it (rule D1 as amended).
          pending.current = null;
          land(fresh, template);
          return;
        }
        if (!before) {
          // No templates (an API from before S54): the first load lands on the default galaxy,
          // generated (D198); a model switch below keeps its own behaviour.
          setState(generateDefault(fresh));
          return;
        }
        // A model switch keeps every value and every confirmation up to the first
        // checkpoint where the two models run different stages; from there on it
        // is a different galaxy, so that confirmation and the later ones go.
        let carried = { ...fresh, values: { ...fresh.values, ...before.values }, confirmed: before.confirmed, current: before.current };
        const d = firstDifference(before.cat.checkpoints, cat.checkpoints as Checkpoint[]);
        if (d !== null && before.confirmed >= d) {
          const lost = Array.from({ length: before.confirmed - d + 1 }, (_, i) => d + i);
          carried = flow.reopen(carried, d) as FlowState;
          setDiscarded((s) => new Set([...s, ...lost]));
        }
        setState(carried);
      })
      .catch((e: Error) => {
        if (!abort.signal.aborted) setError(e.message);
      });
    return () => abort.abort();
  }, [model, asked, land]);

  // Every action runs through flow.js; a FlowError is a bug in the panel, so it
  // is surfaced rather than swallowed.
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

  const confirm = useCallback(() => {
    act((s) => {
      setDiscarded((d) => new Set([...d].filter((n) => n !== s.current)));
      return flow.confirm(s) as FlowState;
    });
  }, [act]);

  const open = useCallback((n: number) => act((s) => flow.goTo(s, n) as FlowState), [act]);

  const reopenAt = useCallback((n: number) => {
    act((s) => {
      const result = reopen(s, n);
      setDiscarded((d) => new Set([...[...d].filter((k) => k !== n), ...result.discarded]));
      return result.state;
    });
  }, [act]);

  const reroll = useCallback((n: number) => act((s) => flow.reroll(s, flow.seedsAt(s, n), () => drawSeed()) as FlowState), [act]);

  // Choosing a template goes through the flow's own state: a fresh flow over the same catalogue, the
  // template's inputs set, every checkpoint confirmed. A template of another model waits for that model's
  // declarations. The query below stays the one source of what is asked of the API.
  const selectTemplate = useCallback(
    (name: string) => {
      const template = templateOf(templates, name);
      if (!template) return;
      const now = previous.current;
      if (now && template.model === model) {
        try {
          setError(null);
          pending.current = null;
          land(flow.initial(now.cat) as FlowState, template);
        } catch (e) {
          setError((e as Error).message);
        }
        return;
      }
      pending.current = template;
      setModelName(template.model);
    },
    [templates, model, land],
  );

  // The whole input vector, explicitly, and the model: what every route is sent. A template is its inputs
  // here, not a `template=` parameter, so an edit is one changed value in the same query, and an API from
  // before the templates is asked exactly as it was.
  const query = state ? { ...flow.query(state), model } : null;
  const template = templateOf(templates, chosen);
  const edited = !!state && !!template && isEdited(state, model, template);

  return {
    model,
    models,
    state,
    discarded,
    error,
    query,
    templates: templates?.templates ?? [],
    template,
    edited,
    selection,
    selectTemplate,
    setModel: setModelName,
    setValue,
    confirm,
    open,
    reopenAt,
    reroll,
  };
}
