# galaxygen frontend

Vite + React + TypeScript, three.js through react-three-fiber. The design
export from Claude Design is in `docs/design/` (reference only: not built, not
tested).

```
uv run python -m galaxy.api      # from the repo root: the API on 127.0.0.1:8017
npm --prefix frontend install
npm --prefix frontend run dev    # http://localhost:5173, /api proxied to 8017
npm --prefix frontend test       # vitest
npm --prefix frontend run build  # tsc + vite build into frontend/dist
```

- **Network:** no request code lives here. `src/api.ts` calls
  `interface/transport.js`, the project's one `fetch` (rule D2), through the
  `@interface` alias.
- **Colour:** every ramp and palette comes from `/api/fields` through
  `interface/ramp.js` (rule A9). `src/galaxy/colors.ts` converts them to linear
  light for WebGL.
- **Styling:** `src/styles/tokens/` is the design system's tokens copied
  verbatim; components use CSS Modules with `var(--...)`. Fonts are self-hosted
  via `@fontsource`.
- **`.npmrc`** sets `legacy-peer-deps`: react-three-fiber lists React Native
  and Expo as optional peers, which npm 11 fails to resolve for a web-only app.

## Templates (S54, D213)

The viewer lands on the Galaxy view of the default template and carries a
switcher (rule D1 as amended). Nothing about a template lives here: its
inputs, camera, lens and filter set come from `/api/templates` (rule D5).

- **Landing and switching:** `workflow/useWorkflow.ts` asks for the templates,
  then for the template's model, and lays the template's inputs on a fresh flow
  through `interface/flow.js` (`workflow/templates.ts`), every checkpoint
  confirmed. Choosing a template in the Galaxy panel is the same landing again.
  The query sent to every route stays the whole input vector, so "Edit galaxy"
  opens the staged process at the template's values with the confirmations
  kept, and a changed control is one changed value. An edited galaxy is no
  longer the template: its button is released and reads "<label> · edited",
  the top bar says the same, and choosing it again restores the template.
- **An older API:** one without `/api/templates` answers 404, and the viewer
  then lands as it did before - the default galaxy at the published defaults,
  the 45 degree lens, no switcher (`readTemplates`).
- **The camera and the lens:** a template states an inclination, an azimuth, a
  framing radius and a vertical field of view (`galaxy/capture.ts`). The view
  stands there until a preset is pressed ("template" beside face-on, edge-on,
  oblique) and keeps the template's lens under a preset. Every distance written
  for the 45 degree lens - the presets' stand, the zoom's range, the near and
  far planes - is carried to the lens by `lensScale` (`galaxy/zoom.ts`), so a
  view is the same number of kiloparsecs across through any lens. The march
  and the star-first mode's points read the camera itself and needed nothing.
- **Thumbnails:** `public/templates/<name>.png`, each a capture of the picture
  test's own (below), so one cannot go stale silently.
