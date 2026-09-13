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
