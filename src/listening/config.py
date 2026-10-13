"""Paths and credentials, read from the environment (and .env when present)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

RAW_DIR = Path(os.environ.get("LISTENING_RAW_DIR", ROOT / "data" / "raw" / "lastfm"))
DB_PATH = Path(os.environ.get("LISTENING_DB", ROOT / "data" / "listening.db"))


def lastfm_credentials() -> tuple[str, str]:
    api_key = os.environ.get("LASTFM_API_KEY", "").strip()
    user = os.environ.get("LASTFM_USER", "").strip()
    if not api_key or not user:
        raise SystemExit("Set LASTFM_API_KEY and LASTFM_USER in .env (see .env.example).")
    return api_key, user


SPOTIFY_TOKEN_PATH = ROOT / "data" / ".spotify_token.json"


def spotify_client_id() -> str:
    client_id = os.environ.get("SPOTIFY_CLIENT_ID", "").strip()
    if not client_id or client_id == "your_spotify_client_id":
        raise SystemExit("Set SPOTIFY_CLIENT_ID in .env (see README: Spotify playlists).")
    return client_id
