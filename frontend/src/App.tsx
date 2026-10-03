import { useEffect, useMemo, useState } from "react";

import { loadFields, loadSample, type FieldsPayload, type Sample } from "./api";
import { PHOTOMETRIC } from "./galaxy/colors";
import type { ComparePicture } from "./galaxy/PictureBeside";
import { Exposure } from "./galaxy/Exposure";
import type { FilterSetName } from "./galaxy/filters";
import { GalaxyTab } from "./galaxy/GalaxyTab";
import { type Preset } from "./galaxy/GalaxyView";
import { CheckpointScene } from "./preview/CheckpointScene";
import { Preview as ScienceView } from "./preview/Preview";
import { Published } from "./preview/Published";
import { panelsAt } from "./preview/panels";
import { ErrorBoundary } from "./ui/ErrorBoundary";
import { useLoad } from "./useLoad";
import { runHash } from "./workflow/logic";
import { templateLabel } from "./workflow/templates";
import { EDIT_VIEW, type View, isGenerated, settleView, useWorkflow } from "./workflow/useWorkflow";
import { WorkflowPanel } from "./workflow/Workflow";
import styles from "./App.module.css";

// The star columns a user can paint the sample by (design brief §3), and photometric
// mode beside them: a choice, never a default that hides the fields (RENDER_PLAN §0).
const COLOUR_FIELDS = ["star_metallicity", "star_alpha", "star_age", "star_population", "star_mass", "star_birth_radius", "star_temperature", "star_luminosity"];
const PAINT_CHOICES = [...COLOUR_FIELDS, PHOTOMETRIC];
const PRESETS: Preset[] = ["oblique", "face-on", "edge-on"];

type Tab = View;

