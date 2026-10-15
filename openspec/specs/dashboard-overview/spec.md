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
Clicking a genre chart while a period is selected SHALL open the Genre page for that period.

#### Scenario: Genre click within a month
- **WHEN** March 2026 is selected and the user clicks the "indie" genre chart
- **THEN** the Genre page opens for indie with the range 1–31 March 2026
