import { legendStops, paintOf } from "@interface/ramp.js";
import { useMemo } from "react";

import type { FieldDecl, FieldsPayload } from "../api";
import { formatNumber } from "../workflow/logic";
import styles from "./GalaxyTab.module.css";

interface Paint {
  lo: number;
  hi: number;
  scale: string;
  cmap: string;
  note: string;
  categories: string[];
  colors: number[][];
}

/** The painting field's legend: its declared ramp sampled by ramp.js, or its palette's categories. */
export function FieldLegend({ decl, values, cmaps }: { decl: FieldDecl; values: ArrayLike<number | bigint>; cmaps: FieldsPayload["cmaps"] }) {
  const palette = decl.ramp?.kind === "palette";
  const paint = useMemo(() => paintOf(decl, cmaps, values) as unknown as Paint, [decl, cmaps, values]);
  const strip = useMemo(
    () => (palette ? "" : `linear-gradient(90deg, ${legendStops(paint, 48).map(([r, g, b]: number[]) => `rgb(${r} ${g} ${b})`).join(",")})`),
    [paint, palette],
  );
  const unit = decl.unit === "dimensionless" ? "" : String(decl.unit_display ?? decl.unit);

  return (
    <div className={styles.section}>
      <div className={styles.legendHead}>
        <span className={styles.fieldName}>{decl.name}</span>
        <span className={styles.muted}>{palette ? "palette" : `${paint.cmap} · ${paint.scale}`}</span>
      </div>
      {palette ? (
        <div className={styles.categories}>
          {paint.categories.map((c, k) => (
            <span key={c}>
              <i style={{ background: `rgb(${paint.colors[k].join(" ")})` }} />
              {c}
            </span>
          ))}
        </div>
      ) : (
        <>
          <div className={styles.strip} style={{ background: strip }} />
          <div className={styles.legendScale}>
            <span>{formatNumber(paint.lo, 3)}</span>
            <span>{unit}</span>
            <span>{formatNumber(paint.hi, 3)}</span>
          </div>
        </>
      )}
      <p className={styles.note}>{String(decl.about ?? "")}</p>
    </div>
  );
}
