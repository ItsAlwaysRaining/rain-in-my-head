## Why

Issue #79 lists four small gaps between the Figma design and the web app (items 10–13 of the Figma vs web gap plan). Two need code: the top bar has no tablet or mobile layout, and the Overview's custom date range shows bare From/To inputs instead of the designed "Custom" popup. The other two were checked in Figma and need no change.

## What Changes

- **Top bar, tablet (801–1100px):** use the short labels from the Figma Tablet header: "Playlists" for Playlist Generator and "Contact" for Contact Me. Other labels stay.
- **Top bar, mobile (800px and below):** show the cloud logo and a 44×44px menu button instead of the links. The button opens a Mobile menu listing every section (with the same lock marks) and Log out. It closes on a link click, Escape, or a second button press. This replaces the current wrap-onto-more-lines layout.
- **Overview date range:** choosing the "Custom" chip opens a popup under the chips with From and To date fields, Apply and Cancel. Apply writes the dates to the URL; Cancel closes it and leaves the range as it was. The inline From/To inputs go away.
- **No change, recorded:** item 11 (Figma `262:1375` "Dashboards - Overview · Desktop" is the current frame; `5:304` is the older Hi-Fi frame) and item 12 (New artists stays its own page; the current frame has no list on the Overview).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `top-bar-menu`: "The menu fits narrow screens" changes from wrapping to a menu button and Mobile menu; adds tablet short labels.
- `dashboard-overview`: adds how a custom date range is chosen (Custom popup with Apply and Cancel).

## Impact

- `web/src/App.tsx`, `web/src/App.module.css` (top bar), `web/src/routes.ts` (short labels).
- `web/src/pages/Overview.tsx` and its CSS module (Custom popup).
- No API, data or hosting changes. Closes #79.
