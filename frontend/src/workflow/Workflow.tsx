import { Check, Plus, RotateCcw, X } from "lucide-react";
import { useState } from "react";

import { Button } from "../ui/Button";
import { MergerTimeline } from "./MergerTimeline";
import {
  type Checkpoint,
  type FlowState,
  type InputDecl,
  type MergerEvent,
  SLIDER_STEPS,
  formatNumber,
  fromSlider,
  isLog,
  reopenCost,
  rerollCost,
  statusOf,
  toSlider,
} from "./logic";
import type { Workflow as WorkflowApi } from "./useWorkflow";
import styles from "./Workflow.module.css";

// What each checkpoint's preview is for, from the design brief's §1 table. The
// API declares stages, not purposes, so this is the one table the rail holds.
const PRODUCES: Record<number, string> = {
  1: "Rotation curve; smooth axisymmetric disc",
  2: "Merger history; the thick disc appears edge-on",
  3: "Gradients and histories; disc colours by [Fe/H]",
  4: "Bar and spiral arms — first recognisable galaxy",
  5: "Resolves into individual stars",
  6: "Systems become openable",
};

function badgeOf(status: string, n: number, invalidated: boolean): { label: string; tone: string } {
  if (invalidated) return { label: "invalidated", tone: "caution" };
  if (status === "locked") return { label: "locked", tone: "nominal" };
  if (status === "editing") return { label: "editing", tone: "accent" };
  if (status === "next") return { label: "next", tone: "neutral" };
  return { label: `needs ${n - 1}`, tone: "neutral" };
}

/** "5", "5 and 6", "4–6": checkpoint lists in the rail's cost lines. */
export function spanOf(ns: number[]): string {
  if (ns.length === 0) return "";
  if (ns.length === 1) return String(ns[0]);
  if (ns.length === 2) return `${ns[0]} and ${ns[1]}`;
  return `${ns[0]}–${ns[ns.length - 1]}`;
}

