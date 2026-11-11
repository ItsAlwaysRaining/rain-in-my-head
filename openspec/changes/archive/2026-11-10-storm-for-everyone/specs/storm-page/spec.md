## ADDED Requirements

### Requirement: Storm opens for every visitor
Storm (`/storm`) SHALL open for every visitor: logged out, guest, trusted and owner. Opening it SHALL NOT send a visitor to the login page. The landing page's lightning bolt SHALL take every visitor to Storm.

#### Scenario: Logged-out bolt click
- **WHEN** a logged-out visitor clicks the lightning bolt on the landing page
- **THEN** Storm opens and the login page is not shown
