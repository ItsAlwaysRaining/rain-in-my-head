"""Pick tracks that characterize a time slot (e.g. Fridays 17–19h) and build Spotify playlists.

Ranking is "distinctive to the slot", not "most played": for each track we compare the
share of its plays that fall in the slot with the slot's share of *all* plays (lift).
Lift is shrunk toward 1 for tracks with few plays, so a song played once (in the slot)
doesn't beat one played 40 times mostly in the slot. Final score = log(lift) × log(1 + slot plays).
"""

from __future__ import annotations

import sqlite3
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, timedelta

import numpy as np
import pandas as pd

WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WEEKDAY_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SHRINK = 10  # pseudo-plays pulling each track's lift toward 1
CREDIT = "Made from my Last.fm history."

# Playlist orders for binges. Songs binged more than once sit at their first binge when
# oldest-first and at their most recent binge when newest-first.
BINGE_ORDERS = {
    "oldest": "in the order I binged them",
    "newest": "most recent binges first",
    "biggest": "biggest binges first",
}


def play_bounds(conn: sqlite3.Connection) -> tuple[date, date]:
    """The first and last local day with a play."""
    first, last = conn.execute("SELECT MIN(date(played_local)), MAX(date(played_local)) FROM v_plays").fetchone()
    return pd.Timestamp(first).date(), pd.Timestamp(last).date()


@dataclass
class Slot:
    weekdays: list[int] = field(default_factory=lambda: list(range(7)))  # 0 = Monday
    start_hour: int = 0  # inclusive
    end_hour: int = 24  # exclusive; start > end wraps past midnight (e.g. 22 → 2)
    since: date | None = None
    until: date | None = None

    def label(self) -> str:
        days = (
            "Every day" if len(self.weekdays) == 7
            else "Weekdays" if sorted(self.weekdays) == [0, 1, 2, 3, 4]
            else "Weekends" if sorted(self.weekdays) == [5, 6]
            else ", ".join(WEEKDAY_FULL[d] + "s" for d in sorted(self.weekdays))
        )
        hours = "" if (self.start_hour, self.end_hour) == (0, 24) else f" {_h(self.start_hour)}–{_h(self.end_hour)}"
        return f"{days}{hours}"

    def describe(self) -> str:
        span = ""
        if self.since or self.until:
            span = f", {self.since or 'start'} to {self.until or 'now'}"
        return f"Tracks distinctive to {self.label()}{span}. {CREDIT}"


def _h(hour: int) -> str:
    hour %= 24
    return f"{(hour % 12) or 12}{'am' if hour < 12 else 'pm'}"


def _slot_sql(slot: Slot) -> tuple[str, list]:
    # v_plays.weekday is SQLite's %w (0 = Sunday); Slot uses 0 = Monday.
    sqlite_days = [(d + 1) % 7 for d in slot.weekdays]
    day_clause = f"weekday IN ({','.join('?' * len(sqlite_days))})"
    if slot.start_hour <= slot.end_hour:
        hour_clause = "(hour >= ? AND hour < ?)"
    else:
        hour_clause = "(hour >= ? OR hour < ?)"
    return f"({day_clause} AND {hour_clause})", [*sqlite_days, slot.start_hour, slot.end_hour]


def rank_tracks(conn: sqlite3.Connection, slot: Slot, min_slot_plays: int = 3) -> pd.DataFrame:
    in_slot, slot_params = _slot_sql(slot)
    where, params = ["1=1"], []
    if slot.since:
        where.append("date(played_local) >= ?")
        params.append(slot.since.isoformat())
    if slot.until:
        where.append("date(played_local) <= ?")
        params.append(slot.until.isoformat())
    df = pd.read_sql(
        f"""SELECT track_key, MIN(artist_name) AS artist, MIN(track_name) AS track,
                   SUM({in_slot}) AS slot_plays, COUNT(*) AS total_plays,
                   MAX(date(played_local)) AS last_played
            FROM v_plays WHERE {' AND '.join(where)}
            GROUP BY track_key""",  # noqa: S608 fixed fragments with ? placeholders; playlists are local only
        conn,
        params=[*slot_params, *params],
    )
    if df.empty or df["slot_plays"].sum() == 0:
        return df.head(0).assign(lift=[], score=[])
    base = df["slot_plays"].sum() / df["total_plays"].sum()  # slot's share of all plays
    df["lift"] = ((df["slot_plays"] + SHRINK * base) / (df["total_plays"] + SHRINK)) / base
    df["score"] = np.log(df["lift"].clip(lower=1)) * np.log1p(df["slot_plays"])
    ranked = df[(df["slot_plays"] >= min_slot_plays) & (df["lift"] > 1)]
    return ranked.sort_values(["score", "slot_plays"], ascending=False).reset_index(drop=True)


