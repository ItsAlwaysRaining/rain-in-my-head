# Proposal

## Why

The owner wants the listening dashboards on the hosted site to open without an invite code, so anyone with the link can see them. Today every page needs a login, which is why the new artist page looks old to people who haven't logged in. The restrictions that protect the site stay: playlists can't be created, AI is off, and the Analyst runs only the pre-defined queries.

## What Changes

- Visitors with no login get the guest page set: Overview, New artists, Genre, Artist, Slot, Mainstream, Playlist Generator (form and preview only), Analyst (pre-defined queries only), AI (coming-soon page), About and Contact.
- Visitors with no login are not sent to the login page for those pages. Visitors and Storm stay behind the login.
- Playlist creation keeps its error message ("This DJ doesn't take request") for everyone on the hosted site.
- The AI page keeps its error page for everyone on the hosted site.
- Page-view tracking is not recorded for anonymous visitors.

**BREAKING** for the threat model: listening data on the dashboards is visible to anyone with the link. Notes that said "every page needs a code" are superseded by this change.

## Capabilities

### New Capabilities

- `public-dashboards`: which hosted pages and data routes anonymous visitors may use.

### Modified Capabilities

None in openspec/specs. The invite-code rules live in the Spec Kit folder `specs/011-viewer-access/`, which is not changed here.

## Impact

- `src/rain_in_my_head/access.py`: anonymous visitors get the guest page set.
- `src/rain_in_my_head/api.py`: `access_guard` allows anonymous requests for the guest routes; `/api/me` reports the guest pages to anonymous visitors.
- `web/src/auth.tsx`: `RequireAccess` uses the page list for anonymous visitors too.
- Tests in `tests/`.
- No change to the database or the pre-defined queries (all six kept).
