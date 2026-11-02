# Design

## Context

See proposal.md for why. What exists today:

- `src/rain_in_my_head/api.py` defines the FastAPI `app` and also serves `web/dist` through a catch-all route. In hosted mode (`LISTENING_HOSTED=1`) it opens the database read-only and immutable, refuses writes, playlists, typed SQL and AI, and checks a login on every data route. It reads `DATABASE_URL` and `SESSION_SECRET` from the environment.
- `config.ROOT` is two folders above `config.py`, and the database path is `LISTENING_DB` or `data/listening.db`. So the function needs the same folder layout as the repo (`src/rain_in_my_head/...`) and an env var pointing at `public.db`.
- Phase 3 (`infra/`) already created the Vercel project (no Git connection, `standard_protection` on previews, region `iad1`), the custom domain, and the env vars `LISTENING_HOSTED`, `DATABASE_URL` (Neon `dev` for the `preview` target, `prod` for `production`) and `SESSION_SECRET`. It also wrote the Actions variables `VERCEL_PROJECT_ID` and `VERCEL_ORG_ID`. The only Vercel secret in Actions is `VERCEL_API_TOKEN`.
- `rain-in-my-head build` makes `data/listening.db` from the committed raw and cache files; `publish` makes `data/public.db` (730 days) from it.
- There are **no Python tests** and no `ci.yml`. Python dependencies for the API live in the `web` dependency group of `pyproject.toml`, not in `[project].dependencies`.
- Vercel's Python runtime reads dependencies from `pyproject.toml` `dependencies`, `requirements.txt` or a Pipfile, supports Python 3.12 to 3.14 (default 3.12; `.python-version` is already 3.12), looks for an `app` in `api/index.py`, and allows 500 MB uncompressed.

## Goals / Non-Goals

**Goals:**
- A PR push gives a working, locked preview on Neon `dev`, using the app code unchanged wherever possible.
- One place for each fact: dependencies stay in `pyproject.toml`, env vars stay in `infra/`, the date window stays in `publish`.
- A smoke test that would have caught "the API doesn't start on Vercel" before a deploy is tried.

**Non-Goals:**
- Production deploys, the nightly rebuild, and post-deploy health checks (phase 7).
- Calling a locked preview from CI. That needs a protection-bypass secret declared in `infra/`.
- A real test suite. The smoke test is the start of one, not the whole thing.

## Decisions

**1. `api/index.py` is a shim, not a copy.** It adds `src/` to `sys.path`, sets `LISTENING_DB` to `<root>/data/public.db` with `os.environ.setdefault`, and does `from rain_in_my_head.api import app`. The app code stays the same for local runs.
*Alternative:* move the app into `api/`. Rejected: it would break `rain-in-my-head serve` and the Streamlit pages that share the same modules (constitution VI).

**2. Static files come from Vercel's CDN, so the function never serves `web/dist`.** `vercel.json` uses `outputDirectory: "web/dist"`, sends `/api/(.*)` to the function, and rewrites any other path that isn't a file to `/index.html` so `/genre` loads directly. The catch-all route in `api.py` stays for local use and is never hit on Vercel.
*Alternative:* let FastAPI serve the frontend. Rejected: every page load would wake Python and use the 4 CPU-hour allowance.

**3. Dependencies come from `pyproject.toml` through a generated `requirements.txt`, never committed.** CI runs `uv export --only-group web --no-dev --no-hashes --no-emit-project` into `requirements.txt` just before `vercel build`. The file is gitignored.
*Alternatives:* (a) move `fastapi`, `pandas` and `uvicorn` into `[project].dependencies`: rejected, because the scheduled sync runs with `--no-default-groups` precisely to stay light (constitution IV). (b) A hand-kept `requirements.txt`: rejected, it would drift from `uv.lock`. `uvicorn` is not needed on Vercel; dropping it from the export (or accepting it) is decided in the spike (task 2.1).

**4. The function bundle is told exactly what to include.** `vercel.json` `functions` lists `includeFiles` for `src/rain_in_my_head/**` and `data/public.db`, and `excludeFiles` for `web/**`, `data/raw/**`, `data/cache/**`, `infra/**`, `specs/**`, `openspec/**` and `dashboard/**`. The 66 MB of raw data and the Streamlit app must not ship; the private history must never be in the bundle (constitution I and VII).
*Alternative:* rely on defaults. Rejected: Vercel has no tree shaking, so the default could pull in `data/raw`.

