# Streamlit vs. TypeScript

This project has two dashboards over the same `data/listening.db`:

- **Streamlit** (`dashboard/`): `uv run streamlit run dashboard/app.py` → http://localhost:8501
- **TypeScript** (`web/` + `src/listening/api.py`): `uv run listening serve` → http://localhost:8000

Both get their numbers from the same functions in `src/listening/`, so any difference you see is the UI, not the maths. This log records what building and changing each one was like, page by page, as the work happened (spec `specs/003-typescript-dashboard`).

## How to read this

- **Lines**: `wc -l` of the code written for that page. For Streamlit, the view in `dashboard/views/`. For TypeScript, the page, its chart builders and its API route. Shared data functions in `src/listening/` are counted once, separately, because both apps use them. Shared components, such as the table and chart wrapper, are counted in "Foundation".
- **Effort**: working sessions, with notes. Not exact hours.
- **Easy / hard**: what each approach made simple or difficult for that page.

## Foundation

| | Streamlit | TypeScript |
|---|---|---|
| Lines | — | |
| Effort | — | |

## Pages

| Page | Streamlit lines | TS lines (page + charts + API route) | Shared function lines | Effort (TS) |
|---|---|---|---|---|
| Overview | | | | |
| Genre | | | | |
| SQL | | | | |
| Schema | | | | |
| Playlists | | | | |

## Same-change test

_Added after all pages are done: one identical small change made in both apps._

## Load times

_Time until each page's figures appear, both apps, same inputs._
