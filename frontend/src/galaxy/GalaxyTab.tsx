import { useState } from "react";

import type { FieldsPayload, Sample } from "../api";
import { formatNumber } from "../workflow/logic";
import { PHOTOMETRIC } from "./colors";
import { Exposure } from "./Exposure";
import { FieldLegend } from "./FieldLegend";
import { GalaxyView, type Preset, type ViewState } from "./GalaxyView";
import { scaleBar } from "./zoom";
import styles from "./GalaxyTab.module.css";

interface Props {
  meta: FieldsPayload;
  sample: Sample;
  positions: Float32Array;
  colors: Float32Array;
  fields: string[];
  field: string;
  onField(name: string): void;
  exposure: number;
  onExposure(stops: number): void;
  preset: Preset;
  onPreset(p: Preset): void;
  onPick(row: number): void;
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

// The three regimes of the design brief. Only the sample is drawn today, so the
// other two are shown and disabled rather than hidden.
const REGIMES = [
  { key: "field", label: "field", ready: false },
  { key: "sampled", label: "sampled", ready: true },
  { key: "stars", label: "stars", ready: false },
];

/** The finished galaxy, laid out as the design's Galaxy tab: controls floating left, regime top right, scale bottom left. */
export function GalaxyTab({ meta, sample, positions, colors, fields, field, onField, exposure, onExposure, preset, onPreset, onPick }: Props) {
  const [zoom, setZoom] = useState<number | undefined>(undefined);
  const [view, setView] = useState<ViewState | null>(null);
  const decl = meta.fields.find((f) => f.name === field);
  const bar = view ? scaleBar(view.pxPerKpc) : null;

  return (
    <>
      <GalaxyView positions={positions} colors={colors} preset={preset} onPick={onPick} zoom={zoom} onView={setView} photometric={field === PHOTOMETRIC} />

      <div className={styles.panel}>
        <div className={styles.section}>
          <div className={styles.label}>Field painting the disc</div>
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

        {decl && <FieldLegend decl={decl} values={sample.columns[field]} cmaps={meta.cmaps} />}
        {field === PHOTOMETRIC && (
          <div className={styles.section}>
            <Exposure stops={exposure} onChange={onExposure} />
            <p className={styles.muted}>
              Each star&apos;s published luminosity in its blackbody colour, added as light and tone-mapped. The sample is
              {` ${sample.header.stars.materialised.toLocaleString("en")}`} stars, so this is the resolved half only: the smooth
              unresolved light (RENDER_PLAN R3) is not drawn yet.
            </p>
          </div>
        )}

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
              <button key={r.key} aria-pressed={r.key === "sampled"} disabled={!r.ready} title={r.ready ? undefined : "Not drawn yet"}>
                {r.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className={styles.regime}>
        <div className={styles.regimeHead}>
          <span className={styles.muted}>regime 2 of 3</span>
          <span className={styles.regimeName}>Sampled points</span>
          <span className={styles.dot} />
        </div>
        <p className={styles.regimeWhat}>
          {sample.header.stars.materialised.toLocaleString("en")} materialised stars. Click one to open its system.
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
