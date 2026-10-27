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
| Schema | 181 → 64 (plus the 322-line `map.js` and 97-line `map.css` component) | 539: page 62 + map port 340 + map CSS 97 + API routes 40 | 138 (`schema_info.py`) + the notes, moved | About a third of a session |
| Playlists | 224 → 143 | 659: page 314 + CSS 114 + API routes 140 + form controls 91 (`Form.tsx`, CSS 108 more) | 141 added to `playlist.py` (the preview builders) | About half a session |
| Artist + new-artists list (spec 001) | 104: page 67 + Overview table 35 + menu entry 2 | 237: page 88 + CSS 43 + Overview table 28 + route 3 + API client 44 + API routes 31 | 113 (`artist.py`) | Built in both apps in the same session |

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

### Schema and Playlists notes (slice 3)

**Easy in Streamlit**
- Every Playlists control is one line: `st.multiselect`, a two-thumb `st.slider`, `st.date_input` for a range, `st.toggle`, `st.progress`. The TypeScript app needed a new `Form.tsx` for the slider, range slider and day chips.
- `st.stop()` after a warning. It is the simplest way to say "nothing more to show".
- Progress during Spotify matching is a callback that updates a widget, in the same process.

**Hard in Streamlit**
- The Schema map already had to leave Streamlit: it is a custom component (`map.js`, `map.css`) living in a shadow root, with a trigger to send the layout back to Python. Of the five pages, it was the one Streamlit couldn't do on its own.
- The preview logic was tangled with the widgets (each form function both drew controls and computed the playlist), so it couldn't be reused without first being pulled apart.

**Easy in TypeScript**
- The Schema map was already plain DOM code, so the port was mostly adding types. The same file now runs as a normal module, with no component bridge and no rerun to survive. Saving is a `PUT`, and the status shows the server's answer.
- The form's state for each playlist type is kept while switching types; Streamlit forgets it.
- Previews refetch 250 ms after the last change, so dragging a slider doesn't fire a query per step.

**Hard in TypeScript**
- Server-sent events over `POST`: `EventSource` only does `GET`, so the client reads the stream by hand and parses `event:`/`data:` blocks. On the server, `match_tracks` reports progress through a callback, so it runs in a thread that feeds a queue the response streams from.
- A range slider is two `<input type="range">` stacked, with CSS so only the thumbs take the pointer.
- `map.css` used `:host` (shadow DOM). In the app it is regenerated with every selector scoped to `.schema-map`, so its generic class names (`.card`, `.bar`) can't leak into other pages.

**Shared**
- The preview builders (`preview_slot`, `preview_discoveries`, `preview_binges`) were checked against the old view: a scratch script ran the old view's code with a stub Streamlit for 141 form settings (days, hours including past midnight, spans, years, orders, windows, minimum plays), and every playlist, preview, name, description, warning and note was identical.
- The layout file is shared: a card moved in either app shows up in the other, and "Reset layout" in one resets both.

### New artists and the Artist page (spec 001)

The first feature built for both apps at once, after they were side by side.

**Easy in Streamlit**
- A hidden page is one `st.Page(..., visibility="hidden")`, and `st.switch_page(..., query_params=...)` opens it with its address.
- Leaving the Overview drops the table's selection, so coming back doesn't jump straight to the artist again.

**Hard in Streamlit**
- Image columns need a URL, so the shared placeholder SVG is read from `web/public/` and passed as a `data:` URL.
- The table is a canvas: clicking a row in a browser test means computing its position, and its cells can't be read back from the page.

**Easy in TypeScript**
- The page was mostly the Genre page's artist panel, reused: same `DataTable`, same back link, same header layout.
- `onRowClick` on the shared table already makes the whole row the target, and the placeholder is just `/no-art.svg`.

**Hard in TypeScript**
- More files for the same thing: the API route and its types on both sides of the wire, a route, a CSS module.

