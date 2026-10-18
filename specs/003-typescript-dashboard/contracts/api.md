# Contract: Dashboard JSON API

The API is served by `uv run rain-in-my-head serve` (default port 8000). All routes are under `/api` and return JSON. Dates are local `YYYY-MM-DD`; datetimes are ISO local with no zone. Field shapes are listed in [data-model.md](../data-model.md).

## Common errors

| Status | Body | When |
|---|---|---|
| 503 | `{"error": "no_database", "message": "No database yet. Run \`uv run rain-in-my-head fetch\` then \`uv run rain-in-my-head build\`."}` | `data/listening.db` missing |
| 422 | FastAPI validation detail | bad parameter type or value |

When the frontend cannot reach `/api` at all, it shows "The data service isn't running. Start it with `uv run rain-in-my-head serve`."

## Slice 1

### `GET /api/health`
`{"ok": true, "db": true|false, "db_mtime": float|null}`

### `GET /api/overview`
- **Query**: `preset`, `start`, `end`, `grain`, `period` (see OverviewRequest).
- **Response**: OverviewResult.

| Case | Response |
|---|---|
| The database has no scrobbles | `200 {"empty": true, "reason": "no_scrobbles"}` |
| The range has no plays | `200 {"empty": true, "reason": "no_plays_in_range", "range": …}` |
| `period` doesn't match a bar | Ignored (`selected: null`) |

## Slice 2

### `GET /api/genre?genre&start&end`
Returns GenreResult without songs. An unknown or missing `genre` falls back to the most-played one. When nothing is tagged yet: `200 {"genres": [], "genre": null, "reason": "no_tags"}`.

### `GET /api/genre/songs?genre&start&end&artist_key`
`{artist: {name, art, plays}, songs: [...]}`, where `art` is the 174s image. `404` when that artist has no plays in the genre and range.

### `GET /api/sql/meta`
`{examples: {title: sql}, schema: [{object, column, type}]}`

### `POST /api/sql`
- **Body**: `{"sql": "..."}`
- **Response**: `200` SqlResult, including `float_columns` (indexes of float columns, so the page can write `72.0` as pandas does). SQL errors are returned as `200 {"error": "..."}`, matching Streamlit's inline message.

## Slice 3

### `GET /api/schema`
SchemaResult.

### `PUT /api/schema/layout`
- **Body**: Layout.
- **Response**: `204`. It writes `data/schema_layout.json` atomically, as `schema.py` does.

### `DELETE /api/schema/layout`
Resets to the defaults and returns the new Layout.

### `GET /api/playlists/meta`
`{first, last, weekdays, binge_orders}`

### `POST /api/playlists/preview`
- **Body**: PlaylistRequest.
- **Response**: PlaylistPreview, or `{warning}` for the same cases where Streamlit shows a warning.

### `GET /api/playlists/spotify`
`{"connected": bool}` (token file present).

### `POST /api/playlists/create`
- **Body**: CreateRequest.
- **Response**: `text/event-stream` of `progress`, `done` and `error` events.

## Frontend routes

Same paths as Streamlit:

| Path | Query |
|---|---|
| `/` | `preset`, `start`, `end`, `grain`, `period`, `measure` mirror the Overview inputs, so a view can be bookmarked |
| `/genre` | `genre`, `start`, `end`, compatible with the Overview's links |
| `/sql` | — |
| `/schema` | — |
| `/playlists` | — |
