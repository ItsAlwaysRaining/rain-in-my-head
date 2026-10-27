# Quickstart: validating the enrichment cache

`$S` is a scratch folder outside the repo. Every check below uses a scratch database: none of them touches `data/listening.db`.

## 1. Export once (owner's Mac, on the branch)

```sh
uv run rain-in-my-head export-cache
uv run rain-in-my-head export-cache        # must refuse: files already have lines
wc -l data/cache/*.jsonl                   # 76,556 tracks and 24,263 artists today
du -h data/cache/*.jsonl                   # about 15 MB and 5 MB
```

## 2. A fresh clone rebuilds everything (US1, SC-001, SC-002)

```sh
git clone --branch feature/enrichment-cache <repo> $S/clone   # after the export is committed and pushed
cd $S/clone && time env -u LASTFM_API_KEY LISTENING_DB=$S/fresh.db uv run --no-default-groups rain-in-my-head build
```

- **Expected**: under 2 minutes, with no network calls.
- **Cross-check against the local database** (constitution III):

```sh
for db in <repo>/data/listening.db $S/fresh.db; do
  sqlite3 "$db" "SELECT (SELECT COUNT(*) FROM tracks),(SELECT COUNT(*) FROM artists),(SELECT COUNT(*) FROM artist_tags);"
  sqlite3 "$db" "SELECT primary_genre, COUNT(*) FROM v_plays WHERE primary_genre IS NOT NULL GROUP BY 1 ORDER BY 2 DESC LIMIT 20;" | md5
done
```

- **Expected**: identical counts and an identical hash.
- **No lookups left**: `LISTENING_DB=$S/fresh.db uv run rain-in-my-head enrich --limit 1` reports `Artists to look up: 0` and `Tracks to look up: 0`.

## 3. A second build changes nothing (FR-006)

Run `build` again on `$S/fresh.db` and on a copy of the local database. The counts and the genre hash must not change.

## 4. Appending (US2)

Copy the database to `$S/a.db`, delete one artist (its row and its tags) and one track, and copy `data/cache` to `$S/cache`. Then:

```sh
LISTENING_DB=$S/a.db LISTENING_CACHE_DIR=$S/cache uv run rain-in-my-head enrich --limit 1 --write-cache
```

- **Expected**: `$S/cache` gains exactly one line in each file. Those lines match the rows now in `$S/a.db`.
- **Without the flag**: run it again on a fresh copy without `--write-cache`. The cache files are unchanged.
- **Cut-off line**: add a cut-off line (`printf '{"artist_key":"x' >> $S/cache/artists.jsonl`), then `build`. It reports `skipped …artists.jsonl:<n>` and finishes.

## 5. Scheduled sync (US3, SC-004)

Trigger `Sync scrobbles` on the branch with `gh workflow run sync.yml --ref feature/enrichment-cache` after a few new plays.

- **Expected**:
  - The run succeeds in under 3 minutes.
  - Its commit contains the new raw lines plus cache lines for any new track or artist.
  - A second run right after makes no commit.

The branch run commits to the branch, not to `main`.
