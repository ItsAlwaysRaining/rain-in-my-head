# Feature Specification: Two-year public dataset and safe SQL page

**Feature Branch**: `feature/public-dataset`

**Created**: 2026-10-27

**Status**: Draft

**Input**: Hosting phase 2. The hosted site must show visitors only two years of listening, and must stay safe when people other than the owner use it. This covers three things:

1. A `publish` command that builds `data/public.db`, a copy of the database limited to a rolling window. It covers the last 730 days, ending 7 days before the build.
2. A read-only mode for the API, where nothing can be written.
3. Limits on the SQL page, so a visitor can't hang the server, read files or attach other databases.

Decided with the owner in the hosting plan: a 730-day window with a 7-day lag; playlists and Streamlit are not hosted.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A two-year copy to put online (Priority: P1)

I run one command and get a small database holding only my last two years of listening, minus the most recent week. It holds no other plays and nothing that isn't needed to show them. The dashboards work on it exactly as they do on the full database, just with less history.

**Why this priority**: this is the "only 2 years" promise. Without it, nothing can be hosted.

**Independent Test**:
1. Run `publish`.
2. Query `public.db` directly: the oldest and newest play, the counts, and any artists or tracks without a play.
3. Point the TypeScript dashboard at it, and click through Overview, Genre, Artist and SQL in a browser.

**Acceptance Scenarios**:

1. **Given** my full database, **When** I run `publish`, **Then** `public.db` holds exactly the plays from 737 days ago up to 7 days ago (about 45,000 today), and none outside that range.
2. **Given** `public.db`, **When** I count tracks and artists, **Then** each one has at least one play in the window, and every play's track and artist is present with its genre tags.
3. **Given** `public.db`, **When** I look for Spotify matches or any other table not needed to show plays, **Then** there are none.
4. **Given** the dashboard running on `public.db`, **When** I open each page, **Then** every page loads and the numbers match a direct query of `public.db`.
5. **Given** I run `publish` a week later, **Then** the window has moved forward by a week.

---

### User Story 2 - The hosted API can't change anything (Priority: P2)

When the API runs on the hosted copy, nothing a visitor does can write to the database or to any file. The pages that save things (the schema layout, playlist creation) say they're unavailable instead.

**Why this priority**: visitors share one copy. Nothing they do should change what the next visitor sees, and the hosted file system is read-only anyway.

**Independent Test**: run the API in read-only mode on `public.db`. Try every route that writes, and check that each is refused with a clear message and that the database file is byte-identical afterwards.

**Acceptance Scenarios**:

1. **Given** read-only mode, **When** a visitor tries to save or reset the schema layout, **Then** they get a "not available on the hosted site" response and nothing is written.
2. **Given** read-only mode, **When** a visitor calls any playlist route, **Then** it's refused in the same way.
3. **Given** read-only mode, **When** every read page is used, **Then** the database file's checksum is unchanged, and no journal or lock file is created next to it.
4. **Given** normal (local) mode, **Then** every route works exactly as before.

---

### User Story 3 - The SQL page is safe to share (Priority: P3)

Visitors I trust can type their own queries on the SQL page. A runaway or hostile query can't slow the site for everyone, read anything outside the listening data, or reveal how the server is set up.

**Why this priority**: SQL is the most powerful page. Phase 4 limits it to trusted codes, but it must be safe even so.

**Independent Test**: on `public.db`, run:
- a normal query
- an endless recursive query
- a query returning 50,000 rows
- an `ATTACH`
- a `PRAGMA`
- a write
- a 10,000-character query
- a syntax error

Check each result against the scenarios below.

**Acceptance Scenarios**:

1. **Given** an ordinary query, **When** I run it, **Then** I get the same result as today.
2. **Given** a query that would run forever, **When** I run it, **Then** it's stopped after about 2 seconds with "Query took too long (limit 2 seconds)".
3. **Given** a query returning more than 1,000 rows, **When** I run it, **Then** I see the first 1,000, with a note that the results were cut off at 1,000 rows.
4. **Given** `ATTACH`, `DETACH`, any `PRAGMA`, or any write or schema change, **When** I run it, **Then** it's refused with "Only SELECT queries are allowed" and nothing happens.
5. **Given** a query over 5,000 characters, **When** I run it, **Then** it's refused before it runs.
6. **Given** invalid SQL, **When** I run it, **Then** the error says what's wrong with the query. It never includes a file path, a server detail or a stack trace.
7. **Given** these limits, **Then** the Streamlit SQL page and the TypeScript SQL page behave the same, including the "cut off" note (constitution VI).

### Edge Cases

