# Implementation Plan: Two-year public dataset and a read-only hosted API

**Branch**: `feature/public-dataset` | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

## Summary

This phase adds four things:

- **`publish`**: a new module (`publish.py`) that builds `data/public.db`. It holds plays from (now − 737 days) up to (now − 7 days), plus the tracks, artists and tags those plays reference. It has no `spotify_matches`, it's compacted, and it's swapped into place in one step.
- **Hosted mode**: one switch, `LISTENING_HOSTED=1`, which makes every read connection immutable.
- **A guard on the hosted API**: it refuses every non-GET route except `POST /api/sql`, and every `/api/playlists*` and `/api/ai*` route. All refusals answer `403 {"error":"refused","message":"This DJ doesn't take requests."}`.
- **Pre-defined queries only on the hosted SQL route**: it accepts only `{"example": "<name>"}`. The TypeScript SQL page shows a read-only picker when `hosted` is true.

## Technical Context

**Language/Version**: Python 3.10+ (uv); TypeScript (Vite + React) in `web/`

**Primary Dependencies**: no new ones. Standard-library `sqlite3`, FastAPI (existing `web` group), React Query (existing).

**Storage**: SQLite: the full `data/listening.db` (read) and `data/public.db` (written by `publish`, gitignored by `data/*.db`).

**Testing**: no suite. [quickstart.md](quickstart.md) covers SQL cross-checks (constitution III), `curl` against hosted-mode routes, and a headless-Chrome click-through of the TypeScript app.

**Target Platform**: macOS locally, and Vercel's Python runtime (phase 6)

**Project Type**: CLI, JSON API and web app

**Performance Goals**: `publish` under 30 s; `public.db` under 25 MB. There are about 45k plays in the window.

**Constraints**:
- In hosted mode, the database file is never written, locked or journaled.
- The sync must not need the `web` group, so `publish` imports only core modules.

**Scale/Scope**:
- Python: 7 modules touched: `config`, `build`, `overview`, `genre`, `artist`, `sql_examples`, `api`. Plus `cli` and the new `publish`.
- TypeScript: 3 files: `api.ts`, `ui.tsx` (`ErrorState`), `Sql.tsx`.

## Constitution Check

| Principle | Check | Result |
|---|---|---|
| I. Source of truth | `publish` only reads `listening.db` (through `ATTACH` with `mode=ro`). `public.db` is built and never committed, since it's already ignored by `data/*.db`. The schema is unchanged; `public.db` just drops `spotify_matches`. | ✅ |
| II. Spec first | Spec 009 is approved, on its own branch with one PR. | ✅ |
| III. Real app | Headless Chrome on `serve` with `LISTENING_HOSTED=1 LISTENING_DB=data/public.db`. Numbers are cross-checked against direct `sqlite3` queries of `public.db`. | ✅ |
| IV. Few dependencies | None added. | ✅ |
| V. APIs and secrets | Hosted mode refuses every playlist route. The deploy bundle (phase 6) contains no Spotify credential (FR-017); this phase makes sure no hosted path needs one. | ✅ |
| VI. Consistent dashboards | **TypeScript only.** The hosted picker exists only in the TypeScript app, because Streamlit is never hosted. Free-form SQL is unchanged in both apps locally. This is noted in `docs/streamlit-vs-typescript.md`. | ✅ (noted) |
| VII. Visitors' access | Deny by default: in hosted mode, any non-GET route not explicitly allowed is refused. There's no visitor data in `public.db`. | ✅ |

## Project Structure

```text
src/rain_in_my_head/
├── config.py        # + HOSTED (LISTENING_HOSTED=1), REFUSAL
├── build.py         # connect_readonly(): adds immutable=1 when HOSTED
├── publish.py       # NEW: publish(db, out, window_days=730, lag_days=7, now=None) -> PublishStats
├── overview.py      # _load via closing(connect_readonly)
├── genre.py         # genres(), genre_plays() via connect_readonly
├── artist.py        # both reads via connect_readonly
├── sql_examples.py  # schema(): _quote table names (FR-013); run_example(db, name)
├── api.py           # hosted guard middleware; /api/sql accepts {example}; meta and health report "hosted"; docs off when hosted; _connect/_binges read-only
└── cli.py           # + publish [--window-days 730] [--lag-days 7] [--out data/public.db]
web/src/
├── api.ts                 # ApiError kind "refused" (403 + error=refused); runSqlExample(); SqlMeta.hosted
├── components/ui.tsx      # ErrorState shows a refusal as a plain Notice
└── pages/Sql.tsx          # hosted: example picker + read-only SQL + Run; no textarea, no "Use in Playlist Generator"
docs/streamlit-vs-typescript.md  # hosted SQL picker is TypeScript-only
README.md                        # publish, hosted mode, what's off there
```

**Structure Decision**: the existing single package plus `web/`. `publish` gets its own module, because it's a separate CLI step that phase 6's CI will call.

## Risks carried to phase 6

- **Timezone.** `v_plays` uses SQLite's `'localtime'`, and the server runs in UTC, so hosted hour and day charts would shift. Phase 6 must set the function's timezone, or `publish` must store local times. Recorded in research R6.
