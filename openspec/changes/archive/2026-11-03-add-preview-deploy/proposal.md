# Proposal

## Why

Phases 0–5 built everything the hosted site needs (data, infrastructure, invite codes, usage tracking), but nothing is deployed yet: the Vercel project exists, `rain.storyandstructure.studio` shows Vercel's "deployment not found" page, and the repo has no CI that runs tests or scans for leaked secrets. Phase 6 of the hosting plan puts the site online as a **preview** (the dev environment) for every pull request, so the whole path can be tried against the Neon `dev` branch before anything goes to production in phase 7.

## What Changes

- Add `api/index.py`, a thin file that exposes the existing FastAPI `app` to Vercel's Python runtime and points it at `data/public.db`.
- Add `vercel.json`: `/api/*` goes to the function, everything else to the React build (`web/dist`, with `index.html` for the app's own routes). It also lists which files go into the function (`src/`, `data/public.db`) and which stay out.
- Add `.github/workflows/deploy.yml`, **preview half only**. On a pull request from this repo it builds `data/public.db`, runs `vercel pull`, `vercel build` and `vercel deploy --prebuilt` (no `--prod`), then posts the preview URL on the PR.
- Add `.github/workflows/ci.yml`: Python tests, `npm run build` in `web/`, gitleaks, and Ruff's `S` (security) rules.
- Add a short "Previews" section to the README: how to open a preview, and the one-time Vercel login it needs.
- **No new dependency.** Vercel's CLI runs through `npx` in CI only, Ruff and gitleaks run ad hoc (constitution IV).
- **No change to `infra/`.** The project, domain, preview protection, preview environment variables (Neon `dev` branch) and the `VERCEL_PROJECT_ID` and `VERCEL_ORG_ID` Actions variables already exist from phase 3.

Not in this change (phase 7): `--prod` deploys on merge, the nightly rebuild, the `/api/health` check after deploy, and sending codes to friends. Also not here: a way for CI to call the locked preview (it would need a protection-bypass secret declared in `infra/`).

## Capabilities

### New Capabilities
- `preview-deploy`: every pull request from this repo gets a locked Vercel preview that serves the built site and the API with a two-year `public.db`, reading and writing visitor data on the Neon `dev` branch only.
- `ci-checks`: every pull request runs the tests, the frontend build, a secret scan and a security lint, and a failure is visible on the PR.

### Modified Capabilities

None. Specs 009 (public dataset), 010 (infrastructure), 011 (viewer access) and 012 (usage tracking) already say how the app behaves when hosted; this change only gets it running there.

## Impact

- New files: `api/index.py`, `vercel.json`, `.github/workflows/deploy.yml`, `.github/workflows/ci.yml`.
- `README.md`: a "Previews" section; `docs/` untouched.
- Possibly `pyproject.toml`: one `[tool.ruff]` block for the `S` rules (config only, not a dependency). Possibly `src/` if the first preview shows the app needs a small fix to start on Vercel (for example the data path).
- Actions minutes: about 3 minutes per push to a PR, within the 2,000 free minutes (plan estimate: about 450 a month in total).
- Secrets: uses `VERCEL_API_TOKEN` (passed to the CLI as `VERCEL_TOKEN`). Nothing new for the owner to create. Fork PRs get no secrets and no deploy.
- Constitution IV (Node and the Vercel CLI allowed in CI only), V (secrets stay in Actions and Vercel) and VII (free plans, no card) all hold.
- Process note: the roadmap labels this phase "Spec Kit · 013-hosting", but CLAUDE.md now makes OpenSpec the default and reserves Spec Kit for changes that touch every part of the app. This is a deploy path with four new files, so it uses OpenSpec.
