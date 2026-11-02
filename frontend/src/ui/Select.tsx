import { ChevronDown } from "lucide-react";
import { type ReactNode, type SelectHTMLAttributes, useId } from "react";

import { cx } from "./cx";
import type { ControlSize } from "./Input";
import styles from "./Select.module.css";

export type SelectOption = string | { value: string; label: ReactNode; title?: string };

/** An option's value and its words. */
export function optionOf(o: SelectOption): { value: string; label: ReactNode; title?: string } {
  return typeof o === "string" ? { value: o, label: o } : o;
}

interface Props extends Omit<SelectHTMLAttributes<HTMLSelectElement>, "size"> {
  /** The mono micro-label above; it names the select. Without one, name it with `aria-label`. */
  label?: ReactNode;
  options: readonly SelectOption[];
  /** A faint line under it; it describes the select. */
  hint?: ReactNode;
  size?: ControlSize;
  /** Mono, where the options are instrument names or values. */
  mono?: boolean;
  /** A class for the outer block. */
  className?: string;
}

/** The design system's Select: the native select, styled as a Galaxy control - the inset, a faint chevron, the focus ring. */
export function Select({ label, options, hint, size = "md", mono = false, disabled, className, id, "aria-describedby": describedBy, ...rest }: Props) {
  const own = useId();
  const field = id ?? own;
  const note = `${field}-note`;
  return (
    <div className={cx(styles.block, disabled && styles.disabled, className)}>
      {label && (
        <label htmlFor={field} className={styles.label}>
          {label}
        </label>
      )}
      <div className={styles.frame}>
        <select
          id={field}
          disabled={disabled}
          aria-describedby={hint ? cx(describedBy, note) : describedBy}
          className={cx(styles.select, styles[size], mono && styles.mono)}
          {...rest}
        >
          {options.map((o) => {
            const { value, label: words, title } = optionOf(o);
            return (
              <option key={value} value={value} title={title}>
                {words}
              </option>
            );
          })}
        </select>
        <ChevronDown className={styles.chevron} aria-hidden />
      </div>
      {hint && (
        <div id={note} className={styles.note}>
          {hint}
        </div>
      )}
    </div>
  );
}
