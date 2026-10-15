# Implementation Plan: Schema Page

**Branch**: `feature/schema-page` | **Date**: 2026-10-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-schema-page/spec.md` (follows issue #8)

## Summary

Add a "Schema" page to the dashboard menu that draws `listening.db` as a map of draggable cards, one
per table and view, joined by labelled link lines. Tables, columns, types and row counts are read
live from SQLite. Plain-English descriptions, data sources, links and default positions live in a
small hand-written module. The map is a Streamlit `components.v2` component (HTML, CSS and JS, no
build step); when a drag ends it sends the positions back to Python, which writes
`data/schema_layout.json` (gitignored).

## Technical Context

**Language/Version**: Python 3.10+ (venv is 3.12), managed with uv; plain browser JavaScript inside the component

**Primary Dependencies**: Streamlit 1.65 (`st.components.v2`, already installed), pandas (existing; nothing new)

**Storage**: SQLite `data/listening.db`, read-only (`sqlite_master`, `PRAGMA table_info`, `COUNT(*)`);
layout in `data/schema_layout.json`

**Testing**: Streamlit AppTest as a smoke test; headless Chrome via Playwright run ad hoc
(`uv run --no-project --with playwright`, `channel="chrome"`); SQLite cross-checks. The repo has no
test suite.

**Target Platform**: local Streamlit server (`uv run streamlit run dashboard/app.py`), desktop browser

**Project Type**: single project: CLI package `src/listening/` + Streamlit dashboard `dashboard/`

**Performance Goals**: page opens in under a second; schema and counts are cached until the
database file changes (measured: all row counts about 170 ms uncached, all `PRAGMA table_info`
calls under 1 ms)

**Constraints**: no API calls; read-only database connection; dark theme palette from
`.streamlit/config.toml`; whole card header is the drag target

**Scale/Scope**: 7 objects, about 50 columns; one new page, one notes module, one component

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. Raw scrobbles are the source of truth | Read-only connection; no schema or raw-file change. The layout file is not derived data and is safe to delete | Pass |
| II. Spec first, small changes | This spec; work on `feature/schema-page`; commits per task group | Pass |
| III. Verify in the real app | quickstart.md drags cards in headless Chrome, restarts the server, and cross-checks columns and counts in SQLite | Pass |
| IV. Few dependencies | `st.components.v2` ships with the installed Streamlit; no new package. Playwright run ad hoc only | Pass |
| V. Respect external APIs and secrets | No API calls; fonts come from the system stack, nothing is fetched | Pass |
| VI. Consistent dashboard | One page module in `dashboard/views/`, registered in `app.py`; colors from the theme palette; drag works anywhere on the header | Pass |
| Data and privacy | `data/schema_layout.json` added to `.gitignore` | Pass |

Post-design re-check (after research, data model and contract): still all Pass. No Complexity
Tracking entries.

## Project Structure

### Documentation (this feature)

```text
specs/002-schema-page/
├── spec.md
├── plan.md              # this file
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── schema-page.md   # what the page shows, the component's data in and out, the layout file
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
.gitignore                   # + data/schema_layout.json
dashboard/
├── app.py                   # register views/schema.py after SQL
├── schema_notes.py          # NEW: descriptions, sources, links, view lineage, default positions
├── schema_map/              # NEW: the map component's front end
│   ├── map.css
│   └── map.js
└── views/
    └── schema.py            # NEW: reads the schema, loads/saves the layout, mounts the component
README.md                    # "Schema page" section
```

**Structure Decision**: keep the existing layout. The component's CSS and JS sit in their own folder
and are read with `Path.read_text()` and passed inline, because `components.v2` only accepts file
paths for components installed as packages (see research.md).

## Complexity Tracking

None.
