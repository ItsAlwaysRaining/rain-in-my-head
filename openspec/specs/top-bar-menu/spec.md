# top-bar-menu Specification

## Purpose
TBD - created by archiving change show-all-menus. Update Purpose after archive.

## Requirements

### Requirement: Every section is in the top bar for everyone
The top bar SHALL list every section (Dashboards, Playlist Generator, Analyst, Visitors, AI, About, Contact Me) in the same order for every visitor: logged out, guest, trusted and owner. A section SHALL NOT be hidden because the visitor lacks access to it.

#### Scenario: Guest sees the full menu
- **WHEN** a logged-in guest opens any page
- **THEN** the top bar lists all seven sections

#### Scenario: Logged-out visitor sees the full menu
- **WHEN** a visitor who is not logged in opens the login page
- **THEN** the top bar lists all seven sections

#### Scenario: Owner on their Mac
- **WHEN** the site runs on the owner's Mac, where every page opens
- **THEN** the top bar lists all seven sections and none is marked locked

### Requirement: Locked sections look locked
A section the visitor cannot open SHALL be marked locked with a lock icon and a muted style. The lock SHALL also be given in text that a screen reader announces, with the reason: "Log in to open" when logged out, "Owner only" for Visitors, and "Not in your invite code" otherwise. Locked SHALL NOT be shown by colour alone.

#### Scenario: Guest and Analyst
- **WHEN** a logged-in guest looks at the top bar
- **THEN** Analyst shows a lock icon and a screen reader announces it as locked with "Not in your invite code"

#### Scenario: Open sections look as before
- **WHEN** a section is one the visitor can open
- **THEN** it has no lock and looks and behaves as it does today

### Requirement: A click on a locked section shows no data
A locked section SHALL stay a link to its normal address. Opening it SHALL send a logged-out visitor to the login page, or show "Not available to you" to a logged-in visitor. It SHALL NOT make any data request.

#### Scenario: Logged-out click
- **WHEN** a logged-out visitor clicks Analyst
- **THEN** they are sent to the login page and no data request is made

#### Scenario: Guest click
- **WHEN** a guest clicks Analyst
- **THEN** the page "Not available to you" shows and no data request is made

### Requirement: The menu fits narrow screens
The top bar SHALL stay usable at a 360px-wide screen with all seven sections, by wrapping onto more lines. No section SHALL be cut off or need sideways scrolling.

#### Scenario: Phone width
- **WHEN** the site is opened at 360px wide
- **THEN** every section can be reached without sideways scrolling
