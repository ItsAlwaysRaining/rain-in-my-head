## 1. Top bar

- [ ] 1.1 Add an optional `short` label to `Section` in `web/src/routes.ts` ("Playlists", "Contact")
- [ ] 1.2 Pull the link list in `web/src/App.tsx` into a `NavLinks` component that renders full and short labels
- [ ] 1.3 Add the 44px menu button and the Mobile menu panel (aria-expanded, aria-controls, Escape closes and refocuses, route change closes)
- [ ] 1.4 CSS in `web/src/App.module.css`: short labels at 801–1100px; at 800px and below hide the desktop nav and wordmark, show the button and panel

## 2. Overview Custom popup

- [ ] 2.1 Check `ChipGroup` in `web/src/components/ui.tsx` lets a click on the selected Custom chip reopen the popup; add what's needed
- [ ] 2.2 In `web/src/pages/Overview.tsx`, replace the inline From/To with a popup holding draft dates, Apply and Cancel; Escape cancels
- [ ] 2.3 Style the popup under the chips in the Overview CSS module

## 3. Check

- [ ] 3.1 `npm run build` in `web/` passes
- [ ] 3.2 In the browser: 1440, 1000 and 360px headers; Mobile menu open, choose a link, Escape; Custom Apply, Cancel and reopen
- [ ] 3.3 Archive the change, push and open the PR with `Closes #79`
