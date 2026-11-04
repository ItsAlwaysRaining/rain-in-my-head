## MODIFIED Requirements

### Requirement: Locked sections look locked
A section the visitor cannot open SHALL be marked locked with a lock icon and a muted style. The lock SHALL also be given in text that a screen reader announces, with the reason: "Log in to open" when logged out, "Owner only" for Visitors, and "Not in your invite code" otherwise. Locked SHALL NOT be shown by colour alone.

#### Scenario: Guest and Analyst
- **WHEN** a logged-in guest looks at the top bar
- **THEN** Analyst has no lock, and Visitors shows a lock icon that a screen reader announces as locked with "Owner only"

#### Scenario: Open sections look as before
- **WHEN** a section is one the visitor can open
- **THEN** it has no lock and looks and behaves as it does today

### Requirement: A click on a locked section shows no data
A locked section SHALL stay a link to its normal address. Opening it SHALL send a logged-out visitor to the login page, or show "Not available to you" to a logged-in visitor. It SHALL NOT make any data request.

#### Scenario: Logged-out click
- **WHEN** a logged-out visitor clicks Analyst
- **THEN** they are sent to the login page and no data request is made

#### Scenario: Guest click
- **WHEN** a guest clicks Visitors
- **THEN** the page "Not available to you" shows and no data request is made
