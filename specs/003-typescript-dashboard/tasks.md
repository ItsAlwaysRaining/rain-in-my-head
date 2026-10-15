---

description: "Tasks for the TypeScript dashboard alongside Streamlit"
---

# Tasks: TypeScript Dashboard

**Input**: Design documents from `specs/003-typescript-dashboard/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md

**Tests**: no automated test suite was requested, and the repo has none. Per constitution III, each story ends with browser verification of both apps (quickstart.md) and a SQLite cross-check. The Streamlit refactor is guarded by a scratch golden-output script (research §9).

**Organization**: grouped by user story. User Story 4 (the comparison log) is spread across the slices: each slice adds the log entry for its pages.

**PR boundaries** (FR-014):
- PR 1 = Phases 1–4
- PR 2 = Phase 5
- PR 3 = Phases 6–7

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependencies)
- **[Story]**: user story from spec.md (US1–US4)

---

## Phase 1: Setup

- [x] T001 Add a `web` dependency group (`fastapi>=0.143`, `uvicorn>=0.54`, `pandas>=2.2`) and set `default-groups = ["dashboard", "web"]` in `pyproject.toml`; run `uv sync`; confirm `uv run --no-default-groups listening --help` still works without them
- [x] T002 [P] Add `web/node_modules/` and `web/dist/` to `.gitignore`
- [x] T003 [P] Scaffold `web/`: `package.json` (react 19, react-dom, react-router 8, @tanstack/react-query 5, vega 6, vega-lite 6, vega-embed 7; dev: vite 8, @vitejs/plugin-react 6, typescript 7, @types/react, @types/react-dom), `tsconfig.json` (strict), `vite.config.ts` (React plugin; dev proxy `/api` → `http://127.0.0.1:8000`), `index.html`, `src/main.tsx`; run `npm install` to create `package-lock.json`
- [x] T004 [P] Start `docs/streamlit-vs-typescript.md` with a "How to read this" intro and a table template: per page, the lines of the Streamlit view, the lines of the TS page + API route + shared function, the sessions spent, what was easy and what was hard in each

---

## Phase 2: Foundational (blocks all stories)

