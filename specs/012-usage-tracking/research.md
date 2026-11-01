# Research: Usage tracking and a fair-use limit

Each entry is a decision the plan relies on. Nothing here was marked "needs clarification" in the plan; these are the choices the spec left open.

## R1. One table for every record, and the limit counted from it

**Decision**: a single table, `usage_events`, holds every record: a page view (`view`), time on page (`time`), a feature use (`feature`) and a limit hit (`limit`). The limit is counted from the `feature` rows.

**Rationale**: the spec's feature uses are exactly the heavy requests (a pre-defined query, a genre song list). So "record this feature use" and "count this person's heavy requests" are the same rows. One statement can check the limit and record the use together:

```sql
insert into usage_events (viewer_id, kind, page, feature, detail)
select $1::bigint, 'feature', $2, $3, $4
where (select count(*) from usage_events where viewer_id = $1::bigint and kind = 'feature'
         and at > now() - interval '1 minute') < $5::int
  and (select count(*) from usage_events where viewer_id = $1::bigint and kind = 'feature'
         and at >= date_trunc('day', now() at time zone 'utc') at time zone 'utc') < $6::int
returning id
```

If a row comes back, the request is allowed and already recorded. If none comes back, the limit was reached. A refused request leaves no row, so it can't use up the day's allowance (FR-011).

**Alternatives considered**:
- A counter table with an upsert per window. Needs a second write, and a counter bumped before the check lets refused requests burn the daily allowance.
- Counting in the app's memory. The site's servers keep nothing between requests, so each server would count separately.

**Known limits**: two requests at the same instant can both pass when the person is one below the limit. The overshoot is at most a few requests, which is fine for protecting a monthly CPU quota. A feature use that is not a heavy route would also count, so every future feature record must be a heavy route (noted in the code comment).

## R2. Windows and the wait time

**Decision**: a rolling minute and a UTC day, both counted from `at`. The limits are `HEAVY_PER_MINUTE = 30` and `HEAVY_PER_DAY = 1000`, defined once in `usage.py` (FR-014). When a request is refused, one more transaction works out the wait and records the limit hit:
- Day limit reached: the wait is the time to the next UTC midnight, and the message says the day's limit is reached.
- Otherwise: the wait is when the oldest of the last 30 uses leaves the minute: `at + 1 minute − now`, rounded up.

A `limit` row is written only if the person has none in the last minute, so a burst of refusals is one hit (spec Story 3, scenario 6).

**Rationale**: a rolling window has no boundary burst, and it needs no reset job. The refusal path runs rarely, so a second query costs nothing that matters.

**Alternatives considered**: fixed per-minute buckets (allow twice the limit across a boundary, and need cleanup); a token bucket (more state, no benefit at ten people).

## R3. Page views and time come from the browser

**Decision**: a hook in the app sends two small reports per page visit to `POST /api/events`:
- **open** when a page is shown: `{event: "open", visit, page}`. Stored as a `view`.
- **leave** when the visitor goes to another page, hides the tab, or closes it: `{event: "leave", visit, page, seconds}`. Stored as a `time`, sent with `navigator.sendBeacon` so it survives closing the tab.

`visit` is a random id the browser makes for each page visit, so the two rows belong together. Seconds count only while the tab is visible and the person has moved, typed or scrolled in the last 60 seconds. The server caps a visit at 1,800 seconds (30 minutes) and ignores a report with a page key the person can't open.

A second open for the same page within 5 seconds is dropped, so a reload doesn't double count (spec edge case).

**Rationale**: most pages are static files served from Vercel's CDN, so the server never sees a page view. Only the browser knows. Two reports per visit is the smallest set that records both a view and a time without a heartbeat (which would spend CPU for as long as a tab is open).

**Alternatives considered**: a heartbeat every 30 seconds (accurate, but many more function calls); recording views on the server from the data routes (misses About, Contact and every page that loads no data); one report on leave only (loses a view when the tab dies before it sends).

**Known limits**: time is an estimate, and a tab killed by the phone's operating system loses its time report. The report says so (spec assumption).

## R4. Reports are a logged-in-only route, with their own cap

**Decision**: `POST /api/events` is allowed for any logged-in person with at least one page. It is listed in a new `SESSION_ROUTES` set in `access.py`, which `check_routes()` also reads, so the deny-by-default startup check still covers every route. The route is capped at 120 reports a minute per person (FR-030), counted from `view` and `time` rows. Over the cap, it returns 204 and stores nothing. The route is also added to the hosted guard's list of allowed POSTs.

**Rationale**: it is the only new route that a valid code can call freely, so it needs a cap. Returning 204 means a script can't tell it was dropped, and a real visitor never reaches 120 (about two per second).

