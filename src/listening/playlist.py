"""Pick tracks that characterize a time slot (e.g. Fridays 17–19h) and build Spotify playlists.

Ranking is "distinctive to the slot", not "most played": for each track we compare the
share of its plays that fall in the slot with the slot's share of *all* plays (lift).
Lift is shrunk toward 1 for tracks with few plays, so a song played once (in the slot)
doesn't beat one played 40 times mostly in the slot. Final score = log(lift) × log(1 + slot plays).
"""

from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass, field
from datetime import date

import numpy as np
import pandas as pd

WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WEEKDAY_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SHRINK = 10  # pseudo-plays pulling each track's lift toward 1


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
        return f"Tracks distinctive to {self.label()}{span}. Made from my Last.fm history."


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
            GROUP BY track_key""",
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


# Playlist orders for binges. Songs binged more than once sit at their first binge when
# oldest-first and at their most recent binge when newest-first.
BINGE_ORDERS = {
    "oldest": "in the order I binged them",
    "newest": "most recent binges first",
    "biggest": "biggest binges first",
}


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
