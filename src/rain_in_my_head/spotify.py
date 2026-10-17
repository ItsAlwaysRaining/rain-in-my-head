"""Spotify, used only to turn track lists into playlists.

Login uses Authorization Code + PKCE (no client secret). The token is cached in
data/.spotify_token.json, which is gitignored. Endpoints follow the February 2026 Web API
changes: POST /me/playlists, POST /playlists/{id}/items, search limit <= 10.
"""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
import time
import webbrowser
from difflib import SequenceMatcher
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

from .build import normalize, normalize_track

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_URL = "https://api.spotify.com/v1"
REDIRECT_PORT = 8888
REDIRECT_URI = f"http://127.0.0.1:{REDIRECT_PORT}/callback"
SCOPES = "playlist-modify-private playlist-modify-public"
MIN_MATCH = 0.85


class SpotifyAuthError(Exception):
    pass


def login(client_id: str, token_path: Path) -> None:
    """Open the browser for consent and store the resulting tokens."""
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)
    url = AUTH_URL + "?" + urlencode({
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "code_challenge_method": "S256",
        "code_challenge": challenge,
        "scope": SCOPES,
        "state": state,
    })

    result: dict[str, str] = {}

    class Callback(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            params = {k: v[0] for k, v in parse_qs(urlparse(self.path).query).items()}
            if urlparse(self.path).path != "/callback":
                self.send_response(404)
                self.end_headers()
                return
            result.update(params)
            ok = "code" in params and params.get("state") == state
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            msg = "Spotify connected. You can close this tab." if ok else "Spotify login failed. Check the terminal."
            self.wfile.write(f"<p style='font-family:sans-serif'>{msg}</p>".encode())

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", REDIRECT_PORT), Callback)
    print(f"Opening Spotify login in your browser. If it doesn't open, visit:\n{url}\n")
    webbrowser.open(url)
    while "code" not in result and "error" not in result:
        server.handle_request()
    server.server_close()

    if "error" in result or result.get("state") != state:
        raise SpotifyAuthError(f"Login failed: {result.get('error', 'state mismatch')}")
    resp = httpx.post(TOKEN_URL, data={
        "grant_type": "authorization_code",
        "code": result["code"],
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
        "code_verifier": verifier,
    })
    resp.raise_for_status()
    _save_token(token_path, resp.json())
    print(f"Logged in. Token saved to {token_path}")


def _save_token(path: Path, data: dict, previous: dict | None = None) -> dict:
    token = {
        "access_token": data["access_token"],
        # PKCE refresh responses usually rotate the refresh token; keep the old one if not.
        "refresh_token": data.get("refresh_token") or (previous or {}).get("refresh_token"),
        "expires_at": int(time.time()) + int(data.get("expires_in", 3600)) - 60,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(token))
    path.chmod(0o600)
    return token


class SpotifyClient:
    def __init__(self, client_id: str, token_path: Path, requests_per_second: float = 5.0):
        if not token_path.exists():
            raise SpotifyAuthError("Not logged in to Spotify. Run `uv run listening spotify-login` first.")
        self.client_id = client_id
        self.token_path = token_path
        self._token = json.loads(token_path.read_text())
        self._min_interval = 1.0 / requests_per_second
        self._last_request = 0.0
        self._http = httpx.Client(base_url=API_URL, timeout=30)

    def _access_token(self) -> str:
        if time.time() >= self._token["expires_at"]:
            resp = httpx.post(TOKEN_URL, data={
                "grant_type": "refresh_token",
                "refresh_token": self._token["refresh_token"],
                "client_id": self.client_id,
            })
            if resp.status_code == 400:
                raise SpotifyAuthError("Spotify login expired. Run `uv run listening spotify-login` again.")
            resp.raise_for_status()
            self._token = _save_token(self.token_path, resp.json(), self._token)
        return self._token["access_token"]

    def request(self, method: str, path: str, **kwargs) -> dict:
        for attempt in range(6):
            wait = self._min_interval - (time.monotonic() - self._last_request)
            if wait > 0:
                time.sleep(wait)
            self._last_request = time.monotonic()
            resp = self._http.request(
                method, path, headers={"Authorization": f"Bearer {self._access_token()}"}, **kwargs
            )
            if resp.status_code == 429 or resp.status_code >= 500:
                time.sleep(float(resp.headers.get("Retry-After", min(2**attempt, 30))))
                continue
            if resp.status_code == 401:
                self._token["expires_at"] = 0  # force a refresh, then retry
                continue
            if resp.status_code == 403:
                raise SpotifyAuthError(
                    "Spotify returned 403. Dev-mode apps need the app owner on Premium, and your "
                    "account must be the app owner or on the app's user list."
                )
            resp.raise_for_status()
            return resp.json() if resp.content else {}
        raise RuntimeError(f"Spotify {method} {path} kept failing")

    def search_track(self, artist: str, track: str) -> dict | None:
        """Best catalog match for an artist/track pair, or None if nothing is close enough."""
        queries = [f'track:"{track}" artist:"{artist}"', f"{artist} {normalize_track(track)}"]
        best = None
        for q in queries:
            items = self.request("GET", "/search", params={"q": q, "type": "track", "limit": 10})
            for item in items.get("tracks", {}).get("items", []):
                score = match_score(artist, track, item)
                if best is None or score > best["score"]:
                    best = {
                        "uri": item["uri"],
                        "name": item["name"],
                        "artist": ", ".join(a["name"] for a in item["artists"]),
                        "score": score,
                    }
            if best and best["score"] >= MIN_MATCH:
                return best
        return best if best and best["score"] >= MIN_MATCH else None

    def create_playlist(self, name: str, description: str, uris: list[str], public: bool = False) -> str:
        playlist = self.request(
            "POST", "/me/playlists", json={"name": name, "description": description, "public": public}
        )
        for i in range(0, len(uris), 100):
            self.request("POST", f"/playlists/{playlist['id']}/items", json={"uris": uris[i : i + 100]})
        return playlist["external_urls"]["spotify"]


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def match_score(artist: str, track: str, item: dict) -> float:
    """Geometric-ish blend of title and artist similarity; both must be good."""
    title = _similar(normalize_track(track), normalize_track(item["name"]))
    artist_n = normalize(artist)
    artist_score = max((_similar(artist_n, normalize(a["name"])) for a in item["artists"]), default=0)
    # Last.fm sometimes credits "A & B" or "A feat. B" as the artist; accept if the primary matches.
    if artist_score < MIN_MATCH and any(
        len(n := normalize(a["name"])) >= 3 and n in artist_n for a in item["artists"]
    ):
        artist_score = MIN_MATCH
    return min(title, artist_score)
