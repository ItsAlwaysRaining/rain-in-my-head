# Quickstart: validating phase 2

`$S` is a scratch folder. None of these steps touches `data/listening.db`, apart from reading it.

## 1. Publish (US1)

```sh
uv run rain-in-my-head build
time uv run --no-default-groups rain-in-my-head publish --out $S/public.db
```

Expected: under 30 s, and under 25 MB.

Cross-check the result against direct queries:

```sh
sqlite3 $S/public.db "SELECT date(MIN(played_at),'unixepoch'), date(MAX(played_at),'unixepoch'), COUNT(*) FROM scrobbles;"
sqlite3 $S/public.db "SELECT COUNT(*) FROM tracks WHERE track_key NOT IN (SELECT track_key FROM scrobbles);"     # 0
sqlite3 $S/public.db "SELECT COUNT(*) FROM artists WHERE artist_key NOT IN (SELECT artist_key FROM scrobbles);"  # 0
sqlite3 $S/public.db "SELECT name FROM sqlite_master WHERE name='spotify_matches';"                              # empty
sqlite3 data/listening.db "SELECT COUNT(*) FROM scrobbles WHERE played_at >= <start> AND played_at < <end>;"     # same count
```

## 2. Hosted mode refuses (US2, US3)

```sh
LISTENING_HOSTED=1 LISTENING_DB=$S/public.db uv run rain-in-my-head serve --port 8010 &
shasum $S/public.db
for r in "PUT /api/schema/layout" "DELETE /api/schema/layout" "GET /api/playlists/meta" "POST /api/playlists/preview" "POST /api/ai/x"; do curl -s -X ${r% *} localhost:8010${r#* }; echo; done
curl -s -XPOST localhost:8010/api/sql -H 'content-type: application/json' -d '{"sql":"SELECT 1"}'
curl -s -XPOST localhost:8010/api/sql -H 'content-type: application/json' -d '{"example":"nope"}'
curl -s -XPOST localhost:8010/api/sql -H 'content-type: application/json' -d '{"example":"Plays by genre"}' | head -c 200
curl -s -o /dev/null -w '%{http_code}\n' localhost:8010/api/docs     # 404
```

Expected:
- Every refusal returns exactly `{"error":"refused","message":"This DJ doesn't take requests."}`.
- "Plays by genre" returns rows that match `sqlite3 $S/public.db` running the same SQL.
- After the browser pass in step 3, `shasum` is unchanged and there's no `public.db-wal`, `-shm` or `-journal` file.

## 3. Browser (constitution III)

Use headless Chrome on `localhost:8010`:
- Overview, Genre and Artist load and show the 2-year range.
- On Analyst, the schema map shows, the example picker runs "Top artists this year", and there's no editable box.
- Dragging the schema map shows the refusal.
- Opening `/playlists` shows "This DJ doesn't take requests."

## 4. Local mode is unchanged (FR-012)

Run `uv run rain-in-my-head serve` on the full database. The SQL page accepts free-form SQL, and the playlist preview works.
