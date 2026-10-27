# Implementation Plan: Landing Page

**Branch**: `feature/landing-page` | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md)

## Summary

Replace the Coming Soon home with the Figma Rain Girl hero. The page uses two SVGs exported from Figma:

- **The artwork**: the rain loop with its own bolt hidden. It's rendered inline so CSS can animate its rain lines.
- **The Lightning bolt (Rest)**: an `<img>` inside a router `<Link>` to `/storm`, rotated on hover.

Only `web/` changes.

## Technical Context

**Language/Version**: TypeScript 7, React 19

**Primary Dependencies**: existing only. Vite's `?raw` import loads the artwork, and react-router's `viewTransition` gives the dissolve.

**Storage**: N/A

**Testing**: `npm run build`, plus headless Chrome screenshots at 1440×900 and 390×844 compared with the frame, and hover, click and keyboard checks.

**Target Platform**: desktop and mobile browsers

**Constraints**: no new dependencies, and no redrawn artwork.

## Research (Phase 0)

- **Rain loop**: the two Figma variants are the same SVG, with 17 rain paths whose `opacity` is 0 or 1. Variant 1 lights Lines 2, 4, 6, 8, 10, 12 and 14, and variant 2 lights the others. The rest of the artwork is identical. The hero's export is variant 1 with its bolt (`Vector`) at opacity 0, so one file plus two CSS keyframe sets (selected by `id`) reproduces the loop: hold 800 ms, smart animate 300 ms, hold 1 ms, smart animate 300 ms. That's a 1401 ms cycle.
  - Alternative: cross-fading two `<img>`s. Rejected, because variant 2's export has its own bolt, which would show from under the tilted overlay bolt.
- **Bolt hover**: Figma's Hover variant is the Rest bolt at −25° instead of −18°. A CSS `rotate(-7deg)` with a 300 ms transition reproduces the smart animate on the Rest asset.
- **Dissolve**: `<Link viewTransition>` plus `::view-transition-*` animations set to 300 ms. Browsers without view transitions navigate without it.
- **Geometry**: in the 569×624 clipped frame, the artwork box is 661.221×559.622 at (−47.61, 30.69) and the bolt is 134×155 at (195, 303), as in the design context. The frame scales down as a whole (CSS `scale` set from the available height and width), so the bolt stays over the cloud.

## Constitution Check (v1.2.0)

| Principle | Status |
|---|---|
| I–II | Pass. No data changes. This spec comes first, on its own branch. |
| III | Planned: browser check, compared with the frame. |
| IV | Pass. No new packages. |
| V | Pass. No external calls. The artwork is local. |
| VI | TypeScript only (Streamlit has no landing page). Noted in `docs/streamlit-vs-typescript.md`. |
| VII | Pass. Nothing about visitors is collected. |

## Project Structure

```text
web/src/assets/landing/rain-girl.svg   # Figma export of the hero's rain loop (bolt hidden), unmodified
web/public/landing/bolt.svg            # Figma export of Landing / Lightning bolt, State=Rest, unmodified
web/src/pages/Landing.tsx, Landing.module.css   # NEW
web/src/pages/Placeholders.tsx         # Home placeholder removed
web/src/App.tsx                        # / → Landing
web/src/theme.css                      # view-transition timing
```
