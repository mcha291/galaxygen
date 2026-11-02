import type { CSSProperties, SVGAttributes } from "react";

/**
 * The stellar sprite (docs/design/stellar-icons-modernist.svg, the design's only ground-truth asset), served from
 * public/ under the app's base: one file, so every glyph is a <use> of it.
 */
export const SPRITE_URL = `${import.meta.env.BASE_URL}stellar-icons-modernist.svg`;

export type SpectralClass = "O" | "B" | "A" | "F" | "G" | "K" | "M" | "L" | "T" | "Y";

/** The spectral ramp, O (hottest) to Y (coolest): a data palette - glyph fills, series, legend keys - never chrome. */
export const SPECTRAL_COLORS: Readonly<Record<SpectralClass, string>> = {
  O: "var(--spectral-o)",
  B: "var(--spectral-b)",
  A: "var(--spectral-a)",
  F: "var(--spectral-f)",
  G: "var(--spectral-g)",
  K: "var(--spectral-k)",
  M: "var(--spectral-m)",
  L: "var(--spectral-l)",
  T: "var(--spectral-t)",
  Y: "var(--spectral-y)",
};

/** The body itself, sized by class (the sprite's `mo-core-*`). */
export const CORES = ["hyper", "super", "bgiant", "giant", "subgiant", "ms", "dwarf", "wd", "browndwarf", "proto", "ns", "bh"] as const;
export type Core = (typeof CORES)[number];

/** What is layered on the body (the sprite's `mo-mod-*`). */
export const MODIFIERS = ["companion", "companion2", "contact", "variable", "planets", "accretion", "jets", "beams", "magnetic", "flare", "nebulosity"] as const;
export type Modifier = (typeof MODIFIERS)[number];

/** What a glyph is made of. */
export interface Glyph {
  core?: Core;
  spectral?: SpectralClass;
  /** The luminosity arc round the body, 1-6. */
  luminosity?: 1 | 2 | 3 | 4 | 5 | 6;
  modifiers?: readonly Modifier[];
  /** The class letter knocked out of the disc (the sprite's `mo-cls-*`, where it carries them). */
  showClass?: boolean;
  /** The dotted reference-scale grid behind the glyph. */
  refGrid?: boolean;
  /** The size tick marks, 1-5. */
  sizeTick?: 1 | 2 | 3 | 4 | 5;
}

/** The sprite's symbol ids for a glyph, in the design's z-order: grid, luminosity arc, core, modifiers, class letter, size ticks. */
export function starLayers({ core = "ms", spectral = "G", luminosity, modifiers = [], showClass = true, refGrid = false, sizeTick }: Glyph): string[] {
  return [
    ...(refGrid ? ["ref-grid"] : []),
    ...(luminosity ? [`lum-${luminosity}`] : []),
    `core-${core}`,
    ...modifiers.map((m) => `mod-${m}`),
    ...(showClass ? [`cls-${spectral}`] : []),
    ...(sizeTick ? [`size-${sizeTick}`] : []),
  ].map((id) => `mo-${id}`);
}

interface Props extends Glyph, Omit<SVGAttributes<SVGSVGElement>, keyof Glyph> {
  /** px; 20 at least, 32 and over for a composed glyph. */
  size?: number;
  sprite?: string;
  /** The glyph's name; the class and the core say it otherwise ("G ms"). */
  title?: string;
}

/**
 * The design system's StarIcon: a stellar classification glyph composed of the sprite's layers, recoloured through
 * the sprite's three channels - `--sp` the spectral fill, `--ink` the annotation lines, `--bg` the knockout.
 */
export function StarIcon({ core = "ms", spectral = "G", luminosity, modifiers, showClass, refGrid, sizeTick, size = 32, sprite = SPRITE_URL, title, style, ...rest }: Props) {
  const channels = { "--sp": SPECTRAL_COLORS[spectral] ?? "var(--spectral-g)", "--ink": "var(--ink-2)", "--bg": "var(--void-0)" } as CSSProperties;
  const layers = starLayers({ core, spectral, luminosity, modifiers, showClass, refGrid, sizeTick });
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      role="img"
      aria-label={title ?? `${spectral} ${core}`}
      style={{ ...channels, display: "block", overflow: "visible", ...style }}
      {...rest}
    >
      {title && <title>{title}</title>}
      {layers.map((id) => (
        <use key={id} href={`${sprite}#${id}`} />
      ))}
    </svg>
  );
}
