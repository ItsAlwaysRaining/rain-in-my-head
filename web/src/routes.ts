// Every page's address, breadcrumb label and top-bar section, in one place (contracts/routes.md in
// specs/005-prototype-redesign). The top bar and the breadcrumbs both read this.

/** Top-bar items, left to right. `pages` are the access keys (src/rain_in_my_head/access.py) that open each one. */
export const SECTIONS = [
  { path: "/dashboards", label: "Dashboards", pages: ["overview", "new-artists", "genre", "artist", "slot", "mainstream"] },
  { path: "/playlists", label: "Playlist Generator", pages: ["playlists"] },
  { path: "/analyst", label: "Analyst", pages: ["analyst"] },
  { path: "/visitors", label: "Visitors", pages: ["visitors"] },
  { path: "/ai", label: "AI", pages: ["ai"] },
  { path: "/about", label: "About", pages: ["about"] },
  { path: "/contact", label: "Contact Me", pages: ["contact"] },
] as const;

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

/** The top-bar items a visitor can open. Hiding the rest is a convenience; the server checks every request. */
export const visibleSections = (can: (page: string) => boolean) => SECTIONS.filter((s) => s.pages.some(can));

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
