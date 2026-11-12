# dashboard-overview Specification

## Purpose
The dashboard's Overview page summarises listening over a chosen date range. This covers how that range is chosen, including narrowing it to one period by clicking the over-time chart.

## Requirements

### Requirement: Select a period from the over-time chart
The Overview's over-time bar chart SHALL let the user select one period (a week, month or year, matching the chosen time grain) by clicking its bar. While a period is selected, every other figure and chart on the Overview SHALL show only plays within that period, intersected with the sidebar range. "#1 per year" is excluded and SHALL keep covering all data.

#### Scenario: Click a month
- **WHEN** the time grain is Month and the user clicks the bar for March 2026
- **THEN** the KPIs, Top lists, "When you listen", new artists, genre charts, mainstream chart, loved tracks and data quality show only plays from 1–31 March 2026
- **AND** the page caption shows "01 Mar 2026 – 31 Mar 2026"

#### Scenario: Partial period at the edge of the range
- **WHEN** the sidebar range starts on 14 October 2025 and the user clicks the October 2025 bar
- **THEN** the page shows plays from 14–31 October 2025 only

#### Scenario: KPI deltas
- **WHEN** a period is selected
- **THEN** each KPI delta compares the period with the period of the same length immediately before it

#### Scenario: "#1 per year" unchanged
- **WHEN** a period is selected
- **THEN** the "#1 per year" table still lists every year

### Requirement: The over-time chart keeps its full range
While a period is selected, the over-time chart SHALL keep showing every period in the sidebar range. The selected bar SHALL be highlighted and the other bars dimmed.

#### Scenario: Pick another period
- **WHEN** March 2026 is selected and the user clicks the May 2026 bar
- **THEN** May 2026 becomes the selected period and the page shows May 2026

### Requirement: Finer time steps inside a selected period
While a period is selected, the "New artists" chart and the genre charts SHALL plot per day when the period is a week or month, and per month when the period is a year. The over-time chart SHALL keep the chosen time grain.

#### Scenario: Month selected
- **WHEN** the user selects a month
- **THEN** the "New artists" chart is titled "New artists per day" and plots one point per day

#### Scenario: Year selected
- **WHEN** the time grain is Year and the user selects 2025
- **THEN** the "New artists" and genre charts plot one point per month of 2025

### Requirement: Clear the selection
While a period is selected, the Overview SHALL name the period in a caption next to a control that restores the whole sidebar range. Clicking the over-time chart's background SHALL also clear the selection.

#### Scenario: Show the whole range
- **WHEN** a period is selected and the user clicks "Show whole range"
- **THEN** no bar is highlighted and every figure shows the whole sidebar range again

#### Scenario: Range or grain changes
- **WHEN** a period is selected and the user changes the time grain, or picks a range that no longer contains that period
- **THEN** the selection is dropped and the page shows the whole new range

### Requirement: Genre drill-down follows the selection
Clicking a genre chart while a period is selected SHALL open the Genre page for that period, with the Custom chip selected. Clicking a genre with no period selected SHALL open the Genre page with the Overview's preset (and its `start`/`end` when the preset is Custom), so the same chip is selected.

#### Scenario: Genre click within a month
- **WHEN** March 2026 is selected and the user clicks the "indie" genre chart
- **THEN** the Genre page opens for indie with the range 1–31 March 2026 and the Custom chip selected

#### Scenario: Genre click with a preset
- **WHEN** the Overview shows "Last 12 months" with no period selected and the user clicks the "indie" legend chip
- **THEN** the Genre page opens with `preset=last12m` and the "Last 12 months" chip selected

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

### Requirement: Mainstream bars open the band's artists
Clicking a bar in the Overview's "Mainstream vs. niche" chart SHALL open the Mainstream vs. niche page for that listener band, with the Overview's current range (the sidebar range, or the selected period when one is set) carried over in the address.

#### Scenario: Click a bar
- **WHEN** the sidebar range is Last 12 months and the user clicks the `100k–1M` bar
- **THEN** the Mainstream vs. niche page opens for the band `100k–1M` with the Last 12 months range

#### Scenario: Click a bar while a period is selected
- **WHEN** March 2026 is selected and the user clicks the `5M+` bar
- **THEN** the page opens for the band `5M+` with the range 1–31 March 2026

### Requirement: Choose a custom date range in a popup
Choosing the "Custom" date-range chip SHALL open a popup directly under the chips with a From date, a To date, an Apply button and a Cancel button. The dates SHALL start at the current range and SHALL be limited to the days that have data, with From no later than To. The page SHALL NOT change while the visitor edits the dates. Apply SHALL set the range to the chosen dates, close the popup and keep the range in the URL. Cancel, or pressing Escape, SHALL close the popup and leave the range and chip as they were before Custom was chosen. With Custom already selected, the chip SHALL reopen the popup with the current dates. The page SHALL NOT show From and To fields outside the popup.

#### Scenario: Apply a custom range
- **WHEN** the visitor chooses Custom, sets From to 1 March 2026 and To to 31 March 2026, and presses Apply
- **THEN** the popup closes, the Custom chip is selected, and the page shows plays from 1–31 March 2026 only

#### Scenario: Cancel keeps the old range
- **WHEN** the visitor is on "Last 12 months", chooses Custom, changes the dates and presses Cancel
- **THEN** the popup closes and the page still shows "Last 12 months" with the same data

#### Scenario: Editing does not reload
- **WHEN** the visitor changes From in the open popup
- **THEN** the KPIs and charts stay as they were until Apply is pressed

#### Scenario: Reopen to edit
- **WHEN** a custom range is applied and the visitor presses the Custom chip again
- **THEN** the popup opens with the applied From and To dates
