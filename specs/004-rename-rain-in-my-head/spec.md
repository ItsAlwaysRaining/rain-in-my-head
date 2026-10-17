# Feature Specification: Rename to rain-in-my-head

**Feature Branch**: `feature/rename-rain-in-my-head`

**Created**: 2026-10-16

**Status**: Draft

**Input**: User description: "Rename the app and repo to a more fitting name" (issue #13). The owner chose the name **rain-in-my-head**. Decided with the owner: rename everywhere, including the Python package and the command; do it now, before the remaining TypeScript dashboard slices; after the PR is merged, Claude renames the GitHub repository and the owner moves the local folder.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One name in everything I type and see (Priority: P1)

I run the project's commands and open either dashboard, and everywhere it is called rain-in-my-head:
the command I type, the browser tab title, the app heading, the README and the project's own rules.
Nothing calls it "spotify-music-analysis" or "listening" any more, except where the words describe
listening history or the real Spotify playlist feature.

**Why this priority**: this is the point of the issue. Today the repo, the command and the dashboards
each use a different name.

**Independent Test**: on the branch, run every command in the README with the new name, open both
dashboards and read the tab titles and headings, then search the repo for the old names.

**Acceptance Scenarios**:

1. **Given** a fresh install from the branch, **When** I run `uv run rain-in-my-head fetch`, `build`,
   `enrich`, `stats`, `serve`, `spotify-login` and `playlist --dry-run`, **Then** each behaves exactly as
   the same `listening` command did before.
2. **Given** the old command, **When** I run `uv run listening build`, **Then** it is not found; there is
   no leftover alias.
3. **Given** the Streamlit dashboard, **When** I open it, **Then** the browser tab and the app heading use
   the display name "Rain in My Head".
4. **Given** the TypeScript dashboard, **When** I open it, **Then** its tab title and heading use the same
   display name as Streamlit.
5. **Given** the repo, **When** I search tracked files for "spotify-music-analysis" and for the old
   package and command name, **Then** the only matches are in historical records (completed specs,
   archived changes, past comparison-log entries), in the post-merge steps that explain the rename, and
  in the database file and settings names kept by FR-007.

---

### User Story 2 - Nothing I already have breaks (Priority: P1)

My listening history, the database, my Spotify login and the scheduled sync keep working through the
rename. Both dashboards show the same numbers before and after.

**Why this priority**: the history is irreplaceable (constitution Principle I), and the sync runs every
6 hours whether or not I'm watching.

**Independent Test**: note the Overview numbers before the change, then after: rebuild, open both
dashboards and compare; run the sync workflow's command locally without the dashboard dependencies.

**Acceptance Scenarios**:

1. **Given** an existing local database, Spotify token and `.env`, **When** I switch to the branch and
   run `build`, **Then** no data is lost, nothing needs deleting, and I don't have to log in to Spotify
   again.
2. **Given** both dashboards, **When** I open the Overview for the same period before and after the
   rename, **Then** every number is identical.
3. **Given** the scheduled sync, **When** it next runs on `main` after the merge, **Then** it fetches and
   commits new scrobbles as before.
4. **Given** the raw scrobble files, **Then** none of them is changed by the rename.

---

### User Story 3 - The repo and my machine follow the new name (Priority: P2)

After the PR is merged, the GitHub repository is called rain-in-my-head and has a description, my
clone points at it, and I have clear steps for the things only I can do: moving the local folder, moving
Claude's project memory with it, and renaming the Spotify developer app.

**Why this priority**: the code rename is useful on its own; this finishes the job but only after merge.

**Independent Test**: after merge, open the repo on GitHub, check the remote of the local clone, follow
the written steps and confirm Claude still recalls its memory in the moved folder.

**Acceptance Scenarios**:

1. **Given** the PR is merged, **When** Claude renames the repository, **Then** it is
   `ItsAlwaysRaining/rain-in-my-head`, has a one-line description, and the old URL redirects to it.
2. **Given** the renamed repository, **When** I run `git remote -v` in the clone, **Then** it shows the
   new URL, and `git pull` works.
3. **Given** the written steps, **When** I move the clone folder and the memory folder, **Then** a new
   Claude session in the new folder still has its saved memories.
4. **Given** the written steps, **When** I rename the Spotify developer app, **Then** playlist creation
   still works without changing `.env` or logging in again.

### Edge Cases

- A scheduled sync commits to `main` while the PR is open: the branch is updated from `main` before
  review; the raw files merge without conflict because the rename doesn't touch them.
- The rename PR merges while a sync run is in progress: that run used the old command on the old
  checkout and finishes normally; the next run uses the new command.
- The scheduled sync runs between the merge and the repository rename: it works, because the workflow
  doesn't name the repository.
- Unmerged branches (`feature/new-artist-page` holds spec 001): they still mention the old package path.
  Their specs are updated on that branch, and later code there uses the new name.
- A stale install in `.venv` still provides the old command after switching branch: syncing the
  environment removes it; the README says to run `uv sync` after pulling the rename.
- Words that describe listening ("listening history", "Biggest listening days") and the real Spotify
  integration (`spotify.py`, `playlist.py`, the Playlists page, the `spotify_matches` table) are not
  renamed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The installable project, its importable package and its command MUST all be named
  rain-in-my-head (with underscores where a name can't contain hyphens). Every subcommand and option
  MUST behave as before.
- **FR-002**: The old command name and old package name MUST NOT remain available; there is no
  compatibility alias.
- **FR-003**: Both dashboards MUST use the new display name in the browser tab title and the app
  heading, and the TypeScript app's package metadata MUST use the new name.
- **FR-004**: The README, `CLAUDE.md`, the constitution, the OpenSpec config, the living OpenSpec specs,
  the comparison log's general text, and the tasks not yet done in spec 003 MUST use the new name,
  command and paths.
- **FR-005**: Completed specs (001's merged parts, 002, 003's done tasks), archived OpenSpec changes and
  past comparison-log entries MUST be left as written, as a record of what was true then.
- **FR-006**: The scheduled sync workflow MUST use the new command and keep running without dashboard
  dependencies.
- **FR-007**: The database file `data/listening.db` and the settings `LISTENING_DB` and
  `LISTENING_RAW_DIR` MUST keep their names: "listening" there describes the data, not the app, and
  keeping them means nothing has to move.
- **FR-008**: The raw scrobble files, the database contents, `.env` and the Spotify token MUST NOT be
  changed or need re-creating.
- **FR-009**: Text that describes listening activity, and everything belonging to the real Spotify
  integration, MUST NOT be renamed.
- **FR-010**: After the PR is merged, the GitHub repository MUST be renamed to `rain-in-my-head` with a
  one-line description, and the local clone's remote updated to the new URL.
- **FR-011**: The README MUST include the one-off steps for after the merge: `uv sync`, moving the local
  folder, moving Claude's project memory folder to match the new path, and renaming the Spotify
  developer app.

### Key Entities

- **Name forms**: the repository and command name (`rain-in-my-head`), the importable name
  (`rain_in_my_head`), and the display name used in titles and headings ("Rain in My Head").
- **Historical record**: specs, archived changes and log entries that describe finished work and keep
  the names used at the time.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every command listed in the README runs with the new name, and 0 run with the old one.
- **SC-002**: A search of tracked files finds 0 uses of the old names outside the historical records,
  descriptive text, the rename steps and the names kept by FR-007.
- **SC-003**: Both dashboards show identical Overview numbers before and after the rename for the same
  period, and match a direct database query.
- **SC-004**: The first scheduled sync after the merge succeeds and commits new scrobbles.
- **SC-005**: After the post-merge steps, the repository, the clone's remote, the local folder and
  Claude's memory all use the new name, with 0 memories lost and no new Spotify login.

## Assumptions

- GitHub keeps redirecting the old repository URL, so links in old PRs and issues keep working.
- The scheduled sync doesn't refer to the repository by name, so renaming the repository doesn't affect it.
- Spotify identifies the app by its client ID, so renaming the developer app changes nothing in `.env`
  or the saved token.
- The `listening-palette.html` reference page is renamed to match, along with the palette's name inside it.
- Claude's project memory is stored in a folder named after the clone's path; moving the clone without
  moving that folder would start a new, empty memory.
