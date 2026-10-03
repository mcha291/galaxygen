import { useMemo, useRef, useState } from "react";

import {
  type BlackbodyTable,
  type BrightFrame,
  type Census,
  type FieldsPayload,
  type Query,
  type Sample,
  STAR_SAMPLE,
  loadBlackbody,
  loadBright,
  loadClouds,
  loadClusters,
  loadRegion,
} from "../api";
import { CellOutlines, CloudMarkers } from "./ComponentLayers";
import { CLOUD_COLUMNS, type DustPaintShown, WHERE_LEVEL, brightestLayers, cloudColors, diagnosticOn, dustRamp, marchWanted, rowsInWindow } from "./components";
import { useLoad } from "../useLoad";
import { formatNumber } from "../workflow/logic";
import { PHOTOMETRIC, lightColors, photometricColors, starColors } from "./colors";
import { Exposure } from "./Exposure";
import { FieldLegend } from "./FieldLegend";
import { FieldVolume, LIGHT_PER_LSUN_PC2, type MarchStats } from "./FieldVolume";
import { fluxOf } from "./flux";
import { FluxPoints, type PointDust } from "./FluxPoints";
import { CLUSTER_SUMMARY, STAR_SUMMARY, type SummaryRow, summaryRows } from "./summary";
import { levelFor } from "./region";
import { RegionVolume } from "./RegionVolume";
import { FILTER_SETS, FILTER_SET_NAMES, type FilterSetName, curvesOf } from "./filters";
import { instrumentPsf } from "./psf";
import { footprint } from "./frustum";
import { GalaxyView, type Preset, type StarLayer, type ViewState } from "./GalaxyView";
import { extent, toScene } from "./positions";
import { REGIME_KPC, regimeWeights, regionAround, regionSampleSize, starsInWindow } from "./regimes";
import { type Tuning, loadTuning, saveTuning } from "./tuning";
import { TuningPanel, useDebounced } from "./TuningPanel";
import { scaleBar } from "./zoom";
import styles from "./GalaxyTab.module.css";

interface Props {
  meta: FieldsPayload;
  sample: Sample;
  fields: string[];
  field: string;
  onField(name: string): void;
  exposure: number;
  onExposure(stops: number): void;
  query: Query;
  preset: Preset;
  onPreset(p: Preset): void;
  /** "Edit galaxy": open the staged generation with the confirmations kept (D198). Discards nothing. */
  onEdit(): void;
}

const SHORT: Record<string, string> = {
  star_metallicity: "[Fe/H]",
  star_alpha: "[α/Fe]",
  star_age: "age",
  star_population: "pop",
  star_mass: "mass",
  star_birth_radius: "R_birth",
  star_temperature: "T_eff",
  star_luminosity: "L",
  [PHOTOMETRIC]: "light",
};

/** The largest sample a region is materialised at (the API's own ceiling is 5 × 10⁶). */
const REGION_MAX_STARS = 1_000_000;
/** About how many stars a close view asks for: dense, and still quick to draw and to send. */
const REGION_TARGET_STARS = 60_000;
/** The framing radius of the view, kpc: most of the disc's light. */
const DISC_RADIUS = 20;

const REGIMES = [
  { key: "field", label: "field", name: "Field", what: "The galaxy's light, integrated along every line of sight through the published fields." },
  { key: "sampled", label: "sampled", name: "Sampled points", what: "The whole-galaxy star sample over the field." },
  { key: "stars", label: "stars", name: "Stars", what: "This region's own stars, materialised at a sample size scaled to the view." },
] as const;

/** The view width, kpc, each regime button takes the camera to. */
const REGIME_VIEW_KPC = { field: 45, sampled: 12, stars: 2.5 } as const;

/**
 * The two ways the galaxy is rendered. The field mode is the design brief's three regimes above.
 * The star-first mode (S50, D208) draws what the model can name, on the field's own scale: the N most
 * luminous disc stars inside the camera's frustum (the bright catalogue, complete above its threshold) and
 * every cluster of the census, each a point of its own light through the filter set, over the field no
 * point carries (the render's remainder under that threshold). It replaces the "brightest" mode, whose
 * stars were the brightest of a number-drawn sample.
 */
