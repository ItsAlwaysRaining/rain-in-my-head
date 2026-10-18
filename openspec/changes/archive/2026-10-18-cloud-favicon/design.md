# Design

## Context

- Streamlit (`dashboard/app.py`) sets `page_icon=":material/graphic_eq:"`. Streamlit 1.65 also accepts a path to a local `.svg` file for `page_icon` and inlines it as a `data:` URL (`streamlit/elements/lib/image_utils.py`).
- The TypeScript app's `web/index.html` has no icon link, and `web/` has no `public/` folder. Vite serves `public/` at `/` in dev and copies it into `dist/` on build. `rain-in-my-head serve` already returns any file in `web/dist` by path (`api.py`, `frontend`), so `/favicon.svg` works there with no API change.

## Goals / Non-Goals

**Goals:**
- One SVG file is the only source of the icon for both apps.

**Non-Goals:**
- PNG/ICO fallbacks and an Apple touch icon. Both dashboards are opened in a desktop browser on this machine, and current Chrome, Firefox and Safari show SVG favicons.
- Changing the tab title or the sidebar menu icons.

## Decisions

**One file at `web/public/favicon.svg`, read by both apps.**
`index.html` links it as `/favicon.svg`. `dashboard/app.py` passes its absolute path (resolved from `__file__`) as `page_icon`.
- *Alternative: Streamlit's `:material/cloud:`* plus a copy of that glyph for the TS app. Rejected: the two would be rendered differently (font vs. SVG), and two sources can drift, which the spec rules out.
- *Alternative: a repo-level `assets/` folder* with Vite's `publicDir` pointed at it. Rejected: more config for no gain. Streamlit reading a file under `web/` is a small cross-app link, but it's the same kind as the shared Python modules both apps already use.

**Two-tone cloud: Rain fill, navy outline.**
The fill is `--rain` `#5CC8F0` and the outline is `--page` `#141A2A`, about 1.5px at 16px. On a white tab, the outline gives about 17:1. On a dark tab (`#202124`), the Rain fill gives about 8:1 and the outline blends in. Both colours are already in the palette.
- *Alternative: one colour plus `prefers-color-scheme` inside the SVG.* Rejected: favicon media queries follow the OS theme, not the browser's tab colour, and support varies by browser. The two-tone shape works everywhere.
- *Rain drops or a lightning bolt under the cloud.* Rejected for now: at 16px they turn into noise. The issue asks for a cloud.

**A plain cloud drawn on a 32×32 viewBox** (three overlapping arcs on a flat base), with whole-pixel coordinates so it stays crisp at 16px.

## Risks / Trade-offs

- [Streamlit drops SVG support for `page_icon` in a later release] → A Streamlit upgrade would show the default icon, not an error. The apply tasks check the tab after any upgrade, and the fix is a PNG export of the same file.
- [Browsers cache favicons hard] → When checking, reload with the cache bypassed, or open the icon URL directly.
