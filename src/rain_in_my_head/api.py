"""JSON API for the TypeScript dashboard (web/). Run: uv run rain-in-my-head serve

Every number comes from the same functions the Streamlit pages use (rain_in_my_head.overview, ...), so the
two dashboards always agree. Also serves the built frontend from web/dist. Contract:
specs/003-typescript-dashboard/contracts/api.md
"""

from __future__ import annotations

import contextlib
import functools
import hashlib
import json
import math
import queue
import sqlite3
import threading
from datetime import date
from urllib.parse import urlsplit
from typing import Literal

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import (
    FileResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
    StreamingResponse,
)
from pydantic import BaseModel, Field

from rain_in_my_head import access, neon, usage, viewers
from rain_in_my_head import artist as ar
from rain_in_my_head import config
from rain_in_my_head import genre as gn
from rain_in_my_head import overview as ov
from rain_in_my_head import playlist as pl
from rain_in_my_head import schema_info as si
from rain_in_my_head import sql_examples as sq
from rain_in_my_head.build import connect_readonly

WEB_DIST = config.ROOT / "web" / "dist"
PRESET_NAMES = {"last30": "Last 30 days", "last12m": "Last 12 months", "ytd": "This year", "all": "All time", "custom": "Custom"}

# The hosted site serves no API docs: nothing there needs them, and they'd map every route for a stranger.
app = FastAPI(
    title="Rain in My Head",
    docs_url=None if config.HOSTED else "/api/docs",
    openapi_url=None if config.HOSTED else "/api/openapi.json",
)
# /api/visitors is the owner's usage report: it needs the owner connection, which only the Mac has (spec 012).
REFUSED_PREFIXES = ("/api/playlists", "/api/ai", "/api/visitors")
# The only routes under REFUSED_PREFIXES the hosted site answers: the Playlist Generator's form data and track
# preview, which read the two-year copy. Creating a playlist, the Spotify check and any route added under
# /api/playlists later stay refused until they are listed here and in access.API_ACCESS.
HOSTED_PLAYLIST_READS = frozenset({("GET", "/api/playlists/meta"), ("POST", "/api/playlists/preview")})


def _refused() -> JSONResponse:
    return JSONResponse({"error": "refused", "message": config.REFUSAL}, status_code=403)


def _error(status: int, error: str, message: str) -> JSONResponse:
    return JSONResponse({"error": error, "message": message}, status_code=status)


def _session_cookie(request: Request) -> str | None:
    return viewers.read_cookie(request.cookies.get("session"))


async def _session(request: Request) -> viewers.Session | None:
    """The logged-in person for this request, or None. Raises neon.NeonUnavailable if the visitor database is down."""
    session_id = _session_cookie(request)
    if session_id is None:
        return None
    return await run_in_threadpool(viewers.lookup_session, config.DATABASE_URL, session_id)


def _client_hash(request: Request) -> str:
    """A hash of the visitor's address, for the limit on visitors with no login. The address is never stored.
    Vercel sets X-Forwarded-For; the first entry is the visitor."""
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    address = forwarded or (request.client.host if request.client else "unknown")
    return hashlib.sha256(address.encode()).hexdigest()


UNAVAILABLE = ("unavailable","The site can't check codes right now. Try again in a minute.")


@app.middleware("http")
async def access_guard(request: Request, call_next):
    """On the hosted site, every data route needs a login whose pages allow it (specs/011-viewer-access).

    Registered before hosted_guard, so hosted_guard runs first: playlists, AI and writes are refused for
    everyone, logged in or not.
    """
    path, method = request.url.path, "GET" if request.method == "HEAD" else request.method
    if config.HOSTED and path.startswith("/api/") and (method, path) not in access.PUBLIC_ROUTES:
        try:
            session = await _session(request)
        except neon.NeonUnavailable:
            return _error(503, *UNAVAILABLE)
        if session is None:
            # No login: the guest pages open (open-dashboards-without-login). Anything else asks for a code.
            if not access.allowed(access.TIER_PAGES["guest"], method, path):
                return _error(403, "login_required", "Log in with your invite code.")
        else:
            if not (access.allowed(session.pages, method, path) or access.session_allowed(session.pages, method, path)):
                return _error(403, "not_available", "That page isn't available to you.")
            request.state.session = session  # the heavy routes and /api/events use it, so there's no second lookup
    return await call_next(request)


