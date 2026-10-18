# Streamlit vs. TypeScript

This project has two dashboards over the same `data/listening.db`:

- **Streamlit** (`dashboard/`): `uv run streamlit run dashboard/app.py` → http://localhost:8501
- **TypeScript** (`web/` + `src/rain_in_my_head/api.py`): `uv run rain-in-my-head serve` → http://localhost:8000

Both get their numbers from the same functions in `src/rain_in_my_head/`, so any difference you see is the UI, not the maths. This log records what building and changing each one was like, page by page, as the work happened (spec `specs/003-typescript-dashboard`).

## How to read this

- **Lines**: `wc -l` of the code written for that page. For Streamlit, the view in `dashboard/views/`. For TypeScript, the page, its chart builders and its API route. Shared data functions in `src/rain_in_my_head/` are counted once, separately, because both apps use them. Shared components, such as the table and chart wrapper, are counted in "Foundation".
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
| Genre | 146 → 105 | 291: page 165 + CSS 76 + API routes 50 | 83 (`genre.py`) | About a third of a session |
| SQL | 80 → 42 | 266: page 144 + CSS 91 + API routes 31 | 58 (`sql_examples.py`) | About a third of a session (shared with Genre) |
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

### Genre and SQL notes (slice 2)

**Easy in Streamlit**
- Clicking anywhere on a row to pick an artist is one argument: `selection_mode=["single-row", "single-cell"]`.
- Image columns, the expander, the select with a placeholder and `st.download_button` are all built in. The SQL page is 42 lines.
- `st.error(str(e))` is the whole error-handling story.

**Hard in Streamlit**
- The selected artist lives in the dataframe's widget state, so the key has to include the genre and range to reset it. It can't go in the URL.
- No keyboard shortcut to run a query; the button is the only way.

**Easy in TypeScript**
- The whole-row click and the selected-row highlight were already in `DataTable` from slice 1, so the Genre page was mostly layout.
- Cmd/Ctrl+Enter to run, a sortable result table and an explicit "None" for NULLs took a few lines each.
- The songs list is its own request, so picking an artist doesn't refetch the artist list.

**Hard in TypeScript**
- The CSV had to be rebuilt by hand to match pandas `to_csv`: quoting only fields that hold a comma, quote or newline, and writing NULL as empty. JSON also drops the `.0` from floats (`72.0` arrives as `72`), so the API now sends which columns are floats, and the page writes them back the pandas way. The CSV for a test query with commas, quotes, newlines, NULLs and whole-number floats is byte-identical to pandas.
- SQL result columns can repeat (`SELECT a, a`), so rows are keyed by position, not name.
- Lazy-loaded thumbnails look missing in a screenshot taken straight after load; Streamlit's canvas table doesn't do this.

**Shared**
- `genre.py` and `sql_examples.py` were moved, not rewritten. A scratch script ran the old view's functions (from `main`) and the new module over 6 genres × 3 ranges, and 51 artists' song lists: all identical. Every SQL example gives the same row count through the API as directly in SQLite.

## Same-change test

_Added after all pages are done: one identical small change made in both apps._

## Load times

_Time until each page's figures appear, both apps, same inputs._

| Page | Streamlit | TypeScript | Notes |
|---|---|---|---|
| Overview: open (warm server) | 0.32–0.50 s | 0.27 s | headless Chrome, same machine; until KPIs and first chart are on screen |
| Overview: click a month | 0.22 s | 0.21 s | until the caption shows the month |

With the data cached, the two are equally quick. Speed is not a reason to pick either one. The full table, measured the same way for every page, comes in slice 3.
