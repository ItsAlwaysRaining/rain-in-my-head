# Feature Specification: Enrichment cache in git

**Feature Branch**: `feature/enrichment-cache`

**Created**: 2026-10-27

**Status**: Draft

**Input**: User description: "Enrichment cache in git (hosting phase 1)". Today every Last.fm lookup made by `enrich` (track details, artist details, artist tags) lives only in the gitignored `data/listening.db`. A fresh clone or a CI runner can rebuild the scrobbles but not the genres, durations or artist details. This is phase 1 of the hosting plan: phase 2 builds the hosted two-year database in CI, which needs this. Constitution v1.2.0 (principle I) already allows `data/cache/` to be committed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A fresh copy rebuilds everything (Priority: P1)

I clone the repo somewhere new, or CI does, and run `build`. The database I get has the same tracks, artists and genres as the one on my Mac. Last.fm isn't called again for anything that was already looked up.

**Why this priority**: this is what hosting needs. Without it, CI would have to redo about 125,000 Last.fm calls before every deploy, or ship a database without genres.

**Independent Test**: run the one-time export on my Mac and commit the cache. Then, in a fresh clone in a scratch folder with no `.env` and no network access to Last.fm, run `build`. Compare the new database with mine: row counts, then the top 20 genres by plays.

**Acceptance Scenarios**:

1. **Given** the committed cache and raw scrobbles, **When** I run `build` in a fresh clone, **Then** the tracks, artists and artist tags counts match my local database exactly (76,556 / 24,263 / 74,391 today).
2. **Given** that rebuilt database, **When** I list the top 20 genres by play count, **Then** the list and its numbers are identical to my local database.
3. **Given** the rebuilt database, **When** I run `enrich`, **Then** it reports 0 tracks and 0 artists to look up.
4. **Given** my existing local database, **When** I run `build` again, **Then** nothing changes: same counts, same top 20 genres.

---

### User Story 2 - New lookups are saved where git can see them (Priority: P2)

When the sync's `enrich` looks something up, the result goes into the committed cache as well as the database. A lookup is never lost just because it only reached one machine's database. A plain `enrich` on my Mac leaves the committed files alone (FR-010).

**Why this priority**: without it, the cache goes stale from the day it's exported. It depends on story 1's file format.

**Independent Test**: delete one artist and one track from a scratch copy of the database, run `enrich --limit 1` with cache writing on and the cache pointed at a scratch folder, and check that the cache gained exactly one artist line and one track line, matching what was written to the database.

**Acceptance Scenarios**:

1. **Given** an artist not yet in the cache, **When** `enrich` looks it up, **Then** one line is appended to the artists cache, holding the artist's details and tags. The same values are written to the database.
2. **Given** a track not yet in the cache, **When** `enrich` looks it up, **Then** one line is appended to the tracks cache.
3. **Given** `enrich` is stopped part-way (Ctrl-C), **When** I run it again, **Then** every lookup that finished before the stop is in both the cache and the database, and the cache has no half-written line.
4. **Given** a key with more than one line in the cache, **When** `build` replays it, **Then** the last line wins.

---

### User Story 3 - The scheduled sync keeps enrichment up to date (Priority: P3)

Every 6 hours the sync workflow fetches new scrobbles, looks up any new tracks and artists, and commits both the scrobbles and the new cache lines to `main`. New music shows its genre without me running anything.

**Why this priority**: it removes the last thing I'd have to run by hand. Stories 1 and 2 still work without it if I enrich locally.

**Independent Test**: run the workflow by hand (`workflow_dispatch`) on the branch after a few new plays. The run commits new cache lines for the new tracks and artists, and finishes within the time limit below.

**Acceptance Scenarios**:

1. **Given** new scrobbles of a track never played before, **When** the sync runs, **Then** its commit includes the new scrobbles and a tracks cache line for that track.
2. **Given** nothing new since the last run, **When** the sync runs, **Then** it makes no commit.
3. **Given** more new items than one run's lookup limit, **When** syncs keep running, **Then** the backlog clears over several runs, most-played first.
4. **Given** the sync runs as it does today, **Then** it still installs no dashboard dependencies.

### Edge Cases

