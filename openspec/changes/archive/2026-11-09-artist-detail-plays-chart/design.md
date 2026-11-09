# Design

## Context

The Artist page gets its header counts and songs from `/api/artist`, which calls `artist_page()` in `src/rain_in_my_head/artist.py`. That function already reads every play of the artist and filters by the page's period. The Overview charts select with `VegaChart`'s `onSelect` (see `web/src/pages/Overview.tsx`). See proposal.md - Why and specs/artist-page/spec.md for the behaviour.

## Goals / Non-Goals

**Goals:**
- Compute the first play date and monthly counts from the same play rows the header already uses.
- Keep the month filter on the server, so the Songs list stays correct for every month, not just the top songs of the period.

**Non-Goals:**
- No change to the Python Streamlit artist view (`dashboard/views/artist.py`).
- No change to the New artists list or its link to this page.

## Decisions

- **Monthly counts and first play from `artist_page()`.** The function already has all the artist's plays in a frame. Add `first_played` (min `played_at`, local date) and `monthly` (list of `{month, plays}` over the page's months, zero-filled). Alternative: a new SQL query. Rejected: a second read of the same rows.
- **Month filter is a query parameter on `/api/artist`** (`month=YYYY-MM`). The server filters `in_period` to that month and rebuilds `songs`. Alternative: client-side filter on a per-month songs map. Rejected: sends every song for every month.
- **Chart is a Vega-Lite line with a point selection**, rendered by `VegaChart` with `param` set to the selection name, the same pattern as the Overview over-time chart. Points are selected by month; the selected point is highlighted. Colours from `RAIN` in `web/src/charts/config.ts`, the line colour already set in the chart config.
- **Zero-filled months come from Python**, not from the chart, so the line does not drop to nothing between points.
- **Filter state lives in the URL** (`month` param), alongside `artist`, `start`, `end`. Alternative: component state. Rejected: a reload or a shared link would lose the month. The URL is also what the query key is built from.

## Risks / Trade-offs

- **Chart points from a long history** (an artist with plays over many years gives many points). → Mitigation: the chart uses the page period when set; all-time pages show first-to-last month only, which is bounded by the listening history.
- **Month boundaries in local time.** Plays are stored as UTC epoch; the existing `day` column is local. → Mitigation: use the same `day` column for the month key so counts match the Songs list.
- **Two endpoints disagree if `month` is outside the period.** → Mitigation: the server ignores a month outside the period and returns the full list, per the spec.

## Migration Plan

No data migration. Deploy with the API and the page together (same repo, same release). Rollback: revert the commit; the old page ignores the new fields.

## Open Questions

None that change the specs or the task split. The Streamlit artist view will keep its current behaviour; a follow-up can bring it to parity if wanted.
