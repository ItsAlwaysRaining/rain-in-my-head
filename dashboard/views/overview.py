"""Overview page: listening stats over data/listening.db."""

from __future__ import annotations

import sqlite3
from datetime import timedelta

import altair as alt
import pandas as pd
import streamlit as st

from listening import config


# Chart steps of the theme palette (see .streamlit/config.toml): iris = plays, teal = discovery.
IRIS, TEAL = "#7F77D6", "#0E9A94"
IRIS_RAMP = ["#1D1C34", "#2B284D", "#393567", "#484383", "#58519E", "#6B63BC", "#7F78D6", "#948FE8", "#AAA8F1", "#C2C1F7"]
BAR = {"cornerRadiusEnd": 4, "color": IRIS}

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
LISTENER_BUCKETS = [0, 10_000, 100_000, 1_000_000, 5_000_000, float("inf")]
LISTENER_LABELS = ["<10k", "10k–100k", "100k–1M", "1M–5M", "5M+"]


@st.cache_data
def load(db_mtime: float) -> pd.DataFrame:
    with sqlite3.connect(config.DB_PATH) as conn:
        df = pd.read_sql("SELECT * FROM v_plays", conn)
    df["played_local"] = pd.to_datetime(df["played_local"])
    df["date"] = df["played_local"].dt.normalize()
    # SQLite weekday is 0 = Sunday; shift to 0 = Monday.
    df["weekday_name"] = pd.Categorical(
        [WEEKDAYS[(w - 1) % 7] for w in df["weekday"]], categories=WEEKDAYS, ordered=True
    )
    df["artist_first_play"] = df.groupby("artist_key")["played_local"].transform("min")
    return df


def top_bar(df: pd.DataFrame, field: str, title: str, n: int = 20) -> alt.Chart:
    counts = df.groupby(field).size().nlargest(n).rename("plays").reset_index()
    return (
        alt.Chart(counts, title=title)
        .mark_bar(**BAR)
        .encode(
            x=alt.X("plays:Q", title="Plays"),
            y=alt.Y(f"{field}:N", sort="-x", title=None, axis=alt.Axis(labelLimit=320, labelOverlap=False)),
            tooltip=[field, "plays"],
        )
        .properties(height=max(200, 26 * len(counts)))
    )


def kpis(cur: pd.DataFrame) -> dict[str, float]:
    return {
        "Scrobbles": len(cur),
        "Hours (est.)": cur["est_minutes"].sum() / 60,
        "Tracks": cur["track_key"].nunique(),
        "Artists": cur["artist_key"].nunique(),
        "Albums": cur["album_name"].nunique(),
    }


if not config.DB_PATH.exists():
    st.title("Listening")
    st.info("No database yet. Run `uv run listening fetch` then `uv run listening build`.")
    st.stop()

data = load(config.DB_PATH.stat().st_mtime)
if data.empty:
    st.info("The database has no scrobbles yet. Run `uv run listening fetch` and `uv run listening build`.")
    st.stop()

# ---- Sidebar filters -------------------------------------------------------
first_day, last_day = data["date"].min().date(), data["date"].max().date()
with st.sidebar:
    st.header("Filters")
    preset = st.radio("Range", ["Last 30 days", "Last 12 months", "This year", "All time", "Custom"], index=1)
    if preset == "Last 30 days":
        start, end = last_day - timedelta(days=29), last_day
    elif preset == "Last 12 months":
        start, end = last_day - timedelta(days=364), last_day
    elif preset == "This year":
        start, end = last_day.replace(month=1, day=1), last_day
    elif preset == "All time":
        start, end = first_day, last_day
    else:
        picked = st.date_input("Dates", (last_day - timedelta(days=364), last_day), first_day, last_day)
        start, end = (picked if len(picked) == 2 else (picked[0], picked[0]))
    start = max(start, first_day)
    grain = st.radio("Time grain", ["Week", "Month", "Year"], index=1, horizontal=True)

in_range = data["date"].between(pd.Timestamp(start), pd.Timestamp(end))
df = data[in_range]
span = pd.Timestamp(end) - pd.Timestamp(start)
prev = data[data["date"].between(pd.Timestamp(start) - span - pd.Timedelta(days=1), pd.Timestamp(start) - pd.Timedelta(days=1))]

st.title("Listening")
st.caption(f"{start:%d %b %Y} – {end:%d %b %Y} · data through {data['played_local'].max():%d %b %Y %H:%M}")

if df.empty:
    st.warning("No scrobbles in this range.")
    st.stop()

# ---- KPIs ------------------------------------------------------------------
cur_k, prev_k = kpis(df), kpis(prev)
for col, (label, value) in zip(st.columns(len(cur_k)), cur_k.items()):
    delta = None
    if not prev.empty and prev_k[label]:
        delta = f"{(value - prev_k[label]) / prev_k[label]:+.0%}"
    col.metric(label, f"{value:,.0f}", delta, help="Change vs. the previous period of equal length")

