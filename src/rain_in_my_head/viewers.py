"""Invite codes, login sessions and the owner's commands for them (specs/011-viewer-access).

This part is the pure functions: making and hashing codes, and signing the login cookie. It touches no
database. A code is never stored or logged; only its SHA-256 is (research R3).
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

from rain_in_my_head import config

# Letters and digits without the look-alikes 0 O o 1 I l: 56 characters, so 16 of them are about 93 bits.
CODE_ALPHABET = "".join(c for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" if c not in "0Oo1Il")
CODE_LENGTH = 16
LOCAL_HOSTS = ("localhost", "127.0.0.1")


def new_code() -> str:
    """A random code, shown as xxxx-xxxx-xxxx-xxxx."""
    raw = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
    return "-".join(raw[i : i + 4] for i in range(0, CODE_LENGTH, 4))


def clean_code(code: str) -> str:
    """What was typed, without spaces and dashes. The case matters."""
    return "".join(ch for ch in code if ch not in " -\t\r\n")


def hash_code(code: str) -> str:
    """The only form of a code that is stored: hex SHA-256 of the cleaned code."""
    return hashlib.sha256(clean_code(code).encode()).hexdigest()


def new_session_id() -> str:
    return secrets.token_urlsafe(32)


def hash_session_id(session_id: str) -> str:
    """The session row's key. A copy of the database can't be turned into a working cookie."""
    return hashlib.sha256(session_id.encode()).hexdigest()


def _signature(session_id: str) -> str:
    if not config.SESSION_SECRET:
        raise RuntimeError("SESSION_SECRET is not set.")
    return hmac.new(config.SESSION_SECRET.encode(), session_id.encode(), hashlib.sha256).hexdigest()


def sign_cookie(session_id: str) -> str:
    return f"{session_id}.{_signature(session_id)}"


def read_cookie(value: str | None) -> str | None:
    """The session id inside a cookie, or None if there's no cookie or it was edited or forged."""
    if not value or "." not in value or not config.SESSION_SECRET:
        return None
    session_id, _, signature = value.rpartition(".")
    if not session_id or not hmac.compare_digest(signature, _signature(session_id)):
        return None
    return session_id


def cookie_secure(request) -> bool:
    """Secure on HTTPS (including behind Vercel's proxy) and on localhost, where Chrome allows it for testing."""
    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    return proto == "https" or request.url.hostname in LOCAL_HOSTS
