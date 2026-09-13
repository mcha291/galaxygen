# Galaxy Design System

Galaxy is an observational-astronomy data platform. Its interfaces are instrument
consoles: dark, dense, monospaced where numbers live, and quiet everywhere else. The
house voice is a duty operator's — precise, declarative, unexcited. "Futuristic techno"
here means *machine readout*, not neon sci-fi: hairline rules, knockout glyphs, spectral
colour as data, and one magenta accent reserved for the thing you can act on.

## Sources given

- **Codebase**: one mounted read-only folder, `claude/`, containing a single file —
  `stellar-icons-modernist (1).svg`. Copied to `assets/icons/stellar-icons-modernist.svg`.
  This is the project's only ground-truth asset and the origin of the colour model.
- **Brand description**: "Galaxy". Additional note: "Futuristic techno tones."
- **No Figma file, GitHub repo, product screens, product copy, slide deck, logo, or font
  binaries were provided.** Everything below the icon sprite is authored, derived from the
  sprite's own conventions, and should be reviewed.

### Derived from the sprite (ground truth, not invented)

| Fact | Where it comes from |
| --- | --- |
| `#05070f` is the canvas colour | hardcoded knockout fill inside `mo-mod-contact` |
| Icons are recoloured via three CSS channels: `--sp`, `--ink`, `--bg` | every symbol references only these |
| 64×64 icon grid, 1px / 1.2px / 1.8px / 2.4px stroke tiers | symbol `viewBox` and `stroke-width` values |
| Dashed hairlines (`3 3`) mean *inferred / non-luminous*; `.9 4.2` round-dot dashes mean *reference scale* | `mo-core-hyper`, `mo-core-ns`, `mo-ref-grid` |
| Class letters are drawn in `--bg` *inside* the star disc (knockout, never outlined) | `mo-cls-*` |
| Spectral classes O→Y form an ordered ramp | `mo-cls-O … mo-cls-Y` |

### Substitutions flagged

- **Fonts.** No binaries supplied. Using **Space Grotesk** (display + UI) and **Azeret
  Mono** (data/telemetry) from Google Fonts as stand-ins — see `tokens/fonts.css`.
  *Please send real font files if Galaxy has them; swapping is a one-file change.*
- **Logo.** None supplied. Nothing was drawn. Wherever a mark belongs, the wordmark
  "Galaxy" is set in Space Grotesk Light at `--track-display` tracking. See `assets/README.md`.
- **UI icons.** The sprite covers stellar objects only, not interface glyphs (chevrons,
  search, close). **Lucide** is linked from CDN for those, chosen for its 1.5px-stroke,
  rounded-cap geometry — the closest common set to the sprite's hairline discipline.
  Flagged as a substitution; replace if Galaxy has a house UI set.

---

## Content fundamentals

**Voice: the duty operator.** Galaxy's copy reports state. It does not sell, reassure, or
celebrate. If a sentence could appear in a log line, it is on tone.

- **Sentence case everywhere** for headings, buttons, and labels. The single exception is
  the mono micro-label (`.gx-label`), which is UPPERCASE with `--track-label` tracking:
  `SPECTRAL CLASS`, `LAST SYNC`, `EPOCH`.
- **Person.** Default to no person at all — name the object, not the reader:
  "Survey queued", not "We've queued your survey" or "Your survey is queued". Use
  **you** only in a direct instruction: "Select a field to begin." Never **we**.
- **Tense.** Present for state, past for completed events. "3 fields offline." /
  "Calibration completed 04:12 UTC."
- **Numbers are never rounded away.** Show the precision the instrument has, with units
  always attached and always mono: `1,847 objects`, `0.42″ seeing`, `−26.74 mag`.
  Use a real minus sign (−) and a real prime (″).
- **No emoji. Ever.** Not in UI, not in docs, not in slides. Status is a coloured dot or
  a spectral glyph; there is always a typographic or iconographic equivalent.
- **No exclamation marks**, no "Oops", no "Uh oh". Errors state the fault and the next
  action: "Field 04 lost sync at 22:18 UTC. Retry ingest."
- **Empty states describe the gap, then the one action.** "No observations in this
  window." + `Widen range`.
