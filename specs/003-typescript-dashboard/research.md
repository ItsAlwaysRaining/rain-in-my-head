# Research: TypeScript Dashboard

## 1. Where the numbers are computed

- **Decision**: move the data work out of each Streamlit view into plain functions in `src/listening/` (`overview.py`, then `genre.py`, `schema_info.py`). They take a pandas DataFrame or a `sqlite3.Connection` plus page inputs and return DataFrames and scalars. The Streamlit views call them and keep only widgets and Altair. The API calls the same functions and serialises the results to JSON.
- **Rationale**: constitution VI ("same numbers … MUST NOT be reimplemented"). [playlist.py](../../src/listening/playlist.py) already follows this pattern, so the Playlists page needs no extraction.
- **Alternatives**:
  - Compute in TypeScript from raw rows: two copies of the maths, ruled out by VI.
  - Run SQLite in the browser: the same problem, plus the whole 80 MB database would ship to the browser.

## 2. API server

- **Decision**: FastAPI 0.143 and uvicorn 0.54, in a new `web` dependency group. A new CLI command, `listening serve [--port 8000] [--dev]`, runs it. It also serves `web/dist/` as static files with an SPA fallback to `index.html`, so a single command runs the built app.
- **Rationale**: typed query parameters with validation and automatic 422 errors give the smallest correct API. `StreamingResponse` covers playlist progress over server-sent events (SSE).
- **Alternatives**:
  - `http.server` from the stdlib: no new dependency, but hand-written routing, parsing and validation.
  - Flask: similar size, but weaker query validation.

## 3. Caching

- **Decision**: cache the `v_plays` DataFrame per database mtime with `functools.lru_cache(maxsize=1)` keyed on `DB_PATH.stat().st_mtime`, the same key Streamlit's `st.cache_data` uses. Responses are not cached; aggregation over the cached frame is fast.
- **Measured**: loading `v_plays` (217,814 rows, about 49 MB in memory) takes 1.0 s. Overview aggregations on the cached frame are expected to take well under 0.5 s. This is verified in the quickstart against SC-004.

## 4. Frontend stack

- **Decision**: Vite 8, React 19, TypeScript, React Router 8 (paths `/`, `/genre`, `/sql`, `/schema`, `/playlists`) and TanStack Query 5 for fetching and caching per input.
- **Rationale**: these are the most widely used tools, with good TS support. The dev proxy (`/api` → `:8000`) keeps one origin and avoids CORS.
- **Alternatives**:
  - Svelte or Vue: equally capable, but React is the more transferable comparison point.
  - No framework: too much hand-rolled state for the Overview's linked inputs.

## 5. Charts

- **Decision**: Vega-Lite 6 via `vega-embed` 7, wrapped in one `<VegaChart spec onSelect>` component. Selections use Vega-Lite point params; the wrapper listens with `view.addSignalListener`.
- **Rationale**: the Altair specs are already Vega-Lite, so each chart ports nearly one to one. Click-to-select, nearest-point hit areas and conditional colour work the same way. Config (fonts, colours, axes) is ours, and any chart can be swapped for hand-written SVG later, which satisfies SC-006.
- **Alternatives**:
  - D3 or visx: the most control, but every axis and tooltip has to be rebuilt. That is better kept for later redesigns.
  - ECharts or Recharts: their own look to fight, and selection semantics that differ from Streamlit's.

## 6. Tables

- **Decision**: a small hand-written `<DataTable>` (sticky header, number formatting, progress-bar cells, image cells, whole-row click, optional sort). There is no table library.
- **Rationale**: the needs are modest, and full control over appearance is the point of the exercise. Building it is also a useful comparison data point, since Streamlit gives it for free.

## 7. Styling

- **Decision**: plain CSS with custom properties in `web/src/theme.css`, one token per palette entry in `.streamlit/config.toml`, plus the chart ramps from `overview.py`. CSS modules are used per component. No UI kit.
- **Rationale**: full control (FR-009) with no build-time styling dependency.

## 8. Dates and time zones

- **Decision**: the API takes and returns local calendar dates as `YYYY-MM-DD` and period starts as ISO local datetimes. All date arithmetic (presets, period bounds, previous period) happens in Python. The browser never does date maths with `Date`, so its time zone cannot shift a value.
- **Rationale**: `v_plays.played_local` is already local time. Doing the maths in one place keeps the two apps identical at month and DST edges.

## 9. Verifying the Streamlit refactor

- **Decision**: before the views change, a scratch script runs the current inline Overview code for a fixed set of inputs (presets × grains × a selected period) and writes the results to JSON. After the extraction, the same inputs run through the shared functions and must match exactly. A headless Chrome pass over Streamlit then confirms the page still renders and responds to clicks. The script stays out of the repo (constitution IV: test tools are ad hoc).

## 10. Browser verification

- **Decision**: Playwright run ad hoc (`uv run --no-project --with playwright python …`, `channel="chrome"`), the same as for spec 002. Scripts live in the scratchpad.

## 11. Node and lockfile

- **Decision**: `web/package.json` with caret ranges and a committed `package-lock.json`. Node 22+ is required (26 is installed). `node_modules/` and `web/dist/` are gitignored.
