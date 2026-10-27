# Feature Specification: Storm Mode

**Feature Branch**: `feature/storm-mode` (stacked on `feature/landing-page`, PR #37)

**Created**: 2026-10-26

**Status**: Draft

**Input**: User description: "Let's do the next git issue." Issue #28 (Storm mode: full-screen rain with thunder and rain sound).

Design source: Figma `1rbbEne7pW8oA2JCNmjhrm`.

- Prototype → **Storm · Desktop** (`246:764`)
- Design system → Group 3 · Brand moments:
  - Storm rain (`255:1447`)
  - Storm sound controls (`252:1456`)
  - Page change fade (`252:1474`)
- Page pieces → Storm / Sound controls, Thunder = Off | On (`220:804`)

TypeScript app only.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Sit in the rain (Priority: P1)

I open Storm (from the landing page's bolt, or `/storm`). Rain in the Rain Girl's dotted style fills the window under the top bar. Near streaks are brighter and thicker and fall twice as fast as far ones, and it never visibly restarts. At the bottom are the sound controls (left) and a "Click the cloud icon to go Home" hint (right).

**Why this priority**: the rain is the page.

**Independent Test**: open `/storm` at 1440×900, compare with the frame, and watch for 10 seconds for any jump.

**Acceptance Scenarios**:

1. **Given** I open `/storm`, **Then** the far and near rain layers fill the window behind the breadcrumb and controls, and loop every 1.2 s with no visible jump.
2. **Given** reduced motion, **Then** the rain is still.
3. **Given** I click the cloud logo, **Then** the landing page opens with a 300 ms dissolve.

---

### User Story 2 - Turn on the thunder (Priority: P1)

The page opens with **Thunder: Off**, which is silent, with the volume slider dimmed. When I click Thunder, the pill turns bolt yellow ("Thunder: On") over 150 ms. Rain sound starts at the slider's volume, the slider wakes up, and every so often lightning flashes the screen and thunder rumbles a moment later. Clicking again stops the sound and the flashes.

**Why this priority**: the issue's sound and lightning requirements.

**Independent Test**: toggle Thunder, move the slider, and wait for a flash. Repeat with reduced motion on.

**Acceptance Scenarios**:

1. **Given** the page has just opened, **Then** no sound plays and nothing flashes.
2. **Given** I turn Thunder on, **Then** rain sound plays at the slider's volume, and changing the slider changes it immediately.
3. **Given** Thunder is on, **Then** lightning flashes come every 6–14 s. Each is at most two flickers within half a second (under 3 flashes per second, WCAG 2.3.1), followed by thunder.
4. **Given** reduced motion and Thunder on, **Then** there are no flashes, but sound still plays.
5. **Given** I leave the page, **Then** all sound stops.

### Edge Cases

- Windows wider than 1440px: the rain tiles across. Windows taller than about 1,100px may show a band without rain at the bottom (the exported layers are 1449 and 1632 px tall).
- A browser without Web Audio: the Thunder toggle still drives the flashes, without sound.

## Requirements *(mandatory)*

- **FR-001**: The rain MUST use the two exported Figma layers (far: 40%, 3 px; near: 85%, 5 px). Each moves a whole number of its streak periods per 1200 ms linear loop (far 137 px; near 2 × 137.273 px). That's within 2% of the design's 140 and 280 px, so the reset is invisible as the design intends.
- **FR-002**: Sound MUST start only after the person turns Thunder on. There's no autoplay.
- **FR-003**: Rain and thunder sounds MUST be synthesised in the browser. There are no audio files and no new dependencies.
- **FR-004**: The controls MUST be keyboard operable: Thunder is a toggle button (`aria-pressed`), and the volume is a labelled range input.
- **FR-005**: Flashes MUST stay under 3 per second and stop under reduced motion.
- **FR-006**: The Storm placeholder is replaced.

## Success Criteria *(mandatory)*

- **SC-001**: At 1440×900 the page matches the Storm · Desktop frame.
- **SC-002**: No sound before Thunder is turned on. Sound stops when Thunder is turned off or the page is left.
- **SC-003**: At 390px wide, the controls are usable with no horizontal scrolling.

## Assumptions

- Design over issue text: the issue lists the volume as the rain-sound control. The design makes Thunder the sound switch ("the volume wakes up"; "sound never plays until someone chooses it"). This follows the design.
- The default volume is 60%, the knob position in the frame.
