"""JSON API for the TypeScript dashboard (web/). Run: uv run listening serve

Every number comes from the same functions the Streamlit pages use (listening.overview, ...), so the
two dashboards always agree. Also serves the built frontend from web/dist. Contract:
specs/003-typescript-dashboard/contracts/api.md
"""

from __future__ import annotations

import math
from datetime import date
from typing import Literal

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse

from listening import config
from listening import overview as ov

WEB_DIST = config.ROOT / "web" / "dist"
NO_DATABASE = "No database yet. Run `uv run listening fetch` then `uv run listening build`."
PRESET_NAMES = {"last30": "Last 30 days", "last12m": "Last 12 months", "ytd": "This year", "all": "All time", "custom": "Custom"}

app = FastAPI(title="Listening", docs_url="/api/docs", openapi_url="/api/openapi.json")


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
