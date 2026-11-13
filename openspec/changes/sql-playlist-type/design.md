## Context

Playlist types share `PlaylistRequest` → `_preview()` → `pl.Preview` → `/api/playlists/preview` and `/api/playlists/create`. Analyst runs typed SQL via `sq.run_readonly` (read-only `mode=ro` connection). The SQL tab is a `ComingSoon` placeholder in `Playlists.tsx`; Analyst's button already navigates to `/playlists?type=sql` but drops the query.

## Goals / Non-Goals

**Goals:** SQL type end to end on the owner's Mac; Analyst hand-off; hosted refusal unchanged.
**Non-Goals:** running typed SQL on the hosted site; a query timeout (Analyst has none today, so "same timeouts" means none added; a separate issue if wanted).

## Decisions

1. **Reuse the preview/create routes** with `kind: "sql"` and a `sql: str` field, not a new route. Create then needs no new code and `check_routes` needs no new entry. A new `/api/playlists/sql` route would be refused on hosted anyway, but reuse is less code.
2. **`pl.preview_sql(conn_path, sql)`** runs `sq.run_readonly`, lowercases column names for the check, returns `Preview(warning=...)` with a `missing` list when columns are absent. Rows keep every column; `ranked` gets a `track_key` built with `build.normalize`/`normalize_track` (same as `build.py`) so `match_tracks` and the `spotify_matches` cache work. Size = min(rows, 100).
3. **Hosted guard inside `_preview`**: if `config.HOSTED and body.kind == "sql"` → `_refused()`. Preview is a hosted-allowed route, so the check must live in the handler.
4. **Frontend**: `SqlForm` with a textarea and Preview button (preview on click, not debounced, since a half-typed query errors). Missing Columns uses `Notice tone="warning"` with the Figma copy. Query travels in the URL as `?type=sql&sql=<encoded>`; the form reads it on mount.
5. **Column labels**: extra columns use the raw column name, kind `number` when numeric.

## Risks / Trade-offs

- Long URLs from big queries → browsers handle ~2 KB fine; if it bites, switch to `sessionStorage`.
- A slow query has no timeout → same as Analyst today; owner-only.
