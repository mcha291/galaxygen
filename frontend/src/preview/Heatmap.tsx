import { imageOf2D } from "@interface/field.js";
import { legendStops, paintOf } from "@interface/ramp.js";
import { codes } from "@interface/transport.js";
import { useEffect, useMemo, useRef, useState } from "react";

import type { FieldDecl, FieldsPayload } from "../api";
import { formatNumber } from "../workflow/logic";
import { type Axis, centres, linearTicks } from "./axes";
import { LinePlot } from "./LinePlot";
import styles from "./Heatmap.module.css";

interface Props {
  decl: FieldDecl;
  values: Float64Array | BigInt64Array;
  R: Axis;
  t: Axis;
  cmaps: FieldsPayload["cmaps"];
  markers?: { at: number; label: string }[];
}

const PAD = { left: 44, right: 10, top: 8, bottom: 26 };

/** What ramp.js's paintOf returns: a ramp (lo, hi, scale, stops) or a palette (categories, colors). */
interface Paint {
  color(value: number): number[];
  at?(t: number): number[];
  lo: number;
  hi: number;
  scale: string;
  cmap: string;
  note: string;
  stops: number[][];
  categories: string[];
  colors: number[][];
}

/**
 * An (R, t) history as an image, radius up and time across, with a scrubber
 * whose position is also drawn as the radial profile at that time.
 *
 * Pixels read the nearest cell and are coloured by the ramp the field declares
 * (interface/field.js, interface/ramp.js): no averaging, no colour chosen here.
 * A value the ramp cannot place (a zero on a log ramp) is transparent, so the
 * grid shows through where the model has no value.
 */
