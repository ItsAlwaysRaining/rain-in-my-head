"""Visitors with no login on the hosted site (openspec/changes/open-dashboards-without-login)."""

import calendar
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from rain_in_my_head import api, config, neon, usage

SCHEMA = Path(__file__).resolve().parents[1] / "src" / "rain_in_my_head" / "schema.sql"


@pytest.fixture
def hosted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """The app in hosted mode with a small local database and no visitor database."""
    path = tmp_path / "listening.db"
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA.read_text())
    day = calendar.timegm((2026, 3, 2, 12, 0, 0))
    conn.execute(
        "INSERT INTO scrobbles (played_at, artist_name, track_name, album_name, artist_key, track_key) "
        "VALUES (?, 'Artist A', 'Song A', 'Album', 'artist-a', 'artist-a\tSong A')",
        (day,),
    )
    conn.commit()
    conn.close()
    monkeypatch.setattr(config, "HOSTED", True)
    monkeypatch.setattr(config, "DB_PATH", path)
    return TestClient(api.app)


def test_anonymous_reads_a_guest_page(hosted: TestClient):
    response = hosted.get("/api/artist", params={"artist": "artist-a"})
    assert response.status_code == 200
    assert response.json()["name"] == "Artist A"


def test_anonymous_me_lists_the_guest_pages(hosted: TestClient):
    body = hosted.get("/api/me").json()
    assert body["logged_in"] is False
    assert "overview" in body["pages"]
    assert "visitors" not in body["pages"]


def test_anonymous_cannot_open_the_visitors_page(hosted: TestClient):
    # The hosted site refuses the Visitors data for everyone (REFUSED_PREFIXES), so it stays closed to anonymous visitors.
    response = hosted.get("/api/visitors")
    assert response.status_code == 403
    assert response.json()["error"] == "refused"


def test_anonymous_cannot_create_a_playlist(hosted: TestClient):
    response = hosted.post("/api/playlists/create", json={})
    assert response.status_code == 403
    assert response.json() == {"error": "refused", "message": config.REFUSAL}


def test_anonymous_typed_sql_is_refused(hosted: TestClient):
    response = hosted.post("/api/sql", json={"sql": "select 1"})
    assert response.json()["error"] == "refused"


def test_anonymous_events_are_refused_and_not_stored(hosted: TestClient):
    response = hosted.post("/api/events", json={"event": "open", "page": "overview", "visit": "v1"})
    assert response.status_code == 403
    assert response.json()["error"] == "login_required"


def test_anonymous_predefined_query_is_allowed(hosted: TestClient, monkeypatch: pytest.MonkeyPatch):
    counted: list[str] = []
    monkeypatch.setattr(usage, "heavy_request_anonymous", lambda url, h, page, feature: counted.append(h))
    response = hosted.post("/api/sql", json={"example": "Top artists this year"}, headers={"x-forwarded-for": "203.0.113.9"})
    assert response.json().get("error") != "refused"
    assert len(counted) == 1


def test_anonymous_limit_counts_a_hash_not_the_address(hosted: TestClient, monkeypatch: pytest.MonkeyPatch):
    counted: list[str] = []
    monkeypatch.setattr(usage, "heavy_request_anonymous", lambda url, h, page, feature: counted.append(h))
    hosted.post("/api/sql", json={"example": "Top artists this year"}, headers={"x-forwarded-for": "203.0.113.9"})
    assert "203.0.113.9" not in counted[0]
    assert len(counted[0]) == 64


def test_anonymous_limit_refuses_past_the_minute_allowance(monkeypatch: pytest.MonkeyPatch):
    answers = iter([[], [{"n": "0"}]])  # the insert finds the minute full; the day count is still low
    monkeypatch.setattr(neon, "query", lambda url, sql, params=(): next(answers))
    with pytest.raises(usage.RateLimited) as refused:
        usage.heavy_request_anonymous("postgres://x", "h", "analyst", "query")
    assert refused.value.retry_after == 60


def test_anonymous_limit_refuses_past_the_day_allowance(monkeypatch: pytest.MonkeyPatch):
    answers = iter([[], [{"n": str(usage.HEAVY_PER_DAY)}]])
    monkeypatch.setattr(neon, "query", lambda url, sql, params=(): next(answers))
    with pytest.raises(usage.RateLimited) as refused:
        usage.heavy_request_anonymous("postgres://x", "h", "analyst", "query")
    assert "today's limit" in refused.value.message
    assert 1 <= refused.value.retry_after <= 86400
