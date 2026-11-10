// Every page's address, breadcrumb label and top-bar section, in one place (contracts/routes.md in
// specs/005-prototype-redesign). The top bar and the breadcrumbs both read this. Every item is shown to everyone; a locked one is only marked,
// because the server and RequireAccess check every request.

export interface Section {
  path: string;
  label: string;
  /** Shorter label for tablet widths (Figma Site Header, Tablet). */
  short?: string;
  pages: readonly string[];
  /** On no hosted tier: only the owner's Mac opens it. */
  ownerOnly?: true;
}

/** Top-bar items, left to right. `pages` are the access keys (src/rain_in_my_head/access.py) that open each one. */
export const SECTIONS = [
  { path: "/dashboards", label: "Dashboards", pages: ["overview", "new-artists", "genre", "artist", "slot", "mainstream"] },
  { path: "/playlists", label: "Playlist Generator", short: "Playlists", pages: ["playlists"] },
  { path: "/analyst", label: "Analyst", pages: ["analyst"] },
  { path: "/visitors", label: "Visitors", pages: ["visitors"], ownerOnly: true },
  { path: "/ai", label: "AI", pages: ["ai"] },
  { path: "/about", label: "About", pages: ["about"] },
  { path: "/contact", label: "Contact Me", short: "Contact", pages: ["contact"] },
] as const satisfies readonly Section[];

/** Why a section is locked for this visitor, in words (shown to screen readers beside the lock), or null if they can open it. */
export function lockReason(section: Section, auth: { can: (page: string) => boolean; loggedIn: boolean }): string | null {
  if (section.pages.some(auth.can)) return null;
  if (!auth.loggedIn) return "Log in to open";
  return section.ownerOnly ? "Owner only" : "Not in your invite code";
}

/** The access key for each page. "playlists" is on no tier, so on the hosted site nobody can open it. */
export const PAGE_KEYS = {
  "/dashboards": "overview",
  "/dashboards/new-artists": "new-artists",
  "/dashboards/genre": "genre",
  "/dashboards/artist": "artist",
  "/dashboards/slot": "slot",
  "/dashboards/mainstream": "mainstream",
  "/playlists": "playlists",
  "/analyst": "analyst",
  // The owner's usage report. On no hosted tier, so only your Mac opens it (specs/012-usage-tracking).
  "/visitors": "visitors",
  "/ai": "ai",
  "/storm": "storm",
  "/about": "about",
  "/contact": "contact",
} as const;
export type PageKey = (typeof PAGE_KEYS)[keyof typeof PAGE_KEYS];

/** Breadcrumb label for each path below a section (the section's own label comes from SECTIONS). */
const PAGES: Record<string, string> = {
  "/dashboards/new-artists": "New artists",
  "/dashboards/genre": "Genre",
  "/dashboards/artist": "Artist",
  "/dashboards/slot": "When you listen",
  "/dashboards/mainstream": "Mainstream vs. niche",
  "/storm": "Storm",
  "/login": "Log in",
};

export interface Crumb {
  label: string;
  to?: string;
}

/** Home › Section › Page for a path; empty on the home page. Unknown paths end in "Not found". */
export function breadcrumbs(pathname: string): Crumb[] {
  if (pathname === "/") return [];
  const crumbs: Crumb[] = [{ label: "Home", to: "/" }];
  const section = SECTIONS.find((s) => pathname === s.path || pathname.startsWith(`${s.path}/`));
  if (section) crumbs.push({ label: section.label, to: section.path });
  if (PAGES[pathname]) crumbs.push({ label: PAGES[pathname] });
  else if (!section) crumbs.push({ label: "Not found" });
  // The last crumb is the current page, so it isn't a link.
  delete crumbs[crumbs.length - 1].to;
  return crumbs;
}

export const issueUrl = (n: number) => `https://github.com/ItsAlwaysRaining/rain-in-my-head/issues/${n}`;
