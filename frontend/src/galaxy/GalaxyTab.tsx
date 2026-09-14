import { identify } from "@interface/stars.js";
import { useMemo, useState } from "react";

import { type FieldsPayload, type Query, type Sample, type StarName, STAR_SAMPLE, loadRegion } from "../api";
import { useLoad } from "../useLoad";
import { formatNumber } from "../workflow/logic";
import { PHOTOMETRIC, photometricColors, starColors } from "./colors";
import { Exposure } from "./Exposure";
import { FieldLegend } from "./FieldLegend";
import { FieldVolume } from "./FieldVolume";
import { GalaxyView, type Preset, type StarLayer, type ViewState } from "./GalaxyView";
import { toScene } from "./positions";
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
const __trace = (name: string) => { const w = window as unknown as { __tc?: Record<string, number> }; w.__tc ??= {}; w.__tc[name] = (w.__tc[name] ?? 0) + 1; if (w.__tc[name] % 50 === 1) console.log("TRACE", name, w.__tc[name]); }; // DEBUG
export function GalaxyTab({ meta, sample, fields, field, onField, exposure, onExposure, query, preset, onPreset, onOpen }: Props) {
  __trace("GalaxyTab"); // DEBUG
  const [zoom, setZoom] = useState<number | undefined>(undefined);
  const [view, setView] = useState<ViewState | null>(null);
  const decl = meta.fields.find((f) => f.name === field);
  const bar = view ? scaleBar(view.pxPerKpc) : null;
  const weights = regimeWeights(view?.across ?? REGIME_KPC.field * 2);
  const regime = REGIMES.find((r) => r.key === weights.active)!;

  // The stars regime: the window around where the view looks, at a sample size scaled to it.
  const area = view && weights.stars > 0 ? regionAround(view.target[0], view.target[2], view.across * 0.75) : null;
  const inWindow = useMemo(() => {
    if (!area) return 0;
    const c = sample.columns as Record<string, ArrayLike<number>>;
    return starsInWindow(c.star_radius, c.star_azimuth, area);
  }, [sample, area?.r_min, area?.r_max, area?.phi_min, area?.phi_max]); // eslint-disable-line react-hooks/exhaustive-deps
  const regionStars = area ? regionSampleSize(STAR_SAMPLE, inWindow, REGION_TARGET_STARS, REGION_MAX_STARS) : 0;
  const regionKey = area ? JSON.stringify([area, regionStars, query]) : null;
  const region = useLoad<Sample>(regionKey, (signal) => loadRegion(area!, regionStars, query, signal));
  const detail = region.value && regionKey ? region.value : null;

  const samplePositions = useMemo(() => positionsOf(sample), [sample]);
  const sampleColors = useMemo(() => colorsFor(meta, sample, field, exposure), [meta, sample, field, exposure]);
  const detailPositions = useMemo(() => (detail ? positionsOf(detail) : null), [detail]);
  const detailColors = useMemo(() => (detail ? colorsFor(meta, detail, field, exposure) : null), [meta, detail, field, exposure]);

  const open = (from: Sample, row: number) => {
    const name = identify(from.header, row) as { cell: number; index: number } | null;
    if (name) onOpen({ ...name, stars: from.header.stars.requested });
  };

  const layers: StarLayer[] = [];
  if (sampleColors) layers.push({ positions: samplePositions, colors: sampleColors, opacity: weights.sampled, onPick: (row) => open(sample, row) });
  if (detail && detailPositions && detailColors && weights.stars > 0) {
    layers.push({ positions: detailPositions, colors: detailColors, opacity: weights.stars, onPick: (row) => open(detail, row) });
  }

  const shown = weights.active === "stars" && detail ? detail : sample;

  return (
    <>
      <GalaxyView layers={layers} reach={DISC_RADIUS} preset={preset} zoom={zoom} onView={setView} hdr additive={field === PHOTOMETRIC}>
        <FieldVolume meta={meta} query={query} stops={exposure} weight={weights.field} />
      </GalaxyView>

      <div className={styles.panel}>
        <div className={styles.section}>
          <div className={styles.label}>Field painting the stars</div>
          <div className={styles.chips}>
            {fields.map((f) => (
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
            The field under the stars is always light: the published surface brightness, colour, Hα, bulge and dust, integrated
            along each line of sight. Exposure scales it, and the stars too when they are painted as light.
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
        </div>
      </div>

      <div className={styles.regime}>
        <div className={styles.regimeHead}>
          <span className={styles.muted}>regime {REGIMES.indexOf(regime) + 1} of 3</span>
          <span className={styles.regimeName}>{regime.name}</span>
          <span className={styles.dot} />
        </div>
        <p className={styles.regimeWhat}>
          {regime.what}{" "}
          {weights.active === "stars"
            ? region.busy || !detail
              ? "Loading this region's stars."
              : `${detail.header.stars.materialised.toLocaleString("en")} stars here, of a ${regionStars.toLocaleString("en")}-star galaxy. Click one to open its system.`
            : weights.active === "sampled"
              ? `${sample.header.stars.materialised.toLocaleString("en")} stars. Click one to open its system.`
              : "Zoom in for stars."}
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
