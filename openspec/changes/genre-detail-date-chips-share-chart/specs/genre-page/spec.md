## ADDED Requirements

### Requirement: Date range chips
The Genre page SHALL show date range chips Last 30 days, This year, Last 12 months, All time and Custom, matching the Overview. The chosen preset SHALL be stored in the URL as `preset` (plus `start` and `end` for Custom). With no `preset` and no dates the page SHALL use All time. With `start`/`end` but no `preset` the page SHALL treat the range as Custom.

#### Scenario: Pick a preset
- **WHEN** the visitor clicks "Last 30 days"
- **THEN** the URL gets `preset=last30`, `start`/`end` are removed, and the header, chart and artist list show the last 30 days with data

#### Scenario: Custom range
- **WHEN** the visitor clicks "Custom", picks dates and clicks Apply
- **THEN** the URL gets `preset=custom&start=…&end=…` and nothing changes until Apply

#### Scenario: Old link with dates only
- **WHEN** the page opens with `?genre=indie&start=2025-01-01&end=2025-06-30`
- **THEN** the Custom chip is selected and that range is shown

### Requirement: Share of tagged plays chart
The Genre page SHALL show an area chart titled "Share of tagged plays": for each step (week for ranges up to about 3 months, else month) the genre's plays divided by all plays with a tag in that step. The area SHALL use the genre's colour from the shared chart palette (`GENRE_COLORS`): the genre's position in the top genres for the same range, as the Overview colours it; a genre outside the top 6 SHALL use Rain. The highest point SHALL carry a label with its percentage.

#### Scenario: Genre in the top 6
- **WHEN** Indie is 5th in the range's top genres
- **THEN** the area is Moss (`GENRE_COLORS[4]`), the same colour as its Overview line

#### Scenario: Peak label
- **WHEN** the chart draws
- **THEN** one label shows the peak share (for example "34%") at the highest point

#### Scenario: No plays
- **WHEN** the genre has no plays in the range
- **THEN** the chart is replaced by the existing "No plays in this genre for this range." notice
