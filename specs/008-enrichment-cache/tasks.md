# Tasks: Enrichment cache in git

**Input**: Design documents from `specs/008-enrichment-cache/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: no automated test suite (none requested). Each story is checked with the matching [quickstart.md](quickstart.md) step.

## Phase 1: Setup

- [x] T001 Add `CACHE_DIR = Path(os.environ.get("LISTENING_CACHE_DIR", ROOT / "data" / "cache"))` next to `RAW_DIR` in src/rain_in_my_head/config.py
- [x] T002 [P] Add .gitattributes marking `data/raw/** linguist-generated=true` and `data/cache/** linguist-generated=true`

## Phase 2: Foundational (blocks all stories)

- [x] T003 Create src/rain_in_my_head/cache.py with:
  - `TRACKS_FILE = "tracks.jsonl"` and `ARTISTS_FILE = "artists.jsonl"`
  - `TRACK_FIELDS` and `ARTIST_FIELDS`, in the column order of `tracks` and `artists` in schema.sql
  - `_dumps(obj)`: `json.dumps(obj, ensure_ascii=False, separators=(",", ":"))`
- [x] T004 In src/rain_in_my_head/cache.py, add `read(path, key) -> dict[str, dict]`:
  - parses each line in file order and keeps the last valid one per key
  - a line is valid if it "parses as a JSON object and has its key and `fetched_at`"
  - each invalid line prints `skipped <path>:<lineno>: <reason>`, followed by a skipped count
  - a missing file returns `{}`
- [x] T005 In src/rain_in_my_head/cache.py, add a `CacheWriter(cache_dir)` class:
  - creates the folder
  - opens both files in append mode on first use; if a file is non-empty and doesn't end in `\n`, writes one `\n` first (research R4)
  - `track(row: dict)` and `artist(row: dict, tags: list[[tag, weight]])` each do one `write(_dumps(...) + "\n")`, then `flush()` and `os.fsync()`
  - counts lines written and supports `close()` / use as a context manager

## Phase 3: User Story 1 — A fresh copy rebuilds everything (P1) 🎯 MVP

**Goal**: `build` in a fresh clone restores tracks, artists and tags with zero Last.fm calls.

**Independent test**: quickstart steps 1–3.

- [x] T006 [US1] In src/rain_in_my_head/cache.py, add `export(conn, cache_dir, append=False) -> tuple[int, int]`:
  - if either file has lines and `append` is false, raise `SystemExit` with the message in contracts/cli.md
  - otherwise write every `tracks` row ordered by `track_key`, then every `artists` row ordered by `artist_key` with its `artist_tags` attached as `tags`, through `CacheWriter`
  - an artist with no tags gets `"tags": []`
  - tag order is weight descending, then tag name
- [x] T007 [US1] In src/rain_in_my_head/cache.py, add `replay(conn, cache_dir) -> tuple[int, int, int]` following the data-model.md replay rules:
  - load the existing `fetched_at` per key from `tracks` and `artists`
  - for each key's current line, write the row with `INSERT OR REPLACE` "if the database has no row, or the line's `fetched_at` is newer than the row's"
  - for an artist that was written, run `DELETE FROM artist_tags WHERE artist_key = ?`, then insert exactly its `tags`
  - all in one transaction; return (tracks, artists, updated)
- [x] T008 [US1] In src/rain_in_my_head/build.py, change `build(raw_dir, db_path, cache_dir=None)`:
  - after the scrobble insert, if `cache_dir` is given, call `cache.replay(conn, cache_dir)` before closing
  - print `Replayed cache: N tracks, M artists (K updated)`, or `No enrichment cache in <dir>` if neither file exists
- [x] T009 [US1] In src/rain_in_my_head/cli.py:
  - `cmd_build` passes `config.CACHE_DIR`
  - add `cmd_export_cache` and an `export-cache` subparser with `--append`: help "write the database's Last.fm lookups to data/cache/ (one-time)"
  - `cmd_export_cache` opens the database with `build.connect_readonly` and prints `Exported N tracks and M artists to <dir> (X.X MB)`
- [x] T010 [US1] Run `uv run rain-in-my-head export-cache` on the owner's database, check it refuses a second run, and commit data/cache/tracks.jsonl and data/cache/artists.jsonl in their own commit
- [x] T011 [US1] Run quickstart steps 2–3: a fresh clone with no Last.fm key and a scratch database. Record the counts, the genre hash and the build time

## Phase 4: User Story 2 — New lookups are saved where git can see them (P2)

**Goal**: `enrich --write-cache` appends one line per lookup. A plain `enrich` leaves the cache alone.

**Independent test**: quickstart step 4.

- [x] T012 [US2] In src/rain_in_my_head/enrich.py:
  - `enrich_tracks` and `enrich_artists` take an optional `writer: CacheWriter | None`
  - when it's set, call `writer.track(...)` or `writer.artist(..., tags)` with the same values, before the `INSERT OR REPLACE` and `conn.commit()`
  - `enrich(client, db_path, limit, cache_dir=None)` opens a `CacheWriter` only when `cache_dir` is given, and prints `Appended N track and M artist lookups to <dir>`
- [x] T013 [US2] In src/rain_in_my_head/cli.py, add `--write-cache` to the `enrich` subparser: help "also append each lookup to data/cache/ (used by the scheduled sync)". `cmd_enrich` passes `config.CACHE_DIR` only when the flag is set
- [x] T014 [US2] Run quickstart step 4 (append with and without the flag, plus a cut-off line) against `$S` copies only

## Phase 5: User Story 3 — The scheduled sync keeps enrichment up to date (P3)

**Goal**: the 6-hourly sync fetches, builds, enriches and commits raw plus cache together.

**Independent test**: quickstart step 5.

- [x] T015 [US3] In .github/workflows/sync.yml:
  - after fetch, add a `Build database` step: `uv run --no-default-groups rain-in-my-head build`
  - add an `Enrich new tracks and artists` step: `uv run --no-default-groups rain-in-my-head enrich --limit 100 --write-cache`, with `continue-on-error: true` and the `LASTFM_*` env
  - the commit step runs `git add data/raw/lastfm data/cache`, and uses the message `Sync scrobbles and lookups <time>` when `git diff --cached --quiet -- data/cache` shows cache changes, otherwise the current message
- [x] T016 [US3] Push the branch and run `gh workflow run sync.yml --ref feature/enrichment-cache` twice. Confirm the first run succeeds in under 3 minutes and the second makes no commit (quickstart step 5)

## Phase 6: Polish

- [x] T017 [P] Update README.md:
  - `data/cache/` is committed and append-only
  - `build` now restores enrichment
  - `enrich --write-cache` is for the sync; a plain `enrich` stays local
  - `export-cache` is one-time
- [x] T018 [P] Update the module docstrings in src/rain_in_my_head/enrich.py and src/rain_in_my_head/cli.py to mention the cache and `export-cache`
- [x] T019 Run `uvx ruff check src/` and fix anything it reports in the changed files
- [ ] T020 Open the PR with .github/pull_request_template.md, listing what was checked (T011, T014, T016) and what wasn't

## Dependencies

- Setup (T001–T002) → Foundational (T003–T005) → US1 (T006–T011) → US2 (T012–T014) → US3 (T015–T016) → Polish
- US2 needs `CacheWriter` (T005) and the exported files (T010). US3 needs US1's `build` replay and US2's `--write-cache`.
- T010 must come before T011 and T016, because a fresh clone needs the committed cache.

## Parallel opportunities

- T002 runs alongside T001.
- T017 and T018 run alongside each other once US3 is done.
- The stories are sequential by design: each builds on the one before.

## Implementation strategy

US1 alone delivers the MVP for hosting: phase 2 (the public dataset) only needs `build` to restore enrichment. US2 and US3 stop the cache going stale. All three ship in one PR.