# ---- Over time -------------------------------------------------------------
freq = {"Week": "W-MON", "Month": "MS", "Year": "YS"}[grain]
label_fmt = {"Week": "%d %b %Y", "Month": "%b %Y", "Year": "%Y"}[grain]
over_time = (
    df.groupby(pd.Grouper(key="played_local", freq=freq, label="left", closed="left"))
    .agg(scrobbles=("track_key", "size"), hours=("est_minutes", lambda m: m.sum() / 60))
    .reset_index()
)
# Ordinal labels keep each bar centered under its own period (a time axis offsets them by half a band).
over_time["period"] = over_time["played_local"].dt.strftime(label_fmt)
metric = st.segmented_control("Measure", ["scrobbles", "hours"], default="scrobbles") or "scrobbles"
st.altair_chart(
    alt.Chart(over_time, title=f"{metric.capitalize()} per {grain.lower()}")
    .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color=IRIS)
    .encode(
        x=alt.X("period:O", sort=None, title=None, scale=alt.Scale(paddingInner=0.2),
                axis=alt.Axis(labelAngle=0, labelOverlap="greedy")),
        y=alt.Y(f"{metric}:Q", title=metric.capitalize()),
        tooltip=[alt.Tooltip("period:O", title=grain), alt.Tooltip(f"{metric}:Q", format=",.0f")],
    )
    .properties(height=260),
    width="stretch",
)

# ---- Top lists -------------------------------------------------------------
st.subheader("Top")
df_named = df.assign(
    track=df["artist_name"] + " – " + df["track_name"],
    album=df["artist_name"] + " – " + df["album_name"].fillna(""),
)
tab_art, tab_trk, tab_alb, tab_year = st.tabs(["Artists", "Tracks", "Albums", "#1 per year"])
with tab_art:
    st.altair_chart(top_bar(df_named, "artist_name", "Top artists"), width="stretch")
with tab_trk:
    st.altair_chart(top_bar(df_named, "track", "Top tracks"), width="stretch")
with tab_alb:
    albums = df_named[df_named["album_name"].fillna("") != ""]
    st.altair_chart(top_bar(albums, "album", "Top albums"), width="stretch")
with tab_year:
    by_year = data.groupby(["year", "artist_name"]).size().rename("plays").reset_index()
    top = by_year.sort_values("plays", ascending=False).drop_duplicates("year").sort_values("year")
    totals = data.groupby("year").size().rename("total")
    top = top.join(totals, on="year").assign(share=lambda t: t["plays"] / t["total"])
    st.dataframe(
        top[["year", "artist_name", "plays", "share"]],
        column_config={
            "year": st.column_config.NumberColumn("Year", format="%d"),
            "artist_name": "Artist",
            "share": st.column_config.ProgressColumn("Share of year", format="percent", min_value=0, max_value=1),
        },
        hide_index=True,
        width="stretch",
    )

# ---- When you listen -------------------------------------------------------
left, right = st.columns(2)
with left:
    heat = df.groupby(["weekday_name", "hour"], observed=False).size().rename("plays").reset_index()
    st.altair_chart(
        alt.Chart(heat, title="When you listen")
        .mark_rect(stroke="#18181C", strokeWidth=2, cornerRadius=2)
        .encode(
            x=alt.X("hour:O", title="Hour of day"),
            y=alt.Y("weekday_name:O", sort=WEEKDAYS, title=None, axis=alt.Axis(labelOverlap=False)),
            color=alt.Color("plays:Q", title="Plays", scale=alt.Scale(range=IRIS_RAMP)),
            tooltip=["weekday_name", "hour", "plays"],
        )
        .properties(height=260),
        width="stretch",
    )

# ---- Discovery -------------------------------------------------------------
with right:
    firsts = data.drop_duplicates("artist_key")[["artist_key", "artist_first_play"]]
    firsts = firsts[firsts["artist_first_play"].dt.normalize().between(pd.Timestamp(start), pd.Timestamp(end))]
    new_artists = (
        firsts.groupby(pd.Grouper(key="artist_first_play", freq=freq, label="left", closed="left"))
        .size()
        .rename("new_artists")
        .reset_index()
    )
    st.altair_chart(
        alt.Chart(new_artists, title=f"New artists per {grain.lower()}")
        .mark_line(color=TEAL, strokeWidth=2, point=alt.OverlayMarkDef(color=TEAL, size=64))
        .encode(
            x=alt.X("artist_first_play:T", title=None),
            y=alt.Y("new_artists:Q", title="Artists heard for the first time"),
            tooltip=[alt.Tooltip("artist_first_play:T", title=grain), "new_artists"],
        )
        .properties(height=260),
        width="stretch",
    )
    new_share = (df["artist_first_play"].dt.year == df["played_local"].dt.year).mean()
    st.caption(f"{new_share:.0%} of plays in this range were artists you first heard that same year.")

