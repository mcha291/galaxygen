import { paintOf } from "@interface/ramp.js";
import { codes } from "@interface/transport.js";
import { useEffect, useMemo, useRef, useState } from "react";
import { Color } from "three";

import { type FieldDecl, type FieldsPayload, type Frame, HISTORY_SAMPLING, type Query, loadArrays } from "../api";
import { DiscLayer } from "../galaxy/DiscLayer";
import { FieldVolume } from "../galaxy/FieldVolume";
import { Isophotes } from "../galaxy/Isophotes";
import { Tracers } from "../galaxy/Tracers";
import { interp, periodMyr } from "../galaxy/shear";
import { GalaxyView, type Preset } from "../galaxy/GalaxyView";
import { useLoad } from "../useLoad";
import { type MergerEvent, formatNumber } from "../workflow/logic";
import { centres } from "./axes";
import { LinePlot } from "./LinePlot";
import {
  arrivalsPerCell,
  arrivedSpread,
  deliveredBy,
  envelopeProfile,
  heightReached,
  kicksSquared,
  radialTransport,
  ringLevels,
  ringRadius,
  towerY,
  valueAt,
  wallProfile,
} from "./mergers";
import { Envelope } from "./Envelope";
import { TimeTower } from "./TimeTower";
import styles from "./CheckpointScene.module.css";

interface Props {
  n: number;
  meta: FieldsPayload;
  query: Query;
  preset: Preset;
  /** Exposure in stops for the field at checkpoints 5 and 6. */
  exposure: number;
  /** Show the inset chart at checkpoint 1 (the rotation curve). Off by default. */
  charts?: boolean;
}

// What each checkpoint's scene draws, by field name. Every name is checked
// against the declarations at run time; a model that lacks one shows the gap.
// Checkpoint 3 is the pattern since S25 (D174): the bar and arms drawn on checkpoint 1's smooth disc,
// because no star has formed yet; checkpoint 4's stars then carry the same pattern.
const DISC_AT: Record<number, string> = { 1: "disc_surface_density", 3: "disc_surface_density", 4: "stellar_surface_density" };
const INSET_AT: Record<number, { title: string; fields: string[] }> = {
  1: { title: "Rotation curve", fields: ["circular_velocity", "halo_circular_velocity", "disc_circular_velocity"] },
};
// Checkpoint 2's playback: the probe disc and the three responses it reads over time.
const PLAYBACK_FIELDS = [
  "disc_surface_density",
  "disc_radial_spread",
  "merger_delivery",
  "disc_heating",
  "halo_potential",
  "halo_potential_midplane",
];
type MergerView = "envelope" | "tower";
const PLAYBACK_SPEEDS = [0.5, 1, 2, 4]; // Gyr per second of wall time
const R_SUN_KPC = 8.2; // where the scatter gauge and the orbit note read
// stars_formed_history is kept out of the scrubber on purpose: it is published at
// the radii those stars occupy *today*, so a slice at an epoch would place past
// stars where they have not yet migrated to (RENDER_PLAN Part 1b, the trap).
const NOT_AN_EPOCH = new Set(["stars_formed_history"]);

/** The preview for one checkpoint: only what that checkpoint has computed, never the finished galaxy. */
export function CheckpointScene({ n, meta, query, preset, exposure, charts = false }: Props) {
  // From Systems on the galaxy is whole, and its preview is the field regime only: the light
  // integrated through the published fields. Stars, and the systems they open, are the Galaxy tab's.
  if (n >= 5) {
    return (
      <GalaxyView reach={20} preset={preset} hdr>
        <FieldVolume meta={meta} query={query} stops={exposure} />
      </GalaxyView>
    );
  }
  if (n === 2) return <MergerScene meta={meta} query={query} preset={preset} />;
  if (n === 4) return <HistoryScene meta={meta} query={query} preset={preset} />;
  return <DiscScene n={n} meta={meta} query={query} preset={preset} charts={charts} />;
}

function declOf(meta: FieldsPayload, name: string): FieldDecl | undefined {
  return meta.fields.find((f) => f.name === name);
}

