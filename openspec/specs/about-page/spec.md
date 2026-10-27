# about-page Specification

## Purpose
The About page of the TypeScript app: who made Rain in My Head and why, with a photo, so visitors to the portfolio site have context for the project.

## Requirements

### Requirement: Reached from the top nav
The About page SHALL open at `/about` from the **About** link in the top nav. The link SHALL show as the current section while the page is open, and the breadcrumbs SHALL read Home › About.

#### Scenario: Open from the nav
- **WHEN** a visitor clicks **About** in the top nav
- **THEN** the About page opens at `/about`, the About link is highlighted and the breadcrumbs read Home › About

### Requirement: Real copy in two sections
The page SHALL have the title **About** and two sections headed **About Me** and **About This App**, in that order, as headings below the title in the document outline. The text SHALL be final copy drawn from the project's Figma research (no placeholder or lorem ipsum text) and SHALL say that the listening data comes from Last.fm.

#### Scenario: Sections and headings
- **WHEN** the About page is open
- **THEN** it shows the title "About" as the page's only top-level heading, followed by the headings "About Me" and "About This App", each with at least one paragraph of text

#### Scenario: No placeholder text
- **WHEN** the About page is open
- **THEN** no "Coming soon" notice, link to issue #33 or lorem ipsum text appears on it

### Requirement: Photo with alt text
The page SHALL show a portrait photo of the owner in a 420 × 480 frame (scaled down to fit narrower screens, keeping that shape) with alt text that describes it. Until the photo file is added, the frame SHALL show an empty placeholder in the design's style, which screen readers skip, and the rest of the page SHALL be unaffected.

#### Scenario: Photo present
- **WHEN** the photo file is in place and the About page is open
- **THEN** the photo fills the frame without being stretched, and its alt text is read by a screen reader

#### Scenario: Photo missing
- **WHEN** the photo file has not been added yet
- **THEN** the frame shows the dashed placeholder with an image icon, no broken-image icon appears, and screen readers don't announce the empty frame

### Requirement: Layout at wide and narrow widths
On wide screens the photo SHALL sit to the left of the text column. On narrow screens the photo SHALL stack above the text. The page SHALL never scroll sideways.

#### Scenario: Desktop
- **WHEN** the window is 1440 px wide
- **THEN** the photo is on the left and the About Me and About This App sections are to its right

#### Scenario: Phone
- **WHEN** the window is 390 px wide
- **THEN** the photo is above the About Me section, fits the width of the content area, and the page has no horizontal scroll

### Requirement: Link to the Figma design file
The **About This App** section SHALL end with a paragraph saying each page was designed in Figma first, containing a link to the Rain in My Head Figma design file (`https://www.figma.com/design/1rbbEne7pW8oA2JCNmjhrm`). The link SHALL open in a new tab, and its accessible name SHALL say what it links to and that it opens in a new tab.

#### Scenario: Follow the link
- **WHEN** a visitor clicks the Figma link in About This App
- **THEN** the Figma design file opens in a new tab and the About page stays open

#### Scenario: Screen reader
- **WHEN** a screen reader reaches the Figma link
- **THEN** it announces the link text naming the Figma design file, followed by "(opens in a new tab)"
