"""Smoke test for the hosted site (openspec/changes/add-preview-deploy, decision 8).

It loads the same entry point Vercel loads (api/index.py), in hosted mode, on the real two-year copy that
`rain-in-my-head publish` makes. The login lookup is replaced, so no network or Neon is needed.

Run it after `build` and `publish`:
    uv run --with pytest --with httpx pytest tests
"""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DB = ROOT / "data" / "public.db"

# config.py reads these once, when it is first imported, so they are set before anything from the app is.
# They are assigned, not defaulted, so a real .env or shell value can never point the test at a live database.
os.environ["LISTENING_HOSTED"] = "1"
os.environ["LISTENING_DB"] = str(PUBLIC_DB)
os.environ["DATABASE_URL"] = ""
os.environ["SESSION_SECRET"] = "smoke-test-secret-not-used-anywhere-else"  # noqa: S105 a throwaway value for the test run
sys.path.insert(0, str(ROOT))

if not PUBLIC_DB.exists():
    pytest.exit(f"{PUBLIC_DB} is missing: run `rain-in-my-head build` and `rain-in-my-head publish` first", returncode=2)

from fastapi.testclient import TestClient  # noqa: E402

from api.index import app  # noqa: E402  (the file Vercel runs; if it can't import, every test here fails)
from rain_in_my_head import access, config, viewers  # noqa: E402

REFUSAL = "This DJ doesn't take requests."

SESSIONS = {
    "guest-session": viewers.Session("v-guest", "Test Guest", "guest", access.pages_for("guest", set())),
    "trusted-session": viewers.Session("v-trusted", "Test Trusted", "trusted", access.pages_for("trusted", set())),
}


@pytest.fixture(autouse=True)
def stub_session_lookup(monkeypatch):
    """Stands in for the Neon lookup: a known session id gives its person, anything else gives nobody."""
    monkeypatch.setattr(viewers, "lookup_session", lambda url, session_id, **kwargs: SESSIONS.get(session_id))


@pytest.fixture
def client():
    return TestClient(app)


def log_in_as(client, session_id):
    client.cookies.set("session", viewers.sign_cookie(session_id))


def test_runs_in_hosted_mode():
    assert config.HOSTED, "LISTENING_HOSTED was not read: the other tests would be testing the Mac's rules"
    assert config.DB_PATH == PUBLIC_DB, "the app is not reading the two-year copy"


def test_health_says_only_that_the_app_is_up(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_a_locked_route_needs_a_login(client):
    response = client.get("/api/genre")
    assert response.status_code == 403
    assert response.json()["error"] == "login_required"


def test_a_forged_cookie_is_not_a_login(client):
    client.cookies.set("session", "guest-session.not-the-real-signature")
    response = client.get("/api/genre")
    assert response.status_code == 403
    assert response.json()["error"] == "login_required"


def test_typed_sql_is_refused_even_for_a_trusted_visitor(client):
    log_in_as(client, "trusted-session")
    response = client.post("/api/sql", json={"sql": "select count(*) from scrobbles"})
    assert response.status_code == 403
    assert response.json() == {"error": "refused", "message": REFUSAL}


PREVIEW_BODY = {"kind": "slot", "min_plays": 3}


def test_a_guest_gets_the_playlist_form_data_and_preview(client):
    log_in_as(client, "guest-session")
    meta = client.get("/api/playlists/meta")
    assert meta.status_code == 200
    assert "weekdays" in meta.json()
    preview = client.post("/api/playlists/preview", json=PREVIEW_BODY)
    assert preview.status_code == 200
    assert "title" in preview.json()


def test_the_playlist_routes_need_a_login(client):
    for method, path in (("get", "/api/playlists/meta"), ("post", "/api/playlists/preview")):
        response = getattr(client, method)(path, **({"json": PREVIEW_BODY} if method == "post" else {}))
        assert response.status_code == 403
        assert response.json()["error"] == "login_required"


def test_creating_a_playlist_is_refused_even_for_a_trusted_visitor(client):
    log_in_as(client, "trusted-session")
    response = client.post("/api/playlists/create", json={**PREVIEW_BODY, "name": "x"})
    assert response.status_code == 403
    assert response.json() == {"error": "refused", "message": REFUSAL}


def test_the_spotify_check_and_unlisted_playlist_routes_are_refused(client):
    log_in_as(client, "trusted-session")
    for path in ("/api/playlists/spotify", "/api/playlists/other"):
        response = client.get(path)
        assert response.status_code == 403
        assert response.json() == {"error": "refused", "message": REFUSAL}


def test_a_visitor_without_the_playlists_page_is_refused_the_preview(client, monkeypatch):
    monkeypatch.setitem(SESSIONS, "no-playlists", viewers.Session("v-none", "Test None", "guest", frozenset({"about"})))
    log_in_as(client, "no-playlists")
    response = client.get("/api/playlists/meta")
    assert response.status_code == 403
    assert response.json()["error"] == "not_available"


def test_a_data_route_answers_for_a_logged_in_guest(client):
    log_in_as(client, "guest-session")
    response = client.get("/api/genre")
    assert response.status_code == 200
    assert "genres" in response.json()


def test_a_guest_cannot_open_the_analyst_routes(client):
    log_in_as(client, "guest-session")
    response = client.get("/api/sql/meta")
    assert response.status_code == 403
    assert response.json()["error"] == "not_available"
