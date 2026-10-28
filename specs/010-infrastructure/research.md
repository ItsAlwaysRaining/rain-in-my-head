# Research: Infrastructure as code

## R1. State encryption

- **Decision**: a `terraform { encryption { … } }` block with `key_provider "pbkdf2"` (the passphrase from `var.state_passphrase`, at least 16 characters, validated) and `method "aes_gcm"`, `enforced = true`, for both state and plan.
- **Verified**: a scratch rehearsal with a `random_password` resource.
  - The state's top-level keys were only `encrypted_data`, `encryption_version`, `lineage`, `meta` and `serial`.
  - The generated password appeared 0 times, and resource names appeared 0 times.
  - A second plan had no changes.
  - A wrong passphrase failed with "decryption failed".

## R2. Neon roles and the app role

- **Finding**: roles created through Neon's API, and so through the provider's `neon_role`, are members of `neon_superuser`.
- **Decision**:
  - Create owner roles through the provider.
  - Create the app role `rain_app` in phase 4 with `CREATE ROLE … LOGIN PASSWORD` as the owner, using a password from `random_password` here, with grants on the visitor tables only.
  - Phase 4 reads it from the `NEON_*_APP_URL` GitHub secrets.
- **Note**: a child branch copies its parent's roles and databases, so `dev` uses different names (`rain_dev_owner`, `visitors_dev`). Its inherited copy of `visitors` is unused.

## R3. Hosts

- **Decision**: prod uses `neon_project.database_host`, the default endpoint. dev gets its own `neon_endpoint` (`read_write`).
- **Free plan**: both at 0.25 CU, suspending after 5 minutes. The free plan only bills compute while the endpoint is awake, within its free allowance.

## R4. Vercel

- **Decision**:
  - `vercel_project` with no `git_repository`
  - `vercel_authentication.deployment_type = "standard_protection"`, so previews need a Vercel login
  - `resource_config.function_default_regions = ["iad1"]`, which replaces the deprecated `serverless_function_region`
- **Environment variables**: one resource per key, with `for_each` over `production` and `preview`. The values come from Neon outputs and `random_password`, with `sensitive = true` for the URL and the secret.
- **The team ID** isn't secret. It goes in the committed `terraform.tfvars`, and `github.tf` copies it to `VERCEL_ORG_ID` for the CLI in phase 6.

## R5. Who applies

- **Decision**: there's no apply on merge. A `workflow_dispatch` on the PR branch applies, then commits `terraform.tfstate` to that branch. It refuses `refs/heads/main`.
- **Rationale**:
  - The owner's decision on 2026-10-27, to protect the accounts.
  - The state still reaches `main` only through the reviewed PR (CLAUDE.md).
- **Bootstrap**: the first apply runs from the owner's Mac, because it creates the GitHub secrets CI later reads.

## R6. The scanner

- **Decision**: Checkov 3.3.29 through `uvx`, not a third-party scanning action, to keep third-party code in the workflow to a minimum.
- **Coverage**: Checkov has few Vercel or Neon rules today. The workflow's own guard (every committed `*.tfstate` must contain `encrypted_data`) is the check that matters.

## R7. The drift check

- **Decision**: `tofu plan -detailed-exitcode` every Monday.
  - Exit 2 opens an issue titled "Infrastructure drift", or comments on the open one.
  - Exit 1 fails the run: an error, such as an expired token.
  - Exit 0 does nothing.
