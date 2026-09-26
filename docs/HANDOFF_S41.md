# HANDOFF — S41 (BUILD_II V4) built on Opus ahead of Fable's rulings

**Why this file exists.** S41 is an Opus row (board row 41), normally opened by the orchestrator (Fable) with a
BRIEF whose rulings are made before any number (D113). Fable's usage limit ran out during S40; the owner asked
Opus to do every task it can. So this row was built on **Opus 5.5** on `session-41`, **branched from the unmerged
`session-40`** (rows merge in order), **to rulings Opus proposed and wrote down first (§1)**. Fable ratifies or
overturns them in D191; nothing here is a decision until then. If S40 changes at its review, `session-41` is
rebased or merged onto the reviewed `session-40` before it is closed. Delete this file at S41's close.

## 1. Proposed rulings (written before the build; for Fable's ratification)

- **P1. Clusters as objects (BUILD_II V4: "cluster objects drawn as objects").** A cluster is drawn as a point of
  light at its position, as a star is, with its own light: two new columns on the `clusters` stage,
  `cluster_luminosity` (L☉, bolometric) = mass × the light per mass formed at the cluster's age and [Fe/H], and
  `cluster_light_temperature` (K) = the correlated colour temperature of the same population's colour — both from
  the tables the light stage integrates (`photometry.population_at`, `correlated_temperature`), never a star sample
  (B8). The alternative, a cluster's light through the filter set by `/api/render`, is V1's machinery at a finer
  grain and is left for later: a point's colour is the declared ramp of its temperature, as for stars (A9, D5).
  Its HII sphere and bubble shell are S40's region volume.
- **P2. Named-instrument PSFs are not built**: the filter curves are files (SVO), a download the owner has not
  approved (#108); the named-instrument mode waits on that word. Recorded, not guessed.
- **P3. The model toggle** (`azimuthal` against `basic`): exists since S27; V4's gate is that both models draw the
  field and the region regimes without error — checked in a browser on a scratch server.
- **P4. The tag batch** is the owner's (C2e: sessions do not tag); MANUAL_TODO carries every queued command.
- **P5. The #69 gate — every published field shown or ruled invisible** — extended from scalars to the object
  classes: a test lists every `of="cloud" | "cluster" | "remnant"` column and asserts each is either read by the
  viewer (the region volume's object table or the cluster points) or says in its about why it is not drawn
  (the D4 sentence's object-class twin). Columns the viewer does not read yet get that sentence, not a drawing
  invented to use them.

## 2. Built / 3. Gate / 4. What Fable owes — filled in as the build proceeds.
