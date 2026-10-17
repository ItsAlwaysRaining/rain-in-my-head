CREATE TABLE IF NOT EXISTS scrobbles (
    played_at   INTEGER NOT NULL,  -- unix seconds, UTC, start of play
    artist_name TEXT NOT NULL,
    track_name  TEXT NOT NULL,
    album_name  TEXT,
    artist_mbid TEXT,
    track_mbid  TEXT,
    album_mbid  TEXT,
    loved       INTEGER NOT NULL DEFAULT 0,
    image_url   TEXT,
    artist_key  TEXT NOT NULL,     -- normalized artist name
    track_key   TEXT NOT NULL,     -- normalized "artist<TAB>track"
    PRIMARY KEY (played_at, artist_name, track_name)
);
CREATE INDEX IF NOT EXISTS scrobbles_track_key ON scrobbles (track_key);
CREATE INDEX IF NOT EXISTS scrobbles_artist_key ON scrobbles (artist_key);

-- Enrichment caches. A row with fetched_at set but NULL info means "looked up, not found".
CREATE TABLE IF NOT EXISTS tracks (
    track_key        TEXT PRIMARY KEY,
    artist_key       TEXT NOT NULL,
    name             TEXT,
    duration_ms      INTEGER,
    global_listeners INTEGER,
    global_playcount INTEGER,
    fetched_at       INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS artists (
    artist_key       TEXT PRIMARY KEY,
    name             TEXT,
    mbid             TEXT,
    global_listeners INTEGER,
    global_playcount INTEGER,
    fetched_at       INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS artist_tags (
    artist_key TEXT NOT NULL,
    tag        TEXT NOT NULL,
    weight     INTEGER NOT NULL,
    PRIMARY KEY (artist_key, tag)
);

DROP VIEW IF EXISTS v_plays;
DROP VIEW IF EXISTS v_artist_genre;

CREATE VIEW v_artist_genre AS
SELECT artist_key, tag AS primary_genre
FROM (
    SELECT artist_key, tag,
           ROW_NUMBER() OVER (PARTITION BY artist_key ORDER BY weight DESC, tag) AS rn
    FROM artist_tags
)
WHERE rn = 1;

-- Local time uses the timezone of the machine running the query.
CREATE VIEW v_plays AS
SELECT
    s.played_at,
    datetime(s.played_at, 'unixepoch', 'localtime')                AS played_local,
    CAST(strftime('%Y', s.played_at, 'unixepoch', 'localtime') AS INTEGER) AS year,
    CAST(strftime('%H', s.played_at, 'unixepoch', 'localtime') AS INTEGER) AS hour,
    CAST(strftime('%w', s.played_at, 'unixepoch', 'localtime') AS INTEGER) AS weekday,  -- 0 = Sunday
    s.artist_name,
    s.track_name,
    s.album_name,
    s.loved,
    s.artist_key,
    s.track_key,
    t.duration_ms,
    COALESCE(t.duration_ms, 210000) / 60000.0 AS est_minutes,
    a.global_listeners AS artist_listeners,
    g.primary_genre
FROM scrobbles s
LEFT JOIN tracks t ON t.track_key = s.track_key
LEFT JOIN artists a ON a.artist_key = s.artist_key
LEFT JOIN v_artist_genre g ON g.artist_key = s.artist_key
-- Some old imported scrobbles have placeholder timestamps (1970-01-01 00:00:01, :02, ...).
WHERE s.played_at >= 946684800;  -- 2000-01-01

-- Last.fm track → Spotify catalog match, cached. spotify_uri NULL = searched, no good match.
CREATE TABLE IF NOT EXISTS spotify_matches (
    track_key      TEXT PRIMARY KEY,
    spotify_uri    TEXT,
    spotify_name   TEXT,
    spotify_artist TEXT,
    score          REAL,
    matched_at     INTEGER NOT NULL
);
