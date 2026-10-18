"""JSON API for the TypeScript dashboard (web/). Run: uv run rain-in-my-head serve

Every number comes from the same functions the Streamlit pages use (rain_in_my_head.overview, ...), so the
two dashboards always agree. Also serves the built frontend from web/dist. Contract:
specs/003-typescript-dashboard/contracts/api.md
"""

from __future__ import annotations

import functools
import json
import math
import queue
import sqlite3
import threading
from datetime import date
from typing import Literal

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, Response, StreamingResponse
from pydantic import BaseModel

from rain_in_my_head import config
from rain_in_my_head import genre as gn
from rain_in_my_head import overview as ov
from rain_in_my_head import playlist as pl
from rain_in_my_head import schema_info as si
from rain_in_my_head import sql_examples as sq

WEB_DIST = config.ROOT / "web" / "dist"
NO_DATABASE = "No database yet. Run `uv run rain-in-my-head fetch` then `uv run rain-in-my-head build`."
PRESET_NAMES = {"last30": "Last 30 days", "last12m": "Last 12 months", "ytd": "This year", "all": "All time", "custom": "Custom"}

app = FastAPI(title="Rain in My Head", docs_url="/api/docs", openapi_url="/api/openapi.json")


class NoDatabase(Exception):
    pass


@app.exception_handler(NoDatabase)
def _no_database(request: Request, exc: NoDatabase) -> JSONResponse:
    return JSONResponse({"error": "no_database", "message": NO_DATABASE}, status_code=503)


def _require_db() -> None:
    if not config.DB_PATH.exists():
        raise NoDatabase()


# ---- JSON helpers ------------------------------------------------------------

def _value(v):
    """A pandas/numpy cell as plain JSON: dates as ISO, NaN as null."""
    if v is None:
        return None
    if isinstance(v, pd.Timestamp):
        return v.date().isoformat() if v == v.normalize() else v.isoformat()
    if isinstance(v, date):
        return v.isoformat()
    if hasattr(v, "item"):
        v = v.item()
    if isinstance(v, float) and math.isnan(v):
        return None
    return v


def _records(df: pd.DataFrame, columns: dict[str, str]) -> list[dict]:
    """Rows of `df` as dicts, keeping and renaming only `columns` (source -> output name)."""
    return [
        {out: _value(row[src]) for src, out in columns.items()}
        for row in df[list(columns)].astype(object).to_dict("records")
    ]


# ---- Routes ------------------------------------------------------------------

@app.get("/api/health")
def health() -> dict:
    exists = config.DB_PATH.exists()
    return {"ok": True, "db": exists, "db_mtime": config.DB_PATH.stat().st_mtime if exists else None}


