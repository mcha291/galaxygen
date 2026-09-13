import { identify } from "@interface/stars.js";
import { Orbit } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { loadFields, loadSample, type FieldsPayload, type Sample } from "./api";
import { starColors } from "./galaxy/colors";
import { GalaxyTab } from "./galaxy/GalaxyTab";
import { GalaxyView, type Preset } from "./galaxy/GalaxyView";
import { toScene } from "./galaxy/positions";
import { Preview as ScienceView } from "./preview/Preview";
import { Published } from "./preview/Published";
import { panelsAt } from "./preview/panels";
import { SystemView } from "./system/SystemView";
import { Button } from "./ui/Button";
import { ErrorBoundary } from "./ui/ErrorBoundary";
import { useLoad } from "./useLoad";
import { formatNumber, runHash } from "./workflow/logic";
import { useWorkflow } from "./workflow/useWorkflow";
import { WorkflowPanel } from "./workflow/Workflow";
import styles from "./App.module.css";

// The star columns a user can paint the sample by (design brief §3).
const COLOUR_FIELDS = ["star_metallicity", "star_age", "star_population", "star_mass", "star_birth_radius"];
const PRESETS: Preset[] = ["oblique", "face-on", "edge-on"];

type Tab = "preview" | "science" | "galaxy";

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
  const last = wf.state?.cat.checkpoints.length ?? 0;
  // "Planets: systems become openable" (design brief §1): the last checkpoint must be reachable.
  const planetsReady = !!wf.state && wf.state.confirmed >= last - 1;
  // Generation is done when every checkpoint is confirmed; the Galaxy tab shows that result only.
  const generated = !!wf.state && last > 0 && wf.state.confirmed === last;
  const panels = useMemo(() => (meta && current ? panelsAt(meta.fields, current.n) : null), [meta, current]);

  // Reopening a checkpoint un-generates the galaxy, so the tab showing it closes.
  useEffect(() => {
    if (tab === "galaxy" && !generated) setTab("preview");
  }, [tab, generated]);

  // The star sample runs every stage, so it is only asked for while a tab draws it.
  const sampleKey = tab !== "science" && wf.query ? JSON.stringify(wf.query) : null;
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

  const seed = wf.state?.values.world_seed;
  const hash = wf.query ? `${runHash(wf.query)} · ${wf.model} · world_seed ${seed}` : "";
  const tabs: { key: Tab; label: string; disabled?: boolean; title?: string }[] = [
    { key: "preview", label: "Preview" },
    { key: "science", label: "Science" },
    { key: "galaxy", label: "Galaxy", disabled: !generated, title: generated ? undefined : `Confirm all ${last} checkpoints to generate the galaxy` },
  ];

  const status = (
    <>
      {!sample && !galaxy.error && <p className={styles.status}>Generating galaxy.</p>}
      {galaxy.error && (
        <p className={styles.status}>
          Generation failed: {galaxy.error}. Check that the API is running (<code>uv run python -m galaxy.api</code>).
        </p>
      )}
      {galaxy.busy && sample && <div className={styles.busy} aria-hidden />}
    </>
  );
  const system = systemStar && meta && wf.query && (
    <SystemView star={systemStar} query={wf.query} meta={meta} onClose={() => setSystemStar(null)} />
  );

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
        <span className={styles.hash} title="Run hash of the input vector · model · world seed">{hash}</span>
        <span className={styles.spacer} />
        <div className={styles.segmented} role="tablist" aria-label="View">
          {tabs.map((t) => (
            <button
              key={t.key}
              role="tab"
              aria-pressed={tab === t.key}
              aria-selected={tab === t.key}
              disabled={t.disabled}
              title={t.title}
              onClick={() => setTab(t.key)}
            >
              {t.label}
            </button>
          ))}
        </div>
      </header>

      <main className={styles.main}>
        <ErrorBoundary resetKey={`${tab}:${current?.n}:${wf.model}`}>
          {tab === "preview" && (
            <div className={styles.canvasStage}>
              {positions && colors && <GalaxyView positions={positions} colors={colors} preset={preset} onPick={setPicked} />}
              {status}
              <WorkflowPanel wf={wf} tMax={meta?.grid.axes.t?.hi} className={styles.floatingRail} />

              {current && (
                <div className={styles.previewTitle}>
                  <span className={styles.overlayLabel}>Preview · checkpoint {current.n}</span>
                  <span className={styles.previewName}>{current.name}</span>
                </div>
              )}

              <aside className={styles.overlayColumn}>
                <section>
                  <div className={styles.overlayHead}>
                    <span className={styles.rule} />
                    <span className={styles.overlayLabel}>View</span>
                  </div>
                  <div className={styles.segmented}>
                    {PRESETS.map((p) => (
                      <button key={p} aria-pressed={p === preset} onClick={() => setPreset(p)}>
                        {p}
                      </button>
                    ))}
                  </div>
                  <select className={styles.select} value={field} onChange={(e) => setField(e.target.value)} aria-label="Colour by">
                    {COLOUR_FIELDS.map((f) => (
                      <option key={f} value={f}>
                        Colour by {meta?.fields.find((d) => d.name === f)?.label ?? f}
                      </option>
                    ))}
                  </select>
                </section>
                {meta && sample && picked !== null && (
                  <StarReadout meta={meta} sample={sample} row={picked} onOpen={setSystemStar} planets={planetsReady} />
                )}
                {panels && wf.query && <Published scalars={panels.scalars} query={wf.query} />}
              </aside>

              {sample && (
                <div className={styles.caption}>
                  <div className={styles.captionNote}>
                    {sample.header.stars.materialised.toLocaleString("en")} sampled stars · {current?.stages.join(" · ")}
                  </div>
                  <p>Drag to orbit, scroll to zoom, click a star to read it.</p>
                </div>
              )}
              {system}
            </div>
          )}

          {tab === "science" && (
            <div className={styles.scienceStage}>
              <WorkflowPanel wf={wf} tMax={meta?.grid.axes.t?.hi} />
              <div className={styles.scienceBody}>
                {current && panels && wf.query && meta ? (
                  <ScienceView checkpoint={current} panels={panels} query={wf.query} cmaps={meta.cmaps} />
                ) : (
                  <p className={styles.status}>Loading field declarations.</p>
                )}
              </div>
            </div>
          )}

          {tab === "galaxy" && (
            <div className={styles.canvasStage}>
              {meta && sample && positions && colors && (
                <GalaxyTab
                  meta={meta}
                  sample={sample}
                  positions={positions}
                  colors={colors}
                  fields={COLOUR_FIELDS}
                  field={field}
                  onField={setField}
                  preset={preset}
                  onPreset={setPreset}
                  onPick={(row) => {
                    const name = identify(sample.header, row) as { cell: number; index: number } | null;
                    if (name) setSystemStar(name);
                  }}
                />
              )}
              {status}
              {system}
            </div>
          )}
        </ErrorBoundary>
      </main>

      {/* The design's bottom bar, left empty for now. */}
      <footer className={styles.footer}>
        <span className={styles.footLeft} />
        <span className={styles.footRight} />
      </footer>
    </div>
  );
}

