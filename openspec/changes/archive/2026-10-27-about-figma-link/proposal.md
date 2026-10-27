# Proposal

## Why

Every page of Rain in My Head is designed in Figma first, and the site is part of a UI/UX portfolio, but nothing on the site or in the repo links to the Figma file (issue #42). The file is private for now. The owner will make it public when the project is finished, so the link goes in now.

## What Changes

- The About page's **About This App** section gets a second paragraph saying each page was designed in Figma first, with a link to the design file (`https://www.figma.com/design/1rbbEne7pW8oA2JCNmjhrm`) that opens in a new tab.
- The README gets a **Design** section linking the Figma file and the design reference page (docs only, no spec needed).

**Track**: OpenSpec, because this adds a link to a page that already exists. No new page, CLI command, data source, dependency or schema change.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `about-page`: adds a requirement for the Figma link in About This App.

## Impact

- `web/src/pages/About.tsx`: one paragraph and a link. `About.module.css`: a visually hidden "(opens in a new tab)" hint, as on the Contact page.
- `README.md`: new Design section.
- No new dependencies, API calls or data changes.
