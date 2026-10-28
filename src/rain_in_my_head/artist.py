"""The Overview's new-artists list and the Artist page, shared by the Streamlit pages and the API.

Built on the ranking helpers in rain_in_my_head.genre, so art, names and counts are picked the same
way as on the Genre page. Reads `scrobbles` (which has `image_url`; `v_plays` doesn't) with the same
filters as `genre_plays`. Spec: specs/001-new-artist-page/.
"""

from __future__ import annotations

import base64
from contextlib import closing
from dataclasses import dataclass
from datetime import date
from functools import cache
from pathlib import Path

import pandas as pd

from rain_in_my_head import config
from rain_in_my_head import genre as gn
from rain_in_my_head.build import MIN_PLAYED_AT, connect_readonly
from rain_in_my_head.genre import PLAY_COLUMNS

# Missing-art image for both dashboards: the TypeScript app serves it as /no-art.svg.
NO_ART_PATH = config.ROOT / "web" / "public" / "no-art.svg"


@cache
def no_art_url() -> str:
    """The missing-art image as a data URL, for Streamlit image columns and st.image."""
    return "data:image/svg+xml;base64," + base64.b64encode(NO_ART_PATH.read_bytes()).decode()


def period_label(start: date, end: date) -> str:
    """'Oct 2026' for a period from the 1st within one month (even a partial one), '2026' from
    1 January within one year, else 'DD Mon YYYY – DD Mon YYYY'."""
    if start.day == 1 and (start.year, start.month) == (end.year, end.month):
        return f"{start:%b %Y}"
    if (start.month, start.day) == (1, 1) and start.year == end.year:
        return f"{start:%Y}"
    return f"{start:%d %b %Y} – {end:%d %b %Y}"


def list_period(start: date, end: date, selected: bool) -> tuple[date, date]:
    """The list's period: the selected over-time period, else the last month the range reaches."""
    return (start, end) if selected else (max(start, end.replace(day=1)), end)


def new_artists(db_path: Path, start: date, end: date) -> pd.DataFrame:
    """Artists whose first play ever is in the period, ranked by plays in it.

    Columns: artist_key, name, art, plays, thumb (art and thumb are None without art)."""
    with closing(connect_readonly(db_path)) as conn:
        plays = pd.read_sql(
            f"""WITH firsts AS (
                    SELECT artist_key FROM scrobbles WHERE played_at >= {MIN_PLAYED_AT}
                    GROUP BY artist_key
                    HAVING date(MIN(played_at), 'unixepoch', 'localtime') BETWEEN :start AND :end)
                SELECT {PLAY_COLUMNS}
                FROM scrobbles s JOIN firsts USING (artist_key)
                WHERE s.played_at >= {MIN_PLAYED_AT}
                  AND date(s.played_at, 'unixepoch', 'localtime') BETWEEN :start AND :end""",
            conn,
            params={"start": start.isoformat(), "end": end.isoformat()},
        )
    if plays.empty:
        return pd.DataFrame(columns=["artist_key", "name", "art", "plays", "thumb"])
    return gn.artists(plays)


@dataclass
class ArtistPage:
    artist_key: str
    name: str
    cover: str | None  # 300px art: the period's most common, else all time's
    period: tuple[date, date] | None  # None means all time
    period_plays: int
    all_time_plays: int
    songs: pd.DataFrame  # track_key, name, album_name, art, thumb, plays; most played first

    @property
    def label(self) -> str | None:
        return None if self.period is None else period_label(*self.period)


def artist_page(db_path: Path, artist_key: str, start: date | None, end: date | None) -> ArtistPage | None:
    """One artist's header counts and songs in the period (all time without one). None if they have no plays."""
    with closing(connect_readonly(db_path)) as conn:
        plays = pd.read_sql(
            f"SELECT {PLAY_COLUMNS} FROM scrobbles s WHERE s.artist_key = ? AND s.played_at >= {MIN_PLAYED_AT}",
            conn,
            params=(artist_key,),
        )
    if plays.empty:
        return None
    period = (start, end) if start is not None and end is not None else None
    in_period = plays if period is None else plays[plays["day"].between(start.isoformat(), end.isoformat())]
    songs = (
        gn.songs(in_period, artist_key) if not in_period.empty
        else pd.DataFrame(columns=["track_key", "name", "album_name", "art", "thumb", "plays"])
    )
    return ArtistPage(
        artist_key=artist_key,
        name=gn.most_common(plays["artist_name"]),
        cover=gn.most_common(in_period["image_url"]) or gn.most_common(plays["image_url"]),
        period=period,
        period_plays=len(in_period),
        all_time_plays=len(plays),
        songs=songs,
    )
