import { Tooltip } from "../ui/Tooltip";
import { EXPOSURE_RANGE } from "./tuning";
import styles from "./Exposure.module.css";

/** Photometric exposure in stops: each doubles the light every star contributes before tone mapping. */
export function Exposure({ stops, onChange }: { stops: number; onChange(stops: number): void }) {
  return (
    <label className={styles.exposure}>
      <span>exposure</span>
      {/* The design system's Tooltip (T17, S84): the slider is described by the line. */}
      <Tooltip content="Each stop doubles the light" className={styles.slot}>
        <input type="range" min={EXPOSURE_RANGE.min} max={EXPOSURE_RANGE.max} step={EXPOSURE_RANGE.step} value={stops} onChange={(e) => onChange(Number(e.target.value))} aria-label="Exposure" />
      </Tooltip>
      <span className={styles.value}>{stops > 0 ? `+${stops}` : stops} stops</span>
    </label>
  );
}
