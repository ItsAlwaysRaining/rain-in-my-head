# Tasks: Usage tracking and a fair-use limit

**Input**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: no suite (as in earlier phases). The checks are in [quickstart.md](quickstart.md), and each story names the part that proves it. Real-browser steps use a headless-Chrome tool started with `npx`, never added to the project (constitution III, IV).

**Format**: `- [ ] T### [P?] [US?] Description with file path`. `[P]` means a different file with no unfinished dependency. **Owner** marks a step only you can do.

**Rule for every task**: no code, code hash, cookie value, connection string or IP address is ever printed, logged, stored in a usage record or committed.

**Where**: all work happens in the worktree `rain-in-my-head-usage-tracking`, on `feature/usage-tracking`. Dev database only until the merge.

## Phase 1: Setup

- [x] T001 src/rain_in_my_head/viewer_schema.sql: add `usage_events` as `CREATE TABLE IF NOT EXISTS`, exactly per [data-model.md](data-model.md). Quote these constraints: `id` bigint generated always as identity primary key; `viewer_id` bigint not null references `viewers (id)` `on delete cascade`; `kind` text not null with a check allowing only `view`, `time`, `feature` and `limit`; `page`, `feature`, `detail` and `visit` text, nullable; `seconds` integer, nullable, with a check `seconds between 0 and 1800`; `at` timestamptz not null default `now()`. Add `CREATE INDEX IF NOT EXISTS usage_events_viewer_kind_at ON usage_events (viewer_id, kind, at DESC)` and `usage_events_at ON usage_events (at)`. Grants: `GRANT INSERT ON usage_events TO rain_app`, `GRANT SELECT (viewer_id, kind, page, at) ON usage_events TO rain_app`. No `UPDATE` or `DELETE` for `rain_app`. Update the header comment to name spec 012.
- [x] T002 [P] src/rain_in_my_head/viewers.py: add `"usage_events"` to `TABLES` so `viewer init` reports 5 tables. Change nothing else in this file.
- [x] T003 [P] src/rain_in_my_head/usage.py (new, constants only for now): `HEAVY_PER_MINUTE = 30`, `HEAVY_PER_DAY = 1000`, `EVENTS_PER_MINUTE = 120`, `MAX_SECONDS = 1800`, `RETENTION_MONTHS = 12`, `DEDUPE_SECONDS = 5`, and the `FREE_LIMITS` dict with a comment per entry saying where each number came from. Leave the two free-plan values as `None` until T032. One place for every limit (FR-014).

## Phase 2: Foundational (blocks every story)

- [x] T004 Run `uv run rain-in-my-head viewer init` against dev, twice. Expect `[dev] ready: 5 tables, role rain_app` both times. Cross-check in the report from `viewer list` that people are unchanged. Then check the grants through the app role's own connection (`VIEWERS_APP_URL_DEV`): an `INSERT` into `usage_events` works, a `SELECT kind, at` works, a `SELECT detail` is refused, and an `UPDATE` or `DELETE` is refused (constitution III).
- [x] T005 [P] src/rain_in_my_head/access.py: add `SESSION_ROUTES = frozenset({("POST", "/api/events")})` with a comment ("any logged-in person with at least one page may call these"). Add `session_allowed(pages, method, path)` returning true for a route in `SESSION_ROUTES` when `pages` is not empty. Do not add `visitors` to `PAGES`.
- [x] T006 src/rain_in_my_head/api.py: (a) in `access_guard`, keep the looked-up session on `request.state.session` and let a `SESSION_ROUTES` route through when `access.session_allowed` is true (otherwise the same 403 `not_available` as today); (b) in `hosted_guard`, add `/api/events` to the allowed POST paths and `/api/visitors` to `REFUSED_PREFIXES`; (c) in `check_routes`, include `SESSION_ROUTES` in the `listed` set. Prove (c) once by adding a throwaway `/api/zzz` route, seeing the app refuse to start, and removing it.
- [x] T007 [P] src/rain_in_my_head/usage.py: `record_event(url, viewer_id, kind, *, page=None, feature=None, detail=None, visit=None, seconds=None)` that inserts one row with the database's `now()`, clamps `seconds` to 0 and `MAX_SECONDS`, and returns nothing. It raises `neon.NeonUnavailable` unchanged so callers decide what a failure means. It never takes or stores a request header, address or cookie.

