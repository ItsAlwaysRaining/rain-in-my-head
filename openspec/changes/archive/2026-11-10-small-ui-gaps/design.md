## Context

The top bar (`TopBar` in `web/src/App.tsx`) renders `SECTIONS` from `web/src/routes.ts` as `NavLink`s; below 800px the CSS stacks and wraps them. Figma's Site Header specimen (`221:150`) shows a Tablet variant with short labels ("Playlists", "Contact") and a Mobile variant with only the cloud logo and a menu button. The Overview's Custom chip (`web/src/pages/Overview.tsx`) shows two date inputs inline that write to the URL on every change.

## Goals / Non-Goals

**Goals:** match the Figma Tablet and Mobile header; replace inline dates with a Custom popup with Apply and Cancel.

**Non-Goals:** redesigning the desktop header; other pages' filters; items 11 and 12 (confirmed no change).

## Decisions

1. **Short labels as data.** Add an optional `short` label to `Section` ("Playlists", "Contact"). Render both spans and switch with CSS media queries, so there is no JS resize listener. Alternative: `matchMedia` in React. Rejected: more code for a pure display change.
2. **Mobile menu as a disclosure, not a modal.** A `<button aria-expanded aria-controls>` toggles a panel under the bar holding the same links in a column. Escape closes it and returns focus; route change closes it (via `useLocation`). Hidden above 800px with CSS; the desktop `<nav>` is hidden at 800px and below. Alternative: `<dialog>`. Rejected: the panel sits under the bar and doesn't need to trap focus.
3. **One link list, rendered twice.** Pull the link markup into a small `NavLinks` component used by the desktop nav and the Mobile menu, so lock handling stays in one place.
4. **Custom popup holds a draft.** Local state holds draft From/To. Choosing Custom opens the popup without touching the URL; Apply calls `update({ preset: "custom", start, end })`; Cancel drops the draft. The popup is an absolutely positioned panel under the chip row with `role="dialog"` and a label, closed by Escape. Native `<input type="date">` stays for the fields.
5. **Breakpoints.** Mobile is 800px and below (the existing breakpoint); tablet is 801–1100px.

## Risks / Trade-offs

- [Two copies of the links in the DOM] → only one is visible at a time, and the hidden one uses `display: none`, so screen readers see one.
- [ChipGroup fires onChange only on a new value] → the Custom chip needs a click handler that also works when Custom is already selected; check `ChipGroup` and add an `onClick` passthrough if needed.
