# Tasks

## 1. API: artist keys in the top-artists payload

- [x] 1.1 In `src/rain_in_my_head/overview.py`, group top artists by `artist_key` and keep the first `artist_name` for each key. Verify: a unit test in `tests/` shows two spellings that normalise to one key give one row with the summed count.
- [x] 1.2 In `src/rain_in_my_head/api.py`, return `artist_key` on `top.artists` rows and leave tracks and albums unchanged. Verify: `/api/overview` JSON has `artist_key` on each top artist and no new keys on tracks or albums (test in `tests/`).

## 2. Web: rows and links

- [x] 2.1 In `web/src/api.ts`, add optional `artist_key` to `NamePlays` for top artists. Verify: `npm run typecheck` (or `tsc --noEmit`) passes.
- [x] 2.2 In `web/src/pages/Overview.tsx`, render Artists, Tracks and Albums with `DataTable` rows (name and plays, most played first). Verify: `npm run dev`, the Top tabs show rows, and the play counts match the API.
- [x] 2.3 In `Overview.tsx`, make artist rows call `onRowClick` to open `/dashboards/artist?artist=&start=&end=` with `data.range` values. Verify: clicking Hozier in the Artists tab opens the Artist page with the sidebar range; clicking with a selected month opens the Artist page for that month.
- [x] 2.4 In `Overview.tsx`, give track and album rows no `onRowClick` and no hover or pointer state. Verify: clicking a Tracks row does nothing and the row has no hover style.
- [x] 2.5 Remove the now-unused `topBar` chart from `web/src/charts/overview.ts`, if nothing else imports it. Verify: `grep -rn topBar web/src` finds no references, and typecheck passes.

## 3. Tests and checks

- [x] 3.1 Scoped check for the Overview: run the existing overview tests and the dashboard-overview scenarios for period selection. Verify: they pass, and no other page is affected.
- [x] 3.2 Run the full regression once before the PR (`uv run pytest`, `npm test` if present, `npm run build`). Verify: all pass, output pasted in the PR description.
