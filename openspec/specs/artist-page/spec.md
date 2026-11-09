# artist-page Specification

## Purpose
The Artist page shows one artist's plays: a header with totals and the first play date, a per-month play chart, and the songs they played. The chart narrows the song list to one month, so a reader can see when the artist's plays happened and what was played then.

## Requirements

### Requirement: Header shows the first play date
The Artist page header SHALL show the date of the artist's first play in the header line, after the play counts. The date uses the same format as the rest of the dashboard (e.g. "2 Mar 2026"). The first play date counts all plays the artist has, not only the selected period.

#### Scenario: Header with a first play date
- **WHEN** the artist has 42 plays in the last 12 months, 120 plays all time, and the first play was on 2 March 2026
- **THEN** the header line reads "42 plays in last 12 months · 120 all time · first played 2 Mar 2026"

#### Scenario: Artist with plays in one day
- **WHEN** all of the artist's plays happened on 9 November 2026
- **THEN** the header shows "first played 9 Nov 2026"

### Requirement: Plays per month chart
The Artist page SHALL show a "Plays per month" line chart with one point per calendar month, including months with no plays (shown as zero). When the page has no period, the months run from the artist's first play to their latest play. When the page has a period, the months run across that period. The chart SHALL use the dashboard's chart colours and style.

#### Scenario: Chart covers every month between first and last play
- **WHEN** the page has no period, the artist's first play was in March 2026 and their last play was in June 2026, with no plays in April
- **THEN** the chart has four points, March to June 2026, and April is at zero

#### Scenario: Chart covers the page period
- **WHEN** the page was opened for 1 January to 31 March 2026
- **THEN** the chart has three points, January to March 2026

### Requirement: Clicking a month filters the songs
Clicking a point on the "Plays per month" chart SHALL select that month. While a month is selected, the Songs list SHALL show only plays from that month, and the selected month SHALL be shown as the filter label (e.g. "Oct 2026 only") with a "show every month" button. Pressing "show every month" SHALL clear the selection and restore the full Songs list for the page's period.

#### Scenario: Select a month
- **WHEN** the user clicks the October 2026 point
- **THEN** the Songs list shows only songs played in October 2026
- **AND** the label "Oct 2026 only" and a "show every month" button are shown

#### Scenario: Clear the month filter
- **WHEN** a month is selected and the user presses "show every month"
- **THEN** the Songs list shows every song for the page's period again
- **AND** the "Oct 2026 only" label is removed

#### Scenario: Month with no plays for the chosen period
- **WHEN** the user selects a month inside the page's period in which the artist has no plays
- **THEN** the Songs list shows an empty-state notice naming that month

### Requirement: Month filter respects the page period
The month filter SHALL apply within the period the Artist page was opened with. A month outside that period SHALL NOT be selectable.

#### Scenario: Month outside the period
- **WHEN** the Artist page was opened for 1 January to 31 March 2026
- **THEN** the chart shows points only for months in that period and a click cannot select a month outside it
