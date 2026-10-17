# Implementation Plan: Rename to rain-in-my-head

**Branch**: `feature/rename-rain-in-my-head` | **Date**: 2026-10-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-rename-rain-in-my-head/spec.md`

## Summary

Rename the project from `spotify-music-analysis` / `listening` to `rain-in-my-head` (issue #13).
The Python package moves to `src/rain_in_my_head/` and the command becomes `rain-in-my-head`. Both
dashboards are titled "Rain in My Head". The docs, the constitution and the open tasks follow. The
database file and its settings keep their names. One PR, merged by the owner. After that Claude
renames the GitHub repo and the owner moves the local folder and Claude's memory.

## Technical Context

- **Language/Version**: Python 3.10+ with uv; TypeScript on Node 22+ (`web/` only).
- **Primary Dependencies**: no new dependencies. hatchling builds the renamed package. `uv.lock` is
  regenerated for the new distribution name.
- **Storage**: SQLite `data/listening.db` and raw JSONL are left alone. Nothing is migrated.
- **Testing**: no test suite (constitution IV). Checks are the quickstart: running the commands, headless
  Chrome on both apps, a SQLite cross-check, `tsc --noEmit` and `npm run build`, and a final `git grep`.
- **Target Platform**: local machine, plus the GitHub Actions sync on ubuntu-latest.
- **Project Type**: Python package (CLI, shared data functions, API), a Streamlit app and a web frontend.
- **Performance Goals**: none. Behaviour is unchanged.
- **Constraints**: the sync keeps running with `--no-default-groups`. No change to raw files, `.env` or
  the Spotify token. No compatibility alias.
- **Scale/Scope**: about 11 import sites, 12 package files moved, about 25 user-facing strings, about 10 docs
  and spec files.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Checked against constitution 1.1.0.

| Principle | Check | Status |
|---|---|---|
| I. Raw scrobbles are the source of truth | Raw files untouched. `listening.db` keeps its name and contents, and needs no rebuild beyond a normal `build`. No schema change | Pass |
| II. Spec first, small changes | This spec; branch `feature/rename-rain-in-my-head`; one PR with one commit per step (move, strings, web, docs, specs) | Pass |
| III. Verify in the real app | Quickstart runs every command, drives both apps in headless Chrome and cross-checks a KPI against SQLite | Pass |
| IV. Few dependencies | No new dependencies. Sync still uses `--no-default-groups` (quickstart step 4) | Pass |
| V. External APIs and secrets | No new calls. The Last.fm User-Agent string changes. `.env` and the token are untouched | Pass |
| VI. Consistent dashboards | Both apps get the same display name in the same places. Shared functions only move package. The PR states it affects both apps | Pass |
| Governance: amendments via a `chore/` PR | The constitution's wording changes in this feature PR | Justified, see Complexity Tracking |

Post-design re-check: all still pass. The single deviation is recorded below.

## Project Structure

### Documentation (this feature)

```text
specs/004-rename-rain-in-my-head/
├── spec.md
├── plan.md              # this file
├── research.md
├── data-model.md        # name forms and what is kept
├── quickstart.md
├── contracts/cli.md     # before → after commands
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
pyproject.toml, uv.lock               # name, script, packages
src/listening/ → src/rain_in_my_head/ # git mv, imports, uvicorn target, messages, User-Agent
dashboard/app.py, dashboard/views/*   # imports, page_title, headings, "Run …" messages
web/index.html, web/package.json, web/package-lock.json, web/src/**, web/vite.config.ts
.github/workflows/sync.yml            # command
README.md, docs/streamlit-vs-typescript.md (intro only)
.specify/memory/constitution.md       # 1.1.1
openspec/config.yaml, openspec/specs/dashboard-overview/spec.md
specs/003-typescript-dashboard/       # open tasks T026–T043 and what they depend on
listening-palette.html → rain-in-my-head-palette.html
```

**Structure Decision**: same layout, with the package directory renamed. No new modules.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Constitution amended (PATCH 1.1.1, wording only) in a `feature/` PR, not a separate `chore/` PR | The constitution quotes `src/listening/` and `listening build`, which this PR renames. It is only correct if it changes in the same merge | A `chore/` PR merged first would name paths that don't exist yet. One merged after would leave `main` wrong in between |
