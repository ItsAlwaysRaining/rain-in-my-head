# Implementation Plan: Usage tracking and a fair-use limit

> **Superseded in part (2026-11-04):** the nightly export to the `analytics` branch was removed so the repository can be public (see `openspec/changes/make-repo-public`, or `openspec/specs/usage-retention` once archived). Visitor data now stays only in the visitor database. The nightly job only deletes records older than 12 months (`.github/workflows/prune.yml`). Anything below about the `analytics` branch, `analytics.yml` or the private copy is history.

**Branch**: `feature/usage-tracking` | **Date**: 2026-11-01 | **Spec**: [spec.md](spec.md)

## Summary

This phase adds usage records, a per-person limit and an owner-only report to the hosted site, in six parts:

- **`usage.py`** (new): everything about usage records. It records page views and time on page, records a heavy request and checks the limit in one query, builds the owner's report, prunes old records and writes the export files. The API and the commands share it, so they always show the same numbers.
- **One new table, `usage_events`**, in the visitor database. Every kind of record (page view, time on page, feature use, limit hit) is a row in it. The per-person limit is counted from the same rows, so there is no separate counter to keep in step (R1, R2).
- **API changes**: `POST /api/events` (the browser's page-view and time-on-page reports), a limit check in the two heavy routes, and `GET /api/visitors` for the owner's Mac. On the hosted site `/api/visitors` is refused for everyone.
- **TypeScript app**: a small tracking hook, a Visitors page that shows only on the owner's Mac, a calm message when the limit is hit, and the longer notice on the login page.
- **`viewer` commands** (extended): `usage` (the report), `prune` (delete records older than 12 months) and `export` (write the files for the `analytics` branch).
- **A nightly workflow** (`analytics.yml`, new): prunes, exports, and replaces the private `analytics` branch with one fresh commit when the copy changed.

Local mode (`LISTENING_HOSTED` not set) stays untouched: no tracking, no limit.

## Technical Context

**Language/Version**: Python 3.10+ (uv); TypeScript (Vite + React) in `web/`

**Primary Dependencies**: no new ones. `httpx` through the existing `neon.py`, and the standard library (`csv`, `datetime`). FastAPI, React, React Router and TanStack Query already exist.

**Storage**: Neon Postgres, the visitor database (separate `dev` and `prod` branches). One new table. No listening data. See [data-model.md](data-model.md).

**Testing**: no suite, as in earlier phases. [quickstart.md](quickstart.md) covers `curl` checks of the limit, direct cross-checks of what is stored, a headless-Chrome click-through (constitution III), and a local dry run of the export.

**Target Platform**: macOS locally (the commands, the Visitors page, and a local run in hosted mode). Vercel's Python runtime for the API from phase 6. GitHub Actions for the nightly job.

**Project Type**: CLI, JSON API and web app

**Performance Goals**:
- Recording adds no wait to a page: the browser sends reports in the background, and a failed report is dropped.
- A heavy request costs one extra Neon query (the check and the record together), and the session lookup is already cached for 3 seconds.
- The Visitors page answers in under 3 seconds for ten people and a year of records.

**Constraints**:
- Free plans only. Active CPU on Vercel is the tight limit, so each report is one short request, and nothing polls.
- No raw IP address, code or code hash is stored, logged or exported.
- The hosted app role gets the fewest privileges that work (R2).
- The hosted site must keep working when the visitor database is slow or down (recording is dropped), and must fail closed for heavy requests.

**Scale/Scope**: about 10 people, one owner. Python: 1 new module, plus `api`, `access`, `viewers`, `cli` changed and the schema file extended. TypeScript: about 6 files. One new workflow. No infra changes.

## Constitution Check

| Principle | Check | Result |
|---|---|---|
| I. Source of truth | No listening data is read or written differently. Usage records live in Neon only. | ✅ |
| II. Spec first | Spec 012 is approved. It was amended once during planning (FR-030 and the app role's read access; see Complexity Tracking) before any code. | ✅ |
| III. Real app | Headless Chrome on a local hosted-mode run against the Neon `dev` branch, direct cross-checks of what is stored, and a hand run of the export. | ✅ |
| IV. Few dependencies | None added. Neon's HTTPS client and the standard library do all of it. The workflow uses `uv run --no-default-groups`, like the sync. | ✅ |
| V. APIs and secrets | The export uses a secret that already exists (`NEON_PROD_OWNER_URL`). No new secret, no third-party API, nothing logged. | ✅ |
| VI. Consistent dashboards | **TypeScript only.** Streamlit is never hosted and gets no Visitors page. Noted in `docs/streamlit-vs-typescript.md`. The report's numbers come from one shared module, used by the API and the command. | ✅ (noted) |
| VII. Visitors' access and privacy | Deny by default stays: the new route is listed, `/api/visitors` is refused when hosted, and the startup check covers both. The login page says what is tracked. No raw IPs. Records older than 12 months are deleted, and the export keeps only the latest copy. Records live in Neon, never in `public.db`. Free plans only. | ✅ |
| Development workflow, item 5 (never force-push) | The nightly job replaces the `analytics` branch, which is a force-update. | ⚠️ justified below |

**Re-check after design**: unchanged. The only deviation is the force-update, justified in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/012-usage-tracking/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── api.md
│   └── cli.md
├── checklists/requirements.md
└── tasks.md          # /speckit-tasks
```

### Source Code (repository root)

```text
src/rain_in_my_head/
├── usage.py          # NEW: record_event, heavy_request (limit + record), report, free_plan, prune, export_files
├── viewer_schema.sql # + usage_events table, two indexes, the app role's grants
├── viewers.py        # TABLES gains "usage_events" (init reports 5 tables)
├── access.py         # + SESSION_ROUTES (routes any logged-in person may call)
├── api.py            # + POST /api/events, GET /api/visitors, the limit in sql and genre_songs, session kept on the request
└── cli.py            # + viewer usage, prune, export

web/src/
├── usage.ts          # NEW: useTracking() hook (open and leave reports, active-time count)
├── api.ts            # + sendEvent, fetchVisitors, ApiError kind "limited"
├── routes.ts         # + "visitors" page key and nav item
├── App.tsx           # + useTracking(), the Visitors route
├── pages/Visitors.tsx (+ .module.css)   # NEW: owner's report (Mac only)
└── pages/Login.tsx   # the longer tracking notice

.github/workflows/analytics.yml   # NEW: nightly prune + export + replace the analytics branch
docs/streamlit-vs-typescript.md   # + note: Visitors page is TypeScript only
README.md                         # + "Usage and limits"
CLAUDE.md                         # + one line: the analytics workflow may replace the analytics branch
```

**Structure Decision**: this follows the layout phase 4 set: shared logic in `src/rain_in_my_head/`, one module per concern, pages as modules in `web/src/pages/`. All usage logic lives in `usage.py`, not in `api.py`, so the report, the commands and the workflow share one implementation (constitution VI's spirit).

## Complexity Tracking

| Item | Why | Simpler alternative rejected because |
|---|---|---|
| **Force-update of the `analytics` branch** by the nightly workflow (deviates from "never force-push", Development Workflow item 5 and `CLAUDE.md`) | The owner chose "latest copy only" (2026-11-01) so deleted records don't live on in git history, keeping the 12-month promise. A branch holding one fresh commit each time can only be updated by replacement. | Normal commits keep every old copy forever (rejected by the owner). A monthly history rewrite is also a force-update, with more parts. Scope of the exception: only the scheduled workflow, only the `analytics` branch. `main` and feature branches stay off-limits, and no Claude session force-pushes anything. `CLAUDE.md` gets one line saying so. |
| **Spec amended twice during planning** | FR-030 (a cap on browser reports) because each report is a function call that spends the free CPU, exactly like a heavy route. The assumption about the app role changed because the limit check has to read back a few columns to count. | Leaving reports uncapped lets one valid code flood the database and the CPU quota. Counting in the app instead of the database would need state that the site's servers don't keep between requests. |
| **The limit counts rows in `usage_events`** instead of a separate counter table | One query both checks and records, and refused requests leave no trace, so they can't use up the day's allowance (FR-011). | A counter table needs a second write, and a counter bumped before the check lets refused requests burn the daily allowance. |
