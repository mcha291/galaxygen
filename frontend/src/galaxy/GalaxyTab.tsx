import { identify } from "@interface/stars.js";
import { useMemo, useState } from "react";

import { type FieldsPayload, type Query, type Sample, type StarName, STAR_SAMPLE, loadBrightest, loadRegion } from "../api";
import { useLoad } from "../useLoad";
import { formatNumber } from "../workflow/logic";
import { PHOTOMETRIC, exposureFor, photometricColors, starColors } from "./colors";
import { Exposure } from "./Exposure";
import { FieldLegend } from "./FieldLegend";
import { FieldVolume } from "./FieldVolume";
import { FILTER_SETS, FILTER_SET_NAMES, type FilterSetName } from "./filters";
import { footprint } from "./frustum";
import { GalaxyView, type Preset, type StarLayer, type ViewState } from "./GalaxyView";
import { extent, toScene } from "./positions";
import { REGIME_KPC, regimeWeights, regionAround, regionSampleSize, starsInWindow } from "./regimes";
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

function colorsFor(meta: FieldsPayload, sample: Sample, field: string, exposure: number): Float32Array | null {
  try {
    return field === PHOTOMETRIC ? photometricColors(meta, sample.columns, exposure) : starColors(meta, sample.columns, field);
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
export function GalaxyTab({ meta, sample, fields, field: chosen, onField, exposure, onExposure, query, preset, onPreset, onOpen }: Props) {
  const [zoom, setZoom] = useState<number | undefined>(undefined);
  const [view, setView] = useState<ViewState | null>(null);
  const [mode, setMode] = useState<Mode>("field");
  const [filterSet, setFilterSet] = useState<FilterSetName>("rgb");
  const [brightestSlider, setBrightestSlider] = useState(500);
  const brightestN = brightestOf(brightestSlider);
  // A column some models lack ([α/Fe] is the advanced chemistry's) offers no chip where the
  // sample has none, and a choice the current model cannot paint falls back to light.
  const paintable = fields.filter((f) => f === PHOTOMETRIC || f in sample.columns);
  const field = paintable.includes(chosen) ? chosen : PHOTOMETRIC;
  const decl = meta.fields.find((f) => f.name === field);
  const bar = view ? scaleBar(view.pxPerKpc) : null;
  const weights = regimeWeights(view?.across ?? REGIME_KPC.field * 2);
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

  const samplePositions = useMemo(() => positionsOf(sample), [sample]);
  const sampleColors = useMemo(() => colorsFor(meta, sample, field, exposure), [meta, sample, field, exposure]);
  const detailPositions = useMemo(() => (detail ? positionsOf(detail) : null), [detail]);
  const detailColors = useMemo(() => (detail ? colorsFor(meta, detail, field, exposure) : null), [meta, detail, field, exposure]);
  const brightPositions = useMemo(() => (bright ? positionsOf(bright) : null), [bright]);
  // A selection is exposed to its own stars, as a photograph is (colors.ts); the slider's stops ride on top.
  const autoStops = useMemo(() => (bright ? exposureFor(bright.columns.star_luminosity) : 0), [bright]);
  const brightColors = useMemo(() => (bright ? colorsFor(meta, bright, field, exposure + autoStops) : null), [meta, bright, field, exposure, autoStops]);
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
  } else if (bright && brightPositions && brightColors) {
    layers.push({ positions: brightPositions, colors: brightColors, onPick: (row) => openBright(bright, row) });
  }

  const shown = mode === "brightest" ? (bright ?? sample) : weights.active === "stars" && detail ? detail : sample;
  const current = MODES.find((m) => m.key === mode)!;

  return (
    <>
      <GalaxyView layers={layers} reach={reach} preset={preset} zoom={zoom} onView={setView} hdr additive={field === PHOTOMETRIC}>
        {mode === "field" && <FieldVolume meta={meta} query={query} stops={exposure} weight={weights.field} filterSet={filterSet} />}
      </GalaxyView>

      <div className={styles.panel}>
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
              ? `The field under the stars is always light, seen through the ${FILTER_SETS[filterSet].label} filters: the model integrates its stars, Hα and bulge through each filter, and the dust dims them along each line of sight. Exposure scales it, and the stars too when they are painted as light (always in broadband colour).`
              : `Stars only, brightest first by published luminosity: no field, no sample. Painted as light, the view is exposed to its hundredth-brightest star, the few above burning out${
                  bright && field === PHOTOMETRIC ? ` (${autoStops >= 0 ? "+" : ""}${autoStops.toFixed(1)} stops here)` : ""
                }, and the slider adds to that.`}
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
