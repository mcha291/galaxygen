import type { HTMLAttributes, ReactNode } from "react";

import { cx } from "./cx";
import styles from "./Readout.module.css";

export type ReadoutTone = "nominal" | "caution" | "fault" | "accent";

interface Props extends HTMLAttributes<HTMLDivElement> {
  /** The mono micro-label above the value. */
  label: ReactNode;
  /** What the instrument read: mono, light weight. */
  value: ReactNode;
  /** Always attached where the value has one. */
  unit?: ReactNode;
  tone?: ReadoutTone;
  /** A change or an uncertainty under the value, mono. */
  delta?: ReactNode;
  align?: "left" | "right";
  /** The value's size: 16, 26 or 34 px. */
  size?: "sm" | "md" | "lg";
}

/** The design system's Readout: a labelled instrument value - mono, light weight, the unit always attached. */
export function Readout({ label, value, unit, tone, delta, align = "left", size = "md", className, ...rest }: Props) {
  return (
    <div className={cx(styles.readout, align === "right" && styles.right, className)} {...rest}>
      <div className={styles.label}>{label}</div>
      <div className={styles.line}>
        <span className={cx(styles.value, styles[size], tone && styles[tone])}>{value}</span>
        {unit && <span className={styles.unit}>{unit}</span>}
      </div>
      {delta && <div className={styles.delta}>{delta}</div>}
    </div>
  );
}
