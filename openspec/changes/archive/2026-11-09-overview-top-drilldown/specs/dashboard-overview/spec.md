## ADDED Requirements

### Requirement: Top lists show ranked rows
The Overview's Top block SHALL show Artists, Tracks and Albums as ranked lists of rows, most played first, each with its play count at the end of the row. The "#1 per year" tab and the tab order SHALL be unchanged. The lists SHALL follow the sidebar range and any selected period.

#### Scenario: Artists tab
- **WHEN** the user opens the Overview with the Artists tab selected
- **THEN** the tab shows up to 20 artist rows, most played first, each with its plays

#### Scenario: Top lists follow a selected period
- **WHEN** March 2026 is selected
- **THEN** the Artists, Tracks and Albums rows count only plays from 1–31 March 2026

### Requirement: Artist rows open the Artist page
Clicking an artist row in the Top block SHALL open the Artist detail page for that artist, with the Overview's current range (the sidebar range, or the selected period when one is set) carried over in the address.

#### Scenario: Click an artist in the Top list
- **WHEN** the sidebar range is Last 12 months and the user clicks the artist "Hozier" in the Artists tab
- **THEN** the Artist page opens for Hozier with the Last 12 months range

#### Scenario: Click an artist while a period is selected
- **WHEN** March 2026 is selected and the user clicks an artist row
- **THEN** the Artist page opens for that artist with the range 1–31 March 2026

### Requirement: Track and album rows are not clickable yet
Rows in the Tracks and Albums tabs SHALL NOT show a clickable state or open a page, until a design defines their drill-down.

#### Scenario: Click a track row
- **WHEN** the user clicks a row in the Tracks tab
- **THEN** nothing happens and the row shows no hover or pointer state
