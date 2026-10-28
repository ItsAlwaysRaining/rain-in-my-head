# Data Model: Two-year public dataset

`public.db` uses the same `schema.sql` as `listening.db`, without `spotify_matches`.

| Table | Rows kept |
|---|---|
| `scrobbles` | `start ≤ played_at < end` (research R2) |
| `tracks` | `track_key IN (SELECT track_key FROM scrobbles)` |
| `artists` | `artist_key IN (SELECT artist_key FROM scrobbles)` |
| `artist_tags` | `artist_key IN (SELECT artist_key FROM scrobbles)` |
| `spotify_matches` | dropped |
| views `v_plays`, `v_artist_genre` | recreated by `schema.sql` |

## Invariants (checked in quickstart)

- No scrobble is outside `[start, end)`.
- No track or artist has no scrobble.
- Every scrobble's `track_key` and `artist_key` has a row in `tracks` and `artists` whenever the full database has one.

## Publish result

`PublishStats(start, end, plays, tracks, artists, tags, bytes)` is printed as:

```text
Published 2024-10-14 → 2026-10-20: 45,188 plays, 23,176 tracks, 9,796 artists → data/public.db (12.3 MB)
```
