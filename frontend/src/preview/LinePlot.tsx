import { useEffect, useRef, useState } from "react";

import { formatNumber, formatPower } from "../workflow/logic";
import { type Range, linearTicks, logTicks, position, rangeOf } from "./axes";
import styles from "./LinePlot.module.css";

// Series take the design system's data palette in order (tokens, never hex).
const SERIES_TOKENS = ["--spectral-o", "--spectral-m", "--aqua-2", "--violet-2", "--spectral-k", "--coral-2", "--amber-2"];

export interface Series {
  label: string;
  values: ArrayLike<number>;
}

interface Props {
  title: string;
  x: { values: ArrayLike<number>; label: string; unit: string };
  unit: string;
  series: Series[];
  log: boolean;
  /** Vertical rules at these x values, e.g. merger times on a time axis. */
  markers?: { at: number; label: string }[];
}

const PAD = { left: 52, right: 12, top: 10, bottom: 30 };

/** A token's resolved colour. Custom properties do not compute to colours on their own. */
function resolve(probe: HTMLElement, token: string): string {
  probe.style.color = `var(${token})`;
  return getComputedStyle(probe).color;
}

export function LinePlot({ title, x, unit, series, log, markers = [] }: Props) {
  const box = useRef<HTMLDivElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const [size, setSize] = useState({ w: 0, h: 0 });
  const [hover, setHover] = useState<number | null>(null);

  const xRange: Range = { lo: x.values[0], hi: x.values[x.values.length - 1] };
  const yRange = rangeOf(series.map((s) => s.values), log);

  useEffect(() => {
    const el = box.current;
    if (!el) return;
    const observer = new ResizeObserver(([entry]) => setSize({ w: entry.contentRect.width, h: entry.contentRect.height }));
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const c = canvas.current;
    if (!c || size.w === 0 || !yRange) return;
    const dpr = window.devicePixelRatio || 1;
    c.width = Math.round(size.w * dpr);
    c.height = Math.round(size.h * dpr);
    const ctx = c.getContext("2d")!;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, size.w, size.h);

    const colour = (token: string) => resolve(c, token);
    const mono = getComputedStyle(c).getPropertyValue("--font-mono") || "monospace";
    const plotW = size.w - PAD.left - PAD.right;
    const plotH = size.h - PAD.top - PAD.bottom;
    const px = (v: number) => PAD.left + position(v, xRange, false) * plotW;
    const py = (v: number) => PAD.top + (1 - position(v, yRange, log)) * plotH;

    // Grid and ticks.
    ctx.font = `10px ${mono}`;
    ctx.lineWidth = 1;
    const grid = colour("--border-hair");
    const tickInk = colour("--text-muted");
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    for (const t of log ? logTicks(yRange.lo, yRange.hi) : linearTicks(yRange.lo, yRange.hi, 4)) {
      const y = Math.round(py(t)) + 0.5;
      ctx.strokeStyle = grid;
      ctx.beginPath();
      ctx.moveTo(PAD.left, y);
      ctx.lineTo(PAD.left + plotW, y);
      ctx.stroke();
      ctx.fillStyle = tickInk;
      ctx.fillText(log ? formatPower(t) : formatNumber(t, 2), PAD.left - 6, y);
    }
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    for (const t of linearTicks(xRange.lo, xRange.hi, 6)) {
      const xp = Math.round(px(t)) + 0.5;
      ctx.strokeStyle = grid;
      ctx.beginPath();
      ctx.moveTo(xp, PAD.top);
      ctx.lineTo(xp, PAD.top + plotH);
      ctx.stroke();
      ctx.fillStyle = tickInk;
      ctx.fillText(formatNumber(t, 3), xp, PAD.top + plotH + 6);
    }

    // Markers: an input, so a solid rule; dashed would mean inferred (design readme).
    ctx.strokeStyle = colour("--border-strong");
    for (const m of markers) {
      if (m.at < xRange.lo || m.at > xRange.hi) continue;
      const xp = Math.round(px(m.at)) + 0.5;
      ctx.beginPath();
      ctx.moveTo(xp, PAD.top);
      ctx.lineTo(xp, PAD.top + plotH);
      ctx.stroke();
    }

    // Series: a gap wherever a value is missing, never a line drawn through it.
    ctx.lineWidth = 1.5;
    ctx.save();
    ctx.beginPath();
    ctx.rect(PAD.left, PAD.top, plotW, plotH);
    ctx.clip();
    series.forEach((s, k) => {
      ctx.strokeStyle = colour(SERIES_TOKENS[k % SERIES_TOKENS.length]);
      ctx.beginPath();
      let pen = false;
      for (let i = 0; i < s.values.length; i += 1) {
        const v = s.values[i];
        if (!Number.isFinite(v) || (log && v <= 0)) {
          pen = false;
          continue;
        }
        const X = px(x.values[i]);
        const Y = py(v);
        if (pen) ctx.lineTo(X, Y);
        else ctx.moveTo(X, Y);
        pen = true;
      }
      ctx.stroke();
    });
    ctx.restore();

    if (hover !== null) {
      const xp = Math.round(px(x.values[hover])) + 0.5;
      ctx.strokeStyle = colour("--magenta-3");
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(xp, PAD.top);
      ctx.lineTo(xp, PAD.top + plotH);
      ctx.stroke();
    }
  }, [size, series, x, log, markers, hover, xRange.lo, xRange.hi, yRange?.lo, yRange?.hi]);

  const onMove = (e: React.PointerEvent) => {
    const rect = box.current!.getBoundingClientRect();
    const t = (e.clientX - rect.left - PAD.left) / (rect.width - PAD.left - PAD.right);
    if (t < 0 || t > 1) return setHover(null);
    const target = xRange.lo + t * (xRange.hi - xRange.lo);
    // Axes are uniform grids, so the nearest cell is arithmetic, not a search.
    const i = Math.round(((target - x.values[0]) / (xRange.hi - xRange.lo)) * (x.values.length - 1));
    setHover(Math.min(Math.max(i, 0), x.values.length - 1));
  };

  return (
    <figure className={styles.plot}>
      <figcaption className={styles.head}>
        <span className={styles.title}>{title}</span>
        <span className={styles.unit}>{unit}</span>
      </figcaption>
      <ul className={styles.legend}>
        {series.map((s, k) => (
          <li key={s.label}>
            <span className={styles.swatch} style={{ background: `var(${SERIES_TOKENS[k % SERIES_TOKENS.length]})` }} />
            {s.label}
            {hover !== null && <span className={styles.readout}>{formatNumber(Number(s.values[hover]), 4)}</span>}
          </li>
        ))}
      </ul>
      <div ref={box} className={styles.canvas} onPointerMove={onMove} onPointerLeave={() => setHover(null)}>
        <canvas ref={canvas} />
        {!yRange && <p className={styles.empty}>No finite values to draw.</p>}
      </div>
      <div className={styles.xlabel}>
        {hover !== null ? `${x.label} = ${formatNumber(Number(x.values[hover]), 4)} ${x.unit}` : `${x.label} / ${x.unit}`}
        {markers.length > 0 && <span> · rules at {markers.map((m) => m.label).join(", ")}</span>}
      </div>
    </figure>
  );
}
