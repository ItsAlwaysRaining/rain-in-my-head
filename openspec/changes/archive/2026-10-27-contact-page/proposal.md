# Proposal

## Why

The Contact Me link in the top nav opens a "Coming soon" placeholder (issue #34). The site is part of a portfolio, so visitors need a way to reach the owner about the project or a role. The Figma file already has the layout (**Contact Me · Desktop**, node `362:20290`, on the **3 Prototype** page).

## What Changes

- Replace the `Contact` placeholder in `web/src/pages/Placeholders.tsx` with a real page that follows the Figma frame: the existing "Contact Me" title and intro line, then a **Get in touch** section with four rows (Email, LinkedIn, GitHub, Last.fm), each with an icon in a circle, the service name and the address, then a **Send email** (primary) and **Download CV** (secondary) button.
- Each row is a link: Email opens a `mailto:` link, and the other three open the profile in a new tab.
- Links:
  - GitHub: `github.com/ItsAlwaysRaining` (real).
  - Last.fm: `last.fm/user/ItsAlwaysRaining` (real).
  - Email: `hello@example.com` for now. The owner swaps in a real address before the issue is closed.
  - LinkedIn: `linkedin.com/in/your-name` for now. The owner swaps in the real profile before the issue is closed.
- **Download CV** downloads `web/public/contact/cv.pdf`. For now that's a one-page placeholder PDF, which the owner replaces with the real CV.
- On narrow screens the rows fill the content width and the page never scrolls sideways.

The route (`/contact`), the top-nav link and the breadcrumbs already exist and don't change.

**Track**: OpenSpec, because this adds content to a page that already exists (route, nav link and placeholder are in place). The owner uses OpenSpec for such changes. It adds no CLI command, data source, dependency or schema change.

## Capabilities

### New Capabilities
- `contact-page`: what the Contact Me page shows (contact links, Send email, Download CV, layout at wide and narrow widths), how it's reached, and how keyboard and screen-reader users use it.

### Modified Capabilities
<!-- None: the shell (nav, breadcrumbs, routes) doesn't change. -->

## Impact

- `web/src/pages/Placeholders.tsx`: `Contact` removed from here.
- New `web/src/pages/Contact.tsx` and `Contact.module.css`. `web/src/App.tsx` imports `Contact` from the new file.
- `web/src/components/ui.tsx`: a `ButtonLink` (an `<a>` with the existing primary or secondary button look), because Send email and Download CV are links, not actions.
- New static assets in `web/public/contact/`: `mail.svg`, `linkedin.svg`, `github.svg`, `lastfm.svg` (from the Figma icon components) and the placeholder `cv.pdf`.
- No new dependencies, API calls or data changes.
- Conflicts: the in-flight About page change (branch `feature/about-page`) also edits `Placeholders.tsx` and `App.tsx`. Whichever PR merges second needs a small rebase.
