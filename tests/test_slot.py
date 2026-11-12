"""The Listening slot page: tracks for one weekday and hour (openspec/specs/listening-slot)."""

import calendar
import os
import sqlite3
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from rain_in_my_head import access, api, config
from rain_in_my_head import overview as ov

SCHEMA = Path(__file__).resolve().parents[1] / "src" / "rain_in_my_head" / "schema.sql"

# 5 March 2026 is a Thursday, 2 March a Monday.
PLAYS = [
    # (artist, track, day, hour, image_url)
    ("Hozier", "Too Sweet", "2026-03-05", 15, "https://img/300x300/a.jpg"),
    ("Hozier", "Too Sweet", "2026-03-12", 15, "https://img/300x300/a.jpg"),
    ("bbno$", "Edamame", "2026-03-05", 15, None),
    ("bbno$", "Edamame", "2026-03-05", 16, None),
    ("Geese", "Cobra", "2026-03-02", 15, None),
]


@pytest.fixture(autouse=True)
def utc(monkeypatch: pytest.MonkeyPatch):
    # v_plays converts to local time; pin it so the hours below are the hours stored.
    monkeypatch.setenv("TZ", "UTC")
    time.tzset()
    yield
    monkeypatch.delenv("TZ")
    time.tzset()


@pytest.fixture
def db(tmp_path: Path) -> Path:
    path = tmp_path / "listening.db"
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA.read_text())
    for i, (artist, track, day, hour, image) in enumerate(PLAYS):
        key = artist.lower()
        conn.execute(
            "INSERT INTO scrobbles (played_at, artist_name, track_name, album_name, image_url, artist_key, track_key) "
            "VALUES (?, ?, ?, 'Album', ?, ?, ?)",
            (calendar.timegm((*map(int, day.split("-")), hour, 10, 0)) + i, artist, track, image, key, f"{key}\t{track.lower()}"),
        )
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def client(db: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(config, "DB_PATH", db)
    return TestClient(api.app)


ALL = {"preset": "all"}


def test_slot_lists_its_tracks_most_played_first(client: TestClient):
    body = client.get("/api/slot", params={"day": "Thu", "hour": 15, **ALL}).json()

    assert [(t["name"], t["artist"], t["plays"]) for t in body["tracks"]] == [("Too Sweet", "Hozier", 2), ("Edamame", "bbno$", 1)]
    assert body["plays"] == 3 and body["distinct_tracks"] == 2
    assert body["tracks"][0]["artist_key"] == "hozier"


def test_plays_match_the_heatmap_square(client: TestClient, db: Path):
    body = client.get("/api/slot", params={"day": "Thu", "hour": 15, **ALL}).json()
    heat = ov.heatmap(ov.load_plays(db)).set_index(["weekday_name", "hour"])["plays"]

    assert body["plays"] == heat.loc[("Thu", 15)]


def test_busiest_slot_is_flagged(client: TestClient):
    assert client.get("/api/slot", params={"day": "Thu", "hour": 15, **ALL}).json()["busiest"] is True
    assert client.get("/api/slot", params={"day": "Thu", "hour": 16, **ALL}).json()["busiest"] is False


def test_tracks_carry_a_small_thumbnail_when_known(client: TestClient):
    tracks = client.get("/api/slot", params={"day": "Thu", "hour": 15, **ALL}).json()["tracks"]

    assert tracks[0]["thumb"] == "https://img/64s/a.jpg"
    assert tracks[1]["thumb"] is None


def test_empty_slot_has_no_tracks(client: TestClient):
    body = client.get("/api/slot", params={"day": "Sun", "hour": 4, **ALL}).json()

    assert body["tracks"] == [] and body["plays"] == 0 and body["busiest"] is False


def test_dates_without_a_preset_are_custom(client: TestClient):
    body = client.get("/api/slot", params={"day": "Thu", "hour": 15, "start": "2026-03-01", "end": "2026-03-07"}).json()

    assert body["range"]["preset"] == "custom"
    assert body["plays"] == 2  # the 12 March play is outside the range


@pytest.mark.parametrize("params", [{"day": "Thursday", "hour": 15}, {"day": "Thu", "hour": 24}, {"day": "Thu", "hour": -1}])
def test_unknown_day_or_hour_is_refused(client: TestClient, params: dict):
    assert client.get("/api/slot", params=params).status_code == 422


def test_start_after_end_is_refused(client: TestClient):
    response = client.get("/api/slot", params={"day": "Thu", "hour": 15, "start": "2026-03-10", "end": "2026-03-01"})
    assert response.status_code == 422


def test_guest_can_open_the_slot_route(db: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(config, "HOSTED", True)
    monkeypatch.setattr(config, "DB_PATH", db)
    assert TestClient(api.app).get("/api/slot", params={"day": "Thu", "hour": 15}).status_code == 200
    assert "slot" in access.API_ACCESS[("GET", "/api/slot")]
