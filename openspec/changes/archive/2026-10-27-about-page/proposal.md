# Proposal

## Why

The About link in the top nav opens a "Coming soon" placeholder (issue #33). The site is part of a portfolio, so visitors need to know who made it and why. The Figma file already has the layout (**About · Desktop**, node `262:1334`) and the material for the copy (the **1 · Research** page).

## What Changes

- Replace the `About` placeholder in `web/src/pages/Placeholders.tsx` with a real page that follows the Figma frame: an "About" title, then a 420 × 480 photo beside a text column with **About Me** and **About This App** sections.
- Write real copy from the Figma Research page in place of the design's lorem ipsum:
  - **About Me**: the "Me, at 1 a.m." persona (listens all day; opens the app late, out of curiosity; wants to be surprised, then dig in) and the problem statement (missing the Windows Media Player features of around 2004 that streaming never brought back).
  - **About This App**: the North Star ("control over my own data to perform my own analytics"), the questions the dashboards answer, the playlists for times of day and seasons of life, and where the data comes from (Last.fm; Spotify only to create playlists).
- Show a photo with alt text. Figma has no photo yet, only a placeholder, so the page loads `web/public/about/photo.jpg` and shows the design's dashed placeholder frame until that file is added.
- On narrow screens the photo stacks above the text.

The route (`/about`), the top-nav link and the breadcrumbs already exist and don't change.

**Track**: the project's OpenSpec rule recommends Spec Kit for a new page. The owner chose OpenSpec because the page, route and nav link already exist as a placeholder; this change fills in one existing page, adds no CLI command, data source, dependency or schema change, and touches one module.

## Capabilities

### New Capabilities
- `about-page`: what the About page shows (copy, photo, layout at wide and narrow widths) and how it's reached.

### Modified Capabilities
<!-- None: the shell (nav, breadcrumbs, routes) doesn't change. -->

## Impact

- `web/src/pages/Placeholders.tsx`: `About` removed from here.
- New `web/src/pages/About.tsx` and `About.module.css`; `web/src/App.tsx` imports `About` from the new file.
- New static asset `web/public/about/image.svg` (the Figma `icon/image` icon for the empty photo frame). `web/public/about/photo.jpg` is added by the owner.
- No new dependencies, API calls or data changes.
