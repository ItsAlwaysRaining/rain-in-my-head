# Proposal

## Why

The owner wants the repository public so employers can read the code, specs and history. It is private today, and the nightly `analytics` workflow copies real visitor data (`viewers.csv`, `usage_events.csv`) to a branch called `analytics`. Every branch of a public repository is public, so flipping visibility now would publish visitors' names and activity.

## What Changes

- **BREAKING:** Stop the nightly usage export. Remove `.github/workflows/analytics.yml` and `.github/scripts/replace-analytics-branch.sh`. Visitor data stays only in Neon.
- Keep the 12-month promise: `viewer prune` was only ever run by the analytics workflow, so a new small nightly workflow, `.github/workflows/prune.yml`, runs it. It is separate from the deploy workflow so the deploy never holds the database owner connection.
- Amend the constitution's Data and Privacy section (version 1.2.1 to 1.3.0, MINOR): the repository is public, only `data/raw/` and `data/cache/` of `data/` are committed, no visitor data ever enters any branch, and the OpenTofu state stays encrypted.
- Update the docs that say "private": `README.md` (setup step and "nightly copy" section), `CLAUDE.md` (branch-protection note and the force-push exception), and a "superseded" note on the affected `specs/012-usage-tracking` files.
- Leave `viewer export` as a local command: it writes to a folder on the owner's Mac, not the repo.
- Out of scope: flipping the visibility and deleting the remote branches. The owner does both after merge (see the post-merge steps in `tasks.md`).

## Capabilities

### New Capabilities
- `usage-retention`: usage records older than 12 months are deleted every night, and visitor data is never copied into the repository.
- `public-repository`: what the public repository may and may not contain, and what the docs say about it.

### Modified Capabilities
<!-- None. No existing capability under openspec/specs/ covers usage tracking: spec 012 is a Spec Kit spec. -->

## Impact

- **Removed:** `.github/workflows/analytics.yml`, `.github/scripts/replace-analytics-branch.sh`.
- **Added:** `.github/workflows/prune.yml`.
- **Edited:** `.specify/memory/constitution.md`, `README.md`, `CLAUDE.md`, `specs/012-usage-tracking/{spec,plan,research,tasks,quickstart,contracts/cli}.md` (notes only).
- **Infra:** no change. `infra/github.tf` still sets `NEON_PROD_OWNER_URL` and `NEON_DEV_OWNER_URL`, and the new prune workflow still uses them. No `infra/` file mentions analytics.
- **Data made public by the flip (owner accepted):** all scrobbles since 2011 in `data/raw/` and the enrichment cache in `data/cache/`.
- **Owner steps after merge:** delete the `analytics` and `analytics-dev` branches and the old analytics workflow runs, then flip visibility.
