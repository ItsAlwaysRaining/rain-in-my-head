# Implementation Plan: Storm Mode

**Branch**: `feature/storm-mode` | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md)

## Summary

A Storm page with two looping CSS rain layers (the exported Figma SVGs as tiled backgrounds), the Figma sound controls, a flash overlay, and a small Web Audio synth for rain and thunder.

## Technical Context

**Language/Version**: TypeScript 7, React 19

**Primary Dependencies**: none new. The Web Audio API is built into browsers.

**Testing**: `npm run build`. Headless Chrome checks:
- geometry and screenshot against the frame
- the layers' transforms over time
- toggle states and `aria-pressed`
- the slider enabled or disabled
- no `AudioContext` before Thunder is clicked
- flash timing (run with a short interval)
- reduced motion

**Constraints**: no autoplay, no audio files, under 3 flashes per second.

## Research (Phase 0)

- **Rain**: the frame's two layers are exported SVGs. Far is 1440×1449, placed 388 px above the rain box. Near is 1440×1632, placed 547 px above. The streak periods are 137.000 and 137.273 px, so moving 137 and 274.546 px per loop makes the reset land on an identical frame. Figma's own 140 and 280 px moves would jump 3 and 5.5 px. The layers are `background-repeat: repeat-x` so they tile on wide windows.
- **Sound**: rain is looping white noise through high-pass (400 Hz) and low-pass (3.2 kHz) filters. Thunder is a 4–6 s noise burst through a falling low-pass (900 → 120 Hz), with a fast attack and exponential decay. Both go through a master gain set by the slider. The `AudioContext` is created in the Thunder click handler (a user gesture) and closed when Thunder is turned off or the page is left.
  - Rejected: bundling rain and thunder recordings. That needs licensing, adds a few MB of assets, and the design has none.
- **Flashes**: a full-screen overlay. Each strike is two flickers, about 0.06 s and 0.3 s apart (2 flashes in under 0.5 s, so under 3 per second), followed by thunder 0.4–1.5 s later. Strikes come every 6–14 s at random.
- **Controls**: the Figma component is one `<button>` containing a slider, which isn't valid HTML. The code splits it into a toggle `<button aria-pressed>` and a labelled `<input type="range">` in the same pill.
- **Back home**: the top bar's cloud logo gets `viewTransition`, matching the design's "Back to home" dissolve. This applies on every page.

## Constitution Check (v1.2.0)

| Principle | Status |
|---|---|
| I–II | Pass. No data changes. This spec comes first, on its own branch. |
| III | Planned: browser checks. |
| IV | Pass. No new packages, and no audio files. |
| V | Pass. No external calls. |
| VI | TypeScript only. Noted in `docs/streamlit-vs-typescript.md`. |
| VII | Pass. Nothing collected. |

## Project Structure

```text
web/public/storm/{far-rain,near-rain,bolt-off,bolt-on,sound-on}.svg   # Figma exports, unmodified
web/src/pages/Storm.tsx, Storm.module.css                            # NEW
web/src/storm/sound.ts                                               # NEW: Web Audio rain + thunder
web/src/pages/Placeholders.tsx, web/src/App.tsx                      # route, logo dissolve
```