**5. `deploy.yml` follows Vercel's documented build-in-CI flow, preview only.** Steps: checkout, set up uv and Node, `uv run --no-default-groups rain-in-my-head build` then `publish`, `npm ci && npm run build` in `web/`, export requirements, then `npx vercel@<pinned> pull --yes --environment=preview`, `vercel build`, `vercel deploy --prebuilt`. The token is passed as `VERCEL_TOKEN` from the secret `VERCEL_API_TOKEN`; project and org IDs come from the existing Actions variables. The preview address from `deploy` is posted as one PR comment, found again by a hidden marker and edited on later pushes.
Triggers are `pull_request` only (never `pull_request_target`), with a job condition that the head repo equals this repo, so forks get no secrets and no deploy. A `concurrency` group per PR cancels an older run when a new commit arrives. Permissions are `contents: read` and `pull-requests: write`, and actions are pinned by SHA as in `infra.yml`.
*Alternative:* Vercel's Git integration. Already ruled out in the plan: sync commits would redeploy, and the data build would run on Vercel's builder. The project has no Git connection on purpose.

**6. `vercel pull` and sensitive variables.** Variables marked sensitive (`DATABASE_URL`, `SESSION_SECRET`) can't be downloaded, which is fine: they are needed at **run** time, and Vercel injects project variables into a prebuilt deployment's function. Nothing in the build reads them. The first preview proves this (task 2.2); if it fails, the fallback is to set them with `vercel deploy --env`, which would put them on the CLI and so needs a separate decision.

**7. `ci.yml` has four independent jobs, none with secrets.** (a) `smoke`: build and publish from the committed data, then run `tests/test_hosted_smoke.py` with `uv run --with pytest --with httpx pytest`. It uses FastAPI's `TestClient` in hosted mode with `DATABASE_URL` unset and a patched session lookup, so it needs no network. (b) `web`: `npm ci && npm run build`. (c) `secrets`: gitleaks over the full history with a checked-in `.gitleaks.toml` allowlist for `.env.example`. (d) `lint`: `uvx ruff check --select S src api` with per-line `# noqa: S… reason` comments where the app has a good reason. pytest, Ruff and gitleaks are not added as dependencies.
*Alternative:* one job. Rejected: four separate results are easier to read on a PR, and one failing step doesn't hide the others.

**8. The smoke test reuses the real app and real committed data.** The build takes about a minute for 219k scrobbles. A small fixture would be faster but would test a different database than the one deployed.

## Risks / Trade-offs

- **[The function fails to start on Vercel because of import paths, bundle size or missing packages]** → The first preview is a spike (tasks group 2): deploy a minimal commit, read the function log, then fix `api/index.py` or `vercel.json`. The smoke test is added after, so it encodes what actually broke.
- **[The cold start is slow because pandas loads]** → Accepted and already stated in the plan ("a few seconds on the first visit"). Measured once in the spike and noted in the README.
- **[`VERCEL_API_TOKEN` is the OpenTofu token, so it can do more than deploy]** → It already sits in Actions for `infra.yml`. Splitting it into a deploy-only token is a later hardening, listed on the to-do page, not done here.
- **[A malicious PR from this repo's own branches could print the secret]** → Only the owner pushes branches. Actions are pinned by SHA, nothing prints the environment, and logs mask secrets.
- **[Each push spends about 3 Actions minutes]** → Within the plan's estimate. The per-PR concurrency group cancels superseded runs.
- **[gitleaks over full history flags old commits]** → The allowlist is reviewed once at setup. Each rule or path exception needs a comment saying why.
- **[Vercel's preview protection blocks CI from checking the deploy]** → No automated check on the preview in this phase. The "done" check is by hand, as the roadmap describes.

## Migration Plan

No data or settings migrate. The workflows start running on the PR that adds them (`ci.yml` runs on its own PR; `deploy.yml` needs to be on the PR branch to run, so it deploys itself). Rollback: delete the two workflows and `vercel.json`/`api/`; nothing in `infra/` changes, so production and DNS are untouched.

## Open Questions

- Does Vercel's Python build want `uvicorn` in the requirements, or does it provide its own server? Answered in the spike; it changes only the export flags.
- Does the owner want preview comments on every push or only on the first? Default: one comment, edited each time.
