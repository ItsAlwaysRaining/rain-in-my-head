# Research: Rename to rain-in-my-head

## 1. Moving the package

- **Decision**: `git mv src/listening src/rain_in_my_head`, then replace `from listening` /
  `import listening` and dotted references such as `"listening.api:app"` (the uvicorn target in
  `cli.py`). Update `pyproject.toml`: `name = "rain-in-my-head"`, script
  `rain-in-my-head = "rain_in_my_head.cli:main"`, `packages = ["src/rain_in_my_head"]`. Run `uv lock` and
  `uv sync`.
- **Rationale**: `git mv` keeps file history (`git log --follow`). A distribution named
  `rain-in-my-head` normalises to the import name `rain_in_my_head`, which is what hatchling and uv expect.
- **Alternatives considered**: keeping `listening` as an alias module that re-exports the new
  package. Rejected by the spec (FR-002: no alias).

## 2. Finding every use of the old names

- **Decision**: a three-way sort of `git grep -n -i -E "listening|spotify-music-analysis"` results:
  1. **Rename**: package, command, imports, user-facing "Run `uv run listening …`" messages, titles,
     `argparse` `prog`, the Last.fm User-Agent (`listening-analytics/0.1` → `rain-in-my-head/0.1`),
     `web/package.json` and `package-lock.json` name (`listening-web` → `rain-in-my-head-web`), the
     FastAPI title, code comments that name the package.
  2. **Keep (descriptive)**: "listening history", "listening days", "listening overall",
     "Listening from", "Last.fm listening analytics" in the argparse description is reworded to keep
     the meaning without the old name.
  3. **Keep (FR-007 / history)**: `data/listening.db`, `LISTENING_DB`, `LISTENING_RAW_DIR`; specs 002
     and 003's done tasks and research; `openspec/changes/archive/`; past entries in
     `docs/streamlit-vs-typescript.md`.
- **Rationale**: a single grep at the end (quickstart step 6) can then be read line by line against
  this list; anything not in groups 2–3 is a miss.

## 3. Display name

- **Decision**: "Rain in My Head" in the Streamlit `page_title`, the Overview `st.title` (both
  occurrences), `web/index.html` `<title>`, the TypeScript Overview `<h1>`, the FastAPI `title`, the
  README heading, the constitution title and the palette reference page.
- **Rationale**: owner's choice (spec clarification). Headings that are page names, not the app name,
  stay as they are.

## 4. Constitution amendment

- **Decision**: PATCH 1.1.0 → 1.1.1, wording only: title and the paths/commands it quotes
  (`src/listening/` → `src/rain_in_my_head/`, `listening build` → `rain-in-my-head build`). No principle
  changes meaning. It goes in this feature PR, not a separate `chore/` PR (see plan Complexity Tracking).
- **Rationale**: the constitution quotes paths that this PR moves. A separate PR merged first would
  point at paths that don't exist yet; one merged after would leave `main` wrong in between.

## 5. Open Spec Kit tasks and spec 001

- **Decision**: in `specs/003-typescript-dashboard/`, update the not-done tasks (T026–T043) and the
  quickstart/contract lines those tasks rely on to `src/rain_in_my_head/` and `rain-in-my-head`. Leave
  done tasks (T001–T025), research and the past log as written. Spec 001 lives only on the local
  branch `feature/new-artist-page`; update it there after this PR merges (by merging `main` into
  it, then editing its paths), as a post-merge step.
- **Rationale**: future work reads the open tasks, so they must be right; finished work is a record.
  Editing spec 001 here would mean adding a file that isn't on `main`.

## 6. Renaming the GitHub repository

- **Decision**: after the owner merges, run
  `gh repo rename rain-in-my-head --repo ItsAlwaysRaining/spotify-music-analysis --yes`, then
  `gh repo edit ItsAlwaysRaining/rain-in-my-head --description "Personal listening history from Last.fm, explored in two dashboards"`,
  then `git remote set-url origin https://github.com/ItsAlwaysRaining/rain-in-my-head.git` (if `gh`
  hasn't already updated it) and check with `git remote -v` and `git fetch`.
- **Rationale**: GitHub redirects the old URL for git and web, so nothing breaks between merge and
  rename. `sync.yml` uses `actions/checkout` of the current repository and never names it.
- **Alternatives considered**: renaming before merge. Rejected: the owner reviews the PR first.

## 7. Moving the local folder and Claude's memory

- **Decision**: the owner, with no Claude session open in the folder, runs:
  ```sh
  cd ~/Documents/claude_projects
  mv spotify-music-analysis rain-in-my-head
  mv ~/.claude/projects/-Users-oliver-Documents-claude-projects-spotify-music-analysis \
     ~/.claude/projects/-Users-oliver-Documents-claude-projects-rain-in-my-head
  cd rain-in-my-head && uv sync
  ```
  `uv sync` is needed because `.venv` scripts record the old absolute path. Then reopen the folder in
  VS Code and start a new session.
- **Rationale**: Claude Code keys project memory on the folder path with `/` and `_` replaced by
  `-`, so the memory folder name must follow the clone.

## 8. Spotify developer app

- **Decision**: rename the app at developer.spotify.com/dashboard → the app → Settings → Edit; the
  name and description are free text. The client ID, redirect URI and saved token don't change.
- **Rationale**: Spotify identifies the app by client ID (spec assumption); the name only shows on
  the consent screen.
