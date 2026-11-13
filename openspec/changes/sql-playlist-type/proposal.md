## Why

The three Playlist Generator types (slot, discoveries, binges) cover common questions. A SQL type covers everything else, such as "loved tracks, most played first". Issue #31.

## What Changes

- A fifth Playlist Generator tab, **SQL**, replaces the "coming soon" placeholder. Paste a read-only query that returns `artist` and `track` columns, preview the rows, and create the playlist on Spotify.
- The query runs through the Analyst page's read-only path (`sq.run_readonly`, `mode=ro` connection).
- If `artist` or `track` is missing, the tab shows the **Missing Columns** state naming the missing column(s).
- Extra columns appear in the preview table.
- Create on Spotify reuses `pl.create_on_spotify` and the existing `/api/playlists/create` stream.
- Analyst's **Use in Playlist Generator** button (already present, but it drops the query) now opens the SQL tab with the current query filled in.
- Hosted site: typed SQL stays refused, as on Analyst; Create stays refused, as for every type.

## Capabilities

### New Capabilities
- `sql-playlist`: the SQL playlist type, its preview, Missing Columns state, and the Analyst hand-off.

### Modified Capabilities
- None. `hosted-playlist-preview` and `hosted-analyst` rules apply unchanged.

## Impact

- `src/rain_in_my_head/playlist.py`: `preview_sql`.
- `src/rain_in_my_head/api.py`: `kind: "sql"` and `sql` field on `PlaylistRequest`; hosted refusal of typed SQL inside preview.
- `web/src/api.ts`, `web/src/pages/Playlists.tsx`, `web/src/pages/Sql.tsx`.
- Tests in `tests/` for the preview and the hosted refusal.
- Figma: Playlist Generator - SQL (343-3397), SQL - Missing Columns (351-20225).
