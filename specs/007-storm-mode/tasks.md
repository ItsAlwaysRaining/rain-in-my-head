# Tasks: Storm Mode

**Input**: `specs/007-storm-mode/` (spec.md, plan.md). No tests requested; verification is in the browser.

## Phase 1: Setup

- [X] T001 Save the Figma exports unmodified in `web/public/storm/`: far and near rain layers, the off and on bolt icons, and the sound icon

## Phase 2: User Story 1 - Sit in the rain (P1) 🎯 MVP

- [X] T002 [US1] Create `web/src/pages/Storm.tsx` and `Storm.module.css`: fixed full-window rain behind the content, with far and near layers (repeat-x) looping 137 px and 274.546 px per 1200 ms linear, still under reduced motion
- [X] T003 [US1] Add the bottom controls row in `Storm.tsx`: the sound pill on the left, and the "Click the cloud icon to go Home" hint pill on the right (raised pills, as in the frame)
- [X] T004 [US1] Route `/storm` to the new page, remove the Storm placeholder, and give the top bar's logo link `viewTransition`, in `web/src/App.tsx` and `web/src/pages/Placeholders.tsx`

## Phase 3: User Story 2 - Thunder (P1)

- [X] T005 [US2] Create `web/src/storm/sound.ts`: `createStorm(volume)` returns `setVolume`, `thunder()` and `close()`. It plays rain noise and thunder bursts through a master gain
- [X] T006 [US2] Add the Thunder toggle in `Storm.tsx`: `aria-pressed`, off and on looks with a 150 ms transition, and the AudioContext created on click and closed on off or unmount. The volume range input (default 60) is disabled while off
- [X] T007 [US2] Add the flash overlay and scheduler in `Storm.tsx`: strikes every 6–14 s while on, two flickers each, then thunder 0.4–1.5 s later. No flashes under reduced motion

## Phase 4: Polish

- [X] T008 [P] Note Storm in `README.md` and `docs/streamlit-vs-typescript.md`
- [X] T009 Build, then check in headless Chrome: frame comparison, loop transforms, toggle and slider states, no audio before the click, flash timing, reduced motion, and 390px
