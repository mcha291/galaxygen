import * as flow from "@interface/flow.js";
import { useCallback, useEffect, useRef, useState } from "react";

import { loadDeclarations, type Query } from "../api";
import { type Checkpoint, type FlowState, drawSeed, firstDifference, reopen } from "./logic";

export interface Workflow {
  model: string;
  models: string[];
  state: FlowState | null;
  /** Checkpoints whose confirmation a reopen or a model switch threw away, until confirmed again. */
  discarded: ReadonlySet<number>;
  error: string | null;
  query: Query | null;
  setModel(model: string): void;
  setValue(name: string, value: unknown): void;
  confirm(): void;
  open(n: number): void;
  reopenAt(n: number): void;
  reroll(n: number): void;
}

/**
 * React state around interface/flow.js. flow.js decides what is allowed (it
 * throws on anything D1 forbids); this hook only holds the result, loads each
 * model's declarations, and remembers which confirmations were discarded so the
 * rail can say so.
 */
export function useWorkflow(initialModel = "simple"): Workflow {
  const [model, setModelName] = useState(initialModel);
  const [models, setModels] = useState<string[]>([initialModel]);
  const [state, setState] = useState<FlowState | null>(null);
  const [discarded, setDiscarded] = useState<Set<number>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const previous = useRef<FlowState | null>(null);
  previous.current = state;

  useEffect(() => {
    const abort = new AbortController();
    loadDeclarations(model, abort.signal)
      .then(({ stages, inputs }) => {
        const cat = flow.catalogue(stages, inputs);
        const fresh = flow.initial(cat) as FlowState;
        const before = previous.current;
        setModels(stages.models);
        if (!before) {
          setState(fresh);
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
  }, [model]);

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

  const query = state ? { ...flow.query(state), model } : null;

  return { model, models, state, discarded, error, query, setModel: setModelName, setValue, confirm, open, reopenAt, reroll };
}
