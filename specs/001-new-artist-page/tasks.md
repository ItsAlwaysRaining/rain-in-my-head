---

description: "Tasks for New Artists and Artist Page (issue #5), both dashboards"
---

# Tasks: New Artists and Artist Page

**Input**: Design documents from `specs/001-new-artist-page/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/artist-page.md, quickstart.md

**Tests**: no automated test suite was requested (the repo has none). Per constitution Principle
III, each story ends with a browser verification task from quickstart.md and a SQLite cross-check.

**Organization**: grouped by user story so each can be checked on its own. Revised 2026-10-18 for
both dashboards; the old T001–T002 (moving the album-art helpers) were done in spec 003.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependencies)
- **[Story]**: user story from spec.md (US1, US2, US3)

## Path Conventions

Shared data code in `src/rain_in_my_head/`; Streamlit in `dashboard/` (pages in `dashboard/views/`);
TypeScript in `web/src/` (pages in `web/src/pages/`), reading `src/rain_in_my_head/api.py`.

---

## Phase 1: Setup

No setup: no new dependencies, no schema change.

---

## Phase 2: Foundational (blocks all stories)

**Purpose**: the shared data functions and the placeholder image both apps use.

- [x] T001 Create `src/rain_in_my_head/artist.py` with `period_label`, `list_period`, `new_artists(db_path, start, end)` and `artist_page(db_path, artist_key, start, end)` per data-model.md, reusing `ranked`, `most_common`, `thumb` and `PLACEHOLDER` from `rain_in_my_head.genre`
- [x] T002 [P] Create `web/public/no-art.svg` (music note, Night `#8C9FE0` on Night Surface `#1C2238`) and check it at 64px
- [x] T003 Cross-check `new_artists` for the latest month and `artist_page` for one artist against the SQLite queries in quickstart.md

**Checkpoint**: shared functions return the right rows.

---

## Phase 3: User Story 1 - See this month's new artists (Priority: P1) 🎯 MVP

**Goal**: a "New artists in <period>" table on the Overview in both apps.

**Independent Test**: quickstart.md scenarios 1 and 2.

- [ ] T004 [US1] In `src/rain_in_my_head/api.py`, add `new_artist_list` to `/api/overview` (contract); add its types to `web/src/api.ts`
- [ ] T005 [P] [US1] Streamlit: in `dashboard/views/overview.py`, show the table under the "New artists per …" chart, titled "New artists in <label>", with art (placeholder where missing), artist and plays; a short message when there are none
- [ ] T006 [P] [US1] TypeScript: the same table in `web/src/pages/Overview.tsx`
- [ ] T007 [US1] Verify quickstart.md scenarios 1–2 in both apps in headless Chrome

**Checkpoint**: the list works and follows the selected period in both apps.

---

## Phase 4: User Story 2 - Open a new artist's page (Priority: P2)

**Goal**: clicking a row opens the Artist page with cover, counts and songs.

**Independent Test**: quickstart.md scenarios 3 and 4.

- [ ] T008 [US2] Add `GET /api/artist` to `src/rain_in_my_head/api.py` (contract) and `fetchArtist` to `web/src/api.ts`
- [ ] T009 [P] [US2] Streamlit: create `dashboard/views/artist.py` per contracts/artist-page.md; register it in `dashboard/app.py` as `st.Page("views/artist.py", url_path="artist", visibility="hidden")`; make the Overview table selectable (`on_select="rerun"`, `selection_mode=["single-row", "single-cell"]`) and `st.switch_page` to it with `artist`, `start`, `end`
- [ ] T010 [P] [US2] TypeScript: create `web/src/pages/Artist.tsx` (+ `Artist.module.css`); add the `/artist` route to `web/src/App.tsx` outside the menu; make the Overview table's rows navigate to it
- [ ] T011 [US2] Verify quickstart.md scenarios 3–4 in both apps (click a name and an album art; check counts against SQLite and that song plays sum to the header)

**Checkpoint**: list → artist page works end to end in both apps.

---

## Phase 5: User Story 3 - Placeholders and the way back (Priority: P3)

**Goal**: no blank art cells; a link back to the Overview; graceful bad links.

**Independent Test**: quickstart.md scenarios 5–7.

- [ ] T012 [US3] In both artist pages, the "Overview" back link, the placeholder for the cover and song rows, and the error states from contracts/artist-page.md (no artist, unknown artist, no plays in the period)
- [ ] T013 [US3] Verify quickstart.md scenarios 5–7 in both apps (find an artist without art via SQLite; open `/artist` and `/artist?artist=zz-no-such-artist`)

**Checkpoint**: all stories work.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T014 [P] Add an "Artist page" section to `README.md` (where the list is, what the page shows, the period it uses, both apps) and mention it in "Filter by period"
- [ ] T015 [P] Add `new_artist_list` and `GET /api/artist` to `specs/003-typescript-dashboard/contracts/api.md`, and an entry for this feature to `docs/streamlit-vs-typescript.md`
- [ ] T016 Run the full quickstart.md, including scenarios 8 (same numbers in both apps) and 9 (Genre regression), plus `npx tsc --noEmit` and `npm run build`; note anything not checked for the PR

---

## Dependencies & Execution Order

- Phase 2 (T001–T003) blocks everything; T002 is independent of T001.
- US1 (T004–T007) before US2: the list is what US2 clicks. T005 and T006 need T004's types only for
  TypeScript; the Streamlit page calls `rain_in_my_head.artist` directly.
- US2: T009 and T010 are independent of each other (different apps); T010 needs T008.
- US3 (T012–T013) after T009 and T010.
- Polish after all stories.

## Implementation Strategy

1. Phase 2, then US1 in both apps → verify (MVP: the list alone answers "who's new this month").
2. US2 → verify; US3 → verify.
3. Polish, full quickstart, PR with `Closes #5`.

Commit after each phase; tick tasks here as they finish.
