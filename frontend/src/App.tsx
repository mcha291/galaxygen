import { useEffect, useMemo, useState } from "react";

import { loadFields, loadSample, type FieldsPayload, type Sample, type StarName } from "./api";
import { PHOTOMETRIC } from "./galaxy/colors";
import { Exposure } from "./galaxy/Exposure";
import { GalaxyTab } from "./galaxy/GalaxyTab";
import { type Preset } from "./galaxy/GalaxyView";
import { CheckpointScene } from "./preview/CheckpointScene";
import { Preview as ScienceView } from "./preview/Preview";
import { Published } from "./preview/Published";
import { panelsAt } from "./preview/panels";
import { SystemView } from "./system/SystemView";
import { ErrorBoundary } from "./ui/ErrorBoundary";
import { useLoad } from "./useLoad";
import { formatNumber, runHash } from "./workflow/logic";
import { useWorkflow } from "./workflow/useWorkflow";
import { WorkflowPanel } from "./workflow/Workflow";
import styles from "./App.module.css";

// The star columns a user can paint the sample by (design brief §3), and photometric
// mode beside them: a choice, never a default that hides the fields (RENDER_PLAN §0).
const COLOUR_FIELDS = ["star_metallicity", "star_alpha", "star_age", "star_population", "star_mass", "star_birth_radius", "star_temperature", "star_luminosity"];
const PAINT_CHOICES = [...COLOUR_FIELDS, PHOTOMETRIC];
const PRESETS: Preset[] = ["oblique", "face-on", "edge-on"];

type Tab = "preview" | "science" | "galaxy";

export function App() {
  const wf = useWorkflow();
  const [meta, setMeta] = useState<FieldsPayload | null>(null);
  const [tab, setTab] = useState<Tab>("preview");
  const [field, setField] = useState<string>(PHOTOMETRIC);
  const [preset, setPreset] = useState<Preset>("oblique");
  const [systemStar, setSystemStar] = useState<StarName | null>(null);
  const [charts, setCharts] = useState(false);
  const [exposure, setExposure] = useState(0); // photometric exposure, in stops

  useEffect(() => {
    const abort = new AbortController();
    loadFields(wf.model, abort.signal).then(setMeta).catch(() => undefined);
    return () => abort.abort();
  }, [wf.model]);

  const query = wf.query;
  const current = wf.state?.cat.checkpoints.find((c) => c.n === wf.state!.current) ?? null;
  const last = wf.state?.cat.checkpoints.length ?? 0;
  // Generation is done when every checkpoint is confirmed; the Galaxy tab shows that result only.
  const generated = !!wf.state && last > 0 && wf.state.confirmed === last;
  const panels = useMemo(() => (meta && current ? panelsAt(meta.fields, current.n) : null), [meta, current]);

  // Confirming the last checkpoint generates the galaxy: the preview closes and the Galaxy tab
  // takes over. Reopening a checkpoint un-generates it, so the Galaxy tab closes in turn.
  useEffect(() => {
    if (tab === "preview" && generated) setTab("galaxy");
    if (tab === "galaxy" && !generated) setTab("preview");
  }, [tab, generated]);

  // The star sample runs every stage, so it is only asked for where stars are drawn: the Galaxy
  // tab. The preview shows fields only, at every checkpoint including the last two.
  const drawsStars = tab === "galaxy";
  const sampleKey = drawsStars && query ? JSON.stringify(query) : null;
  const galaxy = useLoad<Sample>(sampleKey, (signal) => loadSample(query!, signal));
  const sample = galaxy.value;
  // A new galaxy is a new set of stars: an open system named a star in the old one.
  useEffect(() => setSystemStar(null), [sample]);

  const seed = wf.state?.values.world_seed;
  // The model is named only where there is a choice of one; since D170 there is one model.
  const hash = query ? `${runHash(query)}${wf.models.length > 1 ? ` · ${wf.model}` : ""} · world_seed ${seed}` : "";
  const tabs: { key: Tab; label: string; disabled?: boolean; title?: string }[] = [
    { key: "preview", label: "Preview", disabled: generated, title: generated ? "The galaxy is generated; reopen a checkpoint in the Science tab to preview it" : undefined },
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
  const system = systemStar && meta && query && (
    <SystemView star={systemStar} query={query} meta={meta} onClose={() => setSystemStar(null)} />
  );

  return (
    <div className={styles.shell}>
      <header className={styles.topbar}>
        <span className={styles.wordmark}>galaxygen</span>
        {wf.models.length > 1 && (
          <div className={styles.segmented} role="group" aria-label="Model">
            {wf.models.map((m) => (
              <button key={m} aria-pressed={m === wf.model} onClick={() => wf.setModel(m)}>
                {m}
              </button>
            ))}
          </div>
        )}
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
              {current && meta && query && (
                <CheckpointScene
                  n={current.n}
                  meta={meta}
                  query={query}
                  preset={preset}
                  exposure={exposure}
                  charts={charts}
                />
              )}
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
                  {(current?.n ?? 0) >= 5 && <Exposure stops={exposure} onChange={setExposure} />}
                </section>
                {panels && query && <Published scalars={panels.scalars} query={query} />}
              </aside>

              {current && (
                <div className={styles.caption}>
                  <div className={styles.captionNote}>
                    {current.stages.join(" · ")}
                  </div>
                  <p>Drag to orbit, scroll to zoom. Stars and their systems open in the Galaxy tab.</p>
                </div>
              )}
              {system}
            </div>
          )}

          {tab === "science" && (
            <div className={styles.scienceStage}>
              <WorkflowPanel wf={wf} tMax={meta?.grid.axes.t?.hi} className={styles.floatingRail} />
              <div className={styles.scienceBody}>
                {current && panels && query && meta ? (
                  <ScienceView checkpoint={current} panels={panels} query={query} cmaps={meta.cmaps} />
                ) : (
                  <p className={styles.status}>Loading field declarations.</p>
                )}
              </div>
            </div>
          )}

          {tab === "galaxy" && (
            <div className={styles.canvasStage}>
              {meta && sample && query && (
                <GalaxyTab
                  meta={meta}
                  sample={sample}
                  fields={PAINT_CHOICES}
                  field={field}
                  onField={setField}
                  exposure={exposure}
                  onExposure={setExposure}
                  query={query}
                  preset={preset}
                  onPreset={setPreset}
                  onOpen={setSystemStar}
                />
              )}
              {status}
              {system}
            </div>
          )}
        </ErrorBoundary>
      </main>

      {/* The design's bottom bar. Its left slot held two experimental amplitude sliders until S26
          derived the amplitudes (D175); both slots are empty until a control earns one. */}
      <footer className={styles.footer}>
        <span className={styles.footLeft} />
        <span className={styles.footRight}>
          <button type="button" className={styles.footToggle} aria-pressed={charts} onClick={() => setCharts((c) => !c)}>
            preview charts {charts ? "on" : "off"}
          </button>
        </span>
      </footer>
    </div>
  );
}
