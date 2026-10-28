# Feature Specification: Two-year public dataset and a read-only hosted API

**Feature Branch**: `feature/public-dataset`

**Created**: 2026-10-27

**Status**: Draft

**Input**: Hosting phase 2. The hosted site must show visitors only two years of listening, and must stay safe when people other than the owner use it. This covers three things:

1. A `publish` command that builds `data/public.db`, a copy of the database limited to a rolling window. It covers the last 730 days, ending 7 days before the build.
2. A read-only mode for the API, where nothing can be written.
3. No free-form SQL and no AI for visitors. In hosted mode, the SQL page offers only the owner's pre-defined queries: visitors pick one and see its results, but can't edit them or type their own. AI routes are switched off. *(Decided with the owner, 2026-10-27; this replaces the earlier plan to put limits on free-form SQL.)*

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

**Independent Test**: run the API in read-only mode on `public.db`. Try every route that writes, and check that each is refused with "This DJ doesn't take requests." and that the database file is byte-identical afterwards.

**Acceptance Scenarios**:

1. **Given** read-only mode, **When** a visitor tries to save or reset the schema layout, **Then** they get "This DJ doesn't take requests." and nothing is written.
2. **Given** read-only mode, **When** a visitor opens the Playlists page or calls any playlist route, **Then** it's refused with "This DJ doesn't take requests." (FR-018).
3. **Given** read-only mode, **When** every read page is used, **Then** the database file's checksum is unchanged, and no journal or lock file is created next to it.
4. **Given** normal (local) mode, **Then** every route works exactly as before.

---

### User Story 3 - Pre-defined queries only, and no AI, for visitors (Priority: P3)

On the hosted site, visitors can browse every chart. On the Analyst page they can pick any of my pre-defined queries (such as "Top artists this year" or "Plays by genre"), see its results, and read its SQL, but they can't change it or type their own. The schema map stays. The AI page shows its "Coming soon" card, and any AI action is refused.

**Why this priority**: free-form SQL and AI are the two features that let a visitor make the server do open-ended work. AI would also spend the owner's money and use their API keys. With only pre-defined queries, every query that can run on the server is one the owner wrote, so injection is impossible, and the page is still fun to show off.

**Independent Test**: in hosted (read-only) mode on `public.db`:
1. Run each pre-defined query from the Analyst page.
2. Call the SQL route directly with free-form SQL, including a hostile query, and with a query name that doesn't exist.
3. Open the AI page.

Then check that locally, without hosted mode, the SQL page works exactly as today.

**Acceptance Scenarios**:

1. **Given** hosted mode, **When** a visitor opens the Analyst page, **Then** they see the schema map and a list of pre-defined queries. Choosing one shows its SQL (read-only) and its results. There's no editable query box.
2. **Given** hosted mode, **When** anyone sends free-form SQL to the API, **Then** it's refused with "This DJ doesn't take requests." and nothing is executed.
3. **Given** hosted mode, **When** anyone asks for a pre-defined query by a name that doesn't exist, **Then** it's refused with the same message.
4. **Given** hosted mode, **When** a visitor opens the AI page, **Then** they see the "Coming soon" card. Any AI route, now or added later, is refused with "This DJ doesn't take requests."
5. **Given** local mode (no hosted setting), **When** I use the SQL page, **Then** it works exactly as today, with free-form SQL and the examples as starting points.

### Edge Cases

