# Proposal

## Why

The browser tab doesn't say which app it is. Streamlit shows an equaliser icon and the TypeScript app shows the browser's default icon, so the two dashboards look unrelated and neither matches the name "Rain in My Head" (#15).

## What Changes

- Both dashboards show the same cloud icon in the browser tab.
- The icon uses the project palette and is legible at 16px in light and dark browser themes.
- The icon is one SVG file that both apps read. Changing it changes both tabs.

There is no new page, CLI command, data source, dependency or schema change.

## Capabilities

### New Capabilities
- `dashboard-shell`: what both dashboards share outside the pages themselves, starting with the browser-tab icon. No spec covers this yet.

### Modified Capabilities
None.

## Impact

- Code: `dashboard/app.py` (`page_icon`), `web/index.html` (icon link), and a new `web/public/favicon.svg`. Vite serves `web/public/` at the site root and copies it into `web/dist/`.
- The palette page, `rain-in-my-head-palette.html`, is unchanged; the icon only uses colours that are already on it.
