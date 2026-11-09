# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: Send email and Download CV`
- TO: `### Requirement: Send email and View CV`

## MODIFIED Requirements

### Requirement: Send email and View CV
Below the list, the page SHALL show a primary **Send email** button and a secondary **View CV** button. Send email SHALL open a `mailto:` link to the same address as the Email entry. View CV SHALL open the owner's résumé page on Notion (`https://app.notion.com/p/R-sum-Data-Product-Designer-407bd4600b7981808f4fef088372c75e`) in a new tab, and the Contact Me page SHALL stay open in the original tab.

#### Scenario: Send email
- **WHEN** a visitor activates Send email
- **THEN** their mail app opens a new message to the address shown in the Email entry

#### Scenario: Download CV
- **WHEN** a visitor activates View CV
- **THEN** the Notion résumé page opens in a new tab and the Contact Me page stays open in the original tab

### Requirement: Keyboard and screen-reader access
Every contact entry and both buttons SHALL be reachable with the Tab key, in reading order, and SHALL show a visible focus outline. Each contact link SHALL have an accessible name that says which service it is and where it goes. Icons SHALL NOT be announced separately from the name next to them. A link that opens a new tab SHALL say so to screen readers.

#### Scenario: Tab through the page
- **WHEN** a keyboard user tabs from the breadcrumbs through the page
- **THEN** focus moves to Email, LinkedIn, GitHub, Last.fm, Send email and View CV in that order, with a visible outline on each

#### Scenario: Screen reader names
- **WHEN** a screen reader reads the GitHub entry
- **THEN** it announces a link naming GitHub and the address, says it opens in a new tab, and doesn't read the icon as a separate item

#### Scenario: Screen reader names View CV
- **WHEN** a screen reader reads the View CV button
- **THEN** it announces a link naming the résumé and says it opens in a new tab
