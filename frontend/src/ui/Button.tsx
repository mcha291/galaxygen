import type { ButtonHTMLAttributes, ReactNode } from "react";

import styles from "./Button.module.css";

type Variant = "primary" | "secondary" | "ghost";

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  icon?: ReactNode;
}

/** The design system's Button (primary, secondary, ghost; size sm), as a CSS Module. */
export function Button({ variant = "secondary", icon, children, className, ...rest }: Props) {
  return (
    <button type="button" className={[styles.button, styles[variant], className].filter(Boolean).join(" ")} {...rest}>
      {icon}
      {children}
    </button>
  );
}
