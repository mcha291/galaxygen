import { useEffect, useState } from "react";

import { Button } from "../ui/Button";
import { Select } from "../ui/Select";
import { Switch } from "../ui/Switch";
import type { MarchStats } from "./FieldVolume";
import { gpuWords } from "./gpuTimer";
import { illControls } from "./illustrative";
import {
  type Combination,
  type Look,
  type RangeControl,
  type Tuning,
  type TuningControl,
  TUNING_CONTROLS,
  TUNING_DEFAULTS,
  changed,
  copyBoxText as copyBoxTextOfLook,
  parseCombination,
  positionOf,
  valueAt,
} from "./tuning";
import styles from "./GalaxyTab.module.css";

/** A value that follows `value` once it has held still for `ms`: a recompile or a request waits for the slider to settle. */
// Since S105 (fix R1) a `key`: while it changes (another template or look) the value is taken at once, not waited for.
export function useDebounced<T>(value: T, ms: number, key?: unknown): T {
  const [settled, setSettled] = useState<{ value: T; key: unknown }>({ value, key });
  const rekeyed = !Object.is(settled.key, key);
  if (rekeyed) setSettled({ value, key });
  useEffect(() => {
    if (rekeyed || Object.is(value, settled.value)) return;
    const timer = setTimeout(() => setSettled({ value, key }), ms);
    return () => clearTimeout(timer);
  }, [value, settled, ms, key, rekeyed]);
  return rekeyed ? value : settled.value;
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
  /** A new tuning, and (a pasted combination naming another, S105) the look it is for; absent, the look shown. */
  onChange(t: Tuning, look?: Look): void;
  /** The look shown (S105, D275): under "illustrative" the panel shows the Illustrative group and the box says so. */
  look?: Look;
  /** The template's defaults under each look, for a pasted combination that names a look (S105). */
  defaultsOfLook?(look: Look): Tuning;
  /** The field's last re-march, filled in by FieldVolume; read while the section is open. */
  stats: MarchStats;
  /** What the copy box names beside the changed choices (S67, D227): the template tuned on, its filter set and the
   * exposure's stops, which live outside the tuning object, so a pasted box says which galaxy it was found on. */
  template?: string | null;
  filterSet?: string;
  exposure?: number;
  /** The defaults the choices are compared with and reset to: the template's own (S67, D227 R4: tuning.ts defaultsFor). */
  defaults?: Tuning;
  /** Sets the exposure's stops (App's state, the Exposure slider's) when a pasted combination names one (S97). */
  onExposure?(stops: number): void;
  /** Open on first draw (the panel's test; the page opens it closed). */
  initiallyOpen?: boolean;
  /** S105 fix R1: a plane-shaping change is waiting for the sliders to settle or being built (the "rebuilding" mark). */
  illPending?: boolean;
}

/** The one-line notice after a paste is applied (S97): what was applied, and anything not. */
export function combinationNotice(c: Combination, template: string | null | undefined, filterSet: string | null | undefined, exposureApplied: boolean): string {
  if (c.error !== null) return `Not applied - ${c.error}.`;
  const parts = [`Applied over ${template ?? "the"} defaults`];
  const other: string[] = [];
  if (c.template !== null && c.template !== (template ?? null)) other.push(`template ${c.template}`);
  if (c.filters !== null && c.filters !== (filterSet ?? null)) other.push(`filters ${c.filters}`);
  if (other.length) parts.push(`the box was copied on ${other.join(", ")}; applied here anyway, nothing switched`);
  if (c.exposure !== null) parts.push(exposureApplied ? `exposure ${c.exposure} stops` : "exposure not applied here");
  if (c.ignored.length) parts.push(`ignored (no such choice): ${c.ignored.join(", ")}`);
  if (c.rejected.length) parts.push(`kept the default (value unusable): ${c.rejected.join(", ")}`);
  return parts.join("; ") + ".";
}

/**
 * The Tuning section (D199): the field view's display choices as controls, experimental, so the owner can
 * find the combination to rule on. Nothing here is physics (rule D5). Untouched, every value is the
 * view's own from before the panel; the changed ones are shown as JSON to copy into a report.
 */
