import { useMemo, useState } from "react";

import { type FieldDecl, type FieldsPayload, type Frame, type Query, loadArrays } from "../api";
import { useLoad } from "../useLoad";
import { type MergerEvent, formatNumber } from "../workflow/logic";
import { centres } from "./axes";
import { Heatmap } from "./Heatmap";
import { LinePlot } from "./LinePlot";
import { type Panels, wantedAt } from "./panels";
import styles from "./Preview.module.css";

interface Props {
  checkpoint: { n: number; name: string };
  panels: Panels;
  query: Query;
  cmaps: FieldsPayload["cmaps"];
}

/**
 * One checkpoint's preview: its profiles as plots and its scalars as a readout,
 * computed only as far as that checkpoint (the arrays route runs the stages the
 * fields need, and no further).
 */
export function Preview({ checkpoint, panels, query, cmaps }: Props) {
  const names = wantedAt(panels);
  const key = names.length ? JSON.stringify([names, query]) : null;
  const loaded = useLoad<Frame>(key, (signal) => loadArrays(names, query, signal));
  const { busy, error } = loaded;
  // The loader keeps the last frame while a new one computes. That is right when
  // an input moved (same plots, older numbers) and wrong when the checkpoint did
  // (different plots): a frame is drawn only if it holds every field asked for.
  const frame = loaded.value && names.every((n) => n in loaded.value!.arrays || n in loaded.value!.header.scalars) ? loaded.value : null;

  // Merger times as rules on every time-axis plot: the event list is JSON in the query.
  const mergerJson = String(query.mergers ?? "[]");
  const markers = useMemo(
    () =>
      (JSON.parse(mergerJson) as MergerEvent[]).map((m) => ({
        at: m.time,
        label: `${formatNumber(m.time)} Gyr (1:${formatNumber(1 / m.mass_ratio, 2)})`,
      })),
    [mergerJson],
  );

  if (names.length === 0 && panels.maps.length === 0) {
    return <p className={styles.note}>Checkpoint {checkpoint.n} publishes nothing to preview.</p>;
  }

  return (
    <div className={styles.preview}>
      <header className={styles.head}>
        <span className="gx-label">Checkpoint {checkpoint.n} preview</span>
        <span className={styles.name}>{checkpoint.name}</span>
        {frame && (
          // `stages` is what the server ran for this request (rule D4); a cached galaxy runs none.
          <span className={styles.stages}>
            {frame.header.stages.length ? `ran ${frame.header.stages.join(" · ")}` : "served from cache, no stage ran"}
          </span>
        )}
        {busy && <span className="gx-label">Recomputing</span>}
      </header>
      {error && <p className={styles.fault}>Preview failed: {error}</p>}
      {names.length > 0 && !frame && !error && <p className={styles.note}>Computing checkpoint {checkpoint.n}.</p>}

      {frame && panels.scalars.length > 0 && <Scalars fields={panels.scalars} values={frame.header.scalars} />}

      {frame && (
        <div className={styles.grid}>
          {panels.lines.map((panel) => {
            const axis = frame.header.grid.axes[panel.axis];
            const x = { values: centres(axis), label: panel.axis, unit: axis.unit_display };
            return (
              <LinePlot
                key={panel.key}
                title={panel.fields.length === 1 ? panel.fields[0].label : titleOf(panel.fields)}
                unit={panel.unitDisplay}
                x={x}
                log={panel.log}
                // Line panels hold kind "field" only (panelsAt), which is always f8.
                series={panel.fields.map((f) => ({ label: f.label, values: frame.arrays[f.name] as Float64Array }))}
                markers={panel.axis === "t" ? markers : []}
              />
            );
          })}
        </div>
      )}

      {panels.maps.length > 0 && <Histories maps={panels.maps} query={query} cmaps={cmaps} markers={markers} />}
    </div>
  );
}

/** The checkpoint's (R, t) histories: pick one, and only that one is fetched. */
function Histories({ maps, query, cmaps, markers }: {
  maps: FieldDecl[]; query: Query; cmaps: FieldsPayload["cmaps"]; markers: { at: number; label: string }[];
}) {
  const [picked, setPicked] = useState(maps[0].name);
  const name = maps.some((m) => m.name === picked) ? picked : maps[0].name;
  const decl = maps.find((m) => m.name === name)!;
  const loaded = useLoad<Frame>(JSON.stringify([name, query]), (signal) => loadArrays([name], query, signal));
  const frame = loaded.value && name in loaded.value.arrays ? loaded.value : null;

  return (
    <section className={styles.histories}>
      <div className={styles.historyHead}>
        <span className="gx-label">Histories · R against t</span>
        <div className={styles.picker} role="group" aria-label="History">
          {maps.map((m) => (
            <button key={m.name} aria-pressed={m.name === name} onClick={() => setPicked(m.name)} title={m.name}>
              {m.label}
            </button>
          ))}
        </div>
        {loaded.busy && <span className="gx-label">Loading {decl.label}</span>}
      </div>
      {loaded.error && <p className={styles.fault}>History failed: {loaded.error}</p>}
      {frame ? (
        <div className={styles.card}>
          <Heatmap
            decl={decl}
            values={frame.arrays[name]}
            R={frame.header.grid.axes.R}
            t={frame.header.grid.axes.t}
            cmaps={cmaps}
            markers={markers}
          />
        </div>
      ) : (
        !loaded.error && <p className={styles.note}>Loading {decl.label}: 400 × 2000 cells.</p>
      )}
    </section>
  );
}

/** A plot with several series is titled by what they share: their dimension. */
function titleOf(fields: FieldDecl[]): string {
  const dimension = String(fields[0].dimension ?? "").replace(/_/g, " ");
  return dimension ? dimension[0].toUpperCase() + dimension.slice(1) : fields.map((f) => f.label).join(", ");
}

function Scalars({ fields, values }: { fields: FieldDecl[]; values: Record<string, number> }) {
  return (
    <dl className={styles.scalars}>
      {fields.map((f) => {
        const v = values[f.name];
        const categorical = (f.categories?.length ?? 0) > 0;
        const unit = f.unit === "dimensionless" || categorical ? "" : String(f.unit_display ?? f.unit);
        return (
          <div key={f.name} className={styles.scalar} title={`${f.label} (${f.name})\n\n${String(f.about ?? "")}`}>
            <dt>{f.label}</dt>
            <dd>
              {v === undefined || v === null ? "not computed" : categorical ? f.categories![v] : formatNumber(v, 4)}
              {unit && <span className={styles.scalarUnit}> {unit}</span>}
            </dd>
          </div>
        );
      })}
    </dl>
  );
}
