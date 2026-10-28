# Contract: hosted mode (`LISTENING_HOSTED=1`)

Every refusal uses the same response:

```http
HTTP/1.1 403
{"error": "refused", "message": "This DJ doesn't take requests."}
```

| Request | Local | Hosted |
|---|---|---|
| `GET /api/*` (overview, genre, artist, schema, sql/meta, health) | as today | as today |
| `GET /api/playlists/*` | as today | refused |
| `POST /api/playlists/*` | as today | refused |
| `PUT` / `DELETE /api/schema/layout` | as today | refused |
| `* /api/ai*` (none yet) | 404 | refused |
| `POST /api/sql {"sql": "..."}` | runs it (as today) | refused |
| `POST /api/sql {"example": "<name>"}` | runs `EXAMPLES[name]` | runs `EXAMPLES[name]`; refused if the name is unknown |
| any other non-GET | as routed | refused |
| `/api/docs`, `/api/openapi.json` | served | 404 |

## Additions

- `GET /api/health` → `{..., "hosted": bool}`
- `GET /api/sql/meta` → `{"examples": {...}, "schema": [...], "hosted": bool}`
- A `POST /api/sql` success has the same shape as today (`columns`, `float_columns`, `rows`, `row_count`).

## Frontend

- `ApiError.kind = "refused"` for a 403 whose body has `error: "refused"`.
- `ErrorState` renders `message` as a plain notice.
- When `SqlMeta.hosted` is true, `Sql.tsx` shows an example picker, the chosen SQL as read-only text, and a Run button that calls `runSqlExample(name)`.
