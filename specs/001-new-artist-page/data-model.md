# Data Model: New Artists and Artist Page

Read-only; no schema changes. All data comes from the existing `scrobbles` table, through
`rain_in_my_head.artist`.

## Play

From `scrobbles`: `played_at` (unix seconds), its local date, `artist_key` (normalized artist),
`artist_name`, `track_key` (normalized "artist<TAB>track", so "Remastered" etc. merge),
`track_name`, `album_name`, `image_url`.

Rules: plays before 2000-01-01 are excluded (placeholder timestamps, as in `v_plays`). An
`image_url` containing Last.fm's no-image hash `2a96cbd8b46e442fc41c2b86b821562f` counts as missing.

## Period

`start`, `end`: local dates, inclusive. Either the selected over-time period (clamped to the sidebar
range) or the most recent month: `max(range start, first day of range end's month)` to range end.
Its `label` comes from `period_label` (see research.md, "Naming the period").

## New artist (for a period)

Derived per `artist_key` (`genre.ranked` over the period's plays by new artists):

| Field | Meaning |
|---|---|
| `artist_key` | identity, passed to the artist page |
| `name` | most common `artist_name` among the period's plays |
| `art` | most common non-missing `image_url` among the period's plays, else none |
| `thumb` | `art` at the 64px table size, else none (the app shows the placeholder) |
| `plays` | number of plays in the period |

Only artists whose first play ever falls in the period. Sorted by `plays` descending, then `name`.

## Artist page

| Field | Meaning |
|---|---|
| `name` | most common `artist_name` across all their plays |
| `cover` | 300px art: most common in the period, else across all plays, else none |
| `period_plays` | plays in the period (all plays when there's no period) |
| `all_time_plays` | all plays |
| `songs` | below |

## Artist page song

Derived per `track_key` for one artist within the period (`genre.songs`):

| Field | Meaning |
|---|---|
| `name` | most common `track_name` |
| `album` | most common `album_name` |
| `art`, `thumb` | most common non-missing `image_url`, and its 64px version; else none |
| `plays` | number of plays in the period |

Sorted by `plays` descending, then `name`. The sum of `plays` equals `period_plays`.
