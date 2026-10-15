# Feature Specification: TypeScript Dashboard

**Feature Branch**: `feature/typescript-dashboard`

**Created**: 2026-10-15

**Status**: Draft

**Input**: User description: "How much work would it be to convert this to TypeScript? I want full control over the design and layout of the page." Refined with the owner: only the dashboard moves (the CLI and scheduled sync stay as they are), and the Streamlit dashboard is **kept**, so that the two apps, and the work of building and changing them, can be compared side by side.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Overview in the new dashboard (Priority: P1)

I start the new dashboard and open its Overview. It shows the same listening summary as the Streamlit Overview: range presets and time grain, KPIs with change against the previous period, scrobbles or hours over time, top artists, tracks and albums, #1 artist per year, "When you listen", new artists over time, genre panels, mainstream vs. niche, loved tracks and data quality. Clicking a bar narrows everything to that period, exactly as the Streamlit version does today. Every part of the page is laid out and styled the way we choose, not the way Streamlit decides.

**Why this priority**: the Overview is the page used most and the hardest to build. Once it works, the approach is proven and the comparison can start.

**Independent Test**: open both dashboards on the same range and grain, click the same month in each, and compare every figure.

**Acceptance Scenarios**:

1. **Given** both dashboards are running, **When** I open the new Overview with "Last 12 months" and Month, **Then** the five KPIs, their deltas and the over-time bars show the same values as the Streamlit Overview with the same settings.
2. **Given** the new Overview, **When** I click the bar for a month, **Then** every figure follows the requirements in the `dashboard-overview` living spec (`openspec/specs/dashboard-overview/spec.md`). That includes the dates in the caption, previous-period deltas, finer steps inside the period, "#1 per year" left unchanged, the highlighted bar, "Show whole range" and clicking the chart background to clear.
3. **Given** the new Overview, **When** I click a genre panel, **Then** the new dashboard's Genre page opens for that genre and the current range or selected period. Until slice 2 is delivered, the address is built correctly and the page says it is coming.
4. **Given** the new Overview, **When** I switch between Artists, Tracks, Albums and "#1 per year", **Then** each shows the same rows and counts as Streamlit.

---

### User Story 2 - Genre and SQL pages (Priority: P2)

From the new dashboard I open Genre, either from the menu or by clicking a genre panel, and see that genre's artists with their pictures and play counts. Selecting an artist shows my songs by them with album art. On the SQL page I load an example or type a query, run it read-only, see the rows, and download them as CSV.

**Why this priority**: both are small, and Genre is where the Overview's genre panels lead.

**Independent Test**: open the same genre and range in both apps and compare the lists; run each example query in both apps and compare the row counts.

**Acceptance Scenarios**:

1. **Given** a genre and range from the Overview, **When** the Genre page opens, **Then** it lists the same artists, play counts and pictures as Streamlit's Genre page for the same genre and range.
2. **Given** the SQL page, **When** I choose an example and run it, **Then** I see the same rows as Streamlit, a row count, and a "Download CSV" control that saves them.
3. **Given** the SQL page, **When** I run a statement that would change data (for example `DELETE FROM scrobbles`), **Then** it is refused with the database's error message and nothing changes.
4. **Given** the SQL page, **When** I run invalid SQL, **Then** the error is shown on the page and the page keeps working.

---

### User Story 3 - Schema and Playlists pages (Priority: P3)

The new dashboard has the Schema map, with cards I can drag and links between tables. Both dashboards save to the same layout, so a card moved in one is in the same place in the other. It also has the Playlists page with its three kinds of playlist: time slot, discoveries by year and binged songs. Each shows a preview and can create the playlist on Spotify, with progress shown while tracks are matched.

**Why this priority**: completes parity. These pages are used less often than the Overview.

**Independent Test**: move a card in the new app, reload Streamlit's Schema page and see it there. Build the same time-slot preview in both apps and compare the tracks, then create one private playlist from the new app.

**Acceptance Scenarios**:

1. **Given** the Schema page in the new dashboard, **Then** it meets every functional requirement of `specs/002-schema-page/spec.md`. The menu entry follows SQL.
2. **Given** I moved a card in either dashboard, **When** I open the Schema page in the other, **Then** the card is in the same place.
3. **Given** the same playlist settings in both dashboards, **Then** the preview lists the same tracks in the same order with the same figures.
4. **Given** Spotify is connected, **When** I click "Create playlist", **Then** I see matching progress, then a link to the new playlist, and a list of any tracks with no Spotify match.
5. **Given** Spotify is not connected, **Then** the page explains how to connect it from the terminal, as Streamlit does.

---

### User Story 4 - Compare the two (Priority: P2)

As each page is built, a comparison log records, for that page, how big each version is, how long it took, and what was easy or hard in each. Once parity is reached, the same small change is made in both apps and how each went is recorded.

**Why this priority**: comparing the two is the reason for keeping both apps; the log has to be kept as the work happens, not reconstructed afterwards.

**Independent Test**: after each slice, the log has an entry for every page delivered in that slice.

