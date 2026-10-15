---

description: "Tasks for the Schema page (follows issue #8)"
---

# Tasks: Schema Page

**Input**: Design documents from `specs/002-schema-page/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/schema-page.md, quickstart.md

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

- [ ] T001 Add `data/schema_layout.json` to `.gitignore`

---

## Phase 2: Foundational (blocks all stories)

**Purpose**: the hand-written notes and the live schema read that every story uses.

- [ ] T002 [P] Create `dashboard/schema_notes.py` with `TABLES` (title, source, description, column meanings for all 7 objects, from issue #8), `LINKS` (5), `LINEAGE` (5 pairs) and `DEFAULT_POSITIONS` (data-model.md)
- [ ] T003 [P] In `dashboard/views/schema.py`, add `read_schema(db_mtime)` (cached): objects, columns with type/required/key, table row counts, over a read-only connection (data-model.md)

**Checkpoint**: `read_schema` returns 7 objects whose columns and counts match SQLite.

---

## Phase 3: User Story 1 - See the database as a map (Priority: P1) 🎯 MVP

**Goal**: a "Schema" menu entry that shows the cards and link lines.

**Independent Test**: quickstart.md scenarios 1 and 2.

- [ ] T004 [US1] Create `dashboard/schema_map/map.css` and `map.js`: cards, link lines with labels, hover/focus highlight, lineage switch, zoom and fit, legend (contracts/schema-page.md); confirm the rerun behaviour noted in research.md R1
- [ ] T005 [US1] In `dashboard/views/schema.py`, merge schema and notes into the component data (unknown tables and columns get "No description yet") and mount the component; show the "No database yet" message when there is no database
- [ ] T006 [US1] Register `st.Page("views/schema.py", title="Schema", icon=":material/schema:", url_path="schema")` after SQL in `dashboard/app.py`
- [ ] T007 [US1] Verify quickstart.md scenarios 1–2 in headless Chrome and cross-check columns and row counts against SQLite

**Checkpoint**: the map is in the menu and correct.

---

## Phase 4: User Story 2 - Arrange the tables and keep the layout (Priority: P2)

**Goal**: drag cards, keep their positions in `data/schema_layout.json`.

**Independent Test**: quickstart.md scenario 3.

- [ ] T008 [US2] In `dashboard/schema_map/map.js`, drag by the whole header with pointer events, arrow-key moves, keep cards inside the map, two-click "Reset layout", and send the `layout` trigger when a move ends
- [ ] T009 [US2] In `dashboard/views/schema.py`, load the layout file with validation and clamping, and write it atomically from the `on_layout_change` callback
- [ ] T010 [US2] Verify quickstart.md scenario 3 in headless Chrome, including a server restart and a fresh browser context

**Checkpoint**: positions survive a restart and a new browser.

---

## Phase 5: User Story 3 - The map stays current (Priority: P3)

**Goal**: new tables and columns appear without code changes.

**Independent Test**: quickstart.md scenarios 4 and 5.

- [ ] T011 [US3] In `dashboard/views/schema.py`, place objects with no saved or default position in the first free grid slot below the default layout; drop links, lineage and notes that name missing tables or columns
- [ ] T012 [US3] Verify quickstart.md scenarios 4–5 against a temporary copy of the database

**Checkpoint**: schema changes show up on their own.

---

## Phase 6: Polish

- [ ] T013 Add a "Schema page" section to `README.md`
- [ ] T014 Open the PR with what was and wasn't checked; `Closes #8`

---

## Dependencies & Execution Order

- T001 first. T002 and T003 can run in parallel; both block Phase 3.
- US1 (T004–T007) before US2: dragging builds on the rendered cards.
- US3 (T011–T012) needs T005 and T009.
- T013–T014 last.

## Implementation Strategy

Deliver US1 as the MVP and check it in the browser before adding saving (US2) and the
stays-current rules (US3). Commit after each phase.
