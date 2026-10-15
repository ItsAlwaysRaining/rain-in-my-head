# Streamlit vs. TypeScript

This project has two dashboards over the same `data/listening.db`:

- **Streamlit** (`dashboard/`): `uv run streamlit run dashboard/app.py` → http://localhost:8501
- **TypeScript** (`web/` + `src/listening/api.py`): `uv run listening serve` → http://localhost:8000

Both get their numbers from the same functions in `src/listening/`, so any difference you see is the UI, not the maths. This log records what building and changing each one was like, page by page, as the work happened (spec `specs/003-typescript-dashboard`).

## How to read this

- **Lines**: `wc -l` of the code written for that page. For Streamlit, the view in `dashboard/views/`. For TypeScript, the page, its chart builders and its API route. Shared data functions in `src/listening/` are counted once, separately, because both apps use them. Shared components, such as the table and chart wrapper, are counted in "Foundation".
- **Effort**: working sessions, with notes. Not exact hours.
- **Easy / hard**: what each approach made simple or difficult for that page.

## Foundation

| | Streamlit | TypeScript |
|---|---|---|
| Lines | 12 (`dashboard/app.py`) + 46 theme lines in `.streamlit/config.toml` | 953 in `web/` (shell and menu, theme tokens, typed API client, chart wrapper, table, KPI, tabs, radios, notices, build config) + 89 in `api.py` (app, errors, JSON helpers, serving the built app) |
| Effort | Already existed | About half a session |

Streamlit gives you the menu, layout, theme, widgets, tables, caching and the "is the server up" handling for free. In TypeScript each of those was a file to write, but each one is now ours to change.

## Pages

| Page | Streamlit lines | TS lines (page + charts + API route) | Shared function lines | Effort (TS) |
|---|---|---|---|---|
| Overview | 356 → 245 (data work moved out; widgets and charts only) | 592: page 284 + CSS 100 + chart specs 137 + API route 71 | 227 (`listening/overview.py`) | About 1 session |
| Genre | | | | |
| SQL | | | | |
| Schema | | | | |
| Playlists | | | | |

### Overview notes (slice 1)

**Easy in Streamlit**
- Selection state. `on_select="rerun"` plus a widget key gives the clicked bar back on the next run.
- Tables with progress bars come from `st.dataframe` + `column_config`, at about 5 lines each.
- Range presets and the date picker are built-in widgets.

**Hard in Streamlit**
- Layout is fixed: sidebar, a single column and `st.columns`. You can't place a caption next to a chart, control spacing, or style a KPI.
- The page reruns top to bottom on every click, so state has to be threaded through `st.session_state` keys. "Show whole range" works by changing the chart's key. It is still fast, because the data is cached; see Load times.

**Easy in TypeScript**
- The Altair specs ported almost line for line to Vega-Lite (`charts/overview.ts`), including click-to-select.
- All state is in the URL (`?preset=…&grain=…&period=…`), so every view can be bookmarked, and the back button steps through selections.
- A period click refetches only the JSON and keeps the old figures dimmed meanwhile. It is no faster than Streamlit's rerun, though (see Load times).
- Full control over the look: every colour, gap and font is in `theme.css` or a CSS module.

**Hard in TypeScript**
- About 950 lines of foundation before the first chart appeared: things Streamlit simply has.
- Dates. A bare `"2026-03-01"` is read as UTC midnight by the browser and can display as the day before, so the API sends local dates and the charts read them as local time (`localDates`). Streamlit never surfaced this.
- Dev-mode plumbing: two servers (API + Vite) and a proxy. A stale uvicorn reloader held port 8000 during testing and made requests hang.

**Shared**
- Moving the maths into `listening/overview.py` was mechanical. A golden comparison of 24 input combinations was byte-identical before and after, so both apps provably show the same numbers.

## Same-change test

_Added after all pages are done: one identical small change made in both apps._

## Load times

_Time until each page's figures appear, both apps, same inputs._

| Page | Streamlit | TypeScript | Notes |
|---|---|---|---|
| Overview: open (warm server) | 0.32–0.50 s | 0.27 s | headless Chrome, same machine; until KPIs and first chart are on screen |
| Overview: click a month | 0.22 s | 0.21 s | until the caption shows the month |

With the data cached, the two are equally quick. Speed is not a reason to pick either one. The full table, measured the same way for every page, comes in slice 3.
