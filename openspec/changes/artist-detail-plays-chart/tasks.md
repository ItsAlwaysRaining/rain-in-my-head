# Tasks

## 1. Data: first play and monthly counts

- [x] 1.1 Add `first_played` and zero-filled `monthly` (`month`, `plays`) to `ArtistPage` in `src/rain_in_my_head/artist.py`, computed from the existing `plays` frame; verify with a unit test in `tests/` covering a gap month and an artist with one play day
- [x] 1.2 Add an optional `month` (YYYY-MM) argument to `artist_page()`; a month outside the period is ignored; verify with a unit test that songs are filtered to that month and that an out-of-period month returns the full song list

## 2. API

- [x] 2.1 Serialise `first_played`, `monthly` and the `month` argument in the `/api/artist` route in `src/rain_in_my_head/api.py`; verify with `uv run pytest` and a request to `/api/artist?artist=<key>&month=2026-10` returning the filtered songs

## 3. Web: types and data

- [x] 3.1 Extend the `Artist` response type and `fetchArtist` params (`month`) in `web/src/api.ts`; verify with `npm run typecheck` in `web/`

## 4. Web: header

- [x] 4.1 Add "first played <date>" to the header caption in `web/src/pages/Artist.tsx`, using the dashboard's date format; verify on a page with plays by running `npm run dev` and checking the line matches the spec scenario

## 5. Web: Plays per month chart

- [x] 5.1 Build a Vega-Lite line spec from `monthly` (zero-filled, RAIN line colour from `web/src/charts/config.ts`) and render it with `VegaChart` above the Songs heading; verify the chart shows one point per month with zeros in gaps
- [x] 5.2 Wire the point selection to a `month` URL parameter (set on click, cleared by "show every month"); verify clicking a point updates the URL and the Songs list, and that "show every month" restores the list
- [x] 5.3 Show the "Oct 2026 only"-style label with a "show every month" button while `month` is set; verify the label text and button appear and disappear with the URL parameter

## 6. Verification

- [x] 6.1 Run `npm run build` in `web/` and `uv run pytest`; both pass with no new warnings
- [ ] 6.2 Click through the artist page with a multi-month artist in the dev server, matching Figma nodes 263:1930 and 344:3549; record any visual difference in the PR description
