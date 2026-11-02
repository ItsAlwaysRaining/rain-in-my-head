# Instructions for Claude

## Specs before code

Every change except docs and chores starts with a spec. There are two tracks:

| Track | Use for | Commands | Specs live in |
|---|---|---|---|
| **GitHub Spec Kit** | New features: a new dashboard page, CLI command, data source or dependency, a schema change, or anything touching several modules | `/speckit-specify` → (`/speckit-clarify`) → `/speckit-plan` → `/speckit-tasks` → (`/speckit-analyze`) → `/speckit-implement` | `specs/NNN-<name>/` (spec, plan, tasks) |
| **OpenSpec** | Fixes and small additions to existing behaviour, usually in one module | `/opsx:propose` → `/opsx:apply` → `/opsx:archive` | `openspec/changes/<name>/` while in progress, merged into `openspec/specs/` on archive |

- Not sure? Start with OpenSpec. If the proposal turns out to need anything from the Spec Kit row, stop and switch to Spec Kit.
- Project principles are in `.specify/memory/constitution.md`. Plans must pass its checks.
- Create the git branch (below) **before** running `/speckit-specify` or `/opsx:propose`. Neither tool creates branches here.
- Archive an OpenSpec change (`/opsx:archive`) on the branch before opening the PR, so the PR includes the updated living spec.
- If the code needs to differ from the spec, update the spec first.

## Branches and pull requests

`main` only changes by merging a reviewed pull request. GitHub doesn't enforce this on this repo (branch protection needs GitHub Pro for private repos), so follow these rules every time.

For every change:

1. Start from an up-to-date main: `git switch main && git pull`. Always pull first: a scheduled GitHub Action (`.github/workflows/sync.yml`) commits synced scrobbles to `main` every 6 hours.
2. Create a branch: `git switch -c <type>/<short-description>`. Use `feature/`, `fix/`, `docs/` or `chore/`.
3. Commit on the branch.
4. Push and open a PR: `git push -u origin HEAD`, then `gh pr create`, filling in `.github/pull_request_template.md`. Put `Closes #N` in the description for each issue the PR resolves.
5. **Never merge.** The user reviews and merges on GitHub (`gh pr merge` is denied in `.claude/settings.json`).

PRs are merged with a merge commit (squash is off), so every commit on the branch stays in main's history: keep commits small and clearly described.

Never push to `main`. The sync workflow's own commits to `main` are expected.

You may rebase a feature branch onto `origin/main` (for example to clear merge conflicts on a PR) and force-push it, on branches you created (`feature/`, `fix/`, `docs/`, `chore/`). Prefer `git push --force-with-lease`, which refuses to overwrite commits you haven't seen. Never force-push `main`.

One deliberate exception: the scheduled `analytics` workflow (`.github/workflows/analytics.yml`) replaces the private `analytics` branch with one fresh commit each night, so only the latest usage export is kept (spec 012). Only that workflow, and only that branch. That workflow may also force-push the `analytics` branch; no other workflow may force-push.

## Hosting and infrastructure

The site is hosted on Vercel (Hobby) with visitor data in Neon, both on free plans with no card (constitution VII). Everything is declared with OpenTofu in `infra/`.

- Change hosting settings only by editing `infra/` in a PR. Never change them in the Vercel or Neon dashboards.
- Never ask for, print or commit secret values (tokens, passphrases, connection strings). The owner sets them as GitHub or Vercel secrets.
- `data/cache/` is committed and append-only, like `data/raw/`. `data/public.db` is built in CI and never committed.
