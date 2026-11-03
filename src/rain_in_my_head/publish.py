"""Build data/public.db: the two-year copy the hosted site serves (specs/009-public-dataset).

Only plays from `window_days` before the cut-off up to the cut-off (`lag_days` before now) are kept, with the
tracks, artists and tags they reference. Spotify matches are dropped. The full database is only read.
"""

from __future__ import annotations

import os
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .build import SCHEMA

DAY = 86400


@dataclass
class PublishStats:
    start: int
    end: int
    plays: int
    tracks: int
    artists: int
    tags: int
    bytes: int

    def line(self, out: Path) -> str:
        def day(ts: int) -> str:
            return datetime.fromtimestamp(ts, timezone.utc).date().isoformat()

        return (
            f"Published {day(self.start)} → {day(self.end)}: {self.plays:,} plays, {self.tracks:,} tracks, "
            f"{self.artists:,} artists → {out} ({self.bytes / 1e6:.1f} MB)"
        )


def window(window_days: int, lag_days: int, now: float | None = None) -> tuple[int, int]:
    """[start, end) in Unix seconds: `window_days` long, ending `lag_days` before `now`."""
    end = int(now if now is not None else time.time()) - lag_days * DAY
    return end - window_days * DAY, end


def publish(db_path: Path, out: Path, window_days: int = 730, lag_days: int = 7, now: float | None = None) -> PublishStats:
    if not db_path.exists():
        raise SystemExit(f"No database at {db_path}. Run `rain-in-my-head build` first.")
    start, end = window(window_days, lag_days, now)
    tmp = out.with_name(out.name + ".tmp")
    tmp.unlink(missing_ok=True)

    conn = sqlite3.connect(f"file:{tmp}", uri=True)  # uri=True so ATTACH can open the source read-only
    try:
        conn.executescript(SCHEMA.read_text())  # same schema.sql, so the views match the full database exactly
        conn.execute("ATTACH ? AS src", (f"file:{db_path}?mode=ro",))
        with conn:
            conn.execute(
                "INSERT INTO scrobbles SELECT * FROM src.scrobbles WHERE played_at >= ? AND played_at < ?", (start, end)
            )
            conn.execute("INSERT INTO tracks SELECT * FROM src.tracks WHERE track_key IN (SELECT track_key FROM scrobbles)")
            for table in ("artists", "artist_tags"):
                conn.execute(
                    f"INSERT INTO {table} SELECT * FROM src.{table} WHERE artist_key IN (SELECT artist_key FROM scrobbles)"  # noqa: S608 table names come from a fixed tuple
                )
            conn.execute("DROP TABLE spotify_matches")
        conn.execute("DETACH src")
        counts = [conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("scrobbles", "tracks", "artists", "artist_tags")]  # noqa: S608 table names come from a fixed tuple
        conn.execute("VACUUM")
    except sqlite3.Error:
        conn.close()
        tmp.unlink(missing_ok=True)
        raise
    conn.close()
    os.replace(tmp, out)
    return PublishStats(start, end, *counts, out.stat().st_size)
