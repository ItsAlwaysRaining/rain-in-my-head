# Instructions for Claude

## Specs before code

Every change except docs and chores starts with a spec. There are two tracks, and **OpenSpec is the default**:

| Track | Use for | Commands | Specs live in |
|---|---|---|---|
| **OpenSpec** (default) | Almost everything: fixes, new pages, CLI commands, data sources, dependencies, schema changes, and features that touch several modules | `/opsx:propose` → `/opsx:apply` → `/opsx:archive` | `openspec/changes/<name>/` while in progress, merged into `openspec/specs/` on archive |
| **GitHub Spec Kit** | Major overhauls only: changes that touch every part of the app, such as converting the whole app to a new language or changing the entire layout in one go | `/speckit-specify` → (`/speckit-clarify`) → `/speckit-plan` → `/speckit-tasks` → (`/speckit-analyze`) → `/speckit-implement` | `specs/NNN-<name>/` (spec, plan, tasks) |

- Not sure? Use OpenSpec. Only switch to Spec Kit if the change really touches every part of the app. A new feature, even a large one, is not enough.
- Project principles are in `.specify/memory/constitution.md`. Plans must pass its checks.
- Create the worktree and branch (below) **before** running `/opsx:propose` or `/speckit-specify`. Neither tool creates branches here.
- Archive an OpenSpec change (`/opsx:archive`) on the branch before opening the PR, so the PR includes the updated living spec.
- If the code needs to differ from the spec, update the spec first.

## Branches, worktrees and pull requests

`main` only changes by merging a reviewed pull request. GitHub doesn't enforce this on this repo (branch protection needs GitHub Pro for private repos), so follow these rules every time.

**Always work in a worktree.** Every change, including docs and chores, gets its own git worktree so the main checkout stays clean and builds can run in parallel. Never edit files in the main checkout.

For every change:

1. Fetch the latest main: `git fetch origin`. Always fetch first: a scheduled GitHub Action (`.github/workflows/sync.yml`) commits synced scrobbles to `main` every 6 hours.
2. Create the worktree and branch from it: `git worktree add ../rain-in-my-head-<short-description> -b <type>/<short-description> origin/main`. Use `feature/`, `fix/`, `docs/` or `chore/`. Do all work inside that worktree.
3. Commit on the branch.
4. Push and open a PR: `git push -u origin HEAD`, then `gh pr create`, filling in `.github/pull_request_template.md`. Put `Closes #N` in the description for each issue the PR resolves.
5. **Never merge.** The user reviews and merges on GitHub (`gh pr merge` is denied in `.claude/settings.json`).
6. After the user merges, remove the worktree: `git worktree remove ../rain-in-my-head-<short-description>`.

**Never leave code in limbo.** As soon as code has been written, commit it. Then do one of these before ending the task or the session:

- **Work is complete:** push and open the PR (step 4).
- **Work is unfinished:** make a checkpoint commit (message starting `WIP:`), push the branch, and say in the reply what is done and what is left. Open a draft PR if one doesn't exist yet (`gh pr create --draft`).

Uncommitted or unpushed changes at the end of a task are a mistake. Check `git status` and `git log @{u}..` before finishing.

PRs are merged with a merge commit (squash is off), so every commit on the branch stays in main's history: keep commits small and clearly described.

Never push to `main`. The sync workflow's own commits to `main` are expected.

You may rebase a feature branch onto `origin/main` (for example to clear merge conflicts on a PR) and force-push it, on branches you created (`feature/`, `fix/`, `docs/`, `chore/`). Prefer `git push --force-with-lease`, which refuses to overwrite commits you haven't seen. Never force-push `main`.

One deliberate exception: the scheduled `analytics` workflow (`.github/workflows/analytics.yml`) replaces the private `analytics` branch with one fresh commit each night, so only the latest usage export is kept (spec 012). Only that workflow, and only that branch. That workflow may also force-push the `analytics` branch; no other workflow may force-push.

## Hosting and infrastructure

The site is hosted on Vercel (Hobby) with visitor data in Neon, both on free plans with no card (constitution VII). Everything is declared with OpenTofu in `infra/`.

- Change hosting settings only by editing `infra/` in a PR. Never change them in the Vercel or Neon dashboards.
- Never ask for, print or commit secret values (tokens, passphrases, connection strings). The owner sets them as GitHub or Vercel secrets.
- `data/cache/` is committed and append-only, like `data/raw/`. `data/public.db` is built in CI and never committed.
