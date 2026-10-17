"""Genre page: the artists in one genre by plays, and your songs by a selected artist.

Opened by clicking a genre chart on the Overview, which passes `genre`, `start` and `end`
(ISO dates) as query parameters. Without a range it covers all time.
"""

from __future__ import annotations

import sqlite3
from datetime import date

import pandas as pd
import streamlit as st

from rain_in_my_head import config

# Last.fm's grey-star "no image" picture.
PLACEHOLDER = "2a96cbd8b46e442fc41c2b86b821562f"


def thumb(url: str, size: str = "64s") -> str:
    """Smaller Last.fm image for table rows (sizes: 34s, 64s, 174s, 300x300)."""
    return url.replace("/300x300/", f"/{size}/")


@st.cache_data
def genres(db_mtime: float) -> list[str]:
    with sqlite3.connect(config.DB_PATH) as conn:
        rows = conn.execute(
            """SELECT g.primary_genre FROM scrobbles s JOIN v_artist_genre g USING (artist_key)
               GROUP BY g.primary_genre ORDER BY COUNT(*) DESC"""
        ).fetchall()
    return [r[0] for r in rows]


@st.cache_data
def load(db_mtime: float, genre: str, start: str, end: str) -> pd.DataFrame:
    with sqlite3.connect(config.DB_PATH) as conn:
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


if not config.DB_PATH.exists():
    st.title("Genre")
    st.info("No database yet. Run `uv run listening fetch` then `uv run listening build`.")
    st.stop()

mtime = config.DB_PATH.stat().st_mtime
all_genres = genres(mtime)
if not all_genres:
    st.title("Genre")
    st.info("Run `uv run listening enrich` to add genres (Last.fm tags).")
    st.stop()

params = st.query_params
start = params.get("start", "2000-01-01")
end = params.get("end", date.today().isoformat())
asked = params.get("genre")

st.page_link("views/overview.py", label="Overview", icon=":material/arrow_back:")
genre = st.selectbox("Genre", all_genres, index=all_genres.index(asked) if asked in all_genres else 0)
st.query_params["genre"] = genre

plays = load(mtime, genre, start, end)
st.title(genre.title())
range_label = "All time" if "start" not in params else f"{date.fromisoformat(start):%d %b %Y} – {date.fromisoformat(end):%d %b %Y}"
st.caption(f"{range_label} · {len(plays):,} plays · artists whose top Last.fm tag is “{genre}”")

if plays.empty:
    st.warning("No plays in this genre for this range.")
    st.stop()

artists = ranked(plays, "artist_key", "artist_name")
artists["thumb"] = artists["art"].map(thumb, na_action="ignore")

left, right = st.columns(2, gap="large")
with left:
    st.subheader("Artists")
    picked = st.dataframe(
        artists[["thumb", "name", "plays"]],
        column_config={
            "thumb": st.column_config.ImageColumn("", width="small"),
            "name": "Artist",
            "plays": st.column_config.NumberColumn("Plays", format="%d"),
        },
        hide_index=True,
        row_height=56,
        height=640,
        on_select="rerun",
        # Cell selection makes clicking anywhere in a row pick that artist, not just its checkbox.
        selection_mode=["single-row", "single-cell"],
        key=f"artists-{genre}-{start}-{end}",
    )
    st.caption("Click an artist to see your songs by them.")

with right:
    rows = picked.selection.rows or [row for row, _ in picked.selection.cells]
    if not rows:
        st.subheader("Songs")
        st.info("Click an artist on the left.")
    else:
        artist = artists.iloc[rows[0]]
        art_col, info_col = st.columns([1, 3], vertical_alignment="center")
        if pd.notna(artist["art"]):
            art_col.image(thumb(artist["art"], "174s"), width="stretch")
        info_col.subheader(artist["name"])
        info_col.caption(f"{artist['plays']:,} plays in {genre}")

        songs = ranked(plays[plays["artist_key"] == artist["artist_key"]], "track_key", "track_name")
        albums = plays.groupby("track_key")["album_name"].agg(most_common)
        songs = songs.join(albums, on="track_key").assign(thumb=lambda d: d["art"].map(thumb, na_action="ignore"))
        st.dataframe(
            songs[["thumb", "name", "album_name", "plays"]],
            column_config={
                "thumb": st.column_config.ImageColumn("", width="small"),
                "name": "Song",
                "album_name": "Album",
                "plays": st.column_config.NumberColumn("Plays", format="%d"),
            },
            hide_index=True,
            row_height=56,
            height=520,
        )
