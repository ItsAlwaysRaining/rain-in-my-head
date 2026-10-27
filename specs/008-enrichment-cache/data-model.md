# Data Model: Enrichment cache in git

No schema change. The cache files mirror three existing tables (`src/rain_in_my_head/schema.sql`).

## Track lookup (one line of `data/cache/tracks.jsonl`)

| Field | Type | Column in `tracks` | Notes |
|---|---|---|---|
| `track_key` | string, required | `track_key` (PK) | `"<artist_key>\t<normalised track>"`, as written at lookup time |
| `artist_key` | string, required | `artist_key` | |
| `name` | string | `name` | Last.fm's name, or the scrobbled name if the lookup found nothing |
| `duration_ms` | int or null | `duration_ms` | null = unknown |
| `global_listeners` | int or null | `global_listeners` | |
| `global_playcount` | int or null | `global_playcount` | |
| `fetched_at` | int, required | `fetched_at` | Unix seconds |

## Artist lookup (one line of `data/cache/artists.jsonl`)

| Field | Type | Column | Notes |
|---|---|---|---|
| `artist_key` | string, required | `artists.artist_key` (PK) | |
| `name` | string | `artists.name` | |
| `mbid` | string or null | `artists.mbid` | |
| `global_listeners` | int or null | `artists.global_listeners` | |
| `global_playcount` | int or null | `artists.global_playcount` | |
| `fetched_at` | int, required | `artists.fetched_at` | |
| `tags` | list of `[tag, weight]`, required (may be empty) | `artist_tags` rows | Already filtered (weight ≥ 10, not in the stoplist, at most 10), in Last.fm's order |

## Rules

- **Validity**: a line is valid if it parses as a JSON object and has its key and `fetched_at`. Invalid lines are skipped and reported (research R5).
- **Current state**: for each key, the current state is the last valid line in file order.
- **Replay into the database** (research R3), for each key's current state:
  - if the database has no row, or the line's `fetched_at` is at least the row's, write the row (`INSERT OR REPLACE`)
  - for an artist, also replace its `artist_tags` with exactly `tags`, which may be none
  - otherwise leave the row alone
- **Idempotent**: replaying the same files twice gives the same tables.
- **Export**: one line per `tracks` row and per `artists` row, with that artist's `artist_tags` attached, ordered by key.
