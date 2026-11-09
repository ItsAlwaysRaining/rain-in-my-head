# Design

## Context

Access is decided in two places. `access_guard` (src/rain_in_my_head/api.py) rejects `/api/` routes without a session. `RequireAccess` (web/src/auth.tsx) redirects logged-out visitors to the login page. `access.py` maps each route to the pages that unlock it, and `TIER_PAGES["guest"]` already lists the pages a guest may open. See proposal.md for the why.

## Goals / Non-Goals

**Goals:**
- An anonymous visitor gets the guest page set, using the same route rules a guest gets.
- The existing refusals (playlist creation, AI, typed SQL) apply unchanged.

**Non-Goals:**
- No change to invite codes for Visitors and Storm.
- No change to the six pre-defined queries.
- No change to the Spec Kit viewer-access spec.

## Decisions

- **Anonymous = the guest page set.** `access_guard` treats a request with no session as a session with `TIER_PAGES["guest"]`, rather than returning `login_required`. Alternative: a new public list of routes. Rejected: it would duplicate `API_ACCESS` and drift from it.
- **`/api/me` reports the guest pages for anonymous visitors**, with `logged_in: false`. The web then uses one rule: `can(page)` is true when the page is in the list, logged in or not.
- **Login redirect only when the page is closed to the visitor.** `RequireAccess` redirects to login only if the visitor is anonymous and the page is not in their list. Alternative: always redirect. Rejected: it would keep the dashboards behind login.
- **Usage events stay logged-in only.** `/api/events` is a session route, so anonymous page views are refused and nothing is stored. The client already tolerates a refused event; check this in apply.

## Risks / Trade-offs

- **Listening data is public to anyone with the link.** → Accepted by the owner (see proposal). Mitigation: no change to the Visitors page, invite codes, or the pre-defined queries.
- **Anonymous traffic uses the free Neon and Vercel limits.** → Mitigation: the existing per-route limits (`_heavy`) still apply to anonymous requests; check in apply that the limit is keyed on the route, not on the visitor.
- **Old notes say every page needs a code.** → Superseded by this change; update the threat-model note after merge.

## Migration Plan

Deploy as a normal `main` release. Rollback: revert the commit; the login gate returns.

## Open Questions

None that change the specs.
