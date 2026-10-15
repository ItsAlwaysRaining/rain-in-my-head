---

description: "Tasks for New Artists and Artist Page (issue #5)"
---

# Tasks: New Artists and Artist Page

**Input**: Design documents from `specs/001-new-artist-page/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/artist-page.md, quickstart.md

**Tests**: no automated test suite was requested (the repo has none). Per constitution Principle
III, each story ends with a browser verification task from quickstart.md and a SQLite cross-check.

**Organization**: grouped by user story so each can be checked on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependencies)
- **[Story]**: user story from spec.md (US1, US2, US3)

## Path Conventions

Single project. Dashboard code is in `dashboard/` (entry `dashboard/app.py`, pages in
`dashboard/views/`).

---

## Phase 1: Setup

No setup: no new dependencies, no schema change.

---

## Phase 2: Foundational (blocks all stories)

**Purpose**: shared album-art helpers used by the Overview list and the Artist page.

- [ ] T001 Create `dashboard/lastfm_art.py` with `PLACEHOLDER`, `thumb()`, `most_common()` and `ranked()` moved from `dashboard/views/genre.py`, plus `NO_ART` (inline SVG data URI, `#9995E4` note on `#202030`)
- [ ] T002 Update `dashboard/views/genre.py` to import those helpers from `lastfm_art` and delete its copies; verify with AppTest through `dashboard/app.py` that `/genre` has no exceptions and the same rows as before

**Checkpoint**: helpers shared, Genre page unchanged.

---

## Phase 3: User Story 1 - See this month's new artists (Priority: P1) 🎯 MVP

**Goal**: a "New artists in <period>" table on the Overview.

**Independent Test**: quickstart.md scenarios 1 and 2.

- [ ] T003 [US1] In `dashboard/views/overview.py`, compute the list's period (selected period, else `max(start, first of end's month)` to `end`) and the new artists in it (first play across all data within the period; name, art, plays in the period), sorted by plays then name (data-model.md)
- [ ] T004 [US1] In `dashboard/views/overview.py`, show the table under the "New artists per …" chart, titled "New artists in <period>", with art (`NO_ART` where missing), artist and plays; show a short message when there are none
- [ ] T005 [US1] Verify quickstart.md scenarios 1–2 in headless Chrome and cross-check the default month's rows against the SQLite query

**Checkpoint**: the list works and follows the selected period.

---

## Phase 4: User Story 2 - Open a new artist's page (Priority: P2)

**Goal**: clicking a row opens the Artist page with cover, counts and songs.

**Independent Test**: quickstart.md scenarios 3 and 4.

- [ ] T006 [P] [US2] Create `dashboard/views/artist.py` per contracts/artist-page.md: read `artist`/`start`/`end`; query the artist's plays from `scrobbles` (placeholder art and pre-2000 timestamps filtered as in `genre.py`); header with large cover, name and "N plays in {period} · M all time"; songs table (art, song, album, plays) via `ranked()`
- [ ] T007 [US2] Register the page in `dashboard/app.py` as `st.Page("views/artist.py", url_path="artist", visibility="hidden")`
- [ ] T008 [US2] In `dashboard/views/overview.py`, make the new-artists table selectable (`on_select="rerun"`, `selection_mode=["single-row", "single-cell"]`) and `st.switch_page` to the artist page with `artist`, `start`, `end`
- [ ] T009 [US2] Verify quickstart.md scenarios 3–4 in headless Chrome (click a name and an album art; check counts against SQLite and that song plays sum to the header)

**Checkpoint**: list → artist page works end to end.

---

## Phase 5: User Story 3 - Placeholders and the way back (Priority: P3)

**Goal**: no blank art cells; a link back to the Overview; graceful bad links.

**Independent Test**: quickstart.md scenarios 5–7.

- [ ] T010 [US3] In `dashboard/views/artist.py`, add the "Overview" back link, `NO_ART` for the cover and song rows, and the error states from contracts/artist-page.md (no artist, unknown artist, no plays in the period)
- [ ] T011 [US3] Verify quickstart.md scenarios 5–7 in headless Chrome (find an artist without art via SQLite; open `/artist` and `/artist?artist=nobody`)

**Checkpoint**: all stories work.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T012 [P] Add an "Artist page" section to `README.md` (where the list is, what the page shows, the period it uses) and link it from "Filter by period"
- [ ] T013 Run the full quickstart.md, including scenario 8 (Genre page regression), and note anything not checked for the PR

---

## Dependencies & Execution Order

- Phase 2 (T001–T002) blocks everything.
- US1 (T003–T005) before US2: the list is what US2 clicks.
- US2 (T006–T009): T006 and T007 are independent of each other (different files); T008 needs both.
- US3 (T010–T011) after T006.
- Polish after all stories.

## Parallel Example

```text
After T005:
  T006 [US2] dashboard/views/artist.py
  T007 [US2] dashboard/app.py
Then T008 (overview.py) once both exist.
T012 (README.md) can be written any time after T008.
```

## Implementation Strategy

1. Phase 2, then US1 → verify (MVP: the list alone answers "who's new this month").
2. US2 → verify; US3 → verify.
3. Polish, full quickstart, PR with `Closes #5`.

Commit after each phase; tick tasks here as they finish.
