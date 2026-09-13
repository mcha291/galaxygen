import { codes } from "@interface/transport.js";
import { useMemo, useState } from "react";

import { type FieldDecl, type FieldsPayload, type Frame, HISTORY_SAMPLING, type Query, loadArrays } from "../api";
import { DiscLayer } from "../galaxy/DiscLayer";
import { GalaxyView, type Preset } from "../galaxy/GalaxyView";
import { useLoad } from "../useLoad";
import { type MergerEvent, formatNumber } from "../workflow/logic";
import { centres } from "./axes";
import { LinePlot } from "./LinePlot";
import styles from "./CheckpointScene.module.css";

interface Props {
  n: number;
  meta: FieldsPayload;
  query: Query;
  preset: Preset;
  /** Checkpoints 5 and 6 draw the star sample; the caller owns it because the Galaxy tab shares it. */
  stars: { positions: Float32Array; colors: Float32Array } | null;
  onPick(row: number): void;
  /** Show the inset chart at checkpoints 1 and 2 (the rotation curve, the merger history). Off by default. */
  charts?: boolean;
}

// What each checkpoint's scene draws, by field name. Every name is checked
// against the declarations at run time; a model that lacks one shows the gap.
const DISC_AT: Record<number, string> = { 1: "disc_surface_density", 2: "disc_surface_density", 4: "stellar_surface_density" };
const INSET_AT: Record<number, { title: string; fields: string[] }> = {
  1: { title: "Rotation curve", fields: ["circular_velocity", "halo_circular_velocity", "disc_circular_velocity"] },
  2: { title: "Merger history", fields: ["merger_delivery"] },
};
// stars_formed_history is kept out of the scrubber on purpose: it is published at
// the radii those stars occupy *today*, so a slice at an epoch would place past
// stars where they have not yet migrated to (RENDER_PLAN Part 1b, the trap).
const NOT_AN_EPOCH = new Set(["stars_formed_history"]);

/** The preview for one checkpoint: only what that checkpoint has computed, never the finished galaxy. */
export function CheckpointScene({ n, meta, query, preset, stars, onPick, charts = false }: Props) {
  if (n >= 5) {
    return <GalaxyView positions={stars?.positions} colors={stars?.colors} preset={preset} onPick={onPick} />;
  }
  if (n === 3) return <HistoryScene meta={meta} query={query} preset={preset} />;
  return <DiscScene n={n} meta={meta} query={query} preset={preset} charts={charts} />;
}

function declOf(meta: FieldsPayload, name: string): FieldDecl | undefined {
  return meta.fields.find((f) => f.name === name);
}

function mergersOf(query: Query): MergerEvent[] {
  try {
    return JSON.parse(String(query.mergers ?? "[]")) as MergerEvent[];
  } catch {
    return [];
  }
}

function DiscScene({ n, meta, query, preset, charts }: { n: number; meta: FieldsPayload; query: Query; preset: Preset; charts: boolean }) {
  const disc = declOf(meta, DISC_AT[n]);
  const inset = charts ? INSET_AT[n] : undefined; // hidden, so not fetched either, unless the bottom bar's toggle is on
  const insetDecls = (inset?.fields ?? []).map((f) => declOf(meta, f)).filter((d): d is FieldDecl => !!d);
  // From checkpoint 4 the disc carries the bar and arms, when the model publishes them.
  const contrast = n >= 4 ? declOf(meta, "pattern_density_contrast") : undefined;
  const names = [...(disc ? [disc.name] : []), ...(contrast ? [contrast.name] : []), ...insetDecls.map((d) => d.name)];
  const key = names.length ? JSON.stringify([names, query]) : null;
  const loaded = useLoad<Frame>(key, (signal) => loadArrays(names, query, signal));
  const frame = loaded.value && names.every((x) => x in loaded.value!.arrays) ? loaded.value : null;
  const R = frame?.header.grid.axes.R;
  const insetAxis = insetDecls.length ? (insetDecls[0].axes as string[])[0] : null;
  const markers = useMemo(() => mergersOf(query).map((m) => ({ at: m.time, label: `${formatNumber(m.time)} Gyr` })), [query]);

  return (
    <>
      <GalaxyView preset={preset} reach={R ? R.hi : 30}>
        {frame && disc && R && (
          <DiscLayer
            decl={disc}
            profile={frame.arrays[disc.name] as Float64Array}
            R={R}
            cmaps={meta.cmaps}
            contrast={contrast ? (frame.arrays[contrast.name] as Float64Array) : undefined}
            phi={contrast ? frame.header.grid.axes.phi : undefined}
            size={contrast ? 768 : 512}
          />
        )}
      </GalaxyView>
      {frame && inset && insetAxis && (
        <div className={styles.inset}>
          <LinePlot
            title={inset.title}
            unit={String(insetDecls[0].unit_display ?? insetDecls[0].unit)}
            x={{ values: centres(frame.header.grid.axes[insetAxis]), label: insetAxis, unit: frame.header.grid.axes[insetAxis].unit_display }}
            log={false}
            series={insetDecls.map((d) => ({ label: d.label, values: frame.arrays[d.name] as Float64Array }))}
            markers={insetAxis === "t" ? markers : []}
          />
        </div>
      )}
      {loaded.error && <p className={styles.fault}>Preview failed: {loaded.error}</p>}
      {disc && (
        <p className={styles.layerNote}>
          disc painted by {disc.name}
          {contrast ? ` × ${contrast.name}` : ""} · {String(disc.ramp?.cmap ?? "")} · {String(disc.ramp?.scale ?? "")}
        </p>
      )}
    </>
  );
}

