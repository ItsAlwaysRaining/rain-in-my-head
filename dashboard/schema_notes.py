"""Plain-English notes for the Schema page: what each table and column means, how tables link,
and where cards start on the map. Names and columns themselves are read live from the database;
anything missing here shows as "No description yet"."""

from __future__ import annotations

# source: history = Last.fm listening history, details = Last.fm track/artist lookups,
#         spotify = Spotify search, view = a saved query
TABLES: dict[str, dict] = {
    "scrobbles": {
        "title": "Plays",
        "source": "history",
        "description": "One row for every song you played, imported from Last.fm. "
                       "Every other table hangs off this one.",
        "columns": {
            "played_at": "When the play started (Unix seconds, UTC)",
            "artist_name": "Artist, as Last.fm reported it",
            "track_name": "Track title",
            "album_name": "Album title",
            "artist_mbid": "MusicBrainz artist ID",
            "track_mbid": "MusicBrainz track ID",
            "album_mbid": "MusicBrainz album ID",
            "loved": "1 if you loved the track on Last.fm, else 0",
            "image_url": "Link to the album art",
            "artist_key": "Tidied-up artist name, used to link tables",
            "track_key": "Tidied-up artist + track, used to link tables",
        },
    },
    "tracks": {
        "title": "Track details",
        "source": "details",
        "description": "Extra facts about each track, looked up on Last.fm by listening enrich. "
                       "Only some tracks have been looked up so far.",
        "columns": {
            "track_key": "Which track this is",
            "artist_key": "Which artist made it",
            "name": "Track title as Last.fm spells it",
            "duration_ms": "Track length in milliseconds",
            "global_listeners": "How many Last.fm users have played it",
            "global_playcount": "Total plays across all of Last.fm",
            "fetched_at": "When this was looked up (Unix seconds)",
        },
    },
    "artists": {
        "title": "Artist details",
        "source": "details",
        "description": "Extra facts about each artist, looked up on Last.fm by listening enrich.",
        "columns": {
            "artist_key": "Which artist this is",
            "name": "Artist name as Last.fm spells it",
            "mbid": "MusicBrainz artist ID",
            "global_listeners": "How many Last.fm users listen to them",
            "global_playcount": "Total plays across all of Last.fm",
            "fetched_at": "When this was looked up (Unix seconds)",
        },
    },
    "artist_tags": {
        "title": "Artist genres",
        "source": "details",
        "description": "The tags Last.fm users give each artist, such as genres, "
                       "with how strongly each one applies.",
        "columns": {
            "artist_key": "Which artist",
            "tag": "A tag, for example “indie rock”",
            "weight": "How strongly the tag applies; higher is stronger",
        },
    },
    "spotify_matches": {
        "title": "Spotify matches",
        "source": "spotify",
        "description": "The Spotify song found for each Last.fm track when building a playlist. "
                       "Empty until a playlist is built.",
        "columns": {
            "track_key": "Which Last.fm track",
            "spotify_uri": "Spotify link; blank if no match was found",
            "spotify_name": "Track title on Spotify",
            "spotify_artist": "Artist on Spotify",
            "score": "How confident the match is",
            "matched_at": "When the match was made (Unix seconds)",
        },
    },
    "v_artist_genre": {
        "title": "Main genre per artist",
        "source": "view",
        "description": "Picks each artist's strongest tag as their main genre. "
                       "Ties go to the tag that comes first alphabetically.",
        "columns": {
            "artist_key": "Which artist",
            "primary_genre": "Their highest-weighted tag",
        },
    },
    "v_plays": {
        "title": "Plays, ready to analyze",
        "source": "view",
        "description": "Every play since 2000, joined with track, artist and genre details, plus "
                       "local-time columns. Old imports with placeholder 1970 dates are left out. "
                       "Most dashboard charts read from here.",
        "columns": {
            "played_at": "When the play started (UTC)",
            "played_local": "Play time in your local time zone",
            "year": "Year, local time",
            "hour": "Hour of day, 0–23, local time",
            "weekday": "Day of week, 0 = Sunday",
            "artist_name": "From Plays",
            "track_name": "From Plays",
            "album_name": "From Plays",
            "loved": "From Plays",
            "artist_key": "From Plays",
            "track_key": "From Plays",
            "duration_ms": "From Track details; blank if not looked up",
            "est_minutes": "Track length in minutes, or 3.5 if unknown",
            "artist_listeners": "From Artist details",
            "primary_genre": "From Main genre per artist",
        },
    },
}

# The database declares no foreign keys, so links are listed here: (table, column) on the "many"
# side → (table, column) on the "one" side.
LINKS: list[dict] = [
    {"from": ("scrobbles", "track_key"), "to": ("tracks", "track_key"), "label": "many plays → 1 track"},
    {"from": ("scrobbles", "artist_key"), "to": ("artists", "artist_key"), "label": "many plays → 1 artist"},
    {"from": ("tracks", "artist_key"), "to": ("artists", "artist_key"), "label": "many tracks → 1 artist"},
    {"from": ("artist_tags", "artist_key"), "to": ("artists", "artist_key"), "label": "many tags → 1 artist"},
    {"from": ("spotify_matches", "track_key"), "to": ("tracks", "track_key"), "label": "1 match → 1 track"},
]

# (what a view reads from, the view)
LINEAGE: list[tuple[str, str]] = [
    ("scrobbles", "v_plays"),
    ("tracks", "v_plays"),
    ("artists", "v_plays"),
    ("v_artist_genre", "v_plays"),
    ("artist_tags", "v_artist_genre"),
]

# Map pixels. Columns are 460 px apart so link labels fit between cards.
DEFAULT_POSITIONS: dict[str, tuple[int, int]] = {
    "scrobbles": (40, 40),
    "tracks": (500, 40),
    "artists": (500, 640),
    "spotify_matches": (960, 40),
    "artist_tags": (960, 640),
    "v_artist_genre": (960, 1000),
    "v_plays": (1420, 40),
}