def discoveries(conn: sqlite3.Connection, year: int, min_plays: int = 2, rank_by: str = "year") -> pd.DataFrame:
    """Tracks whose first-ever play was in `year`.

    rank_by="year": most played during that year (what you were into right after finding it).
    rank_by="ever": most played overall (the discoveries that stuck with you).
    """
    df = pd.read_sql(
        """SELECT track_key, MIN(artist_name) AS artist, MIN(track_name) AS track,
                  MIN(played_local) AS first_played,
                  SUM(year = ?) AS year_plays, COUNT(*) AS total_plays,
                  MAX(date(played_local)) AS last_played
           FROM v_plays
           GROUP BY track_key
           HAVING MIN(year) = ?""",
        conn,
        params=[year, year],
    )
    df["first_played"] = pd.to_datetime(df["first_played"])
    metric = "year_plays" if rank_by == "year" else "total_plays"
    df = df[df[metric] >= min_plays]
    return df.sort_values([metric, "first_played"], ascending=[False, True]).reset_index(drop=True)


def discoveries_description(year: int, rank_by: str) -> str:
    picked = "plays that year" if rank_by == "year" else "plays since"
    return f"Songs I first heard in {year}, picked by {picked}. {CREDIT}"


def binges(
    conn: sqlite3.Connection,
    min_plays: int = 8,
    window_days: int = 7,
    since_year: int | None = None,
    until_year: int | None = None,
) -> pd.DataFrame:
    """One row per binge: a run where a track got >= min_plays plays within window_days.

    For each play we count plays in the window starting there; every qualifying window
    covers a range of plays, and overlapping/adjacent ranges merge into one episode.
    """
    plays = pd.read_sql(
        """SELECT track_key, artist_name, track_name, played_at, played_local
           FROM v_plays
           WHERE track_key IN (SELECT track_key FROM v_plays GROUP BY track_key HAVING COUNT(*) >= ?)
           ORDER BY track_key, played_at""",
        conn,
        params=[min_plays],
    )
    window = window_days * 86400
    rows = []
    for track_key, g in plays.groupby("track_key", sort=False):
        t = g["played_at"].to_numpy()
        end = np.searchsorted(t, t + window, "left")  # plays [i, end[i]) fall in i's window
        starts = np.flatnonzero(end - np.arange(len(t)) >= min_plays)
        if not len(starts):
            continue
        local = g["played_local"].to_numpy()
        info = {"track_key": track_key, "artist": g["artist_name"].iloc[0], "track": g["track_name"].iloc[0],
                "total_plays": len(t)}
        ep_start, ep_end = starts[0], end[starts[0]]
        for i in starts[1:]:
            if i <= ep_end:  # overlaps or directly follows the current episode
                ep_end = max(ep_end, end[i])
            else:
                rows.append({**info, "start": local[ep_start], "end": local[ep_end - 1], "plays": ep_end - ep_start})
                ep_start, ep_end = i, end[i]
        rows.append({**info, "start": local[ep_start], "end": local[ep_end - 1], "plays": ep_end - ep_start})

    columns = ["track_key", "artist", "track", "start", "end", "plays", "binge_count", "total_plays"]
    if not rows:
        return pd.DataFrame(columns=columns)
    episodes = pd.DataFrame(rows)
    episodes["start"] = pd.to_datetime(episodes["start"])
    episodes["end"] = pd.to_datetime(episodes["end"])
    if since_year:
        episodes = episodes[episodes["start"].dt.year >= since_year]
    if until_year:
        episodes = episodes[episodes["start"].dt.year <= until_year]
    episodes = episodes.assign(binge_count=episodes.groupby("track_key")["plays"].transform("size"))
    return episodes[columns].sort_values("start").reset_index(drop=True)