export function Heatmap({ decl, values: raw, R, t, cmaps, markers = [] }: Props) {
  // A categorical field is int64 on the wire and BigInt in JavaScript; the
  // transport's codes() is the one deliberate copy to numbers.
  const values = useMemo(() => (raw instanceof BigInt64Array ? (codes(raw) as Int32Array) : raw), [raw]);
  const box = useRef<HTMLDivElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const [size, setSize] = useState({ w: 0, h: 0 });
  const [it, setIt] = useState(t.n - 1); // the present day first

  const ramp = useMemo(() => paintOf(decl, cmaps, values) as unknown as Paint, [decl, cmaps, values]);
  // A categorical history (thin or thick at birth) has a palette, not a ramp:
  // its legend is the categories, and a "profile" of category codes means nothing.
  const palette = decl.ramp?.kind === "palette";
  const stops = useMemo(
    () => (palette ? [] : legendStops(ramp, 48).map(([r, g, b]: number[]) => `rgb(${r} ${g} ${b})`)),
    [ramp, palette],
  );

  useEffect(() => {
    const el = box.current;
    if (!el) return;
    const observer = new ResizeObserver(([e]) => setSize({ w: e.contentRect.width, h: e.contentRect.height }));
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  // The image depends on the data and the size only; the scrubber is drawn over it.
  const image = useMemo(() => {
    if (size.w === 0) return null;
    const dpr = window.devicePixelRatio || 1;
    const plotW = Math.max(1, Math.round((size.w - PAD.left - PAD.right) * dpr));
    const plotH = Math.max(1, Math.round((size.h - PAD.top - PAD.bottom) * dpr));
    const { data, width, height } = imageOf2D(values, R.n, t.n, ramp, { maxWidth: plotW, maxHeight: plotH, flipRows: true });
    const off = document.createElement("canvas");
    off.width = width;
    off.height = height;
    off.getContext("2d")!.putImageData(new ImageData(data, width, height), 0, 0);
    return off;
  }, [values, R.n, t.n, ramp, size]);

  useEffect(() => {
    const c = canvas.current;
    if (!c || !image) return;
    const dpr = window.devicePixelRatio || 1;
    c.width = Math.round(size.w * dpr);
    c.height = Math.round(size.h * dpr);
    const ctx = c.getContext("2d")!;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, size.w, size.h);
    const plotW = size.w - PAD.left - PAD.right;
    const plotH = size.h - PAD.top - PAD.bottom;

    ctx.imageSmoothingEnabled = false; // nearest cell, never blended
    ctx.drawImage(image, PAD.left, PAD.top, plotW, plotH);

    const probe = (token: string) => {
      c.style.color = `var(${token})`;
      return getComputedStyle(c).color;
    };
    const mono = getComputedStyle(c).getPropertyValue("--font-mono") || "monospace";
    ctx.font = `10px ${mono}`;
    ctx.fillStyle = probe("--text-muted");
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    for (const r of linearTicks(R.lo, R.hi, 5)) {
      ctx.fillText(formatNumber(r), PAD.left - 6, PAD.top + (1 - (r - R.lo) / (R.hi - R.lo)) * plotH);
    }
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    for (const g of linearTicks(t.lo, t.hi, 6)) {
      ctx.fillText(formatNumber(g), PAD.left + ((g - t.lo) / (t.hi - t.lo)) * plotW, PAD.top + plotH + 6);
    }

    const xOf = (time: number) => Math.round(PAD.left + ((time - t.lo) / (t.hi - t.lo)) * plotW) + 0.5;
    ctx.lineWidth = 1;
    ctx.strokeStyle = probe("--border-strong");
    for (const m of markers) {
      ctx.beginPath();
      ctx.moveTo(xOf(m.at), PAD.top);
      ctx.lineTo(xOf(m.at), PAD.top + plotH);
      ctx.stroke();
    }
    ctx.strokeStyle = probe("--magenta-3");
    ctx.lineWidth = 1.5;
    const xs = xOf(t.lo + (it + 0.5) * t.width);
    ctx.beginPath();
    ctx.moveTo(xs, PAD.top);
    ctx.lineTo(xs, PAD.top + plotH);
    ctx.stroke();
  }, [image, size, it, R, t, markers]);

  const scrubTo = (clientX: number) => {
    const rect = box.current!.getBoundingClientRect();
    const f = (clientX - rect.left - PAD.left) / (rect.width - PAD.left - PAD.right);
    setIt(Math.min(t.n - 1, Math.max(0, Math.floor(f * t.n))));
  };

  const profile = useMemo(() => {
    const out = new Float64Array(R.n);
    for (let i = 0; i < R.n; i += 1) out[i] = values[i * t.n + it];
    return out;
  }, [values, R.n, t.n, it]);
  const radii = useMemo(() => centres(R), [R]);
  const time = t.lo + (it + 0.5) * t.width;
  const unit = decl.unit === "dimensionless" ? "" : String(decl.unit_display ?? decl.unit);

  return (
    <div className={styles.heatmap}>
      <div className={styles.head}>
        <span className={styles.title}>{decl.label}</span>
        <span className={styles.unit}>R / {R.unit_display} against t / {t.unit_display}</span>
      </div>
      <div
        ref={box}
        className={styles.canvas}
        onPointerDown={(e) => {
          (e.target as Element).setPointerCapture(e.pointerId);
          scrubTo(e.clientX);
        }}
        onPointerMove={(e) => e.buttons === 1 && scrubTo(e.clientX)}
      >
        <canvas ref={canvas} />
      </div>
      <input
        type="range"
        className={styles.scrubber}
        min={0}
        max={t.n - 1}
        value={it}
        aria-label={`Time, ${t.unit_display}`}
        onChange={(e) => setIt(Number(e.target.value))}
      />
      {palette ? (
        <div className={styles.legend}>
          {ramp.categories.map((c, k) => {
            const [r, g, b] = ramp.colors[k];
            return (
              <span key={c} className={styles.category}>
                <span className={styles.chip} style={{ background: `rgb(${r} ${g} ${b})` }} />
                {c}
              </span>
            );
          })}
          <span className={styles.scale}>declared palette · at t = {formatNumber(time, 4)} {t.unit_display}</span>
        </div>
      ) : (
        <>
          <div className={styles.legend}>
            <span>{formatNumber(ramp.lo, 3)}</span>
            <span className={styles.strip} style={{ background: `linear-gradient(90deg, ${stops.join(",")})` }} />
            <span>
              {formatNumber(ramp.hi, 3)} {unit}
            </span>
            <span className={styles.scale}>
              {String(ramp.cmap)} · {String(ramp.scale)}
              {ramp.note ? ` · ${ramp.note}` : ""}
            </span>
          </div>
          <LinePlot
            title={`${decl.label} at t = ${formatNumber(time, 4)} ${t.unit_display}`}
            unit={unit}
            x={{ values: radii, label: "R", unit: R.unit_display }}
            series={[{ label: decl.label, values: profile }]}
            log={ramp.scale === "log"}
          />
        </>
      )}
    </div>
  );
}
