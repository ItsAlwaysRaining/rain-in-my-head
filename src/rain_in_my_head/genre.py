"""Data for the Genre page, shared by the Streamlit view (dashboard/views/genre.py) and the API.

The artists in one genre by plays, and your songs by one of those artists. Pure functions: no
Streamlit import, so both dashboards get identical lists.
"""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd

# Last.fm's grey-star "no image" picture.
PLACEHOLDER = "2a96cbd8b46e442fc41c2b86b821562f"
ALL_TIME_START = "2000-01-01"


def thumb(url: str, size: str = "64s") -> str:
    """Smaller Last.fm image for table rows (sizes: 34s, 64s, 174s, 300x300)."""
    return url.replace("/300x300/", f"/{size}/")


def genres(db_path: Path) -> list[str]:
    """Every primary genre, most played first."""
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """SELECT g.primary_genre FROM scrobbles s JOIN v_artist_genre g USING (artist_key)
               GROUP BY g.primary_genre ORDER BY COUNT(*) DESC"""
        ).fetchall()
    return [r[0] for r in rows]


def genre_plays(db_path: Path, genre: str, start: str, end: str) -> pd.DataFrame:
    """One row per play of an artist whose primary genre is `genre`, between ISO dates `start` and `end`."""
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql(
            """SELECT s.artist_key, s.artist_name, s.track_key, s.track_name, s.album_name,
                      CASE WHEN s.image_url LIKE ? THEN NULL ELSE s.image_url END AS image_url
               FROM scrobbles s JOIN v_artist_genre g USING (artist_key)
               WHERE g.primary_genre = ?
                 AND s.played_at >= 946684800  -- same placeholder-timestamp cut as v_plays
                 AND date(s.played_at, 'unixepoch', 'localtime') BETWEEN ? AND ?""",
            conn,
            params=(f"%{PLACEHOLDER}%", genre, start, end),
        )


def range_label(start: str | None, end: str) -> str:
    """'All time' when no start was given, else 'DD Mon YYYY – DD Mon YYYY'."""
    if start is None:
        return "All time"
    return f"{date.fromisoformat(start):%d %b %Y} – {date.fromisoformat(end):%d %b %Y}"


def most_common(s: pd.Series):
    s = s.dropna()
    return s.mode().iloc[0] if not s.empty else None


def ranked(df: pd.DataFrame, key: str, name: str) -> pd.DataFrame:
    """One row per `key`: its most common name and album art, and play count, most played first."""
    return (
        df.groupby(key)
        .agg(name=(name, most_common), art=("image_url", most_common), plays=(key, "size"))
        .sort_values(["plays", "name"], ascending=[False, True])
        .reset_index()
    )


def artists(plays: pd.DataFrame) -> pd.DataFrame:
    """The artists in `plays`, ranked, with a `thumb` column for table rows."""
    df = ranked(plays, "artist_key", "artist_name")
    df["thumb"] = df["art"].map(thumb, na_action="ignore")
    return df


def songs(plays: pd.DataFrame, artist_key: str) -> pd.DataFrame:
    """Your songs by one artist in `plays`, ranked, each with its most common album and a `thumb`."""
    df = ranked(plays[plays["artist_key"] == artist_key], "track_key", "track_name")
    albums = plays.groupby("track_key")["album_name"].agg(most_common)
    return df.join(albums, on="track_key").assign(thumb=lambda d: d["art"].map(thumb, na_action="ignore"))
