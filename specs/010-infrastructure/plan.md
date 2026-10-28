# Implementation Plan: Infrastructure as code

**Branch**: `feature/infrastructure` | **Date**: 2026-10-28 | **Spec**: [spec.md](spec.md)

## Summary

The infrastructure is defined in OpenTofu 1.13 under `infra/`:
- **`main.tf`**: pinned providers, with state and plan encryption (PBKDF2 → AES-GCM, `enforced`).
- **`neon.tf`**: the project (default branch `prod`, owner role `rain_owner`, database `visitors`). The `dev` branch has its own endpoint, owner role and database. It also generates app-role passwords and connection strings.
- **`vercel.tf`**: the project with no Git link, `standard_protection` on previews, region `iad1`, and environment variables per target: `LISTENING_HOSTED`, `DATABASE_URL` (app role) and `SESSION_SECRET` (random).
- **`github.tf`**: Actions variables `VERCEL_PROJECT_ID` and `VERCEL_ORG_ID`, plus secrets for the owner and app URLs.
- **`.github/workflows/infra.yml`**:
  - on PRs: an encrypted-state guard, `fmt`, `validate`, Checkov and a plan posted as a PR comment
  - an apply that you start by hand and that refuses `main`, then commits the encrypted state to the branch
  - a weekly drift check that opens or updates one issue

## Technical Context

**Tools**: OpenTofu 1.13.2. Providers pinned exactly:
- `vercel/vercel` 5.21.1
- `kislerdm/neon` 0.18.0
- `integrations/github` 6.13.0
- `hashicorp/random` 3.9.1

Each was released at least 2 weeks ago. `.terraform.lock.hcl` has hashes for `linux_amd64` and `darwin_arm64`.

**Actions** are pinned by SHA:
- `actions/checkout` v7.0.1
- `opentofu/setup-opentofu` v2.0.2
- `astral-sh/setup-uv` v10.2.0

Checkov 3.3.29 runs ad hoc with `uvx`.

**Storage**: the encrypted `infra/terraform.tfstate` is committed. It uses the local backend, so there's no extra service.

**Testing**:
- `tofu fmt`, `validate`, Checkov and `actionlint` run locally.
- An encryption rehearsal in a scratch folder, using a local-only resource, checks SC-002 before any account exists.
- After the owner's first apply: a second plan, a search of the state for secrets, and the dashboards.

**Constraints**: free plans only (VII), and secret values never printed (V).

## Constitution Check

| Principle | Check | Result |
|---|---|---|
| I | No data files touched. | ✅ |
| II | Spec 010 approved. FR-004 updated before the code differed (app role made by SQL in phase 4). | ✅ |
| III | No dashboard change. Infra checks are listed in quickstart and the PR. | ✅ (n/a) |
| IV | Hosting is Vercel and Neon, declared only in `infra/`. OpenTofu is a tool, not a dependency. No Python or npm dependency added. | ✅ |
| V | Secrets come from GitHub secrets, Vercel env vars and the encrypted state only. Sensitive outputs and env vars are marked sensitive. Plans hide them. | ✅ |
| VII | Free plans: Hobby, and Neon free at 0.25 CU with 2 branches. No card. The app role has least privilege (made in phase 4). | ✅ |

## Project Structure

```text
infra/
├── main.tf               # providers + encryption
├── variables.tf          # state_passphrase (sensitive), vercel_team_id, repo, region
├── terraform.tfvars      # vercel_team_id (added at the first apply; not secret)
├── neon.tf               # project, dev branch/endpoint/owner/db, app passwords, URLs
├── vercel.tf             # project + env vars
├── github.tf             # Actions variables and secrets
├── outputs.tf            # ids; owner URLs (sensitive) for the owner's .env
├── .terraform.lock.hcl   # provider hashes (committed)
├── .gitignore            # .terraform/, plan files
└── terraform.tfstate     # encrypted; appears after the first apply
.github/workflows/infra.yml
README.md                 # Hosting infrastructure section
```

## Risks

- **The community Neon provider.** It's pinned, and the drift check would catch surprises.
- **Checkov has few Vercel or Neon rules.** The real safeguards are the encrypted-state guard, pinned providers and manual apply.
- **The first PR plan fails until the secrets and `terraform.tfvars` exist.** This is expected and noted in the PR.
