# Spec Delta

## Purpose

Visitor activity is kept in the visitor database for 12 months and then deleted, and a copy of it is never written to the repository. This protects visitors in a repository that is public.

## ADDED Requirements

### Requirement: Usage records are deleted after 12 months
A workflow SHALL run every night and delete usage records older than 12 months from the production visitor database. It SHALL delete nothing else (people, sessions and codes are unchanged) and SHALL print only the number of records deleted. The owner SHALL also be able to run it by hand, choosing the production or the dev database.

#### Scenario: A record passes 12 months
- **WHEN** the nightly run happens and a usage record is 12 months and one day old
- **THEN** the record is deleted and the run's output states only how many records were deleted

#### Scenario: A recent record
- **WHEN** the nightly run happens and a usage record is 11 months old
- **THEN** the record is kept, and people and sessions are unchanged

#### Scenario: A run by hand on dev
- **WHEN** the owner starts the workflow by hand and chooses `dev`
- **THEN** only the dev database is pruned and production is untouched

### Requirement: Visitor data is never written to the repository
No workflow SHALL write visitor data (names, usage records or any export of them) to any branch, file, release or log of the repository. The `analytics` and `analytics-dev` branches SHALL NOT exist.

#### Scenario: Nightly run
- **WHEN** the nightly prune finishes
- **THEN** no branch or commit has been created or changed, and the run log contains counts only

#### Scenario: Branch list
- **WHEN** someone lists the repository's branches
- **THEN** there is no `analytics` or `analytics-dev` branch
