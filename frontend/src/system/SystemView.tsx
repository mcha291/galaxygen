import { markSize } from "@interface/system.js";
import { paintOf } from "@interface/ramp.js";
import { codes } from "@interface/transport.js";
import { ArrowLeft } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import { type FieldDecl, type FieldsPayload, type Query, type StarName, type SystemFrame, loadSystem } from "../api";
import { Button } from "../ui/Button";
import { useLoad } from "../useLoad";
import { formatNumber, formatPower } from "../workflow/logic";
import { type RailMode, pickMark, railOf } from "./rail";
import styles from "./SystemView.module.css";

interface Props {
  star: StarName;
  query: Query;
  meta: FieldsPayload;
  onClose(): void;
}

// The planet columns in the order a reader wants them.
const PLANET_COLUMNS = [
  "planet_semi_major_axis", "planet_mass", "planet_radius", "planet_insolation", "planet_orbital_period",
  "planet_rotation_period", "planet_obliquity", "planet_volatile_fraction", "planet_atmosphere",
];

/**
 * One star's system, over the galaxy it was picked from. The galaxy stays
 * mounted underneath, so closing this returns to the same camera, the same
 * colouring and the same selection.
 */
export function SystemView({ star, query, meta, onClose }: Props) {
  const key = JSON.stringify([star, query]);
  const loaded = useLoad<SystemFrame>(key, (signal) => loadSystem(star, query, signal));
  const frame = loaded.value && loaded.value.header.cell === star.cell && loaded.value.header.index === star.index ? loaded.value : null;
  const [mode, setMode] = useState<RailMode>("log");
  const [planet, setPlanet] = useState<number | null>(null);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);
  useEffect(() => setPlanet(null), [key]);

  const byName = useMemo(() => new Map(meta.fields.map((f) => [f.name, f])), [meta]);
  const columns = useMemo(() => {
    if (!frame) return null;
    const out: Record<string, ArrayLike<number>> = {};
    for (const [name, values] of Object.entries(frame.arrays)) {
      out[name] = values instanceof BigInt64Array ? (codes(values) as Int32Array) : values;
    }
    return out;
  }, [frame]);

  return (
    <div className={styles.overlay} role="dialog" aria-label="Star system">
      <header className={styles.head}>
        <Button variant="ghost" icon={<ArrowLeft />} onClick={onClose}>
          Back to galaxy
        </Button>
        <span className="gx-label">
          System · cell {star.cell} · star {star.index}
        </span>
        {loaded.busy && <span className="gx-label">Materialising one cell</span>}
      </header>

      {loaded.error && <p className={styles.fault}>System failed: {loaded.error}</p>}
      {!frame && !loaded.error && <p className={styles.note}>Materialising this star's cell.</p>}

      {frame && columns && (
        <>
          <StarSummary star={frame.header.star} byName={byName} />
          <section className={styles.card}>
            <div className={styles.railHead}>
              <span className={styles.title}>
                {frame.header.planets} planets{frame.header.belts.length ? ` · ${frame.header.belts.map((b) => `${b.kind} belt`).join(", ")}` : " · no belts"}
              </span>
              <div className={styles.segmented} role="group" aria-label="Orbit scale">
                <button aria-pressed={mode === "log"} onClick={() => setMode("log")}>log distance</button>
                <button aria-pressed={mode === "schematic"} onClick={() => setMode("schematic")}>schematic</button>
              </div>
            </div>
            <OrbitRail
              mode={mode}
              columns={columns}
              belts={frame.header.belts}
              atmosphere={byName.get("planet_atmosphere")}
              cmaps={meta.cmaps}
              selected={planet}
              onPick={setPlanet}
            />
            <p className={styles.caption}>
              {mode === "log"
                ? "Distance from the star on a log axis, decades marked. Marker area follows planet radius; neither is to scale."
                : "Order kept, distance dropped: planets evenly spaced, belts between the planets that bound them."}{" "}
              Colour is atmosphere. Dashed bands are belts, derived from giant-planet resonances.
            </p>
          </section>
          <PlanetTable columns={columns} count={frame.header.planets} byName={byName} selected={planet} onPick={setPlanet} />
        </>
      )}
    </div>
  );
}

