import { identify } from "@interface/stars.js";
import { useEffect, useMemo, useState } from "react";

import { loadFields, loadSample, type FieldsPayload, type Sample } from "./api";
import { starColors } from "./galaxy/colors";
import { GalaxyView, type Preset } from "./galaxy/GalaxyView";
import { toScene } from "./galaxy/positions";
import { formatNumber } from "./workflow/logic";
import { useWorkflow } from "./workflow/useWorkflow";
import { WorkflowPanel } from "./workflow/Workflow";
import styles from "./App.module.css";

// The star columns a user can paint the sample by (design brief §3).
const COLOUR_FIELDS = ["star_metallicity", "star_age", "star_population", "star_mass", "star_birth_radius"];
const PRESETS: Preset[] = ["oblique", "face-on", "edge-on"];
// A slider drag sends one request when it pauses, not one per pixel.
const REGENERATE_AFTER_MS = 350;

type Galaxy =
  | { state: "idle" }
  | { state: "error"; message: string }
  | { state: "ready"; sample: Sample };

export function App() {
  const wf = useWorkflow();
  const [meta, setMeta] = useState<FieldsPayload | null>(null);
  const [galaxy, setGalaxy] = useState<Galaxy>({ state: "idle" });
  const [busy, setBusy] = useState(false);
  const [field, setField] = useState(COLOUR_FIELDS[0]);
  const [preset, setPreset] = useState<Preset>("oblique");
  const [picked, setPicked] = useState<number | null>(null);

  useEffect(() => {
    const abort = new AbortController();
    loadFields(wf.model, abort.signal).then(setMeta).catch(() => undefined);
    return () => abort.abort();
  }, [wf.model]);

  // Regenerate whenever the input vector changes. The previous galaxy stays on
  // screen, marked as regenerating, until the new one arrives; a newer change
  // cancels the request in flight rather than racing it.
  const key = wf.query ? JSON.stringify(wf.query) : null;
  useEffect(() => {
    if (!key) return;
    const abort = new AbortController();
    const timer = setTimeout(() => {
      setBusy(true);
      loadSample(JSON.parse(key), abort.signal)
        .then((sample) => {
          setGalaxy({ state: "ready", sample });
          setPicked(null);
        })
        .catch((error: Error) => {
          if (!abort.signal.aborted) setGalaxy({ state: "error", message: error.message });
        })
        .finally(() => {
          if (!abort.signal.aborted) setBusy(false);
        });
    }, REGENERATE_AFTER_MS);
    return () => {
      clearTimeout(timer);
      abort.abort();
    };
  }, [key]);

  const sample = galaxy.state === "ready" ? galaxy.sample : null;

  const positions = useMemo(() => {
    if (!sample) return null;
    const c = sample.columns as Record<string, ArrayLike<number>>;
    return toScene(c.star_radius, c.star_azimuth, c.star_height);
  }, [sample]);

  const colors = useMemo(() => {
    if (!sample || !meta) return null;
    try {
      return starColors(meta, sample.columns, field);
    } catch {
      return null; // the fields for a just-switched model have not arrived yet
    }
  }, [sample, meta, field]);

  return (
    <div className={styles.shell}>
      <header className={styles.topbar}>
        <span className={styles.wordmark}>galaxygen</span>
        <div className={styles.segmented} role="group" aria-label="Model">
          {wf.models.map((m) => (
            <button key={m} aria-pressed={m === wf.model} onClick={() => wf.setModel(m)}>
              {m}
            </button>
          ))}
        </div>
        <span className="gx-label">same seven inputs</span>
        <span className={styles.spacer} />
        {sample && (
          <span className="gx-label">
            {busy ? "Regenerating · " : ""}
            {sample.header.stars.materialised.toLocaleString("en")} stars sampled
          </span>
        )}
      </header>

      <WorkflowPanel wf={wf} />

      <main className={styles.stage}>
        {!sample && galaxy.state !== "error" && <p className={styles.status}>Generating galaxy.</p>}
        {galaxy.state === "error" && (
          <p className={styles.status}>
            Generation failed: {galaxy.message}. Check that the API is running (<code>uv run python -m galaxy.api</code>).
          </p>
        )}
        {positions && colors && (
          <GalaxyView positions={positions} colors={colors} preset={preset} onPick={setPicked} />
        )}
        {busy && sample && <div className={styles.busy} aria-hidden />}
      </main>

      <aside className={styles.inspector}>
        <section>
          <h2 className="gx-label">View</h2>
          <div className={styles.segmented}>
            {PRESETS.map((p) => (
              <button key={p} aria-pressed={p === preset} onClick={() => setPreset(p)}>
                {p}
              </button>
            ))}
          </div>
        </section>
        <section>
          <h2 className="gx-label">Colour by</h2>
          <select className={styles.select} value={field} onChange={(e) => setField(e.target.value)}>
            {COLOUR_FIELDS.map((f) => (
              <option key={f} value={f}>
                {meta?.fields.find((d) => d.name === f)?.label ?? f}
              </option>
            ))}
          </select>
        </section>
        {meta && sample && picked !== null && <StarReadout meta={meta} sample={sample} row={picked} />}
      </aside>
    </div>
  );
}

function StarReadout({ meta, sample, row }: { meta: FieldsPayload; sample: Sample; row: number }) {
  const name = identify(sample.header, row) as { cell: number; index: number } | null;
  return (
    <section>
      <h2 className="gx-label">Selected star</h2>
      <dl className={styles.readout}>
        {name && (
          <div className={styles.row}>
            <dt>Cell / index</dt>
            <dd>
              {name.cell} / {name.index}
            </dd>
          </div>
        )}
        {COLOUR_FIELDS.concat(["star_radius", "star_height"]).map((f) => {
          const decl = meta.fields.find((d) => d.name === f);
          const value = sample.columns[f]?.[row];
          if (!decl || value === undefined) return null;
          const categorical = (decl.categories?.length ?? 0) > 0; // continuous fields declare []
          const shown = categorical ? decl.categories![Number(value)] : formatNumber(Number(value), 4);
          const unit = categorical || decl.unit === "dimensionless" ? "" : String(decl.unit_display ?? decl.unit);
          return (
            <div key={f} className={styles.row}>
              <dt>{decl.label}</dt>
              <dd>
                {shown} {unit}
              </dd>
            </div>
          );
        })}
      </dl>
    </section>
  );
}
