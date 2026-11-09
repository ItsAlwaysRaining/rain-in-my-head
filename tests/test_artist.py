"""The artist page's first play date, monthly counts and month filter (src/rain_in_my_head/artist.py)."""

import calendar
import sqlite3
from datetime import date
from pathlib import Path

import pytest

from rain_in_my_head.artist import artist_page

SCHEMA = Path(__file__).resolve().parents[1] / "src" / "rain_in_my_head" / "schema.sql"


def noon_utc(day: str) -> int:
    """Noon UTC on an ISO day: the same calendar day in every timezone the dashboard runs in."""
    y, m, d = map(int, day.split("-"))
    return calendar.timegm((y, m, d, 12, 0, 0))


@pytest.fixture
def db(tmp_path: Path) -> Path:
    path = tmp_path / "listening.db"
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA.read_text())
    rows = [
        ("2026-03-02", "Song A"),
        ("2026-03-15", "Song A"),
        ("2026-03-15", "Song B"),
        ("2026-06-10", "Song C"),
    ]
    for i, (day, track) in enumerate(rows):
        conn.execute(
            "INSERT INTO scrobbles (played_at, artist_name, track_name, album_name, artist_key, track_key) "
            "VALUES (?, 'Artist A', ?, 'Album', 'artist-a', ?)",
            (noon_utc(day) + i, track, f"artist-a\t{track}"),
        )
    conn.commit()
    conn.close()
    return path


def test_first_played_and_zero_filled_months_all_time(db: Path):
    page = artist_page(db, "artist-a", None, None)
    assert page.first_played == "2026-03-02"
    assert page.monthly == [("2026-03", 3), ("2026-04", 0), ("2026-05", 0), ("2026-06", 1)]


def test_single_play_day(tmp_path: Path):
    path = tmp_path / "one.db"
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA.read_text())
    conn.execute(
        "INSERT INTO scrobbles (played_at, artist_name, track_name, album_name, artist_key, track_key) "
        "VALUES (?, 'Artist A', 'Song A', 'Album', 'artist-a', 'artist-a\tSong A')",
        (noon_utc("2026-11-09"),),
    )
    conn.commit()
    conn.close()
    page = artist_page(path, "artist-a", None, None)
    assert page.first_played == "2026-11-09"
    assert page.monthly == [("2026-11", 1)]


def test_monthly_follows_the_period(db: Path):
    page = artist_page(db, "artist-a", date(2026, 1, 1), date(2026, 3, 31))
    assert page.monthly == [("2026-01", 0), ("2026-02", 0), ("2026-03", 3)]
    assert page.first_played == "2026-03-02"  # first play is all time, not in the period


def test_month_filter_narrows_songs(db: Path):
    page = artist_page(db, "artist-a", None, None, month="2026-06")
    assert list(page.songs["name"]) == ["Song C"]
    assert page.all_time_plays == 4  # header counts do not change with the filter


def test_month_filter_with_no_plays_gives_empty_songs(db: Path):
    page = artist_page(db, "artist-a", None, None, month="2026-04")
    assert page.songs.empty


def test_month_outside_the_period_is_ignored(db: Path):
    page = artist_page(db, "artist-a", date(2026, 1, 1), date(2026, 3, 31), month="2026-06")
    assert sorted(page.songs["name"]) == ["Song A", "Song B"]


@pytest.mark.parametrize("bad", ["2026-6", "June", "2026-06-01", "2026-06; drop"])
def test_malformed_month_is_ignored(db: Path, bad: str):
    page = artist_page(db, "artist-a", None, None, month=bad)
    assert len(page.songs) == 3


def test_api_artist_serialises_first_played_monthly_and_month(db: Path, monkeypatch: pytest.MonkeyPatch):
    from fastapi.testclient import TestClient

    from rain_in_my_head import api, config

    monkeypatch.setattr(config, "HOSTED", False)  # the Mac's rules, whichever test module loaded first
    monkeypatch.setattr(config, "DB_PATH", db)
    client = TestClient(api.app)
    body = client.get("/api/artist", params={"artist": "artist-a"}).json()
    assert body["first_played"] == "2026-03-02"
    assert body["monthly"][-1] == {"month": "2026-06", "plays": 1}
    filtered = client.get("/api/artist", params={"artist": "artist-a", "month": "2026-06"}).json()
    assert [s["name"] for s in filtered["songs"]] == ["Song C"]
    assert filtered["monthly"] == body["monthly"]
