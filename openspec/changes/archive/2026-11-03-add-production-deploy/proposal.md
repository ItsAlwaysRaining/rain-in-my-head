# Proposal

## Why

Phases 0–6 built and tried everything on previews (Neon `dev`), but `rain.storyandstructure.studio` still shows Vercel's "deployment not found" page. Phase 7 puts the site live on the `prod` data, keeps it fresh without anyone merging, and notices when a deploy leaves the site broken.

## What Changes

- Extend `.github/workflows/deploy.yml` with a **production** path, using the same build steps as the preview: build `data/public.db`, build `web/`, export requirements, run the bundle check, then `vercel pull`, `vercel build` and `vercel deploy --prebuilt` with `--prod`. It runs on a push to `main` (a merged pull request), on a schedule at **03:00 UTC**, and by hand (`workflow_dispatch`).
- Add a **check before anything goes live**. A production build is first staged (`--skip-domain`, so visitors still get the old one). `/api/health` must answer `{"ok": true}` and a locked data route with no session must still be refused. Only then is it promoted to the live address. If the check fails, the run goes red and visitors never saw the build. The same check runs on previews, through `vercel curl`, which handles the preview login itself.
- Add the **nightly rebuild**. A push made by `sync.yml` with the default token does not start other workflows, so the scheduled run is what puts the day's new plays on the site.
- Give the production path its own concurrency group that never cancels a running deploy; previews keep one group per pull request.
- Widen the dataset-window check from 737 to **738** days. It sits at 737.0 today, so it fails by rounding some nights, and a nightly deploy can't stop for that.
- README: say what is live (the "Until phase 7…" sentence), add a "Production" section (what starts a deploy, the health check, how to promote an older deployment by hand), and tidy the custom-domain wording so every mention of DNS says Cloudflare.

Not in this change:
- **The nightly clean-up job.** `analytics.yml` already runs `viewer prune` and `viewer export` at 02:43 UTC with the owner role (phase 5). Nothing to add.
- **Sending codes to friends.** The owner makes and sends their own codes. The steps go on the to-do page as a `p7-*` group, not in code.
- A bypass secret in `infra/`. `vercel curl` is used instead; if it can't pass the login, the design has a fallback.
- Any change to `infra/`. The production environment variables, the domain and the secrets already exist.

## Capabilities

### New Capabilities
- `production-deploy`: the live site is deployed from `main` and every night at 03:00 UTC, checked before it goes live, and left on the previous version if the check fails.

### Modified Capabilities
- `preview-deploy`: the dataset-window limit becomes 738 days (the 737 days of the window and lag, plus one day of margin), the "never production" promise is reworded now that the same workflow also deploys production, and a preview must pass the same health check.

## Impact

- `.github/workflows/deploy.yml` (production path, triggers, concurrency, health check, promote).
- `README.md` (live-site wording, "Production" section, Cloudflare wording).
- Uses existing secrets and variables only: `VERCEL_API_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`. The `production` environment variables (`DATABASE_URL` for Neon `prod`, `SESSION_SECRET`, `LISTENING_HOSTED`) are already set by `infra/vercel.tf`.
- First real exposure to the internet: every page still needs an invite code (spec 011), but `/api/health` and the login page are public.
