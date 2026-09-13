import { SLIDER_STEPS, type InputDecl, formatNumber, fromSlider, toSlider } from "./logic";
import styles from "./ExperimentBar.module.css";

interface Props {
  inputs: InputDecl[];
  values: Record<string, number>;
  onChange(name: string, value: number): void;
}

/** Sliders for the inputs being explored, in the bottom bar. Unset values show the published default. */
export function ExperimentBar({ inputs, values, onChange }: Props) {
  return (
    <span className={styles.bar}>
      <span className={styles.tag}>experiment</span>
      {inputs.map((d) => {
        const value = values[d.name] ?? (d.default as number);
        return (
          <label key={d.name} className={styles.item} title={d.about}>
            <span className={styles.name}>{d.name}</span>
            <input
              type="range"
              min={0}
              max={SLIDER_STEPS}
              value={toSlider(d, value)}
              onChange={(e) => onChange(d.name, fromSlider(d, Number(e.target.value)))}
            />
            <span className={styles.value}>{formatNumber(value, 2)}</span>
          </label>
        );
      })}
    </span>
  );
}
