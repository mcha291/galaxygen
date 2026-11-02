import { type HTMLAttributes, type ReactNode, useId } from "react";

import { cx } from "./cx";
import styles from "./Card.module.css";

interface Props extends Omit<HTMLAttributes<HTMLElement>, "title"> {
  /** The card's heading (h3 size); it names the section. */
  title?: ReactNode;
  /** The mono micro-label above the title. */
  label?: ReactNode;
  /** Controls at the header's right. */
  actions?: ReactNode;
  /** The body's padding, a spacing token (the design's default `var(--space-5)`). */
  padding?: string;
}

/** The design system's Card: Galaxy's default container - a hairline panel with an inset highlight, no drop shadow. */
export function Card({ title, label, actions, padding, className, children, ...rest }: Props) {
  const heading = useId();
  const header = title || label || actions;
  return (
    <section className={cx(styles.card, className)} aria-labelledby={title ? heading : undefined} {...rest}>
      {header && (
        <header className={styles.header}>
          <div className={styles.titles}>
            {label && <div className={styles.label}>{label}</div>}
            {title && (
              <div id={heading} className={styles.title}>
                {title}
              </div>
            )}
          </div>
          {actions}
        </header>
      )}
      <div className={styles.body} style={padding ? { padding } : undefined}>
        {children}
      </div>
    </section>
  );
}
