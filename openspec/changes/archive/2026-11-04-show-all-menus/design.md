## Context

- The top bar reads `SECTIONS` in `web/src/routes.ts` and filters it with `visibleSections(auth.can)` (`App.tsx`). Every route is already wrapped in `RequireAccess`, which redirects a logged-out visitor to `/login` and shows `NotAvailable` to a logged-in visitor without the page. Neither makes a data request.
- Tiers live in `access.py` (`GUEST_PAGES`, `TIER_PAGES`). `playlists` and `visitors` are on no tier, so only the Mac (where `auth.can` is always true) opens them.
- `hosted_guard` in `api.py` is deny-by-default: GET is allowed unless the path starts with `REFUSED_PREFIXES` (`/api/playlists`, `/api/ai`, `/api/visitors`); POST only for `/api/sql`, `login`, `logout`, `events`. `access_guard` then needs a login whose pages allow the route (`API_ACCESS`; an unlisted route is refused, and `api.check_routes` stops the app starting if a data route is missing).
- `Playlists.tsx` calls `fetchSpotifyStatus` (`GET /api/playlists/spotify`) before showing the Create bar, so on the hosted site it would show an error today.

## Goals / Non-Goals

**Goals:**
- Full menu for everyone, locked items clearly marked.
- Playlist Generator usable (form and preview) for every tier on the hosted site.
- Create stays impossible on the hosted site, with a friendly message.

**Non-Goals:**
- No change to who may open Analyst, Visitors, Storm or AI.
- No new tier, no owner tier on the hosted site.
- No Spotify access, writes or AI on the hosted site.
- No change to the Streamlit dashboard.

## Decisions

1. **Locked items stay links; the existing page guard handles the click.** A click on a locked section opens its address, and `RequireAccess` shows login or "Not available to you". No new click handler, and keyboard and screen-reader behaviour stay native. *Alternative:* a disabled button or `aria-disabled` link: it gives no explanation and hides the login path for logged-out visitors. Issue #63 asked for "no data request" and not "no navigation", and this meets that.
2. **Lock reason is a small function next to `SECTIONS`.** `lockReason(section, auth)` returns `null` when open, else "Log in to open" (logged out), "Owner only" (a new `ownerOnly: true` flag on Visitors), or "Not in your invite code". The label text is visually hidden and read by screen readers; a lock icon and muted style are the visual cue.
3. **`visibleSections` is replaced, not kept.** It would have no caller. The comment that "hiding the rest is a convenience" moves to the lock logic: the server still checks every request.
4. **Allow two playlist routes by name, keep the prefix refused.** `hosted_guard` gets a small `HOSTED_PLAYLIST_READS` set: `("GET", "/api/playlists/meta")` and `("POST", "/api/playlists/preview")`. The rule becomes "refuse `/api/playlists*` unless the method and path are in that set". Anything new under `/api/playlists` is refused until it is listed, which keeps deny-by-default. *Alternative:* shrink `REFUSED_PREFIXES` to `/api/playlists/create` and `/spotify`: a new route would then be open by default.
5. **Grant the page through the tiers.** Add `playlists` to `GUEST_PAGES` (trusted inherits it) and list the two routes in `API_ACCESS` with `{"playlists"}`. A person with no `playlists` page is refused like on any other route.
6. **Hosted Create is refused by the server and explained by the page.** The Create bar renders on the hosted site without calling `/api/playlists/spotify`. The click sends the real create request; `hosted_guard` answers 403 `refused`, and the page shows `ApiError.message` ("This DJ doesn't take requests.") in a `Notice` of the neutral kind. The server stays the only guard; the page never decides. The web app learns it is hosted from `auth.local` (false on the hosted site).
7. **Preview is not counted as a heavy request.** The preview fires after a 250 ms debounce on every slider change, and 30 per minute would trip while dragging. It only reads `public.db`, and the binge search is cached per setting. Tracking from spec 012 already records page views. *Revisit:* if the Visitors report shows abuse, count it then.

## Risks / Trade-offs

- **Hosted guard is a security rule** → add tests for the exact routes allowed and refused, including an unlisted `/api/playlists/…` route (Decision 4), and a trusted visitor calling create.
- **Create streams server-sent events** → check in a real browser that a 403 JSON body is shown as the message and not as a stream error (`createPlaylist` in `api.ts`); fix there if not.
- **Preview cost on a free plan** → uncached slot and discovery previews take about 1 s each (docs/streamlit-vs-typescript.md). Accepted for now (Decision 7).
- **Longer menu on small screens** → the nav already wraps; checked at 360 px.
- **Hosting threat model** → the menu now names Analyst and Visitors to guests. Names only: the pages and data stay behind the server checks.

## Migration Plan

No data or schema change. Deploy through the normal PR and preview deploy. Roll back by reverting the PR. Existing invite codes need no change: guest and trusted gain `playlists` through the tier, and a code with explicit grants is unaffected.

## Open Questions

None. Rate-limiting the preview is deferred on purpose (Decision 7).
