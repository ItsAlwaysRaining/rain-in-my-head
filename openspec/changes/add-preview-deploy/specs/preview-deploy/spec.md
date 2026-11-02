# Spec Delta

## Purpose

Every pull request from this repository gets its own online copy of the site, locked to the owner, so the whole hosted path can be tried against dev data before production exists.

## ADDED Requirements

### Requirement: A preview for every pull request
When a pull request from a branch of this repository is opened or updated, a workflow SHALL build the two-year dataset, build the site, deploy it to Vercel as a **preview** (never production), and post the preview address on the pull request. A later push to the same pull request SHALL update the same comment, not add another.

#### Scenario: Open a pull request
- **WHEN** a pull request is opened from a branch of this repository
- **THEN** within about five minutes the pull request shows a comment with a preview address

#### Scenario: Push again
- **WHEN** another commit is pushed to the same pull request
- **THEN** the existing comment shows the new preview address and the pull request still has one preview comment

#### Scenario: Never production
- **WHEN** the workflow runs on any pull request
- **THEN** the production deployment and the `rain.storyandstructure.studio` address are unchanged

### Requirement: Previews are locked
A preview SHALL open only for people logged in to the owner's Vercel team. Someone with the address but no Vercel login SHALL NOT see the site.

#### Scenario: Open a preview logged out
- **WHEN** a browser with no Vercel login opens a preview address
- **THEN** it is sent to Vercel's login page and no page or API response from the site is shown

#### Scenario: Open a preview as the owner
- **WHEN** the owner, logged in to Vercel, opens the preview address
- **THEN** the site's own login page appears

### Requirement: The preview serves the real site on dev data
The preview SHALL serve the built dashboard and the API. The API SHALL read the two-year dataset built from the committed scrobbles and lookups, and SHALL keep visitor data (invite codes, sessions, usage) in the Neon `dev` branch only. A preview SHALL NOT read or write the `prod` branch.

#### Scenario: Log in with a test code
- **WHEN** the owner opens a preview and enters a valid invite code created on the `dev` branch
- **THEN** the pages that code unlocks load with listening data, and the Visitors page on the owner's Mac shows that session under `dev`

#### Scenario: A prod code on a preview
- **WHEN** someone enters an invite code that exists only on the `prod` branch
- **THEN** the login is refused like any unknown code

#### Scenario: Pages of the app load directly
- **WHEN** a browser opens a preview address ending in an app route such as `/genre`
- **THEN** the app loads that page, not an error

#### Scenario: Hosted limits apply
- **WHEN** a request on a preview asks for typed SQL, a playlist or AI
- **THEN** it is refused exactly as on the hosted site

### Requirement: No dataset older than the window
The dataset in a preview SHALL contain no play older than 730 days before it was built, and it SHALL be built fresh for each deploy. It SHALL NOT be committed.

#### Scenario: Check the dataset
- **WHEN** the oldest play in the deployed dataset is queried
- **THEN** it is no more than 730 days older than the deploy date

### Requirement: Pull requests from outside this repository do not deploy
A pull request from a fork SHALL NOT be deployed and SHALL NOT be given access to any secret. The workflow SHALL end without error.

#### Scenario: Fork pull request
- **WHEN** a pull request comes from a fork
- **THEN** no deploy step runs and no secret is exposed to it

### Requirement: Secrets stay secret
The workflow SHALL read the Vercel token only from the repository's Actions secrets, SHALL NOT print it or any connection string, and SHALL NOT write secret values to the pull request comment or the job summary.

#### Scenario: Read the logs
- **WHEN** the logs and the pull request comment of a deploy run are searched for the token and for `postgres://`
- **THEN** neither is found
