import type { HTMLAttributes } from "react";

import { cx } from "./cx";
import styles from "./Badge.module.css";

export type BadgeTone = "neutral" | "nominal" | "caution" | "fault" | "archive" | "accent";
export const BADGE_TONES: readonly BadgeTone[] = ["neutral", "nominal", "caution", "fault", "archive", "accent"];

interface Props extends HTMLAttributes<HTMLSpanElement> {
  tone?: BadgeTone;
}

/** The design system's Badge: a small status label - mono, uppercase, hairline-bordered, tinted by its tone. */
export function Badge({ tone = "neutral", className, children, ...rest }: Props) {
  return (
    <span className={cx(styles.badge, styles[tone], className)} data-tone={tone} {...rest}>
      {children}
    </span>
  );
}
