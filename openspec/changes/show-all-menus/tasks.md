## 1. Hosted API and access

- [x] 1.1 In `access.py`, add `playlists` to `GUEST_PAGES` and list `GET /api/playlists/meta` and `POST /api/playlists/preview` in `API_ACCESS` with `{"playlists"}`
- [x] 1.2 In `api.py`, add the `HOSTED_PLAYLIST_READS` set and let `hosted_guard` pass those two routes; keep every other `/api/playlists*` route refused (including `create` and `spotify`)
- [x] 1.3 Update the comments on `REFUSED_PREFIXES` and `hosted_guard` to say what is allowed and why
- [x] 1.4 In `tests/test_hosted_smoke.py`, replace `test_playlists_are_refused_for_everyone` with tests: guest gets 200 on meta and preview; logged-out gets 403 `login_required`; trusted gets 403 `refused` on create and on spotify; an unlisted `/api/playlists/other` route is refused
- [x] 1.5 Run `uv run pytest tests/test_hosted_smoke.py` and confirm it passes

## 2. Top bar

- [ ] 2.1 In `web/src/routes.ts`, add `ownerOnly: true` to the Visitors section and add `lockReason`; remove `visibleSections`
- [ ] 2.2 In `App.tsx`, render every section; for a locked one add a lock icon, a locked style and visually hidden text with the reason
- [ ] 2.3 In `App.module.css`, add the locked style (muted, still readable at 4.5:1 against the top bar) and keep focus rings
- [ ] 2.4 Check `breadcrumbs()` and the `NotFound` text still read correctly with the full menu

## 3. Playlist page

- [ ] 3.1 In `Playlists.tsx`, on the hosted site (`!auth.local`) skip `fetchSpotifyStatus` and show the Create bar
- [ ] 3.2 Show the refusal message from Create in a neutral `Notice` and not the error tone; keep the red error for real failures
- [ ] 3.3 Confirm in `createPlaylist` (`api.ts`) that a 403 JSON body reaches the page as `ApiError.message`; fix there if not

## 4. Verify in the real app

- [ ] 4.1 Run the hosted build locally with guest, trusted and logged-out sessions: all seven sections appear for each, and the right ones are locked
- [ ] 4.2 Click Analyst as logged-out (login page) and as a guest ("Not available to you"), and confirm in the network tab that no data request was made
- [ ] 4.3 As a guest open Playlist Generator, change a setting, see the preview, click Create on Spotify, and see "This DJ doesn't take requests."; confirm no request reached Spotify
- [ ] 4.4 On the Mac build, create a playlist as before (or confirm the Create bar and Spotify status still show)
- [ ] 4.5 Check the top bar at 360 px wide and with keyboard only; confirm a screen reader reads "locked" and the reason
- [ ] 4.6 Cross-check one preview's rows against a direct SQLite query on `public.db` (constitution III)

## 5. Finish

- [ ] 5.1 Update `docs/` or README text that says playlists are not hosted, if any
- [ ] 5.2 Run `/opsx:archive`, then push and open the PR with `Closes #63`
