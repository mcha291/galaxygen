import { useEffect, useMemo, useRef, useState } from "react";

import { type FieldsPayload, type Query, type Sample, loadFields, loadSample } from "../api";
import { useLoad } from "../useLoad";
import { type CompareSource, type ShownTrack, defaultSource, paneExposure, paneGalaxy, sourceItems, sourceKey, sourceSet, trackShown } from "../workflow/comparison";
import type { FlowState } from "../workflow/logic";
import type { Template } from "../workflow/templates";
import type { CameraLink } from "./cameraLink";
import type { PictureScale } from "./compare";
import { FILTER_SETS, FILTER_SET_NAMES, type FilterSetName } from "./filters";
import { GalaxyTab, type Mode } from "./GalaxyTab";
import type { Preset, ViewState } from "./GalaxyView";
import { layerQuery } from "./layer";
import { type ComparePicture, PictureFrame } from "./PictureBeside";
import { extent, toScene } from "./positions";
import { useDebounced } from "./TuningPanel";
import styles from "./ComparePane.module.css";

// The comparison view's right pane (T16, S83): a second galaxy beside the galaxy shown - another template, the draft,
// the galaxy shown through another filter set - or a picture file, chosen from a small bar above it. The galaxy is a
// GalaxyTab of its own (its query, its filter set, its template's display tuning, its own loads through the same
// loaders) under the left pane's camera (cameraLink.ts: one camera state drives both) and in the left pane's mode.
//
// Rule D1 per pane: the pane draws one galaxy, whole. Its view is keyed on the galaxy it was loaded for and made afresh
// for another, so no answer of one galaxy is ever drawn under another's; until the next galaxy's star sample is in,
// the pane keeps the last one, whole, and says what it is loading.
//
// The head start (fieldLoads.ts askFieldAhead) is the galaxy shown's alone: this pane's field loads are asked by its own
// loaders on its mount. api.ts keeps one galaxy's head start at a time and drops (aborts) the last's for another query, so
// asking this pane's ahead while the galaxy shown waits on its own - a landing or a Generate with the comparison on -
// would abort the shown galaxy's untaken answers and turn its head start into repeated requests.

/** The framing radius the left pane's view is made from (GalaxyTab's: the sample's extent, else 20 kpc). */
const DISC_RADIUS = 20;
function reachOf(sample: Sample): number {
  const c = sample.columns as Record<string, ArrayLike<number>>;
  return extent(toScene(c.star_radius, c.star_azimuth, c.star_height)) || DISC_RADIUS;
}

/** How long the draft must stand still before the pane generates it: an edit is a whole new galaxy here. */
const DRAFT_SETTLE_MS = 600;
const noop = () => undefined;

interface Loaded {
  key: string;
  query: Query;
  sample: Sample;
  meta: FieldsPayload;
  template: Template | null;
  label: string;
}

interface Props {
  templates: Template[];
  /** The galaxy shown: the workflow's query (no layer switch), its template and whether it is edited. */
  shown: { query: Query; template: Template | null; edited: boolean };
  /** The edit panel's query while it differs from the galaxy shown and can be generated; else null. */
  draft: Query | null;
  generation: number;
  selection: number;
  /** A model's catalogue, where the workflow holds one (a template's query is laid on it). */
  catalogueOf(model: string): FlowState["cat"] | null;
  /** The left pane: its star sample's key and sample (answered for that key), declarations, set, exposure, template, view. */
  left: { key: string | null; sample: Sample; answered: Sample | null; meta: FieldsPayload; set: FilterSetName; exposure: number; template: Template | null; view: ViewState | null };
  physicsOnly: boolean;
  onPhysicsOnly(on: boolean): void;
  mode: Mode;
  fields: string[];
  field: string;
  onField(name: string): void;
  preset: Preset | null;
  onPreset(p: Preset | null): void;
  camera: { selection: number; preset: Preset | null; template: Template | null };
  link: CameraLink;
}