/** A share as a percentage; the far tail of a Gaussian delivery window reads as none rather than 10⁻¹²%. */
function formatPercent(share: number): string {
  const pct = 100 * share;
  return pct < 0.01 ? "0" : formatNumber(pct, 3);
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
  // From checkpoint 3 (the pattern, since S25) the disc carries the bar and arms, when the model publishes them.
  const contrast = n >= 3 ? declOf(meta, "pattern_density_contrast") : undefined;
  // Checkpoint 1's tracers orbit on the rotation curve, so the curve is always fetched there.
  const curve = n === 1 ? declOf(meta, "circular_velocity") : undefined;
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
  // Isophotes at fixed decades of Σ, at checkpoint 1 only: later discs carry the pattern.
  const rings = useMemo(
    () =>
      n === 1 && profile && radii
        ? ringLevels(profile, 5)
            .map((level) => ringRadius(profile, radii, level))
            .filter((r): r is number => r !== null)
        : [],
    [n, profile, radii],
  );
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
        {R && rings.length > 0 && <Isophotes rings={rings} lift={R.hi / 400} />}
        {radii && v && R && rings.length > 0 && (
          <Tracers R={radii} v={v} rings={rings} playing={playing} speed={speed} resetKey={resetKey} onTime={setTMyr} lift={R.hi / 300} />
        )}
      </GalaxyView>
      {radii && v && (
        <div className={styles.orbits}>
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
          <span className={styles.orbitTime}>t = {formatNumber(tMyr, 3)} Myr</span>
          <span className={styles.orbitNote}>
            isophotes at fixed decades of Σ · tracers on circular orbits at v_c(R)/R · one orbit at R₀ ={" "}
            {formatNumber(periodMyr(R_SUN_KPC, radii, v), 3)} Myr
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
          disc painted by {disc.name}
          {contrast ? ` × ${contrast.name}` : ""} · {String(disc.ramp?.cmap ?? "")} · {String(disc.ramp?.scale ?? "")}
        </p>
      )}
    </>
  );
}

/**
 * Checkpoint 2 as a playback through cosmic time. There are no stars yet and no
 * matter history (checkpoint 4), so the disc is checkpoint 1's Σ(R) used as a
 * probe: at each τ it is moved through the radial scatter of the mergers landed
 * so far, by the model's own transport. The gauges read what the assembly stage
 * publishes at τ. Changing a merger changes when and how hard the disc smears.
 */
