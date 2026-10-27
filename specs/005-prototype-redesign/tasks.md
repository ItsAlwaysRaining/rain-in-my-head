---

description: "Task list for the prototype redesign"
---

# Tasks: Prototype Redesign

**Input**: Design documents from `/specs/005-prototype-redesign/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/routes.md, quickstart.md

**Tests**: none requested. Verification is the browser walk-through in quickstart.md (constitution III).

**Organization**: Tasks are grouped by user story so each can be built and checked on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependencies)
- **[Story]**: the user story the task belongs to (US1–US4)

All paths are relative to the repository root. The app is in `web/`.

---

## Phase 1: Setup

- [ ] T001 Add the Google Fonts `<link>` for Fredoka 600/700, Lexend 300/400/500/600 and Red Hat Mono 400 with `display=swap` to `web/index.html` (research R1)
- [ ] T002 Add font, type-scale, `--shadow-raised` and chart plum/moss/ember tokens, then restyle the base `h1`/`h2`/`h3`/body/code rules in `web/src/theme.css` (FR-003, FR-004, research R2)

---

## Phase 2: Foundational

**⚠️ Every story depends on these**

- [ ] T003 Create `web/src/routes.ts` with the top-bar sections, path → breadcrumb label map and the GitHub issue URL helper (data-model "Route entry", contracts/routes.md)
- [ ] T004 [P] Add `Card`, `ChipGroup` (single-select radiogroup), `Breadcrumbs`, `BackLink` (replaces `BackToOverview`, keeps the Dashboards query string) to `web/src/components/ui.tsx`. Restyle `Kpi` (delta pill), `Tabs` (underline) and `SegmentedControl` in `web/src/components/ui.module.css`
- [ ] T005 [P] Create `web/src/components/ComingSoon.tsx` and `ComingSoon.module.css`: SVG cloud with bolt and animated rain, "Coming soon" pill, title, description, issue link. No animation under `prefers-reduced-motion` (research R6, FR-016)
- [ ] T006 [P] Restyle the multi-select chips, sliders and field labels in `web/src/components/Form.module.css`, and the tables (raised card, row rules, header) in `web/src/components/DataTable.module.css`
- [ ] T007 [P] Switch the Vega font to Lexend and add the plum/moss/ember constants in `web/src/charts/config.ts`

**Checkpoint**: the shared building blocks exist.

---

## Phase 3: User Story 1 - Find my way around (Priority: P1) 🎯 MVP

**Goal**: a top bar, breadcrumbs, new routes and redirects.

**Independent Test**: quickstart checks 2, 3 and 9.

- [ ] T008 [US1] Replace the sidebar with the top bar (logo + name → `/`, section links, active highlight) and breadcrumbs, and remove the `Sidebar` slot, in `web/src/App.tsx` and `web/src/App.module.css`
- [ ] T009 [US1] Register every route in contracts/routes.md, plus `<Navigate>` redirects that keep the query string for `/genre`, `/artist`, `/sql`, and `/schema` → `/analyst?schema=open`, in `web/src/App.tsx`
- [ ] T010 [US1] Restyle the Not Found page (title, message, link to Dashboards) in `web/src/App.tsx`

**Checkpoint**: every top-bar link and old address opens a page.

---

## Phase 4: User Story 2 - Redesigned Dashboards (Priority: P1)

**Goal**: the Overview, New artists, Genre and Artist pages as in the prototype.

**Independent Test**: quickstart checks 4 and 5.

- [ ] T011 [US2] Move the Date range and Grain filters onto the page as `ChipGroup`s with inline Custom dates, title "Overview" with the date caption, in `web/src/pages/Overview.tsx`
- [ ] T012 [US2] Lay out the KPI cards, the "Scrobbles per month" card with the Scrobbles/Hours toggle in its header, the Top card with tabs, the "When you listen" and "New artists per month" cards side by side, and the "Mainstream vs. niche" and "Data quality" cards side by side. Remove Loved tracks and the inline new-artists list. In `web/src/pages/Overview.tsx` and `web/src/pages/Overview.module.css`
- [ ] T013 [US2] Add `genreLines()` (one multi-line chart, six colours, click selects a genre) to `web/src/charts/overview.ts`. Use it with a chip legend that opens `/dashboards/genre` in `web/src/pages/Overview.tsx` (research R4, FR-009)
- [ ] T014 [US2] Make the "New artists per month" points open `/dashboards/new-artists?month=`, the heatmap open `/dashboards/slot` and the mainstream bars open `/dashboards/mainstream`, in `web/src/charts/overview.ts` and `web/src/pages/Overview.tsx`
- [ ] T015 [US2] Create `web/src/pages/NewArtists.tsx` with a month picker and an artist table. Rows open the Artist page. Data from `/api/overview?preset=all&grain=month&period=` (research R3, FR-010)
- [ ] T016 [P] [US2] Restyle `web/src/pages/Genre.tsx`/`.module.css` and `web/src/pages/Artist.tsx`/`.module.css` with `BackLink` and cards. Update their internal links to `/dashboards/...` (FR-011)

**Checkpoint**: Dashboards and its drill-downs match the prototype, with the same numbers as before.

---

## Phase 5: User Story 3 - Playlist Generator and Analyst (Priority: P2)

**Goal**: "Create a playlist" with five tabs, and the merged Analyst page.

**Independent Test**: quickstart checks 6 and 7.

- [ ] T017 [US3] Restyle `web/src/pages/Playlists.tsx`/`.module.css`: title "Create a playlist" with an intro line, underline tabs Time Slot/Discovery/Binge/AI/SQL kept in `?type=`, chip groups for days and "Listening from", results in a card, and Create on Spotify as a bar card (name, public toggle, button) (FR-012, FR-014)
- [ ] T018 [US3] Render `ComingSoon` in the AI tab (#32) and the SQL tab (#31) in `web/src/pages/Playlists.tsx` (FR-013)
- [ ] T019 [US3] Create `web/src/pages/Analyst.tsx`: a collapsible "Database schema" card (open when `?schema=open`) holding the Schema content, then Write SQL, Results and Download CSV from `Sql.tsx`. Demote the `h1`s in `web/src/pages/Sql.tsx` and `web/src/pages/Schema.tsx` (FR-015, research R8)

**Checkpoint**: playlists build the same tracks as before, and Analyst runs queries and saves the schema layout.

---

## Phase 6: User Story 4 - Coming Soon pages (Priority: P3)

**Goal**: every unbuilt prototype page has a branded placeholder.

**Independent Test**: quickstart check 8.

- [ ] T020 [US4] Create `web/src/pages/Placeholders.tsx` exporting Home (#27, with a link to Dashboards), Storm (#28), ListeningSlot (#30), Mainstream (#12), About (#33) and Contact (#34), each a `ComingSoon` with a title and description from data-model.md. Wire them into `web/src/App.tsx`

---

## Phase 7: Polish

- [ ] T021 [P] Record the route, layout and genre-chart differences in `docs/streamlit-vs-typescript.md`, and update the page list in `README.md`
- [ ] T022 Run `npm run build` in `web/`, then the full quickstart.md walk-through in a browser against the real database. Note what was and wasn't checked for the PR

---

## Dependencies & Execution Order

- Setup (T001–T002) → Foundational (T003–T007) → stories.
- US1 (T008–T010) comes before the others because it removes the `Sidebar` export that Overview and Playlists use.
- US2, US3 and US4 are independent of each other after US1.
- Polish comes last.

## Parallel Opportunities

- T004, T005, T006 and T007 touch different files.
- T016 can run alongside T011–T015.
- After US1, US3 and US4 can be built alongside US2.

## Implementation Strategy

1. MVP: Setup + Foundational + US1. The app has the new shell, and existing pages still work at their new addresses.
2. Add US2 (Dashboards), the most-used area.
3. Add US3, then US4, then Polish. Commit after each phase.
