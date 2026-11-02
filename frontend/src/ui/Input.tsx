import { type InputHTMLAttributes, type ReactNode, useId } from "react";

import { cx } from "./cx";
import styles from "./Input.module.css";

export type ControlSize = "sm" | "md" | "lg";

interface Props extends Omit<InputHTMLAttributes<HTMLInputElement>, "size" | "prefix"> {
  /** The mono micro-label above the field; it names the field. Without one, name it with `aria-label`. */
  label?: ReactNode;
  /** A faint line under the field; it describes the field. */
  hint?: ReactNode;
  /** The fault, in place of the hint: the field is marked invalid and described by it. */
  error?: ReactNode;
  size?: ControlSize;
  /** Mono, for instrument values and query syntax. */
  mono?: boolean;
  /** Faint mono text inside the field before the value (a sign, a quantity). */
  prefix?: ReactNode;
  /** Faint mono text inside the field after the value: its unit. */
  suffix?: ReactNode;
  /** A class for the outer block. */
  className?: string;
}

/** The design system's Input: a text field on the inset, 24 / 32 / 40 px, the focus ring on its frame. */
export function Input({ label, hint, error, size = "md", mono = false, prefix, suffix, disabled, className, id, "aria-describedby": describedBy, ...rest }: Props) {
  const own = useId();
  const field = id ?? own;
  const note = `${field}-note`;
  const said = error || hint;
  return (
    <div className={cx(styles.block, disabled && styles.disabled, className)}>
      {label && (
        <label htmlFor={field} className={styles.label}>
          {label}
        </label>
      )}
      <div className={cx(styles.frame, styles[size], error ? styles.invalid : undefined)}>
        {prefix && <span className={styles.affix}>{prefix}</span>}
        <input
          id={field}
          disabled={disabled}
          aria-invalid={error ? true : undefined}
          aria-describedby={said ? cx(describedBy, note) : describedBy}
          className={cx(styles.input, mono && styles.mono)}
          {...rest}
        />
        {suffix && <span className={styles.affix}>{suffix}</span>}
      </div>
      {said && (
        <div id={note} className={cx(styles.note, error ? styles.fault : undefined)}>
          {said}
        </div>
      )}
    </div>
  );
}