- **Plays exactly on the window's edges.** The start of the window is inclusive and the end is exclusive, so a play is never in two consecutive builds' "edge".
- **Placeholder timestamps.** Plays with placeholder timestamps before 2000 are never inside the window.
- **Re-running `publish`.** It replaces `public.db` completely. It never appends to an old copy.
- **A missing or stale full database.** `publish` refuses to run if the full database doesn't exist, and it never writes to it.
- **The schema page on `public.db`.** It shows the same tables, minus Spotify matches.
- **Pre-defined queries that need older data.** "Artists I've stopped listening to" looks for artists last played over 2 years ago, so it finds nothing on `public.db`. It still runs and shows an empty result, not an error.
- **The schema map on the hosted site.** It only reads table and column names from `public.db`, so it stays available.
- **AI routes added later.** Any route that uses AI must be on the hosted-mode refusal list from the day it's added.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A new `publish` command MUST write `data/public.db` from the full database, containing only plays with a timestamp at or after (now − 7 days − 730 days) and before (now − 7 days). The window length, the lag and the output path MUST be options with these defaults.
- **FR-002**: `public.db` MUST contain only the tracks, artists and artist tags referenced by plays in the window. It MUST have the same tables (except Spotify matches) and views as the full database, so every page works unchanged.
- **FR-003**: `public.db` MUST NOT contain Spotify matches, plays outside the window, or any table or file that isn't needed to show plays.
- **FR-004**: `publish` MUST read the full database without changing it, MUST replace the output file whole (writing to a temporary file first), and MUST compact the result.
- **FR-005**: `publish` MUST print the window's dates, the play, track and artist counts, and the file size.
- **FR-006**: The API MUST have a read-only mode, switched on by an environment setting. In it, every database connection opens the file as unchangeable, so no journal, lock or write is ever attempted.
- **FR-007**: In read-only mode, the schema-layout save and reset routes and all playlist routes MUST be refused with "This DJ doesn't take requests.", and the pages using them MUST say so instead of failing. Outside read-only mode, they MUST work as today.
- **FR-008**: Every read in the API and the shared data functions MUST go through one shared way of opening the database. In read-only mode, nothing may open it for writing.
- **FR-009**: In hosted (read-only) mode, the SQL route MUST accept only the name of a pre-defined query, and MUST run that query's SQL as written in the code. Free-form SQL, or an unknown name, MUST be refused without running anything, with "This DJ doesn't take requests." The schema information routes stay available.
- **FR-010**: In hosted mode, the Analyst page MUST show the schema map and the list of pre-defined queries. Choosing one shows its SQL as read-only text and its results. There MUST be no editable query box.
- **FR-011**: In hosted mode, every AI route MUST be refused with "This DJ doesn't take requests." That covers today's none and any added later. The AI page shows only its "Coming soon" card.
- **FR-012**: Outside hosted mode, SQL behaves exactly as today. The pre-defined queries are the same list both modes use, defined once.
- **FR-013**: Table names in the SQL examples' schema listing MUST be quoted the same safe way as on the Schema page. It's a consistency fix: those names come from the database itself, not from visitors.
- **FR-016**: The README MUST describe `publish`, hosted read-only mode, and which features are off there (SQL, AI, playlists, layout saving).
- **FR-017**: No one but the owner may create playlists on the owner's Spotify account. The hosted site MUST NOT hold any Spotify credential (the token file or the client ID), so playlist creation is impossible there even if a route were left on. In read-only mode, every playlist route is refused (FR-007). *(Owner's requirement, 2026-10-27.)*
- **FR-018**: Every refusal on the hosted site MUST say exactly **"This DJ doesn't take requests."** That covers blocked writes (schema layout), playlists, free-form or unknown SQL, AI, and any route refused in hosted mode in future. It applies both in API responses and on the pages that show them. No other refusal wording is used. *(Owner's wording, 2026-10-27.)*

### Key Entities

- **Public dataset**: the two-year copy. It holds plays in the window, plus the tracks, artists and tags they reference. It has a window start, a window end and a build time.
- **Window**: a rolling period of 730 days, ending 7 days before the build.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `public.db` holds 0 plays outside the window and 0 tracks or artists without a play in it. Both are checked by direct query.
- **SC-002**: `public.db` is under 25 MB, against 92 MB for the full database, and `publish` takes under 30 seconds.
- **SC-003**: Every dashboard page shows the same numbers on `public.db` as a direct query of `public.db`.
- **SC-004**: In hosted mode, 0 visitor-supplied SQL statements are executed, and every pre-defined query returns the same rows as running its SQL directly on `public.db`.
- **SC-005**: In hosted mode, every AI and playlist route returns its refusal message. Checked for each route.
- **SC-006**: After a full click-through in read-only mode, the database file is byte-identical, and no extra files appear next to it.

## Assumptions

- "Now" is the time `publish` runs. In CI (phase 6), that's each deploy and the nightly rebuild, so the window moves forward once a day.
- The window uses the plays' UTC timestamps, so the edge can be up to a day off local dates. That's acceptable.
- There are no tiers for SQL or AI on the hosted site. Everyone there gets pre-defined queries only and no AI. The owner uses free-form SQL locally.
- The hosted site's file system is read-only, which is another reason write routes must be off there.
- **Only the TypeScript dashboard is hosted. Streamlit stays local only** (confirmed with the owner, 2026-10-27). Streamlit is never deployed, so it needs no hosted-mode changes.
- **The hosted site is read-only for everyone, the owner included** (decided with the owner, 2026-10-27). The owner changes listening data and layouts on their Mac, and those changes arrive with the next deploy. On the hosted site, the owner code adds only the Visitors page and invite management (phase 4). Every write route there is refused, whatever the code.
