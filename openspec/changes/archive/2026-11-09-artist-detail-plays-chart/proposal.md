# Proposal

## Why

The Figma prototype shows two things the artist page does not have: a "Plays per month" chart that filters the song list by month, and a "first played" date in the header. Without them the artist page shows totals only, and a reader cannot see when they started listening to an artist or when they listened most. This is Figma deviation items 1 and 2 (GitHub issue #77).

## What Changes

- Add a "Plays per month" line chart to the artist page, one point per month of the artist's plays. Clicking a point filters the Songs list to that month.
- While a month is picked, show an "Oct 2026 only"-style state (the picked month's label) with a "show every month" button that clears the filter.
- Add the artist's first play date to the header line, e.g. "42 plays in last 12 months · 120 all time · first played 2 Mar 2026".
- The artist API (`/api/artist`) returns the monthly counts and the first-played date. No other endpoint changes.

No **BREAKING** changes.

## Capabilities

### New Capabilities

- `artist-page`: the Artist page (`web/src/pages/Artist.tsx`) header, per-month play chart, month filter and the Songs list. Covers only behaviour on that page. The page's earlier design lives in `specs/001-new-artist-page/` (Spec Kit) and is not changed here.

### Modified Capabilities

None. The Overview's "New artists" list and its click-through to the artist page are not changing.

## Impact

- `web/src/pages/Artist.tsx` and `Artist.module.css`: chart, month filter state, header line.
- `web/src/api.ts`: response type for `/api/artist` gains the monthly counts and first-played date.
- `src/rain_in_my_head/artist.py` (`artist_page`): computes the monthly counts and first-played date from the same `plays` frame. Python dashboard (`dashboard/views/artist.py`) is not changed in this change; say if it should match.
- `src/rain_in_my_head/api.py`: the `/api/artist` route serialises the new fields and takes an optional month.
- Chart colours come from the existing chart tokens in `web/src/charts/config.ts`; no new colours.
- No schema or data changes; `data/listening.db` is rebuilt from the same scrobbles.
