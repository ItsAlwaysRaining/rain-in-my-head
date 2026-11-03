# Tasks

## 1. The function and the routing

- [x] 1.1 Add `api/index.py` (shim from design decision 1) and verify: `LISTENING_HOSTED=1 LISTENING_DB=data/public.db uv run python -c "import sys; sys.path.insert(0,'.'); from api.index import app; print(app.title)"` prints "Rain in My Head" after `build` and `publish` have made `data/public.db`
- [x] 1.2 Add `vercel.json` with the output directory, the `/api/*` route, the SPA rewrite, and the include and exclude lists (decisions 2 and 4), and verify `python3 -m json.tool vercel.json` parses and that no pattern includes `data/raw`, `data/cache` or `infra`
- [x] 1.3 Add `requirements.txt` to `.gitignore` and verify `uv export --no-default-groups --group web --no-dev --no-hashes --no-emit-project` lists `fastapi`, `pandas`, `httpx` and `python-dotenv` and does not list `streamlit`

## 2. Preview deploy workflow, proved with a real deploy

- [x] 2.1 Add `.github/workflows/deploy.yml` (decision 5): same-repo check, pinned actions by SHA, per-PR concurrency, build and publish the dataset, build `web/`, export requirements, `vercel pull`, `vercel build`, `vercel deploy --prebuilt` (no `--prod`), and verify with `actionlint` (run ad hoc with `uvx`/`npx`) that the file has no errors
- [x] 2.2 Add the step that creates or edits one PR comment holding the preview address, with a hidden marker, never printing the token or any connection string, and verify by pushing the branch and opening a **draft** PR: the run finishes green and the PR shows one comment with a `*.vercel.app` address
- [x] 2.3 Fix whatever the first deploy shows (import paths, bundle contents, missing packages, `uvicorn`), reading the function log with `npx vercel logs`, and verify the preview address, opened logged in to Vercel, shows the site's login page and `/api/health` answers `{"ok": true}`
- [x] 2.4 Verify the bundle is clean: the deployed function's file list (from `vercel build` output in `.vercel/output/functions`) contains `data/public.db` and `src/rain_in_my_head` and contains no `data/raw`, `data/cache` or `infra` path
- [x] 2.5 Verify the preview is locked: open the preview address in a private window with no Vercel login and confirm it goes to Vercel's login (write the result in the PR description)
- [x] 2.6 Verify the dataset window against the deployed file by opening a SQL check on the CI-built `public.db` in the run (`select min(played_at)`), and that it is no older than 737 days (730-day window plus the 7-day lag from spec 009); record the number in the PR description

## 3. CI checks

- [x] 3.1 Add `tests/test_hosted_smoke.py` (decision 8) covering health, a locked route with no session, typed SQL refused, and a data route answering with a stubbed session, and verify `uv run --with pytest --with httpx pytest tests` passes locally and fails when `api/index.py` is renamed (then restore it)
- [ ] 3.2 Add `.github/workflows/ci.yml` with the four jobs from decision 7, no secrets, pinned actions, and verify with `actionlint` and by seeing all four results on the draft PR
- [ ] 3.3 Add a `[tool.ruff]` block to `pyproject.toml` (config only, `select = ["S"]`, `S101` ignored for `tests/`) and verify `uvx ruff check --select S src api tests` runs; fix each finding or add a `# noqa: S… <reason>` comment, and verify the check is green
- [ ] 3.4 Add `.gitleaks.toml` with an allowlist for `.env.example`, each entry with a comment, and verify `gitleaks detect` passes on the repo, then fails on a throwaway branch with a fake token file (delete the branch; do not push it)
- [ ] 3.5 Verify a failing smoke test shows red without hiding the other three results (push a deliberately failing commit to the draft PR, then revert it)

## 4. Docs and hand-over

- [ ] 4.1 Add a "Previews" section to `README.md` (how to open a preview, the Vercel login it needs, how to make a dev test code with `viewer add --env dev`, the cold-start delay measured in task 2.3) and verify each command in it runs as written on the Mac
- [ ] 4.2 Add the new owner steps to the to-do page (create a dev test code, open the preview and log in, check the Visitors page shows the session under `dev`) and tick the phase-6 items as each is done
- [ ] 4.3 Run `openspec validate add-preview-deploy --strict`, then `/opsx:archive` on the branch, `git pull` and merge the latest `origin/main`, push, mark the PR ready, and fill in `.github/pull_request_template.md` with what was checked and what was not (including that the preview was not called from CI)