- [x] T005 Write the scratch golden script `$SCRATCH/golden_overview.py`. It copies the current inline computation from `dashboard/views/overview.py` (load, range presets, over_time, the selected period, KPIs, top lists, #1 per year, heatmap, new artists, genre shares, buckets, loved, coverage). It runs that for presets {Last 30 days, Last 12 months, This year, All time} × grains {Week, Month, Year}, plus one selected period per grain (the second-to-last bar), and writes canonical JSON to `$SCRATCH/golden_before.json`. Run it **before** touching the view
- [x] T006 Create `src/listening/api.py`:
  - a FastAPI `app` with `GET /api/health` (contracts/api.md)
  - a `no_database` 503 handler using the exact message from the contract
  - a mount for `web/dist` as static files with an SPA fallback to `index.html` for non-`/api` paths, and a plain-text hint when `web/dist` is missing
- [x] T007 Add a `serve` command to `src/listening/cli.py` (`--port`, default 8000; `--host`, default 127.0.0.1; `--dev` enables reload). It runs uvicorn on `listening.api:app` and imports uvicorn lazily so the sync install never needs it
- [x] T008 [P] Create `web/src/theme.css`: CSS custom properties for every colour in `.streamlit/config.toml` (page, surface, text, muted, line, iris, iris-strong, teal, coral, the info/success/warning tones) and the chart constants from `dashboard/views/overview.py` (`IRIS`, `TEAL`, the 10-step `IRIS_RAMP`, `IRIS_DIM`). Add base typography, spacing and radius tokens, and a dark `body` background
- [x] T009 [P] Create `web/src/api.ts`: a `getJson<T>(path, params)` helper that throws typed `ApiError` (`no_database`, `unreachable`, `http`) and TS types for every response shape in data-model.md
- [x] T010 [P] Create `web/src/components/VegaChart.tsx`. It renders a Vega-Lite spec with `vega-embed` (`actions: false`, renderer `svg`) and a shared dark config built from the theme tokens (`web/src/charts/config.ts`). It accepts `onSelect(signal, value)`, which uses `view.addSignalListener` for named point params, re-renders on spec change, and resizes to its container width
- [x] T011 [P] Create `web/src/components/DataTable.tsx`: columns with `kind` text, number (`toLocaleString`), percent, progress-bar (0–1), image (thumbnail) and datetime; a sticky header; a max height with scroll; an optional `onRowClick` covering the **whole row**; optional sort by clicking a header
- [x] T012 [P] Create the small UI components in `web/src/components/`:
  - `Kpi.tsx` (label, value, delta coloured teal or coral, help title)
  - `Tabs.tsx`
  - `SegmentedControl.tsx`
  - `Notice.tsx` (info, warning, error in the palette's tones)
  - `PageState.tsx`, which maps `ApiError` to the "run build" or "start the data service" notices (spec edge cases)
- [x] T013 Create `web/src/App.tsx`:
  - React Router routes `/`, `/genre`, `/sql`, `/schema`, `/playlists`
  - a sidebar nav in that order, with the same labels as Streamlit
  - placeholder pages that say "Coming in a later slice" for routes not yet built
  - a `QueryClientProvider`
  - an error boundary

**Checkpoint**: `uv run listening serve` plus `npm run dev` shows the nav and the health status. `npx tsc --noEmit` is clean.

---

## Phase 3: User Story 1 – Overview in the new dashboard (P1) 🎯 MVP

**Goal**: the new Overview shows the same figures as Streamlit's and meets the `dashboard-overview` living spec.

**Independent Test**: quickstart.md, Slice 1, steps 1–7.

### Shared data (both apps)

- [x] T014 [US1] Create `src/listening/overview.py` by moving the logic, not rewriting it, out of `dashboard/views/overview.py`:
  - **`load_plays(db_path)`**: the current `load`, cached per mtime with `functools.lru_cache(maxsize=1)` keyed on `(path, mtime)`.
  - **Constants**: `WEEKDAYS`, `FREQ`, `PERIOD_LENGTH`, `LISTENER_BUCKETS`, `LISTENER_LABELS` and `PRESETS`.
  - **`resolve_range(data, preset, start, end)`**: the preset → `(start, end)` logic, with `start` clamped to the first day.
  - **`over_time(data, start, end, grain)`**: returns `period` labels using the same `label_fmt`.
  - **`select_period(over_time, data, start, end, grain, period)`**: returns `(start, end, selected | None, inner_grain)`. A `period` that matches no bar is ignored.
  - **`previous_range(start, end)`** and **`kpis(df)`**.
  - **`top(df, field, n=20)`** and **`top_per_year(data)`**.
  - **`heatmap(df)`**: 7 × 24, including zeros.
  - **`new_artists(data, start, end, inner_grain)`** and **`new_share(df)`**.
  - **`genre_shares(df, inner_grain)`**: the top 6 genres plus `y_max`, or `None` if nothing is tagged.
  - **`listener_buckets(df)`**, **`loved(data, df)`** and **`coverage(df)`**.

  Pure functions only; no Streamlit import.
- [x] T015 [US1] Change `dashboard/views/overview.py` to call `listening.overview` for every computation. Keep every widget, chart spec, caption, key and layout as it is; `@st.cache_data load(db_mtime)` wraps `load_plays`. The view should then contain only UI code
- [x] T016 [US1] Run the golden comparison: a scratch script runs the same input grid through `listening.overview` and writes `$SCRATCH/golden_after.json`. `diff` it against `golden_before.json` and expect no differences. Then drive Streamlit on :8501 in headless Chrome:
  - change the preset and grain
  - click a month bar, then "Show whole range"
  - click a genre panel and confirm `/genre` opens with the range

### API

- [x] T017 [US1] Add `GET /api/overview` to `src/listening/api.py` per contracts/api.md:
  - **Validate inputs**: `preset` ∈ {`last30`,`last12m`,`ytd`,`all`,`custom`}, `grain` ∈ {`week`,`month`,`year`}, and `start`/`end` as dates when `preset=custom`.
  - **Build the response**: call the T014 functions in the same order as the view, and serialise DataFrames to records with dates as `YYYY-MM-DD` and datetimes as ISO local.
  - **Empty data**: return `{"empty": true, "reason": …}` for no scrobbles or no plays in range.
  - **Over-time series**: `over_time` covers the range **before** the period narrows it.
  - **"#1 per year"**: covers **all data**.
- [x] T018 [US1] Cross-check the API against SQLite with `curl '/api/overview?preset=last12m&grain=month'` and one `period`. Its KPI values must equal `sqlite3` counts (quickstart Slice 1, step 5), and the response must arrive within 1 s on a warm server

### Frontend

- [x] T019 [P] [US1] Create the chart spec builders in `web/src/charts/`, porting each Altair chart in `dashboard/views/overview.py` one to one:
  - **`overTime.ts`**: ordinal `period` x-axis, `paddingInner 0.2`, rounded top corners, a `pick` point param on `period` (click), colour `IRIS` when selected and `IRIS_DIM` otherwise, pointer cursor.
  - **`topBar.ts`**: horizontal bars, sorted by `-x`, height `max(200, 26·n)`, label limit 320.
  - **`heatmap.ts`**: rects stroked `#18181C` with width 2 and radius 2; `IRIS_RAMP` colour scale; weekdays in Mon–Sun order.
  - **`newArtists.ts`**: a teal line with points.
  - **`genrePanel.ts`**: an area with a 2 px iris line at opacity 0.35, a shared `y_max`, a `%` axis, and an invisible `nearest` point layer with a `pick` param, so a click anywhere in the panel selects.
  - **`buckets.ts`**: bars sorted by bucket order, with a `%` y-axis.
- [x] T020 [US1] Create `web/src/pages/Overview.tsx` with the inputs held in the URL (`preset`, `start`, `end`, `grain`, `period`, `measure`) and fetched with TanStack Query (`keepPreviousData`, so a click doesn't blank the page). Sections, in Streamlit's order:
  1. Sidebar filters: range presets as a radio group plus custom date inputs (min and max from the data), and the grain as a segmented control. Changing either clears `period`.
  2. Title and caption: `DD Mon YYYY – DD Mon YYYY · data through …`
  3. Five KPIs with deltas.
  4. Measure toggle and the over-time chart. A bar click sets `period`; a click on the background (a null signal) clears it.
  5. The "Click a bar…" caption, or "Showing X only…" with a "Show whole range" button.
  6. Top tabs: Artists, Tracks, Albums, "#1 per year" (a DataTable with a share progress column).
  7. "When you listen" heatmap and new artists, with the new-share caption.
  8. Genres: a 3-column grid of panels; a click navigates to `/genre?genre=…&start=…&end=…` using the **effective** range. The mainstream chart, or the "run enrich" notice.
  9. Loved tracks and data quality (a progress column), and the hours note.
- [x] T021 [US1] Overview edge cases in `web/src/pages/Overview.tsx`:
  - The API is unreachable: show the data-service notice.
  - `no_database`: show the build notice.
  - `empty`, reason `no_scrobbles`: show "The database has no scrobbles yet…".
  - `empty`, reason `no_plays_in_range`: show "No scrobbles in this range."
  - A `period` in the URL that is no longer valid is dropped silently, because the API returns `selected: null`.
- [x] T022 [US1] Browser verification on :8000 in headless Chrome (quickstart Slice 1, steps 3–4 and 6–7):
  - every `dashboard-overview` living-spec scenario
  - side-by-side parity with :8501 for "Last 12 months / Month" and for one selected month
  - the 2 s and 1 s timings
  - the three edge cases

  Record anything that differs and fix it before moving on.

---

## Phase 4: User Story 4 – Comparison log, slice 1 (P2)

- [x] T023 [US4] Fill in the Overview row and notes in `docs/streamlit-vs-typescript.md`:
  - line counts (`wc -l` of the view before and after, `listening/overview.py`, the API route, and `web/src` files used by the Overview)
  - sessions spent
  - what was easy and hard in each, including what Streamlit gave for free (tables, date input, caching, selection state) and what TS made possible
  - load timings from T022
- [x] T024 Add a "Two dashboards" section to `README.md` (how to run either app or both: build, serve, dev mode; that the numbers are shared). Note that the web group is installed by `uv sync`
- [x] T025 Open PR 1 (Overview), stating it affects **both** apps (the Streamlit Overview now calls shared functions; no behaviour change) and listing what was checked per constitution III. Base it on `main` once PR #10 is merged

**Checkpoint**: PR 1. The MVP is usable: both Overviews show the same numbers.

---

## Phase 5: User Story 2 – Genre and SQL pages (P2)

**Goal**: Genre and SQL pages in the new dashboard, matching Streamlit's.

**Independent Test**: quickstart.md, Slice 2.

- [ ] T026 [US2] Create `src/listening/genre.py` by moving `PLACEHOLDER`, `thumb`, `genres(conn)`, `genre_plays(conn, genre, start, end)`, `most_common` and `ranked` out of `dashboard/views/genre.py`. Add `songs(plays, artist_key)`, which returns the song table with each song's most common album
- [ ] T027 [US2] Change `dashboard/views/genre.py` to call `listening.genre`, with the UI unchanged. In headless Chrome, check that it shows the same artists and songs as before for one genre and range
- [ ] T028 [P] [US2] Create `src/listening/sql_examples.py` by moving `EXAMPLES` and the schema listing from `dashboard/views/sql.py`, plus a `run_readonly(db_path, sql) -> (columns, rows)` helper using `mode=ro`. Update `dashboard/views/sql.py` to use them
- [ ] T029 [US2] Add `GET /api/genre`, `GET /api/genre/songs`, `GET /api/sql/meta` and `POST /api/sql` to `src/listening/api.py` per contracts/api.md. SQL errors are returned as `{error}`. The default genre is the most-played one, and the default range is all time, with the label "All time"
- [ ] T030 [P] [US2] Create `web/src/pages/Genre.tsx`:
  - a back link to the Overview and a genre select that updates `?genre=`
  - a title and caption (range label · plays · "artists whose top Last.fm tag is …")
  - the artists table with thumbnails; a click **anywhere on a row** selects the artist
  - the selected artist's header image (174s), name and plays, and the songs table with album and thumbnails
  - the "Click an artist on the left." notice when no artist is selected
- [ ] T031 [P] [US2] Create `web/src/pages/Sql.tsx`:
  - a collapsible "Tables and columns" list
  - an examples select that loads the example into the editor
  - a query textarea with a monospace font, and a Run button (Cmd/Ctrl+Enter also runs)
  - the row count and result table, or the error notice
  - a client-side "Download CSV" that builds the CSV the way pandas `to_csv` does: header row, comma-separated, quoting fields that contain `,` `"` or a newline
- [ ] T032 [US2] Browser verification (quickstart Slice 2) on both apps: the same genre and range give identical lists; every SQL example gives equal row counts; `DELETE` is refused; the CSV matches
- [ ] T033 [US4] Add the Genre and SQL entries to `docs/streamlit-vs-typescript.md`, then open PR 2, stating that it affects both apps

---

## Phase 6: User Story 3 – Schema and Playlists pages (P3)

**Goal**: Schema and Playlists in the new dashboard; both apps share the schema layout.

**Independent Test**: quickstart.md, Slice 3.

- [ ] T034 [US3] Create `src/listening/schema_info.py`. Move `read_schema`, the layout load, save and reset logic, `MAP_W`, `MAP_H`, `CARD_W`, `GRID_X` and the default-position placement out of `dashboard/views/schema.py`. Move `dashboard/schema_notes.py` to `src/listening/schema_notes.py`, keeping a re-export at the old path if anything else imports it. Update the view to use the new module and confirm the Streamlit Schema page behaves as before (spec 002 quickstart)
- [ ] T035 [US3] Add `GET /api/schema`, `PUT /api/schema/layout` (atomic write, 204) and `DELETE /api/schema/layout` to `src/listening/api.py`
- [ ] T036 [US3] Create `web/src/pages/Schema.tsx` and `web/src/pages/schema/` by porting `dashboard/schema_map/map.js` and `map.css` to TypeScript and React:
  - cards dragged by the whole header, and moved with the arrow keys (20 px, or 80 px with Shift)
  - link lines with labels; highlighting on hover or focus
  - the "Show how views are built" toggle
  - zoom, and fit to screen on open
  - "Reset layout" with an on-page confirmation
  - the layout saved on drag end via `PUT`
- [ ] T037 [US3] Add the Playlists endpoints to `src/listening/api.py`:
  - `GET /api/playlists/meta` and `GET /api/playlists/spotify`
  - `POST /api/playlists/preview`, which builds the same `Spec` as `dashboard/views/playlists.py`. Move the `time_slot`, `year_discoveries` and `binged` assembly, minus its widgets, into `src/listening/playlist.py` as `preview_slot`, `preview_discoveries` and `preview_binges`, so the Streamlit view and the API share it. Update the view to use them
  - `POST /api/playlists/create` as server-sent events, running `match_tracks` with a progress callback that yields `progress` events and then `done` or `error`
- [ ] T038 [US3] Create `web/src/pages/Playlists.tsx`:
  - the "Playlist type" segmented control
  - one form per type with the same controls, defaults and help text as Streamlit: days multi-select, hour range, span radio and custom dates, length and minimum-plays sliders, year select, rank-by and order radios, years range, window radio, binge order
  - the same warnings and info notices
  - the preview table and candidate caption
  - the "Create on Spotify" section: the connect instructions when no token is present; otherwise a name input, a public toggle, and a Create button, then a progress bar, then a success link, then an expandable list of misses
- [ ] T039 [US3] Browser verification (quickstart Slice 3):
  - spec 002 scenarios on :8000
  - layout shared across both apps
  - the same time-slot, discoveries and binges previews in both apps
  - one real private playlist created from :8000
- [ ] T040 [US4] Add the Schema and Playlists entries to `docs/streamlit-vs-typescript.md`

---

## Phase 7: Polish & cross-cutting

- [ ] T041 [US4] Same-change test (spec US4 scenario 2): add one identical small feature to both apps (for example a "Days listened" KPI, with the computation in `listening.overview`). Record the time taken and the files touched for each in `docs/streamlit-vs-typescript.md`
- [ ] T042 [US4] Record side-by-side load timings for every page (spec US4 scenario 3) in `docs/streamlit-vs-typescript.md`
- [ ] T043 Final pass:
  - `npx tsc --noEmit` and `npm run build` are clean
  - `uv run --no-default-groups listening --help` still works
  - the README is up to date
  - open PR 3, stating it affects both apps

---

## Dependencies & execution order

- Setup (T001–T004) → Foundational (T005–T013) → US1 (T014–T022) → US4 slice 1 (T023–T025): **PR 1**.
- T005 must run before T014 and T015, because the golden output must come from the untouched view.
- US2 (T026–T033) depends only on Foundational, but ships after PR 1 so the PRs stay small.
- US3 (T034–T040) depends only on Foundational.
- Polish (T041–T043) comes after all stories.

## Parallel opportunities

- Setup: T002, T003 and T004 together.
- Foundational: T008–T012 together after T003; T006 and T007 alongside them.
- US1: T019 (chart builders) can proceed alongside T014–T018.
- US2: T028, T030 and T031 are in separate files.

## Implementation strategy

MVP is US1 (PR 1): both Overviews with identical numbers, and the comparison log started. Each later PR adds pages without changing earlier ones. Visual redesign of the TS pages is out of scope for these tasks; it happens afterwards, one page at a time, with each redesign noted in the log (spec Assumptions).
