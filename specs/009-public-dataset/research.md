# Research: Two-year public dataset and a read-only hosted API

## R1. How `publish` copies the window

- **Decision**:
  1. Create a temp file `<out>.tmp` with `build.connect`, so it gets the schema, views and indexes.
  2. `ATTACH 'file:<full db>?mode=ro' AS src` (URI).
  3. Run `INSERT … SELECT` for the scrobbles in the window, then for the `tracks`, `artists` and `artist_tags` whose keys appear in those scrobbles.
  4. `DETACH`, `DROP TABLE spotify_matches`, `PRAGMA journal_mode=DELETE`, `VACUUM`, close.
  5. `os.replace` the temp file over `<out>`.
- **Rationale**:
  - SQL-only copying is fast: about 45k rows in well under a second.
  - The views come from the same `schema.sql`, so they match the full database exactly.
  - `journal_mode=DELETE` leaves a single self-contained file. `build.connect` turns on WAL, and an immutable open needs no `-wal` file.
  - `os.replace` means a half-built file is never served.
- **Alternatives**:
  - Copy the whole file, then delete what's outside the window. Rejected: slower, and it relies on `VACUUM` to really drop the deleted data.
  - pandas. Rejected: `publish` must run with core dependencies only.

## R2. Window boundaries

- **Decision**:
  - `end = floor(now) − lag_days × 86400`
  - `start = end − window_days × 86400`
  - keep `start ≤ played_at < end`
  - all in Unix seconds (UTC)
- **Rationale**: start inclusive and end exclusive (spec edge case). Placeholder timestamps before 2000 fall outside automatically.

## R3. The hosted-mode switch

- **Decision**: `LISTENING_HOSTED=1`, read once in `config.HOSTED`. `build.connect_readonly` opens `file:<path>?mode=ro&immutable=1` when hosted, and `mode=ro` otherwise.
- **Rationale**: one name for "this is the hosted site" covers both the database and the route guard. `immutable=1` tells SQLite the file can't change, so it takes no locks and opens no journal (SC-006). Vercel's read-only file system needs that.
- **Alternatives**: a separate `LISTENING_DB_READONLY` flag, as the hosting plan first said. Rejected: two switches that must always match.

## R4. Guarding routes: deny by default

- **Decision**: an HTTP middleware that's active only when `HOSTED`:
  - **Allow** any `GET`, except paths starting with `/api/playlists` or `/api/ai`.
  - **Allow** `POST /api/sql`.
  - **Refuse** everything else with `403 {"error": "refused", "message": config.REFUSAL}`.
- **Rationale**:
  - FR-007, FR-011 and FR-018: a new write or AI route added later is refused without anyone remembering to list it (constitution VII).
  - Phase 4's login and logout routes will be added to the allow list explicitly.
- **Alternatives**: a dependency on each write route. Rejected: easy to forget on a new route.

## R5. Pre-defined queries on the hosted SQL route

- **Decision**:
  - `SqlRequest` becomes `{sql?: str, example?: str}`.
  - **Hosted**: only `example` is accepted, and it must be a key of `sql_examples.EXAMPLES`. The server runs `EXAMPLES[name]` through the existing read-only runner. Anything else gets the refusal.
  - **Local**: `sql` works as now, and `example` works too.
  - `/api/sql/meta` and `/api/health` return `"hosted": bool`, so the page knows which UI to show.
- **Rationale**: the server never runs visitor text (SC-004). The examples are already defined once, in one place shared with Streamlit (FR-012).

## R6. Timezone (carried to phase 6)

- **Finding**: `v_plays` computes `played_local` with `datetime(played_at, 'unixepoch', 'localtime')`. On Vercel, local time is UTC.
- **Decision**: out of scope here. Phase 6 either sets the function's `TZ`, which isn't allowed on some runtimes, or `publish` gains a `--tz` option that stores an offset. It's listed in plan.md's risks.

## R7. Immutable opens and the plays cache

- **Finding**: `overview.load_plays` caches by the file's modification time. An immutable database never changes in place, and a new deploy is a new process, so the cache is always correct.
