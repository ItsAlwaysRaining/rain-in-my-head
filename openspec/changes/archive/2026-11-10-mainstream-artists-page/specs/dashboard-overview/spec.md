# Spec Delta

## ADDED Requirements

### Requirement: Mainstream bars open the band's artists
Clicking a bar in the Overview's "Mainstream vs. niche" chart SHALL open the Mainstream vs. niche page for that listener band, with the Overview's current range (the sidebar range, or the selected period when one is set) carried over in the address.

#### Scenario: Click a bar
- **WHEN** the sidebar range is Last 12 months and the user clicks the `100k–1M` bar
- **THEN** the Mainstream vs. niche page opens for the band `100k–1M` with the Last 12 months range

#### Scenario: Click a bar while a period is selected
- **WHEN** March 2026 is selected and the user clicks the `5M+` bar
- **THEN** the page opens for the band `5M+` with the range 1–31 March 2026
