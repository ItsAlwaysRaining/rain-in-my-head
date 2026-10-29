"""Invite codes, login sessions and the owner's commands for them (specs/011-viewer-access).

The first half is pure functions: making and hashing codes, and signing the login cookie. The second half talks
to the visitor database through neon.py. A code is never stored or logged; only its SHA-256 is (research R3).
"""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from rain_in_my_head import access, config, neon

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


# ---- Setting up the database (the owner's `viewer init`) ---------------------------------------------------

APP_ROLE = "rain_app"
SCHEMA_FILE = Path(__file__).with_name("viewer_schema.sql")
TABLES = ("viewers", "viewer_pages", "sessions", "login_attempts")


def _statements(sql: str) -> list[str]:
    """The statements in a .sql file: comments dropped, split on semicolons (the file has none inside strings)."""
    lines = [line for line in sql.splitlines() if not line.lstrip().startswith("--")]
    return [part.strip() for part in "\n".join(lines).split(";") if part.strip()]


def init_database(env: str) -> None:
    """Make the app role, the tables and the role's grants on one Neon branch. Safe to run again.

    The role's password is the one OpenTofu generated, read from the app URL in .env. OpenTofu makes it
    alphanumeric, and anything else is refused here because it's written into a statement as a literal.
    """
    owner_url = config.viewers_url(env, "owner")
    parts = urlsplit(config.viewers_url(env, "app"))
    password = parts.password or ""
    if parts.username != APP_ROLE or not re.fullmatch(r"[A-Za-z0-9]{16,}", password):
        raise SystemExit(f"VIEWERS_APP_URL_{env.upper()} isn't the {APP_ROLE} URL that OpenTofu makes.")
    exists = neon.query(owner_url, "select 1 as found from pg_roles where rolname = $1", [APP_ROLE])
    verb = "ALTER ROLE" if exists else "CREATE ROLE"
    login = "" if exists else " LOGIN"
    role_sql = f"{verb} {APP_ROLE}{login} PASSWORD '{password}'"
    neon.transaction(owner_url, [(role_sql, ())] + [(sql, ()) for sql in _statements(SCHEMA_FILE.read_text())])


# ---- The owner's commands: add and list --------------------------------------------------------------------

TIERS = ("guest", "trusted")
MAX_NAME = 60


class ViewerError(Exception):
    """Something the owner can fix: an unknown name, a duplicate, a bad option. The message is shown as it is."""


def _clean_name(name: str) -> str:
    name = " ".join(name.split())
    if not name or len(name) > MAX_NAME:
        raise ViewerError(f"A name needs 1 to {MAX_NAME} characters.")
    return name


def add_viewer(url: str, name: str, tier: str = "guest") -> str:
    """Add a person with a new code and return the code. This is the only time it exists in readable form."""
    name = _clean_name(name)
    if tier not in TIERS:
        raise ViewerError(f"The tier must be one of: {', '.join(TIERS)}.")
    code = new_code()
    try:
        neon.query(url, "insert into viewers (name, tier, code_hash) values ($1, $2, $3)", [name, tier, hash_code(code)])
    except neon.NeonError as e:
        if e.code == "23505":  # unique violation: the active-name index (the hash can't collide)
            raise ViewerError(f"{name} already has an active code. Revoke it first to give them a new one.") from None
        raise
    return code


def list_viewers(url: str) -> list[dict[str, str | None]]:
    """Everyone invited, newest first, with the extra pages granted to each."""
    return neon.query(
        url,
        "select v.name, v.tier, v.status, v.created_at, v.last_login_at, "
        "coalesce(string_agg(p.page, ', ' order by p.page), '') as pages "
        "from viewers v left join viewer_pages p on p.viewer_id = v.id group by v.id order by v.id desc",
    )


# ---- Logging in and checking a session (run by the hosted API) ---------------------------------------------

SESSION_CACHE_SECONDS = 3  # a revoke shows up on every server within this long (spec SC-004)


class BadCode(Exception):
    """A wrong, revoked or unknown code. The same error for all three, so nothing hints at which."""


@dataclass(frozen=True)
class Session:
    viewer_id: str
    name: str
    tier: str
    pages: frozenset[str]


_cache: dict[str, tuple[float, Session | None]] = {}


