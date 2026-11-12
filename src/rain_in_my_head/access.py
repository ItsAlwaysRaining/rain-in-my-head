"""Who may open what on the hosted site (specs/011-viewer-access, research R5).

A visitor's pages are their tier's starting pages plus any the owner granted. Every `/api` route that returns
data is listed in API_ACCESS with the pages that unlock it; a route that isn't listed is refused, and the app
refuses to start if one is missing (api.check_routes).
"""

from __future__ import annotations

# One key per page. The same keys are used by the `viewer grant` command and by web/src/routes.ts.
PAGES = (
    "overview", "new-artists", "genre", "artist", "slot", "mainstream", "analyst", "ai", "storm", "about", "contact",
)

GUEST_PAGES = frozenset({
    "overview", "new-artists", "genre", "artist", "slot", "mainstream", "playlists", "analyst", "ai", "storm", "about", "contact",
})
TIER_PAGES = {
    "guest": GUEST_PAGES,
    "trusted": GUEST_PAGES,
}

# (method, path) -> the pages that unlock it. Any one of them is enough: Overview and New artists both use
# /api/overview. Pages with no entry (About, Contact, Storm, AI, the coming-soon pages) load no data.
API_ACCESS: dict[tuple[str, str], frozenset[str]] = {
    ("GET", "/api/overview"): frozenset({"overview", "new-artists"}),
    ("GET", "/api/genre"): frozenset({"genre"}),
    ("GET", "/api/genre/songs"): frozenset({"genre"}),
    ("GET", "/api/artist"): frozenset({"artist"}),
    ("GET", "/api/mainstream"): frozenset({"mainstream"}),
    ("GET", "/api/slot"): frozenset({"slot"}),
    # The Playlist Generator's form and track preview only read the database. Creating a playlist stays refused
    # on the hosted site (api.HOSTED_PLAYLIST_READS lists the only playlist routes it lets through).
    ("GET", "/api/playlists/meta"): frozenset({"playlists"}),
    ("POST", "/api/playlists/preview"): frozenset({"playlists"}),
    ("GET", "/api/sql/meta"): frozenset({"analyst"}),
    ("POST", "/api/sql"): frozenset({"analyst"}),
    ("GET", "/api/schema"): frozenset({"analyst"}),
}

# Open to anyone. Login and logout check the request themselves; health says only that the app is up.
PUBLIC_ROUTES = frozenset({
    ("GET", "/api/health"),
    ("GET", "/api/me"),
    ("POST", "/api/login"),
    ("POST", "/api/logout"),
})


# Routes any logged-in person with at least one page may call (specs/012-usage-tracking): the browser's page-view
# and time-on-page reports. They carry no data back, so no particular page unlocks them.
SESSION_ROUTES = frozenset({
    ("POST", "/api/events"),
})


def pages_for(tier: str, granted: set[str] | frozenset[str]) -> frozenset[str]:
    """The pages a visitor can open: their tier's starting pages plus their grants."""
    return TIER_PAGES.get(tier, frozenset()) | (frozenset(granted) & set(PAGES))


def allowed(pages: set[str] | frozenset[str], method: str, path: str) -> bool:
    """True if a visitor with these pages may call this route. An unlisted route is never allowed."""
    unlock = API_ACCESS.get((method, path))
    return bool(unlock and unlock & set(pages))


def session_allowed(pages: set[str] | frozenset[str], method: str, path: str) -> bool:
    """True for a SESSION_ROUTES route when the visitor has at least one page."""
    return (method, path) in SESSION_ROUTES and bool(pages)
