# Proposal: Mainstream vs. niche: click a bucket to open its artists

Issue #12 · Created 2026-11-09 · Last updated 2026-11-09

## Why

The Overview's "Mainstream vs. niche" chart shows how much of my listening goes to artists with few or many Last.fm listeners, but not which artists sit in each bar. The page for it is a Coming Soon placeholder. Without the artists, I can't find the obscure ones I play or check which big names make up the mainstream share.

## What Changes

- Clicking a bar in the Overview's "Mainstream vs. niche" chart opens `/dashboards/mainstream` for that listener band, with the Overview's current range carried over (`bucket`, `start`, `end`).
- The Mainstream page replaces its Coming Soon card. It shows the band's name, its share of my plays, and a table of every artist in that band with plays in the range. Each row has the artist's Last.fm listener count and my play count, most played first.
- A band with no artists in the range shows a notice instead of an empty table.
- The page has a "Back to Dashboards" link, as the other drill-down pages do.
- Bands use the same thresholds as the chart (`LISTENER_LABELS`), so the artists' plays add up to the bar's share.
- Scope: the TypeScript web app (`web/`). The Streamlit dashboard in `dashboard/` is not changed.

## Capabilities

### New Capabilities

- `mainstream-artists`: the Mainstream vs. niche page that lists the artists in one listener band, with the band's share, each artist's listener count and play count, and the empty and back-link states.

### Modified Capabilities

- `dashboard-overview`: the "Mainstream vs. niche" chart gains a click that opens the band's page with the current range.

## Impact

- **Web**: `web/src/pages/Mainstream.tsx` (new page, replaces the placeholder in `Placeholders.tsx`), `web/src/App.tsx` (route import), `web/src/api.ts` (types and a fetch function). The Overview already passes `bucket`, `start` and `end` in its link, so it needs no change.
- **API**: a new `GET /api/mainstream` in `src/rain_in_my_head/api.py`, backed by a new function in `src/rain_in_my_head/overview.py`. It is listed in `src/rain_in_my_head/access.py` under the `mainstream` page, so guests can open it as they can open the page.
- **Tests**: unit tests in `tests/` for the band grouping and the share.
- **Dependencies**: none.
- **Not in scope**: the Streamlit dashboard's Mainstream view, and any change to the chart itself.
