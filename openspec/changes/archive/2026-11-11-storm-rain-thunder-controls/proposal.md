## Why

Storm's single Thunder switch starts rain sound, lightning and thunder together, with one volume for all of it. You can't sit with the rain while music plays without thunder interrupting, or have the flashes and rumbles without the rain hiss (#39).

## What Changes

- Replace the one Thunder pill with two pills side by side: **Rain** and **Thunder**.
- Each pill has an on/off toggle (`aria-pressed`) and its own labelled volume slider, disabled while its toggle is off.
- Rain controls only the rain hiss. Thunder controls lightning flashes and thunder rumbles. The volumes are fully separate.
- Both start Off. The audio starts on the first toggle click and closes when both are off or the page is left.

Design decisions for the issue's open questions: two pills (not one), both start Off, fully separate volumes.

## Capabilities

### Modified Capabilities

- `storm-page`: adds the Rain and Thunder sound controls.

## Impact

- `web/src/storm/sound.ts` (separate rain and thunder gains), `web/src/pages/Storm.tsx`, `web/src/pages/Storm.module.css`.
- No new dependencies, no audio files, no data or hosting changes.
- Figma (Storm · Desktop `246:764`, Storm / Sound controls `220:804`) to be updated to match.