/**
 * Checkpoint 3 is the formation history (RENDER_PLAN H1): every (R, t) field the
 * checkpoint publishes can be scrubbed through time, the disc swept from the slice
 * at the chosen epoch, merger arrivals marked on the slider.
 */
function HistoryScene({ meta, query, preset }: { meta: FieldsPayload; query: Query; preset: Preset }) {
  const histories = meta.fields.filter(
    (f) => (f.checkpoint as number) === 3 && (f.axes as string[])?.join() === "R,t" && !NOT_AN_EPOCH.has(f.name),
  );
  const [picked, setPicked] = useState<string>("sfr_surface_density_history");
  const decl = histories.find((h) => h.name === picked) ?? histories[0];
  const [epoch, setEpoch] = useState<number | null>(null);

  const key = decl ? JSON.stringify([decl.name, query]) : null;
  const loaded = useLoad<Frame>(key, (signal) => loadArrays([decl!.name], query, signal, HISTORY_SAMPLING));
  const frame = loaded.value && decl && decl.name in loaded.value.arrays ? loaded.value : null;
  const R = frame?.header.grid.axes.R;
  const t = frame?.header.grid.axes.t;

  const values = useMemo(() => {
    if (!frame || !decl) return null;
    const raw = frame.arrays[decl.name];
    return raw instanceof BigInt64Array ? (codes(raw) as Int32Array) : raw;
  }, [frame, decl]);

  const it = t ? Math.min(t.n - 1, Math.max(0, epoch ?? t.n - 1)) : 0;
  const profile = useMemo(() => {
    if (!values || !R || !t) return null;
    const out = new Float64Array(R.n);
    for (let i = 0; i < R.n; i += 1) out[i] = values[i * t.n + it];
    return out;
  }, [values, R, t, it]);

  const mergers = mergersOf(query);
  const time = t ? t.lo + (it + 0.5) * t.width : 0;

  return (
    <>
      <GalaxyView preset={preset} reach={R ? R.hi : 30}>
        {decl && profile && R && values && <DiscLayer decl={decl} profile={profile} R={R} cmaps={meta.cmaps} rangeValues={values} />}
      </GalaxyView>

      <div className={styles.scrubber}>
        <div className={styles.chips} role="group" aria-label="History">
          {histories.map((h) => (
            <button key={h.name} aria-pressed={h.name === decl?.name} onClick={() => setPicked(h.name)} title={String(h.about ?? "")}>
              {h.label}
            </button>
          ))}
        </div>
        <div className={styles.timeRow}>
          <span className={styles.timeLabel}>t</span>
          <div className={styles.track}>
            <input
              type="range"
              min={0}
              max={t ? t.n - 1 : 0}
              value={it}
              disabled={!t}
              aria-label="Cosmic time"
              onChange={(e) => setEpoch(Number(e.target.value))}
            />
            {t &&
              mergers.map((m, i) => (
                <span
                  key={i}
                  className={styles.merger}
                  style={{ left: `${((m.time - t.lo) / (t.hi - t.lo)) * 100}%` }}
                  title={`Merger at ${m.time} Gyr, mass ratio 1:${formatNumber(1 / m.mass_ratio, 2)}`}
                />
              ))}
          </div>
          <span className={styles.timeValue}>{t ? `${formatNumber(time, 3)} ${t.unit_display}` : "—"}</span>
        </div>
        <div className={styles.scrubNote}>
          {loaded.busy || !frame ? `Loading ${decl?.name ?? "history"}: ${HISTORY_SAMPLING.tSamples} time steps.` : `${decl?.name} at t = ${formatNumber(time, 4)} Gyr · merger arrivals marked`}
        </div>
      </div>
      {loaded.error && <p className={styles.fault}>History failed: {loaded.error}</p>}
    </>
  );
}
