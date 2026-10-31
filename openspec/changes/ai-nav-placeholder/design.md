# Design

## Context

The top nav is generated from `SECTIONS` in `web/src/routes.ts`. The breadcrumbs come from the same list, so adding one entry gives both the nav item and Home › AI. Placeholder pages live in `web/src/pages/Placeholders.tsx` (`ListeningSlot`, `Mainstream`) and use `PageHeader` + `ComingSoon`. The Playlist Generator's AI tab builds its own `ComingSoon` with issue 32 inline in `Playlists.tsx`. The nav already wraps (`flex-wrap: wrap`), and below 800 px it moves under the logo.

## Goals / Non-Goals

**Goals:**
- One more nav item and a placeholder page, following the existing placeholder pattern.
- One definition of the AI Coming soon text, so the tab and the page can't drift apart.

**Non-Goals:**
- Any AI functionality, API or model call (#32).
- Designing the AI feature itself. Figma already has the nav item: the Site header (Desktop and Tablet) and the Mobile menu have **AI** after Analyst, and a new **AI · Desktop** frame (`394:5234`, section "About, contact and not found") shows the Coming soon empty state with a "Follow the plan in issue #32" button. The new `icon/sparkles` marks AI in the Mobile menu and the empty state.

## Decisions

**Path `/ai`, label "AI".** This matches the owner's request and the existing tab label. *Alternative:* `/playlists?type=ai`, the existing tab. Rejected because the owner wants a top-level menu entry with its own page and highlight. A query on the Playlists page would highlight Playlist Generator instead.

**Shared card component.** Export `AiPlaylistComingSoon` from `Placeholders.tsx`, holding the current tab copy unchanged. The tab and the `Ai` page both render it. *Alternative:* copy the text. Rejected because the two copies would drift.

**Page title "AI".** `PageHeader title="AI"` with no intro line, like the About placeholder had. The card already explains the feature.

**No layout change for the nav.** At 1440 px the extra item still fits on one line. Below 800 px the nav already wraps. The spec scenario checks 390 px.

## Risks / Trade-offs

- [The nav grows to six items and could crowd mid-width screens of about 800–1000 px] → The nav already wraps, and task 2.3 measures it at 900 px.
- [The menu promises a feature that isn't built] → That's the owner's intent. The page says "Coming soon" and links to the issue.
