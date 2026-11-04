# Proposal

## Why

The top bar hides every page the signed-in person can't open, so a guest never learns that Analyst exists, and Playlist Generator is hidden from everyone on the hosted site. Visitors should see the whole site. Locked pages should look locked, and Playlist Generator should be open to everyone, with only the act of creating a playlist turned off. Closes #63.

## What Changes

- The top bar lists every section for every access level (logged out, guest, trusted, owner). A section the person can't open is marked locked, with the reason in text and not only colour.
- Clicking a locked section goes to its normal address. The page's existing guard sends a logged-out person to the login page, or shows "Not available to you". No data request is made.
- `playlists` joins the guest and trusted starting pages, so every logged-in tier can open Playlist Generator.
- The hosted API allows two read-only playlist routes: `GET /api/playlists/meta` and `POST /api/playlists/preview`. Create (`POST /api/playlists/create`) and `GET /api/playlists/spotify` stay refused, as does everything else under `/api/playlists`.
- On the hosted site, **Create on Spotify** is shown. Clicking it shows "This DJ doesn't take requests." as a friendly notice (not the red error). On the owner's Mac it works as it does now.
- **BREAKING (hosted rule):** the hosted-site rule from spec 009, "every `/api/playlists*` route is refused", now has two exceptions. The owner's Mac is unchanged.

## Capabilities

### New Capabilities
- `top-bar-menu`: which sections the top bar shows, how locked sections look and behave, and what a click does.
- `hosted-playlist-preview`: what the Playlist Generator does on the hosted site: open to every tier, read-only preview, create refused with a friendly notice.

### Modified Capabilities
<!-- None in openspec/specs/. The hosted guard and tiers were specified in Spec Kit specs 009 and 011; their text stays as history, and the new specs above record the changed rules. -->

## Impact

- `src/rain_in_my_head/access.py`: add `playlists` to `GUEST_PAGES`; add the two routes to `API_ACCESS`.
- `src/rain_in_my_head/api.py`: `hosted_guard` allows the two read-only playlist routes; the rest of `REFUSED_PREFIXES` stays.
- `web/src/routes.ts`, `web/src/App.tsx`, `web/src/App.module.css`: show all sections, locked styling and a lock icon.
- `web/src/pages/Playlists.tsx`: on the hosted site skip the Spotify status check and show the notice when Create is clicked.
- `tests/test_hosted_smoke.py`: replace "playlists are refused for everyone" with the new rules.
- Threat model: the hosted site still has no way to write, reach Spotify or use AI. The preview only reads the two-year `public.db`.
