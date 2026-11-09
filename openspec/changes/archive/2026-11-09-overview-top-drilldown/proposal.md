# Proposal: Overview top lists drill into the artist page

Issue #62 · Created 2026-11-09 · Last updated 2026-11-09

## Why

The Overview "Top" block shows the most played artists, tracks and albums as bar charts that can't be clicked. Figma frame 5:304 (Hi-Fi · Overview) shows them as lists of rows, and each artist row is meant to open that artist. Nothing in the web app does that yet, so a visitor who sees a favourite artist near the top has no way to reach its songs.

## What Changes

- Artist rows in the Top block become clickable. A click opens the Artist detail page for that artist, with the Overview's current date range carried over (`/dashboards/artist?artist=…&start=…&end=…`), as the New artists page already does.
- The Top block presents Artists, Tracks and Albums as lists of rows, with the play count at the end of each row, as frame 5:304 shows, instead of horizontal bar charts.
- Track and album rows are not clickable in this change. Frame 5:304 has no drill-down for them, so they show no clickable state until a design says otherwise.
- The `#1 per year` tab and the tab order stay as they are.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `dashboard-overview`: the Top lists change from charts to rows, and artist rows open the Artist detail page with the current range.

## Impact

- **Web**: `web/src/pages/Overview.tsx` (Top block), `web/src/charts/overview.ts` (the `topBar` chart is replaced by a row list for artists, tracks and albums), and the `DataTable` or row component used for lists.
- **API**: `src/rain_in_my_head/api.py` (the `top` payload), which today returns only `name` and `plays`. Artist rows need `artist_key` as well, since the Artist page is keyed by it. Track and album rows don't need a key yet.
- **Dependencies**: none.
- **Design mismatch to note**: frame 262:1375 (Dashboards · Overview, Prototype page) still shows plain bars for Top. This change follows 5:304. If 262:1375 is the newer design, the rows here need to be replaced by bars again.
