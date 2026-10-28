# Implementation Plan: Enrichment cache in git

**Branch**: `feature/enrichment-cache` | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/008-enrichment-cache/spec.md`

## Summary

Last.fm lookups get two new committed files: `data/cache/tracks.jsonl` and `data/cache/artists.jsonl`, with tags inline. A new module, `cache.py`, appends to these files and replays them. `build` replays the cache after loading scrobbles. `enrich --write-cache` appends one line per lookup before it writes the database. A one-time `export-cache` command seeds the files from the local database. The sync workflow becomes fetch → build → enrich (`--limit 100 --write-cache`) → one commit. No new dependencies.

## Technical Context

**Language/Version**: Python 3.10+ (uv)

**Primary Dependencies**: standard library only (`json`, `os`, `sqlite3`). The existing httpx and python-dotenv are unchanged.

**Storage**:
- SQLite `data/listening.db` (gitignored, rebuildable)
- JSONL `data/cache/*.jsonl` (committed, append-only)

**Testing**: no test suite in the repo. Checks are scripted in [quickstart.md](quickstart.md): a fresh-clone rebuild, SQL cross-checks (constitution III) and a manual workflow run.

**Target Platform**: macOS (owner) and `ubuntu-latest` GitHub Actions

**Project Type**: CLI plus scheduled workflow

**Performance Goals**:
- A fresh build including the cache replay takes under 2 minutes. The scrobble load alone takes 2.2 s today.
- A sync run with nothing new takes under 3 minutes.

**Constraints**:
- The sync keeps `--no-default-groups`.
- No file over 50 MB.
- Stay inside the free 2,000 Actions minutes a month.

**Scale/Scope**:
- At export: 76,556 track lines (14.7 MB measured) and 24,263 artist lines (5.4 MB measured).
- Growth: a few hundred lines a week.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Check | Result |
|---|---|---|
| I. Raw scrobbles are the source of truth | Both cache files are append-only. The last line for a key wins. `listening.db` can be rebuilt from raw plus cache. The schema is unchanged. | ✅ |
| II. Spec first, small changes | Spec 008 is approved. The work is on `feature/enrichment-cache`, and there's one PR. | ✅ |
| III. Verify in the real app | No dashboard code changes. The numbers are cross-checked against direct SQLite queries (quickstart steps 2–3), and the top 20 genres are compared. A browser check of the Genre page on the rebuilt database is optional. | ✅ |
| IV. Few dependencies | None added. The sync stays `--no-default-groups`, because `enrich` and `build` import only core modules. | ✅ |
| V. Respect external APIs and secrets | Lookups are cached in `data/cache/` and SQLite. Enrichment stays resumable and rate-limited through the existing client. The sync uses the existing `LASTFM_*` secrets only. | ✅ |
| VI. Consistent dashboards | Not affected: both read the same tables. | ✅ (n/a) |
| VII. Visitors' access and privacy | Not affected. The cache holds only public Last.fm metadata. | ✅ (n/a) |
| Data and Privacy | `data/cache/` is explicitly allowed to be committed. | ✅ |

**Post-design re-check**: still passes. Writing a newline before an append when a file has a cut-off last line (research R4) adds a line and never rewrites one, so it stays append-only.

## Project Structure

### Documentation (this feature)

```text
specs/008-enrichment-cache/
├── plan.md          # this file
├── research.md      # decisions R1–R8
├── data-model.md    # cache line shapes and replay rules
├── quickstart.md    # validation run
├── contracts/
│   ├── cache-format.md   # the JSONL line contract
│   └── cli.md            # export-cache, enrich --write-cache, build
└── tasks.md         # /speckit-tasks
```

### Source Code (repository root)

```text
src/rain_in_my_head/
├── cache.py      # NEW: paths, append_track/append_artist, read (last-wins), replay(conn, dir), export(conn, dir)
├── config.py     # + CACHE_DIR (env LISTENING_CACHE_DIR, default data/cache)
├── build.py      # build(raw_dir, db_path, cache_dir) replays the cache after scrobbles
├── enrich.py     # enrich_*(..., cache_dir | None): append the line before the DB write
└── cli.py        # + export-cache [--append]; enrich --write-cache; build passes CACHE_DIR

data/cache/
├── tracks.jsonl  # NEW, committed
└── artists.jsonl # NEW, committed

.github/workflows/sync.yml  # fetch → build → enrich --limit 100 --write-cache (continue-on-error) → commit raw + cache
.gitattributes              # NEW: data/raw/** and data/cache/** marked linguist-generated (PR diffs collapse)
README.md                   # cache section; `build` restores enrichment
```

**Structure Decision**: this is a single Python package with no new directories under `src/`. Cache handling lives in its own module, so `build`, `enrich` and `export-cache` share one reader and one writer.

## Complexity Tracking

No violations.
