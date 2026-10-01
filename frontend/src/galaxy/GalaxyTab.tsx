import { identify } from "@interface/stars.js";
import { useMemo, useRef, useState } from "react";

import {
  type BlackbodyTable,
  type Census,
  type FieldsPayload,
  type Query,
  type Sample,
  type StarName,
  STAR_SAMPLE,
  loadBlackbody,
  loadBrightest,
  loadClouds,
  loadClusters,
  loadRegion,
} from "../api";
import { CellOutlines, CloudMarkers } from "./ComponentLayers";
import { CLOUD_COLUMNS, type DustPaintShown, WHERE_LEVEL, brightestLayers, cloudColors, diagnosticOn, dustRamp, marchWanted, rowsInWindow } from "./components";
import { useLoad } from "../useLoad";
import { formatNumber } from "../workflow/logic";
import { PHOTOMETRIC, exposureFor, lightColors, photometricColors, starColors } from "./colors";
import { Exposure } from "./Exposure";
import { FieldLegend } from "./FieldLegend";
import { FieldVolume, type MarchStats } from "./FieldVolume";
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
  /** A star was clicked: open its system. */
  onOpen(star: StarName): void;
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
 * The brightest mode is a magnitude-limited catalogue of what the camera sees: the N most
 * luminous stars inside its frustum, from a pool materialised for the frustum's footprint.
 */
type Mode = "field" | "brightest";
const MODES: { key: Mode; label: string; what: string }[] = [
  { key: "field", label: "field", what: "The field, the sample and a region's stars, handed over by zoom." },
  { key: "brightest", label: "brightest", what: "The N most luminous stars inside the view, whatever the zoom." },
];
/**
 * The brightest mode's pool: about this many stars materialised for the footprint, so N reaches
 * a stated way into the luminosity function (N over the pool), at about a second a request.
 */
const POOL_TARGET_STARS = 200_000;
const POOL_MAX_STARS = 2_000_000;
/**
 * How long the view must hold still before the brightest mode re-selects. Shorter than a slider's
 * settle: the server keeps the pool's cells, so a re-selection inside the same pool is tens of
 * milliseconds, and the stars shown lag the camera by little more than this.
 */
