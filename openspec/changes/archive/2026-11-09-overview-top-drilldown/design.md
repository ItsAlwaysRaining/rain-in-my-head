# Design

## Context

The Overview's Top block is built in `web/src/pages/Overview.tsx` from `data.top`, which `/api/overview` builds in `src/rain_in_my_head/api.py` with `ov.top_lists(df)` (`src/rain_in_my_head/overview.py`). Top artists are grouped by `artist_name`, and the payload keeps only `name` and `plays`. The Artist page (`/dashboards/artist`) is keyed by `artist_key`, which `build.py` derives with `normalize(artist)`. The Top block is a Vega-Lite bar chart with no click handler. The rows that frame 5:304 shows are plain lists, and the app already has a `DataTable` with `onRowClick` and `selectedIndex`, used on the Genre and New artists pages. See proposal.md for the motivation and specs/dashboard-overview/spec.md for the requirements.

## Goals / Non-Goals

**Goals:**
- Artist rows open the Artist page for the same artist and range the list shows.
- The Top lists use the same row component as the other lists in the app.

**Non-Goals:**
- Track and album drill-downs (no design yet).
- Changing the `#1 per year` table or the Top tab set.
- Changing the top list length (20 rows, as now).

## Decisions

**1. Rows, not bars, for Top.** Frame 5:304 shows rows. Rendering them with the shared `DataTable` gives sorting, the hover and selected states, and keyboard handling for free, and it matches the Genre and New artists lists. *Alternative considered:* keep the Vega bars and wire a click param like the other charts. Rejected because it doesn't match the frame, and a bar is a poor click target on a long artist list.

**2. Group top artists by `artist_key`, not by display name.** `top_lists` currently groups by `artist_name`. Grouping by the key makes a row's count match the Artist page, which sums by key. The row label is the first `artist_name` seen for that key. This changes counts only where two spellings normalise to the same key, which is the case the Artist page already merges. *Alternative:* keep grouping by name and look up the key afterwards. Rejected because two names could map to one key and show two rows that open the same page with different totals.

**3. Add `artist_key` to the top-artists payload only.** `_records` takes a column map, so `top.artists` gets `name`, `plays` and `artist_key`. Tracks and albums keep their current shape, since they aren't clickable yet. Adding a field is backwards-compatible, and the TypeScript `NamePlays` type gets an optional `artist_key`.

**4. Link with the Overview's effective range.** The Overview already builds Genre and New artists links from `data.range` (`start`, `end`), which is the sidebar range or the selected period. The artist link uses the same values, so a click inside a selected month opens the Artist page for that month.

## Risks / Trade-offs

- **Count change for merged spellings** → Top artists may show a different count for a name that normalises to an existing key. Mitigation: the Artist page already merges these, so the numbers now agree; note it in the PR description.
- **Tracks and albums look unfinished without a click** → Users may expect them to open something. Mitigation: no hover or pointer state, per the spec, so nothing suggests a click that does nothing.
- **Frame mismatch (262:1375 shows bars)** → If that is the newer design, this work is redone. Mitigation: the spec records the choice; the decision is the owner's to confirm before merge.

## Migration Plan

No data migration. Deploy with the API and web change together, since the web app reads `artist_key` from the new payload. Rollback is reverting the PR; the old web app ignores the extra field.

## Open Questions

None. The row/bar question is resolved by frame 5:304 and the owner's choice.
