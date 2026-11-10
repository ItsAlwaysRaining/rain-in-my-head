## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: Tablet widths use short labels
Between 801px and 1100px wide, the top bar SHALL show "Playlists" for Playlist Generator and "Contact" for Contact Me. Every other label SHALL stay the same. Above 1100px the full labels SHALL show.

#### Scenario: Tablet width
- **WHEN** the site is opened at 1000px wide
- **THEN** the top bar shows "Playlists" and "Contact" on one line with the other sections

#### Scenario: Desktop width
- **WHEN** the site is opened at 1440px wide
- **THEN** the top bar shows "Playlist Generator" and "Contact Me"
