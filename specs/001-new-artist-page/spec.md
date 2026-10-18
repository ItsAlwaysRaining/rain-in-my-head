# Feature Specification: New Artists and Artist Page

**Feature Branch**: `feature/new-artist-page`

**Created**: 2026-10-14

**Status**: Draft

**Input**: User description: "New artists this month: click an artist to open their page with album art, songs and play counts" (issue #5). Refined with the owner: the list defaults to the most recent month, and follows a period selected in the Overview's over-time chart; the artist page counts plays in that same period and also shows an all-time total. Updated 2026-10-18: the owner asked for the feature in both dashboards (Streamlit and TypeScript), which now sit side by side (constitution 1.1).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See this month's new artists (Priority: P1)

On the Overview, I see a list of the artists I heard for the first time in the most recent month,
with album art and how many times I played each, most played first. If I've clicked a month (or
week or year) in the "Scrobbles per …" chart, the list shows the new artists of that period instead.

**Why this priority**: there is no list of new artists today, only a count per period. Without the
list there is nothing to click, so the rest of the feature depends on it.

**Independent Test**: open the Overview with no period selected and compare the list with the
artists whose first-ever play falls in the latest month; then click another month and check the
list changes to that month's new artists.

**Acceptance Scenarios**:

1. **Given** the Overview with no period selected and data through 12 Oct 2026, **When** the page
   loads, **Then** a list titled "New artists in Oct 2026" shows every artist whose first-ever play
   falls between 1 and 12 Oct 2026, each with album art and its play count in that period, sorted by
   play count, highest first.
2. **Given** the Overview, **When** I click the "Mar 2026" bar in the over-time chart, **Then** the
   list is titled "New artists in Mar 2026" and shows the artists first heard in March 2026.
3. **Given** a sidebar range that ends partway through a month, **When** no period is selected,
   **Then** the list covers that month only up to the range's last day.

---

### User Story 2 - Open a new artist's page (Priority: P2)

Clicking an artist in the list opens a page for that artist showing their name, album art, and
every song of theirs I played in the list's period with the play count for each, most played first.

**Why this priority**: this is what issue #5 is for: seeing what got me into a new artist.

**Independent Test**: click an artist in the list and compare the page's songs and counts with that
artist's plays in the same period.

**Acceptance Scenarios**:

1. **Given** the "New artists in Mar 2026" list, **When** I click anywhere on an artist's row (name,
   art or count), **Then** that artist's page opens.
2. **Given** an artist's page opened from the March 2026 list, **Then** it shows the artist's name,
   a large album cover, a line like "37 plays in Mar 2026 · 52 all time", and a list of every song I
   played by them in March 2026 with its album art, album and March play count, highest first.
3. **Given** the same page, **Then** the song play counts add up to the period total in the header.

---

### User Story 3 - Placeholders and the way back (Priority: P3)

When album art is missing, a placeholder image is shown, and the page always offers a way back to
the Overview.

**Why this priority**: polish that #5 asks for explicitly, but the page is useful without it.

**Independent Test**: open the page for an artist with no album art and use the back link.

**Acceptance Scenarios**:

1. **Given** an artist or song with no album art, **When** it is shown in the list or on the artist
   page, **Then** a placeholder image appears in its place.
2. **Given** an artist's page, **When** I click "Overview", **Then** the Overview opens.

### Edge Cases

- No new artists in the period: the list says so instead of showing an empty table.
- The artist page is opened without an artist, or with one that has no plays: it shows a short
  message and the link back to the Overview.
- The artist page is opened without a period: it covers all time.
- Last.fm's own grey "no image" picture counts as missing art.
- An artist heard first in an earlier period but played again in this one is not "new" and does not
  appear in the list.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Overview MUST show a "New artists" list of artists whose first-ever play falls in
  the list's period.
- **FR-002**: The list's period MUST be the period selected in the over-time chart if there is one;
  otherwise the most recent calendar month within the sidebar range (from its first day, or the
  range's start if later, to the range's end).
- **FR-003**: The list MUST be titled with its period (e.g. "New artists in Oct 2026") and show, for
  each artist, album art and the number of plays in the period, sorted by plays, highest first.
  A period that starts on the 1st and stays within one month is named by its month ("Oct 2026"),
  even if it ends before the month does; one that starts on 1 January and stays within one year
  is named by its year ("2026"); any other period is shown as "d Mon YYYY – d Mon YYYY". The
  artist page names its period the same way.
- **FR-004**: Clicking anywhere on an artist's row MUST open that artist's page for the list's
  period.
- **FR-005**: The artist page MUST show the artist's name and album art: the cover that appears most
  often in their plays in the period, otherwise across all their plays, otherwise a placeholder.
- **FR-006**: The artist page MUST show the number of plays in the period and the number of plays
  of all time.
- **FR-007**: The artist page MUST list every song by the artist played in the period with its album
  art, album and play count in the period, sorted by play count, highest first. Versions that the
  existing data already counts as the same song (e.g. "Remastered") are counted together.
- **FR-008**: Missing album art MUST be shown as a placeholder image, in the list and on the artist
  page.
- **FR-009**: The artist page MUST have a link back to the Overview.
- **FR-010**: The artist page MUST have its own address, including the artist and period, so it can
  be reloaded or bookmarked.
- **FR-011**: The artist page MUST NOT appear as an entry in the dashboard's page menu; it is
  reached from the list.
- **FR-012**: Both dashboards (Streamlit and TypeScript) MUST have the list and the artist page,
  at the same address, and MUST show the same artists, songs and counts for the same period.

### Key Entities

- **Play (scrobble)**: one listen: artist, song, album, album art, time.
- **New artist (for a period)**: an artist whose earliest play ever falls within the period.
- **Period**: a start and end date: the selected week, month or year, or the most recent month.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: From the Overview, the songs I played by a new artist this month are two clicks away
  (open the list's artist, read the page), down from writing a database query.
- **SC-002**: For a sample period and artist, the list's artists and the page's counts match the
  underlying listening data exactly (0 discrepancies).
- **SC-003**: Every artist and song row shows an image: real album art or the placeholder (no blank
  cells).
- **SC-004**: Clicking the name, art or count of a list row opens the artist page every time.
- **SC-005**: For the same period and artist, the two dashboards show identical lists and counts.

## Assumptions

- "New" means first heard ever in the whole listening history, not just within the sidebar range.
- "This month" is the most recent calendar month that the sidebar range reaches, which is the
  current month when the data is up to date.
- Returning to the Overview from the artist page shows the Overview without the previously clicked
  period; keeping it is out of scope.
- The Genre page keeps leaving missing art blank; linking its artists to the new page is a possible
  follow-up, out of scope here.
- Album art comes from the images already stored with each play; no new downloads or lookups.
