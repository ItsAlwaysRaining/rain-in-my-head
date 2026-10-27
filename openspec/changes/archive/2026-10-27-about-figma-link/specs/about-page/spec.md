## ADDED Requirements

### Requirement: Link to the Figma design file
The **About This App** section SHALL end with a paragraph saying each page was designed in Figma first, containing a link to the Rain in My Head Figma design file (`https://www.figma.com/design/1rbbEne7pW8oA2JCNmjhrm`). The link SHALL open in a new tab, and its accessible name SHALL say what it links to and that it opens in a new tab.

#### Scenario: Follow the link
- **WHEN** a visitor clicks the Figma link in About This App
- **THEN** the Figma design file opens in a new tab and the About page stays open

#### Scenario: Screen reader
- **WHEN** a screen reader reaches the Figma link
- **THEN** it announces the link text naming the Figma design file, followed by "(opens in a new tab)"