@app.middleware("http")
async def hosted_guard(request: Request, call_next):
    """On the hosted site, deny by default: only reads, plus pre-defined SQL (checked in `sql`) and login and logout, get through.

    Anything that writes, makes playlists or uses AI is refused, including routes added later
    (specs/009-public-dataset, research R4). The playlist form's data and preview (HOSTED_PLAYLIST_READS) are the
    two exceptions (openspec/changes/show-all-menus).
    """
    if config.HOSTED:
        path, method = request.url.path, request.method
        allowed = (
            (method in ("GET", "HEAD") and not path.startswith(REFUSED_PREFIXES))
            or (method == "POST" and path in ("/api/sql", "/api/login", "/api/logout", "/api/events"))
            or (("GET" if method == "HEAD" else method), path) in HOSTED_PLAYLIST_READS
        )
        if not allowed:
            return _refused()
    return await call_next(request)


class NoDatabase(Exception):
    pass


@app.exception_handler(NoDatabase)
def _no_database(request: Request, exc: NoDatabase) -> JSONResponse:
    return JSONResponse({"error": "no_database", "message": config.NO_DATABASE}, status_code=503)


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


def _records(df: pd.DataFrame, columns: dict[str, str] | list[str]) -> list[dict]:
    """Rows of `df` as dicts, keeping only `columns`: a list keeps names, a dict renames (source -> output)."""
    if isinstance(columns, list):
        columns = {c: c for c in columns}
    return [
        {out: _value(row[src]) for src, out in columns.items()}
        for row in df[list(columns)].astype(object).to_dict("records")
    ]


# ---- Routes ------------------------------------------------------------------

@app.get("/api/health")
def health() -> dict:
    if config.HOSTED:  # a stranger can ask this: say only that the app is up
        return {"ok": True}
    exists = config.DB_PATH.exists()
    return {"ok": True, "db": exists, "db_mtime": config.DB_PATH.stat().st_mtime if exists else None, "hosted": config.HOSTED}


# ---- Login (specs/011-viewer-access, contracts/api.md) -----------------------------------------------------

COOKIE_DAYS = config.SESSION_DAYS


class LoginRequest(BaseModel):
    code: str = Field(max_length=64)


def _me(session: viewers.Session) -> dict:
    return {"logged_in": True, "name": session.name, "tier": session.tier, "pages": sorted(session.pages)}


def _same_origin(request: Request) -> bool:
    """A login or logout must come from the site's own pages, not from a form on another site."""
    origin = request.headers.get("origin")
    return origin is None or urlsplit(origin).netloc == request.headers.get("host", request.url.netloc)


@app.get("/api/me")
async def me(request: Request):
    if not config.HOSTED:
        return {"local": True}  # on your Mac there is no login and every page opens
    try:
        session = await _session(request)
    except neon.NeonUnavailable:
        return _error(503, *UNAVAILABLE)
    # No login: the guest pages, so the dashboards open for anyone (open-dashboards-without-login).
    return _me(session) if session else {"logged_in": False, "pages": sorted(access.TIER_PAGES["guest"])}


@app.post("/api/login")
async def login(body: LoginRequest, request: Request):
    if not config.HOSTED:
        raise HTTPException(404)
    if not _same_origin(request):
        return _error(403, "refused", config.REFUSAL)
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    address = forwarded or (request.client.host if request.client else "unknown")
    try:
        session_id, session = await run_in_threadpool(viewers.attempt_login, config.DATABASE_URL, body.code, address)
    except viewers.SlowDown:
        return _error(429, "slow_down", "Too many tries. Wait a minute.")
    except viewers.Locked:
        return _error(423, "locked", "Too many tries. Try again later.")
    except viewers.BadCode:
        return _error(401, "bad_code", "That code didn't work.")
    except neon.NeonUnavailable:
        return _error(503, *UNAVAILABLE)
    response = JSONResponse(_me(session))
    response.set_cookie(
        "session", viewers.sign_cookie(session_id), max_age=COOKIE_DAYS * 86400, path="/",
        httponly=True, secure=viewers.cookie_secure(request), samesite="lax",
    )
    return response


@app.post("/api/logout", status_code=204)
async def logout(request: Request):
    if not config.HOSTED:
        raise HTTPException(404)
    if not _same_origin(request):
        return _error(403, "refused", config.REFUSAL)
    session_id = _session_cookie(request)
    if session_id:
        try:
            await run_in_threadpool(viewers.end_session, config.DATABASE_URL, session_id)
        except neon.NeonUnavailable:
            return _error(503, *UNAVAILABLE)
    response = Response(status_code=204)
    response.delete_cookie("session", path="/", httponly=True, secure=viewers.cookie_secure(request), samesite="lax")
    return response


