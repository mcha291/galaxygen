import { type ReactNode, useEffect, useId, useRef } from "react";

import { cx } from "./cx";
import styles from "./Checkbox.module.css";

interface Props {
  label: ReactNode;
  /** A faint line under the label; it describes the box. */
  description?: ReactNode;
  checked?: boolean;
  /** Neither checked nor not (a group partly checked): a bar in the box, `aria-checked="mixed"`. */
  indeterminate?: boolean;
  disabled?: boolean;
  onChange?(checked: boolean): void;
  className?: string;
  title?: string;
}

/**
 * The design system's Checkbox: a 16 px square box, magenta with a knockout tick when checked. A native checkbox
 * underneath (hidden, never removed), so Space toggles it and the label names it; the focus ring is drawn on the box.
 */
export function Checkbox({ label, description, checked = false, indeterminate = false, disabled, onChange, className, title }: Props) {
  const input = useRef<HTMLInputElement>(null);
  const describedBy = useId();
  useEffect(() => {
    if (input.current) input.current.indeterminate = indeterminate;
  }, [indeterminate]);
  const on = checked || indeterminate;
  return (
    <label className={cx(styles.checkbox, disabled && styles.disabled, className)} title={title}>
      <input
        ref={input}
        type="checkbox"
        className={styles.input}
        checked={checked}
        disabled={disabled}
        aria-checked={indeterminate ? "mixed" : undefined}
        aria-describedby={description ? describedBy : undefined}
        onChange={(e) => onChange?.(e.target.checked)}
      />
      <span className={cx(styles.box, on && styles.on)} aria-hidden>
        {indeterminate ? (
          <span className={styles.bar} />
        ) : checked ? (
          <svg viewBox="0 0 24 24" className={styles.tick}>
            <path d="M5 13l4 4L19 7" />
          </svg>
        ) : null}
      </span>
      <span className={styles.text}>
        <span className={styles.label}>{label}</span>
        {description && (
          <span id={describedBy} className={styles.description}>
            {description}
          </span>
        )}
      </span>
    </label>
  );
}