const BRIGHTEST_SETTLE_MS = 120;
/** The N slider's range, decades: 10² to 10⁵ stars, logarithmic. */
const BRIGHTEST_DECADES = { lo: 2, hi: 5 };
/** The brightest mode's component switches (D205), each a tuning value, all off by default. */
const COMPONENT_SWITCHES: { key: "compStars" | "compGas" | "compDust" | "compClouds" | "compCells"; label: string; what: string }[] = [
  { key: "compStars", label: "starlight", what: "The field's stellar layer and the bulge, as the volume the model publishes light for, cell by cell" },
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
 * Any star drawn can be clicked to open its system.
 */
export function GalaxyTab({ meta, sample, fields, field: chosen, onField, exposure, onExposure, query, preset, onPreset, onOpen, onEdit }: Props) {
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

  // The brightest mode: the frustum's footprint, a pool sized to it, and the top N inside the frustum.
  const rMax = meta.grid.axes.R?.hi ?? DISC_RADIUS * 1.5;
  const seen = mode === "brightest" && view ? footprint(view.camera.viewProjection, rMax) : null;
  const inFootprint = useMemo(() => {
    if (!seen) return 0;
    const c = sample.columns as Record<string, ArrayLike<number>>;
    return starsInWindow(c.star_radius, c.star_azimuth, seen);
  }, [sample, seen?.r_min, seen?.r_max, seen?.phi_min, seen?.phi_max]); // eslint-disable-line react-hooks/exhaustive-deps
  const poolStars = seen ? regionSampleSize(STAR_SAMPLE, inFootprint, POOL_TARGET_STARS, POOL_MAX_STARS) : 0;
  const brightestKey = seen && view ? JSON.stringify([seen, poolStars, brightestN, roundedView(view.camera.viewProjection), query]) : null;
  const brightest = useLoad<Sample>(
    brightestKey,
    (signal) => loadBrightest(seen!, poolStars, brightestN, view!.camera.viewProjection, query, signal),
    BRIGHTEST_SETTLE_MS,
  );
  const bright = mode === "brightest" && brightest.value ? brightest.value : null;

  // The brightest mode's component layers (D205): all off by default, so the mode draws as before.
  const R = meta.grid.axes.R;
  const marchOn = mode === "brightest" && marchWanted(tuning);
  const ramp = useMemo(() => dustRamp(meta), [meta]);
  const [dustPaint, setDustPaint] = useState<DustPaintShown | null>(null);
  const marchLayers = brightestLayers(tuning, ramp);
  const diagnostic = mode === "brightest" && diagnosticOn(tuning);
  // The whole disc's cloud census, loaded once per query (about 17 000 clouds) and cut to the footprint here.
  const cloudsKey = mode === "brightest" && tuning.compClouds ? JSON.stringify(["clouds", query]) : null;
  const wholeDisc = { r_min: R?.lo ?? 0, r_max: rMax, phi_min: 0, phi_max: 2 * Math.PI, level: 0 };
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
  const brightPositions = useMemo(() => (bright ? positionsOf(bright) : null), [bright]);
  // A selection is exposed to its own stars, as a photograph is (colors.ts); the slider's stops ride on top.
  const autoStops = useMemo(() => (bright ? exposureFor(bright.columns.star_luminosity) : 0), [bright]);
  const brightColors = useMemo(
    () => (bright ? colorsFor(meta, bright, field, exposure + autoStops, blackbodyTable, pointGain) : null),
    [meta, bright, field, exposure, autoStops, blackbodyTable, pointGain],
  );
  // The framing radius comes from the sample in both modes, so the zoom slider means the same thing in each.
  const reach = useMemo(() => extent(samplePositions) || DISC_RADIUS, [samplePositions]);

  const open = (from: Sample, row: number) => {
    const name = identify(from.header, row) as { cell: number; index: number } | null;
    if (name) onOpen({ ...name, stars: from.header.stars.requested });
  };
  // A brightest row is a selection, named by its own columns rather than the runs.
  const openBright = (from: Sample, row: number) => {
    const c = from.columns as Record<string, ArrayLike<number | bigint>>;
    onOpen({ cell: Number(c.cell[row]), index: Number(c.index[row]), stars: from.header.stars.requested });
  };

  const layers: StarLayer[] = [];
  if (mode === "field") {
    if (sampleColors) layers.push({ positions: samplePositions, colors: sampleColors, opacity: weights.sampled, onPick: (row) => open(sample, row) });
    if (detail && detailPositions && detailColors && weights.stars > 0) {
      layers.push({ positions: detailPositions, colors: detailColors, opacity: weights.stars, onPick: (row) => open(detail, row) });
    }
    // Clusters as objects (V4, S41): each a point of the light its stars sum to, in the region regime.
    if (clusterPositions && clusterColors && weights.stars > 0 && field === PHOTOMETRIC) {
      layers.push({ positions: clusterPositions, colors: clusterColors, opacity: weights.stars });
    }
  } else if (bright && brightPositions && brightColors) {
    layers.push({ positions: brightPositions, colors: brightColors, onPick: (row) => openBright(bright, row) });
  }

  const shown = mode === "brightest" ? (bright ?? sample) : weights.active === "stars" && detail ? detail : sample;
  const current = MODES.find((m) => m.key === mode)!;

  return (
    <>
      <GalaxyView layers={layers} reach={reach} preset={preset} zoom={zoom} onView={setView} hdr additive={field === PHOTOMETRIC} psf={spritePsf} tuning={tuning}>
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
        {/* The brightest mode's components (D205): the march with only the switched layers, at the slider's own
            stops (not the stars' auto-exposure, so the volumes hold still as N changes) and the whole field weight. */}
        {marchOn && (
          <FieldVolume meta={meta} query={query} stops={exposure} weight={1} filterSet={filterSet} tuning={fieldTuning} stats={marchStats} layers={marchLayers} onDepth={setDustPaint} />
        )}
        {mode === "brightest" && tuning.compCells && R && <CellOutlines lo={R.lo} hi={R.hi} />}
        {mode === "brightest" && tuning.compClouds && cloudLayer && cloudLayer.sizes.length > 0 && (
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
              <button key={m.key} aria-pressed={m.key === mode} title={m.what} onClick={() => setMode(m.key)}>
                {m.label}
              </button>
            ))}
          </div>
          {mode === "field" && (
            <>
              <div className={styles.label}>Filters</div>
              <div className={styles.pair}>
                {FILTER_SET_NAMES.map((name) => (
                  <button key={name} aria-pressed={name === filterSet} title={FILTER_SETS[name].about} onClick={() => setFilterSet(name)}>
                    {FILTER_SETS[name].label}
                  </button>
                ))}
              </div>
            </>
          )}
          {mode === "brightest" && (
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

        {mode === "brightest" && (
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
            <p className={styles.muted}>cold atomic gas: published per ring, no layer height — not drawn</p>
          </div>
        )}

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

        {decl && <FieldLegend decl={decl} values={shown.columns[field]} cmaps={meta.cmaps} />}
        <div className={styles.section}>
          <Exposure stops={exposure} onChange={onExposure} />
          <p className={styles.muted}>
            {mode === "field"
              ? `The field under the stars is always light, seen through the ${FILTER_SETS[filterSet].label} filters: the model integrates its stars, bulge, Hα and the dust's scattered and thermal light through each filter, and the dust dims each filter by its own depth along each line of sight. Exposure scales it, and the stars too when they are painted as light - through the same filters, each star's light as a blackbody of its temperature, so a hot star is dimmer here than its bolometric light.`
              : `Stars only, brightest first by published luminosity: no field, no sample. Painted as light, the view is exposed to its hundredth-brightest star, the few above burning out${
                  bright && field === PHOTOMETRIC ? ` (${autoStops >= 0 ? "+" : ""}${autoStops.toFixed(1)} stops here)` : ""
                }, and the slider adds to that.${
                  marchOn ? " The component volumes take the slider's stops alone, not the stars' own exposure, so they hold still as N changes." : ""
                }`}
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
          <span className={styles.regimeName}>{mode === "field" ? regime.name : "Brightest in view"}</span>
          <span className={styles.dot} />
        </div>
        <p className={styles.regimeWhat}>
          {mode === "brightest"
            ? seen === null
              ? "Nothing of the galaxy is in view."
              : brightest.busy || !bright || !bright.header.brightest
                ? `${current.what} Finding the ${brightestN.toLocaleString("en")} brightest.`
                : `${current.what} ${bright.header.brightest.returned.toLocaleString("en")} of the ${bright.header.brightest.in_view.toLocaleString("en")} stars in view, from a pool of ${bright.header.brightest.pool.toLocaleString("en")} (a ${poolStars.toLocaleString("en")}-star galaxy). Click one to open its system.`
            : `${regime.what} ${
                weights.active === "stars"
                  ? region.busy || !detail
                    ? "Loading this region's stars."
                    : `${detail.header.stars.materialised.toLocaleString("en")} stars here, of a ${regionStars.toLocaleString("en")}-star galaxy. Click one to open its system.`
                  : weights.active === "sampled"
                    ? `${sample.header.stars.materialised.toLocaleString("en")} stars. Click one to open its system.`
                    : "Zoom in for stars."
              }`}
        </p>
        {diagnostic && <p className={styles.muted}>diagnostic: shows where it is, not how it looks</p>}
        {mode === "brightest" && marchOn && tuning.compDust && tuning.dustReading === "where" && (
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
