import { useEffect, useMemo, useRef, useState } from "react";

import { loadFields, loadSample, type FieldsPayload, type Sample } from "./api";
import { PHOTOMETRIC } from "./galaxy/colors";
import { PHYSICS_ONLY, layerQuery, onLayerFault } from "./galaxy/layer";
import type { ComparePicture } from "./galaxy/PictureBeside";
import { Exposure } from "./galaxy/Exposure";
import type { FilterSetName } from "./galaxy/filters";
import { GalaxyTab } from "./galaxy/GalaxyTab";
import { exposureFor } from "./galaxy/tuning";
import { type Preset } from "./galaxy/GalaxyView";
import { CheckpointScene } from "./preview/CheckpointScene";
import { Preview as ScienceView } from "./preview/Preview";
import { Published } from "./preview/Published";
import { panelsAt } from "./preview/panels";
import { ErrorBoundary } from "./ui/ErrorBoundary";
import { pendingLoads, settleSwap, useLoad, useSwap } from "./useLoad";
import { runHash } from "./workflow/logic";
import { pinWords, templateLabel } from "./workflow/templates";
import { type View, useWorkflow } from "./workflow/useWorkflow";
import { PRODUCES, WorkflowPanel } from "./workflow/Workflow";
import styles from "./App.module.css";

// The star columns a user can paint the sample by (design brief §3), and photometric
// mode beside them: a choice, never a default that hides the fields (RENDER_PLAN §0).
const COLOUR_FIELDS = ["star_metallicity", "star_alpha", "star_age", "star_population", "star_mass", "star_birth_radius", "star_temperature", "star_luminosity"];
const PAINT_CHOICES = [...COLOUR_FIELDS, PHOTOMETRIC];
const PRESETS: Preset[] = ["oblique", "face-on", "edge-on"];

type Tab = View;
/** The Science tab's two looks at a group: its scene (the published fields drawn in 3D) or its plots. */
type ScienceLook = "scene" | "plots";
const SCIENCE_LOOKS: ScienceLook[] = ["scene", "plots"];

/** A transport error without the request's URL (the whole input vector, which says nothing to a reader): "400: <the API's reason>". */
function briefly(message: string): string {
  return message.replace(/^(\d{3}) \S+: /, "$1: ");
}

