# Spec Delta

## MODIFIED Requirements

### Requirement: Contact links
Below the title **Contact Me** and its intro line, the page SHALL have a section headed **Get in touch** listing, in this order, Email, LinkedIn, GitHub, Last.fm, Résumé and Portfolio. Each entry SHALL show the service's icon, the name and the address. Each entry SHALL be a link: Email SHALL open a `mailto:` link to the shown address, and every other entry SHALL open the shown page in a new tab. Résumé SHALL open the owner's résumé page on Notion (`https://app.notion.com/p/R-sum-Data-Product-Designer-407bd4600b7981808f4fef088372c75e`), and Portfolio SHALL open the owner's portfolio page on Notion (`https://app.notion.com/p/3f3bd4600b7980d088a1e74e415022d3`). Résumé and Portfolio SHALL use the Notion icon. Every entry SHALL point at the owner's real address or page, with no placeholder values: email `August@storyandstructure.studio`, LinkedIn `augustowheeler`, GitHub `ItsAlwaysRaining`, Last.fm `UntiLiUnderstan`.

#### Scenario: Six entries in order
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

## REMOVED Requirements

### Requirement: Send email and Download CV
**Reason**: The Send email button is removed because the Email entry already opens a mail message. The CV button is replaced by the Résumé entry in the Contact links list.
**Migration**: Use the Email entry to send email and the Résumé entry to open the CV. Nothing else depends on the buttons.
