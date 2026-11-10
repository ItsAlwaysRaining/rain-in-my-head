## ADDED Requirements

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
