# Contract: API changes

Extends the API from [phase 4](../../011-viewer-access/contracts/api.md). Everything below applies to the hosted site unless it says otherwise. On the owner's Mac (`LISTENING_HOSTED` not set) there is no login, nothing is recorded and no limit applies, except `GET /api/visitors`, which works only there.

## `POST /api/events` (new)

The browser's page-view and time-on-page reports. Any logged-in person may call it. Not available to someone with no session (403 `login_required`, as for every data route).

**Request** (JSON; sent with `fetch` for `open`, with `navigator.sendBeacon` for `leave`):

```json
{ "event": "open", "visit": "k3j9x2m1q8", "page": "genre" }
{ "event": "leave", "visit": "k3j9x2m1q8", "page": "genre", "seconds": 74 }
```

| Field | Rule |
|---|---|
| `event` | `open` or `leave` |
| `visit` | 8 to 32 letters and digits |
| `page` | a page key the person can open. Any other value is ignored. |
| `seconds` | `leave` only; whole number, clamped to 0 to 1800 |

**Responses**:
- `204` for every well-formed report, whether it was stored, deduplicated, over the cap, or dropped because the database was unreachable. The browser never shows a failure.
- `403` `login_required`, as for any data route, if there is no session.
- `422` for a body that doesn't match the table above.

Same-origin only: a report with an `Origin` header from another site is refused (`403`, "This DJ doesn't take requests."), like login and logout.

**Cap**: more than 120 stored reports a minute for one person are dropped with a `204` (FR-030).

**Effect**: `open` writes a `view` row (unless the same person opened the same page less than 5 seconds ago). `leave` writes a `time` row.

## Heavy routes (changed)

`POST /api/sql` (a pre-defined query by name) and `GET /api/genre/songs` now check the person's limit **after** every other rule. A request refused for the tier, or because it is typed SQL, never reaches the check and leaves no row.

**Limited response** (`429`, with a `Retry-After` header in seconds):

```json
{ "error": "rate_limited", "message": "You're going a bit fast. Try again in 12 seconds.", "retry_after": 12 }
```

For the daily limit the message is "You've reached today's limit. It resets at midnight UTC." and `retry_after` is the seconds until then.

**Database unreachable**: `503`, `{"error": "unavailable", "message": "The site can't check codes right now. Try again in a minute."}`, the same as the locked pages (FR-013).

**Success**: unchanged, and one `feature` row is stored in the same query that did the check.

## `GET /api/visitors` (new, owner's Mac only)

The data for the Visitors page. On the hosted site it is refused for everyone with `403` "This DJ doesn't take requests.", because `/api/visitors` is in `REFUSED_PREFIXES`.

**Query**: `env` (`prod` or `dev`, default `prod`), `range` (`7d`, `30d` or `12m`, default `30d`), `person` (optional, a name, returns that person's detail).

**Response**:

```json
{
  "env": "prod",
  "range": "30d",
  "generated_at": "2026-11-01T20:00:00Z",
  "people": [
    {
      "name": "Sam", "tier": "guest", "status": "active",
      "last_login_at": "2026-10-30T18:02:11Z",
      "visits": 14, "seconds": 2310,
      "pages": [{ "page": "genre", "views": 9, "seconds": 1500 }],
      "features": [{ "feature": "genre-songs", "detail": null, "uses": 21 }],
      "limit_hits": 0
    }
  ],
  "person": null,
  "free_plan": {
    "month": "2026-11",
    "requests": 412,
    "requests_limit": 1000000,
    "heavy_page_seconds": 5200,
    "database_bytes": 9120000,
    "database_limit_bytes": 1073741824,
    "notes": ["Vercel's processing time is shown only on Vercel's own dashboard."]
  }
}
```

`requests_limit` and `database_limit_bytes` come from the `FREE_LIMITS` constants in `usage.py` (research R7). `person` holds, when asked for, `{ "name": ..., "events": [ { "kind", "page", "feature", "detail", "seconds", "at" } ] }`, newest first, the latest 200. No field anywhere holds an address, a code or a hash.

**Errors**: `503` `{"error": "not_configured", "message": "Set VIEWERS_OWNER_URL_PROD in .env (see .env.example)."}` if the owner connection is missing (names the variable, never a value). `503` `unavailable` if the database can't be reached. `422` for an unknown `env`, `range` or name.

## Access rules

- `access.py` gains `SESSION_ROUTES`: routes that any logged-in person with at least one page may call. `POST /api/events` is the only one.
- `check_routes()` also reads `SESSION_ROUTES`, so a route missing from every list still stops the app from starting (constitution VII).
- `hosted_guard` allows `POST /api/events` and keeps refusing `/api/visitors`.
- `visitors` is not in `access.PAGES`. No tier and no grant opens it, and `viewer grant --page visitors` is refused as an unknown page.
- `access_guard` keeps the session on `request.state.session`, so the heavy routes and `/api/events` don't look it up again.

## Unchanged

`/api/me`, `/api/login`, `/api/logout`, `/api/health` and every dashboard route behave as in phase 4. `/api/me` does not report usage.