/** The six-checkpoint rail (design brief §1): each checkpoint, its state, its controls. */
/** `tMax` is the time axis's end from the API's grid, so the merger timeline spans the model's own history. */
export function WorkflowPanel({ wf, tMax = 13.8, className }: { wf: WorkflowApi; tMax?: number; className?: string }) {
  const panelClass = className ? `${styles.panel} ${className}` : styles.panel;
  const [askingReopen, setAskingReopen] = useState<number | null>(null);
  const [askingReroll, setAskingReroll] = useState<number | null>(null);
  const { state } = wf;

  if (!state) {
    return <div className={panelClass}><p className={styles.note}>{wf.error ?? "Loading checkpoints."}</p></div>;
  }

  const requestReopen = (n: number) => {
    setAskingReroll(null);
    if (reopenCost(state, n).length > 0) setAskingReopen(n);
    else wf.reopenAt(n);
  };

  return (
    <div className={panelClass}>
      <div className={styles.heading}>Generation · {state.cat.checkpoints.length} checkpoints</div>
      {wf.error && <p className={styles.fault}>{wf.error}</p>}

      {state.cat.checkpoints.map((cp) => {
        const status = statusOf(state, cp.n);
        const invalidated = wf.discarded.has(cp.n) && status !== "locked";
        const decls = cp.inputs.map((name) => state.cat.inputs.get(name)!);
        const seedOnly = decls.every((d) => d.kind === "seed");
        const seed = decls.find((d) => d.kind === "seed");
        // As in the design, only the checkpoint in hand is expanded; the rest are one row each.
        const open = cp.n === state.current;
        const badge = badgeOf(status, cp.n, invalidated);

        return (
          <section key={cp.n} className={styles.checkpoint} data-open={open || undefined}>
            <div className={styles.head}>
              <button
                type="button"
                className={styles.chip}
                data-status={status}
                disabled={status === "blocked"}
                title={chipTitle(status, cp.n)}
                onClick={() => (status === "locked" && cp.n !== state.current ? requestReopen(cp.n) : wf.open(cp.n))}
              >
                {status === "locked" ? <Check aria-label="locked" /> : cp.n}
              </button>
              <div className={styles.title}>
                <div className={styles.titleRow}>
                  <span className={styles.name} data-status={status}>{cp.name}</span>
                  <span className={styles.badge} data-tone={badge.tone}>{badge.label}</span>
                </div>
                {invalidated && (
                  <div className={styles.caution}>Its confirmation was discarded by an earlier change. Confirm it again to lock.</div>
                )}
                {open && (
                  <>
                    <div className={styles.stages}>{cp.stages.join(" · ")}</div>
                    {PRODUCES[cp.n] && <div className={styles.produces}>{PRODUCES[cp.n]}</div>}
                  </>
                )}
              </div>
            </div>

            {askingReopen === cp.n && !open && (
              <div className={`${styles.ask} ${styles.askOutside}`}>
                <p>
                  Checkpoint {spanOf(reopenCost(state, cp.n))} {reopenCost(state, cp.n).length > 1 ? "are" : "is"} confirmed.
                  Reopening {cp.n} discards {reopenCost(state, cp.n).length > 1 ? "them" : "it"}.
                </p>
                <div className={styles.actions}>
                  <Button variant="primary" onClick={() => { setAskingReopen(null); wf.reopenAt(cp.n); }}>Reopen and discard</Button>
                  <Button variant="ghost" onClick={() => setAskingReopen(null)}>Cancel</Button>
                </div>
              </div>
            )}

            {open && (
              <div className={styles.body}>
                {seedOnly && status === "editing" && (
                  <p className={styles.seedOnly}>
                    No scalar controls at this checkpoint. Its output is determined by everything confirmed above plus one
                    seed, <code>{seed?.name}</code>. A reroll is the only edit there is.
                  </p>
                )}

                {decls.map((decl) => (
                  <Control key={decl.name} decl={decl} state={state} disabled={status === "locked"} wf={wf} tMax={tMax} />
                ))}

                <div className={styles.actions}>
                  {status === "editing" && (
                    <Button variant="primary" onClick={() => { setAskingReroll(null); wf.confirm(); }}>
                      Confirm &amp; lock
                    </Button>
                  )}
                  {status === "locked" && <Button onClick={() => requestReopen(cp.n)}>Reopen to edit</Button>}
                  {status === "editing" && seed && (
                    <Button icon={<RotateCcw />} onClick={() => { setAskingReopen(null); setAskingReroll(cp.n); }}>
                      Reroll seed
                    </Button>
                  )}
                </div>

                {askingReopen === cp.n && open && (
                  <div className={styles.ask}>
                    <p>
                      Checkpoint {spanOf(reopenCost(state, cp.n))} {reopenCost(state, cp.n).length > 1 ? "are" : "is"} confirmed.
                      Reopening {cp.n} discards {reopenCost(state, cp.n).length > 1 ? "them" : "it"}.
                    </p>
                    <div className={styles.actions}>
                      <Button variant="primary" onClick={() => { setAskingReopen(null); wf.reopenAt(cp.n); }}>Reopen and discard</Button>
                      <Button variant="ghost" onClick={() => setAskingReopen(null)}>Cancel</Button>
                    </div>
                  </div>
                )}

                {askingReroll === cp.n && seed && (
                  <RerollAsk
                    state={state}
                    cp={cp}
                    seed={seed}
                    onReroll={() => { setAskingReroll(null); wf.reroll(cp.n); }}
                    onCancel={() => setAskingReroll(null)}
                  />
                )}
              </div>
            )}
          </section>
        );
      })}
    </div>
  );
}

function chipTitle(status: string, n: number): string {
  if (status === "locked") return `Reopen checkpoint ${n}`;
  if (status === "blocked") return `Needs checkpoint ${n - 1} confirmed first`;
  return `Open checkpoint ${n}`;
}

function RerollAsk({ state, cp, seed, onReroll, onCancel }: {
  state: FlowState; cp: Checkpoint; seed: InputDecl; onReroll(): void; onCancel(): void;
}) {
  const later = rerollCost(state, cp.n);
  return (
    <div className={styles.ask}>
      <p>
        <code>{seed.name}</code> gets a new value. {later.length > 0
          ? `Checkpoint ${cp.n} and ${later.length > 1 ? "checkpoints" : "checkpoint"} ${spanOf(later)} are regenerated; nothing earlier changes.`
          : `Checkpoint ${cp.n} is regenerated; nothing earlier changes.`}
      </p>
      <div className={styles.actions}>
        <Button variant="primary" onClick={onReroll}>Reroll</Button>
        <Button variant="ghost" onClick={onCancel}>Cancel</Button>
      </div>
    </div>
  );
}

