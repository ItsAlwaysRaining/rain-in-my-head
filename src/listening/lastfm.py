"""Minimal Last.fm API client: throttling, retries and the few methods we use."""

from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Any

import httpx

API_URL = "https://ws.audioscrobbler.com/2.0/"
PAGE_SIZE = 200  # max allowed by user.getRecentTracks

# 8 operation failed, 11 service offline, 16 temporary error, 29 rate limit exceeded
RETRYABLE_ERRORS = {8, 11, 16, 29}
NOT_FOUND_ERRORS = {6}


class LastfmError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(f"Last.fm error {code}: {message}")
        self.code = code


class LastfmClient:
    def __init__(self, api_key: str, user: str, requests_per_second: float = 4.0, max_retries: int = 6):
        self.api_key = api_key
        self.user = user
        self._min_interval = 1.0 / requests_per_second
        self._max_retries = max_retries
        self._last_request = 0.0
        self._http = httpx.Client(timeout=30, headers={"User-Agent": "listening-analytics/0.1"})

    def _throttle(self) -> None:
        wait = self._min_interval - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        self._last_request = time.monotonic()

    def call(self, method: str, **params: Any) -> dict:
        query = {"method": method, "api_key": self.api_key, "format": "json", **params}
        for attempt in range(self._max_retries):
            backoff = min(2**attempt, 60)
            self._throttle()
            try:
                resp = self._http.get(API_URL, params=query)
            except httpx.TransportError:
                time.sleep(backoff)
                continue
            if resp.status_code == 429 or resp.status_code >= 500:
                time.sleep(float(resp.headers.get("Retry-After", backoff)))
                continue
            try:
                data = resp.json()
            except ValueError:
                time.sleep(backoff)
                continue
            # Last.fm reports errors in the JSON body, sometimes with a 4xx status.
            if "error" in data:
                if data["error"] in RETRYABLE_ERRORS:
                    time.sleep(backoff)
                    continue
                raise LastfmError(data["error"], data.get("message", ""))
            resp.raise_for_status()
            return data
        raise LastfmError(-1, f"{method} still failing after {self._max_retries} attempts")

    def registered_at(self) -> int:
        """Unix time the account was created."""
        user = self.call("user.getInfo", user=self.user)["user"]
        return int(user["registered"]["unixtime"])

    def recent_tracks(self, from_uts: int, to_uts: int) -> Iterator[dict]:
        """Every scrobble with from_uts <= uts <= to_uts, newest first, as slim dicts."""
        page = 1
        while True:
            data = self.call(
                "user.getRecentTracks",
                user=self.user,
                limit=PAGE_SIZE,
                page=page,
                extended=1,
                **{"from": from_uts, "to": to_uts},
            )
            recent = data["recenttracks"]
            tracks = recent.get("track", [])
            if isinstance(tracks, dict):  # a single result comes back as an object
                tracks = [tracks]
            for t in tracks:
                if t.get("@attr", {}).get("nowplaying") == "true" or "date" not in t:
                    continue
                yield _slim_scrobble(t)
            if page >= int(recent["@attr"]["totalPages"]):
                return
            page += 1

    def track_info(self, artist: str, track: str) -> dict | None:
        try:
            return self.call("track.getInfo", artist=artist, track=track, autocorrect=1)["track"]
        except LastfmError as e:
            if e.code in NOT_FOUND_ERRORS:
                return None
            raise

    def artist_info(self, artist: str) -> dict | None:
        try:
            return self.call("artist.getInfo", artist=artist, autocorrect=1)["artist"]
        except LastfmError as e:
            if e.code in NOT_FOUND_ERRORS:
                return None
            raise

    def artist_top_tags(self, artist: str) -> list[dict]:
        try:
            tags = self.call("artist.getTopTags", artist=artist, autocorrect=1)["toptags"].get("tag", [])
        except LastfmError as e:
            if e.code in NOT_FOUND_ERRORS:
                return []
            raise
        return [tags] if isinstance(tags, dict) else tags


def _slim_scrobble(t: dict) -> dict:
    artist = t.get("artist", {})
    album = t.get("album", {})
    images = [i.get("#text") for i in t.get("image", []) if i.get("#text")]
    return {
        "uts": int(t["date"]["uts"]),
        # extended=1 puts the artist under "name"; plain mode uses "#text".
        "artist": artist.get("name") or artist.get("#text") or "",
        "artist_mbid": artist.get("mbid") or None,
        "track": t.get("name", ""),
        "track_mbid": t.get("mbid") or None,
        "album": album.get("#text") or None,
        "album_mbid": album.get("mbid") or None,
        "loved": t.get("loved") == "1",
        "image": images[-1] if images else None,
    }
