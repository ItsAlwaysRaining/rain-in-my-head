# hosted-analyst Specification

## Purpose
TBD - created by archiving change open-analyst-to-all. Update Purpose after archive.

## Requirements

### Requirement: The Analyst page opens for every tier
On the hosted site, a logged-in guest and a trusted visitor SHALL both be able to open the whole Analyst page: the list of pre-defined queries, each query's SQL, and the schema map. A visitor who is not logged in SHALL be sent to the login page.

#### Scenario: Guest opens Analyst
- **WHEN** a logged-in guest opens Analyst
- **THEN** the query picker and the schema map load

#### Scenario: Logged out
- **WHEN** a visitor who is not logged in opens Analyst
- **THEN** they are sent to the login page

### Requirement: Only pre-defined queries run on the hosted site
On the hosted site every tier SHALL be able to run only the pre-defined queries, picked by name. Typed SQL SHALL be refused with 403 `refused` and "This DJ doesn't take requests.", for guests and trusted visitors alike. A pre-defined query counts toward the person's limit on heavy requests.

#### Scenario: Guest runs a pre-defined query
- **WHEN** a guest runs one of the listed queries
- **THEN** the result comes back

#### Scenario: Guest sends typed SQL
- **WHEN** a guest sends their own SQL
- **THEN** the API answers 403 `refused` and nothing runs
