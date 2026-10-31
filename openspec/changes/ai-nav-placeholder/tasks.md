# Tasks

## 1. Shared placeholder and page

- [x] 1.1 In `web/src/pages/Placeholders.tsx`, add `AiPlaylistComingSoon` (the AI tab's current `ComingSoon` with issue 32 and its text, unchanged) and an `Ai` page (`PageHeader title="AI"` + `AiPlaylistComingSoon`). Make the Playlists AI tab render `AiPlaylistComingSoon`. Verify with `npm run typecheck`, and check that `/playlists?type=ai` still shows the same card with the #32 link

## 2. Nav and route

- [x] 2.1 Add `{ path: "/ai", label: "AI", pages: ["ai"] }` to `SECTIONS` in `web/src/routes.ts` after Analyst, add `"/ai": "ai"` to `PAGE_KEYS`, and add the `/ai` route in `App.tsx` inside `RequireAccess page="ai"`. Verify `npm run build` passes
- [x] 2.4 In `src/rain_in_my_head/access.py`, add `ai` to `PAGES` and `GUEST_PAGES`. Verify with Python that `pages_for("guest", set())` includes `ai`, and that `viewer grant` accepts `ai` as a page key
- [x] 2.2 Check at 1440 px: nav order is Dashboards, Playlist Generator, Analyst, AI, About, Contact Me; clicking AI opens `/ai` with AI highlighted (`aria-current="page"`); breadcrumbs read Home › AI; one `h1` "AI"; the card's link points to issue 32 with `target="_blank"`
- [x] 2.3 Check at 900 px and 390 px: every nav item is visible and `scrollWidth` equals the window width on `/ai`

## 3. Docs

- [x] 3.1 Add the `/ai` row to `specs/005-prototype-redesign/contracts/routes.md` (AI, Coming Soon #32, section AI, Home › AI), and update README's Coming soon list to say the AI playlist (#32) is in the top menu as well as the Playlist Generator. Also add `ai` to the page keys in `specs/011-viewer-access/contracts/cli.md` and to README's "What each tier opens" paragraph (guest tier, and the `grant` key list). Verify the files read correctly
