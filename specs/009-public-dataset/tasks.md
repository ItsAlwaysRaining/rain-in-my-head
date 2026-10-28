# Tasks: Two-year public dataset and a read-only hosted API

**Input**: specs/009-public-dataset/ (plan, research, data-model, contracts/api.md, quickstart)

**Tests**: no suite. Each story is checked with a [quickstart.md](quickstart.md) step.

## Phase 1: Setup

- [x] T001 In src/rain_in_my_head/config.py, add `HOSTED = os.environ.get("LISTENING_HOSTED") == "1"` and `REFUSAL = "This DJ doesn't take requests."`

## Phase 2: Foundational

- [x] T002 In src/rain_in_my_head/build.py, make `connect_readonly(db_path)` open `file:{db_path}?mode=ro&immutable=1` when `config.HOSTED`, and `mode=ro` otherwise (research R3)
- [x] T003 [P] In src/rain_in_my_head/overview.py, read through `closing(connect_readonly(...))` instead of `sqlite3.connect` in `_load`
- [x] T004 [P] In src/rain_in_my_head/genre.py, do the same in `genres()` and `genre_plays()`
- [x] T005 [P] In src/rain_in_my_head/artist.py, do the same for both reads
- [x] T006 In src/rain_in_my_head/api.py, make `_connect()` and `_binges()` use `connect_readonly`

## Phase 3: US1, the two-year copy (P1) 🎯 MVP

- [x] T007 [US1] Create src/rain_in_my_head/publish.py, following research R1 and R2. `publish(db_path, out, window_days=730, lag_days=7, now=None)`:
  - builds a temp file with `build.connect`
  - attaches the full database with `mode=ro`
  - copies scrobbles where "start ≤ played_at < end", then the tracks, artists and artist_tags whose keys appear in them
  - detaches, drops `spotify_matches`, sets `journal_mode=DELETE`, runs `VACUUM`, then `os.replace`
  - raises `SystemExit` if the full database is missing
  - returns `PublishStats`
- [x] T008 [US1] In src/rain_in_my_head/cli.py, add `publish --window-days 730 --lag-days 7 --out data/public.db`. It prints the data-model.md line.
- [x] T009 [US1] Run quickstart step 1. Record the dates, counts, size and time, plus the cross-check queries.

## Phase 4: US2, the hosted API can't change anything (P2)

- [x] T010 [US2] In src/rain_in_my_head/api.py, add a hosted guard middleware (research R4):
  - active only when `config.HOSTED`
  - allows GET, except `/api/playlists*` and `/api/ai*`
  - allows `POST /api/sql`
  - refuses everything else with `403 {"error":"refused","message":config.REFUSAL}`
- [x] T011 [US2] In src/rain_in_my_head/api.py, when hosted, create the app with `docs_url=None` and `openapi_url=None`, and add `"hosted": config.HOSTED` to `/api/health`
- [x] T012 [P] [US2] In web/src/api.ts, have `request()` throw `ApiError("refused", body.message)` for a 403 whose body has `error === "refused"`, and add `"refused"` to `ApiErrorKind`
- [x] T013 [P] [US2] In web/src/components/ui.tsx, have `ErrorState` render a refused error as `<Notice>{message}</Notice>`. In web/src/pages/Schema.tsx, have `saveError` pass a refused message through.

## Phase 5: US3, pre-defined queries only and no AI (P3)

- [x] T014 [US3] In src/rain_in_my_head/sql_examples.py:
  - `schema()` quotes table names like `schema_info._quote` (FR-013)
  - add `run_example(db_path, name)`, which raises `KeyError` for an unknown name and otherwise runs `EXAMPLES[name]` through `run_readonly`
- [x] T015 [US3] In src/rain_in_my_head/api.py:
  - `SqlRequest` gets `sql: str | None` and `example: str | None`
  - when hosted, it runs only a known `example` and refuses anything else with the refusal
  - locally, `sql` works as today and `example` also works
  - `/api/sql/meta` adds `"hosted"`
- [x] T016 [US3] In web/src/api.ts, add `hosted: boolean` to `SqlMeta`, and add `runSqlExample(name)`, which sends `{example: name}`
- [x] T017 [US3] In web/src/pages/Sql.tsx, when `meta.data.hosted`:
  - render a "Pre-defined queries" picker, the chosen query's SQL as read-only `<pre>`, and a Run button
  - hide the textarea, Clear and "Use in Playlist Generator"
  - the results table and CSV download stay
  - local behaviour is unchanged
- [x] T018 [US3] Run quickstart steps 2–4 (curl the refusals, check the checksum, browser click-through, local mode)

## Phase 6: Polish

- [x] T019 [P] README.md: `publish`, `LISTENING_HOSTED=1`, and what's off when hosted (SQL text, AI, playlists, layout saving), all with "This DJ doesn't take requests."
- [x] T020 [P] docs/streamlit-vs-typescript.md: the hosted pre-defined-query picker is TypeScript-only, because Streamlit isn't hosted
- [x] T021 Run `uvx ruff check` on the changed Python, and `npm run build` in web/ (type check)
- [ ] T022 Open the PR (template; checked and not checked)

## Dependencies

- T001 → T002 → T003–T006 → US1 → US2 → US3 → Polish
- T012 and T013 run in parallel with T010 and T011.
- T016 → T017.
