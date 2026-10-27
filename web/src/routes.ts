// Every page's address, breadcrumb label and top-bar section, in one place (contracts/routes.md in
// specs/005-prototype-redesign). The top bar and the breadcrumbs both read this.

/** Top-bar items, left to right. */
export const SECTIONS = [
  { path: "/dashboards", label: "Dashboards" },
  { path: "/playlists", label: "Playlist Generator" },
  { path: "/analyst", label: "Analyst" },
  { path: "/about", label: "About" },
  { path: "/contact", label: "Contact Me" },
] as const;

/** Breadcrumb label for each path below a section (the section's own label comes from SECTIONS). */
const PAGES: Record<string, string> = {
  "/dashboards/new-artists": "New artists",
  "/dashboards/genre": "Genre",
  "/dashboards/artist": "Artist",
  "/dashboards/slot": "When you listen",
  "/dashboards/mainstream": "Mainstream vs. niche",
  "/storm": "Storm",
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
