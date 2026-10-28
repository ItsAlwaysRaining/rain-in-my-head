"""The Overview's numbers, shared by the Streamlit page and the JSON API so both show the same thing.

Everything works on the `v_plays` DataFrame from `load_plays`. Dates are local calendar dates.
"""

from __future__ import annotations

from contextlib import closing
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

import pandas as pd

from .build import connect_readonly

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
PRESETS = ["Last 30 days", "Last 12 months", "This year", "All time", "Custom"]
GRAINS = ["Week", "Month", "Year"]
FREQ = {"Day": "D", "Week": "W-MON", "Month": "MS", "Year": "YS"}
PERIOD_LENGTH = {"Week": pd.DateOffset(weeks=1), "Month": pd.DateOffset(months=1), "Year": pd.DateOffset(years=1)}
LABEL_FORMAT = {"Week": "%d %b %Y", "Month": "%b %Y", "Year": "%Y"}
LISTENER_BUCKETS = [0, 10_000, 100_000, 1_000_000, 5_000_000, float("inf")]
LISTENER_LABELS = ["<10k", "10k–100k", "100k–1M", "1M–5M", "5M+"]
COVERAGE_CHECKS = ["Plays with a known track duration", "Plays with artist info", "Plays with a genre tag"]


def load_plays(db_path: Path) -> pd.DataFrame:
    """Every play from `v_plays`, with derived columns. Cached until the database file changes."""
    return _load(str(db_path), db_path.stat().st_mtime)


@lru_cache(maxsize=1)
def _load(db_path: str, db_mtime: float) -> pd.DataFrame:
    with closing(connect_readonly(db_path)) as conn:
        df = pd.read_sql("SELECT * FROM v_plays", conn)
    df["played_local"] = pd.to_datetime(df["played_local"])
    df["date"] = df["played_local"].dt.normalize()
    # SQLite weekday is 0 = Sunday; shift to 0 = Monday.
    df["weekday_name"] = pd.Categorical(
        [WEEKDAYS[(w - 1) % 7] for w in df["weekday"]], categories=WEEKDAYS, ordered=True
    )
    df["artist_first_play"] = df.groupby("artist_key")["played_local"].transform("min")
    return df


def data_bounds(data: pd.DataFrame) -> tuple[date, date]:
    return data["date"].min().date(), data["date"].max().date()


def resolve_range(data: pd.DataFrame, preset: str, custom: tuple[date, date] | None = None) -> tuple[date, date]:
    """The sidebar range: a preset counted back from the last day with data, or `custom` dates."""
    first_day, last_day = data_bounds(data)
    if preset == "Last 30 days":
        start, end = last_day - timedelta(days=29), last_day
    elif preset == "Last 12 months":
        start, end = last_day - timedelta(days=364), last_day
    elif preset == "This year":
        start, end = last_day.replace(month=1, day=1), last_day
    elif preset == "All time" or custom is None:
        start, end = first_day, last_day
    else:
        start, end = custom
    return max(start, first_day), min(end, last_day)


