"""The committed cache of Last.fm lookups in data/cache/, so a fresh clone can rebuild enrichment.

Two append-only JSONL files mirror the `tracks` and `artists` tables (artist lines carry their tags).
A redone lookup is appended, and the last line for a key wins. `build` replays the files into
SQLite; `enrich --write-cache` (the scheduled sync) and the one-time `export-cache` append to them.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

TRACKS_FILE = "tracks.jsonl"
ARTISTS_FILE = "artists.jsonl"
# Column order of the `tracks` and `artists` tables in schema.sql.
TRACK_FIELDS = ("track_key", "artist_key", "name", "duration_ms", "global_listeners", "global_playcount", "fetched_at")
ARTIST_FIELDS = ("artist_key", "name", "mbid", "global_listeners", "global_playcount", "fetched_at")


def _dumps(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def _has_lines(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def read(path: Path, key: str) -> dict[str, dict]:
    """The current state of one cache file: the last valid line for each key, in file order."""
    current: dict[str, dict] = {}
    if not path.exists():
        return current
    skipped = 0
    with path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                reason = f"not valid JSON ({e.msg})"
            else:
                if isinstance(obj, dict) and obj.get(key) and obj.get("fetched_at") is not None:
                    current.pop(obj[key], None)  # re-insert so dict order follows the latest line
                    current[obj[key]] = obj
                    continue
                reason = f"missing {key} or fetched_at"
            skipped += 1
            print(f"  skipped {path}:{lineno}: {reason}")
    if skipped:
        print(f"  {skipped} line(s) skipped in {path.name}")
    return current


class CacheWriter:
    """Appends lookups to the cache, one fully written and synced line per call."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self._files: dict[str, object] = {}
        self.tracks = 0
        self.artists = 0

    def _file(self, name: str):
        if name not in self._files:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            path = self.cache_dir / name
            f = path.open("a", encoding="utf-8")
            if _has_lines(path):
                with path.open("rb") as r:
                    r.seek(-1, os.SEEK_END)
                    if r.read(1) != b"\n":
                        f.write("\n")  # a crashed run left a cut-off line; don't glue onto it
            self._files[name] = f
        return self._files[name]

    def _append(self, name: str, obj: dict) -> None:
        f = self._file(name)
        f.write(_dumps(obj) + "\n")
        f.flush()
        os.fsync(f.fileno())

    def track(self, row: dict) -> None:
        self._append(TRACKS_FILE, {k: row.get(k) for k in TRACK_FIELDS})
        self.tracks += 1

    def artist(self, row: dict, tags: list) -> None:
        obj = {k: row.get(k) for k in ARTIST_FIELDS}
        obj["tags"] = [[tag, weight] for tag, weight in tags]
        self._append(ARTISTS_FILE, obj)
        self.artists += 1

    def close(self) -> None:
        for f in self._files.values():
            f.close()
        self._files.clear()

    def __enter__(self):
        return self

    def __exit__(self, *exc) -> None:
        self.close()


def export(conn: sqlite3.Connection, cache_dir: Path, append: bool = False) -> tuple[int, int]:
    """Write every enriched track and artist in the database to the cache (one-time seeding)."""
    tracks_path, artists_path = cache_dir / TRACKS_FILE, cache_dir / ARTISTS_FILE
    if not append and (_has_lines(tracks_path) or _has_lines(artists_path)):
        n_tracks, n_artists = len(read(tracks_path, "track_key")), len(read(artists_path, "artist_key"))
        raise SystemExit(
            f"{cache_dir} already has lookups ({n_tracks} tracks, {n_artists} artists). "
            "Use --append to add the database's rows after them."
        )
    tags: dict[str, list] = {}
    for artist_key, tag, weight in conn.execute(
        "SELECT artist_key, tag, weight FROM artist_tags ORDER BY artist_key, weight DESC, tag"
    ):
        tags.setdefault(artist_key, []).append((tag, weight))
    with CacheWriter(cache_dir) as writer:
        # One fsync per line is wasteful for 100k rows; write directly and sync once per file.
        for name, fields, sql, with_tags in (
            (TRACKS_FILE, TRACK_FIELDS, "SELECT * FROM tracks ORDER BY track_key", False),
            (ARTISTS_FILE, ARTIST_FIELDS, "SELECT * FROM artists ORDER BY artist_key", True),
        ):
            f = writer._file(name)
            for values in conn.execute(sql):
                obj = dict(zip(fields, values))
                if with_tags:
                    obj["tags"] = [[t, w] for t, w in tags.get(obj["artist_key"], [])]
                    writer.artists += 1
                else:
                    writer.tracks += 1
                f.write(_dumps(obj) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return writer.tracks, writer.artists


def replay(conn: sqlite3.Connection, cache_dir: Path) -> tuple[int, int, int] | None:
    """Load the cache into the database. A row is only replaced by a strictly newer line.

    Returns (tracks, artists, rows written), or None when there is no cache at all.
    """
    tracks_path, artists_path = cache_dir / TRACKS_FILE, cache_dir / ARTISTS_FILE
    if not tracks_path.exists() and not artists_path.exists():
        return None
    tracks = read(tracks_path, "track_key")
    artists = read(artists_path, "artist_key")
    have_tracks = dict(conn.execute("SELECT track_key, fetched_at FROM tracks"))
    have_artists = dict(conn.execute("SELECT artist_key, fetched_at FROM artists"))

    def newer(obj: dict, have: dict, key: str) -> bool:
        return obj[key] not in have or obj["fetched_at"] > have[obj[key]]

    track_rows = [tuple(o.get(k) for k in TRACK_FIELDS) for o in tracks.values() if newer(o, have_tracks, "track_key")]
    new_artists = [o for o in artists.values() if newer(o, have_artists, "artist_key")]
    with conn:
        conn.executemany(f"INSERT OR REPLACE INTO tracks VALUES ({','.join('?' * len(TRACK_FIELDS))})", track_rows)
        conn.executemany(
            f"INSERT OR REPLACE INTO artists VALUES ({','.join('?' * len(ARTIST_FIELDS))})",
            [tuple(o.get(k) for k in ARTIST_FIELDS) for o in new_artists],
        )
        conn.executemany("DELETE FROM artist_tags WHERE artist_key = ?", [(o["artist_key"],) for o in new_artists])
        conn.executemany(
            "INSERT OR IGNORE INTO artist_tags VALUES (?,?,?)",
            [(o["artist_key"], tag, weight) for o in new_artists for tag, weight in o.get("tags") or []],
        )
    return len(tracks), len(artists), len(track_rows) + len(new_artists)
