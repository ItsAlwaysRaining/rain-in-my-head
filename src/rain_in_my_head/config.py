"""Paths and credentials, read from the environment (and .env when present)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

RAW_DIR = Path(os.environ.get("LISTENING_RAW_DIR", ROOT / "data" / "raw" / "lastfm"))
CACHE_DIR = Path(os.environ.get("LISTENING_CACHE_DIR", ROOT / "data" / "cache"))  # committed Last.fm lookups
DB_PATH = Path(os.environ.get("LISTENING_DB", ROOT / "data" / "listening.db"))
# The hosted site (LISTENING_HOSTED=1): the database is opened immutable and anything that writes, makes
# playlists, runs typed SQL or uses AI is refused with REFUSAL (specs/009-public-dataset).
HOSTED = os.environ.get("LISTENING_HOSTED") == "1"
REFUSAL = "This DJ doesn't take requests."
# Visitor access on the hosted site (specs/011-viewer-access). Vercel sets DATABASE_URL (the site's Neon role,
# which can only read people and write sessions) and SESSION_SECRET (signs the login cookie).
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
SESSION_SECRET = os.environ.get("SESSION_SECRET", "").strip()
SESSION_DAYS = 30


def viewers_url(env: str, role: str) -> str:
    """The Neon connection string for the `viewer` commands: role is "owner" or "app", env is "dev" or "prod"."""
    name = f"VIEWERS_{role.upper()}_URL_{env.upper()}"
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Set {name} in .env (see .env.example).")
    return value

# Shown by both dashboards when DB_PATH doesn't exist yet.
NO_DATABASE = "No database yet. Run `uv run rain-in-my-head fetch` then `uv run rain-in-my-head build`."


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
