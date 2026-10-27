"""Load the raw JSONL scrobbles, then the Last.fm lookup cache, into SQLite. Safe to run repeatedly."""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

SCHEMA = Path(__file__).with_name("schema.sql")
# Plays before 2000-01-01 are old imports with placeholder timestamps; v_plays (schema.sql) leaves them out too.
MIN_PLAYED_AT = 946684800

# Version tags that shouldn't split a song's play count, e.g. "Song - Remastered 2011",
# "Song (feat. X)", "Song - Radio Edit". Live versions are left as distinct tracks.
_DASH_SUFFIX = re.compile(
    r"\s+[-–]\s+(\d{4}\s+)?(remaster(ed)?|digital(ly)? remaster(ed)?|mono|stereo|single version|radio edit|"
    r"album version|original mix)\b.*$",
    re.IGNORECASE,
)
_PAREN_SUFFIX = re.compile(
    r"\s*[(\[](feat\.?|ft\.?|featuring|(\d{4}\s+)?remaster(ed)?|mono|stereo|single version|radio edit)\b[^)\]]*[)\]]",
    re.IGNORECASE,
)


def normalize(name: str) -> str:
    return " ".join(name.casefold().replace("’", "'").split())


def normalize_track(name: str) -> str:
    name = _PAREN_SUFFIX.sub("", name)
    name = _DASH_SUFFIX.sub("", name)
    return normalize(name)


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # Wait for locks (e.g. a long-running `enrich`) instead of failing immediately.
    conn = sqlite3.connect(db_path, timeout=60)
    try:
        conn.execute("PRAGMA journal_mode=WAL")  # readers and one writer can work concurrently
    except sqlite3.OperationalError:
        pass  # switching modes needs a moment with no other connections; it sticks once set
    conn.executescript(SCHEMA.read_text())
    return conn


def connect_readonly(db_path: Path) -> sqlite3.Connection:
    """A connection that can't write, so a stray UPDATE/DELETE can't damage the database."""
    return sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)


def build(raw_dir: Path, db_path: Path, cache_dir: Path | None = None) -> int:
    conn = connect(db_path)
    rows = []
    for path in sorted(raw_dir.glob("*.jsonl")):
        with path.open() as f:
            for line in f:
                if not line.strip():
                    continue
                s = json.loads(line)
                artist_key = normalize(s["artist"])
                rows.append((
                    s["uts"], s["artist"], s["track"], s.get("album"),
                    s.get("artist_mbid"), s.get("track_mbid"), s.get("album_mbid"),
                    int(bool(s.get("loved"))), s.get("image"),
                    artist_key, f"{artist_key}\t{normalize_track(s['track'])}",
                ))
    with conn:
        # Re-derive keys on conflict so changes to normalize_track() apply to old rows.
        conn.executemany(
            """INSERT INTO scrobbles VALUES (?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT (played_at, artist_name, track_name) DO UPDATE SET
                 artist_key = excluded.artist_key, track_key = excluded.track_key""",
            rows,
        )
    total = conn.execute("SELECT COUNT(*) FROM scrobbles").fetchone()[0]
    print(f"Loaded {len(rows)} raw rows → {total} scrobbles in {db_path}")
    if cache_dir is not None:
        from .cache import replay

        replayed = replay(conn, cache_dir)
        if replayed is None:
            print(f"No enrichment cache in {cache_dir}")
        else:
            print(f"Replayed cache: {replayed[0]} tracks, {replayed[1]} artists ({replayed[2]} updated)")
    conn.close()
    return total