@app.get("/api/overview")
def overview(
    preset: Literal["last30", "last12m", "ytd", "all", "custom"] = "last12m",
    start: date | None = None,
    end: date | None = None,
    grain: Literal["week", "month", "year"] = "month",
    period: str | None = None,
) -> dict:
    _require_db()
    data = ov.load_plays(config.DB_PATH)
    if data.empty:
        return {"empty": True, "reason": "no_scrobbles"}

    custom = None
    if preset == "custom":
        if start is None or end is None:
            raise HTTPException(422, "preset=custom needs start and end")
        if start > end:
            raise HTTPException(422, "start must not be after end")
        custom = (start, end)
    grain_name = grain.capitalize()
    first_day, last_day = ov.data_bounds(data)
    base_start, base_end = ov.resolve_range(data, PRESET_NAMES[preset], custom)

    periods = ov.over_time(data, base_start, base_end, grain_name)
    start_, end_, selected = ov.select_period(periods, base_start, base_end, grain_name, period)
    df = ov.in_range(data, start_, end_)
    inner = ov.inner_grain(grain_name, selected)

    result: dict = {
        "range": {
            "start": start_.isoformat(), "end": end_.isoformat(),
            "base_start": base_start.isoformat(), "base_end": base_end.isoformat(),
            "data_first": first_day.isoformat(), "data_last": last_day.isoformat(),
            "data_through": data["played_local"].max().isoformat(),
        },
        "grain": grain,
        "selected": None if selected is None else {"label": selected, "start": start_.isoformat(), "end": end_.isoformat()},
        "inner_grain": inner.lower(),
        "over_time": _records(periods, {"period": "period", "played_local": "start", "scrobbles": "scrobbles", "hours": "hours"}),
    }
    if df.empty:
        return {**result, "empty": True, "reason": "no_plays_in_range"}

    top = ov.top_lists(df)
    genres = ov.genre_shares(df, inner)
    result.update({
        "empty": False,
        "kpis": [{"label": label, "value": _value(value), "delta": _value(change)}
                 for label, (value, change) in ov.kpis(df, ov.previous(data, start_, end_)).items()],
        "top": {k: _records(v, {"name": "name", "plays": "plays"}) for k, v in top.items()},
        "top_per_year": _records(ov.top_per_year(data), {"year": "year", "artist_name": "artist", "plays": "plays", "share": "share"}),
        "heatmap": _records(ov.heatmap(df), {"weekday_name": "weekday", "hour": "hour", "plays": "plays"}),
        "new_artists": _records(ov.new_artists(data, start_, end_, inner), {"artist_first_play": "start", "new_artists": "count"}),
        "new_share": ov.new_share(df),
        "genres": None if genres is None else {
            "y_max": genres[1],
            "panels": [
                {"genre": g, "points": _records(genres[2][genres[2]["primary_genre"] == g],
                                                {"played_local": "start", "share": "share", "plays": "plays"})}
                for g in genres[0]
            ],
        },
        "listener_buckets": None if genres is None else _records(ov.listener_buckets(df), {"bucket": "bucket", "share": "share"}),
        "loved": _records(ov.loved(data, df), {"artist_name": "artist", "track_name": "track", "plays": "plays"}),
        "coverage": _records(ov.coverage(df), {"Check": "check", "Coverage": "coverage"}),
    })
    return result


# ---- Genre -------------------------------------------------------------------

def _genre_view(genre: str | None, start: date | None, end: date | None):
    """The genre (asked for, else the most played), its range and plays, as the Streamlit page resolves them."""
    _require_db()
    all_genres = gn.genres(config.DB_PATH)
    if not all_genres:
        return all_genres, None, None, None, None
    chosen = genre if genre in all_genres else all_genres[0]
    start_ = start.isoformat() if start else None
    end_ = (end or date.today()).isoformat()
    plays = gn.genre_plays(config.DB_PATH, chosen, start_ or gn.ALL_TIME_START, end_)
    return all_genres, chosen, start_, end_, plays


@app.get("/api/genre")
def genre(genre: str | None = None, start: date | None = None, end: date | None = None) -> dict:
    all_genres, chosen, start_, end_, plays = _genre_view(genre, start, end)
    if chosen is None:
        return {"genres": [], "genre": None, "reason": "no_tags"}
    return {
        "genres": all_genres,
        "genre": chosen,
        "range_label": gn.range_label(start_, end_),
        "plays": len(plays),
        "artists": [] if plays.empty else _records(
            gn.artists(plays), {"artist_key": "artist_key", "name": "name", "art": "art", "thumb": "thumb", "plays": "plays"}
        ),
    }


@app.get("/api/genre/songs")
def genre_songs(artist_key: str, genre: str | None = None, start: date | None = None, end: date | None = None) -> dict:
    _, chosen, _, _, plays = _genre_view(genre, start, end)
    if chosen is None or plays.empty or artist_key not in set(plays["artist_key"]):
        raise HTTPException(404, "No plays by that artist in this genre and range")
    artist = gn.artists(plays).set_index("artist_key").loc[artist_key]
    return {
        "artist": {
            "name": artist["name"],
            "art": None if pd.isna(artist["art"]) else gn.thumb(artist["art"], "174s"),
            "plays": _value(artist["plays"]),
        },
        "songs": _records(
            gn.songs(plays, artist_key),
            {"track_key": "track_key", "name": "name", "album_name": "album", "art": "art", "thumb": "thumb", "plays": "plays"},
        ),
    }


# ---- SQL ---------------------------------------------------------------------

@app.get("/api/sql/meta")
def sql_meta() -> dict:
    _require_db()
    return {"examples": sq.EXAMPLES, "schema": sq.schema(config.DB_PATH).to_dict("records")}