- **Buttons are verbs, one or two words**: `Run query`, `Export CSV`, `Queue survey`,
  `Discard`. Never `Submit`, never `Click here`, never `Learn more`.
- **Length.** Labels ≤ 3 words. Body paragraphs ≤ 3 sentences. Tooltips one line.

Specimen copy, on tone:

> **Deep Field 07** — 1,847 catalogued objects · last ingest 04:12 UTC
> Two detectors report degraded gain. Photometry is usable; astrometry is not.
> `Review detectors`

Off tone, for contrast: *"Great news — your amazing deep field is ready to explore! 🚀"*

---

## Visual foundations

**Colour.** One canvas (`--void-0` #05070f) and a five-step void ramp for surfaces; a
five-step ink ramp for text. **Signal Magenta** (`--magenta-3` #ff6ba8) is the only
interactive colour — if something is magenta, you can press it or it is selected. Status
uses aqua (nominal), amber (caution), coral (fault), violet (archive). The **spectral
ramp** (`--spectral-o` → `--spectral-y`) is a data palette only: series colour, star
glyph fill, legend keys — never buttons, never chrome. Never more than two surface
colours in one view. No gradient fills anywhere except the protection scrim and the faint
field grid.

**Type.** Space Grotesk for everything human; Azeret Mono for everything measured. The
split is strict: a number a telescope produced is mono, a number a person wrote is not.
Display sizes run Light (300) with `-0.03em` tracking; headings Medium (500); body
Regular. Micro-labels are mono 10px uppercase at `0.14em`. Body line-height 1.5, display
1.05.

**Spacing & layout.** 4px grid, with a 2px step (`--space-1`) that exists only for dense
telemetry tables. Console layouts are three fixed columns — 56px icon rail, 264px
sidebar, 320px inspector — with one fluid centre. The rail and topbar are fixed; content
scrolls under them. Marketing and prose cap at `--content-max` 1280px / `--prose-max` 68ch.

**Backgrounds.** No photography in the system, and none was supplied. Canvases are
`--void-0` plus `--field-grid`: a 32px hairline grid at 4.5% opacity, the console's
graph-paper ground. Starfields, when needed, are rendered as real point data, not
decoration. Full-bleed imagery is reserved for future observation frames; when text sits
over any image, it gets `--scrim-bottom`, never a translucent capsule.

**Borders.** Hairlines carry the whole structure: `--border-hair` (12%) to separate,
`--border-line` (20%) to enclose, `--border-strong` (34%) to emphasise. A solid dash means
measured; `3 3` dashed means inferred, predicted, or offline — borrowed directly from the
sprite's own semantics.

**Corner radii.** Near-square. 5px (`--radius-md`) is the default for controls and cards,
3px for inputs, 2px for tags, 8px only for dialogs. `--radius-full` is for the status dot
and nothing else. No pills, no squircles.

**Cards.** `--surface-card` fill, 1px `--border-hair`, 5px radius, `--shadow-inset` top
highlight, no drop shadow. Elevation comes from the hairline and the inset, not from a
shadow; drop shadows (`--shadow-2`, `--shadow-3`) appear only on true overlays — popovers
and dialogs — where they read as depth of field, wide and near-black, never as paper lift.

**Transparency & blur.** Blur is used in exactly one situation: an overlay above live
data, where hiding the data entirely would hide state. Dialog backdrop is `--scrim`
(72% void) with `--blur-md`. Everything else is opaque. No frosted panels as decoration.

**Animation.** Machine motion: `cubic-bezier(.2,0,.2,1)`, 120–180ms, opacity and 2–4px
translation only. No bounce, no overshoot, no spring. Data updates cross-fade rather than
slide. The one long animation in the system is the 1200ms `--dur-sweep` radar/ingest
sweep, which is linear because instruments are. All motion respects
`prefers-reduced-motion`.

**Hover.** Surfaces lighten one void step (`--surface-hover`); text goes one ink step
brighter; borders go one border step stronger. Never opacity fades, never scale.
**Press.** Background darkens one step and the element translates 1px down — no scaling.
**Focus.** `--shadow-focus`: a 2px void gap then a 3px magenta ring, so it survives on
any surface. Focus is always visible; it is never removed.

**Disabled.** 40% opacity plus `cursor:not-allowed`, no colour change — the control stays
recognisable.

**Imagery vibe (for any future photography):** cool, near-monochrome, blue-black shadows,
no warm grade, slight grain acceptable. Spectral colour may be the only saturation in frame.

---

## Iconography

Two sets, with a hard boundary between them.

**1. Stellar sprite — `assets/icons/stellar-icons-modernist.svg`** (46 symbols, the
project's own asset). Not a flat icon list but a *composable classification system*: you
layer symbols in one `<svg>` to describe an object.

- `mo-core-*` (12) — the body itself, sized by class: `hyper`, `super`, `bgiant`,
  `giant`, `subgiant`, `ms`, `dwarf`, `wd`, `browndwarf`, `proto`, `ns`, `bh`.
- `mo-lum-1…6` — luminosity as an arc gauge around the body.
- `mo-mod-*` (11) — modifiers: `companion`, `companion2`, `contact`, `variable`,
  `planets`, `accretion`, `jets`, `beams`, `magnetic`, `flare`, `nebulosity`.
- `mo-cls-O…Y` (10) — the spectral-class letter, knocked out of the disc in `--bg`.
- `mo-ref-sun`, `mo-ref-grid` — reference scale rings.
- `mo-size-1…5` — size tick marks.

Colour is never baked in: set `--sp` (spectral fill), `--ink` (annotation lines) and
`--bg` (knockout) on any ancestor. Use the `StarIcon` component rather than hand-writing
`<use>` stacks. Render at 20px minimum; composed glyphs need 32px+ to read.

**2. UI glyphs — Lucide, from CDN** (`https://unpkg.com/lucide-static`). 1.5px stroke,
round caps, 24px grid, `currentColor`. Used for chrome only: navigation, search, close,
chevrons, table sort. Flagged substitution — no house UI set was supplied.

**Never:** emoji, unicode symbols as icons (no ▲ ✓ ★ in place of a glyph), or hand-drawn
one-off SVG. If a glyph is missing, add it to the sprite or take it from Lucide.

---

## Index

**Root**
- `styles.css` — the only file consumers link; `@import`s everything below.
- `readme.md` — this document. `SKILL.md` — portable Agent Skill wrapper.
- `thumbnail.html` — homepage tile.

**`tokens/`** — `fonts.css`, `colors.css`, `typography.css`, `spacing.css`,
`elevation.css`, `motion.css`, `base.css` (resets + `.gx-label`, `.gx-field` helpers).

**`guidelines/`** — foundation specimen cards (Colors, Type, Spacing, Motion, Brand groups
in the Design System tab).

**`assets/`** — `icons/stellar-icons-modernist.svg`, plus `assets/README.md` on the logo
absence.

**`components/`** — reusable primitives, each with `.jsx`, `.d.ts`, `.prompt.md`, and one
`@dsCard` HTML per directory.
- `core/` — `Button`, `IconButton`, `Badge`, `Tag`, `Card`, `Tabs`, `Tooltip`, `Dialog`
- `forms/` — `Input`, `Select`, `Checkbox`, `Switch`
- `data/` — `StarIcon`, `Readout`, `Meter`, `StatusDot`, `DataTable`

**`ui_kits/atlas/`** — Galaxy Atlas console recreation: `index.html` (interactive
click-through), `AtlasShell.jsx`, `CatalogScreen.jsx`, `ObjectScreen.jsx`,
`SurveyScreen.jsx`, `README.md`.

### Intentional additions

No source defined a component inventory (the only asset was an icon sprite), so the
standard primitive set was authored. Two additions beyond it, both required by the sprite:
- **`StarIcon`** — wrapper that composes `<use>` layers from the stellar sprite and sets
  the `--sp`/`--ink`/`--bg` channels. Without it, consumers hand-write `<use>` stacks and
  get the layer order wrong.
- **`StatusDot`** — the only `--radius-full` element in the system; codifies the status
  colour mapping so it is not re-derived per screen.

### Open questions for the Galaxy team

1. Real font files, or confirm the Space Grotesk / Azeret Mono stand-ins.
2. Is there a logo? Nothing was drawn deliberately.
3. Is there a house UI icon set, or is Lucide acceptable?
4. Is there a light theme, or is Galaxy dark-only? (Assumed dark-only.)
5. Any real product screens or copy to check the Atlas kit against.
