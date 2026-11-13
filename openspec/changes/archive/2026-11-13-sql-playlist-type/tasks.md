## 1. Backend

- [x] 1.1 Add `preview_sql` to `playlist.py`: run read-only, detect missing `artist`/`track`, build `track_key`, keep extra columns, cap 100
- [x] 1.2 Add `kind: "sql"` and `sql` to `PlaylistRequest`; route it in `_preview`; refuse it when hosted
- [x] 1.3 Return `missing` in the preview JSON
- [x] 1.4 Tests: valid query, missing one/both columns, extra columns, write attempt, hosted 403

## 2. Frontend

- [x] 2.1 Add `"sql"` to `PlaylistKind` and `sql`/`missing` to the types in `api.ts`
- [x] 2.2 Build `SqlForm` (textarea + Preview) and replace the `ComingSoon` tab in `Playlists.tsx`
- [x] 2.3 Missing Columns state per Figma 351-20225; hide Create when shown
- [x] 2.4 Read `?sql=` on mount; Analyst's button passes the current query
- [x] 2.5 Check against Figma 343-3397

## 4. Hand-off for every visitor

- [x] 4.1 Spec: Use in Playlist Generator replaces Download CSV; hosted SQL tab runs pre-defined queries by name
- [x] 4.2 API: `example` on SQL-type preview; hosted allows it (heavy-counted), refuses typed SQL
- [x] 4.3 Analyst: swap Download CSV for Use in Playlist Generator (Mac and hosted); drop the old button
- [x] 4.4 SQL tab on the hosted site: pick a pre-defined query, preview, Create shows the refusal
- [x] 4.5 Tests
- [x] 4.6 Add a playlist-ready pre-defined query ("Loved tracks, most played first"): none of the existing ones return artist and track

## 3. Verify

- [x] 3.1 Run backend tests and `npm run build` / lint
- [ ] 3.2 Create one real playlist on the Mac from a SQL query