def binge_tracks(episodes: pd.DataFrame) -> pd.DataFrame:
    """One row per binged track, biggest binge first (ties: earlier binge first)."""
    if episodes.empty:
        return pd.DataFrame(columns=["track_key", "artist", "track", "peak_plays", "first_binge", "last_binge",
                                     "binge_count", "total_plays"])
    tracks = episodes.groupby("track_key", as_index=False).agg(
        artist=("artist", "first"), track=("track", "first"), peak_plays=("plays", "max"),
        first_binge=("start", "min"), last_binge=("start", "max"),
        binge_count=("binge_count", "first"), total_plays=("total_plays", "first"),
    )
    return tracks.sort_values(["peak_plays", "first_binge"], ascending=[False, True]).reset_index(drop=True)


def binges_description(min_plays: int, window_days: int, order: str) -> str:
    window = "a day" if window_days == 1 else f"{window_days} days"
    return f"Songs I played {min_plays}+ times within {window}, {BINGE_ORDERS[order]}. {CREDIT}"


def order_binge_tracks(tracks: pd.DataFrame, order: str) -> pd.DataFrame:
    """Reorder binge_tracks()-style rows (e.g. Spotify matches) for the playlist."""
    if order == "oldest":
        return tracks.sort_values("first_binge")
    if order == "newest":
        return tracks.sort_values("last_binge", ascending=False)
    return tracks.sort_values(["peak_plays", "first_binge"], ascending=[False, True])


def order_binge_episodes(episodes: pd.DataFrame, order: str) -> pd.DataFrame:
    """Reorder binges() rows for display."""
    if order == "oldest":
        return episodes.sort_values("start")
    if order == "newest":
        return episodes.sort_values("start", ascending=False)
    return episodes.sort_values(["plays", "start"], ascending=[False, True])


def format_span(start: pd.Timestamp, end: pd.Timestamp) -> str:
    """'23 Jan 2017', '23–29 Jan 2017', '28 Dec 2016 – 3 Jan 2017'."""
    if start.date() == end.date():
        return f"{start.day} {start:%b %Y}"
    if (start.year, start.month) == (end.year, end.month):
        return f"{start.day}–{end.day} {end:%b %Y}"
    if start.year == end.year:
        return f"{start.day} {start:%b} – {end.day} {end:%b %Y}"
    return f"{start.day} {start:%b %Y} – {end.day} {end:%b %Y}"


def match_tracks(conn: sqlite3.Connection, client, ranked: pd.DataFrame, want: int, progress=None) -> pd.DataFrame:
    """Walk the ranking, matching to Spotify (cached), until `want` tracks have a match."""
    cached = {
        row[0]: row[1:]
        for row in conn.execute("SELECT track_key, spotify_uri, spotify_name, spotify_artist, score FROM spotify_matches")
    }
    out = []
    matched = 0
    for i, row in enumerate(ranked.itertuples(index=False)):
        if matched >= want:
            break
        if row.track_key in cached:
            uri, name, artist, score = cached[row.track_key]
        else:
            m = client.search_track(row.artist, row.track)
            uri, name, artist, score = (m["uri"], m["name"], m["artist"], m["score"]) if m else (None, None, None, None)
            conn.execute(
                "INSERT OR REPLACE INTO spotify_matches VALUES (?,?,?,?,?,?)",
                (row.track_key, uri, name, artist, score, int(time.time())),
            )
            conn.commit()
        out.append({**row._asdict(), "spotify_uri": uri, "spotify_name": name, "spotify_artist": artist, "match": score})
        matched += uri is not None
        if progress:
            progress(min(matched / want, 1.0), f"Matched {matched}/{want} (checked {i + 1})")
    return pd.DataFrame(out)


def create_on_spotify(
    conn: sqlite3.Connection, client, ranked: pd.DataFrame, size: int, name: str, description: str,
    reorder: Callable[[pd.DataFrame], pd.DataFrame] | None = None, public: bool = False, progress=None,
) -> tuple[str, pd.DataFrame, pd.DataFrame]:
    """Match `ranked` on Spotify until `size` tracks match, then create the playlist.

    Returns (playlist URL, the tracks added, the tracks with no match). Matching walks the
    ranking, so a miss is replaced by the next-ranked track; `reorder` then sets the play order.
    """
    matched = match_tracks(conn, client, ranked, size, progress)
    hits = matched[matched["spotify_uri"].notna()]
    if reorder:
        hits = reorder(hits)
    url = client.create_playlist(name, description, list(hits["spotify_uri"]), public=public)
    return url, hits, matched[matched["spotify_uri"].isna()]