def lookup_session(url: str, session_id: str, *, fresh: bool = False) -> Session | None:
    """The person behind a session id, or None if it's unknown, expired or the person was revoked.

    One query joins the session, the person and their granted pages. The answer is remembered for a few
    seconds, so a page that makes six API calls costs one query (research R6).
    """
    key = hash_session_id(session_id)
    now = time.monotonic()
    hit = _cache.get(key)
    if hit and not fresh and now - hit[0] < SESSION_CACHE_SECONDS:
        return hit[1]
    rows = neon.query(
        url,
        "select v.id, v.name, v.tier, coalesce(string_agg(p.page, ','), '') as pages "
        "from sessions s join viewers v on v.id = s.viewer_id "
        "left join viewer_pages p on p.viewer_id = v.id "
        "where s.id_hash = $1 and s.expires_at > now() and v.status = 'active' group by v.id",
        [key],
    )
    session = None
    if rows:
        r = rows[0]
        granted = {page for page in (r["pages"] or "").split(",") if page}
        session = Session(r["id"], r["name"], r["tier"], access.pages_for(r["tier"], granted))
    if len(_cache) > 500:
        _cache.clear()
    _cache[key] = (now, session)
    return session


def login(url: str, code: str) -> tuple[str, Session]:
    """Check a code. If it's active, start a session and return its id and the person."""
    wanted = hash_code(code)
    rows = neon.query(url, "select id, code_hash from viewers where code_hash = $1 and status = 'active'", [wanted])
    if not rows or not hmac.compare_digest(rows[0]["code_hash"], wanted):
        raise BadCode()
    session_id = new_session_id()
    neon.transaction(url, [
        (f"insert into sessions (id_hash, viewer_id, expires_at) values ($1, $2, now() + interval '{int(config.SESSION_DAYS)} days')",
         [hash_session_id(session_id), rows[0]["id"]]),
        ("update viewers set last_login_at = now() where id = $1", [rows[0]["id"]]),
        ("delete from sessions where expires_at < now()", []),
    ])
    session = lookup_session(url, session_id, fresh=True)
    if session is None:  # revoked between the two steps
        raise BadCode()
    return session_id, session


def end_session(url: str, session_id: str) -> None:
    neon.query(url, "delete from sessions where id_hash = $1", [hash_session_id(session_id)])
    _cache.pop(hash_session_id(session_id), None)


# ---- The owner's commands: revoke and grant ----------------------------------------------------------------


def _active_viewer(url: str, name: str) -> dict[str, str | None]:
    """The person with this name and an active code, or a plain error saying why there isn't one."""
    name = _clean_name(name)
    rows = neon.query(url, "select id, name, tier from viewers where lower(name) = lower($1) and status = 'active'", [name])
    if rows:
        return rows[0]
    if neon.query(url, "select 1 as found from viewers where lower(name) = lower($1)", [name]):
        raise ViewerError(f"{name}'s code is revoked. Add them again with `viewer add` to give them a new one.")
    raise ViewerError(f"No one called {name} has been invited. See `viewer list`.")


def revoke_viewer(url: str, name: str) -> tuple[str, int]:
    """Make a person's code unusable and end their sessions, in one step. Returns their name and how many sessions ended."""
    person = _active_viewer(url, name)
    _, ended = neon.transaction(url, [
        ("update viewers set status = 'revoked', revoked_at = now() where id = $1", [person["id"]]),
        ("delete from sessions where viewer_id = $1 returning id_hash", [person["id"]]),
    ])
    return person["name"], len(ended)


def grant(url: str, name: str, *, add_page: str | None = None, remove_page: str | None = None, tier: str | None = None) -> tuple[str, list[str]]:
    """Add or take back a page, or change the tier, for one person. Returns their name and what changed."""
    if not (add_page or remove_page or tier):
        raise ViewerError("Say what to change: --page, --remove-page or --tier.")
    for page in (add_page, remove_page):
        if page and page not in access.PAGES:
            raise ViewerError(f"Unknown page {page!r}. The pages are: {', '.join(access.PAGES)}.")
    if tier and tier not in TIERS:
        raise ViewerError(f"The tier must be one of: {', '.join(TIERS)}.")
    person = _active_viewer(url, name)
    statements, changes = [], []
    if add_page:
        statements.append(("insert into viewer_pages (viewer_id, page) values ($1, $2) on conflict do nothing", [person["id"], add_page]))
        changes.append(f"+{add_page}")
    if remove_page:
        statements.append(("delete from viewer_pages where viewer_id = $1 and page = $2", [person["id"], remove_page]))
        changes.append(f"-{remove_page}")
    if tier:
        statements.append(("update viewers set tier = $2 where id = $1", [person["id"], tier]))
        changes.append(f"tier {tier}")
    neon.transaction(url, statements)
    return person["name"], changes
