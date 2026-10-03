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

## The picture test (T12)

The Galaxy view captured at fixed cameras on headless Chromium and compared
with committed frames. A development instrument (BUILD_III section 7, rulings 6
and 10): Playwright is a dev dependency, nothing in `src/` or in the model
knows of it, and the pytest suite does not need a browser.

```
npm --prefix frontend run picture          # build, capture, compare with e2e/frames/*.png
npm --prefix frontend run picture:update   # build, capture, rewrite the frames and e2e/frames.json
GALAXYGEN_PICTURE=1 uv run pytest tests/test_picture.py   # the same comparison, from pytest
npm --prefix frontend exec -- playwright install chromium   # once per machine: the browser build
```

- **What is captured:** `e2e/captures.json` lists each picture: a camera
  (inclination from face-on, the azimuth it stands over, a framing radius in
  kpc), a mode (`field` or `stars`), a filter set and a square size. The frame
  is `e2e/frames/<name>.png`: the canvas as displayed, after the bloom and the
  tone curve, with none of the page over it.
- **How:** `e2e/picture.spec.ts` chooses the mode and the filters by the
  viewer's own buttons and uses two instruments on `window` (`GalaxyView.tsx`):
  `__galaxygenCapture` to place the camera and take the picture, and
  `__galaxygenFrameSum` to see the view has stopped changing. A view is ready
  when no `/api` request has run for 1.5 s, the frame's summed light is the same
  over three probes, the star-first mode has named its selection, and two
  pictures in a row are the same bytes.
- **The server** is the API serving `dist/` on **port 8019**
  (`playwright.config.ts`), started for the run and stopped after it; one
  already answering there is used and left alone. Ports 8017, 8018 and 5173 are
  never touched.
- **The renderer:** the browser runs with `--use-angle=d3d11`, which draws on
  the machine's GPU instead of on the CPU (SwiftShader). Each run prints
  WebGL's `UNMASKED_RENDERER` string and `e2e/frames.json` records the one each
  frame was drawn by. **Committed frames belong to that renderer.** On another
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
