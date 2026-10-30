"""A small client for Neon's SQL-over-HTTPS endpoint (specs/011-viewer-access, research R1).

One POST per query, or one POST for a whole transaction, so it needs no Postgres driver and works on Vercel's
Python runtime, which can't hold a connection open. Values come back as text (`Neon-Raw-Text-Output`), so
callers cast what they need. A connection string is never put in an error message or a log.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import urlsplit

import httpx

TIMEOUT_SECONDS = 8  # the first query after Neon wakes from sleep takes about a second
# Neon's HTTP queries use the pooled host (`-pooler` after the endpoint id). Set by the spike in task T006.
POOLED = False


class NeonError(Exception):
    """The database refused the query (a bad statement, a missing privilege, a constraint). Safe to show the owner."""

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.code = code


class NeonUnavailable(Exception):
    """The database couldn't be reached or answered with a server error. Safe to show anyone."""


def _host(url: str) -> str:
    host = urlsplit(url).hostname or ""
    if POOLED and "-pooler" not in host:
        first, _, rest = host.partition(".")
        host = f"{first}-pooler.{rest}"
    return host


def _param(value: Any) -> Any:
    return value.isoformat() if isinstance(value, datetime) else value


def _post(url: str, body: dict) -> dict:
    headers = {
        "Neon-Connection-String": url,
        "Neon-Raw-Text-Output": "true",
        "Neon-Array-Mode": "true",
        "Content-Type": "application/json",
    }
    try:
        response = httpx.post(f"https://{_host(url)}/sql", json=body, headers=headers, timeout=TIMEOUT_SECONDS)
    except httpx.HTTPError:
        raise NeonUnavailable("The visitor database can't be reached.") from None
    if response.status_code == 400:
        info = response.json()
        raise NeonError(str(info.get("message", "The database refused the query.")), info.get("code"))
    if response.status_code != 200:
        raise NeonUnavailable(f"The visitor database answered with an error (HTTP {response.status_code}).")
    return response.json()


def _rows(result: dict) -> list[dict[str, str | None]]:
    names = [field["name"] for field in result.get("fields", [])]
    return [dict(zip(names, row)) for row in result.get("rows", [])]


def _statement(sql: str, params: tuple | list = ()) -> dict:
    return {"query": sql, "params": [_param(p) for p in params]}


def query(url: str, sql: str, params: tuple | list = ()) -> list[dict[str, str | None]]:
    """Run one statement. Rows are dicts of column name to text (or None)."""
    return _rows(_post(url, _statement(sql, params)))


def transaction(url: str, statements: list[tuple[str, tuple | list]]) -> list[list[dict[str, str | None]]]:
    """Run several statements as one transaction: all of them happen, or none. One list of rows per statement."""
    results = _post(url, {"queries": [_statement(sql, params) for sql, params in statements]}).get("results")
    if not isinstance(results, list):
        raise NeonUnavailable("The visitor database answered in an unexpected way.")
    return [_rows(r) for r in results]
