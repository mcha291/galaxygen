import { ChevronDown, ChevronRight, Eye, Plus, RotateCcw, Shuffle, X } from "lucide-react";
import { useState } from "react";

import { Button } from "../ui/Button";
import { MergerTimeline } from "./MergerTimeline";
import { type InputDecl, type MergerEvent, SLIDER_STEPS, formatNumber, fromSlider, isLog, toSlider } from "./logic";
import { pinWords } from "./templates";
import type { Workflow as WorkflowApi } from "./useWorkflow";
import styles from "./Workflow.module.css";

// What each group's previews show, from the design brief's §1 table. The API declares stages, not purposes, so
// this is the one table the panel holds; the Science tab writes it under the group's name.
export const PRODUCES: Record<number, string> = {
  1: "Rotation curve; smooth axisymmetric disc",
  2: "Merger history; the thick disc appears edge-on",
  3: "Bar and spiral arms, on the disc's own dynamics",
  4: "Gradients and histories; disc colours by [Fe/H] — first recognisable galaxy",
  5: "Resolves into individual stars",
  6: "Planetary systems for every star",
};

type Fields = Parameters<typeof pinWords>[1];

interface Props {
  wf: WorkflowApi;
  /** The time axis's end from the API's grid, so the merger timeline spans the model's own history. */
  tMax?: number;
  className?: string;
  /** The field declarations, for the pins' words (templates.ts pinWords). */
  fields?: Fields;
  /** The group whose previews the Science tab shows, and how to choose another; absent where there are none. */
  viewing?: number | null;
  onView?(n: number): void;
  /** Close the panel (the Galaxy view's drawer); absent where the panel is part of the page. */
  onClose?(): void;
}

/**
 * The edit panel (BUILD_III Phase V9, rule D1 as amended at D232): every input in its registry group - the
 * checkpoint names `/api/stages` declares, kept as names with no order and no status - every control enabled at
 * all times, each seed a reroll, the template's pins read-only with their source. One "Generate", enabled while
 * the draft differs from the galaxy shown, with a mark on each group that changed; "Reset to template" returns the
 * draft to the template's inputs. Nothing here confirms, locks or reopens: the galaxy on screen is the shown one's
 * until "Generate" makes the draft the shown, whole.
 */
export function WorkflowPanel({ wf, tMax = 13.8, className, fields, viewing = null, onView, onClose }: Props) {
  const panelClass = className ? `${styles.panel} ${className}` : styles.panel;
  // Folded groups: a convenience of this panel's, no state of the galaxy's. Every group starts open.
  const [folded, setFolded] = useState<ReadonlySet<number>>(new Set());
  const { state } = wf;

  if (!state) {
    return <div className={panelClass}><p className={styles.note}>{wf.error ?? "Loading the inputs."}</p></div>;
  }

  const fold = (n: number) =>
    setFolded((f) => {
      const next = new Set(f);
      if (!next.delete(n)) next.add(n);
      return next;
    });
  const shownModel = wf.shown?.model ?? wf.model;
  const changed = state.cat.checkpoints.filter((cp) => wf.dirtyGroups.has(cp.n)).map((cp) => cp.name);
  const resetLabel = wf.template ? "Reset to template" : "Reset to defaults";

  return (
    <div className={panelClass} aria-label="Edit galaxy">
      <div className={styles.heading}>
        <span>Edit galaxy · {state.cat.checkpoints.length} groups</span>
        {onClose && (
          <button type="button" className={styles.close} aria-label="Close the edit panel" onClick={onClose}>
            <X />
          </button>
        )}
      </div>

      <div className={styles.bar}>
        <div className={styles.actions}>
          <Button
            variant="primary"
            disabled={!wf.dirty}
            title={wf.dirty ? "Regenerate the galaxy whole from the inputs shown" : "The inputs are the galaxy on screen: change one to generate"}
            onClick={wf.generate}
          >
            Generate
          </Button>
          <Button
            icon={<RotateCcw />}
            title={wf.template ? `Return every input to the ${wf.template.label} template's` : "Return every input to its published default"}
            onClick={wf.reset}
          >
            {resetLabel}
          </Button>
        </div>
        <p className={styles.state} data-dirty={wf.dirty || undefined} role="status">
          {wf.dirty
            ? `Changed: ${[...changed, ...(wf.model !== shownModel ? [`the model (${wf.model}; on screen ${shownModel})`] : [])].join(", ") || "the template"}.`
            : "The inputs are the galaxy on screen."}
        </p>
      </div>

      {wf.error && <p className={styles.fault}>{wf.error}</p>}

      {wf.template && wf.template.pins.length > 0 && (
        <section className={styles.pins} aria-label="Pins">
          <div className={styles.pinsHead}>Pinned by {wf.template.label} · read-only</div>
          {wf.template.pins.map((p) => (
            <div key={p.name} className={styles.pin}>
              <div>{pinWords(p, fields)}</div>
              {p.source && <div className={styles.source}>Source: {p.source}</div>}
            </div>
          ))}
        </section>
      )}

      {state.cat.checkpoints.map((cp) => {
        const decls = cp.inputs.map((name) => state.cat.inputs.get(name)!);
        const seeds = decls.filter((d) => d.kind === "seed");
        const open = !folded.has(cp.n);
        const dirty = wf.dirtyGroups.has(cp.n);
        return (
          <section key={cp.n} className={styles.group} data-dirty={dirty || undefined} data-viewing={viewing === cp.n || undefined} aria-label={cp.name}>
            <div className={styles.head}>
              <button type="button" className={styles.fold} aria-expanded={open} aria-label={`${open ? "Fold" : "Open"} ${cp.name}`} onClick={() => fold(cp.n)}>
                {open ? <ChevronDown /> : <ChevronRight />}
              </button>
              <div className={styles.title}>
                <div className={styles.titleRow}>
                  <span className={styles.name}>{cp.name}</span>
                  {dirty && <span className={styles.badge} data-tone="caution" title="An input here differs from the galaxy on screen">changed</span>}
                  {onView && (
                    <button
                      type="button"
                      className={styles.look}
                      aria-pressed={viewing === cp.n}
                      title={`Show ${cp.name}'s previews of the galaxy on screen`}
                      onClick={() => onView(cp.n)}
                    >
                      <Eye /> previews
                    </button>
                  )}
                </div>
                {open && <div className={styles.stages}>{cp.stages.join(" · ")}</div>}
              </div>
            </div>

            {open && (
              <div className={styles.body}>
                {decls.length === 0 && <p className={styles.note}>No input belongs to this group.</p>}
                {decls.filter((d) => d.kind !== "seed").map((decl) => (
                  <Control key={decl.name} decl={decl} value={state.values[decl.name]} wf={wf} tMax={tMax} />
                ))}
                {seeds.map((decl) => (
                  <Seed key={decl.name} decl={decl} value={state.values[decl.name]} wf={wf} />
                ))}
              </div>
            )}
          </section>
        );
      })}
    </div>
  );
}

