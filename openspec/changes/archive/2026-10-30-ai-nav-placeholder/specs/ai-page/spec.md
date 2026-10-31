# Spec Delta

## Purpose

The AI item in the TypeScript app's top nav and its `/ai` page. Until the AI playlist (#32) is built, the page tells visitors that it is planned and links to the issue.

## ADDED Requirements

### Requirement: AI in the top nav
The top nav SHALL show an **AI** item directly after **Analyst** and before **About**. It SHALL open `/ai`, SHALL show as the current section while that page is open, and the breadcrumbs SHALL read Home › AI.

#### Scenario: Nav order
- **WHEN** any page of the TypeScript app is open
- **THEN** the top nav reads Dashboards, Playlist Generator, Analyst, AI, About, Contact Me, in that order

#### Scenario: Open from the nav
- **WHEN** a visitor clicks **AI** in the top nav
- **THEN** the page at `/ai` opens, the AI item is highlighted, and the breadcrumbs read Home › AI

### Requirement: Coming soon placeholder
Until the AI playlist is built, the `/ai` page SHALL show the title **AI** and a Coming soon card that describes the AI playlist and links to GitHub issue #32 in a new tab. The Playlist Generator's AI tab SHALL stay, showing the same card.

#### Scenario: Placeholder content
- **WHEN** the `/ai` page is open
- **THEN** it shows the title "AI", a "Coming soon" card describing the AI playlist, and a link to issue #32 that opens in a new tab

#### Scenario: Playlist Generator tab unchanged
- **WHEN** a visitor opens the AI tab in the Playlist Generator
- **THEN** it shows the same Coming soon card with the link to issue #32

### Requirement: AI page access
On the hosted site, the `/ai` page SHALL have its own access key, `ai`, which every tier opens, so any visitor with a code sees the AI nav item and the page. The page SHALL load no data. Page keys that can be granted SHALL include `ai`.

#### Scenario: Guest sees AI
- **WHEN** a guest is logged in to the hosted site
- **THEN** the top nav shows AI and `/ai` opens the Coming soon page

#### Scenario: No data loaded
- **WHEN** the `/ai` page opens
- **THEN** it makes no `/api` data request

### Requirement: Fits narrow screens
With the extra nav item, the top nav SHALL still fit narrow screens by wrapping, and no page SHALL scroll sideways.

#### Scenario: Phone
- **WHEN** the `/ai` page is open in a window 390 px wide
- **THEN** every nav item is visible and the page has no horizontal scroll
