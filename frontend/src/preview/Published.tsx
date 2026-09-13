import { type FieldDecl, type Frame, type Query, loadArrays } from "../api";
import { useLoad } from "../useLoad";
import { formatNumber } from "../workflow/logic";
import styles from "../App.module.css";

/**
 * "Published at this checkpoint": the checkpoint's galaxy-level scalars as large
 * readouts, as the design's workflow tab shows them. They ride in the header of
 * an arrays request, which runs the stages up to this checkpoint and no further.
 */
export function Published({ scalars, query }: { scalars: FieldDecl[]; query: Query }) {
  const names = scalars.map((f) => f.name);
  const key = names.length ? JSON.stringify([names, query]) : null;
  const loaded = useLoad<Frame>(key, (signal) => loadArrays(names, query, signal));
  const values = loaded.value && names.every((n) => n in loaded.value!.header.scalars) ? loaded.value.header.scalars : null;

  return (
    <section>
      <div className={styles.overlayHead}>
        <span className={styles.rule} />
        <span className={styles.overlayLabel}>Published at this checkpoint</span>
      </div>
      {names.length === 0 && <p className={styles.overlayNote}>No galaxy-level values at this checkpoint.</p>}
      {loaded.error && <p className={styles.overlayNote}>Values unavailable: {loaded.error}</p>}
      {scalars.map((f) => {
        const v = values?.[f.name];
        const categorical = (f.categories?.length ?? 0) > 0;
        const unit = f.unit === "dimensionless" || categorical ? "" : String(f.unit_display ?? f.unit);
        return (
          <div key={f.name} className={styles.stat} title={String(f.about ?? "")}>
            <div className={styles.statKey}>{f.label}</div>
            <div className={styles.statValue}>
              <span>{v === undefined || v === null ? "—" : categorical ? f.categories![v] : formatNumber(v, 4)}</span>
              {unit && <span className={styles.statUnit}>{unit}</span>}
            </div>
          </div>
        );
      })}
    </section>
  );
}
