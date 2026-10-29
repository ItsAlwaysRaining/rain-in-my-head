# Contract: login and access on the hosted API

Applies only when `LISTENING_HOSTED=1`. Locally none of this exists and `GET /api/me` answers `{"local": true}`.

## Cookie

`session=<id>.<signature>`; `HttpOnly`; `Secure` (on HTTPS and on `localhost`); `SameSite=Lax`; `Path=/`; max age 30 days.

## Endpoints

| Route | Auth | Request | Response |
|---|---|---|---|
| `GET /api/me` | none | | `200 {"logged_in": false}` or `200 {"logged_in": true, "name": "Sam", "tier": "guest", "pages": ["overview", …]}` |
| `POST /api/login` | none; `Origin` must match | `{"code": "xxxx-xxxx-xxxx-xxxx"}` | `200` plus `Set-Cookie` and the same body as `/api/me`; `401 {"error": "bad_code", "message": "That code didn't work."}`; `429 {"error": "slow_down", "message": "Too many tries. Wait a minute."}`; `423 {"error": "locked", "message": "Too many tries. Try again later."}` |
| `POST /api/login` while the visitor database is down | | | `503 {"error": "unavailable", "message": "The site can't check codes right now. Try again in a minute."}` |
| `POST /api/logout` | session; `Origin` must match | | `204` plus an expired cookie |
| `GET /api/health` | none | | `200 {"ok": true}` |
| every other `/api/*` route | session with an allowing page | as before | as before |

## Refusals on locked routes

| Case | Status | Body |
|---|---|---|
| No cookie, or a cookie that fails its signature, has expired or points at a revoked person | 403 | `{"error": "login_required", "message": "Log in with your invite code."}` |
| Logged in, but no allowing page | 403 | `{"error": "not_available", "message": "That page isn't available to you."}` |
| A route the hosted site never allows (playlists, AI, writes) | 403 | `{"error": "refused", "message": "This DJ doesn't take requests."}` (unchanged from phase 2) |
| Visitor database down while checking | 503 | `{"error": "unavailable", …}` |

A wrong, revoked or unknown code always gives the same `401 bad_code` (FR-010).

## Allowing pages per route

See the table in [research.md](research.md#r5-deny-by-default-and-which-page-unlocks-which-route). The same table is `API_ACCESS` in `access.py`, and the app refuses to start if a registered `/api` route is missing from it.

## What's logged

The person's name and the route. Never a code, a cookie value, a connection string or an address.
