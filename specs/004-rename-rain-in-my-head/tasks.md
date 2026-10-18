---

description: "Tasks for renaming the app and repo to rain-in-my-head"
---

# Tasks: Rename to rain-in-my-head

**Input**: Design documents from `specs/004-rename-rain-in-my-head/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md, quickstart.md

**Tests**: no automated test suite was requested, and the repo has none. Verification is quickstart.md:
running the commands, headless Chrome on both apps, and a SQLite cross-check (constitution III).

**Organization**: US1 and US2 are delivered together in the PR, and US2 is mostly verification. US3
happens after the owner merges.

**PR boundary**: one PR, Phases 1–5 (`Closes #13`). Phase 6 runs after merge.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependencies)
- **[Story]**: user story from spec.md (US1–US3)

---

## Phase 1: Setup

- [x] T001 Baseline on `main`'s code, before any change: run `uv run listening stats` and save the output to `$SCRATCH/stats_before.txt`. Start Streamlit (`uv run streamlit run dashboard/app.py`) and `uv run listening serve` (after `npm run build` in `web/`). With headless Chrome, save the Overview KPIs for "All time" and "This year" from both apps to `$SCRATCH/kpis_before.json`. Stop both servers (quickstart step 1)

---

## Phase 2: Foundational (blocks all stories)

- [x] T002 `git mv src/listening src/rain_in_my_head` (delete `src/listening/__pycache__` if left behind). In `pyproject.toml` set `name = "rain-in-my-head"`, the script to `rain-in-my-head = "rain_in_my_head.cli:main"`, `packages = ["src/rain_in_my_head"]`, and change the `web` group comment to `src/rain_in_my_head/api.py`
- [x] T003 Replace every `from listening` / `import listening` with `rain_in_my_head` in `src/rain_in_my_head/*.py`, `dashboard/app.py` and `dashboard/views/*.py`. Change the uvicorn target in `src/rain_in_my_head/cli.py` to `"rain_in_my_head.api:app"`
- [x] T004 Run `uv lock` and `uv sync`. Check that `uv run rain-in-my-head --help` works, `uv run listening --help` fails, and `.venv/bin/listening` is gone. Commit "Move the package to rain_in_my_head and rename the command" (T002–T004, including `uv.lock`)

---

## Phase 3: User Story 1 – One name in everything I type and see (P1) 🎯 MVP

**Goal**: the command, both dashboards and every doc say rain-in-my-head or "Rain in My Head".

**Independent Test**: quickstart steps 2, 5 (titles and messages), 6 and 7.

### Code and UI strings

- [x] T005 [US1] In `src/rain_in_my_head/cli.py`, change the module docstring, `prog="rain-in-my-head"`, the argparse description to "Personal listening analytics from Last.fm scrobbles", and the "Run `listening build` first" message to `rain-in-my-head build`
- [x] T006 [P] [US1] In `src/rain_in_my_head/api.py`, set the docstring command and the `listening.overview` mention to the new name, `NO_DATABASE` to "No database yet. Run `uv run rain-in-my-head fetch` then `uv run rain-in-my-head build`.", and the FastAPI `title="Rain in My Head"`
- [x] T007 [P] [US1] In `src/rain_in_my_head/spotify.py`, change both "Run `uv run listening spotify-login`" messages to `uv run rain-in-my-head spotify-login`. In `src/rain_in_my_head/lastfm.py`, set the User-Agent to `rain-in-my-head/0.1`. Check the other modules' docstrings and comments (`config.py`, `build.py`, `enrich.py`, `fetch.py`, `overview.py`, `playlist.py`, `__init__.py`) for the package or command name
- [x] T008 [P] [US1] In `dashboard/app.py`, set `page_title="Rain in My Head"`. In `dashboard/views/overview.py`, change both `st.title("Listening")` to `st.title("Rain in My Head")` and the `(need \`listening enrich\`)` comment. Keep the docstring's `data/listening.db`
- [x] T009 [P] [US1] Change the "Run `uv run listening …`" messages in `dashboard/views/sql.py`, `dashboard/views/playlists.py` and `dashboard/views/genre.py`, and the "by listening enrich" text in `dashboard/schema_notes.py`, to `rain-in-my-head`. Keep descriptive uses ("Biggest listening days", "listening overall", "Listening from") and the `listening.db` mention in `dashboard/views/schema.py`
- [x] T010 [US1] Commit "Use the new name in commands, messages and titles" (T005–T009)