# ---- Previews ------------------------------------------------------------------
# What the Playlists page shows for each playlist type, built from the form's values. Shared by the
# Streamlit view (which owns the widgets) and the API, so both show the same preview.

SPANS = ["All time", "Last 5 years", "Last 2 years", "Custom"]
DISCOVERY_ORDERS = ["Ranking", "Order discovered"]
RANK_BY = {"year": "Most played that year (what hooked you)", "ever": "Most played since (the ones that stuck)"}
BINGE_ORDER_LABELS = {"oldest": "Oldest first", "newest": "Newest first", "biggest": "Biggest binge first"}
WINDOWS = [1, 7, 30]


@dataclass
class Column:
    label: str
    kind: str = "text"  # text | number | lift (1.2×) | date (D MMM YYYY)
    help: str | None = None


@dataclass
class Preview:
    ranked: pd.DataFrame  # one row per track, in the order to try matching on Spotify
    size: int
    name: str  # default playlist name
    description: str
    columns: dict[str, Column]  # preview table columns, in order
    title: str | None = None  # the subheader above the preview
    display: pd.DataFrame | None = None  # preview rows, if not simply ranked.head(size)
    # Reorders matched tracks before creating. Matching always walks `ranked`, so a song with no
    # Spotify match is replaced by the next-ranked one and the requested order still holds.
    reorder: Callable[[pd.DataFrame], pd.DataFrame] | None = None
    note: str | None = None  # info shown before the title
    warning: str | None = None  # when set, there is nothing to preview or create
    info: str | None = None  # info shown after the title
    caption: str = ""  # shown just above the table

    @property
    def rows(self) -> pd.DataFrame:
        return self.display if self.display is not None else self.ranked.head(self.size)


def _empty(warning: str, title: str | None = None) -> Preview:
    return Preview(pd.DataFrame(), 0, "", "", {}, title=title, warning=warning)


def preview_slot(
    conn: sqlite3.Connection, first: date, last: date, days: list[str], hours: tuple[int, int],
    span: str, custom: tuple[date, date] | None, size: int, min_plays: int,
) -> Preview:
    if span == "All time":
        since, until = None, None
    elif span == "Custom":
        since, until = custom or (first, last)
    else:
        since, until = last - timedelta(days=365 * int(span.split()[1])), None
    if not days:
        return _empty("Pick at least one day.")
    if hours[0] == hours[1]:
        return _empty("Pick an hour range of at least one hour.")

    slot = Slot([WEEKDAY_FULL.index(d) for d in days], hours[0], hours[1], since, until)
    ranked = rank_tracks(conn, slot, min_plays)
    if ranked.empty:
        return _empty("No tracks stand out in this slot. Try a wider slot or a lower minimum plays.", slot.label())
    info = None
    if len(ranked) < size and min_plays > 1:
        info = f"Fewer than {size} tracks qualify. Lower **Min. plays in the slot** or widen the slot to get more."
    columns = {
        "artist": Column("Artist"), "track": Column("Track"),
        "slot_plays": Column("Plays in slot", "number"),
        "total_plays": Column("Plays overall", "number"),
        "lift": Column("× more than usual", "lift"),
        "last_played": Column("Last played"),
    }
    return Preview(ranked, size, slot.label(), slot.describe(), columns, title=slot.label(), info=info,
                   caption=_candidates(ranked, size))


def preview_discoveries(
    conn: sqlite3.Connection, first: date, year: int, rank_by: str, order: str, size: int, min_plays: int,
) -> Preview:
    note = None
    if year <= first.year + 1:
        note = (f"Your Last.fm history starts {first:%B %Y}, so {year}'s \"discoveries\" include older "
                "favourites heard for the first time *on Last.fm*.")
    title = f"Discovered in {year}"
    ranked = discoveries(conn, year, min_plays, rank_by)
    if ranked.empty:
        p = _empty("No songs qualify. Try a lower minimum plays.", title)
        p.note = note
        return p
    columns = {
        "artist": Column("Artist"), "track": Column("Track"),
        "first_played": Column("First played", "date"),
        "year_plays": Column(f"Plays in {year}", "number"),
        "total_plays": Column("Plays ever", "number"),
        "last_played": Column("Last played"),
    }
    # Match in ranking order (so misses are replaced by the next best), then play in discovery order.
    by_date = order == "Order discovered"
    display = ranked.head(size).sort_values("first_played") if by_date else None
    return Preview(ranked, size, title, discoveries_description(year, rank_by), columns, title=title,
                   display=display, reorder=(lambda hits: hits.sort_values("first_played")) if by_date else None,
                   note=note, caption=_candidates(ranked, size))