function StarReadout({ meta, sample, row, onOpen, planets }: {
  meta: FieldsPayload; sample: Sample; row: number; onOpen(star: { cell: number; index: number }): void; planets: boolean;
}) {
  const name = identify(sample.header, row) as { cell: number; index: number } | null;
  return (
    <section>
      <div className={styles.overlayHead}>
        <span className={styles.rule} />
        <span className={styles.overlayLabel}>Selected star</span>
      </div>
      {name && (
        <div className={styles.openSystem}>
          <Button variant="primary" icon={<Orbit />} disabled={!planets} onClick={() => onOpen(name)}>
            Open system
          </Button>
          {!planets && <p className={styles.overlayNote}>Systems become openable at checkpoint 6, Planets.</p>}
        </div>
      )}
      {name && (
        <div className={styles.stat}>
          <div className={styles.statKey}>cell / index</div>
          <div className={styles.statValue}>
            <span>
              {name.cell} / {name.index}
            </span>
          </div>
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
          <div key={f} className={styles.stat}>
            <div className={styles.statKey}>{decl.label}</div>
            <div className={styles.statValue}>
              <span>{shown}</span>
              {unit && <span className={styles.statUnit}>{unit}</span>}
            </div>
          </div>
        );
      })}
    </section>
  );
}
