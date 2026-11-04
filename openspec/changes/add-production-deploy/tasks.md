# Tasks

## 1. One workflow, two targets

- [x] 1.1 Edit `.github/workflows/deploy.yml` (decisions 1–3, 6): rename the job `deploy`; add the `push` (main), `schedule` (`0 3 * * *`) and `workflow_dispatch` triggers; add the job guard (same-repo non-Dependabot pull request, or a non-pull-request event on `refs/heads/main`); compute the target; pass it to `vercel pull --environment=`; add `--prod` to `vercel build` and `--prod --skip-domain` to `vercel deploy` for production only; split the concurrency group and turn cancel-in-progress off for production; run the PR-comment step only on pull requests; change the window assert to 738. Verify with `npx actionlint` that the file has no errors, and that the preview path is unchanged by reading the diff (same steps, same order, same flags when the target is `preview`)
- [ ] 1.2 Add the check step (decision 4) after the deploy for both targets: `vercel curl /api/health --deployment "$URL"` expecting `{"ok": true}`, and `vercel curl /api/genre --deployment "$URL"` expecting 403 with `login_required`, retrying every 10 seconds for two minutes, printing only status codes and the matching words (never a body that could hold data, a cookie or a header). Verify on the draft PR: the preview run is green and the log shows 200 for health and 403 for the locked route. **If `vercel curl` cannot get through the preview's login protection, stop here and switch to decision 5 (the fallback) before going on**
- [ ] 1.3 Add the promote step, production only, after the check passes: `vercel promote "$URL"`. Verify by reading the workflow that the step has no `if: always()`, that it depends on the check step's success, and that nothing on the pull-request path can reach it
- [ ] 1.4 Verify the check can fail: push a throwaway commit to the draft PR that expects a wrong body from `/api/health`, confirm the run goes red and the PR's preview comment is not corrupted, then revert it
- [ ] 1.5 Verify the logs are clean: `gh run view <id> --log` for the green preview run, searched for `postgres://` and `VERCEL_TOKEN=`, finds nothing. Record the result in the PR description

## 2. README

- [ ] 2.1 Add a "Production" section after "Previews and CI checks": what starts a deploy (a merge, 03:00 UTC, `gh workflow run deploy.yml --ref main`), the stage-check-promote order, what a red run means (the live address is unchanged, read the check step), and how to promote an older deployment by hand (`vercel promote <deployment>`). Verify each command in it runs as written (`gh workflow run deploy.yml --help` and `npx vercel@64.7.0 promote --help` at least)
- [ ] 2.2 Replace the "Until phase 7 deploys the site to production…" sentence with one that says the address serves the site, and tidy the "Custom domain" paragraph so DNS is always Cloudflare and Spaceship appears only for registration and renewal. Verify with `grep -n -i spaceship README.md infra/*.tf` that every remaining line is about registering or renewing, or the "if the nameservers ever go back" note

## 3. Hand-over

- [ ] 3.1 Add the phase 7 owner steps to the to-do page as a `p7-*` group and republish: watch the first production run after the merge, open `https://rain.storyandstructure.studio` and check it asks for a code, make your own prod code with `viewer add --env prod`, log in and click through the pages, check the Visitors page shows the session under `prod`, make and send the friends' codes, and renew the three tokens before about 26 Jan 2027. Verify by reading the db back with `ArtifactData`
- [ ] 3.2 Update the `phase-6-preview-deploy` memory (or add `phase-7-production-deploy`) with the merge state, and remove the Cloudflare README note once 2.2 is merged
- [ ] 3.3 Run `openspec validate add-production-deploy --strict`, then `/opsx:archive` on the branch, `git pull` and merge the latest `origin/main`, push, open the pull request with `.github/pull_request_template.md` filled in (say plainly that the production path first runs for real at merge, staged and checked before it goes live), and stop. Never merge it

## 4. After the owner merges (checked together, not part of the pull request)

- [ ] 4.1 Watch the merge's `Deploy` run: green, the check step shows 200 and 403, the promote step ran. Verify `curl -s https://rain.storyandstructure.studio/api/health` prints `{"ok":true}` and the root page loads
- [ ] 4.2 Trigger one run by hand (`gh workflow run deploy.yml --ref main`) to prove `workflow_dispatch`, and check the next 03:00 UTC run started, then tick the matching to-do items
- [ ] 4.3 Remove the worktree: `git worktree remove ../rain-in-my-head-production-deploy`
