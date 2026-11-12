## MODIFIED Requirements

### Requirement: Genre drill-down follows the selection
Clicking a genre chart while a period is selected SHALL open the Genre page for that period, with the Custom chip selected. Clicking a genre with no period selected SHALL open the Genre page with the Overview's preset (and its `start`/`end` when the preset is Custom), so the same chip is selected.

#### Scenario: Genre click within a month
- **WHEN** March 2026 is selected and the user clicks the "indie" genre chart
- **THEN** the Genre page opens for indie with the range 1–31 March 2026 and the Custom chip selected

#### Scenario: Genre click with a preset
- **WHEN** the Overview shows "Last 12 months" with no period selected and the user clicks the "indie" legend chip
- **THEN** the Genre page opens with `preset=last12m` and the "Last 12 months" chip selected
