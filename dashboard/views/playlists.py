"""Build Spotify playlists from your history: time-slot favourites, a year's discoveries, or binges."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta

import pandas as pd
import streamlit as st

from rain_in_my_head import config
from rain_in_my_head.build import connect
from rain_in_my_head.playlist import (
    BINGE_ORDERS, WEEKDAY_FULL, Slot, binge_tracks, binges, discoveries, format_span, match_tracks,
    order_binge_episodes, order_binge_tracks, rank_tracks,
)

st.title("Playlists")

if not config.DB_PATH.exists():
    st.info("No database yet. Run `uv run listening build` first.")
    st.stop()

conn = sqlite3.connect(config.DB_PATH, timeout=30)
first, last = conn.execute("SELECT MIN(date(played_local)), MAX(date(played_local)) FROM v_plays").fetchone()
first, last = pd.Timestamp(first).date(), pd.Timestamp(last).date()

kind = st.segmented_control(
    "Playlist type", ["Time slot", "Discoveries by year", "Binged songs"], default="Time slot"
) or "Time slot"


@dataclass
class Spec:
    ranked: pd.DataFrame  # one row per track, in the order to try matching on Spotify
    size: int
    name: str
    description: str
    columns: dict  # column -> st.column_config for the preview table
    display: pd.DataFrame | None = None  # preview rows, if not simply ranked.head(size)
    # Reorders matched tracks before creating. Matching always walks `ranked`, so a song with no
    # Spotify match is replaced by the next-ranked one and the requested order still holds.
    reorder: Callable[[pd.DataFrame], pd.DataFrame] | None = None


def time_slot() -> Spec:
    st.caption(
        "Tracks you play *more than usual* in a time slot, compared with your listening overall. "
        "Tracks with only a few plays are weighted down so one-offs don't dominate."
    )
    c1, c2 = st.columns([3, 2])
    with c1:
        days = st.multiselect("Days", WEEKDAY_FULL, default=["Friday"])
        hours = st.slider("Hours (local time)", 0, 24, (17, 19), format="%d:00",
                          help="End is exclusive: 17–19 means 5:00pm to 6:59pm.")
    with c2:
        span = st.radio("Listening from", ["All time", "Last 5 years", "Last 2 years", "Custom"], horizontal=True)
        if span == "All time":
            since, until = None, None
        elif span == "Custom":
            picked = st.date_input("Dates", (first, last), first, last)
            since, until = (picked if len(picked) == 2 else (picked[0], last))
        else:
            since, until = last - timedelta(days=365 * int(span.split()[1])), None
        size = st.slider("Playlist length", 10, 100, 50, step=5)
        min_plays = st.slider("Min. plays in the slot", 1, 10, 3,
                              help="Higher = only tracks you've played in this slot repeatedly.")
    if not days:
        st.warning("Pick at least one day.")
        st.stop()
    if hours[0] == hours[1]:
        st.warning("Pick an hour range of at least one hour.")
        st.stop()

    slot = Slot([WEEKDAY_FULL.index(d) for d in days], hours[0], hours[1], since, until)
    ranked = rank_tracks(conn, slot, min_plays)
    st.subheader(slot.label())
    if ranked.empty:
        st.warning("No tracks stand out in this slot. Try a wider slot or a lower minimum plays.")
        st.stop()
    if len(ranked) < size and min_plays > 1:
        st.info(f"Fewer than {size} tracks qualify. Lower **Min. plays in the slot** or widen the slot to get more.")
    columns = {
        "artist": "Artist", "track": "Track",
        "slot_plays": st.column_config.NumberColumn("Plays in slot"),
        "total_plays": st.column_config.NumberColumn("Plays overall"),
        "lift": st.column_config.NumberColumn("× more than usual", format="%.1f×"),
        "last_played": "Last played",
    }
    return Spec(ranked, size, slot.label(), slot.describe(), columns)


def year_discoveries() -> Spec:
    st.caption("Songs you heard for the first time in a given year.")
    years = list(range(last.year, first.year - 1, -1))
    c1, c2 = st.columns([3, 2])
    with c1:
        year = st.selectbox("Year", years, index=min(1, len(years) - 1))
        rank_by = st.radio(
            "Pick the songs",
            ["year", "ever"],
            format_func={"year": "Most played that year (what hooked you)",
                         "ever": "Most played since (the ones that stuck)"}.get,
        )
        order = st.radio("Playlist order", ["Ranking", "Order discovered"], horizontal=True)
    with c2:
        size = st.slider("Playlist length", 10, 100, 50, step=5)
        min_plays = st.slider("Min. plays", 1, 10, 2, help="Drop songs you only heard once.")
    if year <= first.year + 1:
        st.info(
            f"Your Last.fm history starts {first:%B %Y}, so {year}'s \"discoveries\" include older "
            "favourites heard for the first time *on Last.fm*."
        )

    ranked = discoveries(conn, year, min_plays, rank_by)
    st.subheader(f"Discovered in {year}")
    if ranked.empty:
        st.warning("No songs qualify. Try a lower minimum plays.")
        st.stop()
    columns = {
        "artist": "Artist", "track": "Track",
        "first_played": st.column_config.DatetimeColumn("First played", format="D MMM YYYY"),
        "year_plays": st.column_config.NumberColumn(f"Plays in {year}"),
        "total_plays": st.column_config.NumberColumn("Plays ever"),
        "last_played": "Last played",
    }
    name = f"Discovered in {year}"
    desc = f"Songs I first heard in {year}, picked by {'plays that year' if rank_by == 'year' else 'plays since'}."
    # Match in ranking order (so misses are replaced by the next best), then play in discovery order.
    by_date = order == "Order discovered"
    display = ranked.head(size).sort_values("first_played") if by_date else None
    return Spec(ranked, size, name, desc + " Made from my Last.fm history.", columns, display,
                (lambda hits: hits.sort_values("first_played")) if by_date else None)


def binged() -> Spec:
    st.caption("Songs you played on repeat in a short burst. Every binge is listed with its dates.")
    c1, c2 = st.columns([3, 2])
    with c1:
        years = st.slider("Years", first.year, last.year, (first.year, last.year))
        window_days = st.radio("Binge window", [1, 7, 30], index=1, horizontal=True,
                               format_func=lambda d: "1 day" if d == 1 else f"{d} days")
        min_plays = st.slider("Min. plays in the window", 3, 30, 8,
                              help="A binge = at least this many plays of one song within the window.")
    with c2:
        size = st.slider("Playlist length", 10, 100, 50, step=5)
        order = st.radio("Playlist order", list(BINGE_ORDERS), horizontal=True,
                         format_func={"oldest": "Oldest first", "newest": "Newest first",
                                      "biggest": "Biggest binge first"}.get)

    episodes = load_binges(min_plays, window_days, years[0], years[1], config.DB_PATH.stat().st_mtime)
    ranked = binge_tracks(episodes)
    span = str(years[0]) if years[0] == years[1] else f"{years[0]}–{years[1]}"
    st.subheader(f"Binged songs, {span}")
    if ranked.empty:
        st.warning("No binges with these settings. Lower the minimum plays or widen the window.")
        st.stop()
    chosen = set(ranked.head(size)["track_key"])
    display = episodes[episodes["track_key"].isin(chosen)].assign(
        when=lambda d: [format_span(a, b) for a, b in zip(d["start"], d["end"])]
    )
    display = order_binge_episodes(display, order)
    st.caption(f"{len(episodes):,} binges across {len(ranked):,} songs; showing the top {min(size, len(ranked))} songs.")
    columns = {
        "when": "When", "artist": "Artist", "track": "Track",
        "plays": st.column_config.NumberColumn("Plays in binge"),
        "binge_count": st.column_config.NumberColumn("Binges", help="How many separate times you binged this song"),
        "total_plays": st.column_config.NumberColumn("Plays ever"),
    }
    window = "a day" if window_days == 1 else f"{window_days} days"
    ordering = BINGE_ORDERS[order]
    description = f"Songs I played {min_plays}+ times within {window}, {ordering}. Made from my Last.fm history."
    full_range = (years[0], years[1]) == (first.year, last.year)
    return Spec(ranked, size, "Binged" if full_range else f"Binged {span}", description, columns,
                display, lambda hits: order_binge_tracks(hits, order))


@st.cache_data(show_spinner="Finding binges…")
def load_binges(min_plays: int, window_days: int, since: int, until: int, db_mtime: float) -> pd.DataFrame:
    with sqlite3.connect(config.DB_PATH, timeout=30) as c:
        return binges(c, min_plays, window_days, since, until)


spec = {"Time slot": time_slot, "Discoveries by year": year_discoveries, "Binged songs": binged}[kind]()
ranked, size = spec.ranked, spec.size
if kind != "Binged songs":
    st.caption(f"{len(ranked):,} candidate tracks; the top {min(size, len(ranked))} are shown.")
preview = spec.display if spec.display is not None else ranked.head(size)
st.dataframe(preview[list(spec.columns)], column_config=spec.columns, hide_index=True, width="stretch")

# ---- Spotify -----------------------------------------------------------------
st.subheader("Create on Spotify")
if not config.SPOTIFY_TOKEN_PATH.exists():
    st.info(
        "Connect Spotify once from the terminal: add `SPOTIFY_CLIENT_ID` to `.env`, then run "
        "`uv run listening spotify-login`. See the README for creating the Spotify app."
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
        matched = match_tracks(conn, client, ranked, size, progress=lambda f, msg: bar.progress(f, msg))
        hits = matched[matched["spotify_uri"].notna()]
        if spec.reorder:
            hits = spec.reorder(hits)
        url = client.create_playlist(name, spec.description, list(hits["spotify_uri"]), public=public)
    except (SpotifyAuthError, SystemExit) as e:
        st.error(str(e))
    else:
        bar.empty()
        st.success(f"Created **{name}** with {len(hits)} tracks: [open in Spotify]({url})")
        misses = matched[matched["spotify_uri"].isna()]
        if not misses.empty:
            with st.expander(f"{len(misses)} tracks had no Spotify match and were skipped"):
                st.dataframe(misses[["artist", "track"]], hide_index=True, width="stretch")
