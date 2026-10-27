# Contract: CLI changes

## `rain-in-my-head export-cache [--append]` (new)

- Writes every `tracks` row to `tracks.jsonl` and every `artists` row, with its tags, to `artists.jsonl`, in key order.
- If either file already has lines and `--append` isn't given, it exits non-zero with: `data/cache/ already has lookups (N tracks, M artists). Use --append to add the database's rows after them.`
- Prints `Exported N tracks and M artists to data/cache/ (X.X MB)`.
- Reads the database read-only and never calls Last.fm.

## `rain-in-my-head build` (changed)

- Loads scrobbles as now, then replays the cache (data-model.md rules).
- Prints the current line, then: `Replayed cache: N tracks, M artists (K updated)`, plus any `skipped …` lines.
- If there are no cache files, it prints `No enrichment cache in data/cache/` and still succeeds.

## `rain-in-my-head enrich [--limit N] [--write-cache]` (changed)

- Without `--write-cache`, it behaves exactly as today.
- With `--write-cache`, it appends one line per lookup before the database write (research R4), and prints `Appended N track and M artist lookups to data/cache/` at the end.

## Environment

- `LISTENING_CACHE_DIR`: the cache folder (default `data/cache`). Same pattern as `LISTENING_RAW_DIR`.
