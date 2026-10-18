# Data Model: New Artists and Artist Page

Read-only; no schema changes. All data comes from the existing `scrobbles` table and `v_plays` view.

## Play

From `scrobbles` (and `v_plays`): `played_at` (unix seconds), local date, `artist_key` (normalized
artist), `artist_name`, `track_key` (normalized "artist<TAB>track", so "Remastered" etc. merge),
`track_name`, `album_name`, `image_url`.

Rules: plays before 2000-01-01 are excluded (placeholder timestamps, as in `v_plays`). An
`image_url` containing Last.fm's no-image hash `2a96cbd8b46e442fc41c2b86b821562f` counts as missing.

## Period

`start`, `end`: local dates, inclusive. Either the selected over-time period (clamped to the sidebar
range) or the most recent month: `max(range start, first day of range end's month)` to range end.

## New artist (for a period)

Derived per `artist_key`:

| Field | Meaning |
|---|---|
| `artist_key` | identity, passed to the artist page |
| `name` | most common `artist_name` among the plays |
| `first_play` | earliest play across all data; must fall in the period |
| `art` | most common non-missing `image_url` among the period's plays, else none |
| `plays` | number of plays in the period |

Sorted by `plays` descending, then `name`.

## Artist page song

Derived per `track_key` for one artist within the period:

| Field | Meaning |
|---|---|
| `name` | most common `track_name` |
| `album` | most common `album_name` |
| `art` | most common non-missing `image_url`, else placeholder |
| `plays` | number of plays in the period |

Sorted by `plays` descending, then `name`. The sum of `plays` equals the header's period total.
