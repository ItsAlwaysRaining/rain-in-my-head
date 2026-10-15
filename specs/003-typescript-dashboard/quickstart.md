# Quickstart: TypeScript Dashboard

## Prerequisites

- `data/listening.db` has been built (`uv run listening build`) and ideally enriched.
- Node 22+ and npm installed.
- `uv sync` installs the `web` group, which is a default group.

## Run both apps

```sh
uv run streamlit run dashboard/app.py          # Streamlit  → http://localhost:8501
cd web && npm install && npm run build && cd ..
uv run listening serve                          # TypeScript → http://localhost:8000
```

Development with hot reload: run `uv run listening serve --dev` (API only) and `npm run dev` in `web/` (http://localhost:5173, which proxies `/api`).

## Validation scenarios

### Slice 1: Overview

1. **The Streamlit refactor didn't change numbers.** Run the scratch golden script (research §9) before and after the extraction. Expect identical JSON for presets {last30, last12m, ytd, all} × grains {week, month, year}, plus one selected period per grain.
2. **Streamlit still works.** In headless Chrome on :8501, change the preset and grain, click a month bar (the caption narrows), click "Show whole range", and click a genre panel (the Genre page opens).
3. **Parity.** In headless Chrome, for "Last 12 months / Month" and then one selected month, read the five KPI values and deltas, the first three top artists, and the "#1 per year" row count from both apps. Expect them to be equal.
4. **Living spec.** Run each scenario of `openspec/specs/dashboard-overview/spec.md` on :8000. That covers the caption dates, the partial edge period, deltas, "#1 per year" unchanged, picking another bar, "per day" inside a month, the year grain stepping by month, "Show whole range", clicking the background, a grain change dropping the selection, and a genre click carrying the period into `/genre?...`.
5. **SQL cross-check.** Run `sqlite3 data/listening.db "SELECT COUNT(*), COUNT(DISTINCT track_key), COUNT(DISTINCT artist_key) FROM v_plays WHERE date(played_local) BETWEEN '<start>' AND '<end>'"`. It must equal the KPIs shown.
6. **Speed (SC-004).** The Overview's figures appear within 2 s of opening (warm server), and within 1 s after clicking a bar.
7. **Edge cases.**
   - Stop the API: the page shows how to start it.
   - Set `LISTENING_DB` to a missing path: the page shows the "run build" message.
   - Use a custom range with no plays: "No scrobbles in this range".

### Slice 2: Genre and SQL

- Open the same genre and range in both apps: the artists and play counts are identical, and clicking an artist shows the same songs.
- Run every SQL example in both apps: the row counts are equal. `DELETE FROM scrobbles` is refused. The CSV download opens with the same rows.

### Slice 3: Schema and Playlists

- Run the spec 002 quickstart scenarios on :8000. Move a card on :8000, then reload :8501: it is in the same place.
- Build a time-slot preview (Friday 17–19, defaults) in both apps: the same tracks in the same order. Create one private playlist from :8000: progress is shown, then the link, then the misses.

### Comparison log

`docs/streamlit-vs-typescript.md` has a section for each page delivered in the PR.
