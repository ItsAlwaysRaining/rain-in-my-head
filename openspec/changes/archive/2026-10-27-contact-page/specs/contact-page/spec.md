# Spec Delta

## Purpose

The Contact Me page of the TypeScript app: how visitors to the portfolio site reach the owner by email or on LinkedIn, GitHub and Last.fm, and get the owner's CV.

## ADDED Requirements

### Requirement: Reached from the top nav
The Contact Me page SHALL open at `/contact` from the **Contact Me** link in the top nav. The link SHALL show as the current section while the page is open, and the breadcrumbs SHALL read Home › Contact Me.

#### Scenario: Open from the nav
- **WHEN** a visitor clicks **Contact Me** in the top nav
- **THEN** the Contact Me page opens at `/contact`, the Contact Me link is highlighted and the breadcrumbs read Home › Contact Me

#### Scenario: No placeholder
- **WHEN** the Contact Me page is open
- **THEN** no "Coming soon" notice or link to issue #34 appears on it

### Requirement: Contact links
Below the title **Contact Me** and its intro line, the page SHALL have a section headed **Get in touch** listing, in this order, Email, LinkedIn, GitHub and Last.fm. Each entry SHALL show the service's icon, the service name and the address. Each entry SHALL be a link: Email SHALL open a `mailto:` link to the shown address, and LinkedIn, GitHub and Last.fm SHALL open the shown profile in a new tab. The GitHub and Last.fm entries SHALL point at the owner's profiles (`ItsAlwaysRaining`).

#### Scenario: Four entries in order
- **WHEN** the Contact Me page is open
- **THEN** the Get in touch section lists Email, LinkedIn, GitHub and Last.fm in that order, each with an icon, a name and an address

#### Scenario: Email entry
- **WHEN** a visitor activates the Email entry
- **THEN** their mail app opens a new message to the shown address

#### Scenario: Profile entry
- **WHEN** a visitor activates the GitHub entry
- **THEN** `https://github.com/ItsAlwaysRaining` opens in a new tab, and the Contact Me page stays open in the original tab

### Requirement: Send email and Download CV
Below the list, the page SHALL show a primary **Send email** button and a secondary **Download CV** button. Send email SHALL open a `mailto:` link to the same address as the Email entry. Download CV SHALL download a PDF file rather than navigate away from the page.

#### Scenario: Send email
- **WHEN** a visitor activates Send email
- **THEN** their mail app opens a new message to the address shown in the Email entry

#### Scenario: Download CV
- **WHEN** a visitor activates Download CV
- **THEN** the browser downloads a PDF file and the Contact Me page stays open

### Requirement: Keyboard and screen-reader access
Every contact entry and both buttons SHALL be reachable with the Tab key, in reading order, and SHALL show a visible focus outline. Each contact link SHALL have an accessible name that says which service it is and where it goes. Icons SHALL NOT be announced separately from the name next to them. A link that opens a new tab SHALL say so to screen readers.

#### Scenario: Tab through the page
- **WHEN** a keyboard user tabs from the breadcrumbs through the page
- **THEN** focus moves to Email, LinkedIn, GitHub, Last.fm, Send email and Download CV in that order, with a visible outline on each

#### Scenario: Screen reader names
- **WHEN** a screen reader reads the GitHub entry
- **THEN** it announces a link naming GitHub and the address, says it opens in a new tab, and doesn't read the icon as a separate item

### Requirement: Layout at wide and narrow widths
On wide screens the contact list SHALL be 480 px wide with the name on the left and the address on the right of each entry. On narrow screens the list SHALL fit the content width, addresses SHALL stay fully readable, and the page SHALL never scroll sideways.

#### Scenario: Desktop
- **WHEN** the window is 1440 px wide
- **THEN** the contact list is 480 px wide, each name is on the left and each address on the right

#### Scenario: Phone
- **WHEN** the window is 390 px wide
- **THEN** every address is fully visible and the page has no horizontal scroll