### Web

- [x] T011 [P] [US1] In `web/index.html`, set `<title>Rain in My Head</title>`. In `web/src/pages/Overview.tsx`, set the `<h1>` to "Rain in My Head" and the `listening.overview` comment to `rain_in_my_head.overview`. In `web/src/components/ui.tsx`, change the three `uv run listening` commands. Change the comments in `web/src/api.ts` and `web/vite.config.ts`
- [x] T012 [US1] In `web/package.json`, set `"name": "rain-in-my-head-web"`. Run `npm install` in `web/` so `package-lock.json` picks up the name (no other lock changes). Run `npx tsc --noEmit` and `npm run build` (both clean). Commit "Rename the TypeScript app" (T011–T012)

### Workflow, docs and specs

- [x] T013 [P] [US1] In `.github/workflows/sync.yml`, change the command to `uv run --no-default-groups rain-in-my-head fetch`
- [x] T014 [P] [US1] In `README.md`, set the heading to `# Rain in My Head` and add a line to the intro that the project was formerly `spotify-music-analysis`. Change every `uv run listening` to `uv run rain-in-my-head` and `src/listening/` to `src/rain_in_my_head/`. Keep `data/listening.db`. Add a short "Renamed from spotify-music-analysis" section with the post-merge steps from research §7–8: `uv sync` after pulling, moving the folder and Claude's memory folder, and renaming the Spotify app (FR-011)
- [x] T015 [P] [US1] In `docs/streamlit-vs-typescript.md`, update only the general text (intro and "How to read this") that names the package. Leave the past rows and notes (`listening/overview.py` in the Overview entry) as written
- [x] T016 [P] [US1] `git mv listening-palette.html rain-in-my-head-palette.html`. Set its `<title>` to "Rain in My Head Palette" and the palette JSON `"name"` to "Rain in My Head"
- [x] T017 [US1] Commit "Rename in the workflow, README, comparison log and palette page" (T013–T016)
- [x] T018 [P] [US1] In `.specify/memory/constitution.md`, set the title to "# Rain in My Head Constitution", the commands to `rain-in-my-head build` / `rain-in-my-head enrich`, and every `src/listening/` to `src/rain_in_my_head/`. Keep `data/listening.db`. Bump to **Version** 1.1.1, Last Amended 2026-10-16 (PATCH, wording only, plan Complexity Tracking)
- [x] T019 [P] [US1] In `openspec/config.yaml` and `openspec/specs/dashboard-overview/spec.md`, change the package path and command names. Leave `openspec/changes/archive/` alone
- [x] T020 [P] [US1] In `specs/003-typescript-dashboard/tasks.md`, change `src/listening/`, `listening.<module>` and `uv run listening` to the new names in the open tasks T026–T043 only. In `specs/003-typescript-dashboard/quickstart.md` and `contracts/api.md`, update the commands and the `no_database` message text, which future slices verify against. Leave done tasks, plan, research and data model as written
- [x] T021 [US1] Commit "Rename in the constitution (1.1.1), living specs and open tasks" (T018–T020). `CLAUDE.md` names neither old name, so it needs no change. Confirm with `grep`

**Checkpoint**: quickstart steps 2, 6 and 7. Every `git grep -n -i -E "listening|spotify-music-analysis"` match is in data-model.md's kept or historical lists.

---

## Phase 4: User Story 2 – Nothing I already have breaks (P1)

**Goal**: data, login, sync and numbers are unchanged.

**Independent Test**: quickstart steps 3, 4 and 5.

