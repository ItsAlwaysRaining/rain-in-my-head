# Feature Specification: Schema Page

**Feature Branch**: `feature/schema-page`

**Created**: 2026-10-15

**Status**: Draft

**Input**: User description: "Add the listening.db schema map to the Streamlit application menu" (follows issue #8, which documents the schema). Refined with the owner: a built-in dashboard page, not a link to an outside page, and the table layout is saved in the project's `data/` folder rather than in the browser.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See the database as a map (Priority: P1)

From the dashboard menu I open "Schema" and see every table and view in the listening database as a
card: a plain-English name and description, the real table name, where its data comes from, how
many rows it holds, and each column with its type and what it means. Lines connect the columns that
link tables together, labelled in words such as "many plays → 1 track".

**Why this priority**: today the only schema view is a flat column list on the SQL page. Without the
map there is nothing to arrange or keep current.

**Independent Test**: open the Schema page and compare the cards, columns and row counts with the
database.

**Acceptance Scenarios**:

1. **Given** the dashboard, **When** I look at the menu, **Then** it has a "Schema" entry after
   "SQL", and clicking it opens the map.
2. **Given** the Schema page, **Then** it shows one card for each of the 5 tables and 2 views, each
   with its plain-English name, real name, data source, description and columns; tables also show
   their row count (for example "218,142 rows" for Plays).
3. **Given** the Schema page, **Then** lines join `scrobbles.track_key` → `tracks.track_key`,
   `scrobbles.artist_key` → `artists.artist_key`, `tracks.artist_key` → `artists.artist_key`,
   `artist_tags.artist_key` → `artists.artist_key` and `spotify_matches.track_key` →
   `tracks.track_key`, each with a label in words.
4. **Given** the Schema page, **When** I hover over (or focus) a card, **Then** its links and the
   linked columns are highlighted and the other links fade.
5. **Given** the Schema page, **When** I turn on "Show how views are built", **Then** dashed lines
   join each view to the tables and views it reads from.

---

### User Story 2 - Arrange the tables and keep the layout (Priority: P2)

I drag a card by its header to wherever I want it. When I come back later, after restarting the
dashboard or from another browser, the cards are where I left them. A reset puts them back.

**Why this priority**: this is what makes the map mine, but the map is useful without it.

**Independent Test**: move two cards, restart the dashboard, open the page in a different browser
and check the cards are where they were left.

**Acceptance Scenarios**:

1. **Given** the Schema page, **When** I press on a card's header and drag, **Then** the card follows
   the pointer and its lines follow the card.
2. **Given** I have moved cards, **When** I restart the dashboard and open the Schema page in another
   browser, **Then** every card is in the position I left it.
3. **Given** a card header has keyboard focus, **When** I press an arrow key, **Then** the card moves
   20 px that way (80 px with Shift), and the new position is saved.
4. **Given** a saved layout, **When** I click "Reset layout" and confirm, **Then** every card returns
   to its default position and that becomes the saved layout.

---

### User Story 3 - The map stays current (Priority: P3)

When a table or column is added to the database, it appears on the map without anyone editing the
page. Anything that has no description yet says so.

**Why this priority**: keeps the map trustworthy as the schema changes, but rarely matters day to day.

**Independent Test**: point the dashboard at a copy of the database with an extra column and an
extra table, and open the Schema page.

**Acceptance Scenarios**:

1. **Given** a database with a column that has no description, **When** I open the Schema page,
   **Then** the column is listed with its type and "No description yet".
2. **Given** a database with a table the page has never seen, **When** I open the Schema page,
   **Then** it appears as a card with its real name as the title, "No description yet", its columns
   and row count, placed where it does not cover another card.
3. **Given** a saved layout that names a table no longer in the database, **When** I open the Schema
   page, **Then** that entry is ignored and the page shows no error.

### Edge Cases

- No database yet: the page says to run `listening build` first, as the SQL page does.
- The saved layout file is missing, empty or not valid: the page uses the default layout and shows
  no error; the next move saves a fresh file.
- A saved position is off the map (for example from a smaller map size): the card is moved back
  inside the map.
- A card is dragged past the edge of the map: it stops at the edge.
- The page is open in two tabs and cards are moved in both: the last move saved wins.
- `spotify_matches` has 0 rows: the card shows "0 rows" and is otherwise normal.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The dashboard menu MUST have a "Schema" entry, after "SQL", that opens the Schema page.
- **FR-002**: The page MUST show one card per table and view in the database, read from the database
  each time it changes, not from a fixed list.
- **FR-003**: Each card MUST show the real name, a plain-English name and description, the data
  source (Last.fm listening history, Last.fm track and artist details, Spotify, or view), and every
  column with its type and meaning. Table cards MUST also show the row count.
- **FR-004**: Columns MUST be marked when they identify a row, link to another table, or can be blank.
- **FR-005**: The page MUST draw a labelled line for each link between tables listed in the
  acceptance scenarios of User Story 1, from the linking column on one card to the column on the other.
- **FR-006**: Hovering over or focusing a card MUST highlight its links and linked columns.
- **FR-007**: A "Show how views are built" switch MUST show or hide dashed lines from each view to
  what it reads from. It is off by default.
- **FR-008**: Cards MUST be movable by dragging anywhere on their header, and with the arrow keys when
  the header has focus. Cards MUST stay within the map.
- **FR-009**: Card positions MUST be saved in a file in the project's `data/` folder when a move
  finishes, and loaded from it when the page opens. The file MUST NOT be committed to git.
- **FR-010**: A "Reset layout" control MUST, after a confirmation step on the page, restore and save
  the default positions.
- **FR-011**: The page MUST offer zoom in, zoom out and "Fit to screen", and open fitted to the screen.
- **FR-012**: Columns and tables without a description MUST show "No description yet"; tables
  without a default position MUST be placed where they do not cover another card.
- **FR-013**: The page MUST NOT change the database, and MUST NOT call any external service.

### Key Entities

- **Table or view**: a named object in the database with columns; tables have a row count.
- **Column**: a name, a type, and whether it identifies a row, links elsewhere or can be blank.
- **Link**: a column in one table that refers to a column in another, with a "many → 1" label.
- **Description**: the plain-English name, source and meaning written for a table or column.
- **Layout**: the saved position of each card on the map.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: From any dashboard page, the full database structure is one click away.
- **SC-002**: Every table, view and column in the database appears on the map (0 missing), and the
  row counts match the database exactly.
- **SC-003**: After moving cards, 100% of positions are the same after a dashboard restart and in a
  second browser.
- **SC-004**: A new column added to the database appears on the map without any change to the page.

## Assumptions

- One layout is shared by everyone using this dashboard; it is a personal, local app.
- Descriptions are written by hand in the project, starting from those in issue #8. A new table or
  column shows up straight away, but its description waits for someone to write it.
- Links between tables are listed by hand, because the database declares none.
- Zoom level and the "Show how views are built" switch are not saved.
- The SQL page keeps its own schema list; replacing it is out of scope.
- The page uses the dashboard's dark theme only.