function valueOf(decl: FieldDecl | undefined, value: number | undefined): string {
  if (value === undefined || value === null || Number.isNaN(value)) return "—";
  if (decl && (decl.categories?.length ?? 0) > 0) return decl.categories![value] ?? String(value);
  return formatNumber(value, 3);
}

function unitOf(decl: FieldDecl | undefined): string {
  if (!decl || decl.unit === "dimensionless" || (decl.categories?.length ?? 0) > 0) return "";
  return String(decl.unit_display ?? decl.unit);
}

function StarSummary({ star, byName }: { star: Record<string, number>; byName: Map<string, FieldDecl> }) {
  // [α/Fe] is the advanced model's column; the simple model's stars carry none, and the row is left out.
  const shown = ["star_mass", "star_age", "star_metallicity", ...(star.star_alpha !== undefined ? ["star_alpha"] : []), "star_population", "star_height"];
  const moved = star.star_radius - star.star_birth_radius;
  return (
    <section className={styles.star}>
      <dl className={styles.facts}>
        {shown.map((name) => (
          <div key={name}>
            <dt>{byName.get(name)?.label ?? name}</dt>
            <dd>
              {valueOf(byName.get(name), star[name])} <span className={styles.unit}>{unitOf(byName.get(name))}</span>
            </dd>
          </div>
        ))}
      </dl>
      <div className={styles.migration}>
        <span className="gx-label">Radial migration</span>
        <MigrationStrip birth={star.star_birth_radius} now={star.star_radius} />
        <span className={styles.migrationText}>
          born at {formatNumber(star.star_birth_radius, 3)} kpc, now at {formatNumber(star.star_radius, 3)} kpc:{" "}
          {moved >= 0 ? "outward" : "inward"} by {formatNumber(Math.abs(moved), 3)} kpc
        </span>
      </div>
    </section>
  );
}

/** Birth radius and present radius on one 0–20 kpc line; the arrow is the migration. */
function MigrationStrip({ birth, now }: { birth: number; now: number }) {
  const max = Math.max(20, Math.ceil(Math.max(birth, now) / 5) * 5);
  const pct = (r: number) => `${(Math.min(Math.max(r, 0), max) / max) * 100}%`;
  const left = Math.min(birth, now);
  const right = Math.max(birth, now);
  return (
    <div className={styles.strip} aria-hidden>
      <div className={styles.span} style={{ left: pct(left), width: `calc(${pct(right)} - ${pct(left)})` }} />
      <div className={styles.birth} style={{ left: pct(birth) }} title="birth radius" />
      <div className={styles.now} style={{ left: pct(now) }} title="present radius" />
      <span className={styles.stripEnd}>0</span>
      <span className={styles.stripEnd} style={{ right: 0 }}>{max} kpc</span>
    </div>
  );
}

