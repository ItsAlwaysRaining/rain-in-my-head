# sql-playlist Specification

## Purpose
TBD - created by archiving change sql-playlist-type. Update Purpose after archive.

## Requirements

### Requirement: SQL tab builds a playlist from a query
Playlist Generator SHALL have a **SQL** tab with a query box and a **Preview** button. The query SHALL run through the same read-only connection the Analyst page uses, so it cannot change data. The placeholder "coming soon" SQL tab SHALL be removed.

#### Scenario: Valid query
- **WHEN** the owner pastes `SELECT artist, track FROM v_plays GROUP BY track_key ORDER BY COUNT(*) DESC LIMIT 50` and clicks Preview
- **THEN** the preview lists those 50 rows in query order

#### Scenario: Write attempt
- **WHEN** the query is `DELETE FROM plays`
- **THEN** the database error is shown and nothing changes

#### Scenario: Invalid SQL
- **WHEN** the query has a syntax error
- **THEN** the error message is shown in place of the preview

### Requirement: Missing Columns state
If the result has no `artist` column or no `track` column (case-insensitive), the tab SHALL show the Missing Columns state naming each missing column, and SHALL NOT show Create on Spotify.

#### Scenario: Track missing
- **WHEN** the query returns `artist, plays`
- **THEN** the Missing Columns state names `track` and Create on Spotify is hidden

#### Scenario: Both missing
- **WHEN** the query returns `day, plays`
- **THEN** the state names both `artist` and `track`

### Requirement: Extra columns appear in the preview
Columns beyond `artist` and `track` SHALL appear in the preview table, in query order.

#### Scenario: Extra column
- **WHEN** the query returns `artist, track, plays`
- **THEN** the preview shows all three columns

### Requirement: Create on Spotify uses the existing path
Create on Spotify SHALL use the existing matching and creation code (`create_on_spotify`, the `spotify_matches` cache and the progress stream). Tracks are matched in query order; a track with no match is skipped and listed. At most 100 rows are used.

#### Scenario: Owner creates
- **WHEN** the owner clicks Create on Spotify on their Mac with Spotify connected
- **THEN** a playlist is created from the rows in query order and the unmatched tracks are listed

### Requirement: Analyst hands its query to the SQL tab
Under the Analyst results, a **Use in Playlist Generator** button SHALL replace **Download CSV**. It SHALL open Playlist Generator on the SQL tab with the query from the active editor filled in and previewed. On the owner's Mac that is the typed query; on the hosted site it is the chosen pre-defined query. The button SHALL show for every visitor.

#### Scenario: Hand-off on the Mac
- **WHEN** the owner runs a typed query on Analyst and clicks Use in Playlist Generator
- **THEN** the SQL tab opens with that query in the box and its preview

#### Scenario: Hand-off on the hosted site
- **WHEN** a visitor runs the pre-defined query "Loved tracks" and clicks Use in Playlist Generator
- **THEN** the SQL tab opens on that query, shows its SQL and preview, and shows Create on Spotify

### Requirement: Hosted site runs only pre-defined queries and refuses Create
On the hosted site the SQL tab SHALL let a visitor pick a pre-defined query by name and preview it; nothing can be typed. A SQL-type preview with typed SQL, or an unknown query name, SHALL be refused with 403 `refused` and "This DJ doesn't take requests." A pre-defined preview counts toward the visitor's heavy-request limit, as on Analyst. Clicking Create on Spotify SHALL show "This DJ doesn't take requests." as for every other type.

#### Scenario: Visitor previews a pre-defined query
- **WHEN** a hosted visitor previews a pre-defined query by name
- **THEN** the preview comes back

#### Scenario: Visitor sends typed SQL
- **WHEN** a hosted visitor sends a SQL-type preview with typed SQL
- **THEN** the API answers 403 `refused` and nothing runs

#### Scenario: Visitor clicks Create
- **WHEN** a hosted visitor clicks Create on Spotify on the SQL tab
- **THEN** a notice reads "This DJ doesn't take requests." and no playlist is created
