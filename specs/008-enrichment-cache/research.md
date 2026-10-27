# Research: Enrichment cache in git

## R1. What a line stores

- **Decision**: store the values `enrich` already writes to the tables (after tag filtering), not Last.fm's raw responses.
- **Rationale**: the one-time export can only produce these values, because the database holds nothing else. Storing raw responses for new lookups only would give two line shapes. The tables replay directly.
- **Alternatives**: raw API responses, so filter changes could be re-derived. Rejected: larger, two formats, and the old data has no raw responses anyway.

## R2. File layout

- **Decision**: two files, `data/cache/tracks.jsonl` and `data/cache/artists.jsonl`. Each artist line carries its tags (`"tags": [["indie rock", 100], …]`).
- **Rationale**: one line per lookup matches what `enrich` does, since an artist lookup returns details and tags together. With tags inline, replaying a line replaces that artist's tag set exactly (FR-005). Measured at export: 14.7 MB and 5.4 MB, under the 50 MB per-file limit for years at current growth.
- **Alternatives**:
  - Monthly files, like `data/raw/`. Rejected: lookups have no natural month, and two files are simpler to replay.
  - A separate tags file. Rejected: it splits one lookup across two appends.

## R3. Last line wins, and the local database is never overwritten with older data

- **Decision**: `replay` reads each file into a dict keyed by `track_key` or `artist_key`, so later lines replace earlier ones. It then upserts only where the cache's `fetched_at` is greater than or equal to the database row's.
- **Rationale**: in CI the database is empty, so everything loads. On the Mac, a plain `enrich` (FR-010) may have newer rows the cache doesn't have yet. The `fetched_at` guard keeps them, and FR-006 holds: a second `build` changes nothing.
- **Alternatives**:
  - Always replace. Rejected: it could roll back a newer local lookup.
  - Skip keys already in the database. Rejected: a newer line from the sync would never reach the Mac.

## R4. Writing safely

- **Decision**: each line is written with one `write()` of `json + "\n"` to a file opened in append mode, then flushed and `fsync`ed. The cache line is written before the database row is committed. Before the first append in a run, if the file doesn't end in `\n`, a single `\n` is written first.
- **Rationale**:
  - A crash between the two writes leaves at worst a cache line with no database row. The next run redoes the lookup and appends a duplicate, which last-wins handles. It never leaves a database row the cache lacks, which in CI would be lost with the runner.
  - The leading newline stops a new line being glued onto a cut-off one. This is an append, not a rewrite.
  - `fsync` costs about 1 ms per lookup, which is nothing against the API's 200 ms.
- **Alternatives**:
  - Write the database first. Rejected for the reason above.
  - Truncate a cut-off tail. Rejected: it modifies the file, and the constitution prefers append-only.

## R5. Reading damaged lines

- **Decision**: `read` skips any line that isn't valid JSON or lacks its key, and prints `skipped data/cache/<file>:<line>: <reason>`. A summary count is printed at the end. `build` doesn't fail.
- **Rationale**: this matches the spec's edge case: skip, say so, never crash, never drop silently. Only a crashed local run can produce such a line. The sync never commits a partial run, because a killed job never reaches its commit step.

## R6. How `enrich` knows to write the cache

- **Decision**: a new `--write-cache` flag, off by default. The sync workflow passes it. `export-cache` is the only other writer.
- **Rationale**: FR-010 (owner's choice): the sync is the only routine writer, and a plain local `enrich` leaves the committed files alone.
- **Alternatives**: an env var (`LISTENING_WRITE_CACHE=1`). Rejected: a flag shows in `--help` and in the workflow file.

## R7. `export-cache` safety

- **Decision**: refuse with a message if either file already has lines, unless `--append` is given. Rows are written in key order, so the export is deterministic and diffs well if it's ever rerun.
- **Rationale**: FR-003. It also stops a second accidental export doubling the files.

## R8. Sync workflow shape

- **Decision**:
  1. `fetch`
  2. `build`
  3. `enrich --limit 100 --write-cache`, with `continue-on-error: true` on this step
  4. commit `data/raw/lastfm` and `data/cache` in one commit, message `Sync scrobbles <time>`, or `Sync scrobbles and N lookups <time>` when the cache changed
- **Rationale**:
  - FR-011 and FR-012: a Last.fm failure during enrich still lets the fetched scrobbles, and any lookups already appended, be committed.
  - `--limit 100` means up to 100 artists (2 calls each) plus 100 tracks: about 300 calls, or about 60 s at 5 calls a second.
  - With nothing new, enrich finds 0 to look up. The run is install plus a 2 s build, so about 1 minute. Monthly use is about 120–240 of the 2,000 free minutes.
- **Also**: `.gitattributes` marks `data/raw/**` and `data/cache/**` as `linguist-generated`, so the 20 MB export and every sync diff collapse in GitHub's PR view.
