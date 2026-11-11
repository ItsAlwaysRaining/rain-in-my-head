"""The Mainstream vs. niche page: artists in one listener band, and the band's share (src/rain_in_my_head/overview.py)."""

import calendar
import sqlite3
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from rain_in_my_head import access, api, config
from rain_in_my_head.overview import listener_band_artists, listener_buckets


def _plays(rows: list[tuple[str, str, float | None]]) -> pd.DataFrame:
    """Rows of (artist_key, artist_name, artist_listeners)."""
    return pd.DataFrame(rows, columns=["artist_key", "artist_name", "artist_listeners"])


def test_spellings_that_share_a_key_are_one_row_with_summed_plays():
    df = _plays([
        ("hozier", "Hozier", 2_000_000),
        ("hozier", "HOZIER", 2_000_000),
        ("geese", "Geese", 50_000),
    ])

    artists, _ = listener_band_artists(df, "1M–5M")

    assert list(artists["artist_key"]) == ["hozier"]
    assert list(artists["plays"]) == [2]
    assert artists.iloc[0]["name"] == "Hozier"  # the first spelling seen


def test_band_edges_follow_the_chart_thresholds():
    # A band starts at its lower bound (right=False): 10,000 is 10k–100k, 100,000 is 100k–1M.
    df = _plays([
        ("a", "A", 9_999),
        ("b", "B", 10_000),
        ("c", "C", 100_000),
        ("d", "D", 5_000_000),
    ])

    assert list(listener_band_artists(df, "<10k")[0]["artist_key"]) == ["a"]
    assert list(listener_band_artists(df, "10k–100k")[0]["artist_key"]) == ["b"]
    assert list(listener_band_artists(df, "100k–1M")[0]["artist_key"]) == ["c"]
    assert list(listener_band_artists(df, "5M+")[0]["artist_key"]) == ["d"]


def test_artists_are_most_played_first_and_carry_listeners():
    df = _plays([
        ("geese", "Geese", 50_000),
        ("big-thief", "Big Thief", 50_000),
        ("big-thief", "Big Thief", 50_000),
    ])

    artists, _ = listener_band_artists(df, "10k–100k")

    assert list(artists["artist_key"]) == ["big-thief", "geese"]
    assert list(artists["plays"]) == [2, 1]
    assert list(artists["listeners"]) == [50_000, 50_000]
    assert set(artists.columns) == {"artist_key", "name", "listeners", "plays"}


def test_share_matches_the_chart_bar():
    df = _plays([
        ("a", "A", 5_000),
        ("b", "B", 50_000),
        ("b", "B", 50_000),
        ("c", "C", 2_000_000),
        ("d", "D", None),  # unknown listeners: left out of the chart and the share
    ])

    _, share = listener_band_artists(df, "10k–100k")
    bar = listener_buckets(df).set_index("bucket").loc["10k–100k", "share"]

    assert share == pytest.approx(bar)
    assert share == pytest.approx(2 / 4)


def test_band_with_no_artists_is_empty_with_zero_share():
    df = _plays([("a", "A", 5_000)])

    artists, share = listener_band_artists(df, "5M+")

    assert artists.empty
    assert share == 0.0


# ---- The /api/mainstream route ----------------------------------------------

SCHEMA = Path(__file__).resolve().parents[1] / "src" / "rain_in_my_head" / "schema.sql"


@pytest.fixture
def db(tmp_path: Path) -> Path:
    """Two bands: Geese (10k–100k, 2 plays in March) and Hozier (1M–5M, 1 play in June)."""
    path = tmp_path / "listening.db"
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA.read_text())
    conn.executemany(
        "INSERT INTO artists (artist_key, name, global_listeners, fetched_at) VALUES (?, ?, ?, 0)",
        [("geese", "Geese", 50_000), ("hozier", "Hozier", 2_000_000)],
    )
    plays = [("geese", "2026-03-02"), ("geese", "2026-03-15"), ("hozier", "2026-06-10")]
    for i, (key, day) in enumerate(plays):
        conn.execute(
            "INSERT INTO scrobbles (played_at, artist_name, track_name, album_name, artist_key, track_key) "
            "VALUES (?, ?, 'Song', 'Album', ?, ?)",
            (calendar.timegm((*map(int, day.split("-")), 12, 0, 0)) + i, key.title(), key, f"{key}\tSong{i}"),
        )
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def client(db: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(config, "DB_PATH", db)
    return TestClient(api.app)


def test_band_lists_its_artists_with_listeners_and_plays(client: TestClient):
    body = client.get("/api/mainstream", params={"bucket": "10k–100k"}).json()

    assert body["artists"] == [{"artist_key": "geese", "name": "Geese", "listeners": 50_000, "plays": 2}]
    assert body["share"] == pytest.approx(2 / 3)
    assert body["start"] == "2026-03-02" and body["end"] == "2026-06-10"  # all time without a range


def test_range_limits_the_band_to_its_plays(client: TestClient):
    body = client.get("/api/mainstream", params={"bucket": "1M–5M", "start": "2026-03-01", "end": "2026-03-31"}).json()

    assert body["artists"] == []
    assert body["share"] == 0.0


def test_unknown_band_is_refused(client: TestClient):
    assert client.get("/api/mainstream", params={"bucket": "huge"}).status_code == 422


def test_start_after_end_is_refused(client: TestClient):
    response = client.get("/api/mainstream", params={"bucket": "10k–100k", "start": "2026-06-01", "end": "2026-03-01"})
    assert response.status_code == 422


def test_guest_can_open_the_mainstream_route(db: Path, monkeypatch: pytest.MonkeyPatch):
    # Hosted mode: an anonymous visitor reaches the route because the guest tier includes the mainstream page.
    monkeypatch.setattr(config, "HOSTED", True)
    monkeypatch.setattr(config, "DB_PATH", db)
    response = TestClient(api.app).get("/api/mainstream", params={"bucket": "10k–100k"})
    assert response.status_code == 200


def test_visitor_without_the_mainstream_page_is_refused(db: Path, monkeypatch: pytest.MonkeyPatch):
    # Same hosted setup, but the route is unlocked only by a page no guest has.
    monkeypatch.setattr(config, "HOSTED", True)
    monkeypatch.setattr(config, "DB_PATH", db)
    monkeypatch.setitem(access.API_ACCESS, ("GET", "/api/mainstream"), frozenset({"no-such-page"}))
    response = TestClient(api.app).get("/api/mainstream", params={"bucket": "10k–100k"})
    assert response.status_code == 403