**Alternatives considered**: no cap (a flood costs CPU and fills the free database); a 429 (visitors see an error for something they didn't do).

## R5. Where the limit is applied

**Decision**: inside the two heavy handlers (`sql` and `genre_songs`), after their other refusals, using the session that `access_guard` already looked up. The guard keeps it on `request.state.session`, so there is no second lookup.

**Rationale**: the hosted rules for `/api/sql` refuse typed SQL and unknown names inside the handler. If the limit ran earlier (as a dependency or in the middleware), a refused request would count (FR-011). The 403 for the wrong tier happens in the middleware, before either.

**Alternatives considered**: a FastAPI dependency (runs before the handler's own refusals); the middleware (can't see the request body without reading it twice).

**Failure rule**: if the visitor database can't be reached, the check raises `NeonUnavailable` and the route answers 503 "try again in a minute", the same message the locked pages already use (FR-013).

**Response**: 429 with a `Retry-After` header and `{"error": "rate_limited", "message": ..., "retry_after": N}`. The error code differs from the login's `slow_down` so the app can tell them apart.

## R6. One shared module for the report

**Decision**: `usage.py` builds the report as plain data (per person, per range, plus a detail list and the free-plan figures). `GET /api/visitors` and `viewer usage` both call it. The Visitors page shows the API's data, and the command prints the same data as a table.

**Rationale**: constitution VI wants the same numbers in every place; the cheapest way to guarantee it is to have one function.

**Local only**: `GET /api/visitors` reads the owner connection string from `.env`, which the hosted site doesn't have. It is also added to `REFUSED_PREFIXES`, so the hosted guard refuses it for everyone, and `check_routes()` needs no access entry for it (FR-019). `visitors` is not in `access.PAGES`, so `viewer grant --page visitors` is refused as an unknown page.

## R7. The free-plan section

**Decision**: the report shows, for the current UTC month:
- recorded requests (page views, feature uses and limit hits) and time on the two heavy pages, from `usage_events`;
- the visitor database's size from `pg_database_size(current_database())`, against the free plan's storage limit.

The free-plan limits are constants in `usage.py` (`FREE_LIMITS`), each with a comment giving where the number came from. A note on the page says that Vercel's processing time appears only on Vercel's own dashboard.

**Rationale**: the site can measure its own requests and its database size. It can't read Vercel's CPU use, so it doesn't pretend to (the owner asked for this, 2026-10-29).

**Open check for implementation**: confirm the current Neon free-plan storage figure and the Vercel Hobby limits on their pricing pages before writing the constants. The plan doesn't hard-code a number so a stale one can't be wrong in the spec.

**Alternatives considered**: reading Vercel's usage through its API (needs another token and a paid-looking scope; rejected for the free-plan rule and secrets).

## R8. Retention

**Decision**: `viewer prune` deletes `usage_events` rows older than 12 months and prints how many. The nightly workflow runs it before the export. It deletes nothing else: not people, sessions or login attempts (FR-021).

**Rationale**: a scheduled job is already needed for the export, so it carries the clean-up. The hosted site's role has no DELETE on `usage_events`, so a stolen site password can't wipe the history.

**Alternatives considered**: deleting from the hosted site on some requests (spends visitor CPU, and needs DELETE for the site role).

## R9. The nightly export

**Decision**: `viewer export DIR --env prod` writes two CSV files into `DIR`:
- `usage_events.csv`: all rows, every column except the database id.
- `viewers.csv`: name, tier, status, created, revoked, last login, and granted pages. No code hash, no session.

The workflow (`analytics.yml`, nightly, plus a manual run) does the following:
1. Runs `viewer prune --env prod`, then `viewer export` into a temporary folder.
2. Fetches the `analytics` branch if it exists, and compares the two CSV files with it.
3. If they're identical, stops. No commit.
4. Otherwise makes one new orphan commit holding only those two files, and pushes it to `analytics` with `--force`. The previous commit, and so every earlier copy, leaves the branch.

The workflow uses `permissions: contents: write` and the existing `NEON_PROD_OWNER_URL` secret, passed to the command as `VIEWERS_OWNER_URL_PROD`. A manual run can choose `dev`, which uses the existing `NEON_DEV_OWNER_URL` secret and a branch called `analytics-dev`, so the export can be tried without touching prod's copy.

**Rationale**: it meets the owner's decision (latest copy only, never on `main`) with the secrets and tools already in place. The sort order of rows is fixed, so an unchanged database gives byte-identical files and no commit.

**Known limits**: GitHub keeps unreachable commits for a while, so an old copy can remain fetchable by its hash for some time after the branch moves on. This is GitHub's housekeeping, and the repository is private. The login page states 12 months as the database's rule, and the README notes this one detail.

**Alternatives considered**: appending commits (rejected by the owner); a monthly rewrite (more parts); a different store such as a release asset (a new thing to secure and an extra token).

## R10. The tracking notice

**Decision**: the login page's notice becomes: "This site records which pages you open, which features you use, and how long you stay, against your name. Records are kept for 12 months, then deleted. Raw IP addresses are never stored."

**Rationale**: this is the wording the constitution (VII) asks for, in the plain style of the phase 4 notice.

## R11. Streamlit

**Decision**: no Streamlit change. Streamlit is never hosted and the Visitors page is a TypeScript page that reads the API. The difference is noted in `docs/streamlit-vs-typescript.md` (constitution VI).

## R12. Setting up the databases

**Decision**: the new table and its grants are added to `viewer_schema.sql`, which every `viewer init` runs. After this branch merges, the owner runs `viewer init` once on dev and once on prod. It is safe to run twice, and until it runs on prod the new routes would fail their queries. That step goes on the to-do page.

**Rationale**: it is the same setup path as phase 4, so there is nothing new to learn or secure.
