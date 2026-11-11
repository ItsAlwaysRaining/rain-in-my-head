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
- **THEN** Analyst has no lock, and Visitors shows a lock icon that a screen reader announces as locked with "Owner only"

#### Scenario: Open sections look as before
- **WHEN** a section is one the visitor can open
- **THEN** it has no lock and looks and behaves as it does today

### Requirement: A click on a locked section shows no data
A locked section SHALL stay a link to its normal address. Opening it SHALL send a logged-out visitor to the login page, or show "Not available to you" to a logged-in visitor. It SHALL NOT make any data request.

#### Scenario: Logged-out click
- **WHEN** a logged-out visitor clicks Analyst
- **THEN** they are sent to the login page and no data request is made

#### Scenario: Guest click
- **WHEN** a guest clicks Visitors
- **THEN** the page "Not available to you" shows and no data request is made

### Requirement: The menu fits narrow screens
At 800px wide and below, the top bar SHALL show the cloud logo and a menu button at least 44×44px in place of the section links. The button SHALL be labelled "Menu" for screen readers and SHALL report whether the menu is open. Pressing it SHALL open a Mobile menu that lists every section in the usual order, with the same lock marks and screen-reader lock text as the top bar, and Log out when logged in. The Mobile menu SHALL close when a link in it is chosen, when Escape is pressed (returning focus to the button), or when the button is pressed again. No section SHALL be cut off or need sideways scrolling at 360px wide.

#### Scenario: Phone width
- **WHEN** the site is opened at 360px wide
- **THEN** the top bar shows the logo and a 44px menu button, and no section link
- **AND** pressing the button shows all seven sections without sideways scrolling

#### Scenario: Choosing a section closes the menu
- **WHEN** the Mobile menu is open and the visitor chooses About
- **THEN** the About page opens and the Mobile menu is closed

#### Scenario: Escape closes the menu
- **WHEN** the Mobile menu is open and the visitor presses Escape
- **THEN** the menu closes and focus is on the menu button

#### Scenario: Locked section in the Mobile menu
- **WHEN** a guest opens the Mobile menu
- **THEN** Visitors shows the lock icon and a screen reader announces it as locked with "Owner only"

### Requirement: Tablet widths use short labels
Between 801px and 1100px wide, the top bar SHALL show "Playlists" for Playlist Generator and "Contact" for Contact Me. Every other label SHALL stay the same. Above 1100px the full labels SHALL show.

#### Scenario: Tablet width
- **WHEN** the site is opened at 1000px wide
- **THEN** the top bar shows "Playlists" and "Contact" on one line with the other sections

#### Scenario: Desktop width
- **WHEN** the site is opened at 1440px wide
- **THEN** the top bar shows "Playlist Generator" and "Contact Me"

### Requirement: Log in is in the top bar when logged out
On the hosted site, a visitor who is not logged in SHALL see a "Log in" link at the end of the top bar and of the Mobile menu, where Log out is shown when logged in. It SHALL go to the login page. It SHALL NOT be shown when logged in, or on the owner's Mac.

#### Scenario: Logged-out visitor
- **WHEN** a logged-out visitor opens any page on the hosted site
- **THEN** the top bar ends with "Log in", and choosing it opens the login page

#### Scenario: Logged-in visitor
- **WHEN** a logged-in visitor opens any page
- **THEN** the top bar shows Log out and no Log in
