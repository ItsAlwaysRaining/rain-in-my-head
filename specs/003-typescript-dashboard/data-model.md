# Data Model: TypeScript Dashboard

There are no database changes. The entities below are the inputs and results that are shared between the Streamlit pages and the API, as produced by the functions in `src/listening/`.

## Overview

### OverviewRequest
| Field | Type | Rules |
|---|---|---|
| `preset` | `last30` \| `last12m` \| `ytd` \| `all` \| `custom` | default `last12m` |
| `start`, `end` | date | used only when `preset=custom`; clamped to the data's first and last day; `start ≤ end` |
| `grain` | `week` \| `month` \| `year` | default `month` |
| `period` | string label or empty | must equal one of the over-time `period` labels for this range and grain, otherwise it is ignored (the selection is dropped, as in the living spec) |
| `measure` | `scrobbles` \| `hours` | affects display only, not the data |

**Resolution** (`resolve_range`): the preset is resolved relative to the last day in the data, then the custom dates are applied, then `start` is clamped. A valid `period` then narrows `[start, end]` to the period intersected with the range. `inner_grain` is the grain when no period is selected, otherwise `Day`, or `Month` when the grain is `Year`.

### OverviewResult
| Field | Shape |
|---|---|
| `range` | `{start, end, data_first, data_last, data_through}`, the effective range after any selected period |
| `selected` | `{label, start, end}` or null |
| `inner_grain` | `day` \| `week` \| `month` \| `year` |
| `kpis` | list of `{label, value, delta}`. Labels in order: Scrobbles, Hours (est.), Tracks, Artists, Albums. `delta` is a fraction or null when the previous period is empty or zero |
| `over_time` | list of `{period, start, scrobbles, hours}` covering the **range before narrowing** (the chart keeps its full range) |
| `top` | `{artists, tracks, albums}`: each up to 20 `{name, plays}`, sorted by plays descending |
| `top_per_year` | `{year, artist, plays, share}` over **all data** |
| `heatmap` | 7 × 24 `{weekday (Mon..Sun), hour, plays}`, including zeros |
| `new_artists` | `{start, count}` per `inner_grain` step |
| `new_share` | fraction of plays whose artist was first heard in the same year |
| `genres` | null if no tags; otherwise `{y_max, panels: [{genre, points: [{start, share, plays}]}]}` for the top 6 genres |
| `listener_buckets` | `{bucket, share}` for `<10k … 5M+` |
| `loved` | `{artist, track, plays}`, sorted by plays descending |
| `coverage` | `{check, coverage}` × 3 |
| `empty` | true when the range has no plays; the other sections are then omitted |

## Genre (slice 2)

- **GenreRequest**: `genre` (optional; defaults to the most-played genre), `start`, `end` (optional; default all time).
- **GenreResult**:
  - `genres` (all, ordered by plays) and `genre`
  - `range_label`, `plays`
  - `artists: [{artist_key, name, art, thumb, plays}]` (`thumb` is the 64s image for table rows)
  - per artist on request: `songs: [{track_key, name, album, art, thumb, plays}]`

## SQL (slice 2)

- **SqlRequest**: `sql` text.
- **SqlResult**: `{columns: [name], float_columns: [index], rows: [[value]], row_count}` or `{error}`. The connection is read-only.
- The schema list and the examples come from shared constants, so both apps show the same ones.

## Schema (slice 3)

- **SchemaResult**: the same objects, columns, links, lineage and defaults that `dashboard/views/schema.py` passes to its component today, plus the saved layout.
- **Layout**: `{name: {x, y}}`, stored in `data/schema_layout.json` and shared by both apps. The last write wins.

## Playlists (slice 3)

- **PlaylistRequest**: `kind` (`slot` \| `discoveries` \| `binges`) plus the same options as the Streamlit form.
- **PlaylistPreview**: `{name, description, columns, rows, candidate_count, notes}`, produced by the existing [playlist.py](../../src/listening/playlist.py) functions.
- **CreateRequest**: PlaylistRequest plus `name` and `public`.
- **Create** streams events: `progress {fraction, message}`* then `done {url, count, misses: [{artist, track}]}` or `error {message}`.