- [x] T022 [US2] Run `uv run rain-in-my-head stats` and `build`, then compare `stats` with `$SCRATCH/stats_before.txt` (same counts). Run `enrich --limit 1` and `fetch`, then `playlist --days fri --hours 17-19 --dry-run`. The dry run must work without a new `spotify-login`. Check `git diff main --stat -- data/raw` shows only sync commits, if any, and nothing from this branch
- [x] T023 [US2] Sync check: in a throwaway environment (`UV_PROJECT_ENVIRONMENT=$SCRATCH/venv-sync uv run --no-default-groups rain-in-my-head --help`), confirm the command runs without the dashboard groups (FR-006)
- [x] T024 [US2] Restart Streamlit and `uv run rain-in-my-head serve`. In headless Chrome on both apps: the tab titles and Overview headings read "Rain in My Head". The KPIs for "All time" and "This year" equal `$SCRATCH/kpis_before.json`, and total plays equals `sqlite3 data/listening.db "SELECT COUNT(*) FROM scrobbles"`. Genre, SQL, Schema and Playlists open in Streamlit without errors. Then restart both with `LISTENING_DB=/nonexistent`: the "No database yet" messages quote `uv run rain-in-my-head`

---

## Phase 5: Polish & PR

- [x] T025 Final `git grep -n -i -E "listening|spotify-music-analysis"` pass, reading each match against data-model.md. Fix misses and commit
- [x] T026 Tick T001–T025 in this file and commit. `git switch main && git pull`, merge `main` into the branch if the sync has moved it, then `git push -u origin HEAD`. Open the PR with `.github/pull_request_template.md`: `Closes #13`, affects both apps, constitution PATCH 1.1.1 in this PR (and why), what was checked and what wasn't, and the post-merge steps

---

## Phase 6: User Story 3 – The repo and my machine follow the new name (P2, after merge)

**Goal**: GitHub, the clone, the local folder, Claude's memory and the Spotify app use the new name.

**Independent Test**: quickstart steps 8–12.

- [ ] T027 [US3] Claude, once the owner says the PR is merged: `gh repo rename rain-in-my-head --repo ItsAlwaysRaining/spotify-music-analysis --yes`, then `gh repo edit ItsAlwaysRaining/rain-in-my-head --description "Personal listening history from Last.fm, explored in two dashboards"`. Run `git remote set-url origin https://github.com/ItsAlwaysRaining/rain-in-my-head.git` if needed, then check `git remote -v`, `git fetch`, and that the old URL redirects (research §6)
- [ ] T028 [US3] Claude: check the next "Sync scrobbles" run succeeds (`gh run list --workflow sync.yml --limit 1`), or ask the owner whether to trigger one with `gh workflow run sync.yml`
- [x] T029 [US3] Claude: on `feature/new-artist-page`, merge `main` and update spec 001's `src/listening/` and `listening` command references to the new names. Commit there (research §5). Done without the merge: the names were updated on the branch, which then reached `main` in #23
- [ ] T030 [US3] Owner: close this Claude session, move the folder and Claude's memory folder, run `uv sync` and reopen the folder (README rename section, research §7). Confirm a new session recalls the "Data sources" memory
- [ ] T031 [US3] Owner: rename the Spotify developer app (research §8). Confirm a playlist dry run still works

---

## Dependencies & execution order

- Phase 1 → Phase 2 (the package move blocks everything) → Phase 3 → Phase 4 → Phase 5.
- Inside Phase 3, the [P] tasks touch different files. Each group ends with its commit task.
- Phase 6 starts only after the owner merges. T030 comes last because moving the folder ends this session.

## Parallel opportunities

- T006, T007, T008 and T009 (different Python files).
- T011 and T013–T016 (web, workflow, README, log and palette).
- T018, T019 and T020 (constitution, OpenSpec and spec 003).

## Implementation strategy

The MVP is Phases 1–3: the rename itself. Phase 4 proves nothing broke before the PR opens. Small
commits per group keep the merge-commit history readable (CLAUDE.md).