type Mode = "field" | "stars";
const MODES: { key: Mode; label: string; what: string }[] = [
  { key: "field", label: "field", what: "The field, the sample and a region's stars, handed over by zoom." },
  { key: "stars", label: "star-first", what: "The N brightest stars in view and every cluster, as points of their own light over the field no point carries." },
];
/**
 * How long the view must hold still before the star-first mode re-selects: a selection is under a second
 * warm (the server keeps the catalogue's cells), and each new threshold asks the field's remainder again.
 */
const BRIGHT_SETTLE_MS = 250;
/** A layer that is picked and not drawn by the view's own sprites carries no colours. */
const NO_COLORS = new Float32Array(0);
/** The N slider's range, decades: 10² to 10⁵ stars, logarithmic. */
const BRIGHTEST_DECADES = { lo: 2, hi: 5 };
/** The star-first mode's component switches (D205, D208), each a tuning value: the picture's four on by default, the diagnostics off. */
const COMPONENT_SWITCHES: { key: "compPoints" | "compStars" | "compGas" | "compDust" | "compClouds" | "compCells"; label: string; what: string }[] = [
  { key: "compPoints", label: "stars", what: "The N most luminous disc stars in view and every cluster, as points of their own light on the field's scale. Off draws the whole starlight as a volume" },
  { key: "compStars", label: "starlight", what: "The starlight no point carries (all of it while the stars are off) and the bulge, as the volume the model publishes light for" },
  { key: "compGas", label: "ionized gas", what: "The HII regions' layer and the diffuse gas's layer, with their lines, as the field draws them" },
  { key: "compDust", label: "dust", what: "The dust: as it acts (extinction, scattered and thermal light) or where it is (a diagnostic)" },
  { key: "compClouds", label: "molecular clouds", what: "The cloud census as markers sized by cloud_size, painted by cloud_mass's ramp (a diagnostic)" },
  { key: "compCells", label: "cell outlines", what: "The level-0 cells, 32 rings by 32 sectors, the volumes the catalogues are drawn in (a diagnostic)" },
];
const DUST_READINGS: { key: "acts" | "where"; label: string; what: string }[] = [
  { key: "acts", label: "as it acts", what: "Extinction of what lies behind it, and its scattered and thermal light: the physical picture" },
  { key: "where", label: "where it is", what: "A diagnostic: its optical depth along each line of sight drawn as light through a declared ramp, normalised to its peak face-on depth, dimming nothing" },
];
const brightestOf = (slider: number) => Math.round(10 ** (BRIGHTEST_DECADES.lo + ((BRIGHTEST_DECADES.hi - BRIGHTEST_DECADES.lo) * slider) / 1000));

/** The view-projection rounded so the request key does not change with the last bits of a settled camera. */
const roundedView = (m: number[]) => m.map((v) => Number(v.toPrecision(5)));

/**
 * The zoom slider position that makes the view `width` kpc across. The slider is linear in
 * log distance over GalaxyView's range (reach/200 to 8 reach, a factor of 1600) and the width
 * is proportional to distance, so it is a shift from where the view is now.
 */
function zoomForWidth(view: ViewState, width: number): number {
  return Math.min(1, Math.max(0, view.zoom - Math.log(width / view.across) / Math.log(1600)));
}

function colorsFor(
  meta: FieldsPayload,
  sample: Sample,
  field: string,
  exposure: number,
  table: BlackbodyTable | null = null,
  pointGain = 1,
): Float32Array | null {
  try {
    return field === PHOTOMETRIC ? photometricColors(meta, sample.columns, exposure, table, pointGain) : starColors(meta, sample.columns, field);
  } catch {
    return null; // the fields for a just-switched model have not arrived yet
  }
}

function positionsOf(sample: Sample): Float32Array {
  const c = sample.columns as Record<string, ArrayLike<number>>;
  return toScene(c.star_radius, c.star_azimuth, c.star_height);
}

/**
 * The finished galaxy in its three regimes (design brief §3), handed over by zoom: the field
 * for the whole galaxy, the sample as it fills the view, and a region's own stars close up.
 */
