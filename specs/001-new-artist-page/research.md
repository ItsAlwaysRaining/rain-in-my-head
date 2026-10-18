# Research: New Artists and Artist Page

No NEEDS CLARIFICATION items were left in the Technical Context. These are the decisions that needed
checking. Revised 2026-10-18 for both dashboards; the 2026-10-14 decisions that no longer hold are
noted under each heading.

## Where the data code lives

- **Decision**: a new `src/rain_in_my_head/artist.py`, used by the Streamlit pages and by the API.
  It reuses `ranked()`, `most_common()`, `thumb()` and `PLACEHOLDER` from `rain_in_my_head.genre`.
- **Rationale**: constitution 1.1 (VI) puts queries, aggregation and ranking in shared functions so
  both dashboards show the same numbers. The album-art helpers already moved from
  `dashboard/views/genre.py` into `rain_in_my_head.genre` during spec 003.
- **Superseded**: the 2026-10-14 plan put the helpers in `dashboard/lastfm_art.py` and the list's
  query in `dashboard/views/overview.py`. Both would now break VI, and the first is already done.

## Which table

- **Decision**: read `scrobbles` directly, with the same filters as `genre_plays`: plays before
  2000-01-01 dropped (as `v_plays` does), and art containing the no-image hash read as missing.
  An artist's first play is `MIN(played_at)` over all their plays.
- **Rationale**: `v_plays` has no `image_url`, and the list needs art. `scrobbles` is indexed on
  `artist_key`, so the artist page stays cheap.

## Hiding the artist page from the menu

- **Decision**: Streamlit: `st.Page("views/artist.py", url_path="artist", visibility="hidden")`,
  opened with `st.switch_page(..., query_params=...)`. TypeScript: a `/artist` route in `App.tsx`
  that isn't in the `PAGES` menu list, opened with `navigate()`.
- **Rationale**: Streamlit 1.65's `st.Page` supports `visibility` (checked with a throwaway app on
  2026-10-14: `switch_page` reached a hidden page and its query parameters arrived).

## Placeholder image

- **Decision**: one file, `web/public/no-art.svg`: a music note in Night (`#8C9FE0`) on Night
  Surface (`#1C2238`). The TypeScript app loads it as `/no-art.svg`; Streamlit reads the same file
  and passes it as a `data:image/svg+xml` URL, the way the favicon is shared.
- **Rationale**: no external request (V), one source for both apps, palette colours (VI). Whether
  Streamlit's image column shows a data URL is checked in the browser (quickstart scenario 5).
- **Superseded**: the iris colours from the old palette.

## Which period and which plays

- **Decision**: the list's period is the selected over-time period (already narrowed into
  `start`/`end` on the Overview), otherwise `max(start, first of end's month)` to `end`. "New" means
  the artist's first play ever falls in the period. The plays counted are the artist's plays in the
  period.
- **Rationale**: matches FR-002 and the owner's choice.

## Naming the period

- **Decision**: `period_label(start, end)`: "%b %Y" when `start` is the 1st and `end` is in the same
  month; "%Y" when `start` is 1 January and `end` is in the same year; otherwise
  "%d %b %Y – %d %b %Y". Used for the list's title and the artist page's header.
- **Rationale**: the default list covers the month so far (e.g. 1–18 Oct) and should still read
  "Oct 2026" (spec US1 scenario 1). One function keeps both apps' wording identical.

## Clicking a row

- **Decision**: Streamlit: `st.dataframe(..., on_select="rerun", selection_mode=["single-row",
  "single-cell"])`, then `st.switch_page` on a selection, as on the Genre page. TypeScript: the
  shared `DataTable`'s `onRowClick`, which already makes the whole row the target.
- **Rationale**: cell selection makes a click anywhere on the row count (the bug fixed in PR #2).
