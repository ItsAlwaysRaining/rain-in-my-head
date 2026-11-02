# Spec Delta

## Purpose

Checks that run on every pull request so a broken test, a broken frontend build, a leaked secret or an unsafe code pattern is caught before the owner reviews the change.

## ADDED Requirements

### Requirement: Checks run on every pull request
On every pull request and on every push to `main`, the repository SHALL run: a smoke test of the API in hosted mode, the frontend build, a scan of the committed files and history for secrets, and a security lint of the Python code. Each check SHALL show on the pull request as its own result.

#### Scenario: Open a pull request
- **WHEN** a pull request is opened
- **THEN** the pull request lists a result for the smoke test, the frontend build, the secret scan and the security lint

#### Scenario: A test fails
- **WHEN** the smoke test fails
- **THEN** its result is red and the other results still report

### Requirement: The smoke test covers the hosted path
The smoke test SHALL build the dataset from the committed data, start the API in hosted mode, and check that: the health route answers, a locked route refuses a request with no login, the typed-SQL route refuses even a logged-in tier, and a route that reads the dataset answers once a session is supplied. It SHALL NOT need the network or a database server.

#### Scenario: Health
- **WHEN** the smoke test asks the health route of the hosted API
- **THEN** it answers `ok` and reveals nothing else

#### Scenario: Locked without a login
- **WHEN** the smoke test asks a locked route with no session
- **THEN** the answer is a refusal, not data

#### Scenario: Typed SQL
- **WHEN** the smoke test sends typed SQL to the hosted API
- **THEN** it is refused

#### Scenario: A change that breaks start-up
- **WHEN** a change makes the API fail to start in hosted mode, for example a missing dataset path
- **THEN** the smoke test fails before any deploy is tried

### Requirement: A leaked secret fails the check
The secret scan SHALL fail when a file in the pull request contains something that looks like a token, key or connection string, and the failure SHALL NOT print the value found.

#### Scenario: Token in a file
- **WHEN** a commit adds a file containing a string shaped like an API token
- **THEN** the secret scan fails and names the file and rule, not the value

#### Scenario: Known test data
- **WHEN** a file contains a documented, harmless value such as a placeholder in `.env.example`
- **THEN** the scan passes, because the exception is written down in the repository

### Requirement: The security lint blocks unsafe patterns
The Python lint SHALL apply Ruff's security (`S`) rules to `src/` and `api/`. A finding SHALL fail the check unless the line carries a written reason for ignoring that rule.

#### Scenario: Unsafe call
- **WHEN** a change adds a call the rules flag, such as building a shell command from input
- **THEN** the lint fails on that line

#### Scenario: Reasoned exception
- **WHEN** a flagged line carries an ignore comment that says why
- **THEN** the lint passes

### Requirement: Checks do not need secrets
The checks SHALL run on pull requests from forks and SHALL NOT use any repository secret, so a result never depends on who opened the pull request.

#### Scenario: Fork pull request
- **WHEN** a pull request comes from a fork
- **THEN** all four checks run to a result without any secret
