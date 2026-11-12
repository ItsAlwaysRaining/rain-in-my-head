## 1. Backend

- [ ] 1.1 Add `preview_sql` to `playlist.py`: run read-only, detect missing `artist`/`track`, build `track_key`, keep extra columns, cap 100
- [ ] 1.2 Add `kind: "sql"` and `sql` to `PlaylistRequest`; route it in `_preview`; refuse it when hosted
- [ ] 1.3 Return `missing` in the preview JSON
- [ ] 1.4 Tests: valid query, missing one/both columns, extra columns, write attempt, hosted 403

## 2. Frontend

- [ ] 2.1 Add `"sql"` to `PlaylistKind` and `sql`/`missing` to the types in `api.ts`
- [ ] 2.2 Build `SqlForm` (textarea + Preview) and replace the `ComingSoon` tab in `Playlists.tsx`
- [ ] 2.3 Missing Columns state per Figma 351-20225; hide Create when shown
- [ ] 2.4 Read `?sql=` on mount; Analyst's button passes the current query
- [ ] 2.5 Check against Figma 343-3397

## 3. Verify

- [ ] 3.1 Run backend tests and `npm run build` / lint
- [ ] 3.2 Create one real playlist on the Mac from a SQL query
