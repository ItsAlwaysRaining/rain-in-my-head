"""The SQL playlist type: a playlist from a read-only query (openspec/specs/sql-playlist)."""

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from rain_in_my_head import api, config
from rain_in_my_head import sql_examples as sq

SCHEMA = Path(__file__).resolve().parents[1] / "src" / "rain_in_my_head" / "schema.sql"
PLAYS = [("Hozier", "Too Sweet"), ("Hozier", "Too Sweet"), ("bbno$", "Edamame"), ("Geese", "Cobra")]


@pytest.fixture
def db(tmp_path: Path) -> Path:
    path = tmp_path / "listening.db"
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA.read_text())
    for i, (artist, track) in enumerate(PLAYS):
        key = artist.lower()
        conn.execute(
            "INSERT INTO scrobbles (played_at, artist_name, track_name, album_name, artist_key, track_key) VALUES (?, ?, ?, 'A', ?, ?)",
            (1_770_000_000 + i, artist, track, key, f"{key}\t{track.lower()}"),
        )
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def client(db: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(config, "DB_PATH", db)
    return TestClient(api.app)


def preview(client: TestClient, sql: str):
    return client.post("/api/playlists/preview", json={"kind": "sql", "sql": sql})


def test_rows_come_back_in_query_order_with_extra_columns(client):
    body = preview(client, "SELECT artist_name AS Artist, track_name AS track, COUNT(*) AS plays FROM scrobbles "
                           "GROUP BY track_key ORDER BY plays DESC, artist").json()
    assert body["missing"] == [] and body["warning"] is None
    assert [c["key"] for c in body["columns"]] == ["artist", "track", "plays"]
    assert [(r["artist"], r["plays"]) for r in body["rows"]] == [("Hozier", 2), ("Geese", 1), ("bbno$", 1)]


@pytest.mark.parametrize(("sql", "missing"), [
    ("SELECT artist_name AS artist, 1 AS plays FROM scrobbles", ["track"]),
    ("SELECT 1 AS day, 2 AS plays", ["artist", "track"]),
])
def test_missing_columns_are_named(client, sql, missing):
    body = preview(client, sql).json()
    assert body["returned"][-1] == "plays"
    assert body["missing"] == missing and body["warning"] and "rows" not in body


def test_a_write_is_refused_and_changes_nothing(client, db):
    response = preview(client, "DELETE FROM scrobbles")
    assert response.status_code == 422
    assert sqlite3.connect(db).execute("SELECT COUNT(*) FROM scrobbles").fetchone()[0] == len(PLAYS)


def test_invalid_sql_returns_the_error(client):
    response = preview(client, "SELEC nonsense")
    assert response.status_code == 422 and "syntax" in response.json()["detail"]


def test_typed_sql_preview_is_refused_when_hosted(client, monkeypatch):
    monkeypatch.setattr(config, "HOSTED", True)
    response = preview(client, "SELECT 'a' AS artist, 'b' AS track")
    assert response.status_code == 403
    assert response.json()["message"] == "This DJ doesn't take requests."


LOVED = {"Loved-ish": "SELECT artist_name AS artist, track_name AS track FROM scrobbles ORDER BY played_at"}


def test_a_pre_defined_query_previews_by_name(client, monkeypatch):
    monkeypatch.setattr(sq, "EXAMPLES", LOVED)
    body = client.post("/api/playlists/preview", json={"kind": "sql", "example": "Loved-ish"}).json()
    assert [r["track"] for r in body["rows"]] == [t for _, t in PLAYS]


def test_hosted_runs_a_pre_defined_query_but_not_an_unknown_name(client, monkeypatch):
    monkeypatch.setattr(sq, "EXAMPLES", LOVED)
    monkeypatch.setattr(config, "HOSTED", True)
    monkeypatch.setattr(api, "_heavy", lambda *a, **k: None)  # the per-person count lives in Neon
    assert client.post("/api/playlists/preview", json={"kind": "sql", "example": "Loved-ish"}).status_code == 200
    assert client.post("/api/playlists/preview", json={"kind": "sql", "example": "Nope"}).status_code == 403


def test_create_stays_refused_when_hosted(client, monkeypatch):
    monkeypatch.setattr(sq, "EXAMPLES", LOVED)
    monkeypatch.setattr(config, "HOSTED", True)
    response = client.post("/api/playlists/create", json={"kind": "sql", "example": "Loved-ish", "name": "x"})
    assert response.status_code == 403 and response.json()["message"] == "This DJ doesn't take requests."
