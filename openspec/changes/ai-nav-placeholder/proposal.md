# Proposal

## Why

The AI playlist (#32) is the project's headline feature, but today it's only reachable as a "Coming soon" tab inside the Playlist Generator. The owner wants it visible in the top menu now, so visitors see it's planned and can follow the issue, before the feature itself is built.

## What Changes

- Add an **AI** item to the top nav, after **Analyst**: Dashboards · Playlist Generator · Analyst · **AI** · About · Contact Me.
- It opens a new page at `/ai` with the title **AI** and the standard **Coming soon** card for the AI playlist, linking to issue #32. Breadcrumbs read Home › AI.
- On the hosted site, the page has its own access key, `ai`, in the guest tier, so everyone with a code sees the nav item and the card. It loads no data. (Decided by the owner during apply, after viewer-access (spec 011) merged.)
- The Playlist Generator keeps its AI tab. Both places show the same Coming soon text, which is defined once.
- Update the routes contract (`specs/005-prototype-redesign/contracts/routes.md`) and the README's list of Coming soon pages.

**Track**: this adds a route, but only a Coming soon placeholder in the existing shell. No CLI command, data source, dependency or schema change is involved. The real AI feature (#32) goes on the Spec Kit track when it's built.

## Capabilities

### New Capabilities
- `ai-page`: the AI item in the top nav and the `/ai` page. For now that page is a Coming soon placeholder linking to #32.

### Modified Capabilities
<!-- None: no existing spec covers the top nav or the Playlist Generator tabs. -->

## Impact

- `web/src/routes.ts`: a new `SECTIONS` entry for `/ai`, and an `ai` page key.
- `web/src/App.tsx`: the `/ai` route, wrapped in `RequireAccess page="ai"`.
- `src/rain_in_my_head/access.py`: `ai` added to `PAGES` and `GUEST_PAGES`. No `API_ACCESS` entry, because the page loads no data.
- `web/src/pages/Placeholders.tsx`: an `Ai` page plus the shared AI Coming soon card. `web/src/pages/Playlists.tsx` uses the shared card for its AI tab.
- Docs: `specs/005-prototype-redesign/contracts/routes.md`, `specs/011-viewer-access/contracts/cli.md` (the page keys) and `README.md`.
- No API route, data or dependency changes.
