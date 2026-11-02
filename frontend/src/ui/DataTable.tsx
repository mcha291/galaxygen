import { type KeyboardEvent, type ReactNode, useState } from "react";

import { cx } from "./cx";
import styles from "./DataTable.module.css";

export interface Column<Row> {
  key: string;
  label: ReactNode;
  /** Numbers are right-aligned. */
  align?: "left" | "right" | "center";
  /** Mono: the column holds what an instrument produced. */
  mono?: boolean;
  /** The muted ink: a column that annotates the others. */
  muted?: boolean;
  /** A CSS width for the column (the table's layout is fixed). */
  width?: string | number;
  render?(row: Row): ReactNode;
  /** The header's accessible name where its label is not text (an icon, nothing). */
  ariaLabel?: string;
}

/** Whether a key on a selectable row selects it: Enter and Space, as a button's. */
export function selectsRow(key: string): boolean {
  return key === "Enter" || key === " ";
}

interface Props<Row> {
  columns: readonly Column<Row>[];
  rows: readonly Row[];
  /** The row whose `rowKey` is this is selected: the magenta rule at its left. */
  selectedId?: unknown;
  /** Rows are chosen with a press, Enter or Space, and are in the Tab order. */
  onSelectRow?(id: unknown): void;
  rowKey?: keyof Row & string;
  /** What the window lacks, said where the rows would be. */
  empty?: ReactNode;
  /** The table's name. */
  "aria-label"?: string;
  /** The telemetry density: cells on the 2 / 4 px steps (--space-1 exists for these tables alone), for a narrow panel. */
  dense?: boolean;
  className?: string;
}

/** The design system's DataTable: a dense hairline table, mono uppercase headers, numeric columns mono and right-aligned. */
export function DataTable<Row extends object>({
  columns,
  rows,
  selectedId,
  onSelectRow,
  rowKey = "id" as keyof Row & string,
  empty = "No rows in this window.",
  "aria-label": label,
  dense = false,
  className,
}: Props<Row>) {
  const [hover, setHover] = useState<unknown>(null);
  if (rows.length === 0) return <div className={cx(styles.empty, className)}>{empty}</div>;
  const cell = (c: Column<Row>) => cx(styles.cell, c.mono && styles.mono, c.align && styles[c.align]);
  return (
    <table className={cx(styles.table, dense && styles.dense, className)} aria-label={label}>
      <thead>
        <tr>
          {columns.map((c) => (
            <th key={c.key} scope="col" className={cx(cell(c), styles.head)} style={c.width != null ? { width: c.width } : undefined} aria-label={c.ariaLabel}>
              {c.label}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((r, i) => {
          const id = (r as Record<string, unknown>)[rowKey] ?? i;
          const selected = selectedId != null && id === selectedId;
          const choose = onSelectRow ? () => onSelectRow(id) : undefined;
          return (
            <tr
              key={String(id)}
              className={cx(styles.row, onSelectRow && styles.selectable, hover === id && styles.hover, selected && styles.selected)}
              aria-selected={onSelectRow ? selected : undefined}
              tabIndex={onSelectRow ? 0 : undefined}
              onClick={choose}
              onKeyDown={
                choose &&
                ((e: KeyboardEvent<HTMLTableRowElement>) => {
                  if (e.target !== e.currentTarget || !selectsRow(e.key)) return;
                  e.preventDefault();
                  choose();
                })
              }
              onMouseEnter={() => setHover(id)}
              onMouseLeave={() => setHover(null)}
            >
              {columns.map((c) => (
                <td key={c.key} className={cx(cell(c), c.muted && styles.muted)}>
                  {c.render ? c.render(r) : ((r as Record<string, ReactNode>)[c.key] ?? null)}
                </td>
              ))}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