# ---- Usage reports (specs/012-usage-tracking, contracts/api.md) --------------------------------------------

class EventRequest(BaseModel):
    event: Literal["open", "leave"]
    visit: str = Field(max_length=32)
    page: str = Field(max_length=40)
    seconds: int | None = None  # leave only; clamped to 0..1800 when stored


@app.post("/api/events", status_code=204)
async def events(body: EventRequest, request: Request):
    """The browser says a page was opened or left. Always answers 204: a dropped, capped or failed report is not
    something the visitor should ever see (FR-005, FR-030). On your Mac (not hosted) nothing is stored."""
    if not config.HOSTED:
        return Response(status_code=204)
    if not _same_origin(request):
        return _error(403, "refused", config.REFUSAL)
    session = request.state.session
    try:
        if body.event == "open":
            await run_in_threadpool(usage.report_open, config.DATABASE_URL, session.viewer_id, session.pages, body.page, body.visit)
        else:
            await run_in_threadpool(
                usage.report_leave, config.DATABASE_URL, session.viewer_id, session.pages, body.page, body.visit, body.seconds or 0
            )
    except (neon.NeonUnavailable, neon.NeonError):
        pass  # a lost report is fine
    return Response(status_code=204)


@app.get("/api/visitors")
def visitors(env: str = "prod", range: str = "30d", person: str | None = None):
    """The owner's usage report, for the Visitors page. It needs the owner connection from .env, which only your
    Mac has, so on the hosted site it is refused for everyone (REFUSED_PREFIXES, and again here)."""
    if config.HOSTED:
        return _refused()
    try:
        return usage.visitors_payload(env, range, person)
    except usage.UsageError as e:
        return _error(422, "bad_request", str(e))
    except SystemExit as e:  # the owner connection string isn't in .env: the message names the variable, never a value
        return _error(503, "not_configured", str(e))
    except neon.NeonError as e:  # shown to the owner only: this route never runs on the hosted site
        return _error(503, "unavailable", f"The visitor database refused the query ({e}). If the usage table is missing, run `viewer init --env {env}`.")
    except neon.NeonUnavailable:
        return _error(503, "unavailable", "The visitor database can't be reached right now.")


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
    list_start, list_end = ar.list_period(start_, end_, selected is not None)
    result.update({
        "empty": False,
        "kpis": [{"label": label, "value": _value(value), "delta": _value(change)}
                 for label, (value, change) in ov.kpis(df, ov.previous(data, start_, end_)).items()],
        "top": {
            "artists": _records(top["artists"], ["name", "plays", "artist_key"]),
            "tracks": _records(top["tracks"], ["name", "plays"]),
            "albums": _records(top["albums"], ["name", "plays"]),
        },
        "top_per_year": _records(ov.top_per_year(data), {"year": "year", "artist_name": "artist", "plays": "plays", "share": "share"}),
        "heatmap": _records(ov.heatmap(df), {"weekday_name": "weekday", "hour": "hour", "plays": "plays"}),
        "new_artists": _records(ov.new_artists(data, start_, end_, inner), {"artist_first_play": "start", "new_artists": "count"}),
        "new_share": ov.new_share(df),
        "new_artist_list": {
            "label": ar.period_label(list_start, list_end),
            "start": list_start.isoformat(), "end": list_end.isoformat(),
            "artists": _records(ar.new_artists(config.DB_PATH, list_start, list_end),
                                ["artist_key", "name", "thumb", "plays"]),
        },
        "genres": None if genres is None else {
            "y_max": genres[1],
            "panels": [
                {"genre": g, "points": _records(genres[2][genres[2]["primary_genre"] == g],
                                                {"played_local": "start", "share": "share", "plays": "plays"})}
                for g in genres[0]
            ],
        },
        "listener_buckets": None if genres is None else _records(ov.listener_buckets(df), ["bucket", "share"]),
        "loved": _records(ov.loved(data, df), {"artist_name": "artist", "track_name": "track", "plays": "plays"}),
        "coverage": _records(ov.coverage(df), {"Check": "check", "Coverage": "coverage"}),
    })
    return result


# ---- The per-person limit on heavy routes (specs/012-usage-tracking) -------------------------------------------

