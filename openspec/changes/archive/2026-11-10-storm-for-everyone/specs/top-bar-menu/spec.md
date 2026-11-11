## ADDED Requirements

### Requirement: Log in is in the top bar when logged out
On the hosted site, a visitor who is not logged in SHALL see a "Log in" link at the end of the top bar and of the Mobile menu, where Log out is shown when logged in. It SHALL go to the login page. It SHALL NOT be shown when logged in, or on the owner's Mac.

#### Scenario: Logged-out visitor
- **WHEN** a logged-out visitor opens any page on the hosted site
- **THEN** the top bar ends with "Log in", and choosing it opens the login page

#### Scenario: Logged-in visitor
- **WHEN** a logged-in visitor opens any page
- **THEN** the top bar shows Log out and no Log in
