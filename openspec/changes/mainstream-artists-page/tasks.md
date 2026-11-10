# Tasks

## 1. API: artists in one listener band

- [ ] 1.1 In `src/rain_in_my_head/overview.py`, add a function that returns, for one band label, each artist's name, `artist_key`, Last.fm listener count and play count in the range, most played first, plus the band's share of known-listener plays. Verify: a unit test in `tests/test_mainstream.py` shows two spellings with one key give one row, a 10k artist and a 100k artist land in the right bands, and the share equals the chart's `listener_buckets` value for the same data.
- [ ] 1.2 In `src/rain_in_my_head/api.py`, add `GET /api/mainstream?bucket=&start=&end=` (start and end default to all time). Return 422 for a band that is not in `LISTENER_LABELS`. Verify: a test in `tests/test_mainstream.py` checks the JSON shape, the 422 for an unknown band, and an empty band returning no artists.
- [ ] 1.3 In `src/rain_in_my_head/access.py`, add `("GET", "/api/mainstream"): frozenset({"mainstream"})`. Verify: the app still starts (`check_routes()` passes) and a guest's request is allowed, while a visitor with no page access is refused (tests in `tests/`).

## 2. Web: the page

- [ ] 2.1 In `web/src/api.ts`, add the `MainstreamArtist` and `Mainstream` types and `fetchMainstream(params)`. Verify: `npm run typecheck` in `web/` passes.
- [ ] 2.2 Create `web/src/pages/Mainstream.tsx`. It shows the band name, its share and the range, a `DataTable` with name, listener count and plays, the empty notice, the unknown-band notice, and `BackLink`. Verify: `npm run dev`, then clicking a bar on the Overview opens the page with the same share and the table's plays add up to the bar's share.
- [ ] 2.3 Remove the `Mainstream` placeholder from `web/src/pages/Placeholders.tsx` and point the route in `web/src/App.tsx` at the new page. Verify: `npm run typecheck` and `npm run build` pass, and `grep -rn "Mainstream" web/src/pages/Placeholders.tsx` finds nothing.
- [ ] 2.4 Check the page at phone width (16px gutters, no horizontal page scroll) and with a band that has no artists in the range. Verify: the browser shows both states as the spec describes.

## 3. Overview link

- [ ] 3.1 Confirm the Overview's existing bar click opens `/dashboards/mainstream?bucket=&start=&end=` with the effective range, including a selected period. Verify: the URL in the browser after a click matches, for the sidebar range and for a selected month.

## 4. Checks

- [ ] 4.1 Scoped check: run `tests/test_mainstream.py` and the existing overview tests (`tests/test_overview_top.py`). Verify: they pass.
- [ ] 4.2 Full regression once before the PR: `uv run --with pytest --with httpx pytest`, `ruff check src api tests`, `npm run typecheck` and `npm run build` in `web/`. Verify: all pass; output goes in the PR description.