**Checkpoint**: the dev database has the new table with the right grants, and the guards know the new routes.

## Phase 3: US1, the site notices what each person does (P1) 🎯 MVP

**Goal**: page views, feature uses and time on page are stored for a logged-in person, and a failure never blocks them.

**Independent test**: [quickstart](quickstart.md) step 1.

- [x] T008 [US1] src/rain_in_my_head/usage.py: `report_open(url, viewer_id, pages, page, visit)` and `report_leave(url, viewer_id, pages, page, visit, seconds)`. Both ignore a `page` not in `pages` (the person's allowed pages), and share the cap: they first run the single statement from [research R4](research.md#r4-reports-are-a-logged-in-only-route-with-their-own-cap) that inserts only if the person has fewer than `EVENTS_PER_MINUTE` `view` and `time` rows in the last minute. `report_open` also skips the insert if the same person has a `view` for the same page within `DEDUPE_SECONDS`. `visit` must match `^[A-Za-z0-9]{8,32}$` and is otherwise ignored. `report_leave` writes a `time` row even with an unknown `visit`.
- [x] T009 [US1] src/rain_in_my_head/api.py: `POST /api/events` per [contracts/api.md](contracts/api.md). A pydantic body with `event` (`open` or `leave`), `visit`, `page` and optional `seconds` (0 to 1800); a bad body is 422. Refuse a mismatching `Origin` with the standard refusal (403). Run the work in `run_in_threadpool`, read the session from `request.state.session`, and answer `204` in every other case, including when the database is unreachable (swallow `neon.NeonUnavailable`, log nothing about the person). Locally (not hosted) answer `204` and store nothing.
- [x] T010 [P] [US1] web/src/api.ts: add `sendEvent(body)`. `open` uses `fetch` with `keepalive: true`; `leave` uses `navigator.sendBeacon` with a JSON `Blob` (`type: "application/json"`), falling back to `fetch` with `keepalive`. Neither throws and neither is awaited by callers. No error ever reaches the page.
- [x] T011 [US1] web/src/usage.ts (new): `useTracking()`. For a logged-in visitor on the hosted site only (`!auth.local && auth.loggedIn`), map the path to a page key with `PAGE_KEYS` in web/src/routes.ts, ignore paths with no key (`/`, `/login`), make a random 12-character `visit` id on each path change, send `open`, and send `leave` with the seconds when the path changes, the tab is hidden (`visibilitychange`) or the page is closed (`pagehide`). Count seconds only while the tab is visible and the person has moved, typed, scrolled or touched in the last 60 seconds; tick every 5 seconds. Cap at 1800 before sending. Send `leave` at most once per visit.
- [x] T012 [US1] web/src/App.tsx: call `useTracking()` once, inside the router and the `AuthProvider`.
- [x] T013 [US1] Run [quickstart](quickstart.md) step 1 on dev in headless Chrome: four page views, time rows near 20 seconds (the two `genre-songs` feature rows in that step appear only after T023, since a feature use is recorded by the same query that checks the limit; check them in T026), no rows from the landing or login page, no second `view` for a reload within 5 seconds, idle time stops after about 60 seconds, and pages still load with a wrong `DATABASE_URL`. Cross-check the counts with one direct query (constitution III).

**Checkpoint (MVP)**: views and time are recorded for a logged-in person, and nothing for anyone else.

## Phase 4: US2, the owner sees who used what (P1)

**Goal**: a Visitors page and a command, Mac only, with the same numbers, plus the free-plan section.

**Independent test**: [quickstart](quickstart.md) step 4 and step 9.

- [x] T014 [US2] src/rain_in_my_head/usage.py: `report(url, range_key)` returning the shape in [contracts/api.md](contracts/api.md) for `7d`, `30d` or `12m` (UTC): per person, `last_login_at` from `viewers`, `visits` (count of `view`), `seconds` (sum of `time`), `pages` (views and seconds per page), `features` (uses per `feature` and `detail`), `limit_hits` (count of `limit`). Include people with no activity. Plus `person_detail(url, name, limit=200)` returning that person's newest rows (`kind`, `page`, `feature`, `detail`, `seconds`, `at`; no id and no address). An unknown name raises a plain `usage.UsageError`.
- [x] T015 [US2] src/rain_in_my_head/usage.py: `free_plan(url)` for the current UTC month: recorded requests (`view` + `feature` + `limit` rows), `heavy_page_seconds` (sum of `time` rows on `genre` and `analyst`), `database_bytes` from `select pg_database_size(current_database())`, `database_limit_bytes` and the Vercel note from `FREE_LIMITS`. It promises no processing time per person (FR-018).
- [x] T016 [US2] src/rain_in_my_head/api.py: `GET /api/visitors` with `env` (`prod` or `dev`, default `prod`), `range` (default `30d`) and `person`, per [contracts/api.md](contracts/api.md). It reads the owner URL with `config.viewers_url`; a missing variable answers `503 not_configured` naming the variable. Unknown `env`, `range` or name is 422. Do the work in the threadpool. It is already refused on the hosted site by T006(b).
- [x] T017 [P] [US2] src/rain_in_my_head/cli.py: `viewer usage [--range 7d|30d|12m] [--person NAME]` per [contracts/cli.md](contracts/cli.md): the people table, then the free-plan section, then the line that time is an estimate. It calls the same `usage.report`, `usage.person_detail` and `usage.free_plan` as the API, so the numbers match (SC-008).
- [x] T018 [P] [US2] web/src/routes.ts: add `visitors: "/visitors"` to `PAGE_KEYS` and a "Visitors" item to `SECTIONS` with `pages: ["visitors"]`, placed after Analyst. It shows only on the owner's Mac, because no hosted tier has the key. Add the "Visitors" breadcrumb label.
- [x] T019 [US2] web/src/api.ts and web/src/pages/Visitors.tsx (+ Visitors.module.css): `fetchVisitors({env, range, person})` and its types from the contract; a page with a prod/dev choice, the three ranges, a table of people (last login, visits, time, top pages, features, limit hits), a click on a whole row to open that person's recent activity (constitution VI: the whole row responds), and the free-plan section with its Vercel note. Say plainly that time is an estimate and that days and months are UTC. A `not_configured` or `unavailable` answer shows the message in a `Notice`, not an error page. Use the existing palette tokens and `PageHeader`.
- [x] T020 [US2] web/src/App.tsx: add the `/visitors` route wrapped in `RequireAccess page="visitors"`. On the hosted site this shows "not available to you" for everyone.
- [x] T021 [US2] Run [quickstart](quickstart.md) step 4 (items 1 to 6) in headless Chrome, and compare the page, `viewer usage` and a direct query for one person (constitution III). Check the hosted-mode refusals for guest, trusted and no-code visitors, and that `viewer grant Robin --page visitors` is refused as an unknown page.

**Checkpoint**: the owner can read what recording stores.

## Phase 5: US3, one person can't use up the free limits (P2)

**Goal**: 30 heavy requests a minute and 1,000 a day per person, with a clear message and no effect on anyone else.

**Independent test**: [quickstart](quickstart.md) steps 2 and 3.

- [x] T022 [US3] src/rain_in_my_head/usage.py: `heavy_request(url, viewer_id, page, feature, detail=None)` that runs the single `insert ... select ... where ... returning 1 as ok` statement (the site can read back only four columns, so not `returning id`) from [research R1](research.md#r1-one-table-for-every-record-and-the-limit-counted-from-it) with `HEAVY_PER_MINUTE` and `HEAVY_PER_DAY` and explicit casts on every parameter (`$1::bigint`, `$5::int`). On a returned row, return. On none, run one transaction that works out the wait per [research R2](research.md#r2-windows-and-the-wait-time) and inserts a `limit` row (`feature` = `minute` or `day`) only if the person has none in the last minute, then raise `usage.RateLimited(message, retry_after)`. The messages are exactly "You're going a bit fast. Try again in N seconds." and "You've reached today's limit. It resets at midnight UTC." (singular "1 second"). `NeonUnavailable` propagates.
- [x] T023 [US3] src/rain_in_my_head/api.py: call `usage.heavy_request` inside `sql` (after the hosted checks that return `_refused()` or raise 422, and only when `config.HOSTED` and `body.example` is set; page `analyst`, feature `query`, detail the example name) and inside `genre_songs` (page `genre`, feature `genre-songs`, no detail), using `request.state.session.viewer_id`. Add `request: Request` to both handlers. Map `RateLimited` to `429` with a `Retry-After` header and `{"error": "rate_limited", "message", "retry_after"}`, and `NeonUnavailable` to the existing `503 unavailable`. Locally nothing is checked or recorded.
- [x] T024 [P] [US3] web/src/api.ts: add the `ApiError` kind `limited` for a `429` whose body has `error: "rate_limited"`, keeping the login's `slow_down` as it is. The error's message is the server's message.
- [x] T025 [US3] web/src/components/ui.tsx and the two callers web/src/pages/Genre.tsx and web/src/pages/Sql.tsx: show a `limited` error as a plain `Notice` with the server's message on the page the person is on, keeping the rest of the page usable, instead of the generic `ErrorState`. Do not retry automatically, and do not log the person out.
- [x] T026 [US3] Run [quickstart](quickstart.md) steps 2 and 3: 30 answers then `429` for one person, a second person unaffected, recovery after the stated wait without a new login, exactly one `limit` row after many refusals, typed SQL refused with 403 and no rows, and the daily message with `HEAVY_PER_DAY` lowered to 5 for one local run (revert it). Check the notice in a real browser. Then check the heavy requests with the database unreachable return `503`.

**Checkpoint**: the heavy routes are protected, and the owner sees who hit the limit in the report from T014.

## Phase 6: US4, visitors know what's tracked, and old records go away (P2)

**Goal**: the login page tells the truth, and records are deleted after 12 months.

**Independent test**: [quickstart](quickstart.md) steps 5 and 6.

- [x] T027 [P] [US4] web/src/pages/Login.tsx: replace the notice with the wording in [research R10](research.md#r10-the-tracking-notice), and update the file's top comment to name spec 012.
- [x] T028 [US4] src/rain_in_my_head/usage.py: `prune(url)` runs `delete from usage_events where at < now() - interval '12 months'` and returns the number deleted. It touches no other table (FR-021).
- [x] T029 [US4] src/rain_in_my_head/cli.py: `viewer prune` per [contracts/cli.md](contracts/cli.md), printing `[prod] deleted N usage records older than 12 months`.
- [x] T030 [US4] Run [quickstart](quickstart.md) step 5 on dev: a 13-month-old row is deleted, an 11-month-old row stays, and `viewer list` is identical before and after. Then read the login page in a real browser and check the new notice.

**Checkpoint**: the privacy promise is true in code, not only in text.

## Phase 7: US5, a nightly copy lands on a private branch (P3)

**Goal**: one fresh commit on `analytics` with the latest export, never touching `main`.

**Independent test**: [quickstart](quickstart.md) steps 6 and 7.

- [x] T031 [US5] src/rain_in_my_head/usage.py: `export_files(url, directory)` writes `usage_events.csv` and `viewers.csv` per [data-model.md](data-model.md#what-the-export-contains): the exact columns listed there, rows ordered by `at` then `id` (and by `name` for people), `\n` line endings, stdlib `csv`. No code hash, session or id column. Running it twice on an unchanged database must give byte-identical files. Returns the two row counts.
- [x] T032 [P] [US5] Owner check, then src/rain_in_my_head/usage.py `FREE_LIMITS`: confirm the current Neon free-plan storage limit and the Vercel Hobby limits on their pricing pages today, then fill the two `None` values from T003 with a comment naming the page and the date. This is research R7's open check. If a page can't be reached, ask the owner for the figure rather than guessing.
- [x] T033 [US5] src/rain_in_my_head/cli.py: `viewer export DIR` per [contracts/cli.md](contracts/cli.md), printing `[prod] wrote 2 files: N usage records, M people`.
- [x] T034 [US5] .github/workflows/analytics.yml (new): nightly `cron` plus `workflow_dispatch` with an `env` choice (`prod` default, `dev`), `permissions: contents: write`, `concurrency: analytics` with `cancel-in-progress: false`, `timeout-minutes: 15`. Steps: checkout, `astral-sh/setup-uv@v6`, then `uv run --no-default-groups rain-in-my-head viewer prune --env <env>` and `... viewer export "$RUNNER_TEMP/out" --env <env>`, with `VIEWERS_OWNER_URL_PROD` set from `secrets.NEON_PROD_OWNER_URL` (or `VIEWERS_OWNER_URL_DEV` from `secrets.NEON_DEV_OWNER_URL`). Then, per [research R9](research.md#r9-the-nightly-export): fetch the target branch (`analytics`, or `analytics-dev` for dev) if it exists; if both CSV files are identical to its current files, print "No change." and stop; otherwise `git checkout --orphan`, add only the two files, commit as `github-actions[bot]` with the date, and `git push --force origin HEAD:<branch>`. It must never push to any other branch. Print counts only, never a row.
- [x] T035 [P] [US5] CLAUDE.md: under "Never push to `main` or force-push", add one line: the scheduled `analytics` workflow replaces the `analytics` branch (only that branch) on purpose, so only the latest export is kept (spec 012).
- [x] T036 [US5] Run [quickstart](quickstart.md) steps 6 and 7's local part on dev: export twice and `diff -r` the output, then do the workflow's git steps by hand in a scratch clone of a local bare repo (orphan commit, force-push, change one row, repeat) and check the branch ends with one commit and an unchanged export makes no commit. Check by search that neither file holds an address, a code or a hash.

**Checkpoint**: the export works by hand. The scheduled run is checked after the merge (T041).

## Phase 8: Polish and the pull request

- [x] T037 [P] docs/streamlit-vs-typescript.md: note that the Visitors page and tracking are TypeScript only, and why (Streamlit is never hosted).
- [x] T038 [P] README.md: a "Usage and limits" section: what is recorded, the limits (30 a minute, 1,000 a day) and where they are changed, the new `viewer usage`, `prune` and `export` commands with `--env`, the nightly `analytics` branch (one commit, latest copy only, and the note that GitHub may keep an old commit reachable by its hash for a while), and the setup step: run `viewer init` on each database after pulling this change.
- [x] T039 Run the whole of [quickstart](quickstart.md) once on dev (steps 0 to 9, and step 8 for local mode: nothing recorded, no limit, the phase 4 checks still pass). Fix anything found. Make sure `uv run rain-in-my-head` still runs with `--no-default-groups`, and `npm run build` in web/ passes.
- [x] T040 Open the PR with `.github/pull_request_template.md`, list what was checked in a real browser and what was not (Vercel's real processing time, and a nightly run on the real schedule), and add `Closes #N` for any issue. Never merge.
- [ ] T041 **Owner**, after the merge: (a) run `uv run rain-in-my-head viewer init --env prod` and expect `[prod] ready: 5 tables, role rain_app`; (b) in Actions → analytics, run the workflow once with `dev`, then once with `prod`, and check the branches and that `main` is unchanged ([quickstart](quickstart.md) step 7). Claude adds both steps to the to-do page.

## Dependencies and order

- **Phase 1 and 2 first.** T001 → T004; T005, T006, T007 can follow in parallel with T004, but T006 needs T005.
- **US1** needs phase 2. T008 → T009; T010 and T011 can run beside the Python work; T012 needs T011.
- **US2** needs US1's table and rows to show anything (T014 can be written once T001 is done). T015 needs T003 for `FREE_LIMITS`; its real limits arrive in T032. T016 and T017 need T014 and T015; T019 needs T016 and T018; T020 needs T019.
- **US3** needs phase 2 and T006's `request.state.session`. It does not need US1 or US2, but its `limit` rows show up in the US2 report. T022 → T023; T024 → T025.
- **US4** needs only T001. T027 is independent. T028 → T029.
- **US5** needs T001 and the table's rows. T031 → T033 → T034; T032 can happen any time before T039.
- **Polish** last. T041 happens only after the owner merges.

## Parallel examples

- After T001: T002, T003 and T005 in parallel (three different files).
- US1: T010 (web/src/api.ts) and T008 (usage.py) in parallel.
- US2: T017 (cli.py) and T018 (routes.ts) in parallel once T014 and T015 exist.
- US4: T027 (Login.tsx) beside T028 (usage.py).
- Polish: T037 and T038 in parallel.

## Implementation strategy

1. **MVP**: phases 1 and 2, then US1 (T001 to T013). The site records what logged-in people do, and nothing else changes.
2. **Then US2** (T014 to T021) so the owner can read it, and **US3** (T022 to T026) so the free limits are protected before the site goes live in phase 6. US3 is P2 but is the reason this phase exists, so don't skip it.
3. **Then US4 and US5** (T027 to T036).
4. **Finish** with polish (T037 to T040), open the PR, and leave T041 to the owner after the merge.
5. Commit after each phase, in small steps. Stop at each checkpoint and run the story's quickstart steps before moving on.
