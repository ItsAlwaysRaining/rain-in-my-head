# Implementation Plan: TypeScript Dashboard

**Branch**: `feature/typescript-dashboard` | **Date**: 2026-10-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-typescript-dashboard/spec.md`

## Summary

Add a second dashboard in `web/` (Vite + React + TypeScript, Vega-Lite charts) next to the Streamlit one, reading a FastAPI JSON API in `src/listening/api.py` that `uv run listening serve` starts.

To guarantee identical numbers, the data work inside each Streamlit view moves into shared functions in `src/listening/`. Streamlit and the API both call them, and the Streamlit pages keep their widgets and look.

Delivery is in three slices, each one a PR:
1. Overview, plus the foundation
2. Genre and SQL
3. Schema and Playlists

`docs/streamlit-vs-typescript.md` logs the comparison as each page lands.

## Technical Context

- **Language/Version**:
  - Python 3.10+ (venv 3.12) with uv.
  - TypeScript 7 on Node 22+ (26 installed).
- **Primary Dependencies**:
  - New Python: FastAPI 0.143 and uvicorn 0.54, in a new `web` dependency group. The group also lists pandas, which the shared functions need.
  - New npm (`web/` only): react 19, react-dom, react-router 8, @tanstack/react-query 5, vega 6, vega-lite 6, vega-embed 7.
  - npm dev only: vite 8, @vitejs/plugin-react 6, typescript 7.
- **Storage**:
  - SQLite `data/listening.db`, read-only for every page except the Playlists match cache (unchanged behaviour).
  - `data/schema_layout.json`, shared by both apps.
- **Testing**:
  - No test suite in the repo; ad hoc tools only (constitution IV).
  - A golden-output scratch script guards the Streamlit refactor.
  - Playwright in headless Chrome is run ad hoc (`uv run --no-project --with playwright`) for both apps.
  - `tsc --noEmit` and `npm run build` must be clean.
  - SQLite cross-checks.
- **Target Platform**: local machine, desktop browser.
  - Streamlit runs on :8501.
  - The API and built app run on :8000; Vite dev runs on :5173.
- **Project Type**: Python package (CLI + shared data functions + API), a Streamlit app, and a web frontend.
- **Performance Goals**:
  - The Overview's figures appear within 2 s of opening and within 1 s after a period click (SC-004).
  - `v_plays` load is 1.0 s, cached per database mtime.
- **Constraints**:
  - No external calls on page load.
  - Read-only connections.
  - The Streamlit behaviour and numbers stay unchanged.
  - The sync keeps running with `--no-default-groups`.
- **Scale/Scope**:
  - About 218k plays.
  - 5 pages, 3 PRs, about 1,150 lines of Streamlit to match.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Checked against constitution 1.1.0 (PR #10). This branch is based on that PR.

| Principle | Check | Status |
|---|---|---|
| I. Raw scrobbles are the source of truth | No schema or raw-file change. The API opens read-only connections, except the existing Spotify match cache write | Pass |
| II. Spec first, small changes | This spec; branch `feature/typescript-dashboard`; three PRs, each with per-task commits | Pass |
| III. Verify in the real app | Quickstart drives both apps in headless Chrome and cross-checks KPIs against SQLite | Pass |
| IV. Few dependencies | FastAPI and uvicorn justified in research §2. npm packages stay in `web/` (research §4–5). The sync is unaffected (`--no-default-groups`). Playwright stays ad hoc | Pass |
| V. External APIs and secrets | No calls on load. Spotify is only contacted on Create. The token stays in `data/` and is never sent to the browser | Pass |
| VI. Consistent dashboards | Shared functions in `src/listening/` serve both apps. Palette tokens mirror `.streamlit/config.toml`. Same paths. Whole-row and whole-panel click targets. Every PR says which app it affects | Pass |
| Data and privacy | `web/dist`, `web/node_modules` gitignored; nothing new from `data/` committed | Pass |

Post-design re-check (after research, data model and contracts): all still pass. There are no Complexity Tracking entries.

## Project Structure

### Documentation (this feature)

```text
specs/003-typescript-dashboard/
├── spec.md
├── plan.md            # this file
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api.md         # JSON API and frontend routes
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
pyproject.toml               # + `web` group (fastapi, uvicorn, pandas); default-groups = ["dashboard", "web"]
.gitignore                   # + web/node_modules/, web/dist/
README.md                    # "Two dashboards" section
docs/streamlit-vs-typescript.md   # NEW: comparison log
src/listening/
├── cli.py                   # + `serve` command
├── api.py                   # NEW: FastAPI app, /api/* routes, static web/dist with SPA fallback
├── overview.py              # NEW (slice 1): load_plays, resolve_range, overview(...)
├── genre.py                 # NEW (slice 2): genres, genre_plays, ranked, songs
├── sql_examples.py          # NEW (slice 2): EXAMPLES, schema listing
└── schema_info.py           # NEW (slice 3): read_schema, layout load/save (moved from the view)
dashboard/views/             # Streamlit views now call the functions above; widgets/look unchanged
web/
├── package.json, package-lock.json, tsconfig.json, vite.config.ts, index.html
└── src/
    ├── main.tsx, App.tsx    # router, nav, error boundary
    ├── theme.css            # palette tokens
    ├── api.ts               # typed fetch helpers + response types (from contracts/api.md)
    ├── components/          # VegaChart, DataTable, Kpi, Tabs, SegmentedControl, Notice…
    ├── charts/              # Vega-Lite spec builders (overTime, topBar, heatmap, newArtists, genrePanel, buckets)
    └── pages/               # Overview.tsx, Genre.tsx, Sql.tsx, Schema.tsx, Playlists.tsx
```

**Structure Decision**: the frontend is a self-contained `web/` folder so that Node never touches the Python side. The API sits in the existing package so the CLI can start it. The shared functions sit beside `playlist.py`, which already works this way.

## Complexity Tracking

None.