def _heavy(request: Request, page: str, feature: str, detail: str | None = None) -> JSONResponse | None:
    """On the hosted site, count one heavy request for this person. Returns the response to send if they're over
    their limit (429) or the visitor database can't say (503), else None. Nothing is checked on your Mac."""
    if not config.HOSTED:
        return None
    session = getattr(request.state, "session", None)
    try:
        if session is None:  # no login: counted per hashed client address
            usage.heavy_request_anonymous(config.DATABASE_URL, _client_hash(request), page, feature)
        else:
            usage.heavy_request(config.DATABASE_URL, session.viewer_id, page, feature, detail)
    except usage.RateLimited as e:
        return JSONResponse(
            {"error": "rate_limited", "message": e.message, "retry_after": e.retry_after},
            status_code=429, headers={"Retry-After": str(e.retry_after)},
        )
    except (neon.NeonUnavailable, neon.NeonError):
        return _error(503, *UNAVAILABLE)
    return None


# ---- Genre -------------------------------------------------------------------

GenrePreset = Literal["last30", "last12m", "ytd", "all", "custom"]


def _genre_view(genre: str | None, preset: GenrePreset | None, start: date | None, end: date | None):
    """The genre (asked for, else the most played), its resolved range and plays.

    The range resolves as the Overview's does. Dates without a preset are Custom (old links); nothing at all is
    All time. Returns (all genres, chosen, range dict, v_plays rows in range, the genre's plays).
    """
    _require_db()
    all_genres = gn.genres(config.DB_PATH)
    if not all_genres:
        return all_genres, None, None, None, None
    chosen = genre if genre in all_genres else all_genres[0]
    if preset is None:
        preset = "custom" if start or end else "all"
    data = ov.load_plays(config.DB_PATH)
    first_day, last_day = ov.data_bounds(data)
    custom = None
    if preset == "custom":
        custom = (start or first_day, end or last_day)
        if custom[0] > custom[1]:
            raise HTTPException(422, "start must not be after end")
    start_, end_ = ov.resolve_range(data, PRESET_NAMES[preset], custom)
    rng = {
        "preset": preset, "start": start_.isoformat(), "end": end_.isoformat(),
        "data_first": first_day.isoformat(), "data_last": last_day.isoformat(),
    }
    plays = gn.genre_plays(config.DB_PATH, chosen, rng["start"], rng["end"])
    return all_genres, chosen, rng, ov.in_range(data, start_, end_), plays


@app.get("/api/genre")
def genre(genre: str | None = None, preset: GenrePreset | None = None, start: date | None = None, end: date | None = None) -> dict:
    all_genres, chosen, rng, df, plays = _genre_view(genre, preset, start, end)
    if chosen is None:
        return {"genres": [], "genre": None, "reason": "no_tags"}
    grain = gn.share_grain(date.fromisoformat(rng["start"]), date.fromisoformat(rng["end"]))
    color_index, share = gn.genre_share(df, chosen, grain)
    return {
        "genres": all_genres,
        "genre": chosen,
        "range": rng,
        "range_label": "All time" if rng["preset"] == "all" else gn.range_label(rng["start"], rng["end"]),
        "plays": len(plays),
        "share": {
            "grain": grain.lower(),
            "color_index": color_index,
            "points": _records(share, {"played_local": "start", "share": "share", "plays": "plays"}),
        },
        "artists": [] if plays.empty else _records(
            gn.artists(plays), ["artist_key", "name", "art", "thumb", "plays"]
        ),
    }


@app.get("/api/genre/songs")
def genre_songs(
    request: Request, artist_key: str, genre: str | None = None, preset: GenrePreset | None = None,
    start: date | None = None, end: date | None = None,
):
    # Checked before the work is done, so a limited person costs the free plan almost nothing. A not-found answer
    # below still counts as a use.
    if (limited := _heavy(request, "genre", "genre-songs")) is not None:
        return limited
    _, chosen, _, _, plays = _genre_view(genre, preset, start, end)
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


# ---- Listening slot ----------------------------------------------------------

SLOT_TOP = 100


