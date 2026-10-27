# Research: Prototype Redesign

## R1. Fonts

- **Decision**: load Fredoka (600, 700), Lexend (300, 400, 500, 600) and Red Hat Mono (400) with one Google Fonts `<link>` in `web/index.html`, with `display=swap` and system fallbacks.
- **Rationale**: these are the families in the Figma text styles. A `<link>` adds no npm dependency (constitution IV). `swap` keeps text visible if loading fails.
- **Alternatives**: `@fontsource/*` packages (new dependencies, rejected); self-hosting the font files in `web/public` (more files to keep up to date, and no gain for a local app).
- **Note**: issue #22 (choose typography for both dashboards) is still open. This takes the Figma choice for TypeScript only.

## R2. Elevation

- **Decision**: a `--shadow-raised` token that copies Figma's Elevation/Raised: `3px 4px 10px #00000073, 1px 1px 2px #0000004d, inset 1px 1px 0 #ffffff12`. Cards use `--surface` with this shadow.

## R3. New artists page data

- **Decision**: call `/api/overview?preset=all&grain=month&period=<label>`. `over_time` gives the month options and `new_artist_list` gives the artists, both from the shared `rain_in_my_head` functions.
- **Rationale**: no backend change, and the numbers match the Overview by construction.
- **Cost**: computes the whole Overview for one list, about a second on the full history. Acceptable for a drill-down. If it's too slow, a thin `/api/new-artists` endpoint can come later.
- **Gap**: the design's "First played" column isn't in `new_artist_list`. It's left out. Plays and artist are shown.

## R4. Genre share over time

- **Decision**: one Vega-Lite multi-line chart built from `genres.panels`, flattened to (genre, start, share). Colours in order: rain, night, bolt, plum, moss, ember. Above it, a chip legend of HTML buttons that open the Genre page. Clicking a line also opens it (a point selection on `genre`).
- **Rationale**: matches the design. HTML chips are bigger, keyboard-reachable click targets (constitution VI, click anywhere reasonable).

## R5. Routes and redirects

- **Decision**: one `routes.ts` table (path, label, section, issue). The top bar and breadcrumbs both read it. Old paths redirect with `<Navigate replace>` and keep the query string.
- **Spotify**: the OAuth callback is handled by the API, and the Playlists page stays at `/playlists`, so the redirect URI doesn't change.

## R6. Coming Soon visual

- **Decision**: a `ComingSoon` component. An inline SVG cloud (rain-coloured outline) with a bolt-yellow lightning glyph and falling rain dashes animated in CSS. A "Coming soon" pill in bolt on bolt-surface. Title, description, and a link to the GitHub issue. The animation is off under `prefers-reduced-motion`.
- **Rationale**: uses the prototype's brand moments (the cloud logo, the loader's drop, the landing bolt) without needing the Rain Girl illustration, which is left for #27.

## R7. Filters on the page

- **Decision**: a shared `ChipGroup` (single-select, `role="radiogroup"`) for Date range, Grain and Listening from. The existing multi-select `Chips` is restyled to match. Custom dates show inline date inputs next to the chips.

## R8. Analyst

- **Decision**: `Analyst.tsx` renders a collapsible "Database schema" card (closed by default, holding the Schema page's content) and then the SQL page's content, with headings demoted. `/sql` and `/schema` redirect to `/analyst`. `/schema` opens with the card expanded (`?schema=open`).