export function ComparePane(props: Props) {
  const { templates, shown, draft, left, physicsOnly, link } = props;
  const [source, setSource] = useState<CompareSource>(() => defaultSource(templates, shown.template, shown.edited));
  const templateOfSource = (s: CompareSource) => (s.kind === "template" ? (templates.find((t) => t.name === s.name) ?? null) : shown.template);
  const [set, setSet] = useState<FilterSetName>(() => sourceSet(source, templateOfSource(source), left.set, FILTER_SET_NAMES));
  const choose = (s: CompareSource) => {
    setSource(s);
    setSet(sourceSet(s, templateOfSource(s), left.set, FILTER_SET_NAMES));
  };

  // The galaxy shown before the last Generate: the draft pane's once the draft is that Generate's (the panes trade).
  const track = useRef<ShownTrack>({ generation: props.generation, selection: props.selection, query: shown.query, previous: null });
  track.current = trackShown(track.current, { generation: props.generation, selection: props.selection, query: shown.query });
  // The draft, generated here once it has stood still (an edit is a whole galaxy); none the moment it is the galaxy shown.
  const draftText = draft ? JSON.stringify(draft) : null;
  const settledDraft = useDebounced(draftText, DRAFT_SETTLE_MS);
  const draftNow = draftText !== null && settledDraft !== null ? (JSON.parse(settledDraft) as Query) : null;

  const galaxy = paneGalaxy(source, { templates, shown, draft: draftNow, previous: track.current.previous, catalogueOf: props.catalogueOf });
  const query = "query" in galaxy ? layerQuery(galaxy.query, physicsOnly) : null;
  const key = query ? JSON.stringify(query) : null;
  // The galaxy shown through another set: its star sample is the left pane's, taken once answered, never asked twice.
  const fromLeft = key !== null && key === left.key;
  const askKey = key !== null && !(fromLeft && !left.answered) ? key : null;
  const model = query ? String(query.model ?? left.meta.model) : null;
  const loaded = useLoad<Loaded>(
    askKey,
    async (signal) => {
      const [sample, meta] = await Promise.all([
        fromLeft && left.answered ? left.answered : loadSample(query!, signal),
        model === left.meta.model ? left.meta : loadFields(model!, signal),
      ]);
      return { key: key!, query: query!, sample, meta, template: "query" in galaxy ? galaxy.template : null, label: "query" in galaxy ? galaxy.label : "" };
    },
    0,
  );
  const drawn = source.kind === "picture" ? null : loaded.value;
  const reach = useMemo(() => reachOf(left.sample), [left.sample]);

  // The picture (T16 ii): a file the user picked, shown through an object URL, released when replaced or unmounted.
  const [picture, setPicture] = useState<ComparePicture | null>(null);
  useEffect(
    () => () => {
      if (picture) URL.revokeObjectURL(picture.url);
    },
    [picture],
  );
  const file = useRef<HTMLInputElement>(null);
  const [band, setBand] = useState("");
  const [unit, setUnit] = useState<"arcsec" | "kpc">("arcsec");
  const [perPixel, setPerPixel] = useState("");
  // The distance an angular scale is read at: the galaxy shown's template's where it states one (NGC 4414's 17.7 Mpc).
  const [distance, setDistance] = useState(() => (shown.template?.instrument.distance_mpc ?? "").toString());
  const scale: PictureScale = unit === "kpc" ? { unit, perPixel: Number(perPixel || Number.NaN) } : { unit, perPixel: Number(perPixel || Number.NaN), distanceMpc: Number(distance || Number.NaN) };
  const distances = templates.filter((t) => t.instrument.distance_mpc !== null);

  const items = sourceItems(templates, shown.template, shown.edited, { ready: draft !== null, previous: track.current.previous !== null }, (m) => props.catalogueOf(m) !== null);
  const loading = source.kind !== "picture" && key !== null && drawn?.key !== key;

  return (
    <>
      {drawn && (
        <GalaxyTab
          key={drawn.key}
          pane="right"
          meta={drawn.meta}
          sample={drawn.sample}
          fields={props.fields}
          field={props.field}
          onField={props.onField}
          exposure={paneExposure(left.exposure, left.template?.name ?? null, drawn.template?.name ?? null)}
          onExposure={noop}
          query={drawn.query}
          preset={props.preset}
          onPreset={props.onPreset}
          onEdit={noop}
          filterSet={set}
          onFilterSet={setSet}
          templates={[]}
          template={drawn.template}
          edited={false}
          onTemplate={noop}
          // The left pane's camera: its landing count too, so this pane is never in a landing's hold of its own (its
          // template is not the camera's), and draws with its own template's tuning.
          selection={props.camera.selection}
          camera={props.camera}
          physicsOnly={physicsOnly}
          onPhysicsOnly={props.onPhysicsOnly}
          link={link}
          mode={props.mode}
          frame={reach}
          label={drawn.label}
        />
      )}
      {source.kind === "picture" && <PictureFrame picture={picture} band={band} scale={scale} pxPerKpc={left.view?.pxPerKpc ?? null} />}
      {source.kind !== "picture" && !drawn && <p className={styles.waiting}>{"none" in galaxy ? galaxy.none : "query" in galaxy ? `Generating ${galaxy.label}.` : ""}</p>}

      <div className={styles.bar} role="group" aria-label="Beside the galaxy shown">
        <div className={styles.row}>
          {items.map((item) => (
            <button
              key={item.key}
              type="button"
              aria-pressed={sourceKey(source) === item.key}
              disabled={item.disabled}
              title={item.title}
              onClick={() => choose(item.source)}
            >
              {item.label}
            </button>
          ))}
        </div>
        {source.kind !== "picture" ? (
          <div className={styles.row} role="group" aria-label="This pane's filter set">
            {FILTER_SET_NAMES.map((name) => (
              <button key={name} type="button" aria-pressed={name === set} title={FILTER_SETS[name].about} onClick={() => setSet(name)}>
                {FILTER_SETS[name].label}
              </button>
            ))}
          </div>
        ) : (
          <div className={styles.row}>
            <input
              ref={file}
              type="file"
              accept="image/png,image/jpeg"
              hidden
              aria-label="Picture to compare with"
              onChange={(e) => {
                const chosen = e.target.files?.[0];
                e.target.value = ""; // so the same file can be chosen again
                if (chosen) setPicture({ url: URL.createObjectURL(chosen), name: chosen.name });
              }}
            />
            <button type="button" title="Choose a PNG or JPEG from this computer. It stays in the browser." onClick={() => file.current?.click()}>
              {picture ? "another file" : "choose file"}
            </button>
            <label className={styles.field} title="The band the picture was taken in, as you state it: shown on the caption, read by nothing">
              band
              <input type="text" value={band} size={9} placeholder="e.g. F814W" onChange={(e) => setBand(e.target.value)} />
            </label>
            <label className={styles.field} title="The picture's pixel scale">
              scale
              <input type="number" min={0} step="any" value={perPixel} size={6} onChange={(e) => setPerPixel(e.target.value)} />
            </label>
            <select aria-label="The scale's unit" value={unit} onChange={(e) => setUnit(e.target.value as "arcsec" | "kpc")}>
              <option value="arcsec">″ / px</option>
              <option value="kpc">kpc / px</option>
            </select>
            {unit === "arcsec" && (
              <label className={styles.field} title="The distance the angular scale is read at, Mpc">
                at
                <input type="number" min={0} step="any" value={distance} size={5} onChange={(e) => setDistance(e.target.value)} />
                Mpc
              </label>
            )}
            {unit === "arcsec" &&
              distances.map((t) => (
                <button key={t.name} type="button" title={`${t.label}'s distance, as its template states it`} onClick={() => setDistance(String(t.instrument.distance_mpc))}>
                  {`${t.label}'s ${t.instrument.distance_mpc} Mpc`}
                </button>
              ))}
          </div>
        )}
        {loading && "query" in galaxy && drawn && <p className={styles.note}>{`Generating ${galaxy.label}: ${drawn.label} until it is in.`}</p>}
      </div>
    </>
  );
}
