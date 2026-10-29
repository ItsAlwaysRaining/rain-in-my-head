# Tasks: Infrastructure as code

**Tests**: no suite. The checks are in [quickstart.md](quickstart.md).

## Phase 1: Setup

- [x] T001 Install OpenTofu 1.13.2 locally, and pin the providers (vercel 5.21.1, neon 0.18.0, github 6.13.0, random 3.9.1) and the actions by SHA
- [x] T002 [P] infra/.gitignore: `.terraform/` and plan files. State is committed, encrypted.

## Phase 2: Foundational

- [x] T003 infra/main.tf: required providers and the encryption block (PBKDF2 → AES-GCM, `enforced` for state and plan). infra/variables.tf: `state_passphrase` (sensitive, at least 16 characters), `vercel_team_id`, the repo and the region.
- [x] T004 Run the encryption rehearsal in a scratch folder (research R1)

## Phase 3: US1, everything in code (P1)

- [x] T005 [US1] infra/neon.tf: the project (`prod`, `rain_owner`, `visitors`, 0.25 CU, 6 h history); the `dev` branch, endpoint, `rain_dev_owner` and `visitors_dev`; the app passwords and the URL locals
- [x] T006 [US1] infra/vercel.tf: the project (no Git, `standard_protection`, `iad1`), plus `LISTENING_HOSTED`, `DATABASE_URL` and `SESSION_SECRET` for production and preview
- [x] T007 [US1] infra/github.tf: `VERCEL_PROJECT_ID` and `VERCEL_ORG_ID` variables, and the `NEON_{PROD,DEV}_{OWNER,APP}_URL` secrets. infra/outputs.tf.
- [x] T008 [US1] Run `tofu fmt -check` and `tofu validate`, and lock providers for linux_amd64 and darwin_arm64
- [x] T009 [US1] **Owner**: add infra/terraform.tfvars with `vercel_team_id` and `neon_org_id`, run the first apply from the Mac, and commit the encrypted state (quickstart)
- [ ] T010 [US1] A second plan shows 0 changes. Check the Vercel and Neon dashboards.

## Phase 4: US2, encrypted state (P2)

- [x] T011 [US2] Workflow guard: fail if any committed `*.tfstate` or `*.tfplan` lacks `encrypted_data`
- [x] T012 [US2] After T009, search the committed state for `neon.tech` and the role names: 0 matches

## Phase 5: US3, reviewed changes (P3)

- [x] T013 [US3] .github/workflows/infra.yml:
  - the PR plan job (guard, fmt, validate, Checkov, plan, PR comment)
  - a manual apply that refuses `main` and commits the state to the branch
  - the weekly drift job (opens or updates an issue)
  - `permissions: {}` by default, secrets only in the steps that need them, and `concurrency: infra`
- [x] T014 [US3] Run `actionlint` on the workflow, and Checkov locally
- [ ] T015 [US3] After T009, run one PR plan and one manual apply on a branch, then trigger the drift check by hand

## Phase 6: Polish

- [x] T016 README: the Hosting infrastructure section (first apply, changes, token renewal, lost passphrase, the scratch Neon project)
- [x] T017 Open the PR. T009, T010, T012 and T015 wait for the owner's accounts.
