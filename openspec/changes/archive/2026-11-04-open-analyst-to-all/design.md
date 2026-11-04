## Context

Analyst is on the trusted tier only (`access.py`). On the hosted site `/api/sql` already refuses typed SQL for everyone and runs a pre-defined query only by name, and each run is counted as a heavy request (`_heavy`, spec 012). The schema map (`/api/schema`) is read-only on the hosted site: saving the layout is refused as any write is.

## Decisions

1. **Move `analyst` into `GUEST_PAGES`; change nothing else.** The guest and trusted lists already feed `API_ACCESS` (`/api/sql/meta`, `/api/sql`, `/api/schema` are unlocked by `analyst`), so no route or page code changes. *Alternative:* a new rule on the page: unneeded, the server already limits what runs.
2. **The limit stays per person.** A guest's pre-defined runs count toward the same 30 per minute and 1,000 per day as a trusted visitor's.

## Risks / Trade-offs

- More people can run the heavy pre-defined queries → the existing per-person limit applies; the Visitors report shows limit hits.
- Existing codes with `grant analyst` stay valid and gain nothing; no migration.

## Open Questions

None.
