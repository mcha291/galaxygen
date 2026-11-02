import type { ReactNode } from "react";

import { cx } from "./cx";
import styles from "./Switch.module.css";

interface Props {
  label: ReactNode;
  checked?: boolean;
  disabled?: boolean;
  onChange?(checked: boolean): void;
  className?: string;
  title?: string;
}

/**
 * The design system's Switch: for live, immediately applied state (an overlay, a layer). A native checkbox with the
 * switch role underneath (hidden, never removed), so Space flips it and the label names it; the track carries the
 * focus ring, magenta when on.
 */
export function Switch({ label, checked = false, disabled, onChange, className, title }: Props) {
  return (
    <label className={cx(styles.switch, disabled && styles.disabled, className)} title={title}>
      <input
        type="checkbox"
        role="switch"
        className={styles.input}
        checked={checked}
        disabled={disabled}
        onChange={(e) => onChange?.(e.target.checked)}
      />
      <span className={cx(styles.track, checked && styles.on)} aria-hidden>
        <span className={styles.knob} />
      </span>
      <span className={styles.label}>{label}</span>
    </label>
  );
}
