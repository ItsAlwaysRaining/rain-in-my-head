"""Cache Last.fm track/artist info and artist tags for everything in `scrobbles`.

Most-played items are fetched first, results are committed in small batches, and
anything already cached is skipped, so this can be stopped and resumed at any time.
"""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path

from .build import connect
from .lastfm import LastfmClient

MIN_TAG_WEIGHT = 10
MAX_TAGS_PER_ARTIST = 10
TAG_STOPLIST = {
    "seen live", "favorites", "favourites", "favorite", "favourite", "love", "loved",
    "awesome", "beautiful", "cool", "amazing", "albums i own", "my favorites", "spotify",
    "under 2000 listeners", "all", "music", "good",
}
COMMIT_EVERY = 1  # commit per item so other tools never wait long for the write lock


def _int(value) -> int | None:
    try:
        return int(value) or None
    except (TypeError, ValueError):
        return None


def enrich_tracks(conn: sqlite3.Connection, client: LastfmClient, limit: int | None) -> int:
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
        conn.execute(
            "INSERT OR REPLACE INTO tracks VALUES (?,?,?,?,?,?,?)",
            (
                track_key, artist_key, info.get("name") or track,
                _int(info.get("duration")),  # milliseconds; "0" means unknown
                _int(info.get("listeners")), _int(info.get("playcount")),
                int(time.time()),
            ),
        )
        if i % COMMIT_EVERY == 0:
            conn.commit()
        if i % 250 == 0:
            print(f"  tracks: {i}/{len(todo)}")
    conn.commit()
    return len(todo)


def enrich_artists(conn: sqlite3.Connection, client: LastfmClient, limit: int | None) -> int:
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
        tags = [
            (artist_key, t["name"].strip().lower(), int(t.get("count", 0)))
            for t in client.artist_top_tags(artist)
            if int(t.get("count", 0)) >= MIN_TAG_WEIGHT and t["name"].strip().lower() not in TAG_STOPLIST
        ][:MAX_TAGS_PER_ARTIST]
        conn.execute(
            "INSERT OR REPLACE INTO artists VALUES (?,?,?,?,?,?)",
            (
                artist_key, info.get("name") or artist, info.get("mbid") or None,
                _int(stats.get("listeners")), _int(stats.get("playcount")), int(time.time()),
            ),
        )
        conn.execute("DELETE FROM artist_tags WHERE artist_key = ?", (artist_key,))
        conn.executemany("INSERT OR IGNORE INTO artist_tags VALUES (?,?,?)", tags)
        if i % COMMIT_EVERY == 0:
            conn.commit()
        if i % 250 == 0:
            print(f"  artists: {i}/{len(todo)}")
    conn.commit()
    return len(todo)


def enrich(client: LastfmClient, db_path: Path, limit: int | None = None) -> None:
    conn = connect(db_path)
    try:
        enrich_artists(conn, client, limit)
        enrich_tracks(conn, client, limit)
    finally:
        conn.commit()
        conn.close()