**Acceptance Scenarios**:

1. **Given** a slice is delivered, **Then** the comparison log has a section for each page in it, giving its size in both versions, the effort spent, and notes on what was easy or hard.
2. **Given** all pages are delivered, **Then** the log records one identical small change made in both apps, with the time taken and the number of files touched in each.
3. **Given** both apps on the same page and range, **Then** the log records how long each takes to show the page.

### Edge Cases

- **No database yet:** each page shows the same "run `listening build`" message as its Streamlit counterpart. If the database has no scrobbles, the Overview says so.
- **Data service not running:** the new dashboard shows a clear message saying how to start it instead of blank charts.
- **Database rebuilt while the app is open:** the next view or reload shows the new data, with no restart needed.
- **Range with no plays:** "No scrobbles in this range", as in Streamlit.
- **No enrichment yet:** the genre and mainstream sections show the "run `listening enrich`" message.
- **Genre page opened directly** (no genre in the address): it uses the most-played genre over all time, as Streamlit does.
- **Spotify token expired or invalid:** the error is shown and no playlist is created.
- **Both apps open on Schema, cards moved in both:** the last move saved wins.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST provide a second dashboard with the pages Overview, Genre, SQL, Schema and Playlists, in that menu order, at the same paths as the Streamlit dashboard (`/`, `/genre`, `/sql`, `/schema`, `/playlists`).
- **FR-002**: The Streamlit dashboard MUST stay available, with unchanged behaviour and numbers, and both MUST be able to run at the same time against the same database.
- **FR-003**: For the same inputs, every number, list and ordering shown in the new dashboard MUST equal the Streamlit dashboard's. Both MUST get them from one shared implementation of the data work, not two copies.
- **FR-004**: The new Overview MUST meet every requirement in `openspec/specs/dashboard-overview/spec.md` and show the sections listed in User Story 1.
- **FR-005**: The Genre page MUST accept a genre and date range in its address, so links from the Overview and bookmarks work.
- **FR-006**: The SQL page MUST run queries read-only, show errors on the page, and offer the result as a CSV download.
- **FR-007**: The Schema page MUST meet the functional requirements of `specs/002-schema-page/spec.md` and share its saved layout with the Streamlit Schema page.
- **FR-008**: The Playlists page MUST offer the same three playlist types and options as Streamlit, show the same preview, and create playlists on Spotify with visible progress and a list of unmatched tracks.
- **FR-009**: The new dashboard MUST use the project's shared dark palette, so a colour has the same meaning in both apps. Its layout, spacing, typography and components MUST be fully defined by the project, with no framework-imposed layout.
- **FR-010**: Pages MUST NOT call external services on load. Spotify is contacted only when the user creates a playlist, as today.
- **FR-011**: The new dashboard MUST be startable with one documented command, and the README MUST explain how to run either app or both.
- **FR-012**: The scheduled sync and the CLI MUST keep working without anything the new dashboard needs installed.
- **FR-013**: A comparison log MUST be kept in the repository and updated in the same pull request as each page, per User Story 4.
- **FR-014**: Delivery MUST be in three slices, each one a pull request that leaves both apps working:
  1. Overview, plus the shared foundation and comparison log
  2. Genre and SQL
  3. Schema and Playlists

### Key Entities

- **Dashboard app**: either the Streamlit app or the new one; both show the same pages over the same database.
- **Page view request**: what a page needs to show something. That is the page plus its inputs, such as a date range, grain, selected period, genre, query or playlist settings.
- **Shared result**: the figures, lists and series for a page view, computed once and shown by either app.
- **Schema layout**: the saved card positions, shared by both apps.
- **Comparison entry**: per page, the size of each version, the effort and notes, plus the results of the same-change test.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For 5 spot checks per page (different ranges, periods, genres, queries and playlist settings), the new dashboard and Streamlit show identical figures, and the Overview KPIs also match a direct database query (0 differences).
- **SC-002**: Every acceptance scenario in the `dashboard-overview` living spec passes in the new dashboard when checked by clicking in a real browser.
- **SC-003**: The Streamlit dashboard passes the same browser checks after the change as before it, with 0 behaviour changes.
- **SC-004**: On the owner's machine, the new Overview shows its figures within 2 seconds of opening, and within 1 second after clicking a period.
- **SC-005**: After the last slice, the comparison log covers all 5 pages and the same-change test.
- **SC-006**: The owner can restyle any element of any page (colour, spacing, position, font) by editing only the new dashboard's own files.

## Assumptions

- It is a personal, local app for one user, the same as the Streamlit dashboard. There is no login and no hosting.
- The Streamlit dashboard keeps its current design; only its data work moves into shared code. Its look and behaviour do not change.
- The CLI, the database schema and the scheduled sync are out of scope.
- The first version of each new page matches Streamlit's content. Visual redesign comes afterwards, page by page, and each redesign is recorded in the comparison log.
- Dark theme only, as now.
- Effort in the comparison log is recorded in working sessions, with notes, not exact hours.
