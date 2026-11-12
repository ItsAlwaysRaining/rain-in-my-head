## Why

The Overview's "When you listen" heatmap shows when the user listens but not what. Clicking a square opens `/dashboards/slot`, which is still a Coming soon placeholder (issue #30).

## What Changes

- **New page** at `/dashboards/slot?day=&hour=&preset=&start=&end=`: the tracks played in one weekday and hour, such as "Thursdays, 15:00–16:00". It has the shared date range chips, Day and Hour pickers, a summary (range, plays, different tracks, whether it's the busiest hour of the week) and a table of tracks, most played first. Clicking a track opens its artist. Design: Figma node 326-17685.
- **New route** `GET /api/slot`, open under the existing `slot` page key.
- The placeholder is removed.

## Capabilities

### New Capabilities

- `listening-slot`: the listening slot page and its data.

## Impact

- `src/rain_in_my_head/overview.py` (`slot_tracks`), `src/rain_in_my_head/api.py` (`/api/slot`), `src/rain_in_my_head/access.py`.
- `web/src/api.ts`, `web/src/pages/Slot.tsx`, `web/src/App.tsx`, `web/src/pages/Placeholders.tsx`.
- `tests/test_slot.py`. No schema or hosting changes.