class SqlRequest(BaseModel):
    sql: str


@app.post("/api/sql")
def sql(body: SqlRequest) -> dict:
    _require_db()
    try:
        result = sq.run_readonly(config.DB_PATH, body.sql)
    except Exception as e:  # shown on the page, as Streamlit does
        return {"error": str(e)}
    return {
        "columns": [str(c) for c in result.columns],
        # So the page can write floats as pandas does (12.0, not 12) in tables and CSV.
        "float_columns": [i for i, t in enumerate(result.dtypes) if pd.api.types.is_float_dtype(t)],
        "rows": [[_value(v) for v in row] for row in result.astype(object).itertuples(index=False)],
        "row_count": len(result),
    }


# ---- Schema ------------------------------------------------------------------

def _schema() -> list[dict]:
    _require_db()
    return si.read_schema(config.DB_PATH)


@app.get("/api/schema")
def schema() -> dict:
    return si.build_data(_schema(), si.load_layout(si.layout_path(config.DB_PATH)))


class Layout(BaseModel):
    positions: dict[str, dict]


def _save_layout(positions: dict, names: set[str]) -> None:
    try:
        si.save_layout(si.layout_path(config.DB_PATH), positions, names)
    except OSError as e:
        raise HTTPException(500, f"Couldn't save the layout: {e.strerror}")


@app.put("/api/schema/layout", status_code=204)
def save_schema_layout(body: Layout) -> Response:
    _save_layout(body.positions, {o["name"] for o in _schema()})
    return Response(status_code=204)


@app.delete("/api/schema/layout")
def reset_schema_layout() -> dict:
    """Saves the default positions (as Streamlit's "Reset layout" does) and returns them."""
    names = [o["name"] for o in _schema()]
    defaults = si.default_positions(names)
    _save_layout(defaults, set(names))
    return {"positions": defaults}


# ---- Playlists ---------------------------------------------------------------

def _connect() -> sqlite3.Connection:
    _require_db()
    return sqlite3.connect(config.DB_PATH, timeout=30)


def _play_bounds(conn: sqlite3.Connection) -> tuple[date, date]:
    first, last = conn.execute("SELECT MIN(date(played_local)), MAX(date(played_local)) FROM v_plays").fetchone()
    return pd.Timestamp(first).date(), pd.Timestamp(last).date()


@functools.lru_cache(maxsize=16)
def _binges(db_mtime: float, min_plays: int, window_days: int, since: int, until: int) -> pd.DataFrame:
    with sqlite3.connect(config.DB_PATH, timeout=30) as conn:
        return pl.binges(conn, min_plays, window_days, since, until)


@app.get("/api/playlists/meta")
def playlists_meta() -> dict:
    with _connect() as conn:
        first, last = _play_bounds(conn)
    return {
        "first": first.isoformat(), "last": last.isoformat(),
        "weekdays": pl.WEEKDAY_FULL, "spans": pl.SPANS, "rank_by": pl.RANK_BY,
        "discovery_orders": pl.DISCOVERY_ORDERS, "windows": pl.WINDOWS,
        "binge_orders": pl.BINGE_ORDER_LABELS,
    }


@app.get("/api/playlists/spotify")
def playlists_spotify() -> dict:
    return {"connected": config.SPOTIFY_TOKEN_PATH.exists()}


class PlaylistRequest(BaseModel):
    kind: Literal["slot", "discoveries", "binges"]
    size: int = 50
    min_plays: int
    # Time slot
    days: list[str] = ["Friday"]
    hours: tuple[int, int] = (17, 19)
    span: str = "All time"
    since: date | None = None
    until: date | None = None
    # Discoveries
    year: int | None = None
    rank_by: Literal["year", "ever"] = "year"
    order: str = "Ranking"
    # Binges
    years: tuple[int, int] | None = None
    window_days: Literal[1, 7, 30] = 7
    binge_order: Literal["oldest", "newest", "biggest"] = "oldest"