@app.get("/api/slot")
def slot(
    day: str, hour: int, preset: GenrePreset | None = None, start: date | None = None, end: date | None = None,
) -> dict:
    """The tracks played in one weekday and hour (openspec/specs/listening-slot), most played first.

    The range resolves as the Genre page's does: dates without a preset are Custom, nothing at all is the last 12
    months (the Overview's default)."""
    _require_db()
    if day not in ov.WEEKDAYS:
        raise HTTPException(422, f"Unknown day: {day}")
    if not 0 <= hour <= 23:
        raise HTTPException(422, "hour must be 0-23")
    if preset is None:
        preset = "custom" if start or end else "last12m"
    data = ov.load_plays(config.DB_PATH)
    if data.empty:
        return {"day": day, "hour": hour, "range": None, "plays": 0, "distinct_tracks": 0, "busiest": False, "tracks": []}
    first_day, last_day = ov.data_bounds(data)
    custom = None
    if preset == "custom":
        custom = (start or first_day, end or last_day)
        if custom[0] > custom[1]:
            raise HTTPException(422, "start must not be after end")
    start_, end_ = ov.resolve_range(data, PRESET_NAMES[preset], custom)
    tracks, busiest = ov.slot_tracks(ov.in_range(data, start_, end_), day, hour)
    shown = tracks.head(SLOT_TOP).copy()
    art = ov.track_art(config.DB_PATH, list(shown["track_key"]))
    shown["thumb"] = [gn.thumb(art[k]) if k in art else None for k in shown["track_key"]]
    return {
        "day": day,
        "hour": hour,
        "range": {
            "preset": preset, "start": start_.isoformat(), "end": end_.isoformat(),
            "data_first": first_day.isoformat(), "data_last": last_day.isoformat(),
        },
        "range_label": PRESET_NAMES[preset] if preset != "custom" else gn.range_label(start_.isoformat(), end_.isoformat()),
        "plays": int(tracks["plays"].sum()),
        "distinct_tracks": len(tracks),
        "busiest": busiest,
        "tracks": _records(shown, ["track_key", "name", "artist", "artist_key", "thumb", "plays"]),
    }


# ---- Mainstream vs. niche ----------------------------------------------------

@app.get("/api/mainstream")
def mainstream(bucket: str, start: date | None = None, end: date | None = None) -> dict:
    """The artists in one Last.fm listener band (openspec/changes/mainstream-artists-page), most played first.

    `start` and `end` default to all time. The share is the band's share of plays with a known listener count."""
    _require_db()
    if bucket not in ov.LISTENER_LABELS:
        raise HTTPException(422, f"Unknown listener band: {bucket}")
    if start is not None and end is not None and start > end:
        raise HTTPException(422, "start must not be after end")
    data = ov.load_plays(config.DB_PATH)
    if data.empty:
        return {"bucket": bucket, "start": None, "end": None, "share": 0.0, "artists": []}
    first_day, last_day = ov.data_bounds(data)
    start_, end_ = start or first_day, end or last_day
    artists, share = ov.listener_band_artists(ov.in_range(data, start_, end_), bucket)
    return {
        "bucket": bucket,
        "start": start_.isoformat(),
        "end": end_.isoformat(),
        "share": _value(share),
        "artists": _records(artists, ["artist_key", "name", "listeners", "plays"]),
    }


# ---- Artist ------------------------------------------------------------------

@app.get("/api/artist")
def artist(artist: str | None = None, start: date | None = None, end: date | None = None, month: str | None = None) -> dict:
    """One artist's page (spec 001): header counts and songs in the period, all time without one.

    `month` (YYYY-MM) narrows the songs to that month; `monthly` and `first_played` are always returned."""
    _require_db()
    page = ar.artist_page(config.DB_PATH, artist, start, end, month) if artist else None
    if page is None:
        return {"found": False}
    return {
        "found": True,
        "artist_key": page.artist_key,
        "name": page.name,
        "cover": page.cover,
        "period": None if page.period is None else {
            "start": page.period[0].isoformat(), "end": page.period[1].isoformat(), "label": page.label,
        },
        "period_plays": page.period_plays,
        "all_time_plays": page.all_time_plays,
        "first_played": page.first_played,
        "monthly": [{"month": m, "plays": n} for m, n in page.monthly],
        "songs": _records(page.songs, {"track_key": "track_key", "name": "name", "album_name": "album", "thumb": "thumb", "plays": "plays"}),
    }


# ---- SQL ---------------------------------------------------------------------

@app.get("/api/sql/meta")
def sql_meta() -> dict:
    _require_db()
    return {"examples": sq.EXAMPLES, "schema": sq.schema(config.DB_PATH).to_dict("records"), "hosted": config.HOSTED}


class SqlRequest(BaseModel):
    sql: str | None = None
    example: str | None = None  # the name of one of sq.EXAMPLES