export function TuningPanel({ tuning, onChange, stats, template, filterSet, exposure, defaults = TUNING_DEFAULTS, onExposure, initiallyOpen = false, look = "physical", defaultsOfLook, illPending = false }: Props) {
  const [open, setOpen] = useState(initiallyOpen);
  const [paste, setPaste] = useState("");
  const [notice, setNotice] = useState<string | null>(null);
  const apply = () => {
    const c = parseCombination(paste, defaults, defaultsOfLook, look);
    // A box names its look (S105): without one it is the physical look's. Without defaultsOfLook the look stays.
    const target: Look = defaultsOfLook ? (c.look ?? "physical") : look;
    if (c.tuning) onChange(c.tuning, target);
    const exposureApplied = c.tuning !== null && c.exposure !== null && onExposure !== undefined;
    if (exposureApplied) onExposure!(c.exposure!);
    setNotice(combinationNotice(c, template, filterSet, exposureApplied));
  };
  const [march, setMarch] = useState<MarchStats>({ ...stats });
  useEffect(() => {
    if (!open) return;
    const read = () => setMarch((m) => (m.width === stats.width && m.height === stats.height && m.ms === stats.ms && m.gpuMs === stats.gpuMs && m.gpuAvailable === stats.gpuAvailable ? m : { ...stats }));
    read();
    const timer = setInterval(read, 500);
    return () => clearInterval(timer);
  }, [open, stats]);

  const set = (key: keyof Tuning, value: Tuning[keyof Tuning] | string) => onChange({ ...tuning, [key]: value } as Tuning);
  const setIll = (key: string, value: number) => onChange({ ...tuning, ill: { ...tuning.ill, [key]: value } });
  const diff = changed(tuning, defaults);
  // The box of the look shown (S105): the physical look's text is the one of before.
  const copyBoxText = (t: Tuning, d: Readonly<Tuning>, tp?: string | null, f?: string, e?: number) => copyBoxTextOfLook(t, d, tp, f, e, look);

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
                // A toggle is the design system's Switch (T17, S84), named by its label; a choice of a few its Select.
                return (
                  <div key={control.key} className={styles.tuningRow} title={control.about}>
                    <div className={styles.zoomHead}>
                      {control.kind === "toggle" ? (
                        <Switch label={control.label} checked={value === true} onChange={(on) => set(control.key, on)} className={styles.tuningSwitch} />
                      ) : (
                        <>
                          <span className={styles.tuningName}>{control.label}</span>
                          <span className={styles.value}>{describe(control, value)}</span>
                        </>
                      )}
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
                    {control.kind === "select" && (
                      <Select
                        size="sm"
                        mono
                        className={styles.tuningSelect}
                        aria-label={control.label}
                        options={control.options}
                        value={String(value)}
                        onChange={(e) => set(control.key, e.target.value)}
                      />
                    )}
                  </div>
                );
              })}
            </div>
          ))}
          {/* The illustrative look's parameters (S105, D275): every registered feature's controls, generically. */}
          {look === "illustrative" && (
            <div className={styles.tuningGroup}>
              <div className={styles.label}>
                Illustrative
                {illPending && (
                  <span className={styles.muted} role="status" title="A slider that reshapes a feature's map is built once it has held still: the picture is behind the sliders until then.">
                    {" "}
                    · rebuilding…
                  </span>
                )}
              </div>
              <p className={styles.muted}>Display-only structure and colour of the viewer's own, tuned to the goal pictures: not the model.</p>
              {illControls().map(({ key, feature, control }) => {
                const value = tuning.ill[key] ?? control.default;
                const fallback = defaults.ill?.[key] ?? control.default;
                const range: RangeControl = { key: "fieldGain", label: control.label, group: "Light", kind: "range", min: control.min, max: control.max, step: control.step, log: control.log, unit: control.unit ?? "", about: control.about };
                return (
                  <div key={key} className={styles.tuningRow} title={`${feature.label}: ${control.about}`}>
                    <div className={styles.zoomHead}>
                      <span className={styles.tuningName}>{control.label}</span>
                      <span className={styles.value}>{shown(range, value)}</span>
                      {value !== fallback && (
                        <button type="button" className={styles.tuningDefault} title={`Back to the default, ${shown(range, fallback)}`} onClick={() => setIll(key, fallback)}>
                          default
                        </button>
                      )}
                    </div>
                    {control.log ? (
                      <input type="range" className={styles.slider} min={0} max={1000} value={positionOf(range, value)} aria-label={control.label} onChange={(e) => setIll(key, valueAt(range, Number(e.target.value)))} />
                    ) : (
                      <input type="range" className={styles.slider} min={control.min} max={control.max} step={control.step} value={value} aria-label={control.label} onChange={(e) => setIll(key, Number(e.target.value))} />
                    )}
                  </div>
                );
              })}
            </div>
          )}
          <div className={styles.tuningGroup}>
            <div className={styles.muted} title="The march target's size, the last re-march's CPU-side time (the render call) and, since S67, the GPU's time for it from a timer query (EXT_disjoint_timer_query_webgl2), where the browser gives one">
              march: {march.width}×{march.height} px, {march.ms.toFixed(1)} ms CPU, {gpuWords(march.gpuMs, march.gpuAvailable ?? false)}
            </div>
            <div className={styles.tuningActions}>
              <Button disabled={Object.keys(diff).length === 0} onClick={() => onChange({ ...defaults })}>
                Reset all
              </Button>
            </div>
            <textarea
              className={styles.tuningCopy}
              readOnly
              rows={3}
              value={copyBoxText(tuning, defaults, template, filterSet, exposure)}
              aria-label="The changed display choices, as JSON"
              onFocus={(e) => e.currentTarget.select()}
            />
            {/* Load a combination (S97): the copy box's own JSON, pasted back. */}
            <p className={styles.muted}>
              Load a combination: paste a copy box here and apply it. The box lists only what differs from its template's
              defaults, so it is laid over this template's defaults: on the template it was copied from it reproduces that
              combination exactly. Its template and filter set are not switched to.
            </p>
            <textarea
              className={styles.tuningCopy}
              rows={3}
              value={paste}
              placeholder='{"template":"milky_way","filters":"rgb","exposure":0,...}'
              aria-label="A combination to load, as the copy box's JSON"
              onChange={(e) => setPaste(e.target.value)}
            />
            <div className={styles.tuningActions}>
              <Button disabled={paste.trim() === ""} onClick={apply}>
                Apply
              </Button>
            </div>
            {notice && (
              <div className={styles.muted} role="status">
                {notice}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