def _preview(body: PlaylistRequest) -> pl.Preview:
    with _connect() as conn:
        first, last = _play_bounds(conn)
        if body.kind == "slot":
            if body.span not in pl.SPANS or any(d not in pl.WEEKDAY_FULL for d in body.days):
                raise HTTPException(422, "Unknown span or weekday")
            custom = (body.since or first, body.until or last) if body.span == "Custom" else None
            return pl.preview_slot(conn, first, last, body.days, body.hours, body.span, custom, body.size, body.min_plays)
        if body.kind == "discoveries":
            year = body.year if body.year is not None else max(first.year, last.year - 1)
            return pl.preview_discoveries(conn, first, year, body.rank_by, body.order, body.size, body.min_plays)
    years = body.years or (first.year, last.year)
    episodes = _binges(config.DB_PATH.stat().st_mtime, body.min_plays, body.window_days, *years)
    return pl.preview_binges(episodes, first, last, years, body.window_days, body.min_plays, body.size, body.binge_order)


@app.post("/api/playlists/preview")
def playlists_preview(body: PlaylistRequest) -> dict:
    p = _preview(body)
    result = {"title": p.title, "note": p.note, "warning": p.warning}
    if p.warning:
        return result
    return {
        **result,
        "info": p.info, "caption": p.caption, "name": p.name, "description": p.description,
        "columns": [{"key": k, "label": c.label, "kind": c.kind, "help": c.help} for k, c in p.columns.items()],
        "rows": _records(p.rows, {k: k for k in p.columns}),
        "candidate_count": len(p.ranked),
    }


class CreateRequest(PlaylistRequest):
    name: str
    public: bool = False


def _event(kind: str, data: dict) -> str:
    return f"event: {kind}\ndata: {json.dumps(data)}\n\n"


@app.post("/api/playlists/create")
def playlists_create(body: CreateRequest) -> StreamingResponse:
    """Matches tracks on Spotify and creates the playlist, streaming progress as server-sent events."""
    p = _preview(body)
    if p.warning:
        raise HTTPException(422, p.warning)
    events: queue.Queue[str | None] = queue.Queue()

    def work() -> None:
        from rain_in_my_head.build import connect
        from rain_in_my_head.spotify import SpotifyAuthError, SpotifyClient

        try:
            client = SpotifyClient(config.spotify_client_id(), config.SPOTIFY_TOKEN_PATH)
            conn = connect(config.DB_PATH)  # ensures the spotify_matches cache table exists
            events.put(_event("progress", {"fraction": 0.0, "message": "Matching tracks on Spotify…"}))
            matched = pl.match_tracks(conn, client, p.ranked, p.size,
                                      progress=lambda f, msg: events.put(_event("progress", {"fraction": f, "message": msg})))
            hits = matched[matched["spotify_uri"].notna()]
            if p.reorder:
                hits = p.reorder(hits)
            url = client.create_playlist(body.name, p.description, list(hits["spotify_uri"]), public=body.public)
            misses = matched[matched["spotify_uri"].isna()]
            events.put(_event("done", {"url": url, "name": body.name, "count": len(hits),
                                       "misses": _records(misses, {"artist": "artist", "track": "track"})}))
        except (SpotifyAuthError, SystemExit) as e:
            events.put(_event("error", {"message": str(e)}))
        except Exception as e:  # anything else still ends the stream with a message
            events.put(_event("error", {"message": f"{type(e).__name__}: {e}"}))
        finally:
            events.put(None)

    threading.Thread(target=work, daemon=True).start()

    def stream():
        while (item := events.get()) is not None:
            yield item

    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})


# ---- Built frontend ----------------------------------------------------------

@app.get("/{path:path}", include_in_schema=False)
def frontend(path: str):
    """Files from web/dist, and index.html for every other path so the app's own routes work."""
    if path.startswith("api/"):
        raise HTTPException(404)
    if not (WEB_DIST / "index.html").exists():
        return PlainTextResponse(
            "The TypeScript dashboard isn't built yet. Run `npm install && npm run build` in web/, "
            "or use `npm run dev` there for development.", status_code=503,
        )
    file = (WEB_DIST / path).resolve()
    if path and file.is_file() and file.is_relative_to(WEB_DIST.resolve()):
        return FileResponse(file)
    return FileResponse(WEB_DIST / "index.html")
