import type { HTMLAttributes, ReactNode } from "react";

import { cx } from "./cx";
import styles from "./StatusDot.module.css";

/**
 * The status tones, and "accent": the component's source has none, but the mockup (Galaxygen.dc.html) asks its
 * StatusDot for "accent" on the zoom regime that is the view's own choice; it is the selected magenta.
 */
export type StatusTone = "nominal" | "caution" | "fault" | "archive" | "idle" | "accent";
export const STATUS_TONES: readonly StatusTone[] = ["nominal", "caution", "fault", "archive", "idle", "accent"];

interface Props extends HTMLAttributes<HTMLSpanElement> {
  tone?: StatusTone;
  /** The state in words: status is a dot and a label, never colour alone. */
  label?: ReactNode;
  /** The nominal glow, for something live. */
  pulse?: boolean;
}

/** The design system's StatusDot: the 8 px status dot, the system's one round element besides the Switch. */
export function StatusDot({ tone = "idle", label, pulse = false, className, children, ...rest }: Props) {
  return (
    <span className={cx(styles.status, className)} data-tone={tone} {...rest}>
      <span className={cx(styles.dot, styles[tone], pulse && tone === "nominal" && styles.pulse)} aria-hidden />
      {label && <span className={styles.label}>{label}</span>}
      {children}
    </span>
  );
}
