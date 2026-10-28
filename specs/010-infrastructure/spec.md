# Feature Specification: Infrastructure as code

**Feature Branch**: `feature/infrastructure`

**Created**: 2026-10-28

**Status**: Draft

**Input**: Hosting phase 3. Declare every hosted resource in code, in `infra/`. That covers:
- the Vercel project that serves the site
- the Neon Postgres project for visitor data, with `dev` and `prod` branches
- the GitHub Actions secrets and variables the workflows need

The state that tracks these resources is committed to git, encrypted. Changes are planned on every pull request, and applied only when the owner starts the apply by hand.

Decided with the owner:
- free plans, with no card (constitution VII)
- tokens expire after 90 days
- apply only by hand, from a manual run, never automatically on merge
- the Neon app role gets the least access that works, and a separate owner role handles clean-up

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Everything that's hosted is written down in the repo (Priority: P1)

I read `infra/` and know exactly what exists on Vercel, Neon and GitHub, and how each piece is configured. When I run the first apply, it creates all of it. When I run it again, it changes nothing.

**Why this priority**: this is "infrastructure as code". Without it there's nothing to deploy to, and settings changed by hand in dashboards would be lost or forgotten.

**Independent Test**: with the owner's tokens in the shell, run the first apply from the Mac, then a second plan. Check each service's dashboard.

**Acceptance Scenarios**:

1. **Given** empty Vercel and Neon accounts, **When** I run the apply, **Then** they're created:
   - one Vercel project with no Git connection, and previews that need a Vercel login to view
   - one Neon project with `prod` and `dev` branches, each with a database and an owner role, plus a generated password and connection string for the app role that phase 4 creates
   - the GitHub Actions secrets and variables the later phases need
2. **Given** that apply has finished, **When** I run a plan again, **Then** it reports no changes.
3. **Given** the Vercel project, **When** I look at its environment variables, **Then**:
   - production points at Neon `prod`
   - previews point at Neon `dev`
   - both use the app role
   - a session-signing secret is set
   - I never had to type any of these values myself
4. **Given** any resource, **When** I look for its settings in the repo, **Then** every setting I care about is in `infra/`. Nothing is configured by hand.

---

### User Story 2 - The state file is in git but can't be read (Priority: P2)

The record of what OpenTofu created is committed to the repo, but it's encrypted. Someone who got a copy of the repo without my passphrase learns nothing from it: no passwords, no tokens, no connection strings.

**Why this priority**: the state holds every secret the tool created. Keeping it in git means no extra storage service to sign up for.

**Independent Test**: after the first apply, open the committed state file and search it for any known secret (the database host, a password prefix) and for plain JSON keys. Then decrypt it with the passphrase and confirm it's valid.

**Acceptance Scenarios**:

1. **Given** the committed state, **When** I read it without the passphrase, **Then** it contains no secret values and no readable resource details.
2. **Given** the passphrase, **When** OpenTofu runs, **Then** it reads and updates the state normally.
3. **Given** a plan saved to a file, **Then** it's encrypted in the same way.
4. **Given** a commit that would add unencrypted state, **Then** the PR checks fail.

---

### User Story 3 - Every change is reviewed before it's applied (Priority: P3)

When a pull request changes `infra/`, GitHub checks the code and posts the plan: what would be created, changed or destroyed. Nothing is applied until I start the apply by hand. Once a week, a check tells me if anything in the real accounts no longer matches the code.

**Why this priority**: it protects my accounts. A bad change, or one made by an AI session, can't reach Vercel, Neon or GitHub without me starting it.

**Independent Test**:
1. Open a PR that changes one setting. Check that the PR shows a plan and that nothing changed in the account.
2. Start the apply by hand on the PR's branch. Check that the change is made and the updated encrypted state is committed to that branch.
3. Change a setting by hand in a dashboard, run the weekly check by hand, and check that it reports the drift.

**Acceptance Scenarios**:

1. **Given** a PR touching `infra/`, **When** the checks run, **Then** they check formatting, validate the code, scan it for insecure settings, and post the plan as a PR comment.
2. **Given** a PR is merged, **Then** nothing is applied automatically.
3. **Given** I start the apply by hand on a branch, **When** it finishes, **Then** the encrypted state is committed back to that branch, ready to merge with the PR.
4. **Given** two applies are started at once, **Then** the second waits for the first.
5. **Given** a setting was changed by hand, **When** the weekly check runs, **Then** it opens or updates one GitHub issue saying what drifted. **Given** nothing drifted, **Then** it does nothing.

### Edge Cases

