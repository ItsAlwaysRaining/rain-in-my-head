# Feature Specification: Landing Page

**Feature Branch**: `feature/landing-page` (stacked on `feature/prototype-redesign`, PR #36)

**Created**: 2026-10-26

**Status**: Draft

**Input**: User description: "Create the landing page based on the Figma design prototype." Issue #27.

Design source: Figma `1rbbEne7pW8oA2JCNmjhrm`.

- Prototype → **Landing · Desktop** (`246:901`)
- Design system → Component animations → **Rain Girl**:
  - rain loop (`231:31166`)
  - Lightning bolt Rest/Hover (`246:851`)
  - Rain Girl hero (`246:859`)

TypeScript app only.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Arrive at the landing page (Priority: P1)

When I open the app at `/`, I see the top bar and, centred in the rest of the window, the Rain Girl artwork: the arched "Rain in My Head" wordmark over a storm cloud with a glowing outline and a lightning bolt, the girl beneath it, and rain lines either side. The rain flickers on a loop as the lit lines swap.

**Why this priority**: it's the first screen, and it replaces the Coming Soon placeholder.

**Independent Test**: open `/` at 1440×900 and compare it with the Landing · Desktop frame. Watch the rain for a few seconds.

**Acceptance Scenarios**:

1. **Given** I open `/`, **Then** the artwork is centred below the top bar at its design size (569×624 frame), with no breadcrumb and no other content.
2. **Given** the page is open, **Then** the two sets of rain lines swap on a loop: one set lit for about 0.8 s, a 0.3 s fade to the other set, then a 0.3 s fade back.
3. **Given** my system asks for reduced motion, **Then** the rain stays still (the first set lit).

---

### User Story 2 - Click the bolt to start a storm (Priority: P1)

The lightning bolt invites a click. When I hover it, it tilts a little further (from −18° to −25° over 0.3 s), and tilts back when I move away. Clicking it opens the Storm page with a short dissolve.

**Why this priority**: it's the landing page's only interaction and the route into Storm mode.

**Independent Test**: hover and click the bolt with the mouse, then tab to it with the keyboard and press Enter.

**Acceptance Scenarios**:

1. **Given** I hover the bolt, **Then** it rotates a further −7° over 300 ms. **When** I leave, it rotates back.
2. **Given** I click the bolt or press Enter on it, **Then** `/storm` opens with a 300 ms cross-fade, where the browser supports one.
3. **Given** a screen reader, **Then** the artwork is announced as "Rain in My Head" and the bolt as a link to Storm mode.

### Edge Cases

- Short or narrow windows: the artwork scales down to fit, keeping its proportions, and the bolt stays exactly over the cloud.
- Browsers without view transitions: the bolt still opens Storm, without the dissolve.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `/` MUST show the Rain Girl hero from the design, using the exact exported artwork. It MUST NOT be redrawn.
- **FR-002**: The rain lines MUST alternate between the design's two variants with the design's timing.
- **FR-003**: The bolt MUST be a link to `/storm`. Hover and keyboard focus tilt it −7° over 300 ms.
- **FR-004**: Navigation from the bolt MUST use a 300 ms dissolve where supported.
- **FR-005**: Motion MUST stop under `prefers-reduced-motion`.
- **FR-006**: The page MUST have one `h1` ("Rain in My Head"), visually hidden because the wordmark in the artwork shows it.

## Success Criteria *(mandatory)*

- **SC-001**: A screenshot at 1440×900 matches the Landing · Desktop frame in the artwork's position, size and colours.
- **SC-002**: The bolt opens Storm by mouse and by keyboard.
- **SC-003**: At 390px wide, there's no horizontal scrolling and the whole artwork is visible.

## Assumptions

- The Storm page stays a placeholder (#28). This feature only links to it.
- Issue #27's acceptance criterion "built from the Figma component (SVG, not a screenshot)" is met by the exported SVGs.
- The "Rain in My Head" wordmark is outlined in the exported SVG, so the Playwrite US Modern font isn't needed.
