## ADDED Requirements

### Requirement: Separate Rain and Thunder controls
Storm SHALL show a Rain control and a Thunder control. Each SHALL have an on/off toggle exposed with `aria-pressed` and a labelled volume slider that is disabled while its toggle is off. Both SHALL be Off when the page opens, and no sound SHALL play until one is turned on.

#### Scenario: Page opens
- **WHEN** a visitor opens Storm
- **THEN** Rain and Thunder are both Off, both sliders are disabled and no sound plays

#### Scenario: Rain only
- **WHEN** Rain is On and Thunder is Off
- **THEN** the rain sound plays and there are no lightning flashes and no thunder

#### Scenario: Thunder only
- **WHEN** Thunder is On and Rain is Off
- **THEN** lightning flashes and thunder rumbles happen and there is no rain hiss

#### Scenario: Separate volumes
- **WHEN** a visitor moves the Rain slider
- **THEN** only the rain sound's volume changes, immediately, and the thunder volume is unchanged

#### Scenario: Both off
- **WHEN** both toggles are turned Off, or the visitor leaves the page
- **THEN** all sound stops and the audio is closed

### Requirement: Safe lightning
Lightning SHALL flash fewer than 3 times per second (WCAG 2.3.1). Under `prefers-reduced-motion` there SHALL be no flashes, but sound SHALL still work. The controls SHALL fit at 390px wide with no horizontal scrolling.

#### Scenario: Reduced motion
- **WHEN** a visitor with `prefers-reduced-motion: reduce` turns Thunder On
- **THEN** thunder rumbles play and no flash is shown
