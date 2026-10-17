# Rain in My Head Constitution

## Core Principles

### I. Raw Scrobbles Are the Source of Truth

- `data/raw/lastfm/YYYY-MM.jsonl` is append-only. Code MUST NOT rewrite or delete existing lines.
- `data/listening.db` MUST be fully rebuildable from the raw files plus cached API lookups
  (`rain-in-my-head build`, `rain-in-my-head enrich`). It stays gitignored.
- Schema changes go in `src/rain_in_my_head/schema.sql` and MUST apply cleanly to an existing database
  on the next `build`. A change that needs the database deleted MUST say so in its spec.

Rationale: the history is personal and irreplaceable; everything derived from it can be rebuilt.

### II. Spec First, Small Changes

- Every change except docs and chores starts with a spec: OpenSpec for fixes and small additions,
  Spec Kit for new features (see `CLAUDE.md`).
- When code needs to differ from the spec, the spec is updated first.
- Work happens on a branch and lands through a pull request that the repository owner reviews and
  merges. PRs stay small, with commits that each describe one step.

Rationale: a one-person project still needs a record of why things are the way they are.

### III. Verify in the Real App

- Dashboard changes MUST be checked in a real browser (for example headless Chrome) by doing what a
  user would do: clicking, selecting, navigating. Unit-style runs such as Streamlit's AppTest are a
  smoke test, not proof.
- Any number a change shows or alters MUST be cross-checked once against a direct SQLite query.
- PR descriptions list what was checked and what was not.

Rationale: the bugs found so far (unclickable rows, unclickable charts) only showed up in a browser.

### IV. Few Dependencies, Existing Stack

- Python 3.10+, managed with uv. The CLI uses httpx and python-dotenv.
- There are two dashboards, kept side by side so they can be compared:
  - **Streamlit** (`dashboard/`): Streamlit, pandas and Altair, in the `dashboard` dependency group.
  - **TypeScript** (`web/`): Vite, React, TypeScript and Vega-Lite, reading a FastAPI JSON API
    (`src/rain_in_my_head/api.py`, FastAPI and uvicorn in the `web` dependency group). Node and npm are
    build and dev tools for `web/` only; nothing outside `web/` needs them.
- The scheduled sync MUST keep running with `--no-default-groups`, so no dashboard dependency is
  ever needed to fetch scrobbles.
- A new runtime dependency (Python or npm) MUST be justified in the plan (what it replaces, why the
  stack can't do it). Test-only tools run ad hoc (e.g. `uv run --with`, `npx`) rather than becoming
  project dependencies.

Rationale: fewer moving parts to update, the scheduled sync stays fast and reliable, and the two
dashboards stay directly comparable.

### V. Respect External APIs and Secrets

- Last.fm and Spotify calls MUST be cached in SQLite, resumable after interruption, and
  rate-limited. A rerun MUST only fetch what is missing.
- Dashboard pages MUST NOT call external APIs on page load; they read the database (images are
  loaded by the browser from the URLs Last.fm already gave us).
- Secrets live only in `.env` and `data/.spotify_token.json`, both gitignored, and in GitHub
  Actions secrets. They MUST NOT appear in code, specs, logs or PRs.

Rationale: keeps within API limits, makes long enrichments safe to stop, and protects the accounts.

### VI. Consistent Dashboards

- Both dashboards use one palette: `.streamlit/config.toml` (and the chart constants in
  `dashboard/views/overview.py`) for Streamlit, mirrored as CSS tokens in `web/` for TypeScript.
  A palette change MUST update both. Charts MUST be readable on the dark theme.
- Both dashboards MUST show the same numbers for the same inputs. Data work (queries,
  aggregation, ranking) lives in shared functions in `src/rain_in_my_head/` that both the Streamlit
  pages and the API call. It MUST NOT be reimplemented in a page or in TypeScript.
- Streamlit: each page is one module in `dashboard/views/`, registered in `dashboard/app.py`.
  TypeScript: each page is one module in `web/src/pages/`, with the same URL path as its
  Streamlit counterpart. Helpers used by more than one page live in a shared module, not copied.
- Every dashboard change states which app(s) it applies to (Streamlit, TypeScript or both). A
  change to one app only is allowed; the difference is noted in `docs/streamlit-vs-typescript.md`.
- Interactive elements MUST respond to a click anywhere a user would reasonably click (a whole
  table row, a whole chart panel), not only on a small target.

Rationale: the dashboards are the product, and comparing them is only meaningful if the numbers
underneath are identical.

## Data and Privacy

The repository is private and holds personal listening history. Nothing from `data/` other than
`data/raw/` is committed. Published artifacts (screenshots, shared pages) contain only what the
owner chooses to share.

## Development Workflow

1. Start from an up-to-date `main` (`git switch main && git pull`); the sync workflow commits to it
   every 6 hours.
2. Create a `feature/`, `fix/`, `docs/` or `chore/` branch before writing specs.
3. Write the spec (OpenSpec or Spec Kit), get it reviewed when the workflow calls for it, then
   implement, ticking tasks as they are done.
4. Verify per Principle III, update the README when behaviour changes, open a PR with
   `.github/pull_request_template.md`, and link issues with `Closes #N`.
5. Never merge, never push to `main`, never force-push.

## Governance

This constitution takes precedence over other practices in the repo; `CLAUDE.md` holds the
operational detail. Spec Kit plans MUST include a Constitution Check against these principles, and
any deviation MUST be justified in the plan's Complexity Tracking. Amendments go through a
`chore/` pull request that states the version bump: MAJOR for removing or redefining a principle,
MINOR for adding one or materially expanding guidance, PATCH for wording.

**Version**: 1.1.1 | **Ratified**: 2026-10-14 | **Last Amended**: 2026-10-16
