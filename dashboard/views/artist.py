"""Artist page: your songs by one artist in a period, opened from the Overview's "New artists" list.

Query parameters: `artist` (artist_key), `start` and `end` (ISO dates); without a period it covers
all time. Hidden from the menu. Contract: specs/001-new-artist-page/contracts/artist-page.md
"""

from __future__ import annotations

from datetime import date

import streamlit as st

from rain_in_my_head import artist as ar
from rain_in_my_head import config


def parse(value: str | None) -> date | None:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


@st.cache_data
def load(db_mtime: float, artist: str, start: date | None, end: date | None) -> ar.ArtistPage | None:
    return ar.artist_page(config.DB_PATH, artist, start, end)


st.page_link("views/overview.py", label="Overview", icon=":material/arrow_back:")

if not config.DB_PATH.exists():
    st.title("Artist")
    st.info("No database yet. Run `uv run rain-in-my-head fetch` then `uv run rain-in-my-head build`.")
    st.stop()

params = st.query_params
key = params.get("artist")
page = load(config.DB_PATH.stat().st_mtime, key, parse(params.get("start")), parse(params.get("end"))) if key else None
if page is None:
    st.title("Artist")
    st.info("No plays found for this artist. Open one from the “New artists” list on the Overview.")
    st.stop()

cover_col, info_col = st.columns([1, 3], vertical_alignment="center")
cover_col.image(page.cover or ar.no_art_url(), width="stretch")
info_col.title(page.name)
if page.label is None:
    info_col.caption(f"{page.all_time_plays:,} plays · all time")
else:
    info_col.caption(f"{page.period_plays:,} plays in {page.label} · {page.all_time_plays:,} all time")

st.subheader("Songs")
if page.songs.empty:
    st.info(f"No plays by {page.name} in {page.label}.")
else:
    st.dataframe(
        page.songs.assign(thumb=page.songs["thumb"].fillna(ar.no_art_url()))[["thumb", "name", "album_name", "plays"]],
        column_config={
            "thumb": st.column_config.ImageColumn("", width="small"),
            "name": "Song",
            "album_name": "Album",
            "plays": st.column_config.NumberColumn("Plays", format="%d"),
        },
        hide_index=True,
        row_height=56,
        height=min(640, 38 + 56 * len(page.songs)),
    )
