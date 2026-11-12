## ADDED Requirements

### Requirement: The page shows one weekday and hour
The Listening slot page SHALL show the tracks played on one weekday (Monday to Sunday) in one hour of the day (0 to 23), in the date range given. The title names the slot, for example "Thursdays, 15:00–16:00". Under it a summary SHALL show the range, the slot's play count, its number of different tracks and, when the slot has the most plays of any weekday and hour in the range, "your busiest hour of the week".

#### Scenario: Slot with plays
- **WHEN** the user opens the page for Thursday, hour 15, for the last 12 months, and that slot has 291 plays of 214 different tracks and is the busiest slot
- **THEN** the title reads "Thursdays, 15:00–16:00" and the summary reads "Last 12 months · 291 plays · 214 different tracks · your busiest hour of the week"

#### Scenario: Counts match the heatmap
- **WHEN** the page opens from a heatmap square
- **THEN** the play count equals the square's count for the same range

#### Scenario: Unknown day or hour
- **WHEN** the page is opened with a day that is not Mon–Sun or an hour outside 0–23
- **THEN** the page shows a notice that the slot does not exist and no table

### Requirement: The page lists the tracks in the slot
The page SHALL list the 100 most played tracks in the slot, each with its album art, song name, artist and play count, most played first. When there are more, a caption SHALL say "Showing 100 of N tracks, most played first." An empty slot SHALL show a notice saying there were no plays in that slot for the range, not an empty table.

#### Scenario: Sorted by plays
- **WHEN** Too Sweet has 9 plays and Edamame 8 in the slot
- **THEN** Too Sweet is listed first

#### Scenario: Empty slot
- **WHEN** the slot has no plays in the range
- **THEN** the page shows a notice and no table

### Requirement: Day, Hour and range are in the address
The page SHALL read `day`, `hour`, `preset`, `start` and `end` from its address, and changing the Day picker, Hour picker or date range chips SHALL update the address and the table. Dates without a preset are Custom, so the heatmap link (which carries the Overview's resolved dates) covers exactly the plays of the square clicked.

#### Scenario: Opened from the heatmap
- **WHEN** the Overview shows 1–31 March 2026 and the user clicks the Thursday 15:00 square
- **THEN** the page opens for Thursday, 15:00–16:00, 1–31 March 2026, with Custom selected

#### Scenario: Change the hour
- **WHEN** the user picks 16:00–17:00 in the Hour picker
- **THEN** the address's `hour` becomes 16 and the table shows that hour's tracks

### Requirement: Track rows open the Artist page
Clicking a track row SHALL open the Artist page for the track's artist with the page's range.

#### Scenario: Click a track
- **WHEN** the user clicks Too Sweet by Hozier
- **THEN** the Artist page opens for Hozier with the same range

### Requirement: Listening slot page is available to guests
The page and `GET /api/slot` SHALL be open to every visitor who can open the Dashboards pages, under the existing `slot` page key.

#### Scenario: Guest opens a slot
- **WHEN** a guest opens the page
- **THEN** the page loads its data
