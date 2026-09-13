import { useRef } from "react";

import { formatNumber, type MergerEvent } from "./logic";
import { heightOf, timeAt } from "./timeline";
import styles from "./MergerTimeline.module.css";

interface Props {
  events: MergerEvent[];
  tMax: number;
  selected: number | null;
  disabled: boolean;
  onSelect(i: number): void;
  onMove(i: number, time: number): void;
}

/**
 * The event list as a timeline (design brief §2): time is the axis, mass ratio
 * is the bar's height on a log scale. Drag a bar to move its event in time; the
 * table below edits every number exactly.
 */
export function MergerTimeline({ events, tMax, selected, disabled, onSelect, onMove }: Props) {
  const track = useRef<HTMLDivElement>(null);
  const ticks = Array.from({ length: Math.floor(tMax / 2) + 1 }, (_, k) => k * 2);

  const drag = (i: number) => (e: React.PointerEvent<HTMLButtonElement>) => {
    onSelect(i);
    if (disabled) return;
    const el = e.currentTarget;
    el.setPointerCapture(e.pointerId);
    const move = (ev: PointerEvent) => {
      const rect = track.current!.getBoundingClientRect();
      onMove(i, timeAt((ev.clientX - rect.left) / rect.width, tMax));
    };
    const up = () => {
      el.removeEventListener("pointermove", move);
      el.removeEventListener("pointerup", up);
    };
    el.addEventListener("pointermove", move);
    el.addEventListener("pointerup", up);
  };

  return (
    <div className={styles.timeline} data-disabled={disabled || undefined}>
      <div ref={track} className={styles.track}>
        {ticks.map((t) => (
          <span key={t} className={styles.tick} style={{ left: `${(t / tMax) * 100}%` }}>
            {t}
          </span>
        ))}
        {events.map((e, i) => (
          <button
            key={i}
            type="button"
            className={styles.bar}
            aria-pressed={i === selected}
            aria-label={`Merger ${i + 1}: t = ${e.time} Gyr, mass ratio ${e.mass_ratio}`}
            title={e.about || `t = ${e.time} Gyr · 1:${formatNumber(1 / e.mass_ratio, 2)} · gas ${e.gas_fraction}`}
            style={{ left: `${(Math.min(e.time, tMax) / tMax) * 100}%`, height: `${Math.max(heightOf(e.mass_ratio), 0.04) * 100}%` }}
            onPointerDown={drag(i)}
            onKeyDown={(ev) => {
              if (disabled) return;
              const step = ev.shiftKey ? 1 : 0.1;
              if (ev.key === "ArrowLeft") onMove(i, Math.max(0, Math.round((e.time - step) * 20) / 20));
              if (ev.key === "ArrowRight") onMove(i, Math.min(tMax, Math.round((e.time + step) * 20) / 20));
            }}
          >
            <span className={styles.ratio}>1:{formatNumber(1 / e.mass_ratio, 2)}</span>
          </button>
        ))}
      </div>
      <div className={styles.axis}>
        <span>time / Gyr →</span>
        <span>height = mass ratio, log</span>
      </div>
    </div>
  );
}