export function App() {
  const wf = useWorkflow();
  // The viewer lands on the default galaxy, generated on first load (D198, rule D1 as amended).
  const [tab, setTab] = useState<Tab>("galaxy");
  // "Edit galaxy" (V9, S68): the edit panel as a drawer over the Galaxy view. In the Science tab it is the rail.
  const [editing, setEditing] = useState(false);
  // The group whose previews the Science tab shows - any group at any time, of the galaxy on screen (T18 by
  // construction). Null for the first.
  const [viewing, setViewing] = useState<number | null>(null);
  const [scienceLook, setScienceLook] = useState<ScienceLook>("scene");
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
    // S67 (D227 R4): and its exposure's default stops (tuning.ts exposureFor; 0 for a template with none).
    setExposure(exposureFor(landed.name));
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

  // "Physics only" (S55, D214: invariant I5's viewer half): the Galaxy view asks the model with the randomness
  // layer off. Display state held here, not an input: it is no part of the workflow's query (so no template is
  // "edited" by it and the run hash is unmoved), and it outlives the Galaxy tab, so "Edit galaxy" keeps it.
  const [physicsOnly, setPhysicsOnlyState] = useState(false);
  // A frame the API made under the other setting than the one asked for (galaxy/layer.ts): refused where it was
  // read, and said here. Changing the switch asks again, so it clears what the last asking was told.
  const [layerFault, setLayerFault] = useState<string | null>(null);
  useEffect(() => onLayerFault(setLayerFault), []);
  const setPhysicsOnly = (on: boolean) => {
    setLayerFault(null);
    setPhysicsOnlyState(on);
  };

  // The model of the galaxy on screen: its fields are what every view draws. A model chosen in the panel is the
  // draft's until "Generate" (rule D1 as amended).
  const shownModel = wf.shown?.model ?? wf.model;
  // A loader like the others (no settling delay), so a Generate that changes the model swaps the field
  // declarations with every other answer, whole (useLoad.ts, the swap).
  const meta = useLoad<FieldsPayload>(shownModel, (signal) => loadFields(shownModel, signal), 0).value;

  // The shown galaxy's query: the input vector, the model and - for a galaxy started from a template -
  // `template=`, which brings the template's pins (S58; useWorkflow.ts queryOf). Every tab asks with it and none
  // with the draft's, so an edit moves nothing on screen until "Generate" moves the whole galaxy.
  const query = wf.query;
  // What the Galaxy view asks the model with: the workflow's query and, under "physics only", `layer=off`. The
  // one place the parameter is added - the star sample below and every loader of the Galaxy tab take this query
  // and no other. The Science tab keeps the workflow's own query: it shows the model as generated, with the
  // layer, whatever the switch says, and the hash line marks the switch on the Galaxy tab alone.
  const galaxyQuery = query ? layerQuery(query, physicsOnly) : null;
  // The group the Science tab previews: one of the shown galaxy's groups, the first until another is chosen.
  const groups = wf.shown?.state.cat.checkpoints ?? [];
  const current = groups.find((c) => c.n === viewing) ?? groups[0] ?? null;
  const panels = useMemo(() => (meta && current ? panelsAt(meta.fields, current.n) : null), [meta, current]);

  // Stale (rule D1 as amended): from a "Generate" until the swap completes - every loader asking with the new
  // query has answered, and every answer is published at once (useLoad.ts) - the galaxy on screen is the previous
  // one's and says so. A failed answer ends the swap like any other, but leaves the mark up with its message until
  // the next Generate or landing: what is drawn is then not wholly the inputs shown. Only a Generate marks it; a
  // landing is the template's galaxy, with its own "Generating" line, and clears what a Generate left.
  const swap = useSwap();
  const [settled, setSettled] = useState(0); // the last Generate whose swap has completed
  const [failure, setFailure] = useState<string | null>(null);
  useEffect(() => {
    if (wf.generation === settled) return;
    // A Generate whose query no loader is asking with (none mounted) has nothing to wait for.
    if (swap.swapping && pendingLoads() === 0) settleSwap();
    if (!swap.swapping) {
      setSettled(wf.generation);
      setFailure(swap.failure);
    }
  }, [wf.generation, settled, swap]);
  useEffect(() => {
    setSettled(wf.generation);
    setFailure(null);
  }, [wf.selection]); // eslint-disable-line react-hooks/exhaustive-deps -- a landing, not a Generate
  const stale = wf.generation !== settled;
  const marked = stale || failure !== null;

  // The star sample runs every stage, so it is only asked for where stars are drawn: the Galaxy
  // tab. The Science tab shows fields only, in every group including the last two.
  // The Science scene keeps its three stands; while the Galaxy view is at a template's camera it shows the oblique one.
  const previewPreset: Preset = preset ?? "oblique";
  const drawsStars = tab === "galaxy";
  const sampleKey = drawsStars && galaxyQuery ? JSON.stringify(galaxyQuery) : null;
  const galaxy = useLoad<Sample>(sampleKey, (signal) => loadSample(galaxyQuery!, signal));
  const sample = galaxy.value;

  const seed = wf.shown?.state.values.world_seed;
  // The model is named only where there is a choice of one; there are two since S27 (D176) and the
  // selector shows them; the default is the azimuthal one since S46 (D197).
  // The hash is the input vector's, the workflow's query: the layer's switch is not an input and does not move
  // it. While the Galaxy view is drawn physics only the line says so after the hash, in words. Since S58 the
  // query names the template the galaxy was started from, and the hash moves with it: the pins it brings are
  // inputs of the run, so the same controls under another template are another galaxy.
  const layerMark = physicsOnly && tab === "galaxy" ? ` · ${PHYSICS_ONLY}` : "";
  const hash = query ? `${runHash(query)}${wf.models.length > 1 ? ` · ${shownModel}` : ""} · world_seed ${seed}${layerMark}` : "";
  // The template the galaxy is, in every tab: its label, and "edited" once it was generated from changed inputs.
  const galaxyName = wf.template && wf.shown ? templateLabel(wf.template, wf.edited) : "";
  // What the header names is what is drawn (rule D1 as amended): while a Generate is under way, or failed, the
  // label stays the previous galaxy's, said so, rather than naming the inputs the picture does not show yet.
  const live = { hash, galaxyName, edited: wf.edited };
  const label = useRef(live);
  if (!marked) label.current = live; // a ref filled in render, never in a memo (StrictMode builds a memo twice)
  const named = marked ? label.current : live;
  const labelMark = stale ? " · generating" : failure !== null ? " · generation failed" : "";
  // The template's pins, in the field declarations' words (S58, D217): they ride with every request the galaxy
  // makes, edited or not, so an edited galaxy's name says they still hold.
  const pinned = wf.template?.pins.map((p) => pinWords(p, meta?.fields)).join("; ") ?? "";
  // Two tabs, both open at any time (V9): the galaxy, and every group's previews of it.
  const tabs: { key: Tab; label: string; title?: string }[] = [
    { key: "science", label: "Science", title: "Every group's published fields, previewed for the galaxy on screen" },
    { key: "galaxy", label: "Galaxy" },
  ];
  // The edit panel as the Science tab's rail: its groups choose the previews.
  const rail = (
    <WorkflowPanel
      wf={wf}
      tMax={meta?.grid.axes.t?.hi}
      fields={meta?.fields}
      className={styles.floatingRail}
      viewing={current?.n ?? null}
      onView={setViewing}
    />
  );
  const staleMark = marked && (
    <p className={styles.stale} role="status" data-failed={failure !== null || undefined}>
      {stale
        ? "Stale · the previous galaxy, until the generated one arrives"
        : `Generation failed: ${briefly(failure ?? "")}. What is drawn is not the inputs shown: change them and generate again, or reset.`}
    </p>
  );

  const status = (
    <>
      {!sample && !galaxy.error && !(wf.error && !wf.state) && <p className={styles.status}>Generating galaxy.</p>}
      {wf.error && !wf.state && (
        <p className={styles.status}>
          Loading the model failed: {wf.error}. Check that the API is running (<code>uv run python -m galaxy.api</code>).
        </p>
      )}
      {galaxy.error && !layerFault && (
        <p className={styles.status}>
          Generation failed: {galaxy.error}. Check that the API is running (<code>uv run python -m galaxy.api</code>).
        </p>
      )}
      {/* A frame refused for its layer setting is not drawn; with the star sample refused the panel that holds
          the switch is gone too, so the way back is here. */}
      {layerFault && (
        <p className={styles.status} role="alert">
          {layerFault}.{" "}
          {physicsOnly && (
            <button type="button" className={styles.footToggle} onClick={() => setPhysicsOnly(false)}>
              draw the galaxy with the layer
            </button>
          )}
        </p>
      )}
      {galaxy.busy && sample && <div className={styles.busy} aria-hidden />}
      {staleMark}
    </>
  );

  return (
    <div className={styles.shell}>
      <header className={styles.topbar}>
        <span className={styles.wordmark}>galaxygen</span>
        {named.galaxyName && (
          <span
            className={styles.galaxyName}
            title={
              named.edited
                ? `Edited from the ${wf.template!.label} template: choose it again in the Galaxy view to restore it${pinned ? `. The template's pins still hold - ${pinned}` : ""}`
                : wf.template!.about
            }
          >
            {named.galaxyName}
          </span>
        )}
        <span
          className={styles.hash}
          title={`Run hash of the input vector · model · world seed${layerMark ? " · the Galaxy view is drawn with the randomness layer off (a display setting: no input, so the hash is the same)" : ""}`}
        >
          {named.hash}
          {labelMark}
        </span>
        <span className={styles.spacer} />
        {tab === "science" && (
          <div className={styles.segmented} role="group" aria-label="Science view">
            {SCIENCE_LOOKS.map((look) => (
              <button key={look} aria-pressed={scienceLook === look} onClick={() => setScienceLook(look)}>
                {look}
              </button>
            ))}
          </div>
        )}
        <div className={styles.segmented} role="tablist" aria-label="View">
          {tabs.map((t) => (
            <button
              key={t.key}
              role="tab"
              aria-pressed={tab === t.key}
              aria-selected={tab === t.key}
              title={t.title}
              onClick={() => setTab(t.key)}
            >
              {t.label}
            </button>
          ))}
        </div>
      </header>

      <main className={styles.main}>
        <ErrorBoundary resetKey={`${tab}:${scienceLook}:${current?.n}:${shownModel}`}>
          {/* The Science tab (V9): every group's previews of the galaxy on screen, any group at any time, nothing
              regenerated to look (T18 by construction). The edit panel is its rail; a group's "previews" button
              chooses what is drawn. */}
          {tab === "science" && scienceLook === "scene" && (
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
              {rail}

              {current && (
                <div className={styles.previewTitle}>
                  <span className={styles.overlayLabel}>Science · {current.name}</span>
                  <span className={styles.previewName}>{PRODUCES[current.n] ?? current.name}</span>
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
              {staleMark}
            </div>
          )}

          {tab === "science" && scienceLook === "plots" && (
            <div className={styles.scienceStage}>
              {rail}
              <div className={styles.scienceBody}>
                {current && panels && query && meta ? (
                  <ScienceView checkpoint={current} panels={panels} query={query} cmaps={meta.cmaps} />
                ) : (
                  <p className={styles.status}>Loading field declarations.</p>
                )}
              </div>
              {staleMark}
            </div>
          )}

          {tab === "galaxy" && (
            <div className={styles.canvasStage}>
              {meta && sample && galaxyQuery && (
                <GalaxyTab
                  meta={meta}
                  sample={sample}
                  fields={PAINT_CHOICES}
                  field={field}
                  onField={setField}
                  exposure={exposure}
                  onExposure={setExposure}
                  query={galaxyQuery}
                  physicsOnly={physicsOnly}
                  onPhysicsOnly={setPhysicsOnly}
                  preset={preset}
                  onPreset={setPreset}
                  editing={editing}
                  onEdit={() => setEditing((e) => !e)}
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
              {editing && (
                <WorkflowPanel
                  wf={wf}
                  tMax={meta?.grid.axes.t?.hi}
                  fields={meta?.fields}
                  className={styles.editDrawer}
                  onClose={() => setEditing(false)}
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
