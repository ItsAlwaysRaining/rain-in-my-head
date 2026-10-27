"""Cache Last.fm track/artist info and artist tags for everything in `scrobbles`.

Most-played items are fetched first, each result is committed as soon as it arrives (so other
tools never wait long for the write lock), and anything already cached is skipped, so this can
be stopped and resumed at any time. With a cache writer (`enrich --write-cache`, used by the
scheduled sync), each lookup is also appended to data/cache/ before it is written to the database.
"""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path

from .build import connect
from .cache import CacheWriter
from .lastfm import LastfmClient

MIN_TAG_WEIGHT = 10
MAX_TAGS_PER_ARTIST = 10
TAG_STOPLIST = {
    "seen live", "favorites", "favourites", "favorite", "favourite", "love", "loved",
    "awesome", "beautiful", "cool", "amazing", "albums i own", "my favorites", "spotify",
    "under 2000 listeners", "all", "music", "good",
}
PROGRESS_EVERY = 250


def _int(value) -> int | None:
    try:
        return int(value) or None
    except (TypeError, ValueError):
        return None


def enrich_tracks(
    conn: sqlite3.Connection, client: LastfmClient, limit: int | None, writer: CacheWriter | None = None
) -> int:
    todo = conn.execute(
        """SELECT s.track_key, s.artist_key, MIN(s.artist_name), MIN(s.track_name)
           FROM scrobbles s
           WHERE s.track_key NOT IN (SELECT track_key FROM tracks)
           GROUP BY s.track_key
           ORDER BY COUNT(*) DESC
           LIMIT ?""",
        (limit if limit is not None else -1,),
    ).fetchall()
    print(f"Tracks to look up: {len(todo)}")
    for i, (track_key, artist_key, artist, track) in enumerate(todo, 1):
        info = client.track_info(artist, track) or {}
        row = {
            "track_key": track_key, "artist_key": artist_key, "name": info.get("name") or track,
            "duration_ms": _int(info.get("duration")),  # milliseconds; "0" means unknown
            "global_listeners": _int(info.get("listeners")), "global_playcount": _int(info.get("playcount")),
            "fetched_at": int(time.time()),
        }
        if writer:
            writer.track(row)  # cache first: a crash here costs a repeat lookup, never a lost one
        conn.execute("INSERT OR REPLACE INTO tracks VALUES (?,?,?,?,?,?,?)", tuple(row.values()))
        conn.commit()
        if i % PROGRESS_EVERY == 0:
            print(f"  tracks: {i}/{len(todo)}")
    return len(todo)


def enrich_artists(
    conn: sqlite3.Connection, client: LastfmClient, limit: int | None, writer: CacheWriter | None = None
) -> int:
    todo = conn.execute(
        """SELECT s.artist_key, MIN(s.artist_name)
           FROM scrobbles s
           WHERE s.artist_key NOT IN (SELECT artist_key FROM artists)
           GROUP BY s.artist_key
           ORDER BY COUNT(*) DESC
           LIMIT ?""",
        (limit if limit is not None else -1,),
    ).fetchall()
    print(f"Artists to look up: {len(todo)}")
    for i, (artist_key, artist) in enumerate(todo, 1):
        info = client.artist_info(artist) or {}
        stats = info.get("stats", {})
        weighted = ((t["name"].strip().lower(), int(t.get("count", 0))) for t in client.artist_top_tags(artist))
        tags = [
            (artist_key, tag, weight)
            for tag, weight in weighted
            if weight >= MIN_TAG_WEIGHT and tag not in TAG_STOPLIST
        ][:MAX_TAGS_PER_ARTIST]
        row = {
            "artist_key": artist_key, "name": info.get("name") or artist, "mbid": info.get("mbid") or None,
            "global_listeners": _int(stats.get("listeners")), "global_playcount": _int(stats.get("playcount")),
            "fetched_at": int(time.time()),
        }
        if writer:
            writer.artist(row, [(tag, weight) for _, tag, weight in tags])
        conn.execute("INSERT OR REPLACE INTO artists VALUES (?,?,?,?,?,?)", tuple(row.values()))
        conn.execute("DELETE FROM artist_tags WHERE artist_key = ?", (artist_key,))
        conn.executemany("INSERT OR IGNORE INTO artist_tags VALUES (?,?,?)", tags)
        conn.commit()
        if i % PROGRESS_EVERY == 0:
            print(f"  artists: {i}/{len(todo)}")
    return len(todo)


def enrich(client: LastfmClient, db_path: Path, limit: int | None = None, cache_dir: Path | None = None) -> None:
    conn = connect(db_path)
    writer = CacheWriter(cache_dir) if cache_dir is not None else None
    try:
        enrich_artists(conn, client, limit, writer)
        enrich_tracks(conn, client, limit, writer)
    finally:
        conn.close()
        if writer:
            writer.close()
            print(f"Appended {writer.tracks} track and {writer.artists} artist lookups to {cache_dir}")
