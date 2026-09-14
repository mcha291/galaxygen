import { codes } from "@interface/transport.js";
import { useMemo, useState } from "react";

import { type FieldDecl, type FieldsPayload, type Frame, HISTORY_SAMPLING, type Query, loadArrays } from "../api";
import { DiscLayer } from "../galaxy/DiscLayer";
import { ShearSpokes } from "../galaxy/ShearSpokes";
import { periodMyr } from "../galaxy/shear";
import { GalaxyView, type Preset } from "../galaxy/GalaxyView";
import { useLoad } from "../useLoad";
import { type MergerEvent, formatNumber } from "../workflow/logic";
import { centres } from "./axes";
import { FieldSurface, surfaceHeightAt } from "./FieldSurface";
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
// The shearing spokes over checkpoints 1 and 2 (galaxy/ShearSpokes.tsx). Off for now.
const SHEAR_SPOKES = false;

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
  // Before then the field has no φ dependence at all, so a swept disc is a 1D
  // function drawn as a 2D picture: half the pixels carry nothing, and the half
  // that does not is the half that makes it look like a galaxy. Those checkpoints
  // get a surface plot instead — axes, grid and contour rings, unmistakably a
  // chart rather than a scene. Checkpoint 4 is where φ enters the model, and it
  // keeps the disc.
  const asSurface = !contrast;
  // Checkpoints 1 and 2 can shear spokes with the rotation curve; when on, the curve is always fetched there.
  const curve = SHEAR_SPOKES && n <= 2 ? declOf(meta, "circular_velocity") : undefined;
  const names = [
    ...new Set([...(disc ? [disc.name] : []), ...(contrast ? [contrast.name] : []), ...(curve ? [curve.name] : []), ...insetDecls.map((d) => d.name)]),
  ];
  const [playing, setPlaying] = useState(true);
  const [speed, setSpeed] = useState(50);
  const [resetKey, setResetKey] = useState(0);
  const [tMyr, setTMyr] = useState(0);
  const key = names.length ? JSON.stringify([names, query]) : null;
  const loaded = useLoad<Frame>(key, (signal) => loadArrays(names, query, signal));
  const frame = loaded.value && names.every((x) => x in loaded.value!.arrays) ? loaded.value : null;
  const R = frame?.header.grid.axes.R;
  const insetAxis = insetDecls.length ? (insetDecls[0].axes as string[])[0] : null;
  const radii = useMemo(() => (R ? centres(R) : null), [R]);
  const v = curve && frame ? (frame.arrays[curve.name] as Float64Array) : null;
  const profile = disc && frame ? (frame.arrays[disc.name] as Float64Array) : null;
  // The spokes lie on the surface rather than cutting through it.
  const heightAt = useMemo(() => (asSurface && profile && R ? surfaceHeightAt(profile, R) ?? undefined : undefined), [asSurface, profile, R]);
  const markers = useMemo(() => mergersOf(query).map((m) => ({ at: m.time, label: `${formatNumber(m.time)} Gyr` })), [query]);

  return (
    <>
      <GalaxyView preset={preset} reach={R ? R.hi : 30}>
        {frame && disc && profile && R && asSurface && <FieldSurface decl={disc} profile={profile} R={R} cmaps={meta.cmaps} />}
        {frame && disc && profile && R && !asSurface && (
          <DiscLayer
            decl={disc}
            profile={profile}
            R={R}
            cmaps={meta.cmaps}
            contrast={contrast ? (frame.arrays[contrast.name] as Float64Array) : undefined}
            phi={contrast ? frame.header.grid.axes.phi : undefined}
            size={768}
          />
        )}
        {radii && v && R && (
          <ShearSpokes
            R={radii}
            v={v}
            rMax={R.hi * 0.8}
            playing={playing}
            speed={speed}
            resetKey={resetKey}
            onTime={setTMyr}
            heightAt={heightAt}
          />
        )}
      </GalaxyView>
      {radii && v && (
        <div className={styles.spokes}>
          <button type="button" onClick={() => setPlaying((p) => !p)} aria-pressed={playing}>
            {playing ? "pause" : "play"}
          </button>
          <button type="button" onClick={() => setResetKey((k) => k + 1)}>reset</button>
          <label>
            <span>speed</span>
            <select value={speed} onChange={(e) => setSpeed(Number(e.target.value))}>
              {[10, 50, 200, 1000].map((s) => (
                <option key={s} value={s}>
                  {s} Myr/s
                </option>
              ))}
            </select>
          </label>
          <span className={styles.spokeTime}>t = {formatNumber(tMyr, 3)} Myr</span>
          <span className={styles.spokeNote}>
            spokes orbit at v_c(R)/R · one orbit at R₀ = {formatNumber(periodMyr(8.2, radii, v), 3)} Myr · circular orbits only
          </span>
        </div>
      )}
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
          {asSurface ? "surface: height and colour by" : "disc painted by"} {disc.name}
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
