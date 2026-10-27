# Feature Specification: Prototype Redesign

**Feature Branch**: `feature/prototype-redesign`

**Created**: 2026-10-26

**Status**: Draft

**Input**: User description: "Update the rain-in-my-head application in TypeScript to match what I have designed in the Figma design for Rain in My Head on the Prototype page. If the feature doesn't already exist, let me know and we can create a placeholder page for it and a GitHub issue to complete that feature. One new feature per GitHub issue. I know that we don't have the AI option yet, so that will need a GitHub issue. Add a visual on that page, in the branding of the prototype page, that says 'Coming Soon'."

Design source: Figma "Rain in My Head — Design process" (`1rbbEne7pW8oA2JCNmjhrm`), page **4 · Prototype**. Applies to the **TypeScript** dashboard (`web/`) only. The Streamlit dashboard is unchanged, and the differences are noted in `docs/streamlit-vs-typescript.md`.

Features in the prototype that the app doesn't have yet, confirmed with the owner on 2026-10-26. This change gives each one a placeholder, and the issue tracks the real feature:

| Feature | Issue | Placeholder |
|---|---|---|
| Landing page with the illustration | #27 | `/` |
| Storm mode | #28 | `/storm` |
| First-load sync screen | #29 | none (the loader look is reused for loading states) |
| Listening-slot drill-down | #30 | `/dashboards/slot` |
| SQL playlist type | #31 | Playlist Generator → SQL tab |
| AI playlist type | #32 | Playlist Generator → AI tab, with a **Coming Soon** visual |
| About page | #33 | `/about` |
| Contact Me page | #34 | `/contact` |
| Mainstream vs. niche artists page | #12 (existing) | `/dashboards/mainstream` |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find my way around the redesigned app (Priority: P1)

I open the app and see the prototype's look: a top bar with the cloud logo and "Rain in My Head" on the left, and Dashboards, Playlist Generator, Analyst, About and Contact Me on the right. The section I'm in is highlighted. Under the bar, a breadcrumb (Home › Section › Page) shows where I am. Headings, body text, code and cards use the prototype's fonts and raised-card style.

**Why this priority**: every other page sits inside this shell, so it has to come first.

**Independent Test**: open each top-bar link in a browser, check the highlight and breadcrumb, and compare against the matching prototype frame.

**Acceptance Scenarios**:

1. **Given** any page, **When** I click a top-bar item, **Then** that section opens and its item is highlighted.
2. **Given** any page, **When** I click the cloud logo or "Home" in the breadcrumb, **Then** the home page opens.
3. **Given** a bookmarked old address (`/sql`, `/schema`, `/genre`, `/artist`), **When** I open it, **Then** I land on the matching new page with the same query string.
4. **Given** an address that doesn't exist, **When** I open it, **Then** the restyled Not Found page offers a way back.

---

### User Story 2 - Read the redesigned Dashboards (Priority: P1)

I open Dashboards and see the Overview laid out as in the prototype. Date range and Grain chips sit at the top of the page, not in a sidebar. Below them come five KPI cards with change pills, a "Scrobbles per month" card with a Scrobbles/Hours toggle, a Top card with Artists/Tracks/Albums/#1 per year tabs, "When you listen" and "New artists per month" side by side, "Genre share over time" as one chart with a clickable genre chip legend, and "Mainstream vs. niche" and "Data quality" side by side. The Loved tracks section is gone. Clicking a month in "New artists per month" opens a New artists page with a month picker. Genre and Artist pages share the look and have a "Back to Dashboards" link.

**Why this priority**: the Overview is the page used most.

**Independent Test**: set the same range and grain on the old and new Overview and compare every number. Click through to New artists, Genre and Artist.

**Acceptance Scenarios**:

1. **Given** Dashboards with "Last 12 months" and Month, **Then** every figure matches what the Overview showed before the redesign for the same inputs.
2. **Given** Dashboards, **When** I click a bar in "Scrobbles per month", **Then** the page narrows to that month, as the `dashboard-overview` living spec requires.
3. **Given** Dashboards, **When** I click a genre chip or a genre's line, **Then** the Genre page opens for that genre and range.
4. **Given** Dashboards, **When** I click a month in "New artists per month", **Then** the New artists page opens for that month. Changing the month picker updates the list, and clicking an artist opens their Artist page.
5. **Given** Dashboards, **When** I click a heatmap square or a mainstream bar, **Then** the matching placeholder page opens (#30, #12).

---

### User Story 3 - Use the Playlist Generator and the Analyst (Priority: P2)

Playlist Generator opens as "Create a playlist" with five tabs: Time Slot, Discovery, Binge, AI and SQL. The first three work as they do today, restyled with chips and sliders, and show results in a table with a "Create on Spotify" bar under it. AI shows a branded **Coming Soon** visual. SQL shows a placeholder. Analyst combines the old SQL and Schema pages: a collapsible "Database schema" card, then Write SQL (examples, query, Run / Clear), Results, and Download CSV.

**Why this priority**: these pages work today. The redesign mostly changes how they look.

**Independent Test**: build the same Time Slot playlist before and after and compare the tracks. Run an example query in Analyst and download the CSV. Open the AI and SQL tabs.

**Acceptance Scenarios**:

1. **Given** the same settings, **Then** Time Slot, Discovery and Binge list the same tracks in the same order as before.
2. **Given** Spotify is connected, **When** I create a playlist from the bar, **Then** it's created exactly as before (progress, link, unmatched tracks).
3. **Given** the AI tab, **Then** I see a Coming Soon visual in the brand style, a short description of the planned feature and a link to issue #32. No form pretends to work.
4. **Given** Analyst, **When** I run an example, **Then** I see the rows, the row count, sortable columns and Download CSV. Write statements are refused as before.
5. **Given** Analyst, **When** I expand "Database schema", **Then** the draggable schema map works and saves its layout as before.

---

### User Story 4 - See what's coming (Priority: P3)

The pages for features that don't exist yet (Landing, Storm, Listening slot, Mainstream vs. niche, About, Contact Me, and the SQL and AI playlist tabs) each show their title, one or two sentences on what's planned, a **Coming Soon** visual in the brand style and a link to their GitHub issue.

**Why this priority**: placeholders keep every top-bar item and every click from the prototype working, so the app can be walked through end to end.

**Independent Test**: open each placeholder and check the title, description, visual and issue link.

**Acceptance Scenarios**:

1. **Given** any placeholder, **Then** it shows the Coming Soon visual and a working link to its issue.
2. **Given** the home placeholder, **Then** it links to Dashboards, so the app is still usable from the start.

### Edge Cases

- The database is empty: Dashboards keeps the existing "no scrobbles yet" notice, restyled.
- A narrow window (below about 800px wide): the top bar's links wrap or collapse so none are hidden off-screen, and side-by-side cards stack.
- A New artists address with a missing or unknown month falls back to the latest month that has new artists.
- The user prefers reduced motion: the Coming Soon visual and loaders don't animate.
- The design's webfonts fail to load: text falls back to system fonts and stays readable.

## Requirements *(mandatory)*

### Functional Requirements

**Shell and style**

- **FR-001**: The app MUST replace the left sidebar with a top bar: the logo and name linking home, then Dashboards, Playlist Generator, Analyst, About and Contact Me, with the current section highlighted.
- **FR-002**: Every page except home MUST show a breadcrumb starting at Home.
- **FR-003**: Text MUST use the prototype's type styles: a rounded display face for page titles and section headings, a light geometric sans for body and controls, and a monospace face for code. Sizes and weights come from the Figma text styles.
- **FR-004**: Cards MUST use the prototype's "Elevation/Raised" look. Colours stay as they are, plus the prototype's three extra chart colours (plum, moss, ember) for the genre lines.
- **FR-005**: Filters MUST appear on the page as chip groups (date range, grain, listening period, days) instead of in a sidebar.

**Routes**

- **FR-006**: Pages MUST be at: `/` home, `/dashboards` Overview, `/dashboards/new-artists`, `/dashboards/genre`, `/dashboards/artist`, `/dashboards/slot`, `/dashboards/mainstream`, `/playlists`, `/analyst`, `/about`, `/contact`, `/storm`.
- **FR-007**: The old addresses `/sql`, `/schema`, `/genre` and `/artist` MUST redirect to their new pages and keep the query string.

**Dashboards**

- **FR-008**: The Overview MUST show the sections listed in User Story 2, in that order, with the same numbers as before for the same inputs. The Loved tracks section is removed.
- **FR-009**: The genre panels MUST become one "Genre share over time" chart with a chip legend. Clicking a chip or a line opens that genre.
- **FR-010**: New artists MUST be its own page with a month picker, opened from "New artists per month". The inline list on the Overview is removed.
- **FR-011**: Genre and Artist pages MUST be restyled and have a "Back to Dashboards" link that keeps the Overview's filters.

**Playlists and Analyst**

- **FR-012**: The Playlist Generator MUST have the tabs Time Slot, Discovery, Binge, AI and SQL. The first three keep their current behaviour and results.
- **FR-013**: The AI tab MUST show a Coming Soon visual in the prototype's brand style and link to #32.
- **FR-014**: Create on Spotify MUST appear as a bar under the results (name, public toggle, button) and behave as it does today.
- **FR-015**: Analyst MUST combine the SQL and Schema pages as in User Story 3, and keep all of their current behaviour.

**Placeholders**

- **FR-016**: Each placeholder MUST show its title, a short description of the planned feature, the Coming Soon visual and a link to its GitHub issue, using one shared component.

### Key Entities

No new data. All pages read the existing API.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every page in the prototype's sections 1–4 can be reached in the running app by clicking, with no dead ends.
- **SC-002**: For three different range and grain settings, 100% of the Overview's figures match a direct database query and the pre-redesign values.
- **SC-003**: Time Slot, Discovery and Binge return the same tracks as before for the same settings.
- **SC-004**: The owner, comparing each implemented page side by side with its prototype frame, finds no difference in layout, type or colour that they'd call a bug.
- **SC-005**: Text and controls meet WCAG 2.2 AA contrast on the dark theme, and everything can be used from the keyboard.

## Assumptions

- Backend and API are unchanged. The prototype's data all exists already.
- Webfonts load from Google Fonts in the page head. No new npm dependency is added.
- The Figma illustrations (Rain Girl, the umbrella) are left for #27 and #28. The placeholders use a simple raining-cloud motif built in CSS/SVG.
- Desktop (1440px) is the reference. Narrower windows only need to stay usable (stacked cards, no horizontal scrolling).
- The prototype's state screens (loading, no results, Spotify not connected, creating, created, failed, SQL errors) map onto the app's existing states and are restyled, not redesigned.
- The routes now differ from Streamlit's (constitution VI). This is recorded in `docs/streamlit-vs-typescript.md` and justified in the plan.
