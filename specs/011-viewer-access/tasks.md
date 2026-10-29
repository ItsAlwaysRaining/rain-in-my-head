# Tasks: Invite codes and locked pages

**Input**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: no suite (as in earlier phases). The checks are in [quickstart.md](quickstart.md), and each story names the part that proves it. Real-browser steps use a headless-Chrome tool started with `npx`, never added to the project (constitution III, IV).

**Format**: `- [ ] T### [P?] [US?] Description with file path`. `[P]` means a different file with no unfinished dependency. **Owner** marks a step only you can do.

**Rule for every task**: no code, cookie value, connection string or IP address is ever printed, logged or committed.

## Phase 1: Setup

- [x] T001 infra/outputs.tf: add `dev_app_url` and `prod_app_url`, both `sensitive = true`, returning `local.dev_app_url` and `local.prod_app_url`. No resource changes. Run `tofu fmt -check` in infra/.
- [ ] T002 **Owner**: push the branch, then in GitHub go to **Actions → Infrastructure → Run workflow** and choose `feature/viewer-access`. Wait for the green apply, then `git pull` (the bot commits the state). Then fill `.env` with the four `VIEWERS_*` values and a local `SESSION_SECRET` from [quickstart.md](quickstart.md) step 0. Each value goes straight into `.env`, never into chat.
- [x] T003 [P] `.env.example`: add the names only, with a comment each: `VIEWERS_OWNER_URL_DEV`, `VIEWERS_OWNER_URL_PROD`, `VIEWERS_APP_URL_DEV`, `VIEWERS_APP_URL_PROD`, and `SESSION_SECRET` and `DATABASE_URL` (the last two are set by Vercel when hosted).
- [x] T004 [P] src/rain_in_my_head/config.py: add `DATABASE_URL` and `SESSION_SECRET` (read from the environment, empty if unset), `SESSION_DAYS = 30`, and `viewers_url(env, role)` that returns the `VIEWERS_<ROLE>_URL_<ENV>` value or raises `SystemExit` naming the variable (never its value).

## Phase 2: Foundational (blocks every story)

