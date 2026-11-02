import type { HTMLAttributes, ReactNode } from "react";

import { cx } from "./cx";
import styles from "./Meter.module.css";

export type MeterTone = "accent" | "nominal" | "caution" | "fault";

/** The bar's filled share, percent: value over max, held to 0-100 (and 0 for a max that is not above zero). */
export function meterPercent(value: number, max: number): number {
  if (!(max > 0) || !Number.isFinite(value)) return 0;
  return Math.max(0, Math.min(100, (value / max) * 100));
}

interface Props extends HTMLAttributes<HTMLDivElement> {
  value: number;
  max?: number;
  /** The mono micro-label at the left; as text, it names the bar. */
  label?: ReactNode;
  /** The value in words at the right, with its unit (mono); as text, it is the bar's value text. */
  valueLabel?: ReactNode;
  tone?: MeterTone;
  /** The bar's height, px (the design's 4). */
  height?: number;
}

/** The design system's Meter: a linear progress / utilisation bar - square ends, a hairline track on the inset. */
export function Meter({ value, max = 100, label, valueLabel, tone = "accent", height = 4, className, ...rest }: Props) {
  return (
    <div className={cx(styles.meter, className)} {...rest}>
      {(label || valueLabel) && (
        <div className={styles.head}>
          <span className={styles.label}>{label}</span>
          <span className={styles.value}>{valueLabel}</span>
        </div>
      )}
      <div
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
        aria-label={typeof label === "string" ? label : undefined}
        aria-valuetext={typeof valueLabel === "string" ? valueLabel : undefined}
        className={styles.track}
        style={{ height }}
      >
        <div className={cx(styles.fill, styles[tone])} style={{ width: `${meterPercent(value, max)}%` }} />
      </div>
    </div>
  );
}
