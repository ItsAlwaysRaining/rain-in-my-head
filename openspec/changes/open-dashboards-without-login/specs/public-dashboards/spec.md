# Spec Delta

## Purpose

On the hosted site, the listening dashboards and the other guest pages open for anyone without an invite code. Playlist creation, AI and Visitors stay closed, and the Analyst runs only the pre-defined queries.

## ADDED Requirements

### Requirement: Anonymous visitors open the guest pages
On the hosted site, a visitor without a login SHALL be able to open the Overview, New artists, Genre, Artist, Slot, Mainstream, Playlist Generator, Analyst, AI, About and Contact pages, and load their data, without being sent to the login page.

#### Scenario: Dashboard without a login
- **WHEN** an anonymous visitor opens the Artist page
- **THEN** the page loads its data and no login page is shown

#### Scenario: Visitors page without a login
- **WHEN** an anonymous visitor opens the Visitors page
- **THEN** the visitor is sent to the login page

### Requirement: Playlist creation stays refused
On the hosted site, creating a playlist SHALL be refused for every visitor, with the message "This DJ doesn't take request".

#### Scenario: Create a playlist anonymously
- **WHEN** an anonymous visitor tries to create a playlist
- **THEN** the site shows "This DJ doesn't take request" and no playlist is created

### Requirement: AI stays off
On the hosted site, the AI page SHALL show its existing error page for every visitor, and no AI route SHALL run.

#### Scenario: Open the AI page
- **WHEN** any visitor opens the AI page
- **THEN** the AI error page is shown and no AI request is made

### Requirement: Analyst runs only the pre-defined queries
On the hosted site, the Analyst SHALL run only the six pre-defined queries by name for every visitor. Typed SQL SHALL be refused.

#### Scenario: Typed SQL on the hosted site
- **WHEN** a visitor submits typed SQL
- **THEN** the request is refused and nothing runs

#### Scenario: Pre-defined query
- **WHEN** an anonymous visitor runs "Top artists this year"
- **THEN** the query runs and its result is shown

### Requirement: Anonymous visits are not tracked
On the hosted site, page-view and time-on-page reports from anonymous visitors SHALL be ignored, not stored.

#### Scenario: Anonymous page view
- **WHEN** an anonymous visitor opens a dashboard page
- **THEN** no usage record is stored for that visit