export function App() {
  const wf = useWorkflow();
  const [meta, setMeta] = useState<FieldsPayload | null>(null);
  // The viewer lands on the default galaxy, generated on first load (D198, rule D1 as amended).
  const [tab, setTab] = useState<Tab>("galaxy");
  const [field, setField] = useState<string>(PHOTOMETRIC);
  // Where the Galaxy view stands: one of the presets, or null for the template's own camera (D213 ruling 5).
  // "oblique" until a template is landed on, and for good where the API has none (one from before S54).
  const [preset, setPreset] = useState<Preset | null>("oblique");
  const [filterSet, setFilterSet] = useState<FilterSetName>("rgb");
  const [charts, setCharts] = useState(false);
  const [exposure, setExposure] = useState(0); // photometric exposure, in stops
  // "Compare with a picture" (T16 ii): a file the user picked, shown through an object URL. It never leaves
  // the browser, and its URL is released when it is replaced or dismissed.
  const [picture, setPicture] = useState<ComparePicture | null>(null);
  useEffect(
    () => () => {
      if (picture) URL.revokeObjectURL(picture.url);
    },
    [picture],
  );

  // A template landed on - the first load, or one chosen in the switcher - brings its camera and its filter
  // set (rule D1 as amended; D213 rulings 5 and 7). What the user changes after that is theirs until the next.
  const landed = wf.template;
  useEffect(() => {
    if (!landed) return;
    setPreset(null);
    setFilterSet(landed.filters);
  }, [wf.selection]); // eslint-disable-line react-hooks/exhaustive-deps -- a landing, not every render of the same template
  // The switcher's choice: the workflow regenerates at the template's inputs (its own state, its own query), and
  // the view takes the template's stand and filters in the same update, so the canvas is made once.
  const chooseTemplate = (name: string) => {
    const chosen = wf.templates.find((t) => t.name === name);
    if (!chosen) return;
    wf.selectTemplate(name);
    setPreset(null);
    setFilterSet(chosen.filters);
  };
  const pickPicture = (file: File | null) => setPicture(file ? { url: URL.createObjectURL(file), name: file.name } : null);

  useEffect(() => {
    const abort = new AbortController();
    loadFields(wf.model, abort.signal).then(setMeta).catch(() => undefined);
    return () => abort.abort();
  }, [wf.model]);

  const query = wf.query;
  const current = wf.state?.cat.checkpoints.find((c) => c.n === wf.state!.current) ?? null;
  const last = wf.state?.cat.checkpoints.length ?? 0;
  // Generation is done when every checkpoint is confirmed; the Galaxy tab shows that result only.
  const generated = isGenerated(wf.state);
  const panels = useMemo(() => (meta && current ? panelsAt(meta.fields, current.n) : null), [meta, current]);

  // Reopening a checkpoint un-generates the galaxy, so the Galaxy tab closes to the Preview. A
  // generated galaxy no longer pulls the Preview back to the Galaxy tab (D198): "Edit galaxy" lands
  // on the Preview with every checkpoint still locked. Nothing settles before the declarations
  // arrive, so the first load waits on the Galaxy tab while they are confirmed through.
  useEffect(() => {
    if (wf.state) setTab((t) => settleView(t, generated));
  }, [wf.state, generated]);

  // The star sample runs every stage, so it is only asked for where stars are drawn: the Galaxy
  // tab. The preview shows fields only, at every checkpoint including the last two.
  // The staged preview keeps its three stands; while the Galaxy view is at a template's camera it shows the oblique one.
  const previewPreset: Preset = preset ?? "oblique";
  const drawsStars = tab === "galaxy";
  const sampleKey = drawsStars && query ? JSON.stringify(query) : null;
  const galaxy = useLoad<Sample>(sampleKey, (signal) => loadSample(query!, signal));
  const sample = galaxy.value;

  const seed = wf.state?.values.world_seed;
  // The model is named only where there is a choice of one; there are two since S27 (D176) and the
  // selector shows them; the default is the azimuthal one since S46 (D197).
  const hash = query ? `${runHash(query)}${wf.models.length > 1 ? ` · ${wf.model}` : ""} · world_seed ${seed}` : "";
  // The template the galaxy is, in every tab: its label, and "edited" once an input or the model has changed.
  const galaxyName = wf.template && wf.state ? templateLabel(wf.template, wf.edited) : "";
  const tabs: { key: Tab; label: string; disabled?: boolean; title?: string }[] = [
    { key: "preview", label: "Preview", title: generated ? "The staged generation: reopen a checkpoint to change the galaxy" : undefined },
    { key: "science", label: "Science" },
    { key: "galaxy", label: "Galaxy", disabled: !!wf.state && !generated, title: generated ? undefined : `Confirm all ${last} checkpoints to generate the galaxy` },
  ];

  const status = (
    <>
      {!sample && !galaxy.error && !(wf.error && !wf.state) && <p className={styles.status}>Generating galaxy.</p>}
      {wf.error && !wf.state && (
        <p className={styles.status}>
          Loading the model failed: {wf.error}. Check that the API is running (<code>uv run python -m galaxy.api</code>).
        </p>
      )}
      {galaxy.error && (
        <p className={styles.status}>
          Generation failed: {galaxy.error}. Check that the API is running (<code>uv run python -m galaxy.api</code>).
        </p>
      )}
      {galaxy.busy && sample && <div className={styles.busy} aria-hidden />}
    </>
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
        {galaxyName && (
          <span
            className={styles.galaxyName}
            title={wf.edited ? `Edited from the ${wf.template!.label} template: choose it again in the Galaxy view to restore it` : wf.template!.about}
          >
            {galaxyName}
          </span>
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
                  preset={previewPreset}
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
                      <button key={p} aria-pressed={p === previewPreset} onClick={() => setPreset(p)}>
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
                  <p>Drag to orbit, scroll to zoom. The stars are drawn in the Galaxy tab.</p>
                </div>
              )}
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
                  onEdit={() => setTab(EDIT_VIEW)}
                  filterSet={filterSet}
                  onFilterSet={setFilterSet}
                  templates={wf.templates}
                  template={wf.template}
                  edited={wf.edited}
                  onTemplate={chooseTemplate}
                  selection={wf.selection}
                  picture={picture}
                  onPicture={pickPicture}
                />
              )}
              {status}
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
