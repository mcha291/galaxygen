import { type KeyboardEvent, type ReactNode, useRef } from "react";

import { cx } from "./cx";
import styles from "./Tabs.module.css";

export interface TabItem<T extends string> {
  value: T;
  label: ReactNode;
  /** A mono count after the label. */
  count?: ReactNode;
  title?: string;
}

/**
 * The tab a key moves to from tab `index` of `count` (the WAI-ARIA tabs pattern, selection following focus): the
 * arrows step and wrap, Home and End go to either end; null for any other key.
 */
export function tabKeyTarget(count: number, index: number, key: string): number | null {
  if (count === 0) return null;
  if (key === "ArrowRight" || key === "ArrowDown") return (index + 1) % count;
  if (key === "ArrowLeft" || key === "ArrowUp") return (index - 1 + count) % count;
  if (key === "Home") return 0;
  if (key === "End") return count - 1;
  return null;
}

interface Props<T extends string> {
  items: readonly TabItem<T>[];
  value: T;
  onChange(value: T): void;
  /** The tab list's name. */
  "aria-label"?: string;
  className?: string;
}

/**
 * The design system's Tabs: an underline tab bar, the selected tab carrying the magenta rule. One tab is in the
 * page's Tab order (the selected one); the arrow keys, Home and End move between them and select as they go.
 */
export function Tabs<T extends string>({ items, value, onChange, "aria-label": label, className }: Props<T>) {
  const tabs = useRef<(HTMLButtonElement | null)[]>([]);
  const onKeyDown = (e: KeyboardEvent<HTMLButtonElement>, index: number) => {
    const to = tabKeyTarget(items.length, index, e.key);
    if (to === null) return;
    e.preventDefault();
    onChange(items[to].value);
    tabs.current[to]?.focus();
  };
  return (
    <div role="tablist" aria-label={label} className={cx(styles.tabs, className)}>
      {items.map((it, i) => {
        const on = it.value === value;
        return (
          <button
            key={it.value}
            ref={(el) => {
              tabs.current[i] = el;
            }}
            type="button"
            role="tab"
            aria-selected={on}
            tabIndex={on ? 0 : -1}
            title={it.title}
            className={cx(styles.tab, on && styles.selected)}
            onClick={() => onChange(it.value)}
            onKeyDown={(e) => onKeyDown(e, i)}
          >
            {it.label}
            {it.count != null && <span className={styles.count}>{it.count}</span>}
          </button>
        );
      })}
    </div>
  );
}
