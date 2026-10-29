# Implementation Plan: Invite codes and locked pages

**Branch**: `feature/viewer-access` | **Date**: 2026-10-29 | **Spec**: [spec.md](spec.md)

## Summary

This phase adds a front door to the hosted site, in five parts:

- **`viewers.py`** (new): everything about people, codes and sessions. It makes and checks codes, signs and checks the cookie, and holds the login rate limit.
- **`neon.py`** (new): a small client for Neon's SQL-over-HTTPS endpoint, built on `httpx` (already a dependency). It runs one query or one transaction.
- **`access.py`** (new): the list of pages, what each tier opens by default, and which page unlocks each API route. Any route missing from the list is refused.
- **API changes**: `GET /api/me`, `POST /api/login` and `POST /api/logout`, plus one guard (`access_guard`) that checks every other `/api/*` request when the site is hosted.
- **`viewer` commands** (new, in `cli.py`): `init`, `add`, `list`, `revoke` and `grant`. They run only on the owner's Mac and talk to Neon directly with the owner role.
- **TypeScript app**: a login page, a "not available to you" page, a Log out control, and a navigation that shows only the pages the visitor can open.

Local mode (`LISTENING_HOSTED` not set) is untouched: no login, no checks.

## Technical Context

**Language/Version**: Python 3.10+ (uv); TypeScript (Vite + React) in `web/`

**Primary Dependencies**: no new ones. `httpx` (core), and the standard library: `hashlib`, `hmac`, `secrets`, `argparse`. FastAPI and React Router already exist.

**Storage**: Neon Postgres, the visitor database from phase 3 (`dev` and `prod` branches, separate). Four tables, no listening data. See [data-model.md](data-model.md).

**Testing**: no suite. [quickstart.md](quickstart.md) covers `curl` checks against the hosted guard, direct SQL cross-checks on the dev branch, and a headless-Chrome click-through (constitution III).

**Target Platform**: macOS locally (the commands, and a local run in hosted mode). Vercel's Python runtime for the API from phase 6.

**Project Type**: CLI, JSON API and web app

**Performance Goals**:
- A login under 1.5 s, including the first query after Neon wakes from sleep.
- At most one Neon query per API request, and none for requests seen in the last 3 seconds (see R6).

**Constraints**:
- Free plans only. Active CPU on Vercel is the tight limit, so waiting on Neon must be the only extra cost per request.
- No raw IP address and no code is ever stored or logged.
- The hosted app role gets the fewest privileges that work (R2).

**Scale/Scope**: about 10 people, one owner. Python: 3 new modules, plus `config`, `api` and `cli` changed. TypeScript: about 6 files. Infra: 2 new outputs, no new resources.

## Constitution Check

| Principle | Check | Result |
|---|---|---|
| I. Source of truth | No listening data is read or written differently. Visitor records live in Neon only. | ✅ |
| II. Spec first | Spec 011 is approved. It is amended once during planning (see Complexity Tracking) before any code. | ✅ |
| III. Real app | Headless Chrome on a local hosted-mode run against the Neon `dev` branch, plus direct SQL checks of what's stored. | ✅ |
| IV. Few dependencies | None added. `httpx` already exists, and Neon's HTTPS endpoint avoids a Postgres driver. | ✅ |
| V. APIs and secrets | The Neon connection strings and the signing secret come from the environment (Vercel env vars, and the owner's `.env`). No code or secret is logged. The two new infra outputs are marked sensitive. | ✅ |
| VI. Consistent dashboards | **TypeScript only.** Streamlit is never hosted, so it gets no login. Noted in `docs/streamlit-vs-typescript.md`. | ✅ (noted) |
| VII. Visitors' access | Deny by default, with a startup check that every route is listed. Codes are hashed. Revoke ends sessions. Raw IPs aren't stored. Visitor data is in Neon, never in `public.db`. | ✅ |

**Re-check after design**: unchanged. The hashing choice differs from the security options page and is justified in R3. No principle is affected.

## Project Structure

### Documentation (this feature)

```text
specs/011-viewer-access/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── cli.md
│   └── api.md
├── checklists/requirements.md
└── tasks.md          # /speckit-tasks
```

### Source Code (repository root)

```text
src/rain_in_my_head/
├── config.py        # + DATABASE_URL, SESSION_SECRET, the owner/app URLs for the commands
├── neon.py          # NEW: query(sql, params), transaction(queries) over HTTPS
├── access.py        # NEW: PAGES, TIER_PAGES, API_ACCESS (route -> pages), public routes
├── viewers.py       # NEW: new_code, hash_code, sign/verify cookie, login, session lookup, rate limit, admin operations
├── api.py           # + /api/me, /api/login, /api/logout, access_guard middleware, minimal /api/health when hosted
├── cli.py           # + `viewer` command group
└── viewer_schema.sql # NEW: tables, indexes and the app role's grants (run by `viewer init`)

web/src/
├── auth.tsx         # NEW: AuthProvider, useAuth(), RequireAccess
├── pages/Login.tsx  # NEW (+ Login.module.css)
├── pages/NotAvailable.tsx  # NEW
├── routes.ts        # + a page key for each path; SECTIONS filtered by access
├── App.tsx          # nav filtered, routes wrapped, Log out
└── api.ts           # + fetchMe, login, logout; ApiError kind "locked"

infra/outputs.tf     # + dev_app_url, prod_app_url (sensitive)
docs/streamlit-vs-typescript.md   # + note: login is TypeScript only
README.md            # + "Visitors and invite codes"
.env.example         # + the four VIEWERS_* names (names only)
```

**Structure Decision**: this follows the existing layout: shared logic in `src/rain_in_my_head/`, one module per concern, pages as modules in `web/src/pages/`. Data work for visitors lives in `viewers.py`, not in `api.py`, so the commands and the API share one implementation (constitution VI's spirit).

## Complexity Tracking

| Item | Why | Simpler alternative rejected because |
|---|---|---|
| **Spec amended**: pages that load no data (About, Contact, Storm, coming-soon pages) are hidden or shown by the browser app, not by the server | The site's files are served as static files from Vercel's CDN. Making the Python function serve every page would spend the 4-hour CPU limit on file downloads. | A server check on static files would need Vercel middleware (Node) or routing all files through Python. Every API route, which is everything that returns data, is checked by the server. |
| Code hash is SHA-256, not the `scrypt` the security options page suggests | Codes have at least 80 bits of randomness, so a slow hash adds nothing, and an indexed lookup needs a hash with no per-person salt. | Per-person scrypt means checking every person on each login, which costs about 50 ms of CPU each. |