**Shared**
- `rain_in_my_head.artist` reuses the Genre page's ranking helpers, so the list, the page and the Genre page pick names, art and counts the same way. Its results were checked against direct SQLite queries for three periods, with no differences.

### Prototype redesign (spec 005, TypeScript only)

The TypeScript app was restyled to match the Figma Prototype page. Streamlit is unchanged, so from here on the two apps no longer look alike. They still show the same numbers.

**Where they now differ**
- Addresses: TypeScript has `/` (a placeholder home), `/dashboards`, `/dashboards/new-artists`, `/dashboards/genre`, `/dashboards/artist`, `/playlists` and `/analyst`. Streamlit keeps `/`, `/genre`, `/artist`, `/sql`, `/schema` and `/playlists`. The old TypeScript addresses redirect. This is the deviation from constitution VI recorded in the spec's plan.
- Navigation: a top bar and breadcrumbs instead of a sidebar. The Overview's filters are chips on the page.
- Overview: no Loved tracks section. The six genre panels are one multi-line chart with a chip legend, using three extra colours (plum, moss, ember) that only TypeScript has. New artists is its own page with a month picker, instead of a table on the Overview.
- SQL and Schema are one Analyst page. Its schema map replaces the Tables and columns expander.
- Type: Fredoka, Lexend and Red Hat Mono, loaded from Google Fonts. Streamlit keeps Source Sans (issue #22 is still open for both).

**Easy in TypeScript**
- The whole shell (top bar, breadcrumbs, redirects) is one `routes.ts` table and about 100 lines in `App.tsx`.
- The new pages reuse the API as is. New artists calls `/api/overview` over all time by month, which already returns both the months and the list.

**Landing page (spec 006, TypeScript only)**
- The Rain Girl artwork is the Figma export, unmodified. It's inlined so CSS can swap which rain lines are lit, matching the two Figma variants and their timing. The bolt tilts on hover and opens Storm with a view-transition dissolve. Streamlit has no landing page, and couldn't animate inside an image without a custom component.

**Storm mode (spec 007, TypeScript only)**
- The rain is the two exported Figma layers looping in CSS. Each moves exactly one or two of its streak periods (137 and 274.5 px, not the 140 and 280 px in the Figma notes, which would jump 3–5 px). Rain and thunder are made with the Web Audio API, started by the Thunder click so nothing autoplays. Lightning flashes are limited to two flickers per strike, under WCAG's 3-per-second limit.
- Found on the way: with the page colour on both `html` and `body`, the body painted over anything placed behind the page. The colour is now on `html` only.

**Would be hard in Streamlit**
- A top bar, breadcrumbs, chips that look like the design, a raised-card shadow and a custom webfont all fight Streamlit's fixed layout and theme.

## Same-change test

_Added after all pages are done: one identical small change made in both apps._

## Load times

_Time until each page's figures appear, both apps, same inputs._

| Page | Streamlit | TypeScript | Notes |
|---|---|---|---|
| Overview: open (warm server) | 0.24–0.50 s | 0.27–0.35 s | until the KPIs and the first chart are on screen |
| Overview: click a month | 0.22 s | 0.21 s | until the caption shows the month (slice 1) |
| Genre (all time, top genre) | 0.59–0.66 s | 0.49–1.07 s | until the artist rows are on screen. The API reads the genre's plays from SQLite on every request; Streamlit caches them, so its time is steadier |
| SQL | 0.30–0.33 s | ≤ 0.12 s | until the editor is on screen (the TS figure is the page load, the earliest the check can run) |
| Schema | 0.26–0.29 s | ≤ 0.12 s | until the first card is on screen |
| Playlists (time slot defaults) | 1.12–1.16 s | 1.13–1.26 s | until the preview rows are on screen; both are dominated by `rank_tracks`, which neither app caches |

Measured in Chrome on the owner's machine with both servers warm, three runs each (the first run after a restart is dropped). The two are about equally quick. Pages that only need the shell (SQL, Schema) appear sooner in TypeScript, because Streamlit waits for its websocket and a script run first. Speed is not a reason to pick either one.
