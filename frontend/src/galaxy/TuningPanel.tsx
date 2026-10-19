import { useEffect, useState } from "react";

import type { MarchStats } from "./FieldVolume";
import { gpuWords } from "./gpuTimer";
import {
  type RangeControl,
  type Tuning,
  type TuningControl,
  TUNING_CONTROLS,
  TUNING_DEFAULTS,
  changed,
  positionOf,
  valueAt,
} from "./tuning";
import styles from "./GalaxyTab.module.css";

/** A value that follows `value` once it has held still for `ms`: a recompile or a request waits for the slider to settle. */
export function useDebounced<T>(value: T, ms: number): T {
  const [settled, setSettled] = useState(value);
  useEffect(() => {
    if (Object.is(value, settled)) return;
    const timer = setTimeout(() => setSettled(value), ms);
    return () => clearTimeout(timer);
  }, [value, settled, ms]);
  return settled;
}

// "Components" holds the brightest mode's layer intensities (D205); its switches are in the mode's own section.
const GROUPS = ["March", "Light", "Bloom and tone", "Points", "Components"] as const;

function shown(control: RangeControl, value: number): string {
  const v = Number((value * (control.scale ?? 1)).toPrecision(4));
  if (control.unit === "×") return `×${v}`;
  return control.unit ? `${v} ${control.unit}` : `${v}`;
}

function describe(control: TuningControl, value: Tuning[keyof Tuning]): string {
  if (control.kind === "range") return shown(control, value as number);
  if (control.kind === "toggle") return value ? "on" : "off";
  return control.options.find((o) => o.value === value)?.label ?? String(value);
}

interface Props {
  tuning: Tuning;
  onChange(t: Tuning): void;
  /** The field's last re-march, filled in by FieldVolume; read while the section is open. */
  stats: MarchStats;
  /** What the copy box names beside the changed choices (S67, D227): the template tuned on, its filter set and the
   * exposure's stops, which live outside the tuning object, so a pasted box says which galaxy it was found on. */
  template?: string | null;
  filterSet?: string;
  exposure?: number;
  /** The defaults the choices are compared with and reset to: the template's own (S67, D227 R4: tuning.ts defaultsFor). */
  defaults?: Tuning;
}

/**
 * The Tuning section (D199): the field view's display choices as controls, experimental, so the owner can
 * find the combination to rule on. Nothing here is physics (rule D5). Untouched, every value is the
 * view's own from before the panel; the changed ones are shown as JSON to copy into a report.
 */
export function TuningPanel({ tuning, onChange, stats, template, filterSet, exposure, defaults = TUNING_DEFAULTS }: Props) {
  const [open, setOpen] = useState(false);
  const [march, setMarch] = useState<MarchStats>({ ...stats });
  useEffect(() => {
    if (!open) return;
    const read = () => setMarch((m) => (m.width === stats.width && m.height === stats.height && m.ms === stats.ms && m.gpuMs === stats.gpuMs && m.gpuAvailable === stats.gpuAvailable ? m : { ...stats }));
    read();
    const timer = setInterval(read, 500);
    return () => clearInterval(timer);
  }, [open, stats]);

  const set = (key: keyof Tuning, value: Tuning[keyof Tuning] | string) => onChange({ ...tuning, [key]: value } as Tuning);
  const diff = changed(tuning, defaults);

  return (
    <div className={styles.section}>
      <button type="button" className={styles.tuningToggle} aria-expanded={open} onClick={() => setOpen((o) => !o)}>
        <span className={styles.label}>Tuning — display choices (experimental)</span>
        <span className={styles.muted}>{open ? "−" : "+"}</span>
      </button>
      {open && (
        <>
          <p className={styles.muted}>
            How the field is sampled and drawn, not what the model publishes. The defaults are today's view; move any and
            report the set below.
          </p>
          {GROUPS.map((group) => (
            <div key={group} className={styles.tuningGroup}>
              <div className={styles.label}>{group}</div>
              {TUNING_CONTROLS.filter((c) => c.group === group && !c.switch).map((control) => {
                const value = tuning[control.key];
                const fallback = defaults[control.key];
                return (
                  <div key={control.key} className={styles.tuningRow} title={control.about}>
                    <div className={styles.zoomHead}>
                      <span className={styles.tuningName}>{control.label}</span>
                      <span className={styles.value}>{describe(control, value)}</span>
                      {value !== fallback && (
                        <button
                          type="button"
                          className={styles.tuningDefault}
                          title={`Back to the default, ${describe(control, fallback)}`}
                          onClick={() => set(control.key, fallback)}
                        >
                          default
                        </button>
                      )}
                    </div>
                    {control.kind === "range" &&
                      (control.log ? (
                        <input
                          type="range"
                          className={styles.slider}
                          min={0}
                          max={1000}
                          value={positionOf(control, value as number)}
                          aria-label={control.label}
                          onChange={(e) => set(control.key, valueAt(control, Number(e.target.value)))}
                        />
                      ) : (
                        <input
                          type="range"
                          className={styles.slider}
                          min={control.min}
                          max={control.max}
                          step={control.step}
                          value={value as number}
                          aria-label={control.label}
                          onChange={(e) => set(control.key, Number(e.target.value))}
                        />
                      ))}
                    {control.kind === "toggle" && (
                      <div className={styles.pair}>
                        {[true, false].map((on) => (
                          <button key={String(on)} type="button" aria-pressed={value === on} onClick={() => set(control.key, on)}>
                            {on ? "on" : "off"}
                          </button>
                        ))}
                      </div>
                    )}
                    {control.kind === "select" && (
                      <div className={styles.chips}>
                        {control.options.map((o) => (
                          <button key={o.value} type="button" aria-pressed={value === o.value} onClick={() => set(control.key, o.value)}>
                            {o.label}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
          <div className={styles.tuningGroup}>
            <div className={styles.muted} title="The march target's size, the last re-march's CPU-side time (the render call) and, since S67, the GPU's time for it from a timer query (EXT_disjoint_timer_query_webgl2), where the browser gives one">
              march: {march.width}×{march.height} px, {march.ms.toFixed(1)} ms CPU, {gpuWords(march.gpuMs, march.gpuAvailable ?? false)}
            </div>
            <div className={styles.pair}>
              <button type="button" disabled={Object.keys(diff).length === 0} onClick={() => onChange({ ...defaults })}>
                Reset all
              </button>
            </div>
            <textarea
              className={styles.tuningCopy}
              readOnly
              rows={3}
              value={JSON.stringify({ template: template ?? null, filters: filterSet ?? null, exposure: exposure ?? 0, ...diff })}
              aria-label="The changed display choices, as JSON"
              onFocus={(e) => e.currentTarget.select()}
            />
          </div>
        </>
      )}
    </div>
  );
}
