# contact-page Specification

## Purpose
The Contact Me page of the TypeScript app: how visitors to the portfolio site reach the owner by email or on LinkedIn, GitHub and Last.fm, and get the owner's CV.

## Requirements

### Requirement: Reached from the top nav
The Contact Me page SHALL open at `/contact` from the **Contact Me** link in the top nav. The link SHALL show as the current section while the page is open, and the breadcrumbs SHALL read Home › Contact Me.

#### Scenario: Open from the nav
- **WHEN** a visitor clicks **Contact Me** in the top nav
- **THEN** the Contact Me page opens at `/contact`, the Contact Me link is highlighted and the breadcrumbs read Home › Contact Me

#### Scenario: No placeholder
- **WHEN** the Contact Me page is open
- **THEN** no "Coming soon" notice or link to issue #34 appears on it

### Requirement: Contact links
Below the title **Contact Me** and its intro line, the page SHALL have a section headed **Get in touch** listing, in this order, Email, LinkedIn, GitHub, Last.fm, Résumé and Portfolio. Each entry SHALL show the service's icon, the name and the address. Each entry SHALL be a link: Email SHALL open a `mailto:` link to the shown address, and every other entry SHALL open the shown page in a new tab. Résumé SHALL open the owner's résumé page on Notion (`https://app.notion.com/p/R-sum-Data-Product-Designer-407bd4600b7981808f4fef088372c75e`), and Portfolio SHALL open the owner's portfolio page on Notion (`https://app.notion.com/p/3f3bd4600b7980d088a1e74e415022d3`). Résumé and Portfolio SHALL use the Notion icon. Every entry SHALL point at the owner's real address or page, with no placeholder values: email `August@storyandstructure.studio`, LinkedIn `augustowheeler`, GitHub `ItsAlwaysRaining`, Last.fm `UntiLiUnderstan`.

#### Scenario: Four entries in order
- **WHEN** the Contact Me page is open
- **THEN** the Get in touch section lists Email, LinkedIn, GitHub, Last.fm, Résumé and Portfolio in that order, each with an icon, a name and an address

#### Scenario: Email entry
- **WHEN** a visitor activates the Email entry
- **THEN** their mail app opens a new message to `August@storyandstructure.studio`

#### Scenario: Profile entry
- **WHEN** a visitor activates the GitHub entry
- **THEN** `https://github.com/ItsAlwaysRaining` opens in a new tab, and the Contact Me page stays open in the original tab

#### Scenario: Résumé entry
- **WHEN** a visitor activates the Résumé entry
- **THEN** the Notion résumé page opens in a new tab, and the Contact Me page stays open in the original tab

#### Scenario: Portfolio entry
- **WHEN** a visitor activates the Portfolio entry
- **THEN** the Notion portfolio page opens in a new tab, and the Contact Me page stays open in the original tab

### Requirement: Keyboard and screen-reader access
Every contact entry SHALL be reachable with the Tab key, in reading order, and SHALL show a visible focus outline. Each contact link SHALL have an accessible name that says which service it is and where it goes. Icons SHALL NOT be announced separately from the name next to them. A link that opens a new tab SHALL say so to screen readers.

#### Scenario: Tab through the page
- **WHEN** a keyboard user tabs from the breadcrumbs through the page
- **THEN** focus moves to Email, LinkedIn, GitHub, Last.fm, Résumé and Portfolio in that order, with a visible outline on each

#### Scenario: Screen reader names
- **WHEN** a screen reader reads the GitHub entry
- **THEN** it announces a link naming GitHub and the address, says it opens in a new tab, and doesn't read the icon as a separate item

#### Scenario: Screen reader names Résumé
- **WHEN** a screen reader reads the Résumé entry
- **THEN** it announces a link naming the résumé, says it opens in a new tab, and doesn't read the icon as a separate item

### Requirement: Layout at wide and narrow widths
On wide screens the contact list SHALL be 480 px wide with the name on the left and the address on the right of each entry. On narrow screens the list SHALL fit the content width, addresses SHALL stay fully readable, and the page SHALL never scroll sideways.

#### Scenario: Desktop
- **WHEN** the window is 1440 px wide
- **THEN** the contact list is 480 px wide, each name is on the left and each address on the right

#### Scenario: Phone
- **WHEN** the window is 390 px wide
- **THEN** every address is fully visible and the page has no horizontal scroll
