# Tasks

All work is on branch `chore/make-repo-public` in the worktree. Never merge; the owner reviews and merges.

## 1. Keep the 12-month prune running

- [x] 1.1 Add `.github/workflows/prune.yml`: nightly at 02:43 UTC plus `workflow_dispatch` with an `env` choice (`prod` default, `dev`), `permissions: contents: read`, one step that runs `uv run --no-default-groups rain-in-my-head viewer prune --env "$TARGET"` with only the matching owner secret. Verify with `actionlint` or a YAML parse, and `grep -c "contents: write" .github/workflows/prune.yml` prints 0.
- [x] 1.2 Add a line to `README.md` "Usage and limits" saying the nightly job `prune.yml` deletes records older than 12 months, and verify the README names the same file and time as the workflow.

## 2. Stop the export

- [x] 2.1 Delete `.github/workflows/analytics.yml` and `.github/scripts/replace-analytics-branch.sh`; verify `git grep -nE "analytics.yml|replace-analytics|analytics-dev"` outside `specs/` and `openspec/changes/archive` finds nothing.
- [x] 2.2 Replace the README "The nightly copy" paragraph (about line 213) with a short note that visitor data is kept only in the visitor database, is never copied to the repository, and that `viewer export DIR` still writes two CSV files to a local folder. Verify no README sentence mentions the `analytics` branch.
- [x] 2.3 Add a "Superseded by `make-repo-public`" note to `specs/012-usage-tracking/` (`spec.md` user story 5, FR-024 to FR-027, SC-010; `plan.md`; `research.md` R8 and R9; `tasks.md` T034; `quickstart.md`; `contracts/cli.md`) and verify each file with a mention of the `analytics` branch now carries the note.

## 3. Make the docs say "public"

- [x] 3.1 Amend `.specify/memory/constitution.md` Data and Privacy: the repository is public; of `data/` only `data/raw/` and `data/cache/` are committed and all scrobbles since 2011 are public; OpenTofu state is committed only encrypted; visitor data never enters any branch. Set **Version** to 1.3.0 and **Last Amended** to 2026-11-04, and state "MINOR" in the PR. Verify `grep -n "private" .specify/memory/constitution.md` shows no claim that the repository or the `analytics` branch is private.
- [x] 3.2 Update `README.md` "Scheduled sync" step 1 so it no longer says to push to a private repository: say it contains your listening history and is public if you make it public. Verify by reading the step.
- [x] 3.3 Update `CLAUDE.md`: line 20 (branch protection is free on public repos and can now be enabled; `sync.yml` commits to `main` so it needs a bypass) and delete the force-push exception at line 46 (the analytics workflow is gone). Verify `grep -n "analytics" CLAUDE.md` finds nothing and `grep -rnE "push.*--force|force-with-lease" .github` finds nothing.
- [x] 3.4 Run the checks the new specs describe against the tracked files: `git ls-files data | cut -d/ -f1-2 | sort -u` prints only `data/cache` and `data/raw`, and `git ls-files | grep -iE "\.env$|\.pem|\.key"` prints nothing. Verify the output is pasted in the PR.
- [x] 3.5 `openspec validate make-repo-public --strict` passes, and CI on the PR is green.

## 4. Pull request

- [x] 4.1 `git fetch origin`, rebase on `origin/main` if needed, push with `git push -u origin HEAD`, and open the PR with `.github/pull_request_template.md`. Put the post-merge steps from group 5 in the description. Archive the change with `/opsx:archive` on this branch before opening the PR. Verify `git status` is clean and `git log @{u}..` is empty.

## 5. After the owner merges (owner steps, listed here so nothing is missed)

- [ ] 5.1 Run `prune.yml` by hand on `dev` (`gh workflow run prune.yml -f env=dev`; GitHub only allows a manual run once the file is on `main`, so this could not be tried on the branch). Verify the run is green, prints one `[dev] deleted N usage records older than 12 months` line and nothing else, and no branch or commit appears. Then run it on `prod` the same way.
- [ ] 5.2 Delete the remote branches: `git push origin --delete analytics analytics-dev`. Verify `git ls-remote --heads origin` shows neither.
- [ ] 5.3 Delete all old analytics workflow runs (`gh run list --workflow analytics.yml` then `gh run delete <id>` for each; there were 4). Verify the list is empty. Do this before 5.4 so no public log shows an old commit hash.
- [ ] 5.4 Flip visibility: GitHub, Settings, General, Danger Zone, Change visibility, Make public. Verify the repository opens in a private browser window.
- [ ] 5.5 In a private window check that `data/raw/` is as expected and no `analytics` branch is listed; skim one Actions run log for anything unexpected.
- [ ] 5.6 Update the Notion portfolio page: replace "Private repository" with the repository link, and tell Claude so it can edit the page.
