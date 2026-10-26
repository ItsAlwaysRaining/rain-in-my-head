"""Build Spotify playlists from your history: time-slot favourites, a year's discoveries, or binges."""

from __future__ import annotations

import sqlite3

import pandas as pd
import streamlit as st

from rain_in_my_head import config
from rain_in_my_head import playlist as pl
from rain_in_my_head.build import connect

st.title("Playlists")

if not config.DB_PATH.exists():
    st.info("No database yet. Run `uv run rain-in-my-head build` first.")
    st.stop()

conn = sqlite3.connect(config.DB_PATH, timeout=30)
first, last = pl.play_bounds(conn)

kind = st.segmented_control(
    "Playlist type", ["Time slot", "Discoveries by year", "Binged songs"], default="Time slot"
) or "Time slot"


def time_slot() -> pl.Preview:
    st.caption(
        "Tracks you play *more than usual* in a time slot, compared with your listening overall. "
        "Tracks with only a few plays are weighted down so one-offs don't dominate."
    )
    c1, c2 = st.columns([3, 2])
    with c1:
        days = st.multiselect("Days", pl.WEEKDAY_FULL, default=["Friday"])
        hours = st.slider("Hours (local time)", 0, 24, (17, 19), format="%d:00",
                          help="End is exclusive: 17–19 means 5:00pm to 6:59pm.")
    with c2:
        span = st.radio("Listening from", pl.SPANS, horizontal=True)
        custom = None
        if span == "Custom":
            picked = st.date_input("Dates", (first, last), first, last)
            custom = picked if len(picked) == 2 else (picked[0], last)
        size = st.slider("Playlist length", 10, 100, 50, step=5)
        min_plays = st.slider("Min. plays in the slot", 1, 10, 3,
                              help="Higher = only tracks you've played in this slot repeatedly.")
    return pl.preview_slot(conn, first, last, days, hours, span, custom, size, min_plays)


def year_discoveries() -> pl.Preview:
    st.caption("Songs you heard for the first time in a given year.")
    years = list(range(last.year, first.year - 1, -1))
    c1, c2 = st.columns([3, 2])
    with c1:
        year = st.selectbox("Year", years, index=min(1, len(years) - 1))
        rank_by = st.radio("Pick the songs", list(pl.RANK_BY), format_func=pl.RANK_BY.get)
        order = st.radio("Playlist order", pl.DISCOVERY_ORDERS, horizontal=True)
    with c2:
        size = st.slider("Playlist length", 10, 100, 50, step=5)
        min_plays = st.slider("Min. plays", 1, 10, 2, help="Drop songs you only heard once.")
    return pl.preview_discoveries(conn, first, year, rank_by, order, size, min_plays)


def binged() -> pl.Preview:
    st.caption("Songs you played on repeat in a short burst. Every binge is listed with its dates.")
    c1, c2 = st.columns([3, 2])
    with c1:
        years = st.slider("Years", first.year, last.year, (first.year, last.year))
        window_days = st.radio("Binge window", pl.WINDOWS, index=1, horizontal=True,
                               format_func=lambda d: "1 day" if d == 1 else f"{d} days")
        min_plays = st.slider("Min. plays in the window", 3, 30, 8,
                              help="A binge = at least this many plays of one song within the window.")
    with c2:
        size = st.slider("Playlist length", 10, 100, 50, step=5)
        order = st.radio("Playlist order", list(pl.BINGE_ORDERS), horizontal=True, format_func=pl.BINGE_ORDER_LABELS.get)
    episodes = load_binges(min_plays, window_days, years[0], years[1], config.DB_PATH.stat().st_mtime)
    return pl.preview_binges(episodes, first, last, years, window_days, min_plays, size, order)


@st.cache_data(show_spinner="Finding binges…")
def load_binges(min_plays: int, window_days: int, since: int, until: int, db_mtime: float) -> pd.DataFrame:
    with sqlite3.connect(config.DB_PATH, timeout=30) as c:
        return pl.binges(c, min_plays, window_days, since, until)


def column_config(col: pl.Column):
    if col.kind == "number":
        return st.column_config.NumberColumn(col.label, help=col.help)
    if col.kind == "lift":
        return st.column_config.NumberColumn(col.label, format="%.1f×")
    if col.kind == "date":
        return st.column_config.DatetimeColumn(col.label, format="D MMM YYYY")
    return col.label


spec = {"Time slot": time_slot, "Discoveries by year": year_discoveries, "Binged songs": binged}[kind]()
if spec.note:
    st.info(spec.note)
if spec.title:
    st.subheader(spec.title)
if spec.warning:
    st.warning(spec.warning)
    st.stop()
if spec.info:
    st.info(spec.info)
st.caption(spec.caption)
st.dataframe(spec.rows[list(spec.columns)], column_config={k: column_config(c) for k, c in spec.columns.items()},
             hide_index=True, width="stretch")

# ---- Spotify -----------------------------------------------------------------
st.subheader("Create on Spotify")
if not config.SPOTIFY_TOKEN_PATH.exists():
    st.info(
        "Connect Spotify once from the terminal: add `SPOTIFY_CLIENT_ID` to `.env`, then run "
        "`uv run rain-in-my-head spotify-login`. See the README for creating the Spotify app."
    )
    st.stop()

name = st.text_input("Playlist name", spec.name, key=f"name_{spec.name}")
public = st.toggle("Public playlist", value=False)
if st.button("Create playlist", type="primary"):
    from rain_in_my_head.spotify import SpotifyAuthError, SpotifyClient

    try:
        client = SpotifyClient(config.spotify_client_id(), config.SPOTIFY_TOKEN_PATH)
        conn = connect(config.DB_PATH)  # ensures the spotify_matches cache table exists
        bar = st.progress(0.0, "Matching tracks on Spotify…")
        url, hits, misses = pl.create_on_spotify(
            conn, client, spec.ranked, spec.size, name, spec.description, spec.reorder, public=public,
            progress=lambda f, msg: bar.progress(f, msg),
        )
    except (SpotifyAuthError, SystemExit) as e:
        st.error(str(e))
    else:
        bar.empty()
        st.success(f"Created **{name}** with {len(hits)} tracks: [open in Spotify]({url})")
        if not misses.empty:
            with st.expander(f"{len(misses)} tracks had no Spotify match and were skipped"):
                st.dataframe(misses[["artist", "track"]], hide_index=True, width="stretch")