def in_range(data: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    return data[data["date"].between(pd.Timestamp(start), pd.Timestamp(end))]


def _per(grain: str, key: str = "played_local") -> pd.Grouper:
    """Group timestamps in `key` into steps of `grain`, each labelled by its first day."""
    return pd.Grouper(key=key, freq=FREQ[grain], label="left", closed="left")


def over_time(data: pd.DataFrame, start: date, end: date, grain: str) -> pd.DataFrame:
    """Scrobbles and hours per period of `grain`, with a display label in `period`."""
    df = in_range(data, start, end)
    table = (
        df.groupby(_per(grain))
        .agg(scrobbles=("track_key", "size"), hours=("est_minutes", lambda m: m.sum() / 60))
        .reset_index()
    )
    # Ordinal labels keep each bar centered under its own period (a time axis offsets them by half a band).
    table["period"] = table["played_local"].dt.strftime(LABEL_FORMAT[grain])
    return table


def select_period(
    periods: pd.DataFrame, start: date, end: date, grain: str, period: str | None
) -> tuple[date, date, str | None]:
    """Narrow the range to the clicked period. A label that names no bar is ignored."""
    match = periods[periods["period"] == period]
    if match.empty:
        return start, end, None
    period_start = match["played_local"].iloc[0]
    period_end = period_start + PERIOD_LENGTH[grain] - pd.Timedelta(days=1)
    return max(start, period_start.date()), min(end, period_end.date()), match["period"].iloc[0]


def inner_grain(grain: str, selected: str | None) -> str:
    """Inside a selected period, time series step by day (week or month) or month (year)."""
    return grain if selected is None else ("Month" if grain == "Year" else "Day")


def previous(data: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    """Plays in the period of the same length just before `start`."""
    span = pd.Timestamp(end) - pd.Timestamp(start)
    return data[data["date"].between(
        pd.Timestamp(start) - span - pd.Timedelta(days=1), pd.Timestamp(start) - pd.Timedelta(days=1)
    )]


def kpis(cur: pd.DataFrame, prev: pd.DataFrame) -> dict[str, tuple[float, float | None]]:
    """Label -> (value, change vs. the previous period as a fraction, or None)."""
    now, before = _kpi_values(cur), _kpi_values(prev)
    return {
        label: (value, (value - before[label]) / before[label] if not prev.empty and before[label] else None)
        for label, value in now.items()
    }


def _kpi_values(df: pd.DataFrame) -> dict[str, float]:
    return {
        "Scrobbles": len(df),
        "Hours (est.)": df["est_minutes"].sum() / 60,
        "Tracks": df["track_key"].nunique(),
        "Artists": df["artist_key"].nunique(),
        "Albums": df["album_name"].nunique(),
    }


def top_lists(df: pd.DataFrame, n: int = 20) -> dict[str, pd.DataFrame]:
    """Top artists, tracks and albums: columns `name`, `plays`, most played first."""
    named = df.assign(
        track=df["artist_name"] + " – " + df["track_name"],
        album=df["artist_name"] + " – " + df["album_name"].fillna(""),
    )
    albums = named[named["album_name"].fillna("") != ""]
    return {
        "artists": _top(named, "artist_name", n),
        "tracks": _top(named, "track", n),
        "albums": _top(albums, "album", n),
    }


def _top(df: pd.DataFrame, field: str, n: int) -> pd.DataFrame:
    return df.groupby(field).size().nlargest(n).rename("plays").reset_index().rename(columns={field: "name"})


def top_per_year(data: pd.DataFrame) -> pd.DataFrame:
    """Each year's most played artist and their share of that year's plays."""
    by_year = data.groupby(["year", "artist_name"]).size().rename("plays").reset_index()
    top = by_year.sort_values("plays", ascending=False).drop_duplicates("year").sort_values("year")
    totals = data.groupby("year").size().rename("total")
    top = top.join(totals, on="year").assign(share=lambda t: t["plays"] / t["total"])
    return top[["year", "artist_name", "plays", "share"]]


def heatmap(df: pd.DataFrame) -> pd.DataFrame:
    """Plays per weekday (Mon..Sun) and hour, including empty cells."""
    return df.groupby(["weekday_name", "hour"], observed=False).size().rename("plays").reset_index()


def new_artists(data: pd.DataFrame, start: date, end: date, grain: str) -> pd.DataFrame:
    """Artists first heard in the range, counted per `grain` step."""
    firsts = data.drop_duplicates("artist_key")[["artist_key", "artist_first_play"]]
    firsts = firsts[firsts["artist_first_play"].dt.normalize().between(pd.Timestamp(start), pd.Timestamp(end))]
    return (
        firsts.groupby(_per(grain, "artist_first_play"))
        .size()
        .rename("new_artists")
        .reset_index()
    )


def new_share(df: pd.DataFrame) -> float:
    """Share of plays by artists first heard in the same year as the play."""
    return float((df["artist_first_play"].dt.year == df["played_local"].dt.year).mean())


def genre_shares(df: pd.DataFrame, grain: str, n: int = 6) -> tuple[list[str], float, pd.DataFrame] | None:
    """(top genres, highest share, per-step share of tagged plays), or None if nothing is tagged."""
    tagged = df[df["primary_genre"].notna()]
    if tagged.empty:
        return None
    top_genres = list(tagged["primary_genre"].value_counts().head(n).index)
    period = _per(grain)
    per_period = tagged.groupby(period).size().rename("tagged")
    genre_time = (
        tagged[tagged["primary_genre"].isin(top_genres)]
        .groupby([period, "primary_genre"]).size().rename("plays").reset_index()
        .join(per_period, on="played_local")
        .assign(share=lambda d: d["plays"] / d["tagged"])
    )
    y_max = float(genre_time["share"].max()) if not genre_time.empty else 1.0
    return top_genres, y_max, genre_time


def listener_buckets(df: pd.DataFrame) -> pd.DataFrame:
    """Share of plays by the artist's global Last.fm listener count."""
    known = df[df["artist_listeners"].notna()]
    return (
        pd.cut(known["artist_listeners"], LISTENER_BUCKETS, labels=LISTENER_LABELS, right=False)
        .value_counts(normalize=True, sort=False)
        .rename("share")
        .reset_index()
        .rename(columns={"artist_listeners": "bucket"})
    )


def loved(data: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """Loved tracks played in `df`, most played first."""
    # `loved` is captured when a scrobble is fetched, so a track counts as loved if any scrobble says so.
    loved_keys = set(data.loc[data["loved"] == 1, "track_key"])
    return (
        df[df["track_key"].isin(loved_keys)]
        .groupby(["artist_name", "track_name"])
        .size()
        .rename("plays")
        .sort_values(ascending=False)
        .reset_index()
    )


def coverage(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "Check": COVERAGE_CHECKS,
        "Coverage": [
            df["duration_ms"].notna().mean(),
            df["artist_listeners"].notna().mean(),
            df["primary_genre"].notna().mean(),
        ],
    })