def preview_binges(
    episodes: pd.DataFrame, first: date, last: date, years: tuple[int, int], window_days: int,
    min_plays: int, size: int, order: str,
) -> Preview:
    """`episodes` is binges(conn, min_plays, window_days, *years), which callers cache."""
    ranked = binge_tracks(episodes)
    span = str(years[0]) if years[0] == years[1] else f"{years[0]}–{years[1]}"
    title = f"Binged songs, {span}"
    if ranked.empty:
        return _empty("No binges with these settings. Lower the minimum plays or widen the window.", title)
    chosen = set(ranked.head(size)["track_key"])
    display = episodes[episodes["track_key"].isin(chosen)].assign(
        when=lambda d: [format_span(a, b) for a, b in zip(d["start"], d["end"])]
    )
    display = order_binge_episodes(display, order)
    columns = {
        "when": Column("When"), "artist": Column("Artist"), "track": Column("Track"),
        "plays": Column("Plays in binge", "number"),
        "binge_count": Column("Binges", "number", "How many separate times you binged this song"),
        "total_plays": Column("Plays ever", "number"),
    }
    full_range = (years[0], years[1]) == (first.year, last.year)
    caption = f"{len(episodes):,} binges across {len(ranked):,} songs; showing the top {min(size, len(ranked))} songs."
    return Preview(ranked, size, "Binged" if full_range else f"Binged {span}",
                   binges_description(min_plays, window_days, order), columns, title=title,
                   display=display, reorder=lambda hits: order_binge_tracks(hits, order), caption=caption)


def _candidates(ranked: pd.DataFrame, size: int) -> str:
    return f"{len(ranked):,} candidate tracks; the top {min(size, len(ranked))} are shown."


# ---- SQL type ------------------------------------------------------------------------------------------------
SQL_MAX = 100  # tracks a SQL playlist uses, in query order
SQL_REQUIRED = ("artist", "track")


@dataclass
class SqlPreview(Preview):
    missing: list[str] = field(default_factory=list)  # required columns the query didn't return


def preview_sql(result: pd.DataFrame) -> SqlPreview:
    """A playlist from a read-only query's result: needs `artist` and `track` columns (any case); keeps the rest."""
    from rain_in_my_head.build import normalize, normalize_track

    by_lower = {str(c).lower(): c for c in result.columns}
    missing = [c for c in SQL_REQUIRED if c not in by_lower]
    title = "From your query"
    if missing:
        p = SqlPreview(pd.DataFrame(), 0, "", "", {}, title=title, missing=missing,
                       warning="The query must return " + " and ".join(f"`{c}`" for c in missing) + " column"
                       + ("s." if len(missing) > 1 else "."))
        return p
    df = result.rename(columns={by_lower["artist"]: "artist", by_lower["track"]: "track"})
    df = df.loc[:, ~df.columns.duplicated()].dropna(subset=["artist", "track"]).head(SQL_MAX).reset_index(drop=True)
    if df.empty:
        return SqlPreview(pd.DataFrame(), 0, "", "", {}, title=title, warning="The query returned no tracks.")
    df.columns = [str(c) for c in df.columns]
    ranked = df.assign(track_key=[f"{normalize(str(a))}\t{normalize_track(str(t))}" for a, t in zip(df["artist"], df["track"])])
    columns = {"artist": Column("Artist"), "track": Column("Track")}
    for c in df.columns:
        if c not in columns:
            columns[c] = Column(c, "number" if pd.api.types.is_numeric_dtype(df[c]) else "text")
    caption = f"{len(df):,} tracks" + (f" (the first {SQL_MAX})" if len(result) > SQL_MAX else "") + ", in query order."
    return SqlPreview(ranked, len(df), "From my query", f"Built from a SQL query. {CREDIT}", columns,
                      title=title, display=df, caption=caption)
