"""Overview page: listening stats over data/listening.db."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from listening import config
from listening import overview as ov


# Chart steps of the theme palette (see .streamlit/config.toml): iris = plays, teal = discovery.
IRIS, TEAL = "#7F77D6", "#0E9A94"
IRIS_RAMP = ["#1D1C34", "#2B284D", "#393567", "#484383", "#58519E", "#6B63BC", "#7F78D6", "#948FE8", "#AAA8F1", "#C2C1F7"]
IRIS_DIM = IRIS_RAMP[2]  # unselected bars while a period is selected
BAR = {"cornerRadiusEnd": 4, "color": IRIS}


@st.cache_data
def load(db_mtime: float) -> pd.DataFrame:
    return ov.load_plays(config.DB_PATH)


def top_bar(counts: pd.DataFrame, field: str, title: str) -> alt.Chart:
    """`counts` has `name` and `plays` (from ov.top_lists); `field` is the tooltip label."""
    return (
        alt.Chart(counts, title=title)
        .mark_bar(**BAR)
        .encode(
            x=alt.X("plays:Q", title="Plays"),
            y=alt.Y("name:N", sort="-x", title=None, axis=alt.Axis(labelLimit=320, labelOverlap=False)),
            tooltip=[alt.Tooltip("name:N", title=field), "plays"],
        )
        .properties(height=max(200, 26 * len(counts)))
    )


if not config.DB_PATH.exists():
    st.title("Listening")
    st.info("No database yet. Run `uv run listening fetch` then `uv run listening build`.")
    st.stop()

data = load(config.DB_PATH.stat().st_mtime)
if data.empty:
    st.info("The database has no scrobbles yet. Run `uv run listening fetch` and `uv run listening build`.")
    st.stop()

# ---- Sidebar filters -------------------------------------------------------
first_day, last_day = ov.data_bounds(data)
with st.sidebar:
    st.header("Filters")
    preset = st.radio("Range", ov.PRESETS, index=1)
    custom = None
    if preset == "Custom":
        picked = st.date_input("Dates", ov.resolve_range(data, "Last 12 months"), first_day, last_day)
        custom = picked if len(picked) == 2 else (picked[0], picked[0])
    start, end = ov.resolve_range(data, preset, custom)
    grain = st.radio("Time grain", ov.GRAINS, index=1, horizontal=True)

# ---- Over-time table, and the period clicked in its chart ------------------
# Built from the sidebar range so the chart keeps every period while one is selected.
over_time = ov.over_time(data, start, end, grain)

# The chart's selection from the last click is in session state before the chart is drawn.
# Range and grain are in the key so changing either drops the selection.
over_time_key = f"over_time-{grain}-{start}-{end}-{st.session_state.get('over_time_resets', 0)}"
clicked = (st.session_state.get(over_time_key) or {}).get("selection", {}).get("pick") or [{}]
start, end, selected = ov.select_period(over_time, start, end, grain, clicked[0].get("period"))
df = ov.in_range(data, start, end)
inner_grain = ov.inner_grain(grain, selected)
prev = ov.previous(data, start, end)

st.title("Listening")
st.caption(f"{start:%d %b %Y} – {end:%d %b %Y} · data through {data['played_local'].max():%d %b %Y %H:%M}")

if df.empty:
    st.warning("No scrobbles in this range.")
    st.stop()

# ---- KPIs ------------------------------------------------------------------
kpis = ov.kpis(df, prev)
for col, (label, (value, change)) in zip(st.columns(len(kpis)), kpis.items()):
    delta = None if change is None else f"{change:+.0%}"
    col.metric(label, f"{value:,.0f}", delta, help="Change vs. the previous period of equal length")

# ---- Over time -------------------------------------------------------------
metric = st.segmented_control("Measure", ["scrobbles", "hours"], default="scrobbles") or "scrobbles"
pick = alt.selection_point(name="pick", fields=["period"], on="click")
st.altair_chart(
    alt.Chart(over_time, title=f"{metric.capitalize()} per {grain.lower()}")
    .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, cursor="pointer")
    .encode(
        x=alt.X("period:O", sort=None, title=None, scale=alt.Scale(paddingInner=0.2),
                axis=alt.Axis(labelAngle=0, labelOverlap="greedy")),
        y=alt.Y(f"{metric}:Q", title=metric.capitalize()),
        color=alt.condition(pick, alt.value(IRIS), alt.value(IRIS_DIM)),
        tooltip=[alt.Tooltip("period:O", title=grain), alt.Tooltip(f"{metric}:Q", format=",.0f")],
    )
    .add_params(pick)
    .properties(height=260),
    width="stretch",
    on_select="rerun",
    key=over_time_key,
)


def show_whole_range() -> None:
    st.session_state["over_time_resets"] = st.session_state.get("over_time_resets", 0) + 1


if selected is None:
    st.caption(f"Click a bar to show just that {grain.lower()}.")
else:
    name = f"the week of {selected}" if grain == "Week" else selected
    note, button = st.columns([4, 1], vertical_alignment="center")
    note.caption(f"Showing {name} only. Click the chart background or the button to show the whole range.")
    button.button("Show whole range", on_click=show_whole_range, width="stretch")

# ---- Top lists -------------------------------------------------------------
st.subheader("Top")
top = ov.top_lists(df)
tab_art, tab_trk, tab_alb, tab_year = st.tabs(["Artists", "Tracks", "Albums", "#1 per year"])
with tab_art:
    st.altair_chart(top_bar(top["artists"], "artist_name", "Top artists"), width="stretch")
with tab_trk:
    st.altair_chart(top_bar(top["tracks"], "track", "Top tracks"), width="stretch")
with tab_alb:
    st.altair_chart(top_bar(top["albums"], "album", "Top albums"), width="stretch")
with tab_year:
    st.dataframe(
        ov.top_per_year(data),
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
    heat = ov.heatmap(df)
    st.altair_chart(
        alt.Chart(heat, title="When you listen")
        .mark_rect(stroke="#18181C", strokeWidth=2, cornerRadius=2)
        .encode(
            x=alt.X("hour:O", title="Hour of day"),
            y=alt.Y("weekday_name:O", sort=ov.WEEKDAYS, title=None, axis=alt.Axis(labelOverlap=False)),
            color=alt.Color("plays:Q", title="Plays", scale=alt.Scale(range=IRIS_RAMP)),
            tooltip=["weekday_name", "hour", "plays"],
        )
        .properties(height=260),
        width="stretch",
    )

# ---- Discovery -------------------------------------------------------------
with right:
    new_artists = ov.new_artists(data, start, end, inner_grain)
    st.altair_chart(
        alt.Chart(new_artists, title=f"New artists per {inner_grain.lower()}")
        .mark_line(color=TEAL, strokeWidth=2, point=alt.OverlayMarkDef(color=TEAL, size=64))
        .encode(
            x=alt.X("artist_first_play:T", title=None),
            y=alt.Y("new_artists:Q", title="Artists heard for the first time"),
            tooltip=[alt.Tooltip("artist_first_play:T", title=inner_grain), "new_artists"],
        )
        .properties(height=260),
        width="stretch",
    )
    st.caption(f"{ov.new_share(df):.0%} of plays in this range were artists you first heard that same year.")

# ---- Genres & mainstream (need `listening enrich`) -------------------------
st.subheader("Genres and mainstream-ness")
genres = ov.genre_shares(df, inner_grain)
if genres is None:
    st.info("Run `uv run listening enrich` to add genres (Last.fm tags), durations and artist popularity.")
else:
    # Small multiples: one panel per genre on a shared y-scale, so no genre needs its own hue.
    top_genres, y_max, genre_time = genres
    st.caption(f"Share of tagged plays per {inner_grain.lower()} for your top {len(top_genres)} genres (artist's top Last.fm tag). "
               "Click a chart to see its artists.")
    for row_start in range(0, len(top_genres), 3):
        for col, genre in zip(st.columns(3), top_genres[row_start : row_start + 3]):
            panel = genre_time[genre_time["primary_genre"] == genre]
            base = alt.Chart(panel, title=alt.Title(genre, anchor="start", fontSize=13)).encode(
                x=alt.X("played_local:T", title=None, axis=alt.Axis(tickCount=4, grid=False)),
                y=alt.Y("share:Q", title=None, scale=alt.Scale(domain=[0, y_max]),
                        axis=alt.Axis(format="%", tickCount=3)),
                tooltip=[alt.Tooltip("played_local:T", title=inner_grain), alt.Tooltip("share:Q", format=".1%", title="Share"),
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
        buckets = ov.listener_buckets(df)
        st.altair_chart(
            alt.Chart(buckets, title="Mainstream vs. niche (artist's Last.fm listeners)")
            .mark_bar(**BAR)
            .encode(
                x=alt.X("bucket:N", sort=ov.LISTENER_LABELS, title="Artist's global listeners", axis=alt.Axis(labelAngle=0)),
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
    loved = ov.loved(data, df)
    if loved.empty:
        st.caption("No loved tracks in this range.")
    else:
        st.dataframe(loved, hide_index=True, width="stretch", height=300,
                     column_config={"artist_name": "Artist", "track_name": "Track", "plays": "Plays"})
with l_right:
    st.subheader("Data quality")
    st.dataframe(
        ov.coverage(df),
        column_config={
            "Coverage": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1)
        },
        hide_index=True,
        width="stretch",
    )
    st.caption("Hours are estimated: plays without a known duration count as 3.5 minutes.")