/** A seed: its value and a reroll of that seed alone, named (checkpoint 3 has two since S55). */
function Seed({ decl, value, wf }: { decl: InputDecl; value: unknown; wf: WorkflowApi }) {
  return (
    <div className={styles.control}>
      <div className={styles.controlRow}>
        <span className={styles.label} title={decl.name}>{decl.label}</span>
        <span className={styles.value}>{String(value)}</span>
        <span className={styles.unit}>seed</span>
      </div>
      <div className={styles.actions}>
        <Button icon={<Shuffle />} aria-label={`Reroll ${decl.name}`} title={`Draw a new ${decl.name}`} onClick={() => wf.reroll(decl.name)}>
          Reroll <code className={styles.code}>{decl.name}</code>
        </Button>
      </div>
      <details className={styles.about}>
        <summary>About</summary>
        {decl.about}
      </details>
    </div>
  );
}

function Control({ decl, value, wf, tMax }: { decl: InputDecl; value: unknown; wf: WorkflowApi; tMax: number }) {
  const unit = decl.unit_display && decl.unit !== "dimensionless" ? decl.unit_display : "";

  if (decl.kind === "events") {
    return <MergerList decl={decl} events={value as MergerEvent[]} wf={wf} tMax={tMax} />;
  }

  return (
    <div className={styles.control}>
      <div className={styles.controlRow}>
        <span className={styles.label} title={decl.name}>{decl.label}</span>
        <span className={styles.value}>{formatNumber(value as number)}</span>
        <span className={styles.unit}>{unit}</span>
      </div>
      <input
        type="range"
        className={styles.slider}
        min={0}
        max={SLIDER_STEPS}
        step={1}
        value={toSlider(decl, value as number)}
        aria-label={decl.label}
        onChange={(e) => wf.setValue(decl.name, fromSlider(decl, Number(e.target.value)))}
      />
      <div className={styles.range}>
        <span>{formatNumber(decl.lo as number)}</span>
        {isLog(decl) && <span>log scale</span>}
        <span>{formatNumber(decl.hi as number)}</span>
      </div>
      <details className={styles.about}>
        <summary>About</summary>
        {decl.about}
      </details>
    </div>
  );
}

function MergerList({ decl, events, wf, tMax }: { decl: InputDecl; events: MergerEvent[]; wf: WorkflowApi; tMax: number }) {
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
    <div className={styles.control}>
      <div className={styles.controlRow}>
        <span className={styles.label} title={decl.name}>{decl.label}</span>
        <span className={styles.value}>{events.length}</span>
      </div>
      <div className={styles.unit}>exempt from the input ceiling</div>
      <MergerTimeline
        events={events}
        tMax={tMax}
        selected={selected}
        disabled={false}
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
              <td><input type="number" min={0} step={0.1} value={e.time} aria-label={`Event ${i + 1} time`} onChange={(x) => update(i, "time", x.target.value)} /></td>
              <td><input type="number" min={0.001} max={1} step={0.01} value={e.mass_ratio} aria-label={`Event ${i + 1} mass ratio`} onChange={(x) => update(i, "mass_ratio", x.target.value)} /></td>
              <td><input type="number" min={0} max={1} step={0.01} value={e.gas_fraction} aria-label={`Event ${i + 1} gas fraction`} onChange={(x) => update(i, "gas_fraction", x.target.value)} /></td>
              <td>
                <button type="button" className={styles.remove} aria-label={`Remove event ${i + 1}`} onClick={() => remove(i)}>
                  <X />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {events.length === 0 && <p className={styles.note}>No mergers. A quiescent history is a legitimate galaxy.</p>}
      <Button variant="ghost" icon={<Plus />} onClick={add}>Add event</Button>
      <details className={styles.about}>
        <summary>About</summary>
        {decl.about}
      </details>
    </div>
  );
}