function OrbitRail({ mode, columns, belts, atmosphere, cmaps, selected, onPick }: {
  mode: RailMode;
  columns: Record<string, ArrayLike<number>>;
  belts: SystemFrame["header"]["belts"];
  atmosphere: FieldDecl | undefined;
  cmaps: FieldsPayload["cmaps"];
  selected: number | null;
  onPick(i: number | null): void;
}) {
  const box = useRef<HTMLDivElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const [width, setWidth] = useState(0);
  const HEIGHT = 120;
  const PAD_X = 36;

  useEffect(() => {
    const el = box.current;
    if (!el) return;
    const observer = new ResizeObserver(([e]) => setWidth(e.contentRect.width));
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const rail = useMemo(
    () => (width ? railOf(mode, columns, belts, { x: PAD_X, y: 0, width: width - PAD_X * 2, height: HEIGHT - 24 }, markSize) : null),
    [mode, columns, belts, width],
  );
  const palette = useMemo(() => (atmosphere ? (paintOf(atmosphere, cmaps, null) as { color(v: number): number[] }) : null), [atmosphere, cmaps]);

  useEffect(() => {
    const c = canvas.current;
    if (!c || !rail) return;
    const dpr = window.devicePixelRatio || 1;
    c.width = Math.round(width * dpr);
    c.height = Math.round(HEIGHT * dpr);
    const ctx = c.getContext("2d")!;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, width, HEIGHT);
    const probe = (token: string) => {
      c.style.color = `var(${token})`;
      return getComputedStyle(c).color;
    };
    const mono = getComputedStyle(c).getPropertyValue("--font-mono") || "monospace";
    const mid = (HEIGHT - 24) / 2;

    // Belts: derived, so dashed (the design system's "inferred").
    ctx.setLineDash([3, 3]);
    ctx.strokeStyle = probe("--text-muted");
    for (const b of rail.bands) {
      ctx.strokeRect(b.x0, mid - 16, Math.max(1, b.x1 - b.x0), 32);
    }
    ctx.setLineDash([]);

    ctx.strokeStyle = probe("--border-line");
    ctx.beginPath();
    ctx.moveTo(PAD_X, mid + 0.5);
    ctx.lineTo(width - PAD_X, mid + 0.5);
    ctx.stroke();

    ctx.font = `10px ${mono}`;
    ctx.fillStyle = probe("--text-muted");
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    for (const t of rail.ticks) {
      ctx.fillRect(Math.round(t.x), mid - 3, 1, 6);
      ctx.fillText(`${formatPower(t.a)} AU`, t.x, HEIGHT - 18);
    }

    // The star, at the rail's origin.
    ctx.fillStyle = probe("--spectral-g");
    ctx.beginPath();
    ctx.arc(PAD_X - 14, mid, 8, 0, Math.PI * 2);
    ctx.fill();

    const atm = columns.planet_atmosphere;
    for (const m of rail.marks) {
      const [r, g, b] = palette && atm ? palette.color(atm[m.index]) : [200, 200, 200];
      ctx.fillStyle = `rgb(${r} ${g} ${b})`;
      ctx.beginPath();
      ctx.arc(m.x, m.y, m.size, 0, Math.PI * 2);
      ctx.fill();
      if (m.index === selected) {
        ctx.strokeStyle = probe("--magenta-3");
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(m.x, m.y, m.size + 4, 0, Math.PI * 2);
        ctx.stroke();
        ctx.lineWidth = 1;
      }
    }
  }, [rail, width, palette, columns, selected]);

  return (
    <div
      ref={box}
      className={styles.rail}
      style={{ height: HEIGHT }}
      onClick={(e) => {
        if (!rail) return;
        const rect = box.current!.getBoundingClientRect();
        const i = pickMark(rail, e.clientX - rect.left, e.clientY - rect.top);
        onPick(i >= 0 ? i : null);
      }}
    >
      <canvas ref={canvas} />
    </div>
  );
}

function PlanetTable({ columns, count, byName, selected, onPick }: {
  columns: Record<string, ArrayLike<number>>;
  count: number;
  byName: Map<string, FieldDecl>;
  selected: number | null;
  onPick(i: number): void;
}) {
  const shown = PLANET_COLUMNS.filter((c) => columns[c]);
  const order = Array.from({ length: count }, (_, i) => i).sort(
    (i, j) => Number(columns.planet_semi_major_axis[i]) - Number(columns.planet_semi_major_axis[j]),
  );
  return (
    <div className={styles.tableWrap}>
      <table className={styles.table}>
        <thead>
          <tr>
            {shown.map((c) => (
              <th key={c} title={String(byName.get(c)?.about ?? c)}>
                {byName.get(c)?.label ?? c}
                <span className={styles.unit}>{unitOf(byName.get(c))}</span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {order.map((i) => (
            <tr key={i} aria-selected={i === selected} onClick={() => onPick(i)}>
              {shown.map((c) => (
                <td key={c}>{valueOf(byName.get(c), Number(columns[c][i]))}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
