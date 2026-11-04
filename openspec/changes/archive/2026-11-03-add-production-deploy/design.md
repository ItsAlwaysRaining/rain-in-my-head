# Design

## Context

- `deploy.yml` today has one job, `preview`, that runs only on `pull_request`. Its steps (build `public.db`, check the window, build `web/`, export requirements, `vercel pull`, `vercel build`, bundle check, `vercel deploy --prebuilt`) are exactly what production needs, apart from the environment and the `--prod` flag.
- The Vercel project has no Git connection (`infra/vercel.tf`), so nothing deploys except this workflow. Its `production` environment variables, the `rain.storyandstructure.studio` domain and the `VERCEL_*` secrets and variables already exist.
- `vercel_authentication = standard_protection` locks every deployment URL except the production domain. CI has no bypass secret (kept out of phase 6 on purpose).
- `sync.yml` pushes to `main` with the default `GITHUB_TOKEN`. GitHub does not start other workflows for those pushes, so the sync alone never redeploys.
- `analytics.yml` already runs `viewer prune` and `viewer export` against Neon `prod` at 02:43 UTC. The 12-month clean-up is done.
- `/api/health` is public and answers `{"ok": true}` on a hosted build. Locked routes answer 403 `login_required` with no session (`tests/test_hosted_smoke.py`).
- Vercel CLI 64.7.0 (the pinned one) has `deploy --skip-domain`, `promote` and `curl` (a curl that adds protection bypass automatically).

## Goals / Non-Goals

**Goals:**
- A merge to `main` and the 03:00 UTC schedule both put a fresh, checked build on the live address.
- A bad build never reaches visitors.
- One workflow file and one list of build steps, so a preview and production can't drift apart.

**Non-Goals:**
- Any change to `infra/`, the secrets, or who can open a page.
- A stored protection-bypass secret.
- The 12-month clean-up (exists) and sending codes (owner's job).
- Deploying on every sync push. Nightly is enough for a site whose newest play is already 7 days old.

## Decisions

1. **One job, two targets.** Rename `preview` to `deploy` and compute the target from the event: `pull_request` is `preview`, anything else is `production`. The target sets `vercel pull --environment=$TARGET`, and production adds `--prod` to `vercel build` and `--prod --skip-domain` to `vercel deploy`. The PR comment step runs only for pull requests. *Alternative:* a second job or a reusable workflow. Rejected: it copies about 60 lines (or adds indirection) for two flag differences, and the bundle check is the part that must never diverge.

2. **Triggers and guards.** `on: pull_request`, `push: branches: [main]`, `schedule: "0 3 * * *"`, `workflow_dispatch`. The job runs when the event is a same-repo non-Dependabot pull request (as now), or when the event is not a pull request and the ref is `refs/heads/main`. A hand-started run on another branch is skipped, so no branch can reach production. The schedule runs on the default branch by definition. GitHub may start a scheduled run a few minutes late; "03:00 UTC" means "queued at 03:00".

3. **Concurrency.** Group `deploy-<PR number>` for pull requests, with cancel-in-progress as now. Group `deploy-production` for everything else, with `cancel-in-progress: false`, so a merge during the nightly run waits and the running deploy is never cut off halfway. GitHub keeps only one waiting run per group, so two merges in a row deploy the newer one. That is fine: each run builds `main` as it is when it starts.

4. **Stage, check, then promote.** Production is deployed with `--prod --skip-domain`, which builds a production deployment (production environment, prod Neon) but does not point the live address at it. The workflow then calls `vercel curl /api/health --deployment <url>` and `vercel curl /api/genre --deployment <url>` (no session cookie), retrying every 10 seconds for two minutes, and expects `{"ok": true}` and a 403 with `login_required`. Only then does `vercel promote <url>` make it live. A failed check leaves the live address on the previous deployment, with no rollback to get wrong. *Why not check the live address after `--prod`:* a broken build would already be serving visitors, and `vercel rollback` turns off automatic domain assignment until someone promotes again, which would silently make the next deploy not go live. The check runs for previews too (they are also locked, and it is the only way to try it before the first merge). *Why `vercel curl`:* the staged URL is locked by standard protection and CI has no bypass secret; `vercel curl` handles the bypass itself, so `infra/` stays untouched.

5. **Fallback if `vercel curl` can't pass protection on Hobby.** The first task proves it on a real staged deploy. If it can't, the fallback is: deploy with `--prod`, check `https://rain.storyandstructure.studio/api/health` and the locked route, and on failure run `vercel promote <previous-deployment>` (found with `vercel ls --prod` before deploying), which also restores automatic assignment. The spec's outcome (the live address ends up on the previous deployment, run red) is the same either way; the fallback only has a short window of bad serving. A bypass secret in `infra/` is a third option and needs its own change.

6. **Window margin.** Change the assert from `<= 737` to `<= 738`. The check is shared by both targets. Nothing else about the window moves.

7. **Bundle check unchanged.** The same step runs before the deploy for both targets, so the `data/listening.db*` rule from phase 6 covers production without a second copy.

8. **README.** Add a "Production" section next to "Previews and CI checks": what starts a deploy, how to run one by hand (`gh workflow run deploy.yml`), what the health check does, what a red run means, and how to promote an older deployment by hand. Replace the "Until phase 7…" sentence. In "Custom domain", keep Spaceship only where it is true (where the name is registered and renewed) and say Cloudflare for DNS everywhere else.

## Risks / Trade-offs

- [`vercel curl` doesn't bypass protection for this account] → Task 1.2 proves it before anything depends on it; decision 5 is the fallback.
- [The first production deploy fails for a reason no preview showed, such as the prod Neon role or the `rain_app` grants] → It stays staged and the live address is unchanged. The run's log (counts and status codes only) names the failing check. The owner already created the prod role (`p4-prod`).
- [Production data is real visitors, and a nightly deploy interrupts a request mid-flight] → Vercel keeps the old deployment serving until promotion completes; sessions are signed cookies, not stored in the function.
- [The schedule starts late or is skipped by GitHub] → `workflow_dispatch` is there, and a missed night only means one more day of stale data. Not worth an alert.
- [GitHub disables scheduled workflows after 60 days without repository activity] → `sync.yml` commits every 6 hours, so activity never lapses.
- [Two merges inside one deploy] → Decision 3: the newer one waits and builds the latest `main`.
- [A 738-day margin hides a real window bug by a day] → The dataset's lower bound is also covered by spec 009's own tests; the check is a backstop, not the test.
