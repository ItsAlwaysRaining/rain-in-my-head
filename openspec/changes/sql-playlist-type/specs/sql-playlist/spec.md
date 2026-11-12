## ADDED Requirements

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
The Analyst page's **Use in Playlist Generator** button SHALL open Playlist Generator on the SQL tab with the current query filled in and previewed.

#### Scenario: Hand-off
- **WHEN** the owner types a query on Analyst and clicks Use in Playlist Generator
- **THEN** the SQL tab opens with that query in the box

### Requirement: Hosted site keeps typed SQL refused
On the hosted site, a SQL-type preview containing typed SQL SHALL be refused with 403 `refused` and "This DJ doesn't take requests.", as on Analyst. Create stays refused for every type.

#### Scenario: Guest previews typed SQL
- **WHEN** a hosted guest sends a SQL-type preview
- **THEN** the API answers 403 `refused` and nothing runs