- **Example queries that need older data.** "Artists I've stopped listening to" looks for artists last played over 2 years ago, so it finds nothing on `public.db`. It still runs, and shows an empty result rather than an error.
- **Plays exactly on the window's edges.** The start of the window is inclusive and the end is exclusive, so a play is never in two consecutive builds' "edge".
- **Placeholder timestamps.** Plays with placeholder timestamps before 2000 are never inside the window.
- **Re-running `publish`.** It replaces `public.db` completely. It never appends to an old copy.
- **A missing or stale full database.** `publish` refuses to run if the full database doesn't exist, and it never writes to it.
- **The schema page on `public.db`.** It shows the same tables, minus Spotify matches.
- **Recursive queries.** A recursive query that is legitimate, for example a calendar CTE, still works if it finishes within 2 seconds.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A new `publish` command MUST write `data/public.db` from the full database, containing only plays with a timestamp at or after (now − 7 days − 730 days) and before (now − 7 days). The window length, the lag and the output path MUST be options with these defaults.
- **FR-002**: `public.db` MUST contain only the tracks, artists and artist tags referenced by plays in the window. It MUST have the same tables (except Spotify matches) and views as the full database, so every page works unchanged.
- **FR-003**: `public.db` MUST NOT contain Spotify matches, plays outside the window, or any table or file that isn't needed to show plays.
- **FR-004**: `publish` MUST read the full database without changing it, MUST replace the output file whole (writing to a temporary file first), and MUST compact the result.
- **FR-005**: `publish` MUST print the window's dates, the play, track and artist counts, and the file size.
- **FR-006**: The API MUST have a read-only mode, switched on by an environment setting. In it, every database connection opens the file as unchangeable, so no journal, lock or write is ever attempted.
- **FR-007**: In read-only mode, the schema-layout save and reset routes and all playlist routes MUST be refused with a clear "not available on the hosted site" response, and the pages using them MUST say so instead of failing. Outside read-only mode, they MUST work as today.
- **FR-008**: Every read in the API and the shared data functions MUST go through one shared way of opening the database. In read-only mode, nothing may open it for writing.
- **FR-009**: The SQL runner shared by both dashboards MUST allow only reading statements. It MUST refuse ATTACH, DETACH, PRAGMA, writes and schema changes with "Only SELECT queries are allowed".
- **FR-010**: The SQL runner MUST stop any query after 2 seconds with "Query took too long (limit 2 seconds)".
- **FR-011**: The SQL runner MUST return at most 1,000 rows, and say when it cut the results off.
- **FR-012**: The SQL runner MUST refuse queries over 5,000 characters before running them.
- **FR-013**: SQL errors shown to the user MUST describe the query's problem only, with no file paths, server details or stack traces.
- **FR-014**: Both SQL pages MUST show the "cut off at 1,000 rows" note when results are truncated.
- **FR-015**: These SQL limits apply everywhere, locally too, since the runner is shared. Local use is unaffected apart from the limits themselves.
- **FR-016**: The README MUST describe `publish`, read-only mode and the SQL limits.

### Key Entities

- **Public dataset**: the two-year copy. It holds plays in the window, plus the tracks, artists and tags they reference. It has a window start, a window end and a build time.
- **Window**: a rolling period of 730 days, ending 7 days before the build.
- **SQL request**: query text up to 5,000 characters. Its result has up to 1,000 rows, a "cut off" flag, or a plain error message.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `public.db` holds 0 plays outside the window and 0 tracks or artists without a play in it. Both are checked by direct query.
- **SC-002**: `public.db` is under 25 MB, against 92 MB for the full database, and `publish` takes under 30 seconds.
- **SC-003**: Every dashboard page shows the same numbers on `public.db` as a direct query of `public.db`.
- **SC-004**: No SQL query can keep the server busy for more than 3 seconds, or return more than 1,000 rows.
- **SC-005**: None of the 8 hostile or edge queries in story 3's test succeeds in writing, attaching, reading pragmas, or showing a path or server detail.
- **SC-006**: After a full click-through in read-only mode, the database file is byte-identical, and no extra files appear next to it.

## Assumptions

- "Now" is the time `publish` runs. In CI (phase 6), that's each deploy and the nightly rebuild, so the window moves forward once a day.
- The window uses the plays' UTC timestamps, so the edge can be up to a day off local dates. That's acceptable.
- Being cut off at 1,000 rows doesn't affect any built-in page. Only the SQL page runs free-form queries.
- Who may use the SQL page (trusted codes only) is decided in phase 4, not here.
- The hosted site's file system is read-only, which is another reason write routes must be off there.
