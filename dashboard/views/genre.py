"""Genre page: the artists in one genre by plays, and your songs by a selected artist.

Opened by clicking a genre chart on the Overview, which passes `genre`, `start` and `end`
(ISO dates) as query parameters. Without a range it covers all time.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from rain_in_my_head import config
from rain_in_my_head import genre as gn


@st.cache_data
def genres(db_mtime: float) -> list[str]:
    return gn.genres(config.DB_PATH)


@st.cache_data
def load(db_mtime: float, genre: str, start: str, end: str) -> pd.DataFrame:
    return gn.genre_plays(config.DB_PATH, genre, start, end)


if not config.DB_PATH.exists():
    st.title("Genre")
    st.info("No database yet. Run `uv run rain-in-my-head fetch` then `uv run rain-in-my-head build`.")
    st.stop()

mtime = config.DB_PATH.stat().st_mtime
all_genres = genres(mtime)
if not all_genres:
    st.title("Genre")
    st.info("Run `uv run rain-in-my-head enrich` to add genres (Last.fm tags).")
    st.stop()

params = st.query_params
start = params.get("start", gn.ALL_TIME_START)
end = params.get("end", date.today().isoformat())
asked = params.get("genre")

st.page_link("views/overview.py", label="Overview", icon=":material/arrow_back:")
genre = st.selectbox("Genre", all_genres, index=all_genres.index(asked) if asked in all_genres else 0)
st.query_params["genre"] = genre

plays = load(mtime, genre, start, end)
st.title(genre.title())
range_label = gn.range_label(params.get("start"), end)
st.caption(f"{range_label} · {len(plays):,} plays · artists whose top Last.fm tag is “{genre}”")

if plays.empty:
    st.warning("No plays in this genre for this range.")
    st.stop()

artists = gn.artists(plays)

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
            art_col.image(gn.thumb(artist["art"], "174s"), width="stretch")
        info_col.subheader(artist["name"])
        info_col.caption(f"{artist['plays']:,} plays in {genre}")

        songs = gn.songs(plays, artist["artist_key"])
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
