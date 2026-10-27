# Implementation Plan: Prototype Redesign

**Branch**: `feature/prototype-redesign` | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/005-prototype-redesign/spec.md`

## Summary

Restyle the TypeScript dashboard to match the Figma Prototype page. The changes:

- a top-bar shell with breadcrumbs instead of the sidebar
- the Figma type styles (Fredoka, Lexend, Red Hat Mono) and the raised-card elevation
- new routes under `/dashboards`, with redirects from the old paths
- a rebuilt Overview layout
- New artists as its own page
- Analyst, which merges SQL and Schema
- a tabbed Playlist Generator
- one shared `ComingSoon` component for the eight unbuilt features (#12, #27, #28, #30–#34)

Only `web/` changes. The pages keep reading the existing API.

## Technical Context

**Language/Version**: TypeScript 7, React 19

**Primary Dependencies**: Vite 8, react-router 8, @tanstack/react-query 5, Vega-Lite 6 (all existing; none added)

**Storage**: N/A (reads the existing JSON API; the Schema layout keeps using `/api/schema/layout`)

**Testing**: `npm run typecheck` and `npm run build`, plus a browser walk-through against the real database (constitution III). No test framework in `web/`.

**Target Platform**: Desktop browsers. Reference width 1440px, usable down to 360px.

**Project Type**: Web front end (SPA) served by the existing FastAPI app

**Performance Goals**: No slower than today. Only New artists makes an extra request (one `/api/overview` call).

**Constraints**: No backend changes. No new npm dependencies. Webfonts load from Google Fonts.

**Scale/Scope**: About 12 routes, 6 existing pages reworked, 1 new data page, 7 placeholder pages/tabs

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|---|---|---|
| I. Raw scrobbles are the source of truth | Pass | No data or schema changes. |
| II. Spec first, small changes | Pass | This spec. The branch was made first. Commits are split by step. |
| III. Verify in the real app | Pass (planned) | [quickstart.md](quickstart.md) walks every route in a browser and cross-checks Overview numbers with SQLite. |
| IV. Few dependencies | Pass | No new packages. Fonts are a `<link>` in `index.html`. |
| V. External APIs and secrets | Pass, with a note | Google Fonts is a font CDN, not a data API. No user data is sent. Pages still don't call Last.fm or Spotify on load. |
| VI. Consistent dashboards | **Deviation** | Palette unchanged except three genre-line colours. TypeScript routes no longer match Streamlit paths. See Complexity Tracking. Numbers still come from the shared Python functions, so the dashboards stay comparable. |

**Post-design re-check**: still passes. The design adds no data logic in TypeScript: New artists reuses `/api/overview`'s `new_artist_list`, and the genre chart re-plots the existing `genres.panels`.

## Project Structure

### Documentation (this feature)

```text
specs/005-prototype-redesign/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/routes.md
└── tasks.md
```

### Source Code

```text
web/
├── index.html                 # + Google Fonts link
└── src/
    ├── theme.css              # + font, type-scale, elevation and chart tokens
    ├── App.tsx / App.module.css   # top bar, breadcrumbs, routes, redirects
    ├── routes.ts              # NEW: one table of paths, labels and sections
    ├── charts/config.ts, overview.ts   # fonts, genre multi-line chart
    ├── components/
    │   ├── ui.tsx / ui.module.css      # Card, ChipGroup, Breadcrumbs, BackLink, Kpi and Tabs restyle
    │   ├── ComingSoon.tsx / .module.css  # NEW: the branded placeholder
    │   └── Form.module.css, DataTable.module.css  # restyle
    └── pages/
        ├── Overview.tsx        # new layout, filters on page, Loved tracks removed
        ├── NewArtists.tsx      # NEW
        ├── Genre.tsx, Artist.tsx       # restyle + BackLink
        ├── Analyst.tsx         # NEW: wraps Sql + Schema
        ├── Sql.tsx, Schema.tsx # become sections of Analyst
        ├── Playlists.tsx       # tabs, chips, Create bar, AI and SQL tabs
        └── Placeholders.tsx    # NEW: Home, Storm, Slot, Mainstream, About, Contact
docs/streamlit-vs-typescript.md  # note the route and layout differences
README.md                        # page list / paths
```

**Structure Decision**: keep the existing `web/src` layout. New pages are new modules in `pages/`. The placeholder pages share one module because each is only a `ComingSoon` with different text.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| VI: TypeScript paths differ from Streamlit's (`/dashboards`, `/analyst`, `/` is home) | The prototype's information architecture has a landing page and groups the drill-downs under Dashboards. The breadcrumbs depend on this. | Keeping Streamlit's paths would put the Overview at `/` and leave no room for the Landing page (#27). Changing Streamlit too is out of scope for a web-only redesign. Old paths redirect, and the difference is recorded in `docs/streamlit-vs-typescript.md`. |
| VI: palette gains three chart colours used only in TypeScript | The prototype draws the six genres as one multi-line chart, which needs six distinguishable series. Streamlit still uses small multiples with one colour. | Reusing rain/night/bolt for six lines makes the lines indistinguishable. |
