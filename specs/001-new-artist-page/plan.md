# Implementation Plan: New Artists and Artist Page

**Branch**: `feature/new-artist-page` | **Date**: 2026-10-14, revised 2026-10-18 for both dashboards | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-new-artist-page/spec.md` (issue #5)

## Summary

Add a "New artists in <period>" table to the Overview's discovery column in both dashboards,
listing artists first heard in the selected period (or the most recent month), with album art and
plays. Clicking a row opens a new, hidden Artist page (`/artist?artist=…&start=…&end=…`) showing the
artist's cover, name, period and all-time play counts, and their songs by plays.

The data work lives in a new shared module, `src/rain_in_my_head/artist.py`, built on the ranking
helpers already in `rain_in_my_head.genre` (`ranked`, `most_common`, `thumb`, the no-image hash).
The Streamlit pages call it directly; the TypeScript pages get the same results from the JSON API.
Missing art is shown with one shared placeholder image, `web/public/no-art.svg`.

## Technical Context

**Language/Version**: Python 3.10+ (venv is 3.12), managed with uv; TypeScript (React, Vite) in `web/`

**Primary Dependencies**: Streamlit 1.65, pandas, Altair; FastAPI; React, React Router, TanStack
Query (all existing; nothing new)

**Storage**: SQLite `data/listening.db`: the `scrobbles` table (it has `image_url`, which `v_plays`
doesn't). No schema change

**Testing**: no test suite. Streamlit AppTest as a smoke test; headless Chrome driven over the
DevTools protocol (or Playwright run ad hoc) for clicks; `npx tsc --noEmit` and `npm run build`;
SQLite cross-checks; the API and the Streamlit page compared for the same period

**Target Platform**: local servers (`uv run streamlit run dashboard/app.py`, `uv run rain-in-my-head
serve`), desktop browser

**Project Type**: CLI package `src/rain_in_my_head/` + Streamlit dashboard `dashboard/` + TypeScript
dashboard `web/` with its JSON API (`src/rain_in_my_head/api.py`)

**Performance Goals**: the Overview loads in about the same time as today; the artist page reads one
artist's rows (indexed on `artist_key`)

**Constraints**: no API calls on page load; images come from stored Last.fm URLs; neon rain palette

**Scale/Scope**: ~218k scrobbles, ~24k artists; one shared module, one API route plus a field on
`/api/overview`, one new page and one new table in each app

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|---|---|---|
| I. Raw scrobbles are the source of truth | Read-only queries; no schema or raw-file change | Pass |
| II. Spec first, small changes | This spec, revised before code; work on `feature/new-artist-page`; a commit per task group | Pass |
| III. Verify in the real app | quickstart.md clicks through both apps in headless Chrome and cross-checks counts in SQLite | Pass |
| IV. Few dependencies | No new dependency in either app | Pass |
| V. Respect external APIs and secrets | No API calls; the browser loads stored image URLs | Pass |
| VI. Consistent dashboards | Data work only in `rain_in_my_head.artist` (reusing `genre` helpers), called by both apps; `/artist` in both; one placeholder file in palette colours; whole row clickable | Pass |

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
│   └── artist-page.md   # the page's URL, what it shows, and the API it reads
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/rain_in_my_head/
├── artist.py            # NEW: period_label, list_period, new_artists, artist_page
└── api.py               # /api/overview gains `new_artist_list`; NEW GET /api/artist
dashboard/
├── app.py               # register views/artist.py (hidden, url_path "artist")
└── views/
    ├── overview.py      # "New artists in …" table under the new-artists chart
    └── artist.py        # NEW: the artist page
web/
├── public/no-art.svg    # NEW: placeholder image, shared by both apps
└── src/
    ├── api.ts           # types and fetchArtist
    ├── App.tsx          # /artist route (not in the menu)
    └── pages/
        ├── Overview.tsx # the same table, rows navigate to /artist
        ├── Artist.tsx   # NEW: the artist page
        └── Artist.module.css
README.md                # "Artist page" section
specs/003-typescript-dashboard/contracts/api.md  # the new route and field
```

**Structure Decision**: follow the two-dashboard layout from spec 003. Shared data code goes in
`src/rain_in_my_head/`; each app only draws it.

## Complexity Tracking

None.
