# Tasks

## 1. Shared placeholder and page

- [ ] 1.1 In `web/src/pages/Placeholders.tsx`, add `AiPlaylistComingSoon` (the AI tab's current `ComingSoon` with issue 32 and its text, unchanged) and an `Ai` page (`PageHeader title="AI"` + `AiPlaylistComingSoon`). Make the Playlists AI tab render `AiPlaylistComingSoon`. Verify with `npm run typecheck`, and check that `/playlists?type=ai` still shows the same card with the #32 link

## 2. Nav and route

- [ ] 2.1 Add `{ path: "/ai", label: "AI" }` to `SECTIONS` in `web/src/routes.ts` after Analyst, and add the `/ai` route in `App.tsx`. Verify `npm run build` passes
- [ ] 2.2 Check at 1440 px: nav order is Dashboards, Playlist Generator, Analyst, AI, About, Contact Me; clicking AI opens `/ai` with AI highlighted (`aria-current="page"`); breadcrumbs read Home › AI; one `h1` "AI"; the card's link points to issue 32 with `target="_blank"`
- [ ] 2.3 Check at 900 px and 390 px: every nav item is visible and `scrollWidth` equals the window width on `/ai`

## 3. Docs

- [ ] 3.1 Add the `/ai` row to `specs/005-prototype-redesign/contracts/routes.md` (AI, Coming Soon #32, section AI, Home › AI), and update README's Coming soon list to say the AI playlist (#32) is in the top menu as well as the Playlist Generator. Verify both files read correctly
