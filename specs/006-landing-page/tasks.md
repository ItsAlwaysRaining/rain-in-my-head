# Tasks: Landing Page

**Input**: `specs/006-landing-page/` (spec.md, plan.md). No tests requested; verification is in the browser.

## Phase 1: Setup

- [X] T001 Save the Figma exports unmodified: the hero's rain loop as `web/src/assets/landing/rain-girl.svg`, and Lightning bolt State=Rest as `web/public/landing/bolt.svg`

## Phase 2: User Story 1 - Arrive at the landing page (P1) 🎯 MVP

- [X] T002 [US1] Create `web/src/pages/Landing.tsx`: a visually hidden `h1`, and the 569×624 hero frame with the inline artwork (role="img", label "Rain in My Head") at (−47.61, 30.69), 661.221×559.622
- [X] T003 [US1] In `web/src/pages/Landing.module.css`, centre the hero in the space under the top bar, scale it to fit small windows, and add the two rain keyframe sets (1401 ms cycle; Lines 2–14 even vs. the rest), turned off under `prefers-reduced-motion`
- [X] T004 [US1] Route `/` to `Landing` and remove the Home placeholder in `web/src/App.tsx` and `web/src/pages/Placeholders.tsx`

## Phase 3: User Story 2 - Click the bolt (P1)

- [X] T005 [US2] Add the bolt `<Link to="/storm" viewTransition aria-label="Storm mode">` at (195, 303), 134×155, in `web/src/pages/Landing.tsx`. Hover and focus rotate it −7° over 300 ms in `Landing.module.css`
- [X] T006 [US2] Set view-transition old/new animations to 300 ms in `web/src/theme.css`

## Phase 4: Polish

- [X] T007 [P] Note the landing page in `README.md` and `docs/streamlit-vs-typescript.md`
- [X] T008 Build, then check in headless Chrome at 1440×900 and 390×844: geometry against the frame, the rain swap, hover tilt, click and Enter to `/storm`, and reduced motion