- [x] T005 src/rain_in_my_head/neon.py: `query(url, sql, params=())` and `transaction(url, queries)` over `httpx`, per [research R1](research.md#r1-reaching-neon-from-the-app-and-the-commands): `POST https://<host>/sql`, headers `Neon-Connection-String`, `Neon-Raw-Text-Output: true`, `Neon-Array-Mode: true`; body `{"query","params"}` or `{"queries":[...]}`; result rows as lists, with the `fields` names. A 400 raises `NeonError(message)`; a network failure or any other status raises `NeonUnavailable`. Short timeout (5 s).
- [x] T006 Spike for T005: run `select 1` against the dev branch with the app URL's direct host. If Neon refuses it, make `neon.py` add `-pooler` after the endpoint id and note the result in research.md R1. Do not print the URL.
- [x] T007 [P] src/rain_in_my_head/viewer_schema.sql: the four tables from [data-model.md](data-model.md), written as `CREATE TABLE IF NOT EXISTS`. Quote these constraints exactly: `viewers.tier` check `guest` or `trusted`; `viewers.status` check `active` or `revoked`, default `active`; `viewers.code_hash` text not null unique; a unique index on `lower(name)` where `status = 'active'`; `viewer_pages` primary key `(viewer_id, page)` with `on delete cascade`; `sessions.id_hash` text primary key, `expires_at` not null, an index on `viewer_id`, `on delete cascade`; `login_attempts.source_key` text primary key. Then the app role's grants exactly as in the "What the app role may do" table, including `UPDATE (last_login_at)` on `viewers` only.
- [x] T008 [P] src/rain_in_my_head/access.py: `PAGES` (the ten keys from [contracts/cli.md](contracts/cli.md)), `TIER_PAGES` (guest: overview, new-artists, genre, artist, slot, mainstream, about, contact; trusted: those plus analyst and storm), `API_ACCESS` mapping each `(method, path)` to its allowing page keys exactly as in [research R5](research.md#r5-deny-by-default-and-which-page-unlocks-which-route), `PUBLIC_ROUTES` (`GET /api/health`, `GET /api/me`, `POST /api/login`, `POST /api/logout`), and `allowed(pages, method, path)`.
- [x] T009 src/rain_in_my_head/viewers.py (part 1, pure functions): `new_code()` (16 characters from the 56-character alphabet with no `0 O o 1 I l`, shown `xxxx-xxxx-xxxx-xxxx`), `clean_code()` (strip spaces and dashes, keep the case), `hash_code()` (hex SHA-256), `new_session_id()` (32 random bytes, URL-safe), `sign_cookie()` and `read_cookie()` (HMAC-SHA256 with `SESSION_SECRET`, `hmac.compare_digest`; a bad or edited cookie reads as no cookie), and `cookie_secure(request)` (true for HTTPS or `localhost` or `127.0.0.1`).
- [x] T010 src/rain_in_my_head/cli.py: add the `viewer` command group with a shared `--env dev|prod` (default `dev`) that prints `[dev]` or `[prod]` first, and the `init` command per [contracts/cli.md](contracts/cli.md): create `rain_app` if missing with the password parsed from `VIEWERS_APP_URL_<ENV>` (refuse anything but letters and digits before putting it in SQL; `ALTER ROLE` if it exists), then run viewer_schema.sql as the owner. Safe to run twice.
- [x] T011 Run `viewer init` against dev ([quickstart](quickstart.md) step 0.3), twice. Expect `[dev] ready: 4 tables, role rain_app` both times. Cross-check in `psql` that the four tables exist and that `rain_app` can `SELECT` from `viewers` but not `INSERT` into it (constitution III).

**Checkpoint**: the dev database has its tables, and `neon.py` works from the Mac.

## Phase 3: US1, the owner invites someone (P1)

**Goal**: add a person, get a code once, list everyone.

**Independent test**: [quickstart](quickstart.md) step 1.

- [x] T012 [US1] src/rain_in_my_head/viewers.py (part 2): `add_viewer(url, name, tier)` inserts a row with `hash_code(code)` and returns the code once. A duplicate active name raises a plain error ("Sam already has an active code"). `list_viewers(url)` returns name, tier, granted pages (joined with `string_agg`), status, created and last login, newest first.
- [x] T013 [US1] src/rain_in_my_head/cli.py: `viewer add NAME [--tier guest|trusted]` (prints `[dev] added Sam (guest)`, then the code and "This code can't be shown again.") and `viewer list` (a table), per [contracts/cli.md](contracts/cli.md). Errors are one plain line and exit code 1.
- [x] T014 [US1] Run quickstart step 1 on dev: add Sam (guest) and Robin (trusted), list them, add Sam again (expect the refusal), and confirm the stored `code_hash` equals the SHA-256 of Sam's code and that the code appears in no column of the four tables.

**Checkpoint**: owner commands work. Nothing is checked on the site yet.

## Phase 4: US2, a visitor logs in and sees only their pages (P1) 🎯 MVP

**Goal**: login page, signed cookie, deny by default, nav that hides locked pages.

**Independent test**: [quickstart](quickstart.md) steps 2, 3 and 4 (items 1 to 4, 8, 9).

- [x] T015 [US2] src/rain_in_my_head/viewers.py (part 3): `login(url, code, source)` looks up the active viewer by hash with `hmac.compare_digest`, creates the session row (`expires_at` = now + `SESSION_DAYS`), sets `last_login_at`, deletes expired sessions, and returns the session id. A wrong, revoked or unknown code gives the same `BadCode` error. `lookup_session(url, session_id)` runs the single join from [research R6](research.md#r6-checking-a-session-on-each-request) (session, viewer status and tier, `string_agg` of granted pages) and caches the answer in memory for 3 seconds. `end_session(url, session_id)` deletes the row. `pages_for(tier, granted)` unions the tier's starting pages with the grants.
- [x] T016 [US2] src/rain_in_my_head/api.py: add `GET /api/me`, `POST /api/login` and `POST /api/logout` per [contracts/api.md](contracts/api.md). Login and logout refuse a mismatching `Origin` (403). The cookie is `HttpOnly`, `Secure` per `cookie_secure`, `SameSite=Lax`, `Path=/`, max age 30 days. Locally (not hosted), `/api/me` returns `{"local": true}` and the other two return 404.
- [x] T017 [US2] src/rain_in_my_head/api.py: add the `access_guard` middleware, used only when hosted and run after the existing `hosted_guard`. For every `/api/*` request not in `PUBLIC_ROUTES`: no valid cookie gives `403 login_required`; a session whose pages don't allow the route gives `403 not_available`; a visitor database failure gives `503 unavailable`. Non-`/api` paths are untouched. Make `GET /api/health` return only `{"ok": true}` when hosted.
- [x] T018 [US2] src/rain_in_my_head/api.py: a start-up check that fails with a clear message if any registered `/api` route is neither in `API_ACCESS`, nor in `PUBLIC_ROUTES`, nor one of the routes `hosted_guard` always refuses (FR-017). Prove it once by adding a throwaway route, seeing the app refuse to start, and removing it.
- [x] T019 [P] [US2] web/src/api.ts: add `fetchMe()`, `login(code)` and `logout()`, and a new `ApiError` kind `locked` for a `403` whose body has `error: "login_required"`. Keep `refused` for the existing refusal.
- [x] T020 [P] [US2] web/src/routes.ts: add a page key for each path (`/dashboards` → `overview`, `/dashboards/new-artists` → `new-artists`, and so on, the same ten keys as `access.py`), and `visibleSections(pages)` so the top bar shows only sections with at least one allowed page.
- [x] T021 [US2] web/src/auth.tsx: `AuthProvider` loading `/api/me` once and exposing `{status, name, tier, pages, local}` through `useAuth()`, plus `RequireAccess page` (not logged in goes to `/login?next=…`; logged in without the page renders `NotAvailable`; local mode allows everything).
- [x] T022 [P] [US2] web/src/pages/Login.tsx and web/src/pages/Login.module.css: a code field, a Log in button, the plain bad-code and slow-down messages from the contract, and the notice from FR-009 ("This site stores your name, tied to your code, and when you log in."). Uses the existing palette tokens and `PageHeader`/`Notice` components. Public.
- [x] T023 [P] [US2] web/src/pages/NotAvailable.tsx: "That page isn't available to you." with a link back to the dashboards.
- [x] T024 [US2] web/src/App.tsx: wrap the app in `AuthProvider`, wrap each route in `RequireAccess` (leave `/` and `/login` public), filter the top bar and the dashboard links with `visibleSections`, add a Log out button when logged in, and redirect to `/login` when any data request fails with `locked`. Playlists keeps its existing "coming soon / refused" behaviour.
- [x] T025 [US2] Run quickstart steps 2 and 3 (hosted-mode run, `curl` with no cookie, every route) and step 4 items 1 to 4, 8 and 9 in headless Chrome. Record the status codes.

**Checkpoint (MVP)**: a guest code opens Genre and gets a 403 on `/api/sql`.

## Phase 5: US3, the owner revokes or changes access (P2)

**Goal**: revoke logs people out within 5 seconds, and grants apply on the next click.

**Independent test**: [quickstart](quickstart.md) step 4 items 5 to 7.

- [x] T026 [US3] src/rain_in_my_head/viewers.py (part 4): `revoke_viewer(url, name)` sets `status = 'revoked'`, `revoked_at`, and deletes that person's sessions in one transaction, returning how many ended. `grant(url, name, add_page=None, remove_page=None, tier=None)` validates page keys against `access.PAGES` and refuses a revoked person.
- [x] T027 [US3] src/rain_in_my_head/cli.py: `viewer revoke NAME` and `viewer grant NAME [--page KEY] [--remove-page KEY] [--tier guest|trusted]` per [contracts/cli.md](contracts/cli.md). `grant` with no option is an error. An unknown page key lists the valid keys.
- [x] T028 [US3] Run quickstart step 4 items 5 to 7 on dev. Time the gap between `viewer revoke` and the refused click: it must be under 5 seconds. Confirm a revoked code gives the same message as a wrong code, and that adding the same name again makes a new code that works while the old one doesn't.

## Phase 6: US4, guessing codes doesn't work (P3)

**Goal**: slow down and then stop guessing, without storing an address.

**Independent test**: [quickstart](quickstart.md) step 5.

- [x] T029 [US4] src/rain_in_my_head/viewers.py (part 5): `source_key(address)` is the hex HMAC of `"<UTC date>:<address>"` with `SESSION_SECRET`; the address is the first `x-forwarded-for` entry, or the connection address locally. `check_rate(url, key)` and `record_failure(url, key)` follow [research R7](research.md#r7-the-login-rate-limit-without-raw-ips): more than 5 wrong codes in a minute gives `SlowDown`; 20 wrong codes in a day sets `locked_until` 15 minutes ahead and gives `Locked`, even for a correct code. Delete rows with `updated_at` older than a day when anyone logs in.
- [x] T030 [US4] src/rain_in_my_head/api.py: call the rate check before the code check in `POST /api/login`, returning `429 slow_down` or `423 locked` per the contract, and record each wrong code.
- [x] T031 [US4] Run quickstart step 5 on dev: 6 wrong codes in a minute (the sixth gives 429), 20 wrong codes (a correct code then gives 423), and a correct code with another `x-forwarded-for` still works. Then confirm every `source_key` is 64 hex characters and no dotted address appears in any table (SC-005).

## Phase 7: Polish and cross-cutting

- [x] T032 [P] README.md: a "Visitors and invite codes" section covering the `.env` names, `viewer init`, the five commands, running the site in hosted mode locally, and what each tier opens. No values.
- [x] T033 [P] docs/streamlit-vs-typescript.md: note that login and locked pages exist in the TypeScript app only, because Streamlit is never hosted (constitution VI).
- [x] T034 Run quickstart step 6 (local mode unchanged): with `LISTENING_HOSTED` unset, every page opens with no login, `GET /api/me` returns `{"local": true}`, and `viewer` commands still work. Run the pages that existed before (Overview, Genre, Artist, Analyst) once and compare one number each with a direct `sqlite3` query (constitution III).
- [x] T035 Search the repo and the dev database once for leaks: `git grep` for the dev code and for a `postgresql://` string in tracked files (expect none), and check the server log from the browser runs contains no code, cookie or address.
- [x] T036 Open the PR with `.github/pull_request_template.md`: list what was checked (quickstart steps 1 to 6, with the numbers from T014, T025, T028, T031 and T034) and what wasn't (the production branch, and the Vercel runtime, which phase 6 covers). Say plainly that `viewer init` was run on dev only, and that `viewer init --env prod` is a step for after the merge. Mark the PR ready only after T014, T025, T028, T031 and T034 pass.
- [ ] T037 **Owner**: run `viewer init --env prod` after the merge, once, from your Mac, with the prod values in `.env`. Phase 7 sends the first codes.

## Dependencies and order

- Phase 1 comes first. T002 (owner) blocks T006, T011 and every run against dev.
- Phase 2 blocks every story. T005 before T006 and T010; T007 before T010; T009 before T012 and T015; T008 before T017.
- **US1 (T012 to T014)** needs Phase 2 only. **US2** needs US1 (it needs someone to log in as). **US3** needs US2 for the browser checks, and its code needs only Phase 2. **US4** changes `POST /api/login` from US2.
- Phase 7 comes last. T037 comes after the merge.

## Parallel opportunities

- T003 and T004 (different files). T007 and T008 (different files, after T005 is started).
- In US2, T019, T020, T022 and T023 are different files and can be written together before T021 and T024 join them.
- T032 and T033 together.

## Implementation strategy

1. **MVP**: Phases 1 and 2, then US1 and US2. That gives a working front door: invite someone, log in, and see only the allowed pages. Stop and demo it on dev.
2. Add US3 (revoke and grant), then US4 (guessing limit), each checked against its quickstart steps.
3. Polish, then the PR. Do not merge it: the owner does that.
4. Each commit is one task or a small group, with a message that says what changed.