- **Compare with a picture (T16 ii):** a button in the Galaxy panel picks an
  image file from disk and sets it beside the render at the same height, the
  render captioned with the template, the filter set, kiloparsecs per pixel at
  the centre (and arcseconds, at the template's distance) and the inclination.
  The file is shown through an object URL: it never leaves the browser, and no
  picture is bundled.

## Physics only (S55, D214)

The viewer's half of invariant I5: a switch in the Galaxy panel, under
"Rendering", off by default. On, the galaxy is drawn from the physics model
alone - `layer=off` on every request the Galaxy view makes for model data.

- **One place adds it:** `galaxy/layer.ts` `layerQuery`, called once, in
  `App.tsx`. The result is the query the star sample and the Galaxy tab take,
  and every loader below spreads the query it is given, so a loader added
  later sends the switch without knowing of it. With the switch off the
  workflow's own query is passed on untouched: no `layer` parameter at all.
- **One place checks the answer:** every binary route in `api.ts` is called
  through `route`, which holds the header's echoed `layer` to the one asked
  for. A frame made under the other setting (an API from before S55 echoes
  nothing) is refused - thrown, so it is not drawn (`useLoad` drops what it
  showed before), and reported, so the page says so and offers the way back.
- **Display state, not an input:** it is no part of the workflow's query. The
  run hash is the input vector's and does not move; the top bar adds
  "· physics only" after it while the Galaxy tab is drawn that way. A template
  is not "edited" by it, and "Edit galaxy" keeps it. **The staged Preview and
  the Science tab do not follow it**: they show the model as it is generated,
  with the layer.
- **The cloud interior** (`galaxy/region.ts`, rule D5 as amended): the noise's
  octave count, lacunarity and gain are read from `/api/clouds`' header
  (`cloud_interior_octaves`, `_lacunarity`, `_gain`) with the census they
  belong to, and written into the march's shader from there. The viewer keeps
  one measured number, the summed octaves' standard deviation, with the
  parameter set it was measured for; a census that publishes another set, or
  none, is drawn smooth and the page says why. With the layer off the
  interior is smooth: each cloud its published mass in its published radius.

## The picture test (T12)

The Galaxy view of each template, captured on headless Chromium and compared
with committed pictures. A development instrument (BUILD_III section 7, rulings 6
and 10): Playwright is a dev dependency, nothing in `src/` or in the model
knows of it, and the pytest suite does not need a browser.

```
npm --prefix frontend run picture          # build, capture, compare with the committed pictures
npm --prefix frontend run picture:update   # build, capture, rewrite the pictures and e2e/frames.json
GALAXYGEN_PICTURE=1 uv run pytest tests/test_picture.py   # the same comparison, from pytest
npm --prefix frontend exec -- playwright install chromium   # once per machine: the browser build
```

- **What is captured:** `e2e/captures.json` lists each picture: a template, a
  mode (`field` or `stars`), a square size and the file it is committed as,
  with the template's camera, lens and filter set stated beside it. Each
  template is taken in both modes at 1024 px - `e2e/frames/<name>.png` - and
  once at 256 px in the field mode: its thumbnail,
  `public/templates/<template>.png`, a render of its own size and not a frame
  scaled down. A picture is the canvas as displayed, after the bloom and the
  tone curve, with none of the page over it.
- **The layer off (S55):** one more frame, `milky_way-physics-only`, is
  `milky_way-field`'s view with the "physics only" switch pressed (the list's
  `layer: "off"`; every other entry omits the key). The test presses the real
  control, holds every request made after it to `layer=off`, then releases it
  and compares the two frames' summed linear light: the model conserves each
  ring's totals, so the sums agree to a quarter of a percent (the frame's edge
  and the dust account for the rest: `e2e/settings.ts` `LAYER_SUM_TOLERANCE`).
  A last test, not a capture, walks both modes and a region under the switch
  and holds every request for model data to `layer=off`.
- **How:** `e2e/picture.spec.ts` chooses the template in the viewer's switcher
  and the mode by its button, as a user would, and uses two instruments on
  `window` (`GalaxyView.tsx`): `__galaxygenCapture`, whose `where()` reads the
  camera's stand and lens back and whose `picture()` takes the picture, and
  `__galaxygenFrameSum` to see the view has stopped changing. The stand, the
  lens and the pressed filter set must be the ones the list states, and the
  list's must be `/api/templates`' own: a camera that moves in the model fails
  by name. A view is ready when no `/api` request has run for 1.5 s, the
  frame's summed light is the same over three probes, the star-first mode has
  named its selection, and two pictures in a row are the same bytes.
- **Against an API without templates** the default template's captures can
  still be taken (its inputs are the published defaults): the test places the
  camera, the lens and the filters itself through `__galaxygenCapture.place`.
  A capture marked `pending` in the list is skipped until the API serves its
  template; `tests/test_picture.py` refuses the mark once it does.
- **The server** is the API serving `dist/` on **port 8019**
  (`playwright.config.ts`), started for the run and stopped after it; one
  already answering there is used and left alone. Ports 8017, 8018 and 5173 are
  never touched.
- **The renderer:** the browser runs with `--use-angle=d3d11`, which draws on
  the machine's GPU instead of on the CPU (SwiftShader). Each run prints
  WebGL's `UNMASKED_RENDERER` string and `e2e/frames.json` records the one each
  picture was drawn by. **Committed pictures belong to that renderer.** On another
  machine or after a driver change, run `picture:update` and compare locally:
  a frame from one renderer is not a gate on another. Measured at S53 on two
  of the captures, SwiftShader against the RTX 4070: a quarter of the pixels
  differ by 1/255, and 0.09 % (face-on, field) and 0.16 % (inclined, stars) by
  more than 2/255 - at the tolerance below, one on each side of it. Four
  captures take about 30 s on the GPU (4-10 s each) and 13-29 s each on
  SwiftShader.
- **The tolerance** (`e2e/settings.ts`): a pixel is different beyond 0.01 of
  pixelmatch's colour distance (about 2/255 in every channel) and a frame fails
  beyond 0.1 % of its pixels. Measured at S53: a capture run again is the same
  file byte for byte, and a field gain of 1.25 for 1 moves 54-67 % of the
  pixels.
- **Versions:** `@playwright/test` is pinned to one exact version because each
  names one Chromium build (1.62.1: build 1234, Chromium 151.0.7922.34).
  `npm run typecheck:e2e` type-checks the spec and the config; vitest takes
  `src/**/*.test.ts` and Playwright `e2e/**/*.spec.ts`.
