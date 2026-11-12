## Why

The web Genre page only takes its date range from the URL, so a visitor can't change it on the page, and it shows no trend for the genre. Figma 263:2051 has date range chips and a "Share of tagged plays" chart. Closes #78 (Figma deviation items 3 and 4).

## What Changes

- Add the Overview's date range chips to the Genre page: Last 30 days / This year / Last 12 months / All time / Custom (Custom opens the same start/end popup).
- `/api/genre` accepts `preset` and returns the resolved range plus a `share` series: the genre's share of tagged plays per step.
- Add a "Share of tagged plays" area chart in the genre's colour, with a label on the peak point.
- The Overview's genre links pass `preset` (and `start`/`end` for Custom) so the right chip is selected.

## Capabilities

### New Capabilities
- `genre-page`: the Genre dashboard page: range chips, genre picker, share chart, artists and songs.

### Modified Capabilities
- `dashboard-overview`: genre chip/chart links carry the range preset.

## Impact

- `src/rain_in_my_head/api.py`, `src/rain_in_my_head/genre.py` (share series, reuse `overview.resolve_range`)
- `web/src/pages/Genre.tsx`, `Genre.module.css`, `web/src/api.ts`, new `web/src/charts/genre.ts`, `web/src/pages/Overview.tsx`
- New `tests/test_genre.py`. No schema or dependency changes.