@app.post("/api/sql")
def sql(body: SqlRequest, request: Request):
    """Typed SQL locally. On the hosted site only a pre-defined query, by name: visitor text never runs."""
    _require_db()
    if config.HOSTED and (body.sql is not None or body.example not in sq.EXAMPLES):
        return _refused()
    if body.example is not None and body.example not in sq.EXAMPLES:
        raise HTTPException(422, f"Unknown example {body.example!r}")
    # Only a pre-defined query gets here when hosted, and only now: the refusals above leave no record (FR-011).
    if body.example and (limited := _heavy(request, "analyst", "query", body.example)) is not None:
        return limited
    try:
        result = sq.run_example(config.DB_PATH, body.example) if body.example else sq.run_readonly(config.DB_PATH, body.sql or "")
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

def _connect() -> contextlib.closing[sqlite3.Connection]:
    _require_db()
    return contextlib.closing(connect_readonly(config.DB_PATH))


@functools.lru_cache(maxsize=16)
def _binges(db_mtime: float, min_plays: int, window_days: int, since: int, until: int) -> pd.DataFrame:
    with contextlib.closing(connect_readonly(config.DB_PATH)) as conn:
        return pl.binges(conn, min_plays, window_days, since, until)


@app.get("/api/playlists/meta")
def playlists_meta() -> dict:
    with _connect() as conn:
        first, last = pl.play_bounds(conn)
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
    kind: Literal["slot", "discoveries", "binges", "sql"]
    size: int = 50
    min_plays: int = 1
    # SQL (owner's Mac only: typed SQL never runs on the hosted site)
    sql: str | None = None
    example: str | None = None  # a pre-defined query, by name (the only SQL that runs on the hosted site)
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
    if body.kind == "sql":
        try:
            result = sq.run_example(config.DB_PATH, body.example) if body.example else sq.run_readonly(config.DB_PATH, body.sql or "")
        except Exception as e:  # invalid SQL or an attempted write: shown on the page, as on Analyst
            raise HTTPException(422, str(e)) from e
        return pl.preview_sql(result)
    with _connect() as conn:
        first, last = pl.play_bounds(conn)
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
def playlists_preview(body: PlaylistRequest, request: Request):
    if body.kind == "sql":
        # As on Analyst: the hosted site runs only a pre-defined query, by name; visitor text never runs.
        if config.HOSTED and (body.sql is not None or body.example not in sq.EXAMPLES):
            return _refused()
        if body.example is not None and body.example not in sq.EXAMPLES:
            raise HTTPException(422, f"Unknown example {body.example!r}")
        if body.example and (limited := _heavy(request, "playlists", "sql", body.example)) is not None:
            return limited
    _require_db()
    p = _preview(body)
    result = {"title": p.title, "note": p.note, "warning": p.warning, "missing": getattr(p, "missing", []),
              "returned": getattr(p, "returned", [])}
    if p.warning:
        return result
    return {
        **result,
        "info": p.info, "caption": p.caption, "name": p.name, "description": p.description,
        "columns": [{"key": k, "label": c.label, "kind": c.kind, "help": c.help} for k, c in p.columns.items()],
        "rows": _records(p.rows, list(p.columns)),
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
            url, hits, misses = pl.create_on_spotify(
                conn, client, p.ranked, p.size, body.name, p.description, p.reorder, public=body.public,
                progress=lambda f, msg: events.put(_event("progress", {"fraction": f, "message": msg})),
            )
            events.put(_event("done", {"url": url, "name": body.name, "count": len(hits),
                                       "misses": _records(misses, ["artist", "track"])}))
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


# ---- Every data route must say who may use it --------------------------------------------------------------

def check_routes() -> None:
    """Stop the app from starting if an /api route that reads data has no entry in access.API_ACCESS.

    Routes under REFUSED_PREFIXES (except HOSTED_PLAYLIST_READS), and anything that isn't a GET or a listed POST,
    are refused by hosted_guard for everyone, so they need no entry (FR-017, constitution VII).
    """
    listed = set(access.API_ACCESS) | set(access.PUBLIC_ROUTES) | set(access.SESSION_ROUTES)
    local_only = {"/api/docs", "/api/openapi.json"}  # not served at all when hosted
    missing = sorted(
        f"{method} {route.path}"
        for route in app.routes
        if getattr(route, "path", "").startswith("/api/")
        and route.path not in local_only
        for method in (getattr(route, "methods", None) or ())
        if method in ("GET", "POST") and (method, route.path) not in listed
        and (not route.path.startswith(REFUSED_PREFIXES) or (method, route.path) in HOSTED_PLAYLIST_READS)
    )
    if missing:
        raise RuntimeError("These routes have no access rule in access.py: " + ", ".join(missing))


check_routes()


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