function MergerScene({ meta, query, preset }: { meta: FieldsPayload; query: Query; preset: Preset }) {
  const decls = PLAYBACK_FIELDS.map((name) => declOf(meta, name));
  const [disc, spreadDecl, deliveryDecl, heatingDecl, potentialDecl, midplaneDecl] = decls;
  const [view, setView] = useState<MergerView>("envelope");
  const names = decls.filter((d): d is FieldDecl => !!d).map((d) => d.name);
  const key = names.length === PLAYBACK_FIELDS.length ? JSON.stringify([names, query]) : null;
  const loaded = useLoad<Frame>(key, (signal) => loadArrays(names, query, signal, HISTORY_SAMPLING));
  const frame = loaded.value && names.every((x) => x in loaded.value!.arrays) ? loaded.value : null;
  const R = frame?.header.grid.axes.R;
  const t = frame?.header.grid.axes.t;
  const radii = useMemo(() => (R ? centres(R) : null), [R]);
  const mergers = useMemo(() => mergersOf(query).sort((a, b) => a.time - b.time), [query]);

  const [tau, setTau] = useState(0);
  const [playing, setPlaying] = useState(true);
  const [speed, setSpeed] = useState(1);
  const tauRef = useRef(0);
  const seek = (value: number) => {
    tauRef.current = value;
    setTau(value);
  };
  // A new history plays from the start.
  useEffect(() => {
    seek(t ? t.lo : 0);
    setPlaying(true);
  }, [key, t?.lo]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (!playing || !t) return;
    let last = performance.now();
    let id = 0;
    const step = (now: number) => {
      const next = tauRef.current + Math.min(0.1, (now - last) / 1000) * speed;
      last = now;
      if (next >= t.hi) {
        seek(t.hi);
        setPlaying(false);
        return;
      }
      seek(next);
      id = requestAnimationFrame(step);
    };
    id = requestAnimationFrame(step);
    return () => cancelAnimationFrame(id);
  }, [playing, speed, t]);

  const arrived = mergers.filter((m) => m.time <= tau).length;
  const profile = frame && disc ? (frame.arrays[disc.name] as Float64Array) : null;
  const spread = frame && spreadDecl ? (frame.arrays[spreadDecl.name] as Float32Array) : null;
  const delivery = frame && deliveryDecl ? (frame.arrays[deliveryDecl.name] as Float32Array) : null;
  const heating = frame && heatingDecl ? (frame.arrays[heatingDecl.name] as Float32Array) : null;

  // The disc after 0, 1, … of the mergers have landed: the scatter only changes on
  // an arrival, so the transport runs once per merger, not per frame.
  const stages = useMemo(() => {
    if (!profile || !spread || !radii || !R || !t) return null;
    return Array.from({ length: mergers.length + 1 }, (_, k) => {
      const scatter = arrivedSpread(spread, R.n, t, k === 0 ? t.lo - 1 : mergers[k - 1].time + t.width / 2);
      return { scatter, moved: radialTransport(profile, radii, R.width, scatter) };
    });
  }, [profile, spread, radii, R, t, mergers]);
  const stage = stages ? stages[arrived] : null;

  // The tower: height is cosmic time. Each fixed-Σ ring is a wall that steps out where
  // a merger lands, coloured by the σ_z matter forming at that height carries today.
  const height = R ? R.hi * 0.9 : 1;
  const tower = useMemo(() => {
    if (!stages || !profile || !radii || !t || !heating || !heatingDecl) return null;
    const perCell = arrivalsPerCell(mergers.map((m) => m.time), t);
    const walls: Float64Array[] = [];
    for (const level of ringLevels(profile)) {
      const byStage = stages.map((st) => ringRadius(st.moved, radii, level));
      if (byStage.some((r) => r === null)) continue;
      walls.push(wallProfile(Array.from(perCell, (k) => byStage[k]!), t, height));
    }
    const ramp = paintOf(heatingDecl, meta.cmaps, heating);
    const colours = new Float32Array(t.n * 3);
    const c = new Color();
    for (let j = 0; j < t.n; j += 1) {
      const [r, g, b] = ramp.color(heating[j]);
      c.setRGB(r / 255, g / 255, b / 255).convertSRGBToLinear();
      colours.set([c.r, c.g, c.b], j * 3);
    }
    return { walls, colours };
  }, [stages, profile, radii, t, heating, heatingDecl, meta.cmaps, mergers, height]);

  // The envelope: how high matter moving up at σ_z climbs in the halo's potential, with
  // σ_z the birth dispersion (disc_heating for matter born today) plus the kicks of the
  // mergers landed so far, each read off the step it puts in disc_heating.
  const kicks = useMemo(() => (heating && t ? kicksSquared(heating, t, mergers.map((m) => m.time)) : null), [heating, t, mergers]);
  const sigma = heating && t && kicks ? Math.sqrt(heating[t.n - 1] ** 2 + kicks.slice(0, arrived).reduce((a, b) => a + b, 0)) : null;
  const envelope = useMemo(() => {
    const potential = frame && potentialDecl ? (frame.arrays[potentialDecl.name] as Float32Array) : null;
    const midplane = frame && midplaneDecl ? (frame.arrays[midplaneDecl.name] as Float32Array) : null;
    const z = frame?.header.grid.axes.z;
    if (!potential || !midplane || !z || !R || !radii || sigma === null || !heatingDecl || !heating) return null;
    const heights = heightReached(potential, midplane, z, R.n, sigma);
    return { profile: envelopeProfile(radii, heights, R.hi * 0.8), atSun: interp(R_SUN_KPC, radii, heights) };
  }, [frame, potentialDecl, midplaneDecl, R, radii, sigma, heatingDecl, heating]);
  // Chrome, not data: magma at a cold disc's σ_z is near black on the ground, so the
  // envelope takes the ink and σ_z is read off the gauge.
  const envelopeColour = useMemo(
    () => new Color(getComputedStyle(document.documentElement).getPropertyValue("--ink-1").trim() || "#e6ebf5"),
    [],
  );

  const landing = mergers.find((m) => tau >= m.time && tau - m.time < 0.5);
  const atEnd = t ? tau >= t.hi : false;

  return (
    <>
      <GalaxyView key={view} preset={preset} reach={R ? (view === "tower" ? R.hi * 1.6 : R.hi) : 30}>
        {disc && stage && profile && R && t && (
          <group position={[0, view === "tower" ? towerY(tau, t, height) : 0, 0]}>
            <DiscLayer decl={disc} profile={stage.moved} R={R} cmaps={meta.cmaps} rangeValues={profile} />
          </group>
        )}
        {view === "tower" && tower && t && <TimeTower walls={tower.walls} colours={tower.colours} now={towerY(tau, t, height)} />}
        {view === "envelope" && envelope && <Envelope profile={envelope.profile} colour={envelopeColour} />}
      </GalaxyView>

      {landing && (
        <p className={styles.arrival}>
          merger 1:{formatNumber(1 / landing.mass_ratio, 2)} landing at {landing.time} Gyr · gas fraction {landing.gas_fraction}
        </p>
      )}

      {disc && heatingDecl && view === "envelope" && (
        <p className={styles.layerNote}>
          envelope: the height matter moving up at σ_z reaches in the halo&apos;s potential alone, so too thick until the disc&apos;s own
          gravity arrives at checkpoint 4 · σ_z is the birth dispersion plus the kicks of the mergers landed so far · best edge-on
        </p>
      )}
      {disc && heatingDecl && view === "tower" && (
        <p className={styles.layerNote}>
          height is cosmic time, today at the top · walls: fixed Σ of checkpoint 1&apos;s {disc.name}, moved through the mergers&apos;
          radial scatter, coloured by {heatingDecl.name} · what these mergers do to a disc like this, not the disc as it was
        </p>
      )}

      <div className={styles.scrubber}>
        <div className={styles.chips} role="group" aria-label="View">
          {(["envelope", "tower"] as const).map((v) => (
            <button key={v} aria-pressed={view === v} onClick={() => setView(v)}>
              {v === "envelope" ? "heated envelope" : "history tower"}
            </button>
          ))}
        </div>
        <div className={styles.timeRow}>
          <div className={styles.playback}>
            <button
              type="button"
              aria-pressed={playing}
              disabled={!t}
              onClick={() => {
                if (atEnd && t) seek(t.lo);
                setPlaying((p) => !p || atEnd);
              }}
            >
              {playing ? "pause" : atEnd ? "replay" : "play"}
            </button>
            <select value={speed} onChange={(e) => setSpeed(Number(e.target.value))} aria-label="Playback speed">
              {PLAYBACK_SPEEDS.map((s) => (
                <option key={s} value={s}>
                  {s} Gyr/s
                </option>
              ))}
            </select>
          </div>
          <div className={styles.track}>
            <input
              type="range"
              min={t?.lo ?? 0}
              max={t?.hi ?? 1}
              step={t ? t.width / 4 : 0.01}
              value={tau}
              disabled={!t}
              aria-label="Cosmic time"
              onChange={(e) => {
                setPlaying(false);
                seek(Number(e.target.value));
              }}
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
          <span className={styles.timeValue}>{t ? `${formatNumber(tau, 3)} ${t.unit_display}` : "—"}</span>
        </div>

        {t && radii && stage && delivery && heating ? (
          <dl className={styles.gauges}>
            <div>
              <dt>gas delivered by mergers</dt>
              <dd>
                {formatPercent(deliveredBy(delivery, t, tau))}% <small>of {formatPercent(deliveredBy(delivery, t, t.hi))}%</small>
              </dd>
            </div>
            {view === "envelope" && sigma !== null && envelope ? (
              <>
                <div>
                  <dt>σ_z, birth + kicks so far</dt>
                  <dd>
                    {formatNumber(sigma, 3)} <small>km/s</small>
                  </dd>
                </div>
                <div>
                  <dt>envelope height at R₀</dt>
                  <dd>
                    {formatNumber(envelope.atSun, 3)} <small>kpc</small>
                  </dd>
                </div>
              </>
            ) : (
              <div>
                <dt>σ_z today, matter forming now</dt>
                <dd>
                  {formatNumber(valueAt(heating, tau, t), 3)} <small>km/s</small>
                </dd>
              </div>
            )}
            <div>
              <dt>radial scatter so far at R₀</dt>
              <dd>
                {formatNumber(interp(R_SUN_KPC, radii, stage.scatter), 3)} <small>kpc</small>
              </dd>
            </div>
          </dl>
        ) : null}

        <div className={styles.scrubNote}>
          {loaded.busy || !frame
            ? `Loading the merger history: ${HISTORY_SAMPLING.tSamples} time steps.`
            : `${mergers.length} merger${mergers.length === 1 ? "" : "s"} marked · only major mergers scatter and heat`}
        </div>
      </div>
      {loaded.error && <p className={styles.fault}>Merger history failed: {loaded.error}</p>}
    </>
  );
}

/**
 * Checkpoint 4 (star formation; 3 until S25) is the formation history (RENDER_PLAN H1): every
 * (R, t) field the checkpoint publishes can be scrubbed through time, the disc swept from the
 * slice at the chosen epoch, merger arrivals marked on the slider.
 */
function HistoryScene({ meta, query, preset }: { meta: FieldsPayload; query: Query; preset: Preset }) {
  const histories = meta.fields.filter(
    (f) => (f.checkpoint as number) === 4 && (f.axes as string[])?.join() === "R,t" && !NOT_AN_EPOCH.has(f.name),
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