- **A token expires.** Tokens last 90 days. When one expires, the plan fails with a message that names the token to renew, and the weekly check opens an issue.
- **The passphrase is lost.** The state can't be decrypted. The README explains how to recover: import each resource again from its ID. It's documented, not automated.
- **A free-plan limit.** Neon's free plan allows a limited number of branches and projects, and Vercel Hobby allows a limited number of projects. The code stays within them: 1 project per service and 2 Neon branches.
- **A card prompt.** If any provider asks for a card, the apply stops and the owner is told. Nothing in the code needs a paid feature.
- **The Neon "scratch" project** made during sign-up. It's not managed by the code. The README says to delete it by hand, once.
- **Secrets never appear in output.** Plans and PR comments must never show a secret value. Sensitive values are marked so the tool hides them.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: All hosted resources MUST be declared in `infra/` with OpenTofu: the Vercel project and its environment variables, the Neon project, branches, databases and roles, and the GitHub Actions secrets and variables.
- **FR-002**: The Vercel project MUST have no Git connection. Deploys come only from CI (phase 6). Preview deployments MUST need a Vercel login to view.
- **FR-003**: Neon MUST have a `prod` branch and a `dev` branch, each with its own database. Production uses `prod`, and previews use `dev`.
- **FR-004**: Each Neon branch MUST have two roles:
  - an **owner** role, which owns the database and is used only by OpenTofu, the nightly clean-up job (phase 7) and the owner's Mac. It's created here.
  - an **app** role, the only one the website uses. This phase only generates its password and connection string. Phase 4 creates the role itself with plain SQL and grants it access to the visitor tables. The role is not created through Neon's API, because roles made that way are Neon superusers. *(Found while planning, 2026-10-28.)*
  The app role MUST NOT own the database or be a superuser.
- **FR-005**: The website's connection string (app role) and a randomly generated session-signing secret MUST be set as Vercel environment variables by the code. No secret value is typed by hand, except the four the owner adds to GitHub first.
- **FR-006**: The values later workflows need MUST be written to GitHub Actions by the code: the Vercel project and team IDs, and the owner-role connection string for the clean-up job.
- **FR-007**: The state, and any saved plan, MUST be encrypted with a key derived from the owner's passphrase before it's written. The encrypted state MUST be committed in `infra/`.
- **FR-008**: The PR check MUST fail if any file in `infra/` looks like unencrypted state.
- **FR-009**: Every PR touching `infra/` MUST run a format check, validation, an insecure-settings scan and a plan, and MUST post the plan as a comment. The plan MUST hide sensitive values.
- **FR-010**: Applying MUST happen only from a run the owner starts by hand, on a chosen branch. The updated encrypted state MUST be committed back to that branch. Merging MUST NOT apply anything.
- **FR-011**: Applies MUST run one at a time.
- **FR-012**: A weekly check MUST compare the real accounts with the code, and open or update a single issue when they differ.
- **FR-013**: Every workflow MUST pin third-party actions to exact commit SHAs, MUST default to no permissions, and MUST give each secret only to the step that needs it.
- **FR-014**: All resources MUST stay within the free plans, and nothing may need a payment card.
- **FR-015**: The README MUST cover the first apply from the Mac, how to start an apply, how to renew tokens, how to recover from a lost passphrase, and how to delete the "scratch" Neon project.

### Key Entities

- **Vercel project**: the site. No Git link, protected previews, environment variables for production and preview.
- **Neon project**: visitor data. Branches `prod` and `dev`, each with a database, an app role and an owner role.
- **GitHub Actions secrets and variables**: the IDs and connection strings the deploy and clean-up workflows read.
- **Encrypted state**: OpenTofu's record of the above, committed in `infra/`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After the first apply, a second plan reports 0 changes.
- **SC-002**: The committed state contains 0 readable secrets: a search for the Neon host, role passwords or the session secret finds nothing.
- **SC-003**: 0 resources change as a result of merging a PR. Changes happen only from manual apply runs.
- **SC-004**: A setting changed by hand shows up in the weekly check's issue within one run.
- **SC-005**: The monthly cost stays at $0, and no service has a card on file.
- **SC-006**: Every third-party action in the workflows is pinned to a 40-character commit SHA.

## Assumptions

- The owner gives the Vercel Team ID (not a secret), which is committed in `infra/terraform.tfvars`.
- The owner has created the accounts and added the GitHub secrets `VERCEL_API_TOKEN`, `NEON_API_KEY`, `GH_INFRA_TOKEN` and `TOFU_STATE_PASSPHRASE` (see the to-do page) before the first apply. The code can be written and validated before then.
- The first apply runs from the owner's Mac, because the GitHub secrets that CI applies would use are created by that same apply.
- Neon region `aws-us-east-1`, close to Vercel's default region (`iad1`).
- The community Neon provider (`kislerdm/neon`) is used, since Neon has no official one. Its version is pinned.
- Phase 4 creates the tables and the grants for the app role. This phase only creates the roles.