function Control({ decl, state, disabled, wf, tMax }: { decl: InputDecl; state: FlowState; disabled: boolean; wf: WorkflowApi; tMax: number }) {
  const value = state.values[decl.name];
  const unit = decl.unit_display && decl.unit !== "dimensionless" ? decl.unit_display : "";

  if (decl.kind === "events") {
    return <MergerList decl={decl} events={value as MergerEvent[]} disabled={disabled} wf={wf} tMax={tMax} />;
  }

  return (
    <div className={styles.control} data-disabled={disabled || undefined}>
      <div className={styles.controlRow}>
        <span className={styles.label} title={decl.name}>{decl.label}</span>
        <span className={styles.value}>{decl.kind === "seed" ? String(value) : formatNumber(value as number)}</span>
        <span className={styles.unit}>{decl.kind === "seed" ? "seed" : unit}</span>
      </div>
      {decl.kind === "control" && (
        <>
          <input
            type="range"
            className={styles.slider}
            min={0}
            max={SLIDER_STEPS}
            step={1}
            value={toSlider(decl, value as number)}
            disabled={disabled}
            aria-label={decl.label}
            onChange={(e) => wf.setValue(decl.name, fromSlider(decl, Number(e.target.value)))}
          />
          <div className={styles.range}>
            <span>{formatNumber(decl.lo as number)}</span>
            {isLog(decl) && <span>log scale</span>}
            <span>{formatNumber(decl.hi as number)}</span>
          </div>
        </>
      )}
      <details className={styles.about}>
        <summary>About</summary>
        {decl.about}
      </details>
    </div>
  );
}

function MergerList({ decl, events, disabled, wf, tMax }: { decl: InputDecl; events: MergerEvent[]; disabled: boolean; wf: WorkflowApi; tMax: number }) {
  const [selected, setSelected] = useState<number | null>(null);
  const update = (i: number, key: keyof MergerEvent, raw: string | number) => {
    const next = events.map((e, k) => (k === i ? { ...e, [key]: Number(raw) } : e));
    wf.setValue(decl.name, next);
  };
  const remove = (i: number) => wf.setValue(decl.name, events.filter((_, k) => k !== i));
  const add = () => {
    const last = events[events.length - 1];
    wf.setValue(decl.name, [...events, { time: Math.min((last?.time ?? 4) + 1, 13), mass_ratio: 0.05, gas_fraction: 0.1 }]);
  };

  return (
    <div className={styles.control} data-disabled={disabled || undefined}>
      <div className={styles.controlRow}>
        <span className={styles.label} title={decl.name}>{decl.label}</span>
        <span className={styles.value}>{events.length}</span>
      </div>
      <div className={styles.unit}>exempt from the input ceiling</div>
      <MergerTimeline
        events={events}
        tMax={tMax}
        selected={selected}
        disabled={disabled}
        onSelect={setSelected}
        onMove={(i, time) => update(i, "time", time)}
      />
      <table className={styles.events}>
        <thead>
          <tr><th>time / Gyr</th><th>mass ratio</th><th>gas fraction</th><th aria-label="remove" /></tr>
        </thead>
        <tbody>
          {events.map((e, i) => (
            <tr key={i} title={e.about} aria-selected={i === selected} onFocus={() => setSelected(i)}>
              <td><input type="number" min={0} step={0.1} value={e.time} disabled={disabled} onChange={(x) => update(i, "time", x.target.value)} /></td>
              <td><input type="number" min={0.001} max={1} step={0.01} value={e.mass_ratio} disabled={disabled} onChange={(x) => update(i, "mass_ratio", x.target.value)} /></td>
              <td><input type="number" min={0} max={1} step={0.01} value={e.gas_fraction} disabled={disabled} onChange={(x) => update(i, "gas_fraction", x.target.value)} /></td>
              <td>
                <button type="button" className={styles.remove} disabled={disabled} aria-label={`Remove event ${i + 1}`} onClick={() => remove(i)}>
                  <X />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {events.length === 0 && <p className={styles.note}>No mergers. A quiescent history is a legitimate galaxy.</p>}
      {!disabled && <Button variant="ghost" icon={<Plus />} onClick={add}>Add event</Button>}
      <details className={styles.about}>
        <summary>About</summary>
        {decl.about}
      </details>
    </div>
  );
}
