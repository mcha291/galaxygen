import styles from "./Exposure.module.css";

/** Photometric exposure in stops: each doubles the light every star contributes before tone mapping. */
export function Exposure({ stops, onChange }: { stops: number; onChange(stops: number): void }) {
  return (
    <label className={styles.exposure}>
      <span>exposure</span>
      <input type="range" min={-6} max={8} step={0.5} value={stops} onChange={(e) => onChange(Number(e.target.value))} aria-label="Exposure" />
      <span className={styles.value}>{stops > 0 ? `+${stops}` : stops} stops</span>
    </label>
  );
}
