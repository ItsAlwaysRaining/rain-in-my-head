# Implementation Plan: New Artists and Artist Page

**Branch**: `feature/new-artist-page` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-new-artist-page/spec.md` (issue #5)

## Summary

Add a "New artists" table to the Overview's discovery column, listing artists first heard in the
selected period (or the most recent month), with album art and plays. Clicking a row opens a new,
hidden Artist page (`/artist?artist=…&start=…&end=…`) showing the artist's cover, name, period and
all-time play counts, and their songs by plays. Album-art helpers now in `dashboard/views/genre.py`
move to a shared module so both pages use them, plus a placeholder image for missing art.

## Technical Context

**Language/Version**: Python 3.10+ (venv is 3.12), managed with uv

**Primary Dependencies**: Streamlit 1.65, pandas, Altair (existing; nothing new)

**Storage**: SQLite `data/listening.db`: `scrobbles` table (incl. `image_url`) and `v_plays` view;
no schema change

**Testing**: Streamlit AppTest as a smoke test; headless Chrome via Playwright run ad hoc
(`uv run --no-project --with playwright`, `channel="chrome"`); SQLite cross-checks. The repo has no
test suite.

**Target Platform**: local Streamlit server (`uv run streamlit run dashboard/app.py`), desktop browser

**Project Type**: single project: CLI package `src/listening/` + Streamlit dashboard `dashboard/`

**Performance Goals**: pages render in about the same time as today; the artist query touches one
artist's rows (indexed on `artist_key`)

**Constraints**: no API calls on page load; images come from stored Last.fm URLs; dark theme palette

**Scale/Scope**: ~218k scrobbles, ~24k artists; one new page, one new table, one shared module

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. Raw scrobbles are the source of truth | Read-only queries; no schema or raw-file change | Pass |
| II. Spec first, small changes | This spec; work on `feature/new-artist-page`; commits per task group | Pass |
| III. Verify in the real app | quickstart.md clicks through in headless Chrome and cross-checks counts in SQLite | Pass |
| IV. Few dependencies | No new dependency; Playwright is run ad hoc only | Pass |
| V. Respect external APIs and secrets | No API calls; browser loads stored image URLs | Pass |
| VI. Consistent dashboard | One module per page; shared helpers moved out of `genre.py` (not copied); placeholder in palette colors; whole row clickable | Pass |

Post-design re-check (after research, data model and contract): still all Pass. No Complexity
Tracking entries.

## Project Structure

### Documentation (this feature)

```text
specs/001-new-artist-page/
├── spec.md
├── plan.md              # this file
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── artist-page.md   # the page's URL and what it shows
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
dashboard/
├── app.py               # register views/artist.py (hidden, url_path "artist")
├── lastfm_art.py        # NEW: PLACEHOLDER, NO_ART, thumb(), most_common(), ranked()
└── views/
    ├── overview.py      # "New artists" table under the new-artists chart
    ├── artist.py        # NEW: the artist page
    └── genre.py         # imports helpers from lastfm_art (behaviour unchanged)
README.md                # "Artist page" section
```

**Structure Decision**: keep the existing layout. Shared dashboard helpers go in `dashboard/` next
to `app.py`, which Streamlit puts on the import path (verified, see research.md).

## Complexity Tracking

None.
