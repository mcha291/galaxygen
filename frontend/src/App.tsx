import { identify } from "@interface/stars.js";
import { Orbit } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { loadFields, loadSample, type FieldsPayload, type Sample } from "./api";
import { starColors } from "./galaxy/colors";
import { GalaxyView, type Preset } from "./galaxy/GalaxyView";
import { toScene } from "./galaxy/positions";
import { Preview } from "./preview/Preview";
import { panelsAt } from "./preview/panels";
import { SystemView } from "./system/SystemView";
import { Button } from "./ui/Button";
import { ErrorBoundary } from "./ui/ErrorBoundary";
import { useLoad } from "./useLoad";
import { formatNumber } from "./workflow/logic";
import { useWorkflow } from "./workflow/useWorkflow";
import { WorkflowPanel } from "./workflow/Workflow";
import styles from "./App.module.css";

// The star columns a user can paint the sample by (design brief §3).
const COLOUR_FIELDS = ["star_metallicity", "star_age", "star_population", "star_mass", "star_birth_radius"];
const PRESETS: Preset[] = ["oblique", "face-on", "edge-on"];

type Tab = "preview" | "galaxy";

export function App() {
  const wf = useWorkflow();
  const [meta, setMeta] = useState<FieldsPayload | null>(null);
  const [tab, setTab] = useState<Tab>("preview");
  const [field, setField] = useState(COLOUR_FIELDS[0]);
  const [preset, setPreset] = useState<Preset>("oblique");
  const [picked, setPicked] = useState<number | null>(null);
  const [systemStar, setSystemStar] = useState<{ cell: number; index: number } | null>(null);

  useEffect(() => {
    const abort = new AbortController();
    loadFields(wf.model, abort.signal).then(setMeta).catch(() => undefined);
    return () => abort.abort();
  }, [wf.model]);

  const current = wf.state?.cat.checkpoints.find((c) => c.n === wf.state!.current) ?? null;
  // "Planets: systems become openable" (design brief §1): the last checkpoint must be reachable.
  const last = wf.state?.cat.checkpoints.length ?? 0;
  const planetsReady = !!wf.state && wf.state.confirmed >= last - 1;
  const panels = useMemo(() => (meta && current ? panelsAt(meta.fields, current.n) : null), [meta, current]);

  // The star sample runs every stage, so it is only asked for while it is on screen.
  const sampleKey = tab === "galaxy" && wf.query ? JSON.stringify(wf.query) : null;
  const galaxy = useLoad<Sample>(sampleKey, (signal) => loadSample(wf.query!, signal));
  const sample = galaxy.value;
  // A new galaxy is a new set of stars: the old selection and open system named stars in the old one.
  useEffect(() => {
    setPicked(null);
    setSystemStar(null);
  }, [sample]);

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
        <div className={styles.segmented} role="tablist" aria-label="View">
          <button role="tab" aria-pressed={tab === "preview"} aria-selected={tab === "preview"} onClick={() => setTab("preview")}>
            Preview
          </button>
          <button role="tab" aria-pressed={tab === "galaxy"} aria-selected={tab === "galaxy"} onClick={() => setTab("galaxy")}>
            Galaxy
          </button>
        </div>
      </header>

      <WorkflowPanel wf={wf} tMax={meta?.grid.axes.t?.hi} />

      <main className={styles.stage}>
        <ErrorBoundary resetKey={`${tab}:${current?.n}:${wf.model}`}>
        {tab === "preview" && current && panels && wf.query && (
          <Preview checkpoint={current} panels={panels} query={wf.query} cmaps={meta!.cmaps} />
        )}
        {tab === "preview" && !panels && <p className={styles.status}>Loading field declarations.</p>}

        {tab === "galaxy" && (
          <>
            {!sample && !galaxy.error && <p className={styles.status}>Generating galaxy: every stage runs for the star sample.</p>}
            {galaxy.error && (
              <p className={styles.status}>
                Generation failed: {galaxy.error}. Check that the API is running (<code>uv run python -m galaxy.api</code>).
              </p>
            )}
            {positions && colors && <GalaxyView positions={positions} colors={colors} preset={preset} onPick={setPicked} />}
            {galaxy.busy && sample && <div className={styles.busy} aria-hidden />}
            {systemStar && meta && wf.query && (
              <SystemView star={systemStar} query={wf.query} meta={meta} onClose={() => setSystemStar(null)} />
            )}
          </>
        )}
        </ErrorBoundary>
      </main>

      <aside className={styles.inspector}>
        {tab === "galaxy" ? (
          <>
            <section>
              <h2 className="gx-label">Sample</h2>
              <p className={styles.readoutLine}>
                {sample ? `${sample.header.stars.materialised.toLocaleString("en")} stars` : "—"}
                {galaxy.busy ? " · regenerating" : ""}
              </p>
            </section>
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
            {meta && sample && picked !== null && (
              <StarReadout meta={meta} sample={sample} row={picked} onOpen={setSystemStar} planets={planetsReady} />
            )}
          </>
        ) : (
          <CheckpointNotes panels={panels} />
        )}
      </aside>
    </div>
  );
}

function CheckpointNotes({ panels }: { panels: ReturnType<typeof panelsAt> | null }) {
  if (!panels) return null;
  const plotted = panels.lines.reduce((n, p) => n + p.fields.length, 0);
  return (
    <section>
      <h2 className="gx-label">This preview</h2>
      <p className={styles.readoutLine}>
        {plotted} profiles on {panels.lines.length} plots · {panels.scalars.length} scalars
      </p>
      <p className={styles.help}>
        Profiles sharing an axis and a unit share a plot. A plot is logarithmic only when every field on it is declared
        so. Hover a plot to read values.
      </p>
      {panels.catalogue && <p className={styles.help}>The star catalogue exists from this checkpoint: open Galaxy to see it.</p>}
    </section>
  );
}

function StarReadout({ meta, sample, row, onOpen, planets }: {
  meta: FieldsPayload; sample: Sample; row: number; onOpen(star: { cell: number; index: number }): void; planets: boolean;
}) {
  const name = identify(sample.header, row) as { cell: number; index: number } | null;
  return (
    <section>
      <h2 className="gx-label">Selected star</h2>
      {name && (
        <div className={styles.openSystem}>
          <Button variant="primary" icon={<Orbit />} disabled={!planets} onClick={() => onOpen(name)}>
            Open system
          </Button>
          {!planets && <p className={styles.help}>Systems become openable at checkpoint 6, Planets.</p>}
        </div>
      )}
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
