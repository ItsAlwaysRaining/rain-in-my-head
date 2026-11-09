"""Usage records, the per-person limit and the owner's report (specs/012-usage-tracking).

Every record is a row in `usage_events` in the visitor database (Neon). The limit on heavy requests is counted
from the same rows. Nothing here takes, stores or logs an IP address, a code or a cookie, except the hash of a
client address for visitors with no login (`anonymous_usage`, see heavy_request_anonymous).
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from rain_in_my_head import config, neon

# One place for every limit (FR-014). A heavy request is a pre-defined query or a genre's song list.
HEAVY_PER_MINUTE = 30     # a rolling minute, per person
HEAVY_PER_DAY = 1000      # since 00:00 UTC, per person
EVENTS_PER_MINUTE = 120   # browser reports (page opens and leaves), per person; extras are dropped quietly
MAX_SECONDS = 1800        # one page visit counts for at most 30 minutes
DEDUPE_SECONDS = 5        # a reload of the same page inside this long isn't a second view
RETENTION_MONTHS = 12     # older records are deleted by `viewer prune`

# The free-plan limits shown beside this month's figures (FR-018). Checked on 2026-11-01 against the providers' own
# pages: https://neon.com/docs/introduction/plans (Free: 1 GB per project; some older Neon pages still say 0.5 GB)
# and https://vercel.com/docs/plans/hobby (Hobby: 4 Active CPU hours and 1,000,000 function invocations a month;
# a project without Fluid compute is held to the older 100,000). Vercel's CPU hours can't be read from here, so
# only the invocation count is shown, as a ceiling: Vercel counts every API call, which is more than we record.
FREE_LIMITS: dict[str, int | None] = {
    "database_bytes": 1024**3,
    "function_invocations": 1_000_000,
}


# ---- Writing records ---------------------------------------------------------------------------------------

def record_event(
    url: str,
    viewer_id: str | int,
    kind: str,
    *,
    page: str | None = None,
    feature: str | None = None,
    detail: str | None = None,
    visit: str | None = None,
    seconds: int | None = None,
) -> None:
    """Store one row. The time comes from the database, never from the browser.

    Raises neon.NeonUnavailable unchanged: the caller decides what a failure means (a dropped report for the
    browser's reports, a refusal for a heavy request). Takes no request, header, address or cookie.
    """
    if seconds is not None:
        seconds = max(0, min(int(seconds), MAX_SECONDS))
    neon.query(
        url,
        "insert into usage_events (viewer_id, kind, page, feature, detail, visit, seconds) "
        "values ($1::bigint, $2, $3, $4, $5, $6, $7::int)",
        [viewer_id, kind, page, feature, detail, visit, seconds],
    )


# ---- The browser's reports: a page opened, a page left (research R3, R4) -----------------------------------

VISIT_ID = re.compile(r"[A-Za-z0-9]{8,32}")

# Both statements store nothing when the person has already sent EVENTS_PER_MINUTE reports in the last minute
# (FR-030). They count only columns the site's database role may read: viewer_id, kind, page, at.
_UNDER_CAP = (
    "(select count(*) from usage_events where viewer_id = $1::bigint and kind in ('view', 'time') "
    "and at > now() - interval '1 minute') < $2::int"
)


def report_open(url: str, viewer_id: str | int, pages: set[str] | frozenset[str], page: str, visit: str) -> None:
    """A page was opened: store a `view`, unless the page isn't one the person can open, the person is over
    the cap, or they opened the same page a moment ago (a reload). Raises neon.NeonUnavailable."""
    if page not in pages or not VISIT_ID.fullmatch(visit):
        return
    neon.query(
        url,
        "insert into usage_events (viewer_id, kind, page, visit) "  # noqa: S608 only module constants are interpolated; values are bound
        f"select $1::bigint, 'view', $3::text, $4::text where {_UNDER_CAP} "
        "and not exists (select 1 from usage_events where viewer_id = $1::bigint and kind = 'view' "
        "and page = $3::text and at > now() - ($5::int * interval '1 second'))",
        [viewer_id, EVENTS_PER_MINUTE, page, visit, DEDUPE_SECONDS],
    )


def report_leave(
    url: str, viewer_id: str | int, pages: set[str] | frozenset[str], page: str, visit: str, seconds: int
) -> None:
    """A page was left: store a `time` row with the seconds spent (0 to MAX_SECONDS). Stored even if the open
    report was lost. Same rules about the page and the cap. Raises neon.NeonUnavailable."""
    if page not in pages or not VISIT_ID.fullmatch(visit):
        return
    neon.query(
        url,
        "insert into usage_events (viewer_id, kind, page, visit, seconds) "
        f"select $1::bigint, 'time', $3::text, $4::text, $5::int where {_UNDER_CAP}",
        [viewer_id, EVENTS_PER_MINUTE, page, visit, max(0, min(int(seconds), MAX_SECONDS))],
    )


# ---- The owner's report (Mac only; research R6, R7) ---------------------------------------------------------
# One function builds it, and both the Visitors page (GET /api/visitors) and `viewer usage` call it, so the two
# always show the same numbers. Time is in UTC.

RANGES = {"7d": "7 days", "30d": "30 days", "12m": "12 months"}
HEAVY_PAGES = ("genre", "analyst")  # the pages whose time is counted as "time on heavy pages"
VERCEL_NOTE = "Vercel's processing time is shown only on Vercel's own dashboard."
REQUESTS_NOTE = "Recorded requests are page views, feature uses and limit hits. Vercel counts every API call against its 1,000,000, so its own number is higher."


class UsageError(Exception):
    """A bad choice from the owner (an unknown range, environment or name). Safe to show."""


ISO_LOGIN = "to_char(v.last_login_at at time zone 'utc', 'YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"')"
ISO_AT = "to_char(at at time zone 'utc', 'YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"')"


def _n(value: str | None) -> int:
    return int(value or 0)


def report(url: str, range_key: str) -> list[dict]:
    """One entry per invited person, with their activity in the range. People with no activity are included."""
    if range_key not in RANGES:
        raise UsageError(f"Unknown range {range_key!r}. Choose 7d, 30d or 12m.")
    span = RANGES[range_key]
    recent = "e.at > now() - $1::interval"
    people, pages, features = neon.transaction(url, [
        (
            "select v.id, v.name, v.tier, v.status, " + ISO_LOGIN + " as last_login_at, "
            "count(e.id) filter (where e.kind = 'view') as visits, "
            "coalesce(sum(e.seconds) filter (where e.kind = 'time'), 0) as seconds, "
            "count(e.id) filter (where e.kind = 'limit') as limit_hits "
            f"from viewers v left join usage_events e on e.viewer_id = v.id and {recent} "
            "group by v.id order by lower(v.name), v.id",
            [span],
        ),
        (
            "select e.viewer_id, e.page, count(*) filter (where e.kind = 'view') as views, "  # noqa: S608 only module constants are interpolated; values are bound
            "coalesce(sum(e.seconds) filter (where e.kind = 'time'), 0) as seconds "
            f"from usage_events e where {recent} and e.page is not null and e.kind in ('view', 'time') "
            "group by e.viewer_id, e.page order by views desc, seconds desc, e.page",
            [span],
        ),
        (
            "select e.viewer_id, e.feature, e.detail, count(*) as uses "  # noqa: S608 only module constants are interpolated; values are bound
            f"from usage_events e where {recent} and e.kind = 'feature' "
            "group by e.viewer_id, e.feature, e.detail order by uses desc, e.feature, e.detail",
            [span],
        ),
    ])
    out = []
    for p in people:
        out.append({
            "name": p["name"], "tier": p["tier"], "status": p["status"], "last_login_at": p["last_login_at"],
            "visits": _n(p["visits"]), "seconds": _n(p["seconds"]),
            "pages": [{"page": r["page"], "views": _n(r["views"]), "seconds": _n(r["seconds"])} for r in pages if r["viewer_id"] == p["id"]],
            "features": [{"feature": r["feature"], "detail": r["detail"], "uses": _n(r["uses"])} for r in features if r["viewer_id"] == p["id"]],
            "limit_hits": _n(p["limit_hits"]),
        })
    return out


def person_detail(url: str, name: str, limit: int = 200) -> dict:
    """One person's newest records, newest first. No id, address or code in it."""
    found = neon.query(url, "select id, name from viewers where lower(name) = lower($1) order by created_at desc, id desc limit 1", [name])
    if not found:
        raise UsageError(f"Nobody called {name!r} has been invited.")
    rows = neon.query(
        url,
        "select kind, page, feature, detail, seconds, " + ISO_AT + " as at from usage_events where viewer_id = $1::bigint "  # noqa: S608 only module constants are interpolated; values are bound
        "order by at desc, id desc limit $2::int",
        [found[0]["id"], limit],
    )
    return {"name": found[0]["name"], "events": [
        {**r, "seconds": None if r["seconds"] is None else int(r["seconds"])} for r in rows
    ]}


def free_plan(url: str) -> dict:
    """This UTC month's figures the site can measure for itself, and the database size. It says nothing about
    Vercel's processing time (only Vercel knows it) and promises none per person (FR-018)."""
    month = "date_trunc('month', now() at time zone 'utc') at time zone 'utc'"
    counts, size = neon.transaction(url, [
        (
            "select to_char(now() at time zone 'utc', 'YYYY-MM') as month, "  # noqa: S608 only module constants are interpolated; values are bound
            "count(*) filter (where kind in ('view', 'feature', 'limit')) as requests, "
            "coalesce(sum(seconds) filter (where kind = 'time' and page = any($1::text[])), 0) as heavy_seconds "
            f"from usage_events where at >= {month}",
            ["{" + ",".join(HEAVY_PAGES) + "}"],
        ),
        ("select pg_database_size(current_database()) as bytes", []),
    ])
    return {
        "month": counts[0]["month"],
        "requests": _n(counts[0]["requests"]),
        "heavy_page_seconds": _n(counts[0]["heavy_seconds"]),
        "database_bytes": _n(size[0]["bytes"]),
        "requests_limit": FREE_LIMITS.get("function_invocations"),
        "database_limit_bytes": FREE_LIMITS.get("database_bytes"),
        "notes": [VERCEL_NOTE, REQUESTS_NOTE],
    }


def visitors_payload(env: str, range_key: str = "30d", person: str | None = None) -> dict:
    """Everything the Visitors page and `viewer usage` show, for one environment. Raises UsageError for a bad
    choice, SystemExit (naming the missing variable) if the owner connection isn't in .env, and
    neon.NeonUnavailable if the database can't be reached."""
    if env not in ("dev", "prod"):
        raise UsageError(f"Unknown environment {env!r}. Choose dev or prod.")
    url = config.viewers_url(env, "owner")
    return {
        "env": env,
        "range": range_key,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "people": report(url, range_key),
        "person": person_detail(url, person) if person else None,
        "free_plan": free_plan(url),
    }


# ---- The per-person limit on heavy requests (research R1, R2, R5) ------------------------------------------

class RateLimited(Exception):
    """A person has used up their heavy requests for now. `message` is shown to them, `retry_after` is in seconds."""

    def __init__(self, message: str, retry_after: int):
        super().__init__(message)
        self.message = message
        self.retry_after = retry_after


_DAY_START = "date_trunc('day', now() at time zone 'utc') at time zone 'utc'"
_FEATURE_ROWS = "from usage_events where viewer_id = $1::bigint and kind = 'feature'"


def _seconds(n: int) -> str:
    return f"{n} second" + ("" if n == 1 else "s")


def heavy_request(url: str, viewer_id: str | int, page: str, feature: str, detail: str | None = None) -> None:
    """Record one heavy request (a pre-defined query, a genre's song list) if the person is under their limits,
    in a single statement that both checks and records, so a refused request leaves no row (FR-011).

    Raises RateLimited when over the limit (and records one `limit` row a minute at most), and lets
    neon.NeonUnavailable and neon.NeonError through: the caller refuses the request rather than let it run
    unchecked (FR-013). Every feature use is a heavy route today, so counting `feature` rows counts them.
    """
    allowed = neon.query(
        url,
        "insert into usage_events (viewer_id, kind, page, feature, detail) "
        "select $1::bigint, 'feature', $2::text, $3::text, $4::text "
        f"where (select count(*) {_FEATURE_ROWS} and at > now() - interval '1 minute') < $5::int "
        f"and (select count(*) {_FEATURE_ROWS} and at >= {_DAY_START}) < $6::int "
        "returning 1 as ok",
        [viewer_id, page, feature, detail, HEAVY_PER_MINUTE, HEAVY_PER_DAY],
    )
    if allowed:
        return
    # Refused. Work out how long to wait, and record that the limit was hit (at most once a minute).
    info, _ = neon.transaction(url, [
        (
            f"select (select count(*) {_FEATURE_ROWS} and at >= {_DAY_START}) as day_count, "  # noqa: S608 only module constants are interpolated; values are bound
            f"(select ceil(extract(epoch from (at + interval '1 minute' - now())))::int {_FEATURE_ROWS} "
            "and at > now() - interval '1 minute' order by at desc offset ($2::int - 1) limit 1) as minute_wait, "
            f"ceil(extract(epoch from ((date_trunc('day', now() at time zone 'utc') + interval '1 day') at time zone 'utc' - now())))::int as day_wait",
            [viewer_id, HEAVY_PER_MINUTE],
        ),
        (
            "insert into usage_events (viewer_id, kind, page, feature) "  # noqa: S608 only module constants are interpolated; values are bound
            "select $1::bigint, 'limit', $2::text, "
            f"case when (select count(*) {_FEATURE_ROWS} and at >= {_DAY_START}) >= $3::int then 'day' else 'minute' end "
            "where not exists (select 1 from usage_events where viewer_id = $1::bigint and kind = 'limit' "
            "and at > now() - interval '1 minute')",
            [viewer_id, page, HEAVY_PER_DAY],
        ),
    ])
    row = info[0] if info else {}
    if _n(row.get("day_count")) >= HEAVY_PER_DAY:
        raise RateLimited("You've reached today's limit. It resets at midnight UTC.", max(1, _n(row.get("day_wait"))))
    wait = max(1, _n(row.get("minute_wait")))
    raise RateLimited(f"You're going a bit fast. Try again in {_seconds(wait)}.", wait)


def heavy_request_anonymous(url: str, visitor_hash: str, page: str, feature: str) -> None:
    """The same limit for a visitor with no login, counted per hashed client address in `anonymous_usage`.

    `visitor_hash` is a hash of the address (see api._client_hash), so no address is stored. Raises RateLimited
    when over the limit; lets neon errors through, so the caller refuses the request."""
    allowed = neon.query(
        url,
        "insert into anonymous_usage (visitor_hash, page, feature) select $1::text, $2::text, $3::text "  # noqa: S608 only module constants are interpolated; values are bound
        "where (select count(*) from anonymous_usage where visitor_hash = $1::text and at > now() - interval '1 minute') < $4::int "
        f"and (select count(*) from anonymous_usage where visitor_hash = $1::text and at >= {_DAY_START}) < $5::int "
        "returning 1 as ok",
        [visitor_hash, page, feature, HEAVY_PER_MINUTE, HEAVY_PER_DAY],
    )
    if allowed:
        return
    day = neon.query(
        url,
        f"select count(*) as n from anonymous_usage where visitor_hash = $1::text and at >= {_DAY_START}",  # noqa: S608 only module constants are interpolated; values are bound
        [visitor_hash],
    )
    if day and _n(day[0].get("n")) >= HEAVY_PER_DAY:
        now = datetime.now(timezone.utc)
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        raise RateLimited("You've reached today's limit. It resets at midnight UTC.", max(1, int((midnight - now).total_seconds())))
    raise RateLimited("You're going a bit fast. Try again in a minute.", 60)


# ---- Retention (research R8)-------------------------------------------------------------------------------

def prune(url: str) -> int:
    """Delete usage records older than RETENTION_MONTHS and say how many went. Deletes nothing else: not people,
    sessions or login attempts (FR-021). Needs the owner role, because the site's role can't delete."""
    deleted = neon.query(
        url,
        "delete from usage_events where at < now() - ($1::int * interval '1 month') returning 1 as gone",
        [RETENTION_MONTHS],
    )
    return len(deleted)


# ---- The nightly export (research R9) ----------------------------------------------------------------------

_ISO = "'YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"'"


def export_files(url: str, directory) -> tuple[int, int]:
    """Write usage_events.csv and viewers.csv into `directory` (made if missing) and return the two row counts.

    The files hold names, tiers, dates and usage only: no code, code hash, session, id or address. Rows are in a
    fixed order and the line ending is always "\\n", so an unchanged database gives byte-identical files.
    """
    import csv
    from pathlib import Path

    out = Path(directory)
    out.mkdir(parents=True, exist_ok=True)
    events, people = neon.transaction(url, [
        (
            "select v.name as viewer, e.kind, e.page, e.feature, e.detail, e.visit, e.seconds, "  # noqa: S608 only module constants are interpolated; values are bound
            f"to_char(e.at at time zone 'utc', {_ISO}) as at "
            "from usage_events e join viewers v on v.id = e.viewer_id order by e.at, e.id",
            [],
        ),
        (
            "select v.name, v.tier, v.status, coalesce(string_agg(p.page, ' ' order by p.page), '') as pages, "  # noqa: S608 only module constants are interpolated; values are bound
            f"to_char(v.created_at at time zone 'utc', {_ISO}) as created_at, "
            f"to_char(v.revoked_at at time zone 'utc', {_ISO}) as revoked_at, "
            f"to_char(v.last_login_at at time zone 'utc', {_ISO}) as last_login_at "
            "from viewers v left join viewer_pages p on p.viewer_id = v.id "
            "group by v.id order by lower(v.name), v.id",
            [],
        ),
    ])
    for filename, columns, rows in (
        ("usage_events.csv", ["viewer", "kind", "page", "feature", "detail", "visit", "seconds", "at"], events),
        ("viewers.csv", ["name", "tier", "status", "pages", "created_at", "revoked_at", "last_login_at"], people),
    ):
        with open(out / filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(columns)
            writer.writerows([["" if r[c] is None else r[c] for c in columns] for r in rows])
    return len(events), len(people)