export function GalaxyTab({ meta, sample, fields, field: chosen, onField, exposure, onExposure, query, preset, onPreset, onEdit }: Props) {
  const [zoom, setZoom] = useState<number | undefined>(undefined);
  const [view, setView] = useState<ViewState | null>(null);
  const [mode, setMode] = useState<Mode>("field");
  const [filterSet, setFilterSet] = useState<FilterSetName>("rgb");
  // The Tuning panel's display choices (D199): a UI preference kept in localStorage, today's values by default.
  const [tuning, setTuningState] = useState<Tuning>(() => loadTuning());
  const setTuning = (t: Tuning) => {
    setTuningState(t);
    saveTuning(t);
  };
  // A new step count recompiles the march's shader and a new white point asks the model again: both wait for the slider to settle.
  const steps = useDebounced(tuning.steps, 300);
  const whiteKelvin = useDebounced(tuning.whiteKelvin, 400);
  const fieldTuning = { ...tuning, steps, whiteKelvin };
  const marchStats = useRef<MarchStats>({ width: 0, height: 0, ms: 0 }).current;
  const pointGain = tuning.pointGain;
  // The filter set's blackbody table (S42, P6): stars and clusters are drawn through the same curves as the field.
  const blackbodyKey = JSON.stringify([filterSet, whiteKelvin]);
  const blackbodyTable = useLoad<BlackbodyTable>(blackbodyKey, (signal) => loadBlackbody(curvesOf(filterSet), whiteKelvin, signal)).value ?? null;
  // A named instrument's filter set brings its point spread function to the stars (S42).
  const spritePsf = useMemo(() => instrumentPsf(FILTER_SETS[filterSet]), [filterSet]);
  const [brightestSlider, setBrightestSlider] = useState(500);
  const brightestN = brightestOf(brightestSlider);
  // A column some models lack ([α/Fe] is the advanced chemistry's) offers no chip where the
  // sample has none, and a choice the current model cannot paint falls back to light.
  const paintable = fields.filter((f) => f === PHOTOMETRIC || f in sample.columns);
  const field = paintable.includes(chosen) ? chosen : PHOTOMETRIC;
  const decl = meta.fields.find((f) => f.name === field);
  const bar = view ? scaleBar(view.pxPerKpc) : null;
  const weights = regimeWeights(view?.across ?? REGIME_KPC.field * 2, tuning.fieldFloor);
  const regime = REGIMES.find((r) => r.key === weights.active)!;

  // The stars regime: the window around where the view looks, at a sample size scaled to it.
  const area = mode === "field" && view && weights.stars > 0 ? regionAround(view.target[0], view.target[2], view.across * 0.75) : null;
  const inWindow = useMemo(() => {
    if (!area) return 0;
    const c = sample.columns as Record<string, ArrayLike<number>>;
    return starsInWindow(c.star_radius, c.star_azimuth, area);
  }, [sample, area?.r_min, area?.r_max, area?.phi_min, area?.phi_max]); // eslint-disable-line react-hooks/exhaustive-deps
  const regionStars = area ? regionSampleSize(STAR_SAMPLE, inWindow, REGION_TARGET_STARS, REGION_MAX_STARS) : 0;
  const regionKey = area ? JSON.stringify([area, regionStars, query]) : null;
  const region = useLoad<Sample>(regionKey, (signal) => loadRegion(area!, regionStars, query, signal));
  const detail = region.value && regionKey ? region.value : null;
  // The region's clusters (V3's volume, V4's points, S41): loaded once at the level the view asks for.
  const level = area && view ? levelFor(view.across) : 0;
  const clustersKey = area ? JSON.stringify([area, level, query]) : null;
  const regionClusters = useLoad<Census>(clustersKey, (signal) => loadClusters({ ...area!, level }, query, signal)).value ?? null;
  const shownClusters = area && regionClusters ? regionClusters : null;
  const clusterPositions = useMemo(() => {
    if (!shownClusters) return null;
    const c = shownClusters.columns as Record<string, ArrayLike<number>>;
    return c.cluster_radius ? toScene(c.cluster_radius, c.cluster_azimuth, c.cluster_height) : null;
  }, [shownClusters]);
  const clusterColors = useMemo(() => {
    if (!shownClusters || !shownClusters.columns.cluster_luminosity) return null;
    return lightColors(meta, shownClusters.columns, exposure, "cluster_light_temperature", "cluster_luminosity", blackbodyTable, pointGain);
  }, [meta, shownClusters, exposure, blackbodyTable, pointGain]);

  // The star-first mode (D208): the frustum's footprint, and the N brightest disc stars inside the frustum, each
  // with its own light through the filter set. Nothing is asked for while the star points are switched off (the
  // footprint still cuts the cloud census).
  const rMax = meta.grid.axes.R?.hi ?? DISC_RADIUS * 1.5;
  const R = meta.grid.axes.R;
  const wholeDisc = { r_min: R?.lo ?? 0, r_max: rMax, phi_min: 0, phi_max: 2 * Math.PI, level: 0 };
  const seen = mode === "stars" && view ? footprint(view.camera.viewProjection, rMax) : null;
  const pointsOn = mode === "stars" && tuning.compPoints;
  const brightKey =
    seen && view && pointsOn ? JSON.stringify([seen, brightestN, roundedView(view.camera.viewProjection), filterSet, whiteKelvin, query]) : null;
  const brightLoad = useLoad<BrightFrame>(
    brightKey,
    (signal) => loadBright(seen!, brightestN, view!.camera.viewProjection, curvesOf(filterSet), whiteKelvin, query, signal),
    BRIGHT_SETTLE_MS,
  );
  const bright = pointsOn && brightLoad.value ? brightLoad.value : null;
  // The young population is the cluster census's (the bright catalogue holds no star under 20 Myr): every cluster
  // of the disc with its own light through the set, loaded once per set and query (about 13 000).
  const starClustersKey = pointsOn ? JSON.stringify(["clusters", filterSet, whiteKelvin, query]) : null;
  const starClusters = useLoad<Census>(starClustersKey, (signal) =>
    loadClusters(wholeDisc, query, signal, { curves: curvesOf(filterSet), white: whiteKelvin }),
  ).value;
  const clusterCensus = pointsOn && starClusters ? starClusters : null;
  // The field under the points is the light no point carries, above the luminosity the selection is complete to:
  // the bright header's own threshold, never the viewer's arithmetic (D5, D208). Without points, the whole of it.
  const lMin = bright ? bright.header.threshold.l_min : null;
  const brightPoints = useMemo(() => {
    if (!bright) return null;
    const c = bright.columns as Record<string, ArrayLike<number>>;
    if (!c.bright_star_radius) return null;
    const flux = fluxOf(c.response, bright.header.white?.response, c.bright_star_radius.length);
    return flux ? { positions: toScene(c.bright_star_radius, c.bright_star_azimuth, c.bright_star_height), flux } : null;
  }, [bright]);
  const clusterPoints = useMemo(() => {
    if (!clusterCensus) return null;
    const c = clusterCensus.columns as Record<string, ArrayLike<number>>;
    if (!c.cluster_radius) return null;
    const flux = fluxOf(c.response, clusterCensus.header.white?.response, c.cluster_radius.length);
    return flux ? { positions: toScene(c.cluster_radius, c.cluster_azimuth, c.cluster_height), flux } : null;
  }, [clusterCensus]);
  // One gain for the field and the points (D208): the field's per L☉/pc², its gain and the exposure's stops; the
  // point gain stays a display multiplier on the points (D199).
  const pointsGain = LIGHT_PER_LSUN_PC2 * tuning.fieldGain * 2 ** exposure * pointGain;
  // The march's dust, handed up by the field volume for the segment to each point (T20): only as it acts.
  const [fieldDust, setFieldDust] = useState<PointDust | null>(null);
  const pointDust = mode === "stars" && tuning.compDust && tuning.dustReading === "acts" ? fieldDust : null;
  // What a click on a point opened (T23): the object's own published columns.
  const [picked, setPicked] = useState<{ title: string; rows: SummaryRow[] } | null>(null);
  const named = (columns: Record<string, ArrayLike<number | bigint>>, row: number, key: string) =>
    columns[key] ? Number(columns[key][row]).toLocaleString("en") : "—";
  const pickStar = (row: number) => {
    if (!bright) return;
    const c = bright.columns as Record<string, ArrayLike<number | bigint>>;
    setPicked({ title: `bright star · cell ${named(c, row, "cell")}, rank ${named(c, row, "rank")}`, rows: summaryRows(meta, bright.columns, row, STAR_SUMMARY) });
  };
  const pickCluster = (row: number) => {
    if (!clusterCensus) return;
    const c = clusterCensus.columns as Record<string, ArrayLike<number | bigint>>;
    setPicked({ title: `cluster · cell ${named(c, row, "cell")}, index ${named(c, row, "index")}`, rows: summaryRows(meta, clusterCensus.columns, row, CLUSTER_SUMMARY) });
  };

  // The star-first mode's component layers (D205, D208): the picture's four on by default, the diagnostics off.
  const marchOn = mode === "stars" && marchWanted(tuning);
  const ramp = useMemo(() => dustRamp(meta), [meta]);
  const [dustPaint, setDustPaint] = useState<DustPaintShown | null>(null);
  const marchLayers = brightestLayers(tuning, ramp);
  const diagnostic = mode === "stars" && diagnosticOn(tuning);
  // The whole disc's cloud census, loaded once per query (about 17 000 clouds) and cut to the footprint here.
  const cloudsKey = mode === "stars" && tuning.compClouds ? JSON.stringify(["clouds", query]) : null;
  const cloudCensus = useLoad<Census>(cloudsKey, (signal) => loadClouds(wholeDisc, query, signal)).value ?? null;
  const cloudPaint = useMemo(() => {
    if (!cloudCensus || !CLOUD_COLUMNS.every((k) => k in cloudCensus.columns)) return null;
    try {
      return cloudColors(meta, cloudCensus.columns, tuning.cloudIntensity);
    } catch {
      return null; // a census from a just-switched model, before its declarations
    }
  }, [meta, cloudCensus, tuning.cloudIntensity]);
  const cloudLayer = useMemo(() => {
    if (!cloudCensus || !cloudPaint || !seen) return null;
    const c = cloudCensus.columns as Record<string, ArrayLike<number>>;
    const rows = rowsInWindow(c.cloud_radius, c.cloud_azimuth, seen);
    const of = (col: ArrayLike<number>) => Float64Array.from(rows, (i) => Number(col[i]));
    const colors = new Float32Array(rows.length * 4);
    rows.forEach((i, k) => colors.set(cloudPaint.subarray(4 * i, 4 * i + 4), 4 * k));
    return {
      positions: toScene(of(c.cloud_radius), of(c.cloud_azimuth), of(c.cloud_height)),
      sizes: Float32Array.from(rows, (i) => Number(c.cloud_size[i])),
      colors,
    };
  }, [cloudCensus, cloudPaint, seen?.r_min, seen?.r_max, seen?.phi_min, seen?.phi_max]); // eslint-disable-line react-hooks/exhaustive-deps
  const setComponent = (patch: Partial<Tuning>) => setTuning({ ...tuning, ...patch });

  const samplePositions = useMemo(() => positionsOf(sample), [sample]);
  const sampleColors = useMemo(() => colorsFor(meta, sample, field, exposure, blackbodyTable, pointGain), [meta, sample, field, exposure, blackbodyTable, pointGain]);
  const detailPositions = useMemo(() => (detail ? positionsOf(detail) : null), [detail]);
  const detailColors = useMemo(() => (detail ? colorsFor(meta, detail, field, exposure, blackbodyTable, pointGain) : null), [meta, detail, field, exposure, blackbodyTable, pointGain]);
  // The framing radius comes from the sample in both modes, so the zoom slider means the same thing in each.
  const reach = useMemo(() => extent(samplePositions) || DISC_RADIUS, [samplePositions]);


  const layers: StarLayer[] = [];
  if (mode === "field") {
    // Drawn, not picked: clicking a star to open its planetary system was removed (D209); the system's
    // information will be shown another way.
    if (sampleColors) layers.push({ positions: samplePositions, colors: sampleColors, opacity: weights.sampled });
    if (detail && detailPositions && detailColors && weights.stars > 0) {
      layers.push({ positions: detailPositions, colors: detailColors, opacity: weights.stars });
    }
    // Clusters as objects (V4, S41): each a point of the light its stars sum to, in the region regime.
    if (clusterPositions && clusterColors && weights.stars > 0 && field === PHOTOMETRIC) {
      layers.push({ positions: clusterPositions, colors: clusterColors, opacity: weights.stars });
    }
  }
  // The star-first mode's points are drawn by FluxPoints on the field's scale; the view only picks them.
  const pickable: StarLayer[] = [];
  if (brightPoints) pickable.push({ positions: brightPoints.positions, colors: NO_COLORS, onPick: pickStar });
  if (clusterPoints) pickable.push({ positions: clusterPoints.positions, colors: NO_COLORS, onPick: pickCluster });

  const shown = weights.active === "stars" && detail ? detail : sample;
  const current = MODES.find((m) => m.key === mode)!;

  return (
    <>
      <GalaxyView layers={layers} pickable={pickable} reach={reach} preset={preset} zoom={zoom} onView={setView} hdr additive={field === PHOTOMETRIC} psf={spritePsf} tuning={tuning}>
        {mode === "field" && (
          <FieldVolume
            meta={meta}
            query={query}
            stops={exposure}
            weight={weights.field}
            filterSet={filterSet}
            regionWindow={area}
            hiiFade={area ? weights.stars : 0}
            tuning={fieldTuning}
            stats={marchStats}
          />
        )}
        {/* The star-first mode's field (D205, D208): the march with the switched layers at the whole field weight,
            its starlight the remainder under the points' threshold (the whole of it while the points are off). */}
        {marchOn && (
          <FieldVolume
            meta={meta}
            query={query}
            stops={exposure}
            weight={1}
            filterSet={filterSet}
            tuning={fieldTuning}
            stats={marchStats}
            layers={marchLayers}
            onDepth={setDustPaint}
            lMin={lMin}
            onDust={setFieldDust}
          />
        )}
        {/* The points, on the field's scale (D208): the clusters first, the bright stars over them. */}
        {clusterPoints && (
          <FluxPoints positions={clusterPoints.positions} flux={clusterPoints.flux} gain={pointsGain} psf={spritePsf} spriteSize={tuning.spriteSize} dust={pointDust} />
        )}
        {brightPoints && (
          <FluxPoints positions={brightPoints.positions} flux={brightPoints.flux} gain={pointsGain} psf={spritePsf} spriteSize={tuning.spriteSize} dust={pointDust} />
        )}
        {mode === "stars" && tuning.compCells && R && <CellOutlines lo={R.lo} hi={R.hi} />}
        {mode === "stars" && tuning.compClouds && cloudLayer && cloudLayer.sizes.length > 0 && (
          <CloudMarkers positions={cloudLayer.positions} sizes={cloudLayer.sizes} colors={cloudLayer.colors} />
        )}
        {/* The region regime (V3, S40): the window's clouds, HII regions and shells, at the level the view needs. */}
        {mode === "field" && area && view && weights.stars > 0 && (
          <RegionVolume query={query} window={area} level={level} clusters={regionClusters} stops={exposure} weight={weights.stars} filterSet={filterSet} whiteKelvin={whiteKelvin} />
        )}
      </GalaxyView>

      <div className={styles.panel}>
        <div className={styles.section}>
          <div className={styles.pair}>
            <button type="button" title="Open the staged generation and reopen a checkpoint to change the galaxy" onClick={onEdit}>
              Edit galaxy
            </button>
          </div>
        </div>
        <div className={styles.section}>
          <div className={styles.label}>Rendering</div>
          <div className={styles.pair}>
            {MODES.map((m) => (
              <button
                key={m.key}
                aria-pressed={m.key === mode}
                title={m.what}
                onClick={() => {
                  setMode(m.key);
                  setPicked(null);
                }}
              >
                {m.label}
              </button>
            ))}
          </div>
          {/* The filter set is chosen in either mode (T22): the star-first mode's points and its component
              volumes are seen through it as the field is, and a line set (SHO, HOO) is what shows the ionized gas. */}
          <div className={styles.label}>Filters</div>
          <div className={styles.pair}>
            {FILTER_SET_NAMES.map((name) => (
              <button key={name} aria-pressed={name === filterSet} title={FILTER_SETS[name].about} onClick={() => setFilterSet(name)}>
                {FILTER_SETS[name].label}
              </button>
            ))}
          </div>
          {mode === "stars" && (
            <>
              <div className={styles.zoomHead}>
                <span className={styles.label}>Brightest</span>
                <span className={styles.value}>{brightestN.toLocaleString("en")} stars</span>
              </div>
              <input
                type="range"
                className={styles.slider}
                min={0}
                max={1000}
                value={brightestSlider}
                aria-label="Brightest stars in view"
                onChange={(e) => setBrightestSlider(Number(e.target.value))}
              />
            </>
          )}
        </div>

        {mode === "stars" && (
          <div className={styles.section}>
            <div className={styles.label}>Components</div>
            <div className={styles.chips}>
              {COMPONENT_SWITCHES.map((s) => (
                <button key={s.key} type="button" aria-pressed={tuning[s.key]} title={s.what} onClick={() => setComponent({ [s.key]: !tuning[s.key] })}>
                  {s.label}
                </button>
              ))}
            </div>
            {tuning.compDust && (
              <div className={styles.pair}>
                {DUST_READINGS.map((r) => (
                  <button key={r.key} type="button" aria-pressed={tuning.dustReading === r.key} title={r.what} onClick={() => setComponent({ dustReading: r.key })}>
                    {r.label}
                  </button>
                ))}
              </div>
            )}
            <p className={styles.muted}>cold atomic gas: published per ring, with its layer height since D206 (the dust shares it) — not drawn yet</p>
          </div>
        )}

        {mode === "stars" && picked && (
          <div className={styles.section}>
            <div className={styles.zoomHead}>
              <span className={styles.label}>{picked.title}</span>
              <button type="button" className={styles.tuningDefault} title="Close" onClick={() => setPicked(null)}>
                close
              </button>
            </div>
            {picked.rows.map((r) => (
              <div key={r.label} className={styles.zoomHead}>
                <span className={styles.muted}>{r.label}</span>
                <span className={styles.value}>{r.value}</span>
              </div>
            ))}
            <p className={styles.muted}>The model's published numbers for this object.</p>
          </div>
        )}

        {/* The star-first mode's points are light on the field's scale; painting stars by a column is the field mode's. */}
        {mode === "field" && (
          <div className={styles.section}>
            <div className={styles.label}>Field painting the stars</div>
            <div className={styles.chips}>
              {paintable.map((f) => (
                <button
                  key={f}
                  aria-pressed={f === field}
                  onClick={() => onField(f)}
                  title={f === PHOTOMETRIC ? "Published luminosity and blackbody colour, summed as light" : meta.fields.find((d) => d.name === f)?.label}
                >
                  {SHORT[f] ?? f}
                </button>
              ))}
            </div>
          </div>
        )}

        {mode === "field" && decl && <FieldLegend decl={decl} values={shown.columns[field]} cmaps={meta.cmaps} />}
        <div className={styles.section}>
          <Exposure stops={exposure} onChange={onExposure} />
          <p className={styles.muted}>
            {mode === "field"
              ? `The field under the stars is always light, seen through the ${FILTER_SETS[filterSet].label} filters: the model integrates its stars, bulge, Hα and the dust's scattered and thermal light through each filter, and the dust dims each filter by its own depth along each line of sight. Exposure scales it, and the stars too when they are painted as light - through the same filters, each star's light as a blackbody of its temperature, so a hot star is dimmer here than its bolometric light.`
              : `One exposure for the field and the points, seen through the ${FILTER_SETS[filterSet].label} filters. A point is its own published light on the field's scale: its sprite sums to that light over the sky one pixel covers at the point. So at the whole galaxy a single star is lost in the glow and the clusters stand out, and the stars emerge as the view closes in; raise the exposure, or switch the starlight off, to see them alone.`}
          </p>
        </div>

        <div className={styles.section}>
          <div className={styles.label}>Projection</div>
          <div className={styles.pair}>
            {(["face-on", "edge-on", "oblique"] as Preset[]).map((p) => (
              <button key={p} aria-pressed={p === preset} onClick={() => onPreset(p)}>
                {p}
              </button>
            ))}
          </div>
        </div>

        <div className={styles.section}>
          <div className={styles.zoomHead}>
            <span className={styles.label}>Zoom</span>
            <span className={styles.value}>{view ? `${formatNumber(view.across, 3)} kpc across` : "—"}</span>
          </div>
          <input
            type="range"
            className={styles.slider}
            min={0}
            max={1000}
            value={Math.round((view?.zoom ?? 0) * 1000)}
            aria-label="Zoom"
            onChange={(e) => setZoom(Number(e.target.value) / 1000)}
          />
          {mode === "field" && (
            <div className={styles.pair}>
              {REGIMES.map((r) => (
                <button
                  key={r.key}
                  aria-pressed={r.key === weights.active}
                  title={`${r.name}: ${r.what}`}
                  onClick={() => view && setZoom(zoomForWidth(view, REGIME_VIEW_KPC[r.key]))}
                >
                  {r.label}
                </button>
              ))}
            </div>
          )}
        </div>

        <TuningPanel tuning={tuning} onChange={setTuning} stats={marchStats} />
      </div>

      <div className={styles.regime}>
        <div className={styles.regimeHead}>
          <span className={styles.muted}>{mode === "field" ? `regime ${REGIMES.indexOf(regime) + 1} of 3` : "mode 2 of 2"}</span>
          <span className={styles.regimeName}>{mode === "field" ? regime.name : "Star-first"}</span>
          <span className={styles.dot} />
        </div>
        <p className={styles.regimeWhat}>
          {mode === "stars"
            ? seen === null
              ? "Nothing of the galaxy is in view."
              : !tuning.compPoints
                ? `${current.what} The stars are switched off: the starlight volume is the whole of the stars' light.`
                : !bright
                  ? `${current.what} Finding the ${brightestN.toLocaleString("en")} brightest.`
                  : `${current.what} ${bright.header.count.returned.toLocaleString("en")} stars: every disc star in view above ${formatNumber(bright.header.threshold.l_min, 3)} L☉${
                      clusterCensus ? `, and ${(clusterCensus.columns.cluster_radius?.length ?? 0).toLocaleString("en")} clusters` : ""
                    }. The field under them is the light no point carries. Click a point for its numbers.`
            : `${regime.what} ${
                weights.active === "stars"
                  ? region.busy || !detail
                    ? "Loading this region's stars."
                    : `${detail.header.stars.materialised.toLocaleString("en")} stars here, of a ${regionStars.toLocaleString("en")}-star galaxy.`
                  : weights.active === "sampled"
                    ? `${sample.header.stars.materialised.toLocaleString("en")} stars.`
                    : "Zoom in for stars."
              }`}
        </p>
        {diagnostic && <p className={styles.muted}>diagnostic: shows where it is, not how it looks</p>}
        {mode === "stars" && marchOn && tuning.compDust && tuning.dustReading === "where" && (
          <p className={styles.muted}>
            {ramp
              ? `dust: ${ramp.field}'s declared ramp${ramp.coloured ? "" : " (grey)"}, ${ramp.scale}${
                  ramp.inferred ? " [inferred: log display scale]" : ""
                }, τ ${dustPaint === null ? "…" : `${formatNumber(dustPaint.lo, 2)} … ${formatNumber(dustPaint.hi, 2)}`} (the top drawn at ${WHERE_LEVEL} face-on: a display normalisation)`
              : "dust: no dust field is declared with a ramp, so its depth is not drawn"}
          </p>
        )}
      </div>

      {bar && (
        <div className={styles.scale}>
          <div className={styles.scaleBar} style={{ width: bar.px }} />
          <div className={styles.muted}>{formatNumber(bar.kpc, 2)} kpc</div>
        </div>
      )}
    </>
  );
}