# ---- Genres & mainstream (need `listening enrich`) -------------------------
st.subheader("Genres and mainstream-ness")
if df["primary_genre"].notna().sum() == 0:
    st.info("Run `uv run listening enrich` to add genres (Last.fm tags), durations and artist popularity.")
else:
    # Small multiples: one panel per genre on a shared y-scale, so no genre needs its own hue.
    tagged = df[df["primary_genre"].notna()]
    top_genres = list(tagged["primary_genre"].value_counts().head(6).index)
    period = pd.Grouper(key="played_local", freq=freq, label="left", closed="left")
    per_period = tagged.groupby(period).size().rename("tagged")
    genre_time = (
        tagged[tagged["primary_genre"].isin(top_genres)]
        .groupby([period, "primary_genre"]).size().rename("plays").reset_index()
        .join(per_period, on="played_local")
        .assign(share=lambda d: d["plays"] / d["tagged"])
    )
    y_max = float(genre_time["share"].max()) if not genre_time.empty else 1.0
    st.caption(f"Share of tagged plays per {grain.lower()} for your top {len(top_genres)} genres (artist's top Last.fm tag). "
               "Click a chart to see its artists.")
    for row_start in range(0, len(top_genres), 3):
        for col, genre in zip(st.columns(3), top_genres[row_start : row_start + 3]):
            panel = genre_time[genre_time["primary_genre"] == genre]
            base = alt.Chart(panel, title=alt.Title(genre, anchor="start", fontSize=13)).encode(
                x=alt.X("played_local:T", title=None, axis=alt.Axis(tickCount=4, grid=False)),
                y=alt.Y("share:Q", title=None, scale=alt.Scale(domain=[0, y_max]),
                        axis=alt.Axis(format="%", tickCount=3)),
                tooltip=[alt.Tooltip("played_local:T", title=grain), alt.Tooltip("share:Q", format=".1%", title="Share"),
                         alt.Tooltip("plays:Q", title="Plays")],
            )
            # Invisible points with `nearest` make a click anywhere in the panel select, not just on the thin area.
            hit = base.mark_point(opacity=0, cursor="pointer").add_params(
                alt.selection_point(name="pick", on="click", nearest=True)
            )
            clicked = col.altair_chart(
                alt.layer(base.mark_area(line={"strokeWidth": 2, "color": IRIS}, color=IRIS, opacity=0.35), hit)
                .properties(height=140),
                width="stretch",
                on_select="rerun",
                key=f"genre-{genre}",
            )
            if clicked.selection.get("pick"):
                st.switch_page("views/genre.py", query_params={
                    "genre": genre, "start": start.isoformat(), "end": end.isoformat(),
                })
    g_left, _ = st.columns(2)
    with g_left:
        known = df[df["artist_listeners"].notna()]
        buckets = (
            pd.cut(known["artist_listeners"], LISTENER_BUCKETS, labels=LISTENER_LABELS, right=False)
            .value_counts(normalize=True, sort=False)
            .rename("share")
            .reset_index()
            .rename(columns={"artist_listeners": "bucket"})
        )
        st.altair_chart(
            alt.Chart(buckets, title="Mainstream vs. niche (artist's Last.fm listeners)")
            .mark_bar(**BAR)
            .encode(
                x=alt.X("bucket:N", sort=LISTENER_LABELS, title="Artist's global listeners", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("share:Q", title="Share of your plays", axis=alt.Axis(format="%")),
                tooltip=["bucket", alt.Tooltip("share:Q", format=".1%")],
            )
            .properties(height=300),
            width="stretch",
        )

# ---- Loved tracks & data quality ------------------------------------------
l_left, l_right = st.columns(2)
with l_left:
    st.subheader("Loved tracks")
    # `loved` is captured when a scrobble is fetched, so a track counts as loved if any scrobble says so.
    loved_keys = set(data.loc[data["loved"] == 1, "track_key"])
    loved = (
        df[df["track_key"].isin(loved_keys)]
        .groupby(["artist_name", "track_name"])
        .size()
        .rename("plays")
        .sort_values(ascending=False)
        .reset_index()
    )
    if loved.empty:
        st.caption("No loved tracks in this range.")
    else:
        st.dataframe(loved, hide_index=True, width="stretch", height=300,
                     column_config={"artist_name": "Artist", "track_name": "Track", "plays": "Plays"})
with l_right:
    st.subheader("Data quality")
    st.dataframe(
        pd.DataFrame(
            {
                "Check": [
                    "Plays with a known track duration",
                    "Plays with artist info",
                    "Plays with a genre tag",
                ],
                "Coverage": [
                    df["duration_ms"].notna().mean(),
                    df["artist_listeners"].notna().mean(),
                    df["primary_genre"].notna().mean(),
                ],
            }
        ),
        column_config={
            "Coverage": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1)
        },
        hide_index=True,
        width="stretch",
    )
    st.caption("Hours are estimated: plays without a known duration count as 3.5 minutes.")