- **Lookups that find nothing.** Last.fm returns no data for a track or artist. It is cached anyway (name only, empty details, no tags), so it isn't retried every run. This matches what the database does today: 13,687 tracks have no duration.
- **Artists with no tags.** About 5,400 artists have no tags. They're cached with an empty tag list, and replaying that removes any tags the database had for them.
- **A damaged last line.** If a process is killed mid-write and the final line is cut off, `build` skips that line, says so, and carries on. It never crashes, and never silently drops a good line.
- **The same file changed in two places.** If both the sync and my Mac appended to the cache, git could conflict at the end of the file. FR-010 prevents this: only the sync writes it. A plain local `enrich` that runs before the next sync will look up the same item the sync later looks up. That's one extra call, and `build` then takes the sync's line.
- **Cache entries for music no longer in the scrobbles.** They're still loaded into the database. This is harmless, and the same as the database today.
- **File size.** The export is about 15 MB. A file must stay well under GitHub's 100 MB per-file limit. Growth is a few hundred lines a week.
- **A cache directory that doesn't exist yet.** `build` treats it as empty, and `enrich` creates it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repo MUST hold a committed cache of Last.fm lookups in `data/cache/`. Track lookups and artist lookups go in separate files, one JSON object per line. Each artist line holds the artist's tags with their weights.
- **FR-002**: The cache MUST be append-only. A redone lookup is appended, and the last line for a key wins (constitution I).
- **FR-003**: A new one-time `export-cache` command MUST write the current tracks, artists and artist tags from the local database into the cache. It MUST refuse to run if the cache files already hold lines, unless told to append anyway.
- **FR-004**: `build` MUST replay the cache into the database after loading scrobbles, so that a fresh clone with no Last.fm access gets the same tracks, artists and artist tags as the database the cache was exported from.
- **FR-005**: Replaying an artist line MUST replace that artist's tags with exactly the tags on the line, matching what `enrich` does today.
- **FR-006**: Running `build` again on an up-to-date database MUST leave tracks, artists and artist tags unchanged.
- **FR-007**: When asked to write the cache (see FR-010), `enrich` MUST append one cache line for each lookup, holding the same values it writes to the database. The line MUST be fully written before `enrich` moves on to the next lookup.
- **FR-008**: `enrich` MUST skip anything already in the database, as now. After a `build` from the cache, that means anything already in the cache.
- **FR-009**: The cache location MUST default to `data/cache/` and be overridable by an environment variable, the same way the raw scrobbles folder is.
- **FR-010**: Once this is merged, the scheduled sync is the only routine writer of the committed cache. A plain `enrich` on my Mac updates only my local database and leaves `data/cache/` untouched, so `git pull` never conflicts with the bot's commits. Cache writing (FR-007) happens only when `enrich` is explicitly asked for it, which the sync workflow does. My Mac gets the bot's lookups by pulling and running `build`. *(Decided with the owner, 2026-10-27.)*
- **FR-011**: The sync workflow MUST run fetch, then build, then enrich with a per-run lookup limit (100 tracks and 100 artists), then commit both the raw scrobbles and the cache in one commit. It MUST keep installing only the core dependencies.
- **FR-012**: A failed or rate-limited lookup during the sync MUST NOT lose the scrobbles fetched in the same run. If enrichment fails, the run still commits whatever it fetched and cached.
- **FR-013**: Spotify matches are NOT cached in git. They stay in the local database only.
- **FR-014**: The README MUST say that the cache is committed and append-only, when to run `export-cache`, and that `build` now restores enrichment.

### Key Entities

- **Track lookup**: the result of one Last.fm track lookup. It holds the track's key, its artist's key, its display name, its duration (if known), Last.fm's listener and play counts, and when it was looked up.
- **Artist lookup**: the result of one Last.fm artist lookup. It holds the artist's key, display name, MusicBrainz id (if any), listener and play counts, when it was looked up, and the artist's tags (each a name and a weight; up to 10, already filtered as `enrich` does today).
- **Cache file**: an append-only list of lookups of one kind. Its current state is the last line for each key.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A fresh clone rebuilds the full enriched database with zero Last.fm calls, in under 2 minutes on my Mac.
- **SC-002**: The rebuilt database matches the local one exactly on tracks, artists and artist tags counts, and on the top 20 genres by plays (names and play counts).
- **SC-003**: After the change, no new track or artist stays without a lookup for more than 24 hours, unless more than 400 new items arrive in one day.
- **SC-004**: A scheduled sync run with nothing new still takes under 3 minutes. The total stays well inside the free 2,000 Actions minutes a month (about 120 used today).
- **SC-005**: The committed cache is under 25 MB at export, and no cache file is over 50 MB.

## Assumptions

- The cache stores the values `enrich` already keeps (after tag filtering), not Last.fm's raw responses. Changing the tag filter later would need fresh lookups, as it does today.
- Keys are the existing normalised track and artist keys, so a change to the normalising rules would need a new export. `build` already re-derives scrobble keys, but cache keys are kept as written.
- The one-time export is run once on my Mac, and committed on this feature branch. The scheduled sync only starts appending after this branch is merged.
- Last.fm's rate limit (about 5 calls a second) allows 100 artists (2 calls each) and 100 tracks in about a minute per run.
- The local database on my Mac is complete today: every scrobbled track and artist has been looked up.
