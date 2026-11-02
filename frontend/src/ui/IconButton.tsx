import type { ButtonHTMLAttributes } from "react";

import { cx } from "./cx";
import styles from "./IconButton.module.css";

export type IconButtonSize = "sm" | "md" | "lg";

interface Props extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "aria-label"> {
  /** The button's name, read by assistive technology and shown as its title: an icon alone names nothing. */
  label: string;
  size?: IconButtonSize;
  /** A toggle's state (a rail's current item): magenta, and `aria-pressed`. Left out, the button is no toggle. */
  selected?: boolean;
  /** The title where it should say more than the name (the name stays `label`). */
  title?: string;
}

/** The design system's IconButton: a square icon-only control for toolbars and rails - 24, 32 or 40 px. */
export function IconButton({ label, size = "md", selected, title, className, children, ...rest }: Props) {
  return (
    <button
      type="button"
      aria-label={label}
      title={title ?? label}
      aria-pressed={selected}
      className={cx(styles.button, styles[size], selected && styles.selected, className)}
      {...rest}
    >
      {children}
    </button>
  );
}
